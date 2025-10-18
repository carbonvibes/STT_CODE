"""
Main Execution Script for Lab 7: Reaching Definitions Analyzer
Course: CS202 Software Tools and Techniques for CSE

This script orchestrates the complete analysis workflow:
1. Constructs Control Flow Graphs for C programs
2. Calculates cyclomatic complexity metrics
3. Performs reaching definitions analysis
4. Generates comprehensive reports with visualizations
"""

import os
import sys
from cfg_builder import CFGBuilder
from reaching_definitions import ReachingDefinitionsAnalyzer
from report_generator import ReportGenerator


def main():
    """Main execution function"""
    print("="*80)
    print("Lab 7: Reaching Definitions Analyzer for C Programs")
    print("CS202 - Software Tools and Techniques for CSE")
    print("="*80)
    
    # Define paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    programs_dir = os.path.join(base_dir, "programs")
    results_dir = os.path.join(base_dir, "results")
    
    # Ensure directories exist
    os.makedirs(results_dir, exist_ok=True)
    
    # Define programs to analyze
    programs = [
        ("program1_calculator.c", "Calculator"),
        ("program2_matrix.c", "Matrix Operations"),
        ("program3_student.c", "Student Grade Management")
    ]
    
    # Check if program files exist
    print("\nChecking program files...")
    for prog_file, prog_name in programs:
        prog_path = os.path.join(programs_dir, prog_file)
        if not os.path.exists(prog_path):
            print(f"Error: Program file not found: {prog_path}")
            sys.exit(1)
        print(f"  ✓ Found: {prog_file}")
    
    # Initialize report generator
    report_gen = ReportGenerator(results_dir)
    
    # Analyze each program
    print("\n" + "="*80)
    print("Starting Analysis")
    print("="*80)
    
    program_results = []
    
    for prog_file, prog_name in programs:
        prog_path = os.path.join(programs_dir, prog_file)
        
        try:
            result = report_gen.generate_program_report(prog_path, prog_name)
            program_results.append(result)
            
            # Print summary
            print(f"\n✓ Analysis complete for {prog_name}")
            print(f"  - Basic Blocks: {result['N']}")
            print(f"  - Edges: {result['E']}")
            print(f"  - Cyclomatic Complexity: {result['CC']}")
            print(f"  - Definitions Found: {len(result['definitions'])}")
            print(f"  - Convergence: {result['num_iterations']} iterations")
            
        except Exception as e:
            print(f"\n✗ Error analyzing {prog_name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Generate final comprehensive report
    print("\n" + "="*80)
    print("Generating Final Report")
    print("="*80)
    
    if program_results:
        report_file = os.path.join(results_dir, "Lab7_Final_Report.md")
        report_gen.generate_final_report(program_results, report_file)
        
        print("\n" + "="*80)
        print("Analysis Complete!")
        print("="*80)
        print(f"\nResults saved to: {results_dir}")
        print(f"  - Final Report: {report_file}")
        print(f"  - CFG Diagrams: {os.path.join(results_dir, 'cfg_diagrams')}")
        print("\nPrograms analyzed:")
        for result in program_results:
            print(f"  ✓ {result['program_name']}")
        
        print("\nTo view the report:")
        print(f"  cat {report_file}")
        print(f"  or open {report_file} in a markdown viewer")
    else:
        print("\n✗ No programs were successfully analyzed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
