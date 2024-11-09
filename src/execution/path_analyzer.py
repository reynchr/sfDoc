# src/execution/path_analyzer.py
"""Analyzer for execution paths in Salesforce automations."""

from typing import Dict, List, Set, Optional
import logging
from pathlib import Path
import networkx as nx

from ..models.analysis_models import (
    ExecutionNode, 
    AnalysisResult, 
    AutomationType, 
    TriggerContext
)
from ..models.apex_models import DMLOperation, SOQLQuery

logger = logging.getLogger(__name__)

class ExecutionPathAnalyzer:
    """Analyzes execution paths across different types of Salesforce automations."""

    def __init__(self, config: Dict):
        self.config = config
        self.max_depth = config['execution']['max_depth']
        self.graph = nx.DiGraph()
        self.visited = set()
        
    def analyze_object(self, object_name: str, metadata: Dict) -> AnalysisResult:
        """Analyze all automation paths for a given object."""
        entry_points = []
        execution_paths = {}
        recursion_risks = []
        
        # Reset tracking for new analysis
        self.graph.clear()
        self.visited.clear()
        
        # Analyze each trigger context
        for context in TriggerContext:
            paths = self._analyze_trigger_context(object_name, context, metadata)
            if paths:
                execution_paths[context] = paths
                
                # Add entry points
                for path in paths:
                    if path not in entry_points:
                        entry_points.append(path)
                        
                # Check for recursion risks
                risks = self._check_recursion_risks(paths)
                recursion_risks.extend(risks)
        
        return AnalysisResult(
            object_name=object_name,
            entry_points=entry_points,
            execution_paths=execution_paths,
            recursion_risks=recursion_risks,
            metadata=metadata
        )
    
    def _analyze_trigger_context(
        self, 
        object_name: str, 
        context: TriggerContext,
        metadata: Dict
    ) -> List[ExecutionNode]:
        """Analyze execution path for a specific trigger context."""
        paths = []
        
        # Find triggers for this context
        triggers = self._find_triggers(object_name, context, metadata)
        for trigger in triggers:
            path = self._build_execution_path(trigger, metadata, depth=0)
            if path:
                paths.append(path)
                
        return paths
    
    def _build_execution_path(
        self, 
        node: ExecutionNode, 
        metadata: Dict, 
        depth: int
    ) -> Optional[ExecutionNode]:
        """Recursively build execution path starting from a node."""
        if depth >= self.max_depth or node.name in self.visited:
            return None
            
        self.visited.add(node.name)
        
        # Add node to graph
        self.graph.add_node(
            node.name, 
            type=node.type.value,
            object=node.object_name,
            context=node.context.value if node.context else None
        )
        
        # Find next nodes based on type
        next_nodes = []
        if node.type == AutomationType.TRIGGER:
            next_nodes = self._find_trigger_calls(node, metadata)
        elif node.type == AutomationType.PROCESS_BUILDER:
            next_nodes = self._find_process_builder_actions(node, metadata)
        elif node.type == AutomationType.FLOW:
            next_nodes = self._find_flow_elements(node, metadata)
            
        # Recursively process next nodes
        for next_node in next_nodes:
            processed_node = self._build_execution_path(next_node, metadata, depth + 1)
            if processed_node:
                node.next_nodes.append(processed_node)
                self.graph.add_edge(node.name, processed_node.name)
                
        return node
    
    def _check_recursion_risks(self, paths: List[ExecutionNode]) -> List[str]:
        """Identify potential recursion risks in execution paths."""
        risks = []
        cycles = list(nx.simple_cycles(self.graph))
        
        for cycle in cycles:
            risk = f"Potential recursion cycle detected: {' -> '.join(cycle)}"
            risks.append(risk)
            logger.warning(risk)
            
        return risks

# src/execution/visualizer.py
"""Visualization tools for execution paths."""

from typing import Dict, List, Optional
from pathlib import Path
import networkx as nx

from ..models.analysis_models import ExecutionNode, AnalysisResult, TriggerContext

class ExecutionPathVisualizer:
    """Generates visualizations of execution paths."""

    def __init__(self, config: Dict):
        self.config = config
        self.include_conditions = config['visualization']['include_conditions']
        self.show_dml = config['visualization']['show_dml_operations']
        self.show_soql = config['visualization']['show_soql_queries']
        
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
            label = f"{node.name}<br/>{node.type.value}"
            if self.include_conditions and node.conditions:
                label += f"<br/>Conditions: {', '.join(node.conditions)}"
                
            lines.append(f'{node_id}["{label}"]')
            
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
            "class trigger_* trigger",
            "class flow_* flow",
            "class process_builder_* process_builder",
            "class workflow_* workflow"
        ]