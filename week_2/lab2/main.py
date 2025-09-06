#!/usr/bin/env python3
"""
Lab Assignment 2: Commit Message Rectification for Bug-Fixing Commits in the Wild
Course: CS202 Software Tools and Techniques for CSE
Date: 11th August 2025

This is the main script that orchestrates the entire analysis pipeline.
"""

import sys
import argparse
import logging
from pathlib import Path

# Import our custom modules
from repository_selector import RepositorySelector
from commit_analyzer import CommitAnalyzer
from diff_extractor import DiffExtractor
from message_rectifier import MessageRectifier
from evaluator import Evaluator
from report_generator import ReportGenerator

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('lab2_analysis.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main function to run the complete analysis pipeline"""
    parser = argparse.ArgumentParser(
        description='Analyze bug-fixing commits and rectify commit messages'
    )
    parser.add_argument('--repo-url', type=str,
                       help='GitHub repository URL to analyze')
    parser.add_argument('--output-dir', type=str, default='output',
                       help='Output directory for results')
    parser.add_argument('--max-commits', type=int, default=100,
                       help='Maximum number of commits to analyze')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Lab Assignment 2 Analysis")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Step 1: Repository Selection
        logger.info("Step 1: Repository Selection")
        if args.repo_url:
            repo_selector = RepositorySelector()
            repo_info = repo_selector.analyze_repository(args.repo_url)
            selected_repo = args.repo_url
        else:
            repo_selector = RepositorySelector()
            selected_repo = repo_selector.select_repository()
            repo_info = repo_selector.analyze_repository(selected_repo)
        
        logger.info("Selected repository: %s", selected_repo)
        
        # Step 2: Bug-Fixing Commit Identification
        logger.info("Step 2: Bug-Fixing Commit Identification")
        commit_analyzer = CommitAnalyzer(selected_repo)
        bug_fixing_commits = commit_analyzer.identify_bug_fixing_commits(
            max_commits=args.max_commits
        )
        
        # Save commit data
        commits_file = output_dir / 'bug_fixing_commits.csv'
        commit_analyzer.save_commits_to_csv(bug_fixing_commits, commits_file)
        logger.info("Saved %d bug-fixing commits to %s", len(bug_fixing_commits), commits_file)
        
        # Step 3: Diff Extraction and Analysis
        logger.info("Step 3: Diff Extraction and Analysis")
        diff_extractor = DiffExtractor(selected_repo)
        diff_data = diff_extractor.extract_diffs(bug_fixing_commits)
        
        # Save diff data
        diffs_file = output_dir / 'commit_diffs.csv'
        diff_extractor.save_diffs_to_csv(diff_data, diffs_file)
        logger.info("Saved diff data to %s", diffs_file)
        
        # Step 4: Message Rectification
        logger.info("Step 4: Message Rectification")
        rectifier = MessageRectifier()
        rectified_data = rectifier.rectify_messages(diff_data)
        
        # Save rectified data
        rectified_file = output_dir / 'rectified_messages.csv'
        rectifier.save_rectified_data(rectified_data, rectified_file)
        logger.info("Saved rectified data to %s", rectified_file)
        
        # Step 5: Evaluation
        logger.info("Step 5: Evaluation")
        evaluator = Evaluator()
        evaluation_results = evaluator.evaluate_all(
            original_commits=bug_fixing_commits,
            diff_data=diff_data,
            rectified_data=rectified_data
        )
        
        # Step 6: Report Generation
        logger.info("Step 6: Report Generation")
        report_generator = ReportGenerator(output_dir)
        report_generator.generate_comprehensive_report(
            repo_info=repo_info,
            commits_data=bug_fixing_commits,
            diff_data=diff_data,
            rectified_data=rectified_data,
            evaluation_results=evaluation_results
        )
        
        logger.info("Analysis completed successfully!")
        logger.info("Results saved in: %s", output_dir)
        
    except Exception as e:
        logger.error("An error occurred: %s", str(e))
        raise

if __name__ == "__main__":
    main()
