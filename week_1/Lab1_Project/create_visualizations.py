#!/usr/bin/env python3
"""
Git Workflow Visualization Script
Creates a visual representation of the Git workflow demonstrated in Lab 1.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


def create_pylint_score_chart():
    """Create a chart showing pylint score improvement."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    versions = ['Initial\nCode', 'After\nFormatting\nFixes']
    scores = [6.94, 10.0]
    colors = ['orange', 'green']

    bars = ax.bar(versions, scores, color=colors, alpha=0.7,
                  edgecolor='black', linewidth=2)

    # Add score labels on bars
    for bar, score in zip(bars, scores):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{score}/10', ha='center', va='bottom',
                fontweight='bold', fontsize=12)

    ax.set_ylabel('Pylint Score', fontsize=12, fontweight='bold')
    ax.set_title('Code Quality Improvement with Pylint\nCS202 Lab 1 - calculator.py',
                 fontsize=14, fontweight='bold')
    ax.set_ylim(0, 11)
    ax.grid(axis='y', alpha=0.3)

    # Add threshold line
    ax.axhline(y=8.0, color='red', linestyle='--', alpha=0.7, linewidth=2)
    ax.text(1.5, 8.2, 'GitHub Actions Threshold (8.0)',
            ha='center', color='red', fontweight='bold')

    # Add improvement arrow
    ax.annotate('', xy=(1, 9.8), xytext=(0, 7.2),
                arrowprops=dict(arrowstyle='->', lw=3, color='blue'))
    ax.text(0.5, 8.5, '+3.06\nImprovement', ha='center',
            color='blue', fontweight='bold')

    plt.tight_layout()
    plt.savefig('/workspaces/STT/STT/Week 1/Lab1_Project/pylint_improvement_chart.png',
                dpi=300, bbox_inches='tight')
    plt.close()

    print("✅ Pylint improvement chart created successfully!")


def create_lab_summary_chart():
    """Create a summary chart of lab completion."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Completion status
    tasks = ['Git Config', 'Repository Init', 'File Operations',
             'Python Code\n(30+ lines)', 'GitHub Actions', 'Remote Setup']
    completion = [100, 100, 100, 100, 100, 100]
    colors = ['green'] * len(tasks)

    bars1 = ax1.bar(range(len(tasks)), completion, color=colors,
                    alpha=0.7, edgecolor='black')
    ax1.set_ylabel('Completion %', fontweight='bold')
    ax1.set_title('Lab 1 Task Completion Status', fontweight='bold')
    ax1.set_xticks(range(len(tasks)))
    ax1.set_xticklabels(tasks, rotation=45, ha='right')
    ax1.set_ylim(0, 110)

    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 2,
                 '✅', ha='center', va='bottom', fontsize=16)

    # Code metrics
    metrics = ['Lines of Code', 'Pylint Score', 'Commits Made']
    values = [85, 10.0, 2]
    targets = [30, 8.0, 1]

    x_pos = np.arange(len(metrics))
    width = 0.35

    bars2 = ax2.bar(x_pos - width/2, values, width, label='Achieved',
                    color='lightgreen', edgecolor='green')
    bars3 = ax2.bar(x_pos + width/2, targets, width, label='Required',
                    color='lightblue', edgecolor='blue')

    ax2.set_ylabel('Value', fontweight='bold')
    ax2.set_title('Lab 1 Metrics vs Requirements', fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(metrics)
    ax2.legend()

    # Add value labels
    for bar, value in zip(bars2, values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                 str(value), ha='center', va='bottom', fontweight='bold')

    for bar, target in zip(bars3, targets):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                 str(target), ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    plt.savefig('/workspaces/STT/STT/Week 1/Lab1_Project/lab_summary_chart.png',
                dpi=300, bbox_inches='tight')
    plt.close()

    print("✅ Lab summary chart created successfully!")


if __name__ == "__main__":
    print("Creating Lab 1 visualization diagrams...")
    create_pylint_score_chart()
    create_lab_summary_chart()
    print("\n🎉 All visualizations completed successfully!")
    print("Files created:")
    print("  - pylint_improvement_chart.png")
    print("  - lab_summary_chart.png")
