"""Data models for analysis results."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class AutomationType(Enum):
    """Types of Salesforce automations."""
    TRIGGER = 'trigger'
    WORKFLOW = 'workflow'
    PROCESS_BUILDER = 'process_builder'
    FLOW = 'flow'
    VALIDATION_RULE = 'validation_rule'
    APEX = 'apex'

class TriggerContext(Enum):
    """Salesforce trigger contexts."""
    BEFORE_INSERT = 'before insert'
    AFTER_INSERT = 'after insert'
    BEFORE_UPDATE = 'before update'
    AFTER_UPDATE = 'after update'
    BEFORE_DELETE = 'before delete'
    AFTER_DELETE = 'after delete'
    AFTER_UNDELETE = 'after undelete'

@dataclass
class ExecutionNode:
    """Represents a node in the execution path."""
    type: AutomationType
    name: str
    object_name: str
    context: Optional[TriggerContext] = None
    conditions: List[str] = field(default_factory=list)
    next_nodes: List['ExecutionNode'] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

@dataclass
class AnalysisResult:
    """Contains the complete analysis results for an object."""
    object_name: str
    entry_points: List[ExecutionNode] = field(default_factory=list)
    execution_paths: Dict[TriggerContext, List[ExecutionNode]] = field(default_factory=dict)
    recursion_risks: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)