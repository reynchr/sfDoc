# src/llm/documenter.py
"""LLM-powered documentation generation for Salesforce automations."""

from typing import Dict, List, Optional
from pathlib import Path
import logging
from dataclasses import dataclass
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from ..models.analysis_models import AnalysisResult, ExecutionNode

logger = logging.getLogger(__name__)

@dataclass
class DocumentationRequest:
    """Structure for documentation generation requests."""
    context: str
    technical_details: Dict
    business_impact: Optional[str] = None
    existing_documentation: Optional[str] = None

@dataclass
class DocumentationResult:
    """Structure for generated documentation."""
    overview: str
    technical_details: str
    business_impact: str
    recommendations: List[str]
    raw_llm_response: Optional[str] = None

class LLMDocumenter:
    """Generates documentation using local LLMs."""

    def __init__(self, config: Dict):
        self.config = config
        self.model_name = config['llm']['model']
        self.temperature = config['llm']['temperature']
        self.max_length = config['llm']['max_length']
        self.prompt_template = config['llm']['prompt_template']
        
        # Initialize model and tokenizer
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize the LLM model and tokenizer."""
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
            
    def generate_documentation(self, analysis_result: AnalysisResult) -> DocumentationResult:
        """Generate comprehensive documentation for analysis results."""
        # Prepare the documentation request
        request = self._prepare_documentation_request(analysis_result)
        
        # Generate the documentation
        try:
            response = self._generate_llm_response(request)
            result = self._process_llm_response(response)
            return result
        except Exception as e:
            logger.error(f"Error generating documentation: {str(e)}")
            return self._generate_fallback_documentation(analysis_result)
            
    def _prepare_documentation_request(self, analysis_result: AnalysisResult) -> DocumentationRequest:
        """Prepare the documentation request from analysis results."""
        # Collect technical details
        technical_details = {
            "object": analysis_result.object_name,
            "entry_points": len(analysis_result.entry_points),
            "automation_count": self._count_automations(analysis_result),
            "recursion_risks": analysis_result.recursion_risks
        }
        
        # Build context string
        context = self._build_context_string(analysis_result)
        
        return DocumentationRequest(
            context=context,
            technical_details=technical_details
        )
        
    def _generate_llm_response(self, request: DocumentationRequest) -> str:
        """Generate documentation using the LLM."""
        # Prepare the prompt
        prompt = self.prompt_template.format(
            context=request.context,
            technical_details=request.technical_details
        )
        
        # Generate response
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_length=self.max_length,
            temperature=self.temperature,
            num_return_sequences=1
        )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
    def _process_llm_response(self, response: str) -> DocumentationResult:
        """Process the LLM response into structured documentation."""
        # Split response into sections
        sections = self._split_response_sections(response)
        
        return DocumentationResult(
            overview=sections.get('overview', ''),
            technical_details=sections.get('technical_details', ''),
            business_impact=sections.get('business_impact', ''),
            recommendations=sections.get('recommendations', []),
            raw_llm_response=response
        )
        
    def _generate_fallback_documentation(self, analysis_result: AnalysisResult) -> DocumentationResult:
        """Generate basic documentation when LLM fails."""
        return DocumentationResult(
            overview=f"Analysis of {analysis_result.object_name}",
            technical_details=f"Found {len(analysis_result.entry_points)} entry points",
            business_impact="Unable to determine business impact",
            recommendations=["Review automation manually"],
            raw_llm_response=None
        )