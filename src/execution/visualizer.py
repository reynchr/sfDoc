# src/execution/visualizer.py
"""Visualization tools for execution paths."""

from typing import Dict, List, Optional, Set
from pathlib import Path

from src.models.analysis_models import ExecutionNode, AnalysisResult, TriggerContext, AutomationType

class ExecutionPathVisualizer:
    """Generates visualizations of execution paths."""

    def __init__(self, config: Dict):
        self.config = config
        self.include_conditions = config['visualization']['include_conditions']
        self.show_dml = config.get('visualization', {}).get('show_dml_operations', True)
        self.show_soql = config.get('visualization', {}).get('show_soql_queries', True)
        
    def generate_mermaid(self, analysis_result: AnalysisResult, context: Optional[TriggerContext] = None) -> str:
        """Generate Mermaid diagram for execution paths."""
        diagram = ["graph TD"]
        
        # Track processed nodes to avoid duplicates
        processed = set()
        
        # Process specific context or all contexts
        if context:
            paths = analysis_result.execution_paths.get(context, [])
            diagram.extend(self._process_paths(paths, processed))
        else:
            for paths in analysis_result.execution_paths.values():
                diagram.extend(self._process_paths(paths, processed))
                
        # Add styling
        diagram.extend(self._generate_styling())
        
        return "\n    ".join(diagram)
    
    def _process_paths(self, paths: List[ExecutionNode], processed: Set[str]) -> List[str]:
        """Process execution paths into Mermaid diagram lines."""
        lines = []
        
        for node in paths:
            lines.extend(self._process_node(node, processed))
            
        return lines
    
    def _process_node(self, node: ExecutionNode, processed: Set[str]) -> List[str]:
        """Process a single node into Mermaid diagram lines."""
        lines = []
        node_id = f"{node.type.value}_{node.name}"
        
        if node_id not in processed:
            processed.add(node_id)
            
            # Node definition
            label = [f"{node.name}"]
            label.append(f"({node.type.value})")
            
            if self.include_conditions and node.conditions:
                conditions = "<br/>".join(node.conditions)
                label.append(f"Conditions:<br/>{conditions}")
            
            # Add metadata if available
            if node.metadata:
                if self.show_dml and 'dml_operations' in node.metadata:
                    dml_ops = "<br/>".join(node.metadata['dml_operations'])
                    label.append(f"DML:<br/>{dml_ops}")
                if self.show_soql and 'soql_queries' in node.metadata:
                    soql = "<br/>".join(node.metadata['soql_queries'])
                    label.append(f"SOQL:<br/>{soql}")
            
            lines.append(f'{node_id}["{"|".join(label)}"]')
            
            # Process next nodes
            for next_node in node.next_nodes:
                next_id = f"{next_node.type.value}_{next_node.name}"
                lines.append(f"{node_id} --> {next_id}")
                lines.extend(self._process_node(next_node, processed))
                
        return lines
    
    def _generate_styling(self) -> List[str]:
        """Generate Mermaid styling definitions."""
        return [
            "classDef trigger fill:#f96,stroke:#333,stroke-width:2px",
            "classDef flow fill:#9cf,stroke:#333,stroke-width:2px",
            "classDef process_builder fill:#9f9,stroke:#333,stroke-width:2px",
            "classDef workflow fill:#f9f,stroke:#333,stroke-width:2px",
            "classDef apex fill:#ff9,stroke:#333,stroke-width:2px",
            "class trigger_* trigger",
            "class flow_* flow",
            "class process_builder_* process_builder",
            "class workflow_* workflow",
            "class apex_* apex"
        ]

    def save_diagram(self, diagram: str, output_path: Path) -> None:
        """Save the Mermaid diagram to a file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write("```mermaid\n")
            f.write(diagram)
            f.write("\n```")
            
    def generate_html(self, diagram: str) -> str:
        """Generate HTML version of the diagram."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Execution Path Diagram</title>
            <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
            <script>mermaid.initialize({{startOnLoad:true}});</script>
        </head>
        <body>
            <div class="mermaid">
            {diagram}
            </div>
        </body>
        </html>
        """