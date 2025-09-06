"""
Repository Selection Module
This module handles the selection and analysis of GitHub repositories based on defined criteria.
"""

import requests
import json
import logging
import os
from typing import Dict, List, Optional
from pathlib import Path

class RepositorySelector:
    """
    Class to handle repository selection based on defined criteria
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.github_token = os.getenv('GITHUB_TOKEN')
        if self.github_token:
            self.logger.info("Using GitHub Personal Access Token for API access")
        else:
            self.logger.warning("No GitHub token found. API calls may be rate limited.")
        
        self.selection_criteria = {
            'min_stars': 1000,
            'min_forks': 100,
            'primary_language': ['Python', 'JavaScript', 'Java', 'C++', 'C', 'Go'],
            'min_commits': 500,
            'has_issues': True,
            'not_archived': True
        }
    
    def search_repositories(self, query: str = "", language: str = "Python",
                          sort: str = "stars", per_page: int = 30) -> List[Dict]:
        """
        Search for repositories using GitHub API
        """
        base_url = "https://api.github.com/search/repositories"
        
        # Build search query
        search_query = f"language:{language} stars:>={self.selection_criteria['min_stars']}"
        if query:
            search_query = f"{query} {search_query}"
        
        params = {
            'q': search_query,
            'sort': sort,
            'order': 'desc',
            'per_page': per_page
        }
        
        headers = {}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            return response.json().get('items', [])
        except requests.RequestException as e:
            self.logger.error("Error searching repositories: %s", str(e))
            return []
    
    def analyze_repository(self, repo_url: str) -> Dict:
        """
        Analyze a specific repository to gather metadata
        """
        # Extract owner and repo name from URL
        parts = repo_url.rstrip('/').split('/')
        owner, repo = parts[-2], parts[-1]
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        
        headers = {}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            repo_data = response.json()
            
            # Get additional statistics
            commits_url = f"{api_url}/commits"
            commits_response = requests.get(commits_url, params={'per_page': 1}, headers=headers)
            total_commits = self._get_total_commits_estimate(commits_response)
            
            analysis = {
                'name': repo_data['name'],
                'full_name': repo_data['full_name'],
                'description': repo_data.get('description', ''),
                'language': repo_data.get('language', ''),
                'stars': repo_data['stargazers_count'],
                'forks': repo_data['forks_count'],
                'open_issues': repo_data['open_issues_count'],
                'size': repo_data['size'],
                'created_at': repo_data['created_at'],
                'updated_at': repo_data['updated_at'],
                'archived': repo_data['archived'],
                'estimated_commits': total_commits,
                'clone_url': repo_data['clone_url'],
                'selection_criteria_met': self._check_criteria(repo_data, total_commits)
            }
            
            return analysis
            
        except requests.RequestException as e:
            self.logger.error("Error analyzing repository %s: %s", repo_url, str(e))
            return {}
    
    def _get_total_commits_estimate(self, response) -> int:
        """
        Estimate total commits from response headers
        """
        link_header = response.headers.get('Link', '')
        if 'last' in link_header:
            # Parse the last page number
            import re
            match = re.search(r'page=(\d+)>; rel="last"', link_header)
            if match:
                return int(match.group(1)) * 30  # Approximate
        return 100  # Default estimate
    
    def _check_criteria(self, repo_data: Dict, total_commits: int) -> Dict[str, bool]:
        """
        Check if repository meets selection criteria
        """
        criteria_met = {
            'min_stars': repo_data['stargazers_count'] >= self.selection_criteria['min_stars'],
            'min_forks': repo_data['forks_count'] >= self.selection_criteria['min_forks'],
            'primary_language': repo_data.get('language') in self.selection_criteria['primary_language'],
            'min_commits': total_commits >= self.selection_criteria['min_commits'],
            'has_issues': repo_data['open_issues_count'] > 0,
            'not_archived': not repo_data['archived']
        }
        return criteria_met
    
    def select_repository(self) -> str:
        """
        Interactive repository selection process
        """
        print("Repository Selection Process")
        print("=" * 40)
        
        # Show selection criteria
        print("Selection Criteria:")
        for key, value in self.selection_criteria.items():
            print(f"  - {key}: {value}")
        print()
        
        # Search for repositories
        language = input("Enter primary language (default: Python): ").strip() or "Python"
        query = input("Enter additional search terms (optional): ").strip()
        
        repositories = self.search_repositories(query=query, language=language)
        
        if not repositories:
            print("No repositories found matching criteria.")
            return ""
        
        print(f"\nFound {len(repositories)} repositories:")
        print("-" * 60)
        
        for i, repo in enumerate(repositories[:10], 1):
            print(f"{i:2d}. {repo['full_name']}")
            print(f"    ⭐ {repo['stargazers_count']} stars | "
                  f"🍴 {repo['forks_count']} forks | "
                  f"📝 {repo['language']}")
            print(f"    📋 {repo.get('description', 'No description')[:80]}...")
            print()
        
        # Let user select
        while True:
            try:
                choice = input("Select repository (1-10) or enter GitHub URL: ").strip()
                
                if choice.startswith('http'):
                    return choice
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(repositories):
                    selected_repo = repositories[choice_num - 1]
                    return selected_repo['html_url']
                else:
                    print("Invalid choice. Please try again.")
                    
            except ValueError:
                print("Invalid input. Please enter a number or URL.")
    
    def save_selection_report(self, repo_info: Dict, filepath: Path):
        """
        Save repository selection justification report
        """
        report = [
            "Repository Selection Report",
            "=" * 30,
            "",
            f"Selected Repository: {repo_info.get('full_name', 'N/A')}",
            f"GitHub URL: {repo_info.get('clone_url', 'N/A')}",
            "",
            "Repository Metrics:",
            f"  - Stars: {repo_info.get('stars', 0):,}",
            f"  - Forks: {repo_info.get('forks', 0):,}",
            f"  - Primary Language: {repo_info.get('language', 'N/A')}",
            f"  - Estimated Commits: {repo_info.get('estimated_commits', 0):,}",
            f"  - Open Issues: {repo_info.get('open_issues', 0):,}",
            f"  - Repository Size: {repo_info.get('size', 0):,} KB",
            "",
            "Selection Criteria Assessment:",
        ]
        
        criteria_met = repo_info.get('selection_criteria_met', {})
        for criterion, met in criteria_met.items():
            status = "✅ PASSED" if met else "❌ FAILED"
            report.append(f"  - {criterion}: {status}")
        
        report.extend([
            "",
            "Justification:",
            "This repository was selected based on the following factors:",
            "1. High community engagement (stars and forks)",
            "2. Active development (recent commits and issues)",
            "3. Substantial codebase for meaningful analysis",
            "4. Popular programming language for better tool support",
            "5. Open source nature allowing full commit history access"
        ])
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        self.logger.info("Repository selection report saved to %s", filepath)


# Example repositories that meet criteria (fallback options)
EXAMPLE_REPOSITORIES = [
    "https://github.com/torvalds/linux",
    "https://github.com/pallets/flask",
    "https://github.com/django/django", 
    "https://github.com/psf/requests",
    "https://github.com/numpy/numpy",
    "https://github.com/scikit-learn/scikit-learn",
    "https://github.com/pandas-dev/pandas"
]
