"""
Report Generator Module
Generates comprehensive reports including CFG diagrams, metrics tables,
and reaching definitions analysis results.
"""

import os
import subprocess
from typing import Dict, List
from cfg_builder import CFGBuilder, BasicBlock
from reaching_definitions import ReachingDefinitionsAnalyzer


class ReportGenerator:
    """Generates analysis reports in markdown format"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.cfg_dir = os.path.join(output_dir, "cfg_diagrams")
        os.makedirs(self.cfg_dir, exist_ok=True)
        
    def generate_cfg_diagram(self, cfg_builder: CFGBuilder, program_name: str) -> str:
        """Generate CFG diagram using Graphviz"""
        dot_file = os.path.join(self.cfg_dir, f"{program_name}_cfg.dot")
        png_file = os.path.join(self.cfg_dir, f"{program_name}_cfg.png")
        
        # Generate DOT file
        cfg_builder.generate_dot(dot_file)
        
        # Generate PNG using Graphviz
        try:
            result = subprocess.run(
                ['dot', '-Tpng', dot_file, '-o', png_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"Generated CFG diagram: {png_file}")
                return png_file
            else:
                print(f"Error generating diagram: {result.stderr}")
                return dot_file
        except FileNotFoundError:
            print("Warning: Graphviz not found. Install with: apt-get install graphviz")
            return dot_file
        except Exception as e:
            print(f"Error generating diagram: {e}")
            return dot_file
    
    def generate_metrics_table_markdown(self, metrics_data: List[Dict]) -> str:
        """Generate metrics table in markdown format"""
        md = "## Cyclomatic Complexity Metrics\n\n"
        md += "| Program | No. of Nodes (N) | No. of Edges (E) | Cyclomatic Complexity (CC) |\n"
        md += "|---------|------------------|------------------|---------------------------|\n"
        
        for metric in metrics_data:
            md += f"| {metric['program']} | {metric['N']} | {metric['E']} | {metric['CC']} |\n"
        
        md += "\n**Note:** Cyclomatic Complexity (CC) = E - N + 2\n\n"
        return md
    
    def generate_definitions_table_markdown(self, definitions: List, mapping: Dict[str, str]) -> str:
        """Generate definitions mapping table"""
        md = "## Definitions Mapping\n\n"
        md += "| Definition ID | Variable | Statement |\n"
        md += "|---------------|----------|----------|\n"
        
        for definition in definitions:
            # Escape pipe characters in statement
            stmt = definition.statement.replace('|', '\\|')
            if len(stmt) > 60:
                stmt = stmt[:60] + "..."
            md += f"| {definition.id} | {definition.variable} | {stmt} |\n"
        
        md += "\n"
        return md
    
    def generate_reaching_defs_table_markdown(self, table_data: List[Dict]) -> str:
        """Generate reaching definitions analysis table"""
        md = "## Reaching Definitions Analysis Results (Final)\n\n"
        md += "| Basic Block | gen[B] | kill[B] | in[B] | out[B] |\n"
        md += "|-------------|--------|---------|-------|--------|\n"
        
        for row in table_data:
            md += f"| {row['block']} | {row['gen']} | {row['kill']} | "
            md += f"{row['in']} | {row['out']} |\n"
        
        md += "\n"
        return md
    
    def generate_iterations_tables_markdown(self, rd_analyzer) -> str:
        """Generate iteration-by-iteration analysis tables"""
        md = "## Iterative Computation Process\n\n"
        md += "The following tables show how the in[B] and out[B] sets evolve "
        md += "during each iteration until convergence.\n\n"
        
        if not rd_analyzer.iterations:
            md += "No iteration data available.\n\n"
            return md
        
        for iter_data in rd_analyzer.iterations:
            iteration_num = iter_data['iteration']
            md += f"### Iteration {iteration_num}\n\n"
            md += "| Basic Block | in[B] | out[B] |\n"
            md += "|-------------|-------|--------|\n"
            
            for block_id in sorted(iter_data['in'].keys()):
                in_set = iter_data['in'][block_id]
                out_set = iter_data['out'][block_id]
                
                in_str = rd_analyzer.format_def_set(in_set)
                out_str = rd_analyzer.format_def_set(out_set)
                
                md += f"| B{block_id} | {in_str} | {out_str} |\n"
            
            md += "\n"
        
        md += f"**Convergence achieved after {len(rd_analyzer.iterations)} iteration(s).**\n\n"
        return md
    
    def generate_interpretations_markdown(self, interpretations: List[str]) -> str:
        """Generate interpretations section"""
        md = "## Interpretation of Results\n\n"
        
        if not interpretations:
            md += "No multiple reaching definitions detected. All variables have unique definitions at each program point.\n\n"
        else:
            for i, interpretation in enumerate(interpretations, 1):
                md += f"{i}. {interpretation}\n\n"
        
        return md
    
    def generate_program_report(self, program_file: str, program_name: str) -> Dict:
        """Generate complete analysis report for a single program"""
        print(f"\n{'='*80}")
        print(f"Analyzing: {program_name}")
        print(f"{'='*80}")
        
        # Build CFG
        cfg_builder = CFGBuilder(program_file)
        basic_blocks = cfg_builder.build_cfg()
        
        # Get metrics
        N, E, CC = cfg_builder.get_metrics()
        print(f"\nMetrics: N={N}, E={E}, CC={CC}")
        
        # Generate CFG diagram
        diagram_file = self.generate_cfg_diagram(cfg_builder, program_name)
        
        # Perform reaching definitions analysis
        rd_analyzer = ReachingDefinitionsAnalyzer(basic_blocks)
        definitions, num_iterations = rd_analyzer.analyze()
        
        # Get analysis results
        def_mapping = rd_analyzer.get_definition_mapping()
        analysis_table = rd_analyzer.generate_analysis_table()
        interpretations = rd_analyzer.interpret_results()
        
        return {
            'program_name': program_name,
            'program_file': program_file,
            'N': N,
            'E': E,
            'CC': CC,
            'diagram_file': diagram_file,
            'definitions': definitions,
            'def_mapping': def_mapping,
            'analysis_table': analysis_table,
            'interpretations': interpretations,
            'num_iterations': num_iterations,
            'basic_blocks': basic_blocks,
            'rd_analyzer': rd_analyzer
        }
    
    def generate_final_report(self, program_results: List[Dict], output_file: str):
        """Generate final comprehensive report"""
        md = "# Lab 7: Reaching Definitions Analysis Report\n\n"
        md += "**Course:** CS202 Software Tools and Techniques for CSE\n\n"
        md += "**Lab Topic:** Reaching Definitions Analyzer for C Programs\n\n"
        md += "---\n\n"
        
        # Table of Contents
        md += "## Table of Contents\n\n"
        md += "1. [Program Corpus Selection](#program-corpus-selection)\n"
        md += "2. [Control Flow Graphs](#control-flow-graphs)\n"
        md += "3. [Cyclomatic Complexity Metrics](#cyclomatic-complexity-metrics)\n"
        md += "4. [Reaching Definitions Analysis](#reaching-definitions-analysis)\n"
        md += "5. [Conclusions](#conclusions)\n\n"
        md += "---\n\n"
        
        # Program Corpus Selection
        md += "## Program Corpus Selection\n\n"
        md += "Three C programs were selected for analysis, each containing 200-300 lines of code "
        md += "with various control flow structures.\n\n"
        
        program_descriptions = [
            {
                'name': 'Calculator',
                'file': 'program1_calculator.c',
                'description': 'A calculator program with history tracking that performs basic arithmetic operations. Includes conditionals for operation selection, loops for continuous operation, and multiple variable reassignments.',
                'features': ['Menu-driven interface', 'Operation history tracking', 'Statistical calculations (average, min, max)', 'Multiple conditional branches', 'While loops for program flow']
            },
            {
                'name': 'Matrix Operations',
                'file': 'program2_matrix.c',
                'description': 'A matrix operations processor that performs addition, subtraction, multiplication, transpose, and analysis operations. Features nested loops and complex conditional logic.',
                'features': ['Matrix arithmetic operations', 'Nested loops for matrix processing', 'Dimensional validation with conditionals', 'Multiple variable definitions in loop contexts', 'Complex control flow with nested structures']
            },
            {
                'name': 'Student Grade Management',
                'file': 'program3_student.c',
                'description': 'A student grade management system with statistics, sorting, and reporting. Includes arrays, structures, and various control flow patterns.',
                'features': ['Array and structure manipulation', 'Sorting algorithms with loops', 'Search functionality with conditionals', 'Statistical calculations', 'Multiple data updates and reassignments']
            }
        ]
        
        for i, desc in enumerate(program_descriptions, 1):
            md += f"### Program {i}: {desc['name']}\n\n"
            md += f"**File:** `{desc['file']}`\n\n"
            md += f"**Description:** {desc['description']}\n\n"
            md += "**Key Features:**\n"
            for feature in desc['features']:
                md += f"- {feature}\n"
            md += "\n"
            md += f"**Justification:** This program was selected because it demonstrates real-world control flow complexity with "
            md += f"{'loops' if 'loop' in desc['description'].lower() else 'conditionals'}, "
            md += f"multiple variable reassignments, and practical programming patterns suitable for dataflow analysis.\n\n"
        
        md += "---\n\n"
        
        # Control Flow Graphs
        md += "## Control Flow Graphs\n\n"
        md += "Control Flow Graphs (CFGs) were constructed for each program using the following methodology:\n\n"
        md += "### CFG Construction Methodology\n\n"
        md += "1. **Leader Identification:**\n"
        md += "   - First instruction is a leader\n"
        md += "   - Target of any branch/jump/loop is a leader\n"
        md += "   - Instruction immediately after branch/jump/loop is a leader\n\n"
        md += "2. **Basic Block Formation:**\n"
        md += "   - Group consecutive statements between leaders\n"
        md += "   - Each block has single entry and exit point\n\n"
        md += "3. **Edge Construction:**\n"
        md += "   - Sequential flow between consecutive blocks\n"
        md += "   - Conditional branches create multiple edges\n"
        md += "   - Loop edges create back edges\n\n"
        
        for result in program_results:
            md += f"### {result['program_name']} CFG\n\n"
            md += f"**Number of Basic Blocks:** {result['N']}\n\n"
            
            # Include diagram
            diagram_name = os.path.basename(result['diagram_file'])
            md += f"![{result['program_name']} CFG](cfg_diagrams/{diagram_name})\n\n"
            
            # Basic blocks summary
            md += "**Basic Blocks Summary:**\n\n"
            for block_id in sorted(result['basic_blocks'].keys()):
                block = result['basic_blocks'][block_id]
                md += f"- **B{block_id}:** {len(block.statements)} statement(s), "
                md += f"Successors: {block.successors if block.successors else 'None (exit)'}\n"
            md += "\n"
        
        md += "---\n\n"
        
        # Metrics Table
        metrics_data = [
            {
                'program': result['program_name'],
                'N': result['N'],
                'E': result['E'],
                'CC': result['CC']
            }
            for result in program_results
        ]
        md += self.generate_metrics_table_markdown(metrics_data)
        
        md += "### Metrics Analysis\n\n"
        md += "The cyclomatic complexity provides insights into program complexity:\n\n"
        for result in program_results:
            md += f"- **{result['program_name']}:** CC = {result['CC']}, indicating "
            if result['CC'] <= 10:
                md += "low to moderate complexity with straightforward control flow.\n"
            elif result['CC'] <= 20:
                md += "moderate complexity with multiple decision points.\n"
            else:
                md += "high complexity with intricate control flow structures.\n"
        md += "\n---\n\n"
        
        # Reaching Definitions Analysis
        md += "## Reaching Definitions Analysis\n\n"
        md += "Reaching definitions analysis identifies which variable definitions may reach each program point.\n\n"
        md += "### Methodology\n\n"
        md += "1. **Definition Extraction:** Identify all assignment statements\n"
        md += "2. **Gen/Kill Computation:**\n"
        md += "   - gen[B]: Definitions created in block B\n"
        md += "   - kill[B]: Definitions of same variables overwritten by B\n"
        md += "3. **Dataflow Equations:**\n"
        md += "   - in[B] = ∪ out[P] for all predecessors P\n"
        md += "   - out[B] = gen[B] ∪ (in[B] - kill[B])\n"
        md += "4. **Iterative Application:** Until convergence (no changes)\n\n"
        
        for result in program_results:
            md += f"### {result['program_name']} Analysis\n\n"
            md += f"**Convergence:** {result['num_iterations']} iteration(s)\n\n"
            
            # Definitions
            md += self.generate_definitions_table_markdown(result['definitions'], result['def_mapping'])
            
            # Gen and Kill sets
            md += "## Gen and Kill Sets\n\n"
            md += "| Basic Block | gen[B] | kill[B] |\n"
            md += "|-------------|--------|---------|\n"
            for row in result['analysis_table']:
                md += f"| {row['block']} | {row['gen']} | {row['kill']} |\n"
            md += "\n"
            
            # Iteration-by-iteration tables
            md += self.generate_iterations_tables_markdown(result['rd_analyzer'])
            
            # Final analysis table
            md += self.generate_reaching_defs_table_markdown(result['analysis_table'])
            
            # Interpretations
            md += self.generate_interpretations_markdown(result['interpretations'])
        
        md += "---\n\n"
        
        # Conclusions
        md += "## Conclusions\n\n"
        md += "This lab successfully demonstrated the implementation of reaching definitions analysis "
        md += "through the following achievements:\n\n"
        md += "1. **CFG Construction:** Successfully constructed control flow graphs for three non-trivial C programs "
        md += f"with an average of {sum(r['N'] for r in program_results) / len(program_results):.1f} basic blocks.\n\n"
        md += "2. **Complexity Metrics:** Calculated cyclomatic complexity metrics automatically, revealing "
        md += f"complexity ranging from {min(r['CC'] for r in program_results)} to {max(r['CC'] for r in program_results)}.\n\n"
        md += "3. **Reaching Definitions:** Implemented dataflow analysis that converged in "
        md += f"{min(r['num_iterations'] for r in program_results)}-{max(r['num_iterations'] for r in program_results)} iterations "
        md += "across all programs.\n\n"
        md += "4. **Analysis Insights:** Identified variables with multiple reaching definitions, "
        md += "revealing potential program points where variable values are uncertain.\n\n"
        md += "### Key Learnings\n\n"
        md += "- Understanding of CFG construction principles and leader identification\n"
        md += "- Implementation of dataflow analysis algorithms\n"
        md += "- Practical application of reaching definitions for program analysis\n"
        md += "- Experience with automated program analysis tools\n\n"
        md += "### Future Enhancements\n\n"
        md += "- Support for more complex C constructs (switch, do-while, goto)\n"
        md += "- Integration with other dataflow analyses (live variables, available expressions)\n"
        md += "- Enhanced visualization of dataflow information\n"
        md += "- Support for inter-procedural analysis\n\n"
        
        # Write report
        with open(output_file, 'w') as f:
            f.write(md)
        
        print(f"\nFinal report generated: {output_file}")
        return output_file
