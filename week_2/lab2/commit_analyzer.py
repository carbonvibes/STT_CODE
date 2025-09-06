"""
Commit Analyzer Module
This module identifies bug-fixing commits from a repository using various heuristics.
"""

import re
import csv
import logging
import tempfile
import shutil
from typing import List, Dict, Set
from pathlib import Path
from pydriller import Repository
from git import Repo

class CommitAnalyzer:
    """
    Class to identify and analyze bug-fixing commits
    """
    
    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        self.logger = logging.getLogger(__name__)
        self.bug_keywords = [
            'fix', 'bug', 'error', 'issue', 'problem', 'resolve', 'solve',
            'patch', 'correct', 'repair', 'debug', 'defect', 'fault',
            'crash', 'exception', 'failure', 'broken', 'hotfix'
        ]
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
            self.logger.info("Cloning repository: %s", self.repo_url)
            Repo.clone_from(self.repo_url, temp_dir)
            self.logger.info("Repository cloned to: %s", temp_dir)
            return temp_dir
        except Exception as e:
            self.logger.error("Failed to clone repository: %s", str(e))
            raise
    
    def _is_bug_fixing_commit(self, commit) -> bool:
        """
        Determine if a commit is bug-fixing based on multiple heuristics
        """
        message = commit.msg.lower()
        
        # Heuristic 1: Keywords in commit message
        keyword_match = any(keyword in message for keyword in self.bug_keywords)
        
        # Heuristic 2: Issue references (e.g., "fixes #123", "closes #456")
        issue_pattern = r'(fix|fixes|fixed|close|closes|closed|resolve|resolves|resolved)\s*#\d+'
        issue_reference = bool(re.search(issue_pattern, message, re.IGNORECASE))
        
        # Heuristic 3: Files modified (focus on source code files)
        source_files_modified = any(
            self._is_source_file(mod.filename) 
            for mod in commit.modified_files
        )
        
        # Heuristic 4: Small to medium sized changes (typically bug fixes)
        lines_changed = sum(mod.added_lines + mod.deleted_lines for mod in commit.modified_files)
        reasonable_size = 1 <= lines_changed <= 500
        
        # Heuristic 5: Not a merge commit (merge commits are typically not direct bug fixes)
        not_merge = len(commit.parents) <= 1
        
        # Combine heuristics
        is_bug_fix = (keyword_match or issue_reference) and source_files_modified and reasonable_size and not_merge
        
        return is_bug_fix
    
    def _is_source_file(self, filename: str) -> bool:
        """
        Check if file is a source code file
        """
        if not filename:
            return False
        
        source_extensions = {
            '.py', '.java', '.js', '.cpp', '.c', '.h', '.hpp', '.cs', '.rb',
            '.php', '.go', '.rs', '.swift', '.kt', '.scala', '.ts', '.jsx',
            '.tsx', '.vue', '.html', '.css', '.scss', '.less'
        }
        
        return any(filename.lower().endswith(ext) for ext in source_extensions)
    
    def identify_bug_fixing_commits(self, max_commits: int = 100) -> List[Dict]:
        """
        Identify bug-fixing commits from the repository
        """
        self.logger.info("Starting bug-fixing commit identification")
        
        repo_path = self._clone_repository()
        bug_fixing_commits = []
        
        try:
            # Use pydriller to traverse commits
            repo = Repository(repo_path)
            
            commit_count = 0
            analyzed_count = 0
            
            for commit in repo.traverse_commits():
                analyzed_count += 1
                
                if self._is_bug_fixing_commit(commit):
                    commit_info = {
                        'hash': commit.hash,
                        'message': commit.msg,
                        'author': commit.author.name,
                        'author_email': commit.author.email,
                        'date': commit.committer_date.isoformat(),
                        'parent_hashes': [parent for parent in commit.parents],
                        'is_merge_commit': len(commit.parents) > 1,
                        'modified_files': [mod.filename for mod in commit.modified_files if mod.filename],
                        'lines_added': sum(mod.added_lines for mod in commit.modified_files),
                        'lines_deleted': sum(mod.deleted_lines for mod in commit.modified_files),
                        'files_changed': len(commit.modified_files),
                        'bug_indicators': self._extract_bug_indicators(commit)
                    }
                    
                    bug_fixing_commits.append(commit_info)
                    commit_count += 1
                    
                    self.logger.info("Found bug-fixing commit: %s", commit.hash[:8])
                    
                    if commit_count >= max_commits:
                        break
                
                # Log progress every 100 commits
                if analyzed_count % 100 == 0:
                    self.logger.info("Analyzed %d commits, found %d bug fixes", 
                                   analyzed_count, commit_count)
            
            self.logger.info("Analysis complete. Found %d bug-fixing commits out of %d analyzed", 
                           len(bug_fixing_commits), analyzed_count)
            
        except Exception as e:
            self.logger.error("Error during commit analysis: %s", str(e))
            raise
        
        return bug_fixing_commits
    
    def _extract_bug_indicators(self, commit) -> Dict:
        """
        Extract specific bug indicators from commit
        """
        message = commit.msg.lower()
        
        indicators = {
            'keywords_found': [kw for kw in self.bug_keywords if kw in message],
            'issue_references': re.findall(r'#\d+', commit.msg),
            'urgency_indicators': [],
            'bug_type_hints': []
        }
        
        # Check for urgency indicators
        urgency_words = ['urgent', 'critical', 'hotfix', 'emergency', 'immediate']
        indicators['urgency_indicators'] = [word for word in urgency_words if word in message]
        
        # Check for bug type hints
        bug_types = {
            'crash': ['crash', 'segfault', 'abort', 'exit'],
            'memory': ['memory', 'leak', 'allocation', 'free'],
            'logic': ['logic', 'algorithm', 'calculation', 'condition'],
            'ui': ['ui', 'interface', 'display', 'render', 'visual'],
            'performance': ['performance', 'slow', 'optimize', 'speed'],
            'security': ['security', 'vulnerability', 'exploit', 'safe']
        }
        
        for bug_type, keywords in bug_types.items():
            if any(keyword in message for keyword in keywords):
                indicators['bug_type_hints'].append(bug_type)
        
        return indicators
    
    def save_commits_to_csv(self, commits: List[Dict], filepath: Path):
        """
        Save commit data to CSV file
        """
        if not commits:
            self.logger.warning("No commits to save")
            return
        
        fieldnames = [
            'hash', 'message', 'author', 'author_email', 'date',
            'parent_hashes', 'is_merge_commit', 'modified_files',
            'lines_added', 'lines_deleted', 'files_changed',
            'keywords_found', 'issue_references', 'urgency_indicators', 'bug_type_hints'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for commit in commits:
                # Flatten the bug_indicators dict
                row = commit.copy()
                indicators = row.pop('bug_indicators', {})
                row.update(indicators)
                
                # Convert lists to strings for CSV
                for field in ['parent_hashes', 'modified_files', 'keywords_found', 
                             'issue_references', 'urgency_indicators', 'bug_type_hints']:
                    if field in row and isinstance(row[field], list):
                        row[field] = '; '.join(str(item) for item in row[field])
                
                writer.writerow(row)
        
        self.logger.info("Saved %d commits to %s", len(commits), filepath)
    
    def get_commit_statistics(self, commits: List[Dict]) -> Dict:
        """
        Generate statistics about the identified commits
        """
        if not commits:
            return {}
        
        stats = {
            'total_commits': len(commits),
            'merge_commits': sum(1 for c in commits if c['is_merge_commit']),
            'avg_files_changed': sum(c['files_changed'] for c in commits) / len(commits),
            'total_lines_changed': sum(c['lines_added'] + c['lines_deleted'] for c in commits),
            'authors': len(set(c['author'] for c in commits)),
            'most_common_keywords': {},
            'bug_types_distribution': {}
        }
        
        # Analyze keywords
        all_keywords = []
        for commit in commits:
            indicators = commit.get('bug_indicators', {})
            all_keywords.extend(indicators.get('keywords_found', []))
        
        from collections import Counter
        stats['most_common_keywords'] = dict(Counter(all_keywords).most_common(10))
        
        # Analyze bug types
        all_bug_types = []
        for commit in commits:
            indicators = commit.get('bug_indicators', {})
            all_bug_types.extend(indicators.get('bug_type_hints', []))
        
        stats['bug_types_distribution'] = dict(Counter(all_bug_types))
        
        return stats
    
    def __del__(self):
        """
        Cleanup temporary repository directory
        """
        if self.local_repo_path and Path(self.local_repo_path).exists():
            try:
                shutil.rmtree(self.local_repo_path)
            except Exception:
                pass  # Silent cleanup failure
