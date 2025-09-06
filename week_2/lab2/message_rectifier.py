"""
Message Rectifier Module
This module uses LLM to generate and rectify commit messages for bug fixes.
"""

import logging
import csv
from typing import List, Dict, Optional
from pathlib import Path
import re

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers library not available. LLM features will be disabled.")

class MessageRectifier:
    """
    Class to rectify commit messages using LLM and rule-based approaches
    """
    
    def __init__(self, model_name: str = "mamiksik/CommitPredictorT5"):
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        
        if TRANSFORMERS_AVAILABLE:
            self._load_model()
        else:
            self.logger.warning("LLM model not loaded. Using rule-based rectification only.")
    
    def _load_model(self):
        """
        Load the pre-trained LLM model for commit message generation
        """
        try:
            self.logger.info("Loading LLM model: %s", self.model_name)
            
            # Load the CommitPredictorT5 model using AutoTokenizer and AutoModelForSeq2SeqLM
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.logger.info("Successfully loaded CommitPredictorT5 model")
                
        except Exception as e:
            self.logger.error("Failed to load CommitPredictorT5 model: %s", str(e))
            # Try fallback to T5-small
            try:
                self.pipeline = pipeline("text2text-generation", model="t5-small")
                self.logger.info("Loaded fallback T5-small model")
            except Exception as e2:
                self.logger.error("Failed to load fallback model: %s", str(e2))
                self.model = None
                self.tokenizer = None
                self.pipeline = None
    
    def _generate_llm_message(self, diff: str, context: str = "") -> str:
        """
        Generate commit message using LLM
        """
        if not TRANSFORMERS_AVAILABLE:
            return ""
        
        try:
            # Use the CommitPredictorT5 model if loaded
            if self.model and self.tokenizer:
                input_text = f"diff: {diff[:1000]}"  # Limit input length
                inputs = self.tokenizer.encode(
                    input_text, return_tensors="pt", max_length=100, truncation=True
                )
                
                import torch
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs, max_length=30, num_beams=2, early_stopping=True
                    )
                
                generated_message = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
            elif self.pipeline:
                # Use fallback pipeline
                input_text = f"Generate commit message for: {diff[:500]}"
                result = self.pipeline(input_text, max_length=30, do_sample=False)
                generated_message = result[0]['generated_text']
            
            else:
                return ""
            
            # Clean up the generated message
            generated_message = self._clean_generated_message(generated_message)
            return generated_message
            
        except Exception as e:
            self.logger.error("Error generating LLM message: %s", str(e))
            return ""
    
    def _clean_generated_message(self, message: str) -> str:
        """
        Clean and normalize generated commit message
        """
        # Remove common prefixes that models might add
        prefixes_to_remove = [
            "commit message:",
            "message:",
            "diff:",
            "fix:",
            "bug:",
            "change:"
        ]
        
        message = message.strip()
        message_lower = message.lower()
        
        for prefix in prefixes_to_remove:
            if message_lower.startswith(prefix):
                message = message[len(prefix):].strip()
                break
        
        # Ensure first letter is capitalized
        if message:
            message = message[0].upper() + message[1:]
        
        # Remove excessive punctuation
        message = re.sub(r'[.]{2,}', '.', message)
        message = re.sub(r'[!]{2,}', '!', message)
        
        # Limit length
        if len(message) > 100:
            message = message[:97] + "..."
        
        return message
    
    def _rule_based_rectification(self, original_message: str, diff_data: Dict) -> str:
        """
        Apply rule-based rectification to commit messages
        """
        filename = diff_data.get('filename', '')
        change_analysis = diff_data.get('change_analysis', {})
        fix_patterns = change_analysis.get('fix_patterns', [])
        change_scope = change_analysis.get('change_scope', '')
        
        # Start with original message
        rectified = original_message.strip()
        
        # Add file context if missing and change is file-specific
        if len(diff_data.get('filename', '').split('/')) > 1:  # File in subdirectory
            file_component = Path(filename).stem
            if file_component.lower() not in rectified.lower():
                rectified = f"{rectified} in {file_component}"
        
        # Add fix pattern context
        if fix_patterns:
            primary_pattern = fix_patterns[0]
            pattern_descriptions = {
                'null_check': 'null check',
                'bounds_check': 'bounds checking',
                'error_handling': 'error handling',
                'initialization': 'initialization',
                'condition_fix': 'conditional logic',
                'resource_management': 'resource management'
            }
            
            pattern_desc = pattern_descriptions.get(primary_pattern, primary_pattern)
            if pattern_desc.lower() not in rectified.lower():
                rectified = f"{rectified} - {pattern_desc}"
        
        # Add scope indication for larger changes
        if change_scope in ['medium', 'large']:
            if 'multiple' not in rectified.lower() and change_scope == 'large':
                rectified = f"{rectified} (multiple changes)"
        
        # Improve vague messages
        vague_messages = ['fix', 'bug fix', 'update', 'change', 'minor fix']
        if rectified.lower() in vague_messages:
            if fix_patterns:
                primary_pattern = fix_patterns[0]
                rectified = f"Fix {pattern_descriptions.get(primary_pattern, primary_pattern)}"
            else:
                rectified = f"Fix issue in {Path(filename).stem}"
        
        # Ensure proper capitalization and punctuation
        if rectified and not rectified[0].isupper():
            rectified = rectified[0].upper() + rectified[1:]
        
        if rectified and not rectified.endswith('.'):
            rectified += '.'
        
        return rectified
    
    def _calculate_message_alignment_score(self, message: str, diff_data: Dict) -> float:
        """
        Calculate how well aligned a commit message is with the actual changes
        """
        if not message:
            return 0.0
        
        score = 0.0
        message_lower = message.lower()
        
        # Check if message mentions the file being changed
        filename = diff_data.get('filename', '')
        if filename:
            file_stem = Path(filename).stem.lower()
            if file_stem in message_lower:
                score += 0.2
        
        # Check if message mentions detected fix patterns
        change_analysis = diff_data.get('change_analysis', {})
        fix_patterns = change_analysis.get('fix_patterns', [])
        
        pattern_keywords = {
            'null_check': ['null', 'none', 'empty'],
            'bounds_check': ['index', 'bound', 'range', 'limit'],
            'error_handling': ['error', 'exception', 'handle', 'catch'],
            'initialization': ['init', 'default', 'setup'],
            'condition_fix': ['condition', 'check', 'logic', 'if'],
            'resource_management': ['close', 'cleanup', 'resource']
        }
        
        for pattern in fix_patterns:
            keywords = pattern_keywords.get(pattern, [])
            if any(keyword in message_lower for keyword in keywords):
                score += 0.3
        
        # Check for change scope alignment
        change_scope = change_analysis.get('change_scope', '')
        lines_changed = diff_data.get('lines_added', 0) + diff_data.get('lines_deleted', 0)
        
        if change_scope == 'large' and lines_changed > 50:
            if any(word in message_lower for word in ['major', 'significant', 'multiple', 'extensive']):
                score += 0.2
        elif change_scope == 'minimal' and lines_changed <= 5:
            if any(word in message_lower for word in ['minor', 'small', 'quick', 'simple']):
                score += 0.2
        
        # Penalize overly generic messages
        generic_phrases = ['fix bug', 'update code', 'make changes', 'fix issue']
        if any(phrase in message_lower for phrase in generic_phrases):
            score -= 0.2
        
        # Bonus for specific technical terms
        if any(term in message_lower for term in ['fix', 'resolve', 'correct', 'patch']):
            score += 0.1
        
        return max(0.0, min(1.0, score))  # Clamp between 0 and 1
    
    def rectify_messages(self, diff_data: List[Dict]) -> List[Dict]:
        """
        Rectify commit messages for all diff data
        """
        self.logger.info("Starting message rectification for %d diffs", len(diff_data))
        
        rectified_data = []
        
        for i, diff_info in enumerate(diff_data):
            try:
                original_message = diff_info.get('message', '')
                diff_text = diff_info.get('diff', '')
                
                # Generate LLM inference
                llm_message = self._generate_llm_message(diff_text)
                
                # Apply rule-based rectification
                rectified_message = self._rule_based_rectification(original_message, diff_info)
                
                # Calculate alignment scores
                original_score = self._calculate_message_alignment_score(original_message, diff_info)
                llm_score = self._calculate_message_alignment_score(llm_message, diff_info)
                rectified_score = self._calculate_message_alignment_score(rectified_message, diff_info)
                
                # Create rectified record
                rectified_record = diff_info.copy()
                rectified_record.update({
                    'llm_inference': llm_message,
                    'rectified_message': rectified_message,
                    'original_alignment_score': original_score,
                    'llm_alignment_score': llm_score,
                    'rectified_alignment_score': rectified_score,
                    'improvement_achieved': rectified_score > original_score
                })
                
                rectified_data.append(rectified_record)
                
                if (i + 1) % 10 == 0:
                    self.logger.info("Processed %d/%d diffs", i + 1, len(diff_data))
                
            except Exception as e:
                self.logger.error("Error rectifying message for diff %d: %s", i, str(e))
                # Add original record with empty rectification fields
                rectified_record = diff_info.copy()
                rectified_record.update({
                    'llm_inference': '',
                    'rectified_message': diff_info.get('message', ''),
                    'original_alignment_score': 0.0,
                    'llm_alignment_score': 0.0,
                    'rectified_alignment_score': 0.0,
                    'improvement_achieved': False
                })
                rectified_data.append(rectified_record)
        
        self.logger.info("Message rectification completed")
        return rectified_data
    
    def save_rectified_data(self, rectified_data: List[Dict], filepath: Path):
        """
        Save rectified data to CSV file
        """
        if not rectified_data:
            self.logger.warning("No rectified data to save")
            return
        
        # Use the same fieldnames as diff_extractor plus rectification fields
        base_fieldnames = [
            'hash', 'message', 'filename', 'change_type',
            'source_code_before', 'source_code_current', 'diff',
            'lines_added', 'lines_deleted', 'complexity_before', 'complexity_after',
            'methods_changed', 'fix_patterns', 'change_scope', 'risk_level',
            'change_categories'
        ]
        
        rectification_fieldnames = [
            'llm_inference', 'rectified_message',
            'original_alignment_score', 'llm_alignment_score', 'rectified_alignment_score',
            'improvement_achieved'
        ]
        
        fieldnames = base_fieldnames + rectification_fieldnames
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in rectified_data:
                # Prepare row for CSV (handle nested data)
                row = {}
                for field in fieldnames:
                    if field in record:
                        value = record[field]
                        # Convert lists to strings
                        if isinstance(value, list):
                            row[field] = '; '.join(str(item) for item in value)
                        else:
                            row[field] = value
                    else:
                        row[field] = ''
                
                # Truncate very long fields
                for field in ['source_code_before', 'source_code_current', 'diff']:
                    if field in row and len(str(row[field])) > 10000:
                        row[field] = str(row[field])[:10000] + "... [TRUNCATED]"
                
                writer.writerow(row)
        
        self.logger.info("Saved %d rectified records to %s", len(rectified_data), filepath)
    
    def get_rectification_statistics(self, rectified_data: List[Dict]) -> Dict:
        """
        Generate statistics about the rectification process
        """
        if not rectified_data:
            return {}
        
        total_records = len(rectified_data)
        improvements = sum(1 for record in rectified_data 
                          if record.get('improvement_achieved', False))
        
        avg_original_score = sum(record.get('original_alignment_score', 0) 
                               for record in rectified_data) / total_records
        avg_llm_score = sum(record.get('llm_alignment_score', 0) 
                          for record in rectified_data) / total_records
        avg_rectified_score = sum(record.get('rectified_alignment_score', 0) 
                                for record in rectified_data) / total_records
        
        stats = {
            'total_rectified': total_records,
            'improvements_achieved': improvements,
            'improvement_rate': improvements / total_records if total_records > 0 else 0,
            'avg_original_alignment': avg_original_score,
            'avg_llm_alignment': avg_llm_score,
            'avg_rectified_alignment': avg_rectified_score,
            'llm_success_rate': sum(1 for record in rectified_data 
                                  if record.get('llm_inference', '').strip()) / total_records,
            'score_improvement': avg_rectified_score - avg_original_score
        }
        
        return stats
