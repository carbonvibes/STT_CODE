"""
Bug-Fixing Commit Analysis Orchestrator
This script orchestrates the full lab pipeline to satisfy the assignment:
- Repository selection and analysis
- Bug-fixing commit identification and CSV export
- Diff extraction and CSV export
- Message rectification (LLM + rule-based) and CSV export
- Evaluation (RQ1, RQ2, RQ3) and visualizations
- Report generation (Markdown + JSON + CSV summaries)

Usage:
    python bug_commit_analyzer.py --repo-url <url> --max-commits 50 --output-dir results

Defaults are chosen to be safe for development (smaller numbers and local output dir).
"""

import argparse
import logging
from pathlib import Path
import csv

from repository_selector import RepositorySelector
from commit_analyzer import CommitAnalyzer
from diff_extractor import DiffExtractor
from message_rectifier import MessageRectifier
from evaluator import Evaluator
from report_generator import ReportGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BugCommitAnalyzer:
    """Orchestrates the analysis pipeline and ensures assignment objectives are met."""

    def __init__(self, repo_url: str, max_commits: int = 50, output_dir: Path = Path('results')):
        self.repo_url = repo_url
        self.max_commits = max_commits
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.repo_selector = RepositorySelector()
        self.commit_analyzer = CommitAnalyzer(self.repo_url)
        self.diff_extractor = DiffExtractor(self.repo_url)
        self.message_rectifier = MessageRectifier()
        self.evaluator = Evaluator()
        self.report_generator = ReportGenerator(self.output_dir)

    def run(self):
        logger.info("Starting end-to-end analysis for: %s", self.repo_url)

        # Repository analysis
        repo_info = self.repo_selector.analyze_repository(self.repo_url)
        logger.info("Repository: %s", repo_info.get('full_name', self.repo_url))

        # Identify bug-fixing commits
        bug_commits = self.commit_analyzer.identify_bug_fixing_commits(max_commits=self.max_commits)
        logger.info("Identified %d bug-fixing commits", len(bug_commits))

        # Save commits CSV using CommitAnalyzer helper (rich metadata)
        commits_csv = self.output_dir / 'bug_fixing_commits.csv'
        try:
            self.commit_analyzer.save_commits_to_csv(bug_commits, commits_csv)
            logger.info("Saved bug-fixing commits to %s", commits_csv)
        except Exception as e:
            logger.warning("Failed to save commits CSV via module method: %s. Falling back to minimal CSV.", e)
            # Fallback minimal CSV
            with open(commits_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['Hash', 'Message', 'Hashes of parents', 'Is a merge commit?', 'List of modified files'])
                writer.writeheader()
                for c in bug_commits:
                    writer.writerow({
                        'Hash': c.get('hash',''),
                        'Message': c.get('message',''),
                        'Hashes of parents': ';'.join(c.get('parent_hashes',[])),
                        'Is a merge commit?': c.get('is_merge_commit', False),
                        'List of modified files': ';'.join(c.get('modified_files', []))
                    })
            logger.info("Wrote fallback commits CSV to %s", commits_csv)

        # Extract diffs (limit to a reasonable number to keep runtime feasible)
        diffs_limit = min( max(10, self.max_commits // 5), len(bug_commits) )
        commit_subset = bug_commits[:diffs_limit]
        diff_data = self.diff_extractor.extract_diffs(commit_subset)
        logger.info("Extracted %d file diffs", len(diff_data))

        # Save diffs CSV using DiffExtractor helper
        diffs_csv = self.output_dir / 'commit_diffs.csv'
        try:
            self.diff_extractor.save_diffs_to_csv(diff_data, diffs_csv)
            logger.info("Saved diffs to %s", diffs_csv)
        except Exception as e:
            logger.error("Failed to save diffs CSV: %s", e)

        # Rectify messages
        rectified_data = self.message_rectifier.rectify_messages(diff_data)
        rectified_csv = self.output_dir / 'rectified_messages.csv'
        try:
            self.message_rectifier.save_rectified_data(rectified_data, rectified_csv)
            logger.info("Saved rectified messages to %s", rectified_csv)
        except Exception as e:
            logger.error("Failed to save rectified data: %s", e)

        # Evaluate
        evaluation_results = self.evaluator.evaluate_all(bug_commits, diff_data, rectified_data)

        # Generate visualizations
        try:
            self.evaluator.generate_visualizations(evaluation_results, self.output_dir)
            logger.info("Visualizations generated in %s", self.output_dir)
        except Exception as e:
            logger.warning("Failed to generate visualizations: %s", e)

        # Generate comprehensive report and JSON summary
        try:
            self.report_generator.generate_comprehensive_report(repo_info, bug_commits, diff_data, rectified_data, evaluation_results)
            logger.info("Comprehensive report generated in %s", self.output_dir)
        except Exception as e:
            logger.error("Failed to generate comprehensive report: %s", e)

        # Also save evaluation JSON explicitly
        try:
            import json
            eval_file = self.output_dir / 'evaluation_summary.json'
            with open(eval_file, 'w', encoding='utf-8') as f:
                json.dump(evaluation_results, f, indent=2, default=str)
            logger.info("Saved evaluation summary to %s", eval_file)
        except Exception as e:
            logger.warning("Unable to write evaluation summary JSON: %s", e)

        # Ensure assignment-specific CSVs exist and have exact expected columns
        try:
            # Bug-fixing commits CSV (assignment schema)
            commits_csv_assign = self.output_dir / 'bug_fixing_commits.csv'
            with open(commits_csv_assign, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['Hash', 'Message', 'Hashes of parents', 'Is a merge commit?', 'List of modified files'])
                writer.writeheader()
                for c in bug_commits:
                    writer.writerow({
                        'Hash': c.get('hash', ''),
                        'Message': c.get('message', ''),
                        'Hashes of parents': ';'.join(c.get('parent_hashes', [])) if isinstance(c.get('parent_hashes', []), (list, tuple)) else c.get('parent_hashes', ''),
                        'Is a merge commit?': bool(c.get('is_merge_commit', False)),
                        'List of modified files': ';'.join(c.get('modified_files', [])) if isinstance(c.get('modified_files', []), (list, tuple)) else c.get('modified_files', '')
                    })
            logger.info("Assignment-format commits CSV written to %s", commits_csv_assign)

            # Commit diffs CSV (assignment schema)
            diffs_csv_assign = self.output_dir / 'commit_diffs.csv'
            with open(diffs_csv_assign, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['Message', 'Filename', 'Source Code (before)', 'Source Code (current)', 'Diff', 'LLM Inference (fix type)', 'Rectified Message', 'Hash'])
                writer.writeheader()
                for d in diff_data:
                    writer.writerow({
                        'Message': d.get('message', ''),
                        'Filename': d.get('filename', ''),
                        'Source Code (before)': d.get('source_code_before', ''),
                        'Source Code (current)': d.get('source_code_current', ''),
                        'Diff': d.get('diff', ''),
                        'LLM Inference (fix type)': d.get('llm_inference', ''),
                        'Rectified Message': d.get('rectified_message', ''),
                        'Hash': d.get('hash', '')
                    })
            logger.info("Assignment-format diffs CSV written to %s", diffs_csv_assign)

            # Rectified messages CSV (assignment schema - per file)
            rectified_csv_assign = self.output_dir / 'rectified_messages.csv'
            with open(rectified_csv_assign, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['Message', 'Filename', 'Source Code (before)', 'Source Code (current)', 'Diff', 'LLM Inference (fix type)', 'Rectified Message', 'Hash'])
                writer.writeheader()
                for r in rectified_data:
                    writer.writerow({
                        'Message': r.get('message', ''),
                        'Filename': r.get('filename', ''),
                        'Source Code (before)': r.get('source_code_before', ''),
                        'Source Code (current)': r.get('source_code_current', ''),
                        'Diff': r.get('diff', ''),
                        'LLM Inference (fix type)': r.get('llm_inference', ''),
                        'Rectified Message': r.get('rectified_message', ''),
                        'Hash': r.get('hash', '')
                    })
            logger.info("Assignment-format rectified CSV written to %s", rectified_csv_assign)

        except Exception as e:
            logger.error("Failed to write assignment-specific CSVs: %s", e)

        logger.info("Pipeline completed. Outputs are in: %s", self.output_dir)
        return {
            'commits_count': len(bug_commits),
            'diffs_count': len(diff_data),
            'rectified_count': len(rectified_data)
        }


def main():
    parser = argparse.ArgumentParser(description='Bug-fixing commit analysis pipeline')
    parser.add_argument('--repo-url', type=str, default=None, help='GitHub repository URL to analyze')
    parser.add_argument('--max-commits', type=int, default=50, help='Maximum number of bug-fixing commits to identify')
    parser.add_argument('--output-dir', type=str, default='results', help='Directory to save output files')

    args = parser.parse_args()

    repo_url = args.repo_url
    if not repo_url:
        # Use repository selector to provide default recommendation
        selector = RepositorySelector()
        # Use example repository if interactive selection not possible
        repo_url = 'https://github.com/pallets/flask'
        logger.info('No repo-url provided. Defaulting to %s', repo_url)

    analyzer = BugCommitAnalyzer(repo_url=repo_url, max_commits=args.max_commits, output_dir=Path(args.output_dir))

    result = analyzer.run()

    print('\n' + '='*60)
    print('ANALYSIS COMPLETED')
    print('='*60)
    print(f"Bug-fixing commits identified: {result['commits_count']}")
    print(f"File modifications analyzed: {result['diffs_count']}")
    print(f"Rectified messages produced: {result['rectified_count']}")
    print('\nOutputs saved to:', Path(args.output_dir).resolve())


if __name__ == '__main__':
    main()
