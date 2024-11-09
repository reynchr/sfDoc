"""
    Analyzer for Apex code dependencies and execution paths.

    This module analyzes Salesforce Apex code to understand dependencies,
    execution paths, and potential issues. It focuses on identifying trigger
    execution paths, recursion risks, and automation entry points.
"""

from dataclasses import dataclass
from typing import List, Dict, Set, Optional
from pathlib import Path
from .parser import ApexParser, ApexClass, ApexMethod
import re

@dataclass
class TriggerContext:
    """
        Represents a Salesforce trigger execution context.
        
        Attributes:
            object_name: Name of the Salesforce object (e.g., 'Account')
            context: Trigger timing and operation (e.g., 'before insert')
            trigger_name: Name of the trigger being executed
            
        Example:
            >>> context = TriggerContext(
            ...     object_name='Account',
            ...     context='before insert',
            ...     trigger_name='AccountTrigger'
            ... )
    """
    object_name: str
    context: str  # before/after insert/update/delete/undelete
    trigger_name: str

@dataclass
class ExecutionNode:
    """
        Represents a node in the automation execution path.
        
        Attributes:
            component_type: Type of automation component
            name: Name of the component
            method: Optional method name for class components
            next_nodes: List of nodes executed after this one
            conditions: Optional execution conditions
            order: Execution order in the path
            
        Example:
            >>> node = ExecutionNode(
            ...     component_type='trigger',
            ...     name='AccountTrigger',
            ...     method=None,
            ...     next_nodes=[],
            ...     conditions=None,
            ...     order=0
            ... )
    """
    component_type: str  # 'trigger', 'class', 'flow', 'process_builder', 'workflow'
    name: str
    method: Optional[str]
    next_nodes: List['ExecutionNode']
    conditions: Optional[str]
    order: int

class ApexAnalyzer:
    """
        Analyzer for Apex code that builds execution paths and identifies dependencies.
        
        Analyzes Apex classes and triggers to:
        1. Map execution paths through trigger contexts
        2. Identify potential recursion risks
        3. Document automation entry points
        
        Attributes:
            parser: Parser for Apex code files
            classes: Dictionary of parsed Apex classes
            triggers: Dictionary of parsed triggers
            execution_paths: Mapped execution paths by context
            
        Example:
            >>> analyzer = ApexAnalyzer()
            >>> analyzer.load_source(Path('./force-app/main/default'))
            >>> paths = analyzer.build_execution_path(trigger_context)
    """
    
    def __init__(self):
        """
            Initialize the Apex analyzer.
        """
        self.parser = ApexParser()
        self.classes: Dict[str, ApexClass] = {}
        self.triggers: Dict[str, Dict] = {}
        self.execution_paths: Dict[str, List[ExecutionNode]] = {}
        
    def load_source(self, source_path: Path):
        """
            Load all Apex classes and triggers from the source directory.
            
            Args:
                source_path: Path to the directory containing Apex files
                
            Example:
                >>> analyzer.load_source(Path('./force-app/main/default'))
        """
        # Load classes
        for class_file in source_path.rglob('*.cls'):
            apex_class = self.parser.parse_file(class_file)
            if apex_class:
                self.classes[apex_class.name] = apex_class
                
        # Load triggers
        for trigger_file in source_path.rglob('*.trigger'):
            self._parse_trigger(trigger_file)

    def _parse_trigger(self, trigger_file: Path):
        """
            Parse a trigger file to extract its metadata.
            
            Args:
                trigger_file: Path to the trigger file
                
            Note:
                Extracts:
                - Trigger name
                - Object context
                - Execution contexts
                - Full content for analysis
        """
        try:
            with open(trigger_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract trigger name and contexts
            trigger_pattern = re.compile(
                r'trigger\s+(?P<name>\w+)\s+on\s+(?P<object>\w+)\s*\('
                r'(?P<contexts>[^)]+)\)',
                re.MULTILINE
            )
            
            match = trigger_pattern.search(content)
            if match:
                trigger_dict = match.groupdict()
                contexts = [ctx.strip() for ctx in trigger_dict['contexts'].split(',')]
                
                self.triggers[trigger_dict['name']] = {
                    'object': trigger_dict['object'],
                    'contexts': contexts,
                    'content': content
                }
        except Exception as e:
            print(f"Error parsing trigger {trigger_file}: {str(e)}")

    def build_execution_path(self, trigger_context: TriggerContext) -> List[ExecutionNode]:
        """
            Build the execution path for a given trigger context.
            
            Maps out the complete execution path starting from a trigger,
            following through to all called classes and methods.
            
            Args:
                trigger_context: Context for which to build the path
                
            Returns:
                List[ExecutionNode]: Complete execution path
                
            Example:
                >>> context = TriggerContext('Account', 'before insert', 'AccountTrigger')
                >>> path = analyzer.build_execution_path(context)
        """
        path = []
        visited = set()
        
        def build_path(component: str, comp_type: str, method: Optional[str] = None, 
                      conditions: Optional[str] = None, order: int = 0):
            """Recursively build execution path for a component."""
            if component in visited:
                return None  # Prevent infinite recursion
                
            visited.add(component)
            node = ExecutionNode(
                component_type=comp_type,
                name=component,
                method=method,
                next_nodes=[],
                conditions=conditions,
                order=order
            )
            
            # If it's a class, analyze its method calls
            if comp_type == 'class' and component in self.classes:
                apex_class = self.classes[component]
                for apex_method in apex_class.methods:
                    for call in apex_method.calls:
                        # Check if the call is to another class we know about
                        if call in self.classes:
                            next_node = build_path(call, 'class', None, None, order + 1)
                            if next_node:
                                node.next_nodes.append(next_node)
            
            return node
        # Start with the trigger
        if trigger_context.trigger_name in self.triggers:
            trigger_data = self.triggers[trigger_context.trigger_name]
            trigger_node = ExecutionNode(
                component_type='trigger',
                name=trigger_context.trigger_name,
                method=None,
                next_nodes=[],
                conditions=None,
                order=0
            )
            path.append(trigger_node)
            
            # Analyze the trigger body for class calls
            for class_name in self.classes:
                if class_name in trigger_data['content']:
                    class_node = build_path(class_name, 'class', None, None, 1)
                    if class_node:
                        trigger_node.next_nodes.append(class_node)
        
        self.execution_paths[f"{trigger_context.object_name}_{trigger_context.context}"] = path
        return path

    def analyze_recursion_risks(self) -> Dict[str, List[str]]:
        """Identify potential recursion risks in the codebase."""
        risks = {}
        
        for trigger_name, trigger_data in self.triggers.items():
            object_name = trigger_data['object']
            
            # Look for patterns that might cause recursion
            for class_name, apex_class in self.classes.items():
                for method in apex_class.methods:
                    # Look for DML operations on the same object
                    if (f"insert {object_name}" in method.body or
                        f"update {object_name}" in method.body or
                        f"delete {object_name}" in method.body):
                        
                        if trigger_name not in risks:
                            risks[trigger_name] = []
                        risks[trigger_name].append(
                            f"Potential recursion in {class_name}.{method.name}: "
                            f"DML operation on {object_name}"
                        )
        
        return risks

    def get_entry_points(self) -> Dict[str, List[str]]:
        """Identify all automation entry points for each object."""
        entry_points = {}
        
        # Analyze triggers
        for trigger_name, trigger_data in self.triggers.items():
            object_name = trigger_data['object']
            if object_name not in entry_points:
                entry_points[object_name] = []
            
            entry_points[object_name].append(
                f"Trigger: {trigger_name} ({', '.join(trigger_data['contexts'])})"
            )
        
        return entry_points