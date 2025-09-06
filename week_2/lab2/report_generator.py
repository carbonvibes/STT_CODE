"""
Report Generator Module
This module generates comprehensive reports for the lab assignment.
"""

import logging
import json
from typing import Dict, List
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

class ReportGenerator:
    """
    Class to generate comprehensive analysis reports
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.logger = logging.getLogger(__name__)
        
    def generate_comprehensive_report(self, repo_info: Dict, commits_data: List[Dict],
                                    diff_data: List[Dict], rectified_data: List[Dict],
                                    evaluation_results: Dict):
        """
        Generate a comprehensive markdown report
        """
        self.logger.info("Generating comprehensive report")
        
        report_content = self._generate_markdown_report(
            repo_info, commits_data, diff_data, rectified_data, evaluation_results
        )
        
        # Save main report
        report_file = self.output_dir / 'Lab2_Analysis_Report.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # Generate additional files
        self._generate_json_summary(evaluation_results)
        self._generate_csv_summaries(commits_data, diff_data, rectified_data)
        
        self.logger.info("Comprehensive report generated: %s", report_file)
    
    def _generate_markdown_report(self, repo_info: Dict, commits_data: List[Dict],
                                diff_data: List[Dict], rectified_data: List[Dict],
                                evaluation_results: Dict) -> str:
        """
        Generate the main markdown report content
        """
        current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        report = f"""# Lab Assignment 2: Commit Message Rectification Analysis Report

**Course:** CS202 Software Tools and Techniques for CSE  
**Lab Topic:** Commit Message Rectification for Bug-Fixing Commits in the Wild  
**Date:** {current_time}  
**Student:** [Your Name Here]  
**Student ID:** [Your Student ID Here]

---

## Executive Summary

This report presents a comprehensive analysis of bug-fixing commits and commit message rectification for the selected open-source repository. The study addresses three key research questions regarding developer precision, LLM effectiveness, and rectifier performance in improving commit message quality.

### Key Findings
- **Total Commits Analyzed:** {len(commits_data):,}
- **Bug-Fixing Commits Identified:** {len(commits_data):,}
- **File Changes Analyzed:** {len(diff_data):,}
- **Rectification Success Rate:** {evaluation_results.get('rq3_rectifier_evaluation', {}).get('hit_rate', 0):.1%}

---

## 1. Repository Selection

### Selected Repository
**Repository:** {repo_info.get('full_name', 'N/A')}  
**GitHub URL:** {repo_info.get('clone_url', 'N/A')}  
**Primary Language:** {repo_info.get('language', 'N/A')}  

### Repository Metrics
- **⭐ Stars:** {repo_info.get('stars', 0):,}
- **🍴 Forks:** {repo_info.get('forks', 0):,}
- **📝 Open Issues:** {repo_info.get('open_issues', 0):,}
- **📊 Estimated Commits:** {repo_info.get('estimated_commits', 0):,}
- **📅 Created:** {repo_info.get('created_at', 'N/A')[:10]}
- **🔄 Last Updated:** {repo_info.get('updated_at', 'N/A')[:10]}

### Selection Criteria Justification

This repository was selected based on the following hierarchical funnel criteria:

1. **Community Engagement:** High star count ({repo_info.get('stars', 0):,}) indicates active community use
2. **Development Activity:** Substantial fork count ({repo_info.get('forks', 0):,}) shows developer engagement  
3. **Issue Management:** Active issue tracking ({repo_info.get('open_issues', 0):,} open issues)
4. **Codebase Maturity:** Established project with extensive commit history
5. **Language Ecosystem:** {repo_info.get('language', 'N/A')} provides good tool support for analysis

### Selection Criteria Assessment
"""

        # Add criteria assessment if available
        criteria_met = repo_info.get('selection_criteria_met', {})
        if criteria_met:
            for criterion, met in criteria_met.items():
                status = "✅ PASSED" if met else "❌ FAILED"
                report += f"- **{criterion.replace('_', ' ').title()}:** {status}\n"
        
        report += f"""

---

## 2. Bug-Fixing Commit Identification

### Methodology

Bug-fixing commits were identified using a multi-heuristic approach:

1. **Keyword Analysis:** Searching for bug-related terms in commit messages
2. **Issue References:** Detecting patterns like "fixes #123" or "closes #456"
3. **File Type Filtering:** Focusing on source code modifications
4. **Change Size Analysis:** Filtering for reasonable bug-fix sized changes
5. **Merge Commit Exclusion:** Avoiding indirect bug fixes through merges

### Results Summary

- **Total Commits Identified:** {len(commits_data):,}
- **Average Files Changed per Commit:** {sum(c.get('files_changed', 0) for c in commits_data) / len(commits_data) if commits_data else 0:.1f}
- **Total Lines Modified:** {sum(c.get('lines_added', 0) + c.get('lines_deleted', 0) for c in commits_data):,}
- **Unique Authors:** {len(set(c.get('author', '') for c in commits_data))}

### Bug-Fixing Commit Statistics

| Metric | Value |
|--------|-------|
| Total Bug-Fix Commits | {len(commits_data):,} |
| Merge Commits | {sum(1 for c in commits_data if c.get('is_merge_commit', False))} |
| Average Lines Added | {sum(c.get('lines_added', 0) for c in commits_data) / len(commits_data) if commits_data else 0:.1f} |
| Average Lines Deleted | {sum(c.get('lines_deleted', 0) for c in commits_data) / len(commits_data) if commits_data else 0:.1f} |

---

## 3. Diff Extraction and Analysis

### File Modification Analysis

The analysis extracted and examined diffs for {len(diff_data):,} file modifications across the identified bug-fixing commits.

"""

        # Add diff statistics if available
        if diff_data:
            file_extensions = {}
            for diff in diff_data:
                filename = diff.get('filename', '')
                if '.' in filename:
                    ext = '.' + filename.split('.')[-1]
                    file_extensions[ext] = file_extensions.get(ext, 0) + 1
            
            report += "### File Types Modified\n\n"
            for ext, count in sorted(file_extensions.items(), key=lambda x: x[1], reverse=True)[:10]:
                report += f"- **{ext}:** {count} files\n"

        report += f"""

### Change Pattern Analysis

The analysis identified various bug-fix patterns in the code changes:

- **Null/None Checks:** Safety improvements for null pointer handling
- **Bounds Checking:** Array/list index validation fixes  
- **Error Handling:** Exception catching and error management
- **Initialization:** Variable and object initialization fixes
- **Conditional Logic:** If/else statement corrections
- **Resource Management:** Memory and resource cleanup fixes

---

## 4. Research Questions Analysis

### RQ1: Developer Commit Message Precision

**Research Question:** Do developers use precise commit messages in bug-fixing commits?

"""

        rq1_results = evaluation_results.get('rq1_developer_evaluation', {})
        if rq1_results:
            report += f"""
**Findings:**
- **Hit Rate:** {rq1_results.get('hit_rate', 0):.1%} of developer messages were classified as precise
- **Average Precision Score:** {rq1_results.get('average_precision_score', 0):.3f} out of 1.0
- **Message Quality Distribution:**
"""
            categories = rq1_results.get('message_categories', {})
            for category, count in categories.items():
                percentage = (count / sum(categories.values()) * 100) if categories else 0
                report += f"  - **{category.replace('_', ' ').title()}:** {count} ({percentage:.1f}%)\n"

            report += f"""
**Analysis:** Developer commit messages show {'high' if rq1_results.get('hit_rate', 0) > 0.7 else 'moderate' if rq1_results.get('hit_rate', 0) > 0.4 else 'low'} precision overall. The results indicate that developers {'frequently' if rq1_results.get('hit_rate', 0) > 0.7 else 'sometimes' if rq1_results.get('hit_rate', 0) > 0.4 else 'rarely'} provide detailed, context-specific commit messages for bug fixes.
"""

        report += f"""

### RQ2: LLM Commit Message Generation

**Research Question:** Does the LLM generate precise commit messages for bug-fixing commits?

"""

        rq2_results = evaluation_results.get('rq2_llm_evaluation', {})
        if rq2_results:
            report += f"""
**Findings:**
- **LLM Hit Rate:** {rq2_results.get('hit_rate', 0):.1%} of LLM-generated messages were precise
- **LLM Success Rate:** {rq2_results.get('llm_success_rate', 0):.1%} of commits received LLM-generated messages
- **Average LLM Precision:** {rq2_results.get('average_precision_score', 0):.3f} out of 1.0
- **Improvement over Original:** {rq2_results.get('improvement_over_original', 0):.1%} of cases

**Comparison with Developers:**
- **Developer Average:** {rq2_results.get('average_original_score', 0):.3f}
- **LLM Average:** {rq2_results.get('average_precision_score', 0):.3f}
- **Score Improvement:** {rq2_results.get('score_improvement', 0):+.3f}

**Analysis:** The LLM {'outperformed' if rq2_results.get('score_improvement', 0) > 0 else 'underperformed' if rq2_results.get('score_improvement', 0) < 0 else 'matched'} developer messages on average, showing {'significant potential' if rq2_results.get('hit_rate', 0) > 0.6 else 'moderate effectiveness' if rq2_results.get('hit_rate', 0) > 0.3 else 'limited success'} in generating contextually appropriate commit messages.
"""

        report += f"""

### RQ3: Rectifier Effectiveness

**Research Question:** To what extent can the rectifier improve commit message quality?

"""

        rq3_results = evaluation_results.get('rq3_rectifier_evaluation', {})
        if rq3_results:
            report += f"""
**Findings:**
- **Rectification Hit Rate:** {rq3_results.get('hit_rate', 0):.1%} of messages were successfully improved
- **Average Score Improvement:** {rq3_results.get('average_score_improvement', 0):+.3f} points
- **Successful Rectifications:** {rq3_results.get('successful_rectifications', 0):,} out of {rq3_results.get('total_rectified', 0):,}

**Improvement Categories:**
"""
            improvements = rq3_results.get('improvement_categories', {})
            total_cases = sum(improvements.values()) if improvements else 1
            for category, count in improvements.items():
                percentage = (count / total_cases * 100) if total_cases > 0 else 0
                report += f"- **{category.replace('_', ' ').title()}:** {count} ({percentage:.1f}%)\n"

            before_after = rq3_results.get('before_after_comparison', {})
            if before_after:
                report += f"""
**Before vs After Comparison:**
- **Average Score Before:** {before_after.get('avg_original', 0):.3f}
- **Average Score After:** {before_after.get('avg_rectified', 0):.3f}  
- **Improvement Ratio:** {before_after.get('improvement_ratio', 0):.2f}x

**Analysis:** The rectifier achieved {'excellent' if rq3_results.get('hit_rate', 0) > 0.8 else 'good' if rq3_results.get('hit_rate', 0) > 0.6 else 'moderate' if rq3_results.get('hit_rate', 0) > 0.4 else 'limited'} success in improving commit message quality, demonstrating the value of automated message enhancement techniques.
"""

        report += f"""

---

## 5. Methodology and Implementation

### Tools and Technologies Used

- **PyDriller:** For Git repository mining and commit analysis
- **Transformers:** For LLM-based commit message generation
- **Pandas/NumPy:** For data manipulation and statistical analysis
- **Matplotlib/Seaborn:** For data visualization
- **Git/GitHub API:** For repository access and metadata extraction

### Data Processing Pipeline

1. **Repository Cloning:** Temporary local clone for analysis
2. **Commit Traversal:** Chronological examination of commit history  
3. **Heuristic Filtering:** Multi-criteria bug-fix identification
4. **Diff Extraction:** Detailed change analysis per file
5. **LLM Inference:** Automated message generation using T5 model
6. **Rule-Based Rectification:** Pattern-based message improvement
7. **Evaluation:** Multi-metric assessment of all approaches

### Challenges and Limitations

- **LLM Model Access:** Limited availability of specialized commit message models
- **Context Window:** Diff size limitations for LLM processing
- **Subjective Evaluation:** Commit message quality assessment subjectivity
- **Repository Scale:** Processing time for large repositories
- **Tool Dependencies:** Availability and version compatibility issues

---

## 6. Conclusions and Future Work

### Key Conclusions

1. **Developer Precision:** Developers show {'high' if rq1_results.get('hit_rate', 0) > 0.7 else 'moderate' if rq1_results.get('hit_rate', 0) > 0.4 else 'low'} precision in commit message authoring for bug fixes
2. **LLM Effectiveness:** Current LLM models show {'promising' if rq2_results.get('hit_rate', 0) > 0.5 else 'limited'} capability for automated commit message generation  
3. **Rectification Value:** Automated rectification can {'significantly' if rq3_results.get('hit_rate', 0) > 0.6 else 'moderately'} improve message quality

### Implications for Software Engineering

- **Code Review:** Enhanced commit messages improve code review efficiency
- **Documentation:** Better commit history serves as living documentation
- **Debugging:** Precise messages aid in understanding bug fix context
- **Team Communication:** Clear messages facilitate developer collaboration

### Future Research Directions

1. **Fine-Tuned Models:** Training specialized models on commit message datasets
2. **Multi-Modal Analysis:** Incorporating code structure and test results
3. **Real-Time Integration:** IDE plugins for live message suggestions
4. **Cross-Project Studies:** Comparative analysis across different project types
5. **Developer Feedback:** User studies on rectifier acceptance and usability

---

## 7. References and Resources

- [PyDriller Documentation](https://pydriller.readthedocs.io/)
- [CommitPredictorT5 Model](https://huggingface.co/mamiksik/CommitPredictorT5)
- [GitHub REST API](https://docs.github.com/en/rest)
- Course Lecture 2 Slides: Mining Software Repositories

---

## Appendices

### Appendix A: Data Files Generated

- `bug_fixing_commits.csv` - Identified bug-fixing commits with metadata
- `commit_diffs.csv` - Detailed diff analysis for each file modification  
- `rectified_messages.csv` - Complete rectification results with scores
- `evaluation_summary.json` - Comprehensive evaluation metrics
- Visualization plots: `rq1_developer_evaluation.png`, `rq3_rectifier_evaluation.png`

### Appendix B: Code Repository

The complete analysis code is available in the `lab2/` directory with the following modules:

- `main.py` - Main orchestration script
- `repository_selector.py` - Repository selection and analysis
- `commit_analyzer.py` - Bug-fixing commit identification  
- `diff_extractor.py` - Diff extraction and analysis
- `message_rectifier.py` - LLM and rule-based message rectification
- `evaluator.py` - Comprehensive evaluation framework
- `report_generator.py` - Report generation utilities

---

*Report generated on {current_time}*
"""

        return report
    
    def _generate_json_summary(self, evaluation_results: Dict):
        """
        Generate JSON summary of evaluation results
        """
        summary_file = self.output_dir / 'evaluation_summary.json'
        
        # Add timestamp
        evaluation_results['generated_at'] = datetime.now().isoformat()
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(evaluation_results, f, indent=2, default=str)
        
        self.logger.info("Evaluation summary saved to %s", summary_file)
    
    def _generate_csv_summaries(self, commits_data: List[Dict], 
                               diff_data: List[Dict], rectified_data: List[Dict]):
        """
        Generate CSV summary files for key metrics
        """
        # Commit summary
        if commits_data:
            commit_df = pd.DataFrame(commits_data)
            summary_stats = commit_df.describe(include='all')
            summary_stats.to_csv(self.output_dir / 'commit_summary_stats.csv')
        
        # Diff summary
        if diff_data:
            diff_df = pd.DataFrame(diff_data)
            # Select numeric columns for summary
            numeric_cols = ['lines_added', 'lines_deleted', 'complexity_before', 'complexity_after']
            available_cols = [col for col in numeric_cols if col in diff_df.columns]
            if available_cols:
                diff_summary = diff_df[available_cols].describe()
                diff_summary.to_csv(self.output_dir / 'diff_summary_stats.csv')
        
        # Rectification summary
        if rectified_data:
            rect_df = pd.DataFrame(rectified_data)
            score_cols = ['original_alignment_score', 'llm_alignment_score', 'rectified_alignment_score']
            available_score_cols = [col for col in score_cols if col in rect_df.columns]
            if available_score_cols:
                rect_summary = rect_df[available_score_cols].describe()
                rect_summary.to_csv(self.output_dir / 'rectification_summary_stats.csv')
        
        self.logger.info("CSV summary files generated")
    
    def generate_quick_start_guide(self):
        """
        Generate a quick start guide for running the analysis
        """
        guide_content = """# Lab 2 Quick Start Guide

## Prerequisites

1. Python 3.10 or later
2. Install required packages:
   ```bash
   pip install pydriller pandas numpy matplotlib seaborn transformers torch requests gitpython scikit-learn
   ```

## Running the Analysis

### Option 1: Automatic Repository Selection
```bash
python main.py --output-dir results --max-commits 100
```

### Option 2: Specific Repository
```bash
python main.py --repo-url https://github.com/pallets/flask --output-dir results --max-commits 50
```

### Option 3: Interactive Mode
```bash
python main.py
```

## Output Files

The analysis will generate:
- `bug_fixing_commits.csv` - Identified bug-fixing commits
- `commit_diffs.csv` - Diff analysis results  
- `rectified_messages.csv` - Rectification results
- `Lab2_Analysis_Report.md` - Comprehensive report
- Various visualization plots (PNG files)

## Troubleshooting

- **Memory Issues:** Reduce `--max-commits` parameter
- **Network Issues:** Ensure stable internet for repository cloning
- **LLM Issues:** Analysis will continue with rule-based rectification only

## Expected Runtime

- Small analysis (50 commits): 5-10 minutes
- Medium analysis (100 commits): 15-30 minutes  
- Large analysis (200+ commits): 45+ minutes

Runtime depends on repository size and commit complexity.
"""
        
        guide_file = self.output_dir / 'QUICK_START.md'
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        self.logger.info("Quick start guide generated: %s", guide_file)
