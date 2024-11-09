"""
    Data models for Apex code components.

    This module defines the core data structures for representing Apex code elements,
    including modifiers, annotations, parameters, DML operations, and SOQL queries.
    These models support detailed static analysis of Apex code.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set
from enum import Enum

class ApexModifier(Enum):
    """
        Apex access modifiers and other modifiers.
        
        Enumerates all possible Apex code modifiers including:
            - Access levels (private, public, global, protected)
            - Method modifiers (static, virtual, abstract)
            - Class modifiers (with sharing, without sharing)
            - Special modifiers (override, testmethod)
        
        Example:
            >>> method_modifier = ApexModifier.STATIC
            >>> print(method_modifier.value)
            'static'
            
        Notes:
            - Sharing modifiers only apply to classes
            - testmethod is equivalent to @isTest annotation
            - Some modifiers are mutually exclusive (e.g., abstract and override)
    """
    PRIVATE = 'private'                     # Accessible only within the same class
    PUBLIC = 'public'                       # Accessible within the same namespace
    GLOBAL = 'global'                       # Accessible across namespaces
    PROTECTED = 'protected'                 # Accessible by parent and child classes
    STATIC = 'static'                       # No instance required
    VIRTUAL = 'virtual'                     # Can be overridden
    ABSTRACT = 'abstract'                   # Must be overridden
    OVERRIDE = 'override'                   # Overrides parent method
    TESTMETHOD = 'testmethod'               # Test method indicator
    WITH_SHARING = 'with sharing'           # Enforces sharing rules
    WITHOUT_SHARING = 'without sharing'     # Bypasses sharing rules
    INHERITED_SHARING = 'inherited sharing' # Inherits sharing from caller

@dataclass
class ApexAnnotation:
    """
        Represents an Apex annotation with its parameters.
        
        Captures metadata about Apex code elements through annotations
        and their associated parameters.
        
        Attributes:
            name: Name of the annotation (e.g., 'InvocableMethod')
            parameters: Dictionary of parameter name-value pairs
            
        Example:
            >>> annotation = ApexAnnotation(
            ...     name='InvocableMethod',
            ...     parameters={'label': 'My Method', 'description': 'Does something'}
            ... )
    """
    name: str
    parameters: Dict[str, str] = field(default_factory=dict)

@dataclass
class ApexParameter:
    """
        Represents a parameter in an Apex method.
        
        Models method parameters including their type information and
        collection status.
        
        Attributes:
            name: Parameter name
            type: Apex data type
            is_collection: Whether parameter is a collection type
            collection_type: Type of collection if applicable
            
        Example:
            >>> param = ApexParameter(
            ...     name='accounts',
            ...     type='Account',
            ...     is_collection=True,
            ...     collection_type='List'
            ... )
            
        Notes:
            - collection_type can be: List, Set, Map
            - type for Map should be the value type (key is determined by Map type)
    """
    name: str
    type: str
    is_collection: bool = False
    collection_type: Optional[str] = None

@dataclass
class DMLOperation:
    """
        Represents a DML operation in Apex code.
        
        Tracks database operations including the operation type,
        affected object, and location in code.
        
        Attributes:
            operation: DML operation type (insert, update, delete, upsert, merge)
            object_type: Salesforce object being operated on
            is_bulk: Whether operation is bulk (list/array) or single record
            line_number: Source code line number of the operation
            
        Example:
            >>> dml = DMLOperation(
            ...     operation='insert',
            ...     object_type='Account',
            ...     is_bulk=True,
            ...     line_number=42
            ... )
            
        Notes:
            - Bulk operations should be preferred for better performance
            - Line numbers are useful for error reporting and optimization suggestions
    """
    operation: str
    object_type: str
    is_bulk: bool
    line_number: int

@dataclass
class SOQLQuery:
    """
        Represents a SOQL query in Apex code.
        
        Models SOQL queries including the query text and objects referenced.
        
        Attributes:
            query: Complete SOQL query text
            referenced_objects: List of Salesforce objects referenced in query
            line_number: Source code line number of the query
            
        Example:
            >>> query = SOQLQuery(
            ...     query='SELECT Id, Name FROM Account WHERE Type = :accType',
            ...     referenced_objects=['Account'],
            ...     line_number=57
            ... )
            
        Notes:
            - referenced_objects includes both main and related objects
            - Line numbers help with performance optimization
            - Consider SOQL limits when analyzing queries
    """
    query: str
    referenced_objects: List[str]
    line_number: int

    def is_selective(self) -> bool:
        """
            Check if the query uses selective filters.
            
            Returns:
                bool: True if query includes selective filters
                
            Example:
                >>> if not query.is_selective():
                ...     print("Warning: Query may cause performance issues")
        """
        # Implement selective filter checking logic
        return True

    def get_query_type(self) -> str:
        """
            Determine the type of SOQL query.
            
            Returns:
                str: Query type (aggregate, relationship, simple)
                
            Example:
                >>> query_type = query.get_query_type()
                >>> if query_type == 'aggregate':
                ...     print("Query performs aggregation")
        """
        if 'COUNT()' in self.query or 'SUM(' in self.query:
            return 'aggregate'
        elif '.' in self.query:
            return 'relationship'
        return 'simple'

    def has_bind_variables(self) -> bool:
        """
            Check if query uses bind variables.
            
            Returns:
                bool: True if query contains bind variables
                
            Example:
                >>> if query.has_bind_variables():
                ...     print("Query uses bind variables for safe value injection")
        """
        return ':' in self.query