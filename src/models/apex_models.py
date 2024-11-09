"""Data models for Apex code components."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set
from enum import Enum

class ApexModifier(Enum):
    """Apex access modifiers and other modifiers."""
    PRIVATE = 'private'
    PUBLIC = 'public'
    GLOBAL = 'global'
    PROTECTED = 'protected'
    STATIC = 'static'
    VIRTUAL = 'virtual'
    ABSTRACT = 'abstract'
    OVERRIDE = 'override'
    TESTMETHOD = 'testmethod'
    WITH_SHARING = 'with sharing'
    WITHOUT_SHARING = 'without sharing'
    INHERITED_SHARING = 'inherited sharing'

@dataclass
class ApexAnnotation:
    """Represents an Apex annotation with its parameters."""
    name: str
    parameters: Dict[str, str] = field(default_factory=dict)

@dataclass
class ApexParameter:
    """Represents a parameter in an Apex method."""
    name: str
    type: str
    is_collection: bool = False
    collection_type: Optional[str] = None

@dataclass
class DMLOperation:
    """Represents a DML operation in Apex code."""
    operation: str
    object_type: str
    is_bulk: bool
    line_number: int

@dataclass
class SOQLQuery:
    """Represents a SOQL query in Apex code."""
    query: str
    referenced_objects: List[str]
    line_number: int