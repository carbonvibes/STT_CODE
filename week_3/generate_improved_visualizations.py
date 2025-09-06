#!/usr/bin/env python3
"""
Improved Visualization Generator for Lab Assignment 3
Creates only meaningful visualizations with proper separation
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
from pathlib import Path
import logging

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 12

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImprovedLab3Visualizer:
    def __init__(self, results_dir: Path):
        self.results_dir = Path(results_dir)
        self.viz_dir = self.results_dir / "visualizations"
        self.viz_dir.mkdir(exist_ok=True)
        
    def load_data(self):
        """Load the Lab 3 analysis results"""
        dataset_file = self.results_dir / "lab3_results_final.csv"
        if not dataset_file.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_file}")
        
        self.df = pd.read_csv(dataset_file)
        
        # Extract file extensions
        self.df['file_ext'] = self.df['Filename'].str.extract(r'\.([^.]+)$')[0].fillna('no_ext')
        
        logger.info(f"Loaded {len(self.df)} records for visualization")
        
        # Analyze data quality for meaningful plots
        self._analyze_data_quality()
    
    def _analyze_data_quality(self):
        """Analyze which visualizations will have meaningful content"""
        self.plot_candidates = {}
        
        # 1. File type distribution (always meaningful)
        file_types = self.df['file_ext'].value_counts()
        self.plot_candidates['file_types'] = len(file_types) > 1
        
        # 2. Files per commit (meaningful if multiple commits)
        if 'Hash' in self.df.columns:
            files_per_commit = self.df.groupby('Hash').size()
            self.plot_candidates['files_per_commit'] = len(files_per_commit) > 1 and files_per_commit.std() > 0
        else:
            self.plot_candidates['files_per_commit'] = False
        
        # 3. Structural metrics (meaningful if Python files exist)
        python_files = self.df[self.df['file_ext'] == 'py']
        structural_data = python_files.dropna(subset=['MI_Before', 'MI_After'])
        self.plot_candidates['structural_metrics'] = len(structural_data) > 0
        
        # 4. Token similarity (meaningful if variation exists)
        token_sim = self.df['Token_Similarity'].dropna()
        self.plot_candidates['token_similarity'] = len(token_sim) > 0 and token_sim.std() > 0.01
        
        # 5. Semantic similarity (check if meaningful variation)
        semantic_sim = self.df['Semantic_Similarity'].dropna()
        self.plot_candidates['semantic_similarity'] = len(semantic_sim) > 0 and semantic_sim.std() > 0.001
        
        # 6. Classification agreement (meaningful if any disagreement)
        if 'Classes_Agree' in self.df.columns:
            agree_data = self.df['Classes_Agree'].dropna()
            self.plot_candidates['classification'] = len(agree_data) > 0 and agree_data.nunique() > 1
        else:
            self.plot_candidates['classification'] = False
        
        # 7. Missing data patterns (always meaningful for explanation)
        self.plot_candidates['missing_data'] = True
        
        logger.info(f"Plot candidates: {self.plot_candidates}")
    
    def plot_file_type_distribution(self):
        """Plot file type distribution"""
        if not self.plot_candidates.get('file_types', False):
            logger.info("Skipping file type distribution - insufficient variety")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Count plot
        file_counts = self.df['file_ext'].value_counts()
        colors = plt.cm.Set3(np.linspace(0, 1, len(file_counts)))
        
        bars = ax1.bar(file_counts.index, file_counts.values, color=colors, alpha=0.8, edgecolor='black')
        ax1.set_title('File Type Distribution in Bug Fixes', fontweight='bold', fontsize=14)
        ax1.set_xlabel('File Extension')
        ax1.set_ylabel('Number of Files')
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        # Pie chart
        ax2.pie(file_counts.values, labels=file_counts.index, autopct='%1.1f%%', 
                colors=colors, startangle=90)
        ax2.set_title('File Type Proportion', fontweight='bold', fontsize=14)
        
        plt.suptitle('Dataset Composition Analysis', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.viz_dir / 'file_type_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("Generated: file_type_distribution.png")
    
    def plot_files_per_commit(self):
        """Plot files per commit distribution"""
        if not self.plot_candidates.get('files_per_commit', False):
            logger.info("Skipping files per commit - insufficient variation")
            return
        
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        
        files_per_commit = self.df.groupby('Hash').size()
        
        # Create histogram
        ax.hist(files_per_commit, bins=min(10, len(files_per_commit.unique())), 
                alpha=0.7, color='lightcoral', edgecolor='black', linewidth=1.2)
        
        ax.set_title('Distribution of Files Modified per Commit', fontweight='bold', fontsize=14)
        ax.set_xlabel('Number of Files per Commit')
        ax.set_ylabel('Number of Commits')
        ax.grid(True, alpha=0.3)
        
        # Add statistics
        mean_files = files_per_commit.mean()
        ax.axvline(mean_files, color='red', linestyle='--', linewidth=2, 
                  label=f'Mean: {mean_files:.1f} files/commit')
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(self.viz_dir / 'files_per_commit.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("Generated: files_per_commit.png")
    
    def plot_structural_metrics(self):
        """Plot structural metrics for Python files"""
        if not self.plot_candidates.get('structural_metrics', False):
            logger.info("Skipping structural metrics - no Python files with data")
            return
        
        python_files = self.df[self.df['file_ext'] == 'py']
        structural_data = python_files.dropna(subset=['MI_Before', 'MI_After', 'CC_Before', 'CC_After'])
        
        if len(structural_data) == 0:
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # Maintainability Index Before vs After
        ax1.scatter(structural_data['MI_Before'], structural_data['MI_After'], 
                   alpha=0.7, s=100, color='blue', edgecolor='black')
        
        # Add diagonal line (no change line)
        mi_min = min(structural_data['MI_Before'].min(), structural_data['MI_After'].min())
        mi_max = max(structural_data['MI_Before'].max(), structural_data['MI_After'].max())
        ax1.plot([mi_min, mi_max], [mi_min, mi_max], 'r--', alpha=0.8, linewidth=2)
        
        ax1.set_xlabel('Maintainability Index (Before)')
        ax1.set_ylabel('Maintainability Index (After)')
        ax1.set_title('Maintainability Index: Before vs After', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Cyclomatic Complexity Before vs After
        ax2.scatter(structural_data['CC_Before'], structural_data['CC_After'], 
                   alpha=0.7, s=100, color='green', edgecolor='black')
        
        cc_min = min(structural_data['CC_Before'].min(), structural_data['CC_After'].min())
        cc_max = max(structural_data['CC_Before'].max(), structural_data['CC_After'].max())
        ax2.plot([cc_min, cc_max], [cc_min, cc_max], 'r--', alpha=0.8, linewidth=2)
        
        ax2.set_xlabel('Cyclomatic Complexity (Before)')
        ax2.set_ylabel('Cyclomatic Complexity (After)')
        ax2.set_title('Cyclomatic Complexity: Before vs After', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # MI Change Distribution
        if 'MI_Change' in structural_data.columns:
            mi_changes = structural_data['MI_Change'].dropna()
            if len(mi_changes) > 0:
                ax3.hist(mi_changes, bins=min(10, len(mi_changes)), 
                        alpha=0.7, color='lightblue', edgecolor='black')
                ax3.axvline(0, color='red', linestyle='--', linewidth=2, label='No Change')
                ax3.set_title('Distribution of MI Changes', fontweight='bold')
                ax3.set_xlabel('MI Change (After - Before)')
                ax3.set_ylabel('Number of Files')
                ax3.legend()
                ax3.grid(True, alpha=0.3)
        
        # CC Change Distribution
        if 'CC_Change' in structural_data.columns:
            cc_changes = structural_data['CC_Change'].dropna()
            if len(cc_changes) > 0:
                ax4.hist(cc_changes, bins=min(10, len(cc_changes)), 
                        alpha=0.7, color='lightgreen', edgecolor='black')
                ax4.axvline(0, color='red', linestyle='--', linewidth=2, label='No Change')
                ax4.set_title('Distribution of CC Changes', fontweight='bold')
                ax4.set_xlabel('CC Change (After - Before)')
                ax4.set_ylabel('Number of Files')
                ax4.legend()
                ax4.grid(True, alpha=0.3)
        
        plt.suptitle('Structural Code Quality Metrics (Python Files Only)', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.viz_dir / 'structural_metrics.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("Generated: structural_metrics.png")
    
    def plot_token_similarity(self):
        """Plot token similarity analysis"""
        if not self.plot_candidates.get('token_similarity', False):
            logger.info("Skipping token similarity - insufficient variation")
            return
        
        token_sim = self.df['Token_Similarity'].dropna()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Distribution histogram
        ax1.hist(token_sim, bins=15, alpha=0.7, color='orange', edgecolor='black')
        ax1.axvline(token_sim.mean(), color='red', linestyle='--', linewidth=2, 
                   label=f'Mean: {token_sim.mean():.3f}')
        ax1.axvline(0.75, color='green', linestyle='--', linewidth=2, 
                   label='Minor Fix Threshold: 0.75')
        ax1.set_title('Token Similarity Distribution (BLEU)', fontweight='bold')
        ax1.set_xlabel('Token Similarity Score')
        ax1.set_ylabel('Number of Files')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Box plot by file type
        file_types_with_data = []
        similarity_by_type = []
        
        for file_type in self.df['file_ext'].unique():
            type_data = self.df[self.df['file_ext'] == file_type]['Token_Similarity'].dropna()
            if len(type_data) > 0:
                file_types_with_data.append(file_type)
                similarity_by_type.append(type_data)
        
        if len(similarity_by_type) > 1:
            ax2.boxplot(similarity_by_type, labels=file_types_with_data)
            ax2.set_title('Token Similarity by File Type', fontweight='bold')
            ax2.set_xlabel('File Type')
            ax2.set_ylabel('Token Similarity Score')
            ax2.grid(True, alpha=0.3)
        else:
            ax2.text(0.5, 0.5, 'Insufficient data\nfor file type comparison', 
                    ha='center', va='center', transform=ax2.transAxes, fontsize=12)
            ax2.set_title('Token Similarity by File Type', fontweight='bold')
        
        plt.suptitle('Token-Based Change Magnitude Analysis', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.viz_dir / 'token_similarity.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("Generated: token_similarity.png")
    
    def plot_missing_data_patterns(self):
        """Plot missing data patterns for methodology explanation"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Missing data by metric type
        metrics = ['MI_Before', 'CC_Before', 'LOC_Before', 'Semantic_Similarity', 'Token_Similarity']
        missing_counts = []
        total_files = len(self.df)
        
        for metric in metrics:
            if metric in self.df.columns:
                missing = self.df[metric].isna().sum()
                missing_counts.append(missing)
            else:
                missing_counts.append(total_files)
        
        colors = ['red' if count > 0 else 'green' for count in missing_counts]
        bars = ax1.bar(range(len(metrics)), missing_counts, color=colors, alpha=0.7, edgecolor='black')
        
        ax1.set_title('Missing Data by Metric Type', fontweight='bold')
        ax1.set_xlabel('Metric Type')
        ax1.set_ylabel('Number of Missing Values')
        ax1.set_xticks(range(len(metrics)))
        ax1.set_xticklabels([m.replace('_', '\n') for m in metrics], rotation=45)
        ax1.grid(True, alpha=0.3)
        
        # Add value labels
        for i, bar in enumerate(bars):
            height = bar.get_height()
            percentage = (height / total_files) * 100
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                    f'{int(height)}\n({percentage:.1f}%)', 
                    ha='center', va='bottom', fontweight='bold')
        
        # Data availability by file type
        file_types = self.df['file_ext'].unique()
        data_matrix = []
        
        for file_type in file_types:
            type_data = self.df[self.df['file_ext'] == file_type]
            row = []
            for metric in ['MI_Before', 'Semantic_Similarity']:
                if metric in type_data.columns:
                    available = type_data[metric].notna().sum()
                    percentage = (available / len(type_data)) * 100
                    row.append(percentage)
                else:
                    row.append(0)
            data_matrix.append(row)
        
        data_matrix = np.array(data_matrix)
        
        im = ax2.imshow(data_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
        ax2.set_title('Data Availability by File Type', fontweight='bold')
        ax2.set_xlabel('Metric Type')
        ax2.set_ylabel('File Type')
        ax2.set_xticks(range(2))
        ax2.set_xticklabels(['Structural\n(MI/CC)', 'Similarity\n(Semantic)'])
        ax2.set_yticks(range(len(file_types)))
        ax2.set_yticklabels(file_types)
        
        # Add percentage text
        for i in range(len(file_types)):
            for j in range(2):
                text = ax2.text(j, i, f'{data_matrix[i, j]:.0f}%',
                               ha="center", va="center", color="black", fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax2)
        cbar.set_label('Data Availability (%)', rotation=270, labelpad=15)
        
        plt.suptitle('Data Quality and Coverage Analysis', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.viz_dir / 'missing_data_patterns.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("Generated: missing_data_patterns.png")
    
    def plot_semantic_vs_token_comparison(self):
        """Plot semantic vs token similarity comparison if both have variation"""
        semantic_sim = self.df['Semantic_Similarity'].dropna()
        token_sim = self.df['Token_Similarity'].dropna()
        
        # Check if we have both metrics and sufficient variation
        if len(semantic_sim) == 0 or len(token_sim) == 0:
            logger.info("Skipping semantic vs token comparison - missing data")
            return
        
        # Align the data (only files with both metrics)
        both_metrics = self.df.dropna(subset=['Semantic_Similarity', 'Token_Similarity'])
        
        if len(both_metrics) < 2:
            logger.info("Skipping semantic vs token comparison - insufficient paired data")
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Scatter plot comparison
        ax1.scatter(both_metrics['Semantic_Similarity'], both_metrics['Token_Similarity'], 
                   alpha=0.7, s=100, color='purple', edgecolor='black')
        
        ax1.set_xlabel('Semantic Similarity (CodeBERT)')
        ax1.set_ylabel('Token Similarity (BLEU)')
        ax1.set_title('Semantic vs Token Similarity', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Add correlation coefficient
        correlation = both_metrics['Semantic_Similarity'].corr(both_metrics['Token_Similarity'])
        ax1.text(0.05, 0.95, f'Correlation: {correlation:.3f}', transform=ax1.transAxes,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"),
                fontweight='bold')
        
        # Difference analysis
        both_metrics['Similarity_Diff'] = both_metrics['Semantic_Similarity'] - both_metrics['Token_Similarity']
        
        ax2.hist(both_metrics['Similarity_Diff'], bins=10, alpha=0.7, color='lightcoral', edgecolor='black')
        ax2.axvline(0, color='red', linestyle='--', linewidth=2, label='No Difference')
        ax2.axvline(both_metrics['Similarity_Diff'].mean(), color='blue', linestyle='--', linewidth=2, 
                   label=f'Mean Diff: {both_metrics["Similarity_Diff"].mean():.4f}')
        
        ax2.set_title('Difference Between Similarity Measures', fontweight='bold')
        ax2.set_xlabel('Semantic - Token Similarity')
        ax2.set_ylabel('Number of Files')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.suptitle('Comparison of Similarity Measurement Approaches', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.viz_dir / 'semantic_vs_token_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("Generated: semantic_vs_token_comparison.png")
    
    def generate_all_visualizations(self):
        """Generate all meaningful visualizations"""
        logger.info("Starting visualization generation...")
        
        # Generate individual plots based on data availability
        self.plot_file_type_distribution()
        self.plot_files_per_commit()
        self.plot_structural_metrics()
        self.plot_token_similarity()
        self.plot_semantic_vs_token_comparison()
        self.plot_missing_data_patterns()
        
        logger.info("All meaningful visualizations generated!")
        
        # Create summary of what was generated
        generated_plots = []
        for plot_name, candidate in self.plot_candidates.items():
            if candidate:
                generated_plots.append(plot_name)
        
        logger.info(f"Generated plots: {generated_plots}")
        return generated_plots

def main():
    """Generate improved Lab 3 visualizations"""
    results_dir = Path("data")
    if not results_dir.exists():
        print("Data directory not found! Please run the analysis first.")
        return
    
    visualizer = ImprovedLab3Visualizer(results_dir)
    visualizer.load_data()
    generated_plots = visualizer.generate_all_visualizations()
    
    print("\n" + "="*60)
    print("IMPROVED LAB 3 VISUALIZATION GENERATION COMPLETE")
    print("="*60)
    print(f"Generated {len(generated_plots)} meaningful visualizations:")
    for plot in generated_plots:
        print(f"  ✅ {plot}")
    print("="*60)

if __name__ == "__main__":
    main()
