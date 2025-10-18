"""
CFG Construction Module
Constructs Control Flow Graphs from C programs by identifying leaders,
creating basic blocks, and building the control flow structure.
"""

import re
from typing import List, Dict, Tuple, Set


class BasicBlock:
    """Represents a basic block in the CFG"""
    def __init__(self, block_id: int, label: str = ""):
        self.id = block_id
        self.label = label or f"B{block_id}"
        self.statements = []
        self.successors = []
        self.predecessors = []
        
    def add_statement(self, statement: str):
        """Add a statement to this basic block"""
        self.statements.append(statement)
        
    def add_successor(self, block_id: int):
        """Add a successor block"""
        if block_id not in self.successors:
            self.successors.append(block_id)
            
    def add_predecessor(self, block_id: int):
        """Add a predecessor block"""
        if block_id not in self.predecessors:
            self.predecessors.append(block_id)
    
    def get_code(self) -> str:
        """Get the code representation of this block"""
        return "\\n".join(self.statements)
    
    def __str__(self):
        return f"{self.label}: {len(self.statements)} statements"


class CFGBuilder:
    """Builds Control Flow Graphs from C source code"""
    
    def __init__(self, source_file: str):
        self.source_file = source_file
        self.source_code = ""
        self.lines = []
        self.basic_blocks = {}
        self.entry_block = None
        self.exit_block = None
        self.block_counter = 0
        
    def read_source(self):
        """Read the C source file"""
        with open(self.source_file, 'r') as f:
            self.source_code = f.read()
        self.lines = self.source_code.split('\n')
        
    def preprocess_code(self) -> List[str]:
        """
        Preprocess the code to simplify analysis:
        - Remove comments
        - Remove empty lines
        - Normalize whitespace
        """
        processed_lines = []
        in_multiline_comment = False
        
        for line in self.lines:
            # Handle multi-line comments
            if '/*' in line:
                in_multiline_comment = True
                line = line[:line.index('/*')]
            if '*/' in line:
                in_multiline_comment = False
                line = line[line.index('*/') + 2:]
                
            if in_multiline_comment:
                continue
                
            # Remove single-line comments
            if '//' in line:
                line = line[:line.index('//')]
                
            # Strip whitespace
            line = line.strip()
            
            # Skip empty lines and preprocessor directives
            if line and not line.startswith('#'):
                processed_lines.append(line)
                
        return processed_lines
    
    def identify_leaders(self, statements: List[str]) -> Set[int]:
        """
        Identify leaders according to the rules:
        1. First statement is a leader
        2. Target of any branch/jump/loop is a leader
        3. Statement immediately after branch/jump/loop is a leader
        """
        leaders = set()
        
        if not statements:
            return leaders
            
        # Rule 1: First statement is a leader
        leaders.add(0)
        
        # Keywords that indicate control flow
        branch_keywords = ['if', 'else', 'while', 'for', 'do', 'switch', 'case']
        
        for i, stmt in enumerate(statements):
            stmt_lower = stmt.lower()
            
            # Rule 2 & 3: Branches and loops
            if any(keyword in stmt_lower for keyword in branch_keywords):
                leaders.add(i)  # The branch/loop statement itself
                if i + 1 < len(statements):
                    leaders.add(i + 1)  # Statement after branch
                    
            # Check for opening braces (start of block)
            if '{' in stmt:
                if i + 1 < len(statements):
                    leaders.add(i + 1)
                    
            # Check for closing braces (end of block)
            if '}' in stmt:
                if i + 1 < len(statements):
                    leaders.add(i + 1)
                    
            # Return statements
            if 'return' in stmt_lower:
                if i + 1 < len(statements):
                    leaders.add(i + 1)
                    
            # Break and continue statements
            if 'break' in stmt_lower or 'continue' in stmt_lower:
                if i + 1 < len(statements):
                    leaders.add(i + 1)
        
        return leaders
    
    def create_basic_blocks(self, statements: List[str], leaders: Set[int]) -> Dict[int, BasicBlock]:
        """Create basic blocks from leaders"""
        blocks = {}
        sorted_leaders = sorted(leaders)
        
        for i, leader_idx in enumerate(sorted_leaders):
            block = BasicBlock(i, f"B{i}")
            
            # Determine the end of this block
            if i + 1 < len(sorted_leaders):
                end_idx = sorted_leaders[i + 1]
            else:
                end_idx = len(statements)
            
            # Add statements to the block
            for stmt_idx in range(leader_idx, end_idx):
                if stmt_idx < len(statements):
                    block.add_statement(statements[stmt_idx])
            
            blocks[i] = block
            
        return blocks
    
    def build_control_flow(self, blocks: Dict[int, BasicBlock], statements: List[str]):
        """Build control flow edges between basic blocks"""
        sorted_block_ids = sorted(blocks.keys())
        
        for i, block_id in enumerate(sorted_block_ids):
            block = blocks[block_id]
            
            if not block.statements:
                continue
                
            last_stmt = block.statements[-1].lower()
            
            # Determine control flow based on last statement
            has_explicit_flow = False
            
            # Check for if statement
            if 'if' in last_stmt and '{' not in last_stmt:
                # If statement - branches to next block (true) and potentially skips
                if i + 1 < len(sorted_block_ids):
                    block.add_successor(sorted_block_ids[i + 1])
                    blocks[sorted_block_ids[i + 1]].add_predecessor(block_id)
                if i + 2 < len(sorted_block_ids):
                    block.add_successor(sorted_block_ids[i + 2])
                    blocks[sorted_block_ids[i + 2]].add_predecessor(block_id)
                has_explicit_flow = True
                
            # Check for else
            elif 'else' in last_stmt:
                if i + 1 < len(sorted_block_ids):
                    block.add_successor(sorted_block_ids[i + 1])
                    blocks[sorted_block_ids[i + 1]].add_predecessor(block_id)
                has_explicit_flow = True
                
            # Check for while/for loop
            elif 'while' in last_stmt or 'for' in last_stmt:
                # Loop condition - branches to body and exit
                if i + 1 < len(sorted_block_ids):
                    block.add_successor(sorted_block_ids[i + 1])
                    blocks[sorted_block_ids[i + 1]].add_predecessor(block_id)
                # Also add edge to exit (after loop)
                if i + 2 < len(sorted_block_ids):
                    block.add_successor(sorted_block_ids[i + 2])
                    blocks[sorted_block_ids[i + 2]].add_predecessor(block_id)
                has_explicit_flow = True
                
            # Check for return statement
            elif 'return' in last_stmt:
                # No successor (exits function)
                has_explicit_flow = True
                
            # Check for break/continue
            elif 'break' in last_stmt or 'continue' in last_stmt:
                # Will need context to determine target
                has_explicit_flow = True
            
            # Default: sequential flow to next block
            if not has_explicit_flow and i + 1 < len(sorted_block_ids):
                block.add_successor(sorted_block_ids[i + 1])
                blocks[sorted_block_ids[i + 1]].add_predecessor(block_id)
    
    def build_cfg(self) -> Dict[int, BasicBlock]:
        """Main method to build the CFG"""
        self.read_source()
        statements = self.preprocess_code()
        
        # Identify leaders
        leaders = self.identify_leaders(statements)
        
        # Create basic blocks
        self.basic_blocks = self.create_basic_blocks(statements, leaders)
        
        # Build control flow edges
        self.build_control_flow(self.basic_blocks, statements)
        
        # Set entry and exit blocks
        if self.basic_blocks:
            self.entry_block = 0
            self.exit_block = max(self.basic_blocks.keys())
        
        return self.basic_blocks
    
    def generate_dot(self, output_file: str):
        """Generate Graphviz DOT file for visualization"""
        with open(output_file, 'w') as f:
            f.write("digraph CFG {\n")
            f.write("    node [shape=box, style=filled, fillcolor=lightblue];\n")
            f.write("    rankdir=TB;\n\n")
            
            # Write nodes
            for block_id, block in self.basic_blocks.items():
                label = f"{block.label}:\\n"
                # Escape special characters and limit statement length
                for stmt in block.statements:
                    stmt_clean = stmt.replace('"', '\\"').replace('\\n', '\\\\n')
                    if len(stmt_clean) > 60:
                        stmt_clean = stmt_clean[:60] + "..."
                    label += stmt_clean + "\\n"
                
                # Color entry and exit blocks differently
                if block_id == self.entry_block:
                    f.write(f'    {block_id} [label="{label}", fillcolor=lightgreen];\n')
                elif block_id == self.exit_block:
                    f.write(f'    {block_id} [label="{label}", fillcolor=lightcoral];\n')
                else:
                    f.write(f'    {block_id} [label="{label}"];\n')
            
            f.write("\n")
            
            # Write edges
            for block_id, block in self.basic_blocks.items():
                for successor in block.successors:
                    # Determine edge label based on context
                    if len(block.successors) > 1:
                        # Multiple successors - likely a branch
                        if block.successors.index(successor) == 0:
                            f.write(f'    {block_id} -> {successor} [label="true"];\n')
                        else:
                            f.write(f'    {block_id} -> {successor} [label="false"];\n')
                    else:
                        f.write(f'    {block_id} -> {successor};\n')
            
            f.write("}\n")
    
    def get_metrics(self) -> Tuple[int, int, int]:
        """
        Calculate CFG metrics:
        Returns (N, E, CC) where:
        - N = number of nodes (basic blocks)
        - E = number of edges
        - CC = cyclomatic complexity (E - N + 2)
        """
        N = len(self.basic_blocks)
        E = sum(len(block.successors) for block in self.basic_blocks.values())
        CC = E - N + 2
        return N, E, CC
    
    def print_cfg(self):
        """Print CFG structure for debugging"""
        print(f"\nControl Flow Graph for {self.source_file}")
        print(f"Number of basic blocks: {len(self.basic_blocks)}")
        print("\nBasic Blocks:")
        
        for block_id in sorted(self.basic_blocks.keys()):
            block = self.basic_blocks[block_id]
            print(f"\n{block.label}:")
            for stmt in block.statements:
                print(f"  {stmt}")
            print(f"  Successors: {block.successors}")
            print(f"  Predecessors: {block.predecessors}")
