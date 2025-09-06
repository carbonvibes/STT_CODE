"""
Evaluator Module
This module evaluates the effectiveness of commit message rectification.
"""

import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

class Evaluator:
    """
    Class to evaluate the effectiveness of commit message rectification
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def evaluate_developer_precision(self, commits_data: List[Dict]) -> Dict:
        """
        RQ1: Evaluate developer commit message precision
        """
        self.logger.info("Evaluating developer commit message precision (RQ1)")
        
        if not commits_data:
            return {'error': 'No commit data provided'}
        
        # Analyze original commit messages
        precise_messages = 0
        total_messages = len(commits_data)
        
        precision_scores = []
        message_categories = {
            'specific': 0,
            'generic': 0,
            'very_generic': 0,
            'descriptive': 0
        }
        
        for commit in commits_data:
            message = commit.get('message', '').lower().strip()
            
            # Calculate precision score based on message characteristics
            score = self._calculate_developer_precision_score(commit)
            precision_scores.append(score)
            
            if score >= 0.7:
                precise_messages += 1
                message_categories['specific'] += 1
            elif score >= 0.5:
                message_categories['descriptive'] += 1
            elif score >= 0.3:
                message_categories['generic'] += 1
            else:
                message_categories['very_generic'] += 1
        
        hit_rate = precise_messages / total_messages if total_messages > 0 else 0
        avg_precision = np.mean(precision_scores) if precision_scores else 0
        
        result = {
            'total_commits': total_messages,
            'precise_messages': precise_messages,
            'hit_rate': hit_rate,
            'average_precision_score': avg_precision,
            'message_categories': message_categories,
            'precision_distribution': {
                'mean': np.mean(precision_scores),
                'std': np.std(precision_scores),
                'median': np.median(precision_scores),
                'min': np.min(precision_scores),
                'max': np.max(precision_scores)
            }
        }
        
        self.logger.info("Developer precision evaluation complete. Hit rate: %.2f", hit_rate)
        return result
    
    def _calculate_developer_precision_score(self, commit: Dict) -> float:
        """
        Calculate precision score for a developer's commit message
        """
        message = commit.get('message', '').lower().strip()
        
        if not message:
            return 0.0
        
        score = 0.0
        
        # Length and detail (longer messages tend to be more descriptive)
        if len(message) > 50:
            score += 0.2
        elif len(message) > 20:
            score += 0.1
        
        # Specific technical terms
        technical_terms = [
            'function', 'method', 'class', 'variable', 'parameter',
            'return', 'condition', 'loop', 'array', 'object',
            'null', 'exception', 'error', 'validation', 'parse'
        ]
        
        tech_terms_found = sum(1 for term in technical_terms if term in message)
        score += min(0.3, tech_terms_found * 0.1)
        
        # Action specificity
        specific_actions = [
            'fix', 'resolve', 'correct', 'handle', 'prevent',
            'add', 'remove', 'update', 'refactor', 'optimize'
        ]
        
        if any(action in message for action in specific_actions):
            score += 0.2
        
        # File or component specificity
        file_indicators = [
            '.py', '.java', '.js', '.cpp', '.c', '.h',
            'test', 'util', 'helper', 'config', 'api'
        ]
        
        if any(indicator in message for indicator in file_indicators):
            score += 0.1
        
        # Issue references
        import re
        if re.search(r'#\d+', message):
            score += 0.1
        
        # Penalize very generic messages
        generic_messages = [
            'fix', 'bug fix', 'update', 'change', 'misc', 'minor fix',
            'quick fix', 'small change', 'fix bug', 'fix issue'
        ]
        
        if message in generic_messages:
            score -= 0.3
        
        return max(0.0, min(1.0, score))
    
    def evaluate_llm_precision(self, rectified_data: List[Dict]) -> Dict:
        """
        RQ2: Evaluate LLM commit message precision
        """
        self.logger.info("Evaluating LLM commit message precision (RQ2)")
        
        if not rectified_data:
            return {'error': 'No rectified data provided'}
        
        llm_messages_with_content = []
        llm_precision_scores = []
        
        for record in rectified_data:
            llm_message = record.get('llm_inference', '').strip()
            if llm_message:  # Only evaluate non-empty LLM messages
                llm_messages_with_content.append(record)
                score = record.get('llm_alignment_score', 0)
                llm_precision_scores.append(score)
        
        total_llm_messages = len(llm_messages_with_content)
        precise_llm_messages = sum(1 for score in llm_precision_scores if score >= 0.7)
        
        hit_rate = precise_llm_messages / total_llm_messages if total_llm_messages > 0 else 0
        avg_precision = np.mean(llm_precision_scores) if llm_precision_scores else 0
        
        # Compare with original messages
        original_scores = [record.get('original_alignment_score', 0) 
                          for record in llm_messages_with_content]
        
        improvement_count = sum(1 for i, record in enumerate(llm_messages_with_content)
                               if record.get('llm_alignment_score', 0) > 
                               record.get('original_alignment_score', 0))
        
        result = {
            'total_llm_messages': total_llm_messages,
            'precise_llm_messages': precise_llm_messages,
            'hit_rate': hit_rate,
            'average_precision_score': avg_precision,
            'improvement_over_original': improvement_count / total_llm_messages if total_llm_messages > 0 else 0,
            'average_original_score': np.mean(original_scores) if original_scores else 0,
            'score_improvement': avg_precision - (np.mean(original_scores) if original_scores else 0),
            'llm_success_rate': total_llm_messages / len(rectified_data) if rectified_data else 0
        }
        
        self.logger.info("LLM precision evaluation complete. Hit rate: %.2f", hit_rate)
        return result
    
    def evaluate_rectifier_effectiveness(self, rectified_data: List[Dict]) -> Dict:
        """
        RQ3: Evaluate rectifier effectiveness
        """
        self.logger.info("Evaluating rectifier effectiveness (RQ3)")
        
        if not rectified_data:
            return {'error': 'No rectified data provided'}
        
        total_records = len(rectified_data)
        improvements = sum(1 for record in rectified_data 
                          if record.get('improvement_achieved', False))
        
        # Calculate score improvements
        original_scores = [record.get('original_alignment_score', 0) for record in rectified_data]
        rectified_scores = [record.get('rectified_alignment_score', 0) for record in rectified_data]
        
        score_improvements = [rectified_scores[i] - original_scores[i] 
                             for i in range(len(original_scores))]
        
        # Categorize improvements
        significant_improvements = sum(1 for imp in score_improvements if imp >= 0.3)
        moderate_improvements = sum(1 for imp in score_improvements if 0.1 <= imp < 0.3)
        minor_improvements = sum(1 for imp in score_improvements if 0.0 < imp < 0.1)
        no_change = sum(1 for imp in score_improvements if imp == 0.0)
        degradations = sum(1 for imp in score_improvements if imp < 0.0)
        
        # Calculate hit rate (successful rectifications)
        hit_rate = improvements / total_records if total_records > 0 else 0
        
        result = {
            'total_rectified': total_records,
            'successful_rectifications': improvements,
            'hit_rate': hit_rate,
            'average_score_improvement': np.mean(score_improvements),
            'median_score_improvement': np.median(score_improvements),
            'improvement_categories': {
                'significant': significant_improvements,
                'moderate': moderate_improvements,
                'minor': minor_improvements,
                'no_change': no_change,
                'degradations': degradations
            },
            'before_after_comparison': {
                'avg_original': np.mean(original_scores),
                'avg_rectified': np.mean(rectified_scores),
                'improvement_ratio': np.mean(rectified_scores) / np.mean(original_scores) if np.mean(original_scores) > 0 else 0
            }
        }
        
        self.logger.info("Rectifier evaluation complete. Hit rate: %.2f", hit_rate)
        return result
    
    def evaluate_all(self, original_commits: List[Dict], diff_data: List[Dict], 
                    rectified_data: List[Dict]) -> Dict:
        """
        Perform comprehensive evaluation covering all research questions
        """
        self.logger.info("Starting comprehensive evaluation")
        
        evaluation_results = {
            'rq1_developer_evaluation': self.evaluate_developer_precision(original_commits),
            'rq2_llm_evaluation': self.evaluate_llm_precision(rectified_data),
            'rq3_rectifier_evaluation': self.evaluate_rectifier_effectiveness(rectified_data),
            'overall_statistics': self._calculate_overall_statistics(
                original_commits, diff_data, rectified_data
            )
        }
        
        self.logger.info("Comprehensive evaluation completed")
        return evaluation_results
    
    def _calculate_overall_statistics(self, original_commits: List[Dict], 
                                    diff_data: List[Dict], 
                                    rectified_data: List[Dict]) -> Dict:
        """
        Calculate overall statistics across all data
        """
        stats = {
            'data_summary': {
                'total_commits_analyzed': len(original_commits),
                'total_file_changes': len(diff_data),
                'total_rectifications': len(rectified_data)
            }
        }
        
        if original_commits:
            # Commit statistics
            authors = set(commit.get('author', '') for commit in original_commits)
            total_lines_changed = sum(
                commit.get('lines_added', 0) + commit.get('lines_deleted', 0)
                for commit in original_commits
            )
            
            stats['commit_statistics'] = {
                'unique_authors': len(authors),
                'total_lines_changed': total_lines_changed,
                'avg_lines_per_commit': total_lines_changed / len(original_commits),
                'avg_files_per_commit': sum(commit.get('files_changed', 0) 
                                           for commit in original_commits) / len(original_commits)
            }
        
        if rectified_data:
            # Rectification effectiveness
            improvement_rate = sum(1 for record in rectified_data 
                                 if record.get('improvement_achieved', False)) / len(rectified_data)
            
            avg_original = np.mean([record.get('original_alignment_score', 0) 
                                  for record in rectified_data])
            avg_rectified = np.mean([record.get('rectified_alignment_score', 0) 
                                   for record in rectified_data])
            
            stats['rectification_effectiveness'] = {
                'overall_improvement_rate': improvement_rate,
                'average_score_before': avg_original,
                'average_score_after': avg_rectified,
                'relative_improvement': (avg_rectified - avg_original) / avg_original if avg_original > 0 else 0
            }
        
        return stats
    
    def generate_visualizations(self, evaluation_results: Dict, output_dir: Path):
        """
        Generate visualization plots for the evaluation results
        """
        self.logger.info("Generating evaluation visualizations")
        
        # Set style
        plt.style.use('seaborn-v0_8')
        
        # RQ1: Developer Precision Distribution
        if 'rq1_developer_evaluation' in evaluation_results:
            rq1_data = evaluation_results['rq1_developer_evaluation']
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Message categories pie chart
            categories = rq1_data.get('message_categories', {})
            if categories:
                ax1.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%')
                ax1.set_title('Developer Message Categories (RQ1)')
            
            # Hit rate comparison
            hit_rates = [
                rq1_data.get('hit_rate', 0),
                evaluation_results.get('rq2_llm_evaluation', {}).get('hit_rate', 0),
                evaluation_results.get('rq3_rectifier_evaluation', {}).get('hit_rate', 0)
            ]
            labels = ['Developers', 'LLM', 'Rectifier']
            
            ax2.bar(labels, hit_rates, color=['skyblue', 'lightcoral', 'lightgreen'])
            ax2.set_ylabel('Hit Rate')
            ax2.set_title('Precision Hit Rate Comparison')
            ax2.set_ylim(0, 1)
            
            # Add value labels on bars
            for i, v in enumerate(hit_rates):
                ax2.text(i, v + 0.01, f'{v:.2f}', ha='center', va='bottom')
            
            plt.tight_layout()
            plt.savefig(output_dir / 'rq1_developer_evaluation.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # RQ3: Rectifier Improvement Analysis
        if 'rq3_rectifier_evaluation' in evaluation_results:
            rq3_data = evaluation_results['rq3_rectifier_evaluation']
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Improvement categories
            improvements = rq3_data.get('improvement_categories', {})
            if improvements:
                ax1.bar(improvements.keys(), improvements.values(), 
                       color=['darkgreen', 'green', 'lightgreen', 'gray', 'red'])
                ax1.set_ylabel('Number of Cases')
                ax1.set_title('Rectification Improvement Categories (RQ3)')
                ax1.tick_params(axis='x', rotation=45)
            
            # Before vs After comparison
            before_after = rq3_data.get('before_after_comparison', {})
            if before_after:
                categories = ['Before Rectification', 'After Rectification']
                scores = [before_after.get('avg_original', 0), before_after.get('avg_rectified', 0)]
                
                bars = ax2.bar(categories, scores, color=['lightcoral', 'lightgreen'])
                ax2.set_ylabel('Average Alignment Score')
                ax2.set_title('Before vs After Rectification')
                ax2.set_ylim(0, 1)
                
                # Add value labels
                for bar, score in zip(bars, scores):
                    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                            f'{score:.3f}', ha='center', va='bottom')
            
            plt.tight_layout()
            plt.savefig(output_dir / 'rq3_rectifier_evaluation.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        self.logger.info("Visualizations saved to %s", output_dir)
