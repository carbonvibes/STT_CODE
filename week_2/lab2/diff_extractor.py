"""
Diff Extraction Module
This module extracts and analyzes diffs for bug-fixing commits.
"""

import csv
import logging
import tempfile
import shutil
from collections import Counter
from typing import List, Dict, Tuple
from pathlib import Path
from pydriller import Repository
from git import Repo
import difflib

class DiffExtractor:
    """
    Class to extract and analyze diffs from bug-fixing commits
    """
    
    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        self.logger = logging.getLogger(__name__)
        self.local_repo_path = None
    
    def _clone_repository(self) -> str:
        """
        Clone repository to temporary directory for analysis
        """
        if self.local_repo_path and Path(self.local_repo_path).exists():
            return self.local_repo_path
        
        temp_dir = tempfile.mkdtemp()
        self.local_repo_path = temp_dir
        
        try:
            self.logger.info("Cloning repository for diff extraction: %s", self.repo_url)
            Repo.clone_from(self.repo_url, temp_dir)
            return temp_dir
        except Exception as e:
            self.logger.error("Failed to clone repository: %s", str(e))
            raise
    
    def extract_diffs(self, bug_fixing_commits: List[Dict]) -> List[Dict]:
        """
        Extract diffs for each file in each bug-fixing commit
        """
        self.logger.info("Starting diff extraction for %d commits", len(bug_fixing_commits))
        
        repo_path = self._clone_repository()
        diff_data = []
        
        try:
            repo = Repository(repo_path)
            
            for commit_info in bug_fixing_commits:
                commit_hash = commit_info['hash']
                
                # Get the actual commit object
                commit = None
                for c in repo.traverse_commits():
                    if c.hash == commit_hash:
                        commit = c
                        break
                
                if not commit:
                    self.logger.warning("Commit %s not found", commit_hash)
                    continue
                
                # Extract diffs for each modified file
                for mod_file in commit.modified_files:
                    if not mod_file.filename:
                        continue
                    
                    file_diff_info = self._analyze_file_diff(commit, mod_file, commit_info)
                    if file_diff_info:
                        diff_data.append(file_diff_info)
                
                self.logger.info("Processed diffs for commit: %s", commit_hash[:8])
        
        except Exception as e:
            self.logger.error("Error during diff extraction: %s", str(e))
            raise
        
        self.logger.info("Extracted diffs for %d file modifications", len(diff_data))
        return diff_data
    
    def _analyze_file_diff(self, commit, modified_file, commit_info: Dict) -> Dict:
        """
        Analyze diff for a single file modification
        """
        try:
            # Get source code before and after
            source_before = modified_file.source_code_before or ""
            source_current = modified_file.source_code or ""
            
            # Generate unified diff
            diff_lines = list(difflib.unified_diff(
                source_before.splitlines(keepends=True),
                source_current.splitlines(keepends=True),
                fromfile=f"a/{modified_file.filename}",
                tofile=f"b/{modified_file.filename}",
                lineterm=""
            ))
            
            unified_diff = ''.join(diff_lines)
            
            # Analyze the changes
            change_analysis = self._analyze_change_patterns(modified_file, unified_diff)
            
            # Helper function to safely get line counts
            def safe_line_count(line_data):
                if line_data is None:
                    return 0
                elif isinstance(line_data, int):
                    return line_data
                elif isinstance(line_data, (list, tuple)):
                    return len(line_data)
                else:
                    return 0
            
            file_diff_info = {
                'hash': commit.hash,
                'message': commit.msg,
                'filename': modified_file.filename,
                'change_type': modified_file.change_type.name,
                'source_code_before': source_before,
                'source_code_current': source_current,
                'diff': unified_diff,
                'lines_added': safe_line_count(modified_file.added_lines),
                'lines_deleted': safe_line_count(modified_file.deleted_lines),
                'complexity_before': getattr(modified_file, 'complexity_before', 0) or 0,
                'complexity_after': getattr(modified_file, 'complexity', 0) or 0,
                'methods_changed': len(modified_file.changed_methods) if modified_file.changed_methods else 0,
                'change_analysis': change_analysis,
                'llm_inference': "",  # To be filled by LLM
                'rectified_message': ""  # To be filled by rectifier
            }
            
            return file_diff_info
            
        except Exception as e:
            self.logger.error("Error analyzing diff for %s: %s", modified_file.filename, str(e))
            return None
    
    def _analyze_change_patterns(self, modified_file, unified_diff: str) -> Dict:
        """
        Analyze patterns in the code changes
        """
        analysis = {
            'fix_patterns': [],
            'change_scope': 'unknown',
            'risk_level': 'low',
            'change_categories': []
        }
        
        diff_lower = unified_diff.lower()
        
        # Detect common fix patterns
        fix_patterns = {
            'null_check': ['null', 'none', 'nullptr'],
            'bounds_check': ['index', 'bound', 'range', 'length'],
            'error_handling': ['try', 'catch', 'except', 'error', 'exception'],
            'initialization': ['init', 'initialize', 'default'],
            'condition_fix': ['if', 'else', 'condition', '==', '!='],
            'resource_management': ['close', 'dispose', 'free', 'release']
        }
        
        for pattern_name, keywords in fix_patterns.items():
            if any(keyword in diff_lower for keyword in keywords):
                analysis['fix_patterns'].append(pattern_name)
        
        # Determine change scope - handle PyDriller inconsistencies
        try:
            # Handle added_lines - could be int, list, or None
            if hasattr(modified_file, 'added_lines') and modified_file.added_lines is not None:
                if isinstance(modified_file.added_lines, int):
                    added_lines = modified_file.added_lines
                elif isinstance(modified_file.added_lines, (list, tuple)):
                    added_lines = len(modified_file.added_lines)
                else:
                    added_lines = 0
            else:
                added_lines = 0
            
            # Handle deleted_lines - could be int, list, or None
            if hasattr(modified_file, 'deleted_lines') and modified_file.deleted_lines is not None:
                if isinstance(modified_file.deleted_lines, int):
                    deleted_lines = modified_file.deleted_lines
                elif isinstance(modified_file.deleted_lines, (list, tuple)):
                    deleted_lines = len(modified_file.deleted_lines)
                else:
                    deleted_lines = 0
            else:
                deleted_lines = 0
                
            lines_changed = added_lines + deleted_lines
        except Exception as e:
            # Fallback if everything fails
            lines_changed = 0
        if lines_changed <= 5:
            analysis['change_scope'] = 'minimal'
        elif lines_changed <= 20:
            analysis['change_scope'] = 'small'
        elif lines_changed <= 100:
            analysis['change_scope'] = 'medium'
        else:
            analysis['change_scope'] = 'large'
        
        # Assess risk level
        try:
            methods_count = len(modified_file.changed_methods) if (
                hasattr(modified_file, 'changed_methods') and
                modified_file.changed_methods
            ) else 0
        except:
            methods_count = 0
            
        risk_indicators = [
            'delete' in diff_lower and 'file' in diff_lower,
            methods_count > 5,
            lines_changed > 100,
            'critical' in unified_diff.lower(),
            'unsafe' in unified_diff.lower()
        ]
        
        if sum(risk_indicators) >= 2:
            analysis['risk_level'] = 'high'
        elif sum(risk_indicators) == 1:
            analysis['risk_level'] = 'medium'
        
        # Categorize changes
        categories = []
        
        # Use safe line counts for categorization
        safe_added = (added_lines if isinstance(added_lines, int)
                     else len(added_lines) if added_lines else 0)
        safe_deleted = (deleted_lines if isinstance(deleted_lines, int)
                       else len(deleted_lines) if deleted_lines else 0)
        
        if safe_added > safe_deleted * 2:
            categories.append('feature_addition')
        elif safe_deleted > safe_added * 2:
            categories.append('code_removal')
        else:
            categories.append('modification')
        
        if 'test' in modified_file.filename.lower():
            categories.append('test_change')
        elif modified_file.filename.endswith(('.md', '.txt', '.rst')):
            categories.append('documentation')
        else:
            categories.append('source_code')
        
        analysis['change_categories'] = categories
        
        return analysis
    
    def save_diffs_to_csv(self, diff_data: List[Dict], filepath: Path):
        """
        Save diff data to CSV file
        """
        if not diff_data:
            self.logger.warning("No diff data to save")
            return
        
        fieldnames = [
            'hash', 'message', 'filename', 'change_type',
            'source_code_before', 'source_code_current', 'diff',
            'lines_added', 'lines_deleted', 'complexity_before', 'complexity_after',
            'methods_changed', 'fix_patterns', 'change_scope', 'risk_level',
            'change_categories', 'llm_inference', 'rectified_message'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for diff_info in diff_data:
                # Flatten the change_analysis dict
                row = diff_info.copy()
                change_analysis = row.pop('change_analysis', {})
                
                # Add analysis fields to row
                row['fix_patterns'] = '; '.join(change_analysis.get('fix_patterns', []))
                row['change_scope'] = change_analysis.get('change_scope', '')
                row['risk_level'] = change_analysis.get('risk_level', '')
                row['change_categories'] = '; '.join(change_analysis.get('change_categories', []))
                
                # Truncate very long fields to prevent CSV issues
                for field in ['source_code_before', 'source_code_current', 'diff']:
                    if field in row and len(str(row[field])) > 10000:
                        row[field] = str(row[field])[:10000] + "... [TRUNCATED]"
                
                writer.writerow(row)
        
        self.logger.info("Saved %d diff records to %s", len(diff_data), filepath)
    
    def get_diff_statistics(self, diff_data: List[Dict]) -> Dict:
        """
        Generate statistics about the extracted diffs
        """
        if not diff_data:
            return {}
        
        # Collect all fix patterns
        all_fix_patterns = []
        for diff in diff_data:
            change_analysis = diff.get('change_analysis', {})
            all_fix_patterns.extend(change_analysis.get('fix_patterns', []))
        
        # Collect file extensions
        file_extensions = []
        for diff in diff_data:
            filename = diff.get('filename', '')
            if '.' in filename:
                ext = '.' + filename.split('.')[-1]
                file_extensions.append(ext)
        
        stats = {
            'total_file_changes': len(diff_data),
            'unique_files': len(set(diff['filename'] for diff in diff_data)),
            'avg_lines_added': sum(diff['lines_added'] for diff in diff_data) / len(diff_data),
            'avg_lines_deleted': sum(diff['lines_deleted'] for diff in diff_data) / len(diff_data),
            'change_scopes': Counter(
                diff.get('change_analysis', {}).get('change_scope', 'unknown')
                for diff in diff_data
            ),
            'risk_levels': Counter(
                diff.get('change_analysis', {}).get('risk_level', 'unknown')
                for diff in diff_data
            ),
            'fix_patterns': Counter(all_fix_patterns),
            'file_types': Counter(file_extensions),
            'change_types': Counter(diff.get('change_type', 'unknown') for diff in diff_data)
        }
        
        return stats
    
    def __del__(self):
        """
        Cleanup temporary repository directory
        """
        if self.local_repo_path and Path(self.local_repo_path).exists():
            try:
                shutil.rmtree(self.local_repo_path)
            except (OSError, PermissionError):
                pass  # Silent cleanup failure
