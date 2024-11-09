"""
    Enhanced parser for Salesforce Apex code analysis.

    This module provides comprehensive parsing capabilities for Salesforce Apex code,
    extracting detailed information about classes, methods, properties, and their
    relationships. It handles complex Apex features including:

    - Class structure and inheritance
    - Methods and properties
    - Annotations and modifiers
    - DML operations and SOQL queries
    - Documentation comments
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Set, Union
from pathlib import Path
import re
from enum import Enum

class ApexModifier(Enum):
    """
        Salesforce Apex access and behavior modifiers.
        
        Defines all possible modifiers that can be applied to Apex
        classes, methods, and properties.
        
        Access Modifiers:
            PRIVATE: Accessible only within the defining class
            PUBLIC: Accessible within the same namespace
            GLOBAL: Accessible across namespaces
            PROTECTED: Accessible to the defining and child classes
            
        Method Modifiers:
            STATIC: No instance required
            VIRTUAL: Can be overridden
            ABSTRACT: Must be overridden
            OVERRIDE: Overrides parent implementation
            TESTMETHOD: Denotes a test method
            
        Sharing Modifiers:
            WITH_SHARING: Enforces sharing rules
            WITHOUT_SHARING: Bypasses sharing rules
            INHERITED_SHARING: Inherits sharing from caller
    """

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
    """
        Represents a Salesforce Apex annotation.
        
        Captures metadata annotations and their parameters.
        
        Attributes:
            name: Annotation name (e.g., '@TestSetup', '@InvocableMethod')
            parameters: Dictionary of parameter name-value pairs
            
        Example:
            >>> annotation = ApexAnnotation(
            ...     name='InvocableMethod',
            ...     parameters={'label': 'My Method'}
            ... )
    """

    name: str
    parameters: Dict[str, str]

@dataclass
class ApexParameter:
    """
        Represents a parameter in an Apex method.
        
        Captures parameter details including collection type information.
        
        Attributes:
            name: Parameter name
            type: Parameter data type
            is_collection: Whether parameter is a collection
            collection_type: Type of collection if applicable
            
        Example:
            >>> param = ApexParameter(
            ...     name='accounts',
            ...     type='Account',
            ...     is_collection=True,
            ...     collection_type='List'
            ... )
    """

    name: str
    type: str
    is_collection: bool
    collection_type: Optional[str] = None  # List, Set, Map, etc.

@dataclass
class DMLOperation:
    """
        Represents a database operation in Apex code.
        
        Tracks DML operations and their characteristics.
        
        Attributes:
            operation: Type of DML operation
            object_type: Target Salesforce object
            is_bulk: Whether operation handles multiple records
            line_number: Location in source code
            
        Example:
            >>> dml = DMLOperation(
            ...     operation='insert',
            ...     object_type='Account',
            ...     is_bulk=True,
            ...     line_number=42
            ... )
    """

    operation: str  # insert, update, delete, upsert, merge
    object_type: str
    is_bulk: bool
    line_number: int

@dataclass
class SOQLQuery:
    """
        Represents a SOQL query in Apex code.
        
        Tracks queries and their referenced objects.
        
        Attributes:
            query: Complete SOQL query text
            referenced_objects: Objects referenced in query
            line_number: Location in source code
            
        Example:
            >>> query = SOQLQuery(
            ...     query='SELECT Id FROM Account',
            ...     referenced_objects=['Account'],
            ...     line_number=43
            ... )
    """

    query: str
    referenced_objects: List[str]
    line_number: int

@dataclass
class ApexMethod:
    """
        Represents a method in an Apex class.
        
        Captures complete method information including signature,
        body contents, and dependencies.
        
        Attributes:
            name: Method name
            return_type: Return type of method
            parameters: List of method parameters
            modifiers: Access and behavior modifiers
            annotations: Method annotations
            body: Method implementation
            calls: Set of methods called
            dml_operations: Database operations performed
            soql_queries: SOQL queries executed
            line_number: Source code location
            doc_comment: Documentation comment if present
            
        Example:
            >>> method = ApexMethod(
            ...     name='createAccount',
            ...     return_type='Account',
            ...     parameters=[ApexParameter(...)],
            ...     modifiers=[ApexModifier.PUBLIC],
            ...     annotations=[],
            ...     body="// implementation",
            ...     calls={'save', 'validate'},
            ...     dml_operations=[...],
            ...     soql_queries=[...],
            ...     line_number=45,
            ...     doc_comment='/** Creates a new account */'
            ... )
    """

    name: str
    return_type: str
    parameters: List[ApexParameter]
    modifiers: List[ApexModifier]
    annotations: List[ApexAnnotation]
    body: str
    calls: Set[str]
    dml_operations: List[DMLOperation]
    soql_queries: List[SOQLQuery]
    line_number: int
    doc_comment: Optional[str]

@dataclass
class ApexProperty:
    """
        Represents a property in an Apex class.
        
        Captures property definition including access methods.
        
        Attributes:
            name: Property name
            type: Property data type
            modifiers: Access modifiers
            getter: Getter implementation
            setter: Setter implementation
            line_number: Source code location
            
        Example:
            >>> property = ApexProperty(
            ...     name='status',
            ...     type='String',
            ...     modifiers=[ApexModifier.PUBLIC],
            ...     getter='return status;',
            ...     setter='this.status = value;',
            ...     line_number=50
            ... )
    """

    name: str
    type: str
    modifiers: List[ApexModifier]
    getter: Optional[str]
    setter: Optional[str]
    line_number: int

@dataclass
class ApexClass:
    """
        Represents a complete Apex class.
        
        Captures all aspects of an Apex class including its structure,
        methods, properties, and relationships.
        
        Attributes:
            name: Class name
            file_path: Source file location
            modifiers: Class modifiers
            annotations: Class annotations
            methods: Class methods
            properties: Class properties
            superclass: Parent class if any
            interfaces: Implemented interfaces
            inner_classes: Nested class definitions
            doc_comment: Class documentation
            
        Example:
            >>> apex_class = ApexClass(
            ...     name='AccountService',
            ...     file_path='/src/classes/AccountService.cls',
            ...     modifiers=[ApexModifier.PUBLIC],
            ...     annotations=[],
            ...     methods=[...],
            ...     properties=[...],
            ...     superclass=None,
            ...     interfaces=['IService'],
            ...     inner_classes=[],
            ...     doc_comment='/** Service class for Account operations */'
            ... )
    """

    name: str
    file_path: str
    modifiers: List[ApexModifier]
    annotations: List[ApexAnnotation]
    methods: List[ApexMethod]
    properties: List[ApexProperty]
    superclass: Optional[str]
    interfaces: List[str]
    inner_classes: List['ApexClass']
    doc_comment: Optional[str]

class ApexParser:
    """
        Enhanced parser for Apex code that extracts detailed class structure and dependencies.
    """
    
    def __init__(self):
        """
            Initialize parser with regex patterns.
        """
        self._init_patterns()

    def _init_patterns(self):
        """
            Initialize all regex patterns used for parsing.
        """
        # Annotation pattern with parameter support
        self.annotation_pattern = re.compile(
            r'@(?P<name>\w+)(?:\((?P<params>.*?)\))?',
            re.MULTILINE
        )
        # Enhanced method pattern with annotations and modifiers
        self.method_pattern = re.compile(
            r'(?P<annotations>(?:@\w+(?:\(.*?\))?\s+)*)'
            r'(?P<modifiers>(?:(?:private|public|global|protected|static|virtual|abstract|override|testmethod)\s+)*)'
            r'(?P<return_type>[\w\.<>]+(?:\[\])?)\s+'
            r'(?P<name>\w+)\s*'
            r'\((?P<params>.*?)\)'
            r'(?:\s+(?P<throws>throws\s+[\w\s,]+))?\s*'
            r'{(?P<body>(?:[^{}]|{[^{}]*})*)}',
            re.MULTILINE | re.DOTALL
        )
        # Property pattern
        self.property_pattern = re.compile(
            r'(?P<modifiers>(?:(?:private|public|global|protected|static)\s+)*)'
            r'(?P<type>[\w\.<>]+(?:\[\])?)\s+'
            r'(?P<name>\w+)\s*{'
            r'(?P<accessors>(?:[^{}]|{[^{}]*})*)}',
            re.MULTILINE | re.DOTALL
        )
        # Class pattern
        self.class_pattern = re.compile(
            r'(?P<annotations>(?:@\w+(?:\(.*?\))?\s+)*)'
            r'(?P<modifiers>(?:(?:private|public|global|virtual|abstract)\s+)*)'
            r'(?P<sharing>(?:with|without|inherited)\s+sharing\s+)?'
            r'class\s+'
            r'(?P<name>\w+)'
            r'(?:\s+extends\s+(?P<superclass>\w+))?'
            r'(?:\s+implements\s+(?P<interfaces>[\w\s,]+))?'
            r'\s*{(?P<body>(?:[^{}]|{[^{}]*})*)}',
            re.MULTILINE | re.DOTALL
        )
        # SOQL pattern
        self.soql_pattern = re.compile(
            r'\[(?P<query>'
            r'SELECT\s+[\w\s,\.*()]+\s+'
            r'FROM\s+(?P<object>\w+)'
            r'(?:\s+WHERE\s+[^]\n]+)?'
            r'(?:\s+ORDER\s+BY\s+[^]\n]+)?'
            r'(?:\s+LIMIT\s+\d+)?'
            r')\]',
            re.IGNORECASE | re.MULTILINE
        )
        # DML pattern
        self.dml_pattern = re.compile(
            r'(?P<operation>insert|update|delete|upsert|merge)\s+'
            r'(?P<object>[\w\s,]+?);',
            re.MULTILINE
        )
        # Doc comment pattern
        self.doc_comment_pattern = re.compile(
            r'/\*\*(?P<comment>.*?)\*/',
            re.MULTILINE | re.DOTALL
        )
        # Inner class pattern
        self.inner_class_pattern = re.compile(
            r'(?P<access>private|public|global)\s+'
            r'class\s+'
            r'(?P<name>\w+)'
            r'\s*{(?P<body>(?:[^{}]|{[^{}]*})*)}',
            re.MULTILINE | re.DOTALL
        )

    def _parse_annotations(self, annotations_str: str) -> List[ApexAnnotation]:
        """
            Parse annotations and their parameters.
        """
        annotations = []
        if not annotations_str:
            return annotations
        for match in self.annotation_pattern.finditer(annotations_str):
            params = {}
            if match.group('params'):
                param_str = match.group('params')
                if '=' in param_str:
                    # Named parameters
                    param_pairs = param_str.split(',')
                    for pair in param_pairs:
                        key, value = pair.split('=')
                        params[key.strip()] = value.strip().strip('"\'')
                else:
                    # Single unnamed parameter
                    params['value'] = param_str.strip().strip('"\'')
            annotations.append(ApexAnnotation(
                name=match.group('name'),
                parameters=params
            ))
        return annotations

    def _parse_parameters(self, params_str: str) -> List[ApexParameter]:
        """
            Parse method parameters with enhanced type support.
        """
        parameters = []
        if not params_str.strip():
            return parameters
        for param in params_str.split(','):
            param = param.strip()
            if param:
                is_collection = False
                collection_type = None
                param_parts = param.split()
                type_str = ' '.join(param_parts[:-1])
                name = param_parts[-1]
                # Handle collection types
                collection_match = re.match(r'(List|Set|Map)<(.+)>', type_str)
                if collection_match:
                    is_collection = True
                    collection_type = collection_match.group(1)
                    type_str = collection_match.group(2)
                elif type_str.endswith('[]'):
                    is_collection = True
                    collection_type = 'Array'
                    type_str = type_str[:-2]
                
                parameters.append(ApexParameter(
                    name=name,
                    type=type_str,
                    is_collection=is_collection,
                    collection_type=collection_type
                ))
        return parameters

    def _parse_method_body(self, body: str, line_offset: int) -> tuple[Set[str], List[DMLOperation], List[SOQLQuery]]:
        """
            Parse method body for calls, DML operations, and SOQL queries.
        """
        calls = set()
        dml_operations = []
        soql_queries = []
        # Extract method calls
        call_pattern = re.compile(r'(?<!new\s)\b\w+\s*\([^)]*\)')
        for match in call_pattern.finditer(body):
            call = match.group()
            method_name = call[:call.index('(')].strip()
            if method_name not in ('if', 'while', 'for', 'switch'):
                calls.add(method_name)
        # Extract DML operations
        for match in self.dml_pattern.finditer(body):
            line_number = line_offset + body[:match.start()].count('\n')
            dml_operations.append(DMLOperation(
                operation=match.group('operation'),
                object_type=match.group('object').strip(),
                is_bulk=bool(re.search(r'\[\]|\<.+\>', match.group('object'))),
                line_number=line_number
            ))
        # Extract SOQL queries
        for match in self.soql_pattern.finditer(body):
            line_number = line_offset + body[:match.start()].count('\n')
            query = match.group('query')
            referenced_objects = [match.group('object')]
            # Extract related objects
            for relationship in re.finditer(r'FROM\s+(\w+)|JOIN\s+(\w+)', query, re.IGNORECASE):
                obj = relationship.group(1) or relationship.group(2)
                if obj not in referenced_objects:
                    referenced_objects.append(obj)
            soql_queries.append(SOQLQuery(
                query=query,
                referenced_objects=referenced_objects,
                line_number=line_number
            ))
        return calls, dml_operations, soql_queries

    def _parse_property(self, property_match: re.Match) -> ApexProperty:
        """
            Parse an Apex property definition.
        """
        property_dict = property_match.groupdict()
        modifiers = [ApexModifier(mod.strip()) 
                    for mod in property_dict['modifiers'].split()
                    if mod.strip()]
        accessors = property_dict['accessors']
        getter = setter = None
        # Extract getter and setter if present
        getter_match = re.search(r'get\s*{([^}]+)}', accessors)
        if getter_match:
            getter = getter_match.group(1).strip()
        setter_match = re.search(r'set\s*{([^}]+)}', accessors)
        if setter_match:
            setter = setter_match.group(1).strip()
        return ApexProperty(
            name=property_dict['name'],
            type=property_dict['type'],
            modifiers=modifiers,
            getter=getter,
            setter=setter,
            line_number=0  # Would need to calculate actual line number
        )

    def _parse_inner_classes(self, class_body: str) -> List[ApexClass]:
        """
            Parse inner class definitions.
        """
        inner_classes = []
        for match in self.inner_class_pattern.finditer(class_body):
            inner_dict = match.groupdict()
            inner_class = self._parse_class_content(inner_dict['body'], Path(""))
            if inner_class:
                inner_classes.append(inner_class)
        return inner_classes

    def parse_file(self, file_path: Path) -> Optional[ApexClass]:
        """
            Parse an Apex class file and return its structure.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self._parse_class_content(content, file_path)
        except Exception as e:
            print(f"Error parsing {file_path}: {str(e)}")
            return None

    def _parse_class_content(self, content: str, file_path: Path) -> Optional[ApexClass]:
        """
            Parse the content of an Apex class.
        """
        class_match = self.class_pattern.search(content)
        if not class_match:
            return None
        class_dict = class_match.groupdict()
        # Parse modifiers including sharing
        modifiers = [ApexModifier(mod.strip()) 
                    for mod in class_dict['modifiers'].split()
                    if mod.strip()]
        if class_dict['sharing']:
            sharing_mod = ApexModifier(class_dict['sharing'].strip())
            modifiers.append(sharing_mod)
        # Parse interfaces
        interfaces = []
        if class_dict['interfaces']:
            interfaces = [i.strip() for i in class_dict['interfaces'].split(',')]
        # Parse annotations
        annotations = self._parse_annotations(class_dict['annotations'] or '')
        # Parse doc comment
        doc_comment = None
        doc_match = self.doc_comment_pattern.search(content[:class_match.start()])
        if doc_match:
            doc_comment = doc_match.group('comment').strip()
        # Parse components
        methods = self._parse_methods(class_dict['body'])
        properties = self._parse_properties(class_dict['body'])
        inner_classes = self._parse_inner_classes(class_dict['body'])
        return ApexClass(
            name=class_dict['name'],
            file_path=str(file_path),
            modifiers=modifiers,
            annotations=annotations,
            methods=methods,
            properties=properties,
            superclass=class_dict['superclass'],
            interfaces=interfaces,
            inner_classes=inner_classes,
            doc_comment=doc_comment
        )

    def _parse_methods(self, class_body: str) -> List[ApexMethod]:
        """
            Extract methods from class body.
        """
        methods = []
        for match in self.method_pattern.finditer(class_body):
            method_dict = match.groupdict()
            # Parse annotations
            annotations = self._parse_annotations(method_dict['annotations'] or '')
            # Parse modifiers
            modifiers = [ApexModifier(mod.strip()) 
                        for mod in method_dict['modifiers'].split()
                        if mod.strip()]
            # Parse parameters
            parameters = self._parse_parameters(method_dict['params'])
            # Calculate line number
            line_number = class_body[:match.start()].count('\n') + 1
            # Parse method body
            calls, dml_operations, soql_queries = self._parse_method_body(
                method_dict['body'],
                line_number
            )
            # Parse doc comment
            doc_comment = None
            doc_match = self.doc_comment_pattern.search(class_body[:match.start()])
            if doc_match:
                doc_comment = doc_match.group('comment').strip()
            methods.append(ApexMethod(
                name=method_dict['name'],
                return_type=method_dict['return_type'],
                parameters=parameters,
                modifiers=modifiers,
                annotations=annotations,
                body=method_dict['body'],
                calls=calls,
                dml_operations=dml_operations,
                soql_queries=soql_queries,
                line_number=line_number,
                doc_comment=doc_comment
            ))
        return methods

    def _parse_properties(self, class_body: str) -> List[ApexProperty]:
        """
            Extract properties from class body.
        """
        properties = []
        for match in self.property_pattern.finditer(class_body):
            properties.append(self._parse_property(match))
        return properties