"""
    Visualization tools for execution paths.

    This module provides tools for generating visual representations of Salesforce
    automation execution paths using Mermaid diagrams. It supports both standalone
    diagrams and HTML-embedded visualizations with customizable styling and detail
    levels.
"""

from typing import Dict, List, Optional, Set
from pathlib import Path
from src.models.analysis_models import ExecutionNode, AnalysisResult, TriggerContext, AutomationType

class ExecutionPathVisualizer:
    """
        Generates visualizations of execution paths.
        
        Creates Mermaid diagrams representing automation execution paths,
        with configurable detail levels and styling options.
        
        Args:
            config: Configuration dictionary containing visualization settings
            
        Configuration Options:
            visualization:
                include_conditions: Include condition details in nodes
                show_dml_operations: Show DML operations in nodes
                show_soql_queries: Show SOQL queries in nodes
                
        Example:
            >>> visualizer = ExecutionPathVisualizer(config)
            >>> diagram = visualizer.generate_mermaid(analysis_result)
    """

    def __init__(self, config: Dict):
        """
            Initialize the visualizer with configuration.
            
            Args:
                config: Configuration dictionary with visualization settings
        """
        self.config = config
        self.include_conditions = config['visualization']['include_conditions']
        self.show_dml = config.get('visualization', {}).get('show_dml_operations', True)
        self.show_soql = config.get('visualization', {}).get('show_soql_queries', True)
        
    def generate_mermaid(self, analysis_result: AnalysisResult, context: Optional[TriggerContext] = None) -> str:
        """
            Generate Mermaid diagram for execution paths.
            
            Creates a Mermaid-formatted diagram showing automation execution paths.
            Can focus on a specific trigger context or show all contexts.
            
            Args:
                analysis_result: Analysis results to visualize
                context: Optional specific trigger context to visualize
                
            Returns:
                str: Mermaid diagram definition
                
            Example:
                >>> diagram = visualizer.generate_mermaid(
                ...     analysis_result,
                ...     context=TriggerContext.BEFORE_INSERT
                ... )
        """
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
        """
            Process execution paths into Mermaid diagram lines.
            
            Args:
                paths: List of execution paths to process
                processed: Set of already processed node IDs
                
            Returns:
                List[str]: Mermaid diagram lines for paths
        """
        lines = []
        for node in paths:
            lines.extend(self._process_node(node, processed))
        return lines
    
    def _process_node(self, node: ExecutionNode, processed: Set[str]) -> List[str]:
        """
            Process a single node into Mermaid diagram lines.
            
            Creates the node definition and connections in Mermaid format,
            including all configured details and metadata.
            
            Args:
                node: Node to process
                processed: Set of already processed node IDs
                
            Returns:
                List[str]: Mermaid diagram lines for node
        """
        lines = []
        node_id = f"{node.type.value}_{node.name}"
        if node_id not in processed:
            processed.add(node_id)
            # Node definition with hierarchical information
            label = [f"{node.name}"]
            label.append(f"({node.type.value})")
            # Add conditions if configured
            if self.include_conditions and node.conditions:
                conditions = "<br/>".join(node.conditions)
                label.append(f"Conditions:<br/>{conditions}")
            # Add metadata details if available
            if node.metadata:
                if self.show_dml and 'dml_operations' in node.metadata:
                    dml_ops = "<br/>".join(node.metadata['dml_operations'])
                    label.append(f"DML:<br/>{dml_ops}")
                if self.show_soql and 'soql_queries' in node.metadata:
                    soql = "<br/>".join(node.metadata['soql_queries'])
                    label.append(f"SOQL:<br/>{soql}")
            # Create node definition
            lines.append(f'{node_id}["{"|".join(label)}"]')
            # Add connections to next nodes
            for next_node in node.next_nodes:
                next_id = f"{next_node.type.value}_{next_node.name}"
                lines.append(f"{node_id} --> {next_id}")
                lines.extend(self._process_node(next_node, processed))
        return lines
    
    def _generate_styling(self) -> List[str]:
        """
            Generate Mermaid styling definitions.
            
            Returns:
                List[str]: Mermaid class definitions for node styling
                
            Note:
                Colors are chosen for optimal contrast and readability:
                - Triggers: Orange (#f96)
                - Flows: Blue (#9cf)
                - Process Builder: Green (#9f9)
                - Workflow: Purple (#f9f)
                - Apex: Yellow (#ff9)
        """
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
        """
            Save the Mermaid diagram to a file.
            
            Saves the diagram with proper Markdown fencing for rendering.
            
            Args:
                diagram: Mermaid diagram content
                output_path: Path where to save the diagram
                
            Example:
                >>> visualizer.save_diagram(diagram, Path('diagrams/account_flow.md'))
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write("```mermaid\n")
            f.write(diagram)
            f.write("\n```")
            
    def generate_html(self, diagram: str) -> str:
        """
            Generate HTML version of the diagram.
            
            Creates a self-contained HTML page with the diagram and Mermaid renderer.
            
            Args:
                diagram: Mermaid diagram content
                
            Returns:
                str: Complete HTML document with embedded diagram
                
            Example:
                >>> html = visualizer.generate_html(diagram)
                >>> with open('diagram.html', 'w') as f:
                ...     f.write(html)
        """
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