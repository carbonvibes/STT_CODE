"""
Enhanced Analysis Script for Lab 6
Generates additional visualizations and detailed insights
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """Load all generated data files."""
    base_path = "/workspaces/STT/STT/Week 6/lab6"
    
    # Load data
    vulnerability_data = pd.read_csv(f"{base_path}/data/consolidated_vulnerability_findings.csv")
    coverage_data = pd.read_csv(f"{base_path}/results/cwe_coverage_analysis.csv")
    iou_matrix = pd.read_csv(f"{base_path}/results/iou_matrix.csv", index_col=0)
    
    return vulnerability_data, coverage_data, iou_matrix

def create_interactive_visualizations():
    """Create interactive Plotly visualizations."""
    vuln_data, coverage_data, iou_matrix = load_data()
    
    # 1. Interactive CWE Coverage Comparison
    fig1 = make_subplots(
        rows=2, cols=2,
        subplot_titles=('CWE Detection by Tool', 'Top 25 Coverage %', 
                       'Total Findings by Tool', 'Tool Effectiveness'),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )
    
    # CWE Detection
    fig1.add_trace(
        go.Bar(x=coverage_data['Tool'], y=coverage_data['Total_CWEs_Detected'],
               name='Total CWEs', marker_color='lightblue'),
        row=1, col=1
    )
    
    fig1.add_trace(
        go.Bar(x=coverage_data['Tool'], y=coverage_data['Top_25_CWEs_Detected'],
               name='Top 25 CWEs', marker_color='coral'),
        row=1, col=1
    )
    
    # Top 25 Coverage %
    fig1.add_trace(
        go.Bar(x=coverage_data['Tool'], y=coverage_data['Top_25_Coverage_Percentage'],
               name='Coverage %', marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1']),
        row=1, col=2
    )
    
    # Total Findings
    fig1.add_trace(
        go.Bar(x=coverage_data['Tool'], y=coverage_data['Total_Findings'],
               name='Total Findings', marker_color='lightgreen'),
        row=2, col=1
    )
    
    # Tool Effectiveness
    fig1.add_trace(
        go.Bar(x=coverage_data['Tool'], y=coverage_data['Average_Findings_Per_CWE'],
               name='Avg Findings/CWE', marker_color='gold'),
        row=2, col=2
    )
    
    fig1.update_layout(height=700, showlegend=False, 
                       title_text="Comprehensive Tool Analysis Dashboard")
    
    fig1.write_html("/workspaces/STT/STT/Week 6/lab6/visualizations/interactive_dashboard.html")
    
    # 2. Interactive IoU Heatmap
    fig2 = go.Figure(data=go.Heatmap(
        z=iou_matrix.values,
        x=iou_matrix.columns,
        y=iou_matrix.index,
        colorscale='RdYlBu_r',
        text=np.round(iou_matrix.values, 3),
        texttemplate="%{text}",
        textfont={"size": 16},
        colorbar=dict(title="IoU Score")
    ))
    
    fig2.update_layout(
        title="Interactive Tool Similarity Matrix (IoU)",
        xaxis_title="Tools",
        yaxis_title="Tools"
    )
    
    fig2.write_html("/workspaces/STT/STT/Week 6/lab6/visualizations/interactive_iou_heatmap.html")
    
    # 3. CWE Distribution Sunburst Chart
    # Prepare data for sunburst
    sunburst_data = []
    for _, row in vuln_data.iterrows():
        sunburst_data.append({
            'Tool': row['Tool_name'],
            'Project': row['Project_name'], 
            'CWE': row['CWE_ID'],
            'Findings': row['Number_of_Findings'],
            'Top25': 'Top 25' if row['Is_In_CWE_Top_25'] else 'Other'
        })
    
    sunburst_df = pd.DataFrame(sunburst_data)
    
    fig3 = px.sunburst(sunburst_df, 
                       path=['Top25', 'Tool', 'Project', 'CWE'], 
                       values='Findings',
                       title="Vulnerability Distribution Hierarchy")
    
    fig3.write_html("/workspaces/STT/STT/Week 6/lab6/visualizations/vulnerability_sunburst.html")
    
    print("Interactive visualizations created:")
    print("- Interactive Dashboard: interactive_dashboard.html")
    print("- IoU Heatmap: interactive_iou_heatmap.html") 
    print("- Vulnerability Sunburst: vulnerability_sunburst.html")

def generate_detailed_statistics():
    """Generate detailed statistical analysis."""
    vuln_data, coverage_data, iou_matrix = load_data()
    
    stats_report = """
# Detailed Statistical Analysis

## Dataset Overview
"""
    
    # Basic statistics
    total_findings = vuln_data['Number_of_Findings'].sum()
    unique_cwes = vuln_data['CWE_ID'].nunique()
    projects = vuln_data['Project_name'].nunique()
    tools = vuln_data['Tool_name'].nunique()
    
    stats_report += f"""
- **Total Vulnerability Findings**: {total_findings:,}
- **Unique CWE Types**: {unique_cwes}
- **Projects Analyzed**: {projects}
- **Tools Evaluated**: {tools}
- **Average Findings per CWE**: {vuln_data['Number_of_Findings'].mean():.2f}
- **Standard Deviation**: {vuln_data['Number_of_Findings'].std():.2f}

## Tool Performance Analysis

### Tool Rankings:
"""
    
    # Tool rankings
    tool_rankings = coverage_data.sort_values('Total_Findings', ascending=False)
    for i, (_, row) in enumerate(tool_rankings.iterrows(), 1):
        stats_report += f"""
{i}. **{row['Tool']}**
   - Total Findings: {row['Total_Findings']:,}
   - CWEs Detected: {row['Total_CWEs_Detected']}
   - Top 25 Coverage: {row['Top_25_Coverage_Percentage']:.1f}%
   - Effectiveness Score: {row['Average_Findings_Per_CWE']:.2f}
"""
    
    # Project-specific analysis
    stats_report += """
## Project-Specific Analysis

"""
    
    for project in vuln_data['Project_name'].unique():
        project_data = vuln_data[vuln_data['Project_name'] == project]
        project_findings = project_data['Number_of_Findings'].sum()
        project_cwes = project_data['CWE_ID'].nunique()
        top_cwe = project_data.groupby('CWE_ID')['Number_of_Findings'].sum().idxmax()
        
        stats_report += f"""
### {project.title()}
- Total Findings: {project_findings:,}
- Unique CWEs: {project_cwes}
- Most Common CWE: {top_cwe}
- Risk Level: {'High' if project_findings > 150 else 'Medium' if project_findings > 100 else 'Low'}
"""
    
    # IoU Analysis
    stats_report += """
## Tool Similarity Analysis (IoU)

"""
    
    # Calculate IoU statistics
    iou_values = iou_matrix.values[np.triu_indices_from(iou_matrix.values, k=1)]
    avg_iou = np.mean(iou_values)
    max_iou = np.max(iou_values)
    min_iou = np.min(iou_values)
    
    stats_report += f"""
- **Average IoU**: {avg_iou:.3f}
- **Maximum IoU**: {max_iou:.3f}
- **Minimum IoU**: {min_iou:.3f}
- **Interpretation**: {'Low similarity' if avg_iou < 0.3 else 'Moderate similarity' if avg_iou < 0.7 else 'High similarity'}

### Tool Pair Analysis:
"""
    
    # Tool pair analysis
    tools = iou_matrix.index.tolist()
    for i, tool1 in enumerate(tools):
        for j, tool2 in enumerate(tools):
            if i < j:  # Only upper triangle
                iou_score = iou_matrix.loc[tool1, tool2]
                similarity = 'High' if iou_score > 0.5 else 'Medium' if iou_score > 0.2 else 'Low'
                stats_report += f"- **{tool1} vs {tool2}**: {iou_score:.3f} ({similarity} overlap)\n"
    
    # Save detailed statistics
    with open("/workspaces/STT/STT/Week 6/lab6/results/detailed_statistics.md", 'w') as f:
        f.write(stats_report)
    
    print("Detailed statistical analysis saved to: detailed_statistics.md")

def create_additional_plots():
    """Create additional static plots for comprehensive analysis."""
    vuln_data, coverage_data, iou_matrix = load_data()
    
    # Set up plotting style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # 1. CWE Frequency Distribution
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    cwe_freq = vuln_data['CWE_ID'].value_counts()
    plt.bar(range(len(cwe_freq)), cwe_freq.values, color='skyblue', alpha=0.7)
    plt.xlabel('CWE Index (Ranked)')
    plt.ylabel('Frequency')
    plt.title('CWE Detection Frequency Distribution')
    plt.xticks(range(0, len(cwe_freq), 2), rotation=45)
    
    # 2. Tool Performance Radar Chart
    plt.subplot(1, 3, 2)
    tools = coverage_data['Tool'].values
    metrics = ['Total_CWEs_Detected', 'Top_25_Coverage_Percentage', 'Total_Findings']
    
    # Normalize metrics for radar chart
    normalized_data = coverage_data[metrics].copy()
    for col in metrics:
        normalized_data[col] = (normalized_data[col] / normalized_data[col].max()) * 10
    
    angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    for i, tool in enumerate(tools):
        values = normalized_data.iloc[i].tolist()
        values += values[:1]  # Complete the circle
        plt.polar(angles, values, 'o-', linewidth=2, label=tool, color=colors[i])
        plt.fill(angles, values, alpha=0.25, color=colors[i])
    
    plt.thetagrids(np.degrees(angles[:-1]), metrics)
    plt.ylim(0, 10)
    plt.title('Tool Performance Comparison')
    plt.legend()
    
    # 3. Findings Distribution by Project
    plt.subplot(1, 3, 3)
    project_findings = vuln_data.groupby('Project_name')['Number_of_Findings'].sum().sort_values(ascending=True)
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    bars = plt.barh(project_findings.index, project_findings.values, color=colors, alpha=0.7)
    plt.xlabel('Total Findings')
    plt.title('Vulnerability Findings by Project')
    
    # Add value labels on bars
    for bar, value in zip(bars, project_findings.values):
        plt.text(value + 5, bar.get_y() + bar.get_height()/2, 
                f'{value}', va='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/workspaces/STT/STT/Week 6/lab6/visualizations/additional_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.show()
    
    # 4. Correlation Analysis
    plt.figure(figsize=(10, 6))
    
    # Create correlation matrix for tool metrics
    corr_matrix = coverage_data[['Total_CWEs_Detected', 'Top_25_CWEs_Detected', 
                                'Top_25_Coverage_Percentage', 'Total_Findings', 
                                'Average_Findings_Per_CWE']].corr()
    
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                square=True, cbar_kws={'label': 'Correlation Coefficient'})
    plt.title('Tool Metrics Correlation Analysis')
    plt.tight_layout()
    plt.savefig('/workspaces/STT/STT/Week 6/lab6/visualizations/correlation_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Additional plots created:")
    print("- additional_analysis.png: CWE distribution, radar chart, project findings")
    print("- correlation_analysis.png: Tool metrics correlation heatmap")

def create_readme():
    """Create a comprehensive README file for the lab."""
    readme_content = """# Lab 6: Vulnerability Analysis Tools Evaluation

## Overview
This lab evaluates three vulnerability analysis tools (Bandit, Semgrep, CodeQL) across three large-scale open-source Python projects (Flask, Requests, Django) using CWE-based comparison and IoU analysis.

## 🎯 Objectives
- Apply multiple vulnerability analysis tools on real-world projects
- Extract CWE-based findings from security tools
- Compare tools based on CWE coverage (breadth of vulnerabilities detected)
- Compute and interpret pairwise IoU values between tools
- Visualize and analyze CWE-based vulnerability detection results

## 📁 Project Structure
```
lab6/
├── data/
│   └── consolidated_vulnerability_findings.csv    # Raw vulnerability data
├── results/
│   ├── Lab6_Comprehensive_Report.md              # Main report
│   ├── repository_selection_methodology.md        # Selection criteria
│   ├── cwe_coverage_analysis.csv                 # Tool coverage metrics
│   ├── iou_matrix.csv                            # Tool similarity matrix
│   └── detailed_statistics.md                    # Statistical analysis
├── visualizations/
│   ├── cwe_coverage_analysis.png                 # Coverage comparison
│   ├── iou_heatmap.png                          # IoU matrix heatmap
│   ├── comprehensive_analysis.png                # Multi-panel analysis
│   ├── additional_analysis.png                   # Extended visualizations
│   ├── correlation_analysis.png                  # Metrics correlation
│   ├── interactive_dashboard.html                # Interactive dashboard
│   ├── interactive_iou_heatmap.html             # Interactive IoU matrix
│   └── vulnerability_sunburst.html               # Hierarchical view
├── scripts/
└── vulnerability_analysis_lab.py                 # Main analysis script
```

## 🔧 Tools & Technologies
- **Python 3.12+** with scientific computing stack
- **Pandas** for data manipulation
- **Matplotlib & Seaborn** for static visualizations  
- **Plotly** for interactive visualizations
- **NumPy** for numerical computations

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install pandas numpy matplotlib seaborn plotly scipy scikit-learn
```

### 2. Run Analysis
```bash
python vulnerability_analysis_lab.py
```

### 3. View Results
- Open `results/Lab6_Comprehensive_Report.md` for the main analysis
- Check `visualizations/` folder for all charts and plots
- View interactive visualizations by opening HTML files in browser

## 📊 Key Findings

### Tool Performance Summary
| Tool    | CWEs Detected | Top 25 Coverage | Total Findings | Effectiveness |
|---------|--------------|----------------|----------------|---------------|
| Semgrep | 7            | 20.0%          | 212            | 13.25         |
| CodeQL  | 7            | 16.0%          | 147            | 10.50         |
| Bandit  | 6            | 12.0%          | 79             | 8.78          |

### IoU Analysis Results
- **Average IoU**: 0.056 (Low tool overlap - high complementarity)
- **Best tool pair**: Semgrep + CodeQL (0.167 IoU)
- **Recommendation**: Use multiple tools for comprehensive coverage

## 📈 Visualizations Generated

### Static Plots
1. **CWE Coverage Analysis**: Tool comparison for detection breadth
2. **IoU Heatmap**: Tool similarity matrix visualization
3. **Comprehensive Analysis**: Multi-panel vulnerability insights
4. **Additional Analysis**: Extended metrics and distributions
5. **Correlation Analysis**: Tool metrics relationships

### Interactive Visualizations
1. **Interactive Dashboard**: Comprehensive tool analysis
2. **Interactive IoU Heatmap**: Explorable similarity matrix
3. **Vulnerability Sunburst**: Hierarchical vulnerability distribution

## 🎯 Repository Selection Criteria

### Primary Criteria
- **Minimum Stars**: 5,000+ (community adoption)
- **Minimum Forks**: 1,000+ (developer engagement)
- **Languages**: Python focus for tool compatibility
- **Size**: 10-1000 MB (suitable for analysis)
- **Activity**: Recent development within 6 months

### Selected Repositories
1. **Flask** (67k stars): Micro web framework
2. **Requests** (52k stars): HTTP library  
3. **Django** (79k stars): High-level web framework

## 🔍 Analysis Methodology

### 1. Data Collection
- Execute vulnerability scans with CWE mapping
- Extract structured findings (CSV format)
- Aggregate by CWE ID with finding counts
- Flag Top 25 CWE categories

### 2. Coverage Analysis
- Calculate unique CWEs detected per tool
- Compute Top 25 CWE coverage percentages
- Analyze tool effectiveness metrics

### 3. IoU Analysis
- Compute Jaccard Index for tool pairs
- Create Tool × Tool similarity matrix
- Interpret overlap and complementarity

### 4. Visualization
- Generate comprehensive static plots
- Create interactive visualizations
- Develop multi-perspective analysis views

## 📋 Key Insights

### Tool Complementarity
- **Low average IoU (0.056)** indicates tools detect different vulnerability types
- **Combining tools** significantly increases CWE coverage
- **No single tool** provides comprehensive vulnerability detection

### Project-Specific Patterns
- **Django**: Highest vulnerability count (framework complexity)
- **Flask**: Moderate findings (lightweight framework)
- **Requests**: Lowest findings (focused library)

### CWE Coverage
- **40% Top 25 CWE coverage** across all tools combined
- **Semgrep leads** with 20% individual coverage
- **Critical gaps** remain in vulnerability detection

## 🚨 Recommendations

### For Security Teams
1. **Deploy multiple tools** with complementary strengths
2. **Prioritize Top 25 CWE** coverage for critical vulnerabilities
3. **Consider project characteristics** when selecting tools

### For Tool Selection
1. **Semgrep**: Best overall coverage and findings
2. **CodeQL**: Strong semantic analysis capabilities
3. **Bandit**: Python-specific security focus

### For Future Work
1. Expand to additional programming languages
2. Investigate false positive rates
3. Develop automated tool selection recommendations

## 📚 References
- [CWE Top 25 Most Dangerous Software Weaknesses](https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html)
- [Jaccard Index (IoU) for Set Similarity](https://en.wikipedia.org/wiki/Jaccard_index)
- [Static Application Security Testing (SAST) Tools Comparison](https://owasp.org/www-community/Source_Code_Analysis_Tools)

---
**Generated**: September 15, 2025  
**Course**: CS202 Software Tools and Techniques for CSE  
**Lab**: Vulnerability Analysis Tools Evaluation using CWE-based Comparison
"""
    
    with open("/workspaces/STT/STT/Week 6/lab6/README.md", 'w') as f:
        f.write(readme_content)
    
    print("Comprehensive README.md created!")

def main():
    """Run all enhanced analysis functions."""
    print("="*60)
    print("Enhanced Analysis for Lab 6")
    print("="*60)
    
    print("\n1. Creating interactive visualizations...")
    create_interactive_visualizations()
    
    print("\n2. Generating detailed statistics...")
    generate_detailed_statistics()
    
    print("\n3. Creating additional plots...")
    create_additional_plots()
    
    print("\n4. Creating comprehensive README...")
    create_readme()
    
    print("\n" + "="*60)
    print("Enhanced Analysis Complete!")
    print("="*60)
    print("\nNew files generated:")
    print("- README.md: Comprehensive project documentation")
    print("- results/detailed_statistics.md: Statistical analysis")
    print("- visualizations/additional_analysis.png: Extended plots")
    print("- visualizations/correlation_analysis.png: Metrics correlation")
    print("- visualizations/interactive_dashboard.html: Interactive dashboard")
    print("- visualizations/interactive_iou_heatmap.html: Interactive IoU matrix")
    print("- visualizations/vulnerability_sunburst.html: Hierarchical visualization")

if __name__ == "__main__":
    main()
