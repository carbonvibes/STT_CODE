"""
Reaching Definitions Analysis Module
Implements reaching definitions analysis using dataflow equations.
"""

import re
from typing import Dict, Set, List, Tuple
from cfg_builder import BasicBlock


class Definition:
    """Represents a definition (assignment) in the program"""
    def __init__(self, def_id: str, variable: str, statement: str, block_id: int):
        self.id = def_id
        self.variable = variable
        self.statement = statement
        self.block_id = block_id
        
    def __str__(self):
        return f"{self.id}: {self.variable} = ... (in {self.statement})"
    
    def __repr__(self):
        return self.id
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if isinstance(other, Definition):
            return self.id == other.id
        return False


class ReachingDefinitionsAnalyzer:
    """Performs reaching definitions analysis on a CFG"""
    
    def __init__(self, basic_blocks: Dict[int, BasicBlock]):
        self.basic_blocks = basic_blocks
        self.definitions = []
        self.def_counter = 1
        self.gen = {}  # gen[B] for each block
        self.kill = {}  # kill[B] for each block
        self.in_set = {}  # in[B] for each block
        self.out_set = {}  # out[B] for each block
        self.iterations = []  # Store iterations for reporting
        
    def extract_definitions(self) -> List[Definition]:
        """
        Extract all definitions (assignments) from the CFG.
        A definition is any statement that assigns a value to a variable.
        """
        definitions = []
        
        # Common C assignment patterns
        assignment_patterns = [
            r'(\w+)\s*=\s*[^=]',  # Simple assignment: var = ...
            r'(\w+)\s*\+\+',  # Post-increment: var++
            r'(\w+)\s*--',  # Post-decrement: var--
            r'\+\+\s*(\w+)',  # Pre-increment: ++var
            r'--\s*(\w+)',  # Pre-decrement: --var
            r'(\w+)\s*\+=',  # Compound assignment: var += ...
            r'(\w+)\s*-=',
            r'(\w+)\s*\*=',
            r'(\w+)\s*/=',
        ]
        
        for block_id, block in self.basic_blocks.items():
            for stmt in block.statements:
                # Skip declarations without initialization
                if any(keyword in stmt for keyword in ['int', 'float', 'double', 'char', 'void']):
                    # Check if it's an initialization
                    if '=' in stmt:
                        # Extract variable name
                        match = re.search(r'(int|float|double|char)\s+(\w+)\s*=', stmt)
                        if match:
                            var_name = match.group(2)
                            def_id = f"D{self.def_counter}"
                            definition = Definition(def_id, var_name, stmt, block_id)
                            definitions.append(definition)
                            self.def_counter += 1
                else:
                    # Check for assignments
                    for pattern in assignment_patterns:
                        match = re.search(pattern, stmt)
                        if match:
                            var_name = match.group(1)
                            # Skip if it's a comparison (==)
                            if '==' not in stmt or stmt.index('=') < stmt.index('=='):
                                def_id = f"D{self.def_counter}"
                                definition = Definition(def_id, var_name, stmt, block_id)
                                definitions.append(definition)
                                self.def_counter += 1
                                break  # Only one definition per statement
        
        self.definitions = definitions
        return definitions
    
    def compute_gen_kill(self):
        """
        Compute gen[B] and kill[B] for each basic block.
        - gen[B]: definitions generated (created) in block B
        - kill[B]: definitions killed (overwritten) by block B
        """
        # Initialize gen and kill sets
        for block_id in self.basic_blocks.keys():
            self.gen[block_id] = set()
            self.kill[block_id] = set()
        
        # Compute gen sets - definitions created in each block
        for definition in self.definitions:
            self.gen[definition.block_id].add(definition)
        
        # Compute kill sets - definitions of same variable in other blocks
        for block_id in self.basic_blocks.keys():
            for def_in_block in self.gen[block_id]:
                # Find all other definitions of the same variable
                for other_def in self.definitions:
                    if (other_def.variable == def_in_block.variable and 
                        other_def.id != def_in_block.id):
                        self.kill[block_id].add(other_def)
    
    def apply_dataflow_equations(self) -> int:
        """
        Apply dataflow equations iteratively until convergence:
        - in[B] = union of out[P] for all predecessors P of B
        - out[B] = gen[B] union (in[B] - kill[B])
        
        Returns the number of iterations needed for convergence.
        """
        # Initialize in and out sets
        for block_id in self.basic_blocks.keys():
            self.in_set[block_id] = set()
            self.out_set[block_id] = set()
        
        iteration = 0
        changed = True
        
        while changed:
            iteration += 1
            changed = False
            
            # Store current state for reporting
            iteration_state = {
                'iteration': iteration,
                'in': {bid: set(s) for bid, s in self.in_set.items()},
                'out': {bid: set(s) for bid, s in self.out_set.items()}
            }
            
            # Process each block
            for block_id in sorted(self.basic_blocks.keys()):
                block = self.basic_blocks[block_id]
                
                # Compute in[B] = union of out[P] for all predecessors
                new_in = set()
                for pred_id in block.predecessors:
                    new_in = new_in.union(self.out_set[pred_id])
                
                # Compute out[B] = gen[B] union (in[B] - kill[B])
                new_out = self.gen[block_id].union(new_in - self.kill[block_id])
                
                # Check if anything changed
                if new_in != self.in_set[block_id] or new_out != self.out_set[block_id]:
                    changed = True
                    self.in_set[block_id] = new_in
                    self.out_set[block_id] = new_out
            
            self.iterations.append(iteration_state)
            
            # Safety check to prevent infinite loops
            if iteration > 100:
                print("Warning: Maximum iterations reached!")
                break
        
        return iteration
    
    def analyze(self) -> Tuple[List[Definition], int]:
        """
        Perform complete reaching definitions analysis.
        Returns (definitions, num_iterations)
        """
        print("Extracting definitions...")
        definitions = self.extract_definitions()
        
        print(f"Found {len(definitions)} definitions")
        print("\nComputing gen and kill sets...")
        self.compute_gen_kill()
        
        print("Applying dataflow equations...")
        num_iterations = self.apply_dataflow_equations()
        
        print(f"Converged in {num_iterations} iterations")
        
        return definitions, num_iterations
    
    def get_definition_mapping(self) -> Dict[str, str]:
        """Get mapping of definition IDs to their code"""
        mapping = {}
        for definition in self.definitions:
            mapping[definition.id] = f"{definition.variable} in '{definition.statement}'"
        return mapping
    
    def format_def_set(self, def_set: Set[Definition]) -> str:
        """Format a set of definitions for display"""
        if not def_set:
            return "{}"
        return "{" + ", ".join(sorted([d.id for d in def_set])) + "}"
    
    def generate_analysis_table(self) -> List[Dict]:
        """Generate table data for reaching definitions analysis"""
        table_data = []
        
        for block_id in sorted(self.basic_blocks.keys()):
            row = {
                'block': f"B{block_id}",
                'gen': self.format_def_set(self.gen[block_id]),
                'kill': self.format_def_set(self.kill[block_id]),
                'in': self.format_def_set(self.in_set[block_id]),
                'out': self.format_def_set(self.out_set[block_id])
            }
            table_data.append(row)
        
        return table_data
    
    def interpret_results(self) -> List[str]:
        """
        Interpret the reaching definitions analysis results.
        Identify variables with multiple reaching definitions at program points.
        """
        interpretations = []
        
        # Analyze each block's in set
        for block_id in sorted(self.basic_blocks.keys()):
            in_defs = self.in_set[block_id]
            
            if not in_defs:
                continue
            
            # Group definitions by variable
            var_defs = {}
            for definition in in_defs:
                if definition.variable not in var_defs:
                    var_defs[definition.variable] = []
                var_defs[definition.variable].append(definition.id)
            
            # Find variables with multiple reaching definitions
            for var, defs in var_defs.items():
                if len(defs) > 1:
                    interpretation = (
                        f"At entry to block B{block_id}, variable '{var}' has "
                        f"{len(defs)} possible reaching definitions: {', '.join(defs)}. "
                        f"This indicates multiple paths where '{var}' may have been defined."
                    )
                    interpretations.append(interpretation)
        
        # Analyze variables that are never killed
        always_live = {}
        for definition in self.definitions:
            # Check if this definition is never killed
            never_killed = True
            for block_id in self.basic_blocks.keys():
                if definition in self.kill[block_id]:
                    never_killed = False
                    break
            
            if never_killed and definition.variable not in always_live:
                always_live[definition.variable] = definition.id
        
        if always_live:
            interpretation = (
                f"Variables with definitions that are never killed (single assignment): "
                f"{', '.join([f'{var} ({did})' for var, did in always_live.items()])}"
            )
            interpretations.append(interpretation)
        
        # Check for dead definitions (definitions that never reach any use)
        dead_defs = []
        for definition in self.definitions:
            reaches_any = False
            for block_id in self.basic_blocks.keys():
                if definition in self.out_set[block_id]:
                    reaches_any = True
                    break
            
            if not reaches_any and definition.block_id != max(self.basic_blocks.keys()):
                dead_defs.append(definition.id)
        
        if dead_defs:
            interpretation = (
                f"Potentially dead definitions (never reach exit): {', '.join(dead_defs)}"
            )
            interpretations.append(interpretation)
        
        return interpretations
    
    def print_analysis(self):
        """Print analysis results to console"""
        print("\n=== Reaching Definitions Analysis ===\n")
        
        print("Definitions:")
        for definition in self.definitions:
            print(f"  {definition}")
        
        print("\n" + "="*80)
        print("Gen and Kill Sets:")
        print("="*80)
        
        for block_id in sorted(self.basic_blocks.keys()):
            print(f"\nBlock B{block_id}:")
            print(f"  gen[B{block_id}] = {self.format_def_set(self.gen[block_id])}")
            print(f"  kill[B{block_id}] = {self.format_def_set(self.kill[block_id])}")
        
        print("\n" + "="*80)
        print("Final In and Out Sets:")
        print("="*80)
        
        for block_id in sorted(self.basic_blocks.keys()):
            print(f"\nBlock B{block_id}:")
            print(f"  in[B{block_id}] = {self.format_def_set(self.in_set[block_id])}")
            print(f"  out[B{block_id}] = {self.format_def_set(self.out_set[block_id])}")
