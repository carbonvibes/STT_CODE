
# Detailed Statistical Analysis

## Dataset Overview

- **Total Vulnerability Findings**: 438
- **Unique CWE Types**: 18
- **Projects Analyzed**: 3
- **Tools Evaluated**: 3
- **Average Findings per CWE**: 11.23
- **Standard Deviation**: 6.19

## Tool Performance Analysis

### Tool Rankings:

1. **Semgrep**
   - Total Findings: 212
   - CWEs Detected: 7
   - Top 25 Coverage: 20.0%
   - Effectiveness Score: 13.25

2. **CodeQL**
   - Total Findings: 147
   - CWEs Detected: 7
   - Top 25 Coverage: 16.0%
   - Effectiveness Score: 10.50

3. **Bandit**
   - Total Findings: 79
   - CWEs Detected: 6
   - Top 25 Coverage: 12.0%
   - Effectiveness Score: 8.78

## Project-Specific Analysis


### Flask
- Total Findings: 121
- Unique CWEs: 11
- Most Common CWE: CWE-89
- Risk Level: Medium

### Requests
- Total Findings: 101
- Unique CWEs: 11
- Most Common CWE: CWE-200
- Risk Level: Medium

### Django
- Total Findings: 216
- Unique CWEs: 13
- Most Common CWE: CWE-79
- Risk Level: High

## Tool Similarity Analysis (IoU)


- **Average IoU**: 0.056
- **Maximum IoU**: 0.167
- **Minimum IoU**: 0.000
- **Interpretation**: Low similarity

### Tool Pair Analysis:
- **Bandit vs Semgrep**: 0.000 (Low overlap)
- **Bandit vs CodeQL**: 0.000 (Low overlap)
- **Semgrep vs CodeQL**: 0.167 (Low overlap)
