"""
    Data models for analysis results.

    This module defines the core data structures used to represent Salesforce
    automation analysis results, including execution paths, trigger contexts,
    and automation types. It uses dataclasses for efficient data handling
    and type safety.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class AutomationType(Enum):
    """
        Types of Salesforce automations.
        
        Enumerates all possible automation types that can be analyzed:
            - TRIGGER: Apex triggers
            - WORKFLOW: Workflow rules
            - PROCESS_BUILDER: Process Builder flows
            - FLOW: Lightning flows
            - VALIDATION_RULE: Validation rules
            - APEX: Apex class methods
        
        Example:
            >>> node_type = AutomationType.TRIGGER
            >>> print(node_type.value)
            'trigger'
    """
    TRIGGER = 'trigger'
    WORKFLOW = 'workflow'
    PROCESS_BUILDER = 'process_builder'
    FLOW = 'flow'
    VALIDATION_RULE = 'validation_rule'
    APEX = 'apex'

class TriggerContext(Enum):
    """
        Salesforce trigger contexts.
        
        Defines all possible trigger execution contexts:
            - BEFORE_INSERT: Before record creation
            - AFTER_INSERT: After record creation
            - BEFORE_UPDATE: Before record update
            - AFTER_UPDATE: After record update
            - BEFORE_DELETE: Before record deletion
            - AFTER_DELETE: After record deletion
            - AFTER_UNDELETE: After record restoration
        
        Example:
            >>> context = TriggerContext.BEFORE_INSERT
            >>> print(context.value)
            'before insert'
    """
    BEFORE_INSERT = 'before insert'
    AFTER_INSERT = 'after insert'
    BEFORE_UPDATE = 'before update'
    AFTER_UPDATE = 'after update'
    BEFORE_DELETE = 'before delete'
    AFTER_DELETE = 'after delete'
    AFTER_UNDELETE = 'after undelete'

@dataclass
class ExecutionNode:
    """
        Represents a node in the execution path.
        
        A node represents a single automation component (trigger, flow, etc.)
        in the execution path, including its type, conditions, and connections
        to other nodes.

        Attributes:
            type: The type of automation (trigger, flow, etc.)
            name: Name of the automation component
            object_name: Salesforce object the automation operates on
            context: Trigger context (if applicable)
            conditions: List of conditions that must be met for execution
            next_nodes: List of nodes that execute after this one
            metadata: Additional metadata about the node

        Example:
            >>> node = ExecutionNode(
            ...     type=AutomationType.TRIGGER,
            ...     name="AccountTrigger",
            ...     object_name="Account",
            ...     context=TriggerContext.BEFORE_INSERT
            ... )
    """
    type: AutomationType
    name: str
    object_name: str
    context: Optional[TriggerContext] = None
    conditions: List[str] = field(default_factory=list)
    next_nodes: List['ExecutionNode'] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

@dataclass
class AnalysisResult:
    """
        Contains the complete analysis results for an object.

        Stores all analysis findings for a Salesforce object, including
        entry points, execution paths, and potential issues.

        Attributes:
            object_name: Name of the analyzed Salesforce object
            entry_points: List of initial automation entry points
            execution_paths: Mapping of trigger contexts to their execution paths
            recursion_risks: List of identified potential recursion issues
            metadata: Additional analysis metadata

        Example:
            >>> result = AnalysisResult(
            ...     object_name="Account",
            ...     entry_points=[trigger_node],
            ...     execution_paths={
            ...         TriggerContext.BEFORE_INSERT: [trigger_node, flow_node]
            ...     },
            ...     recursion_risks=["Potential recursion in AccountTrigger->FlowA"]
            ... )

        Analysis Structure:
            - Each execution path starts with an entry point (trigger, flow, etc.)
            - Paths are organized by trigger context when applicable
            - Recursion risks identify potential infinite loops
            - Metadata can include performance insights, complexity metrics, etc.
    """
    object_name: str
    entry_points: List[ExecutionNode] = field(default_factory=list)
    execution_paths: Dict[TriggerContext, List[ExecutionNode]] = field(default_factory=dict)
    recursion_risks: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def get_path_by_context(self, context: TriggerContext) -> List[ExecutionNode]:
        """
            Get execution path for a specific trigger context.

            Args:
                context: The trigger context to retrieve paths for

            Returns:
                List[ExecutionNode]: List of nodes in the execution path

            Example:
                >>> before_insert_path = result.get_path_by_context(
                ...     TriggerContext.BEFORE_INSERT
                ... )
        """
        return self.execution_paths.get(context, [])

    def has_recursion_risks(self) -> bool:
        """
            Check if any recursion risks were identified.

            Returns:
                bool: True if recursion risks exist

            Example:
                >>> if result.has_recursion_risks():
                ...     print("Warning: Recursion risks found!")
        """
        return len(self.recursion_risks) > 0

    def get_automation_count(self) -> Dict[AutomationType, int]:
        """
            Count automations by type.

            Returns:
                Dict[AutomationType, int]: Count of each automation type

            Example:
                >>> counts = result.get_automation_count()
                >>> print(f"Found {counts[AutomationType.TRIGGER]} triggers")
        """
        counts = {automation_type: 0 for automation_type in AutomationType}
        for node in self.entry_points:
            counts[node.type] += 1
        return counts