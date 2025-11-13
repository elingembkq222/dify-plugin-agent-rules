"""
Generate Rule from Query Tool

This tool generates a rule from natural language query using LLM.
"""

import json
import os
from typing import Any, Dict

from dify_plugin import Tool

from provider.llm_query_parser import parse_query_to_ruleset


class GenerateRuleFromQuery(Tool):
    """
    Generate Rule from Query Tool
    """
    
    def run(self, query: str, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """
        Generate a rule from natural language query using LLM.
        
        Args:
            query: Natural language query
            context: Context data structure
            **kwargs: Additional keyword arguments
            
        Returns:
            Generated rule
        """
        try:
            # Parse context if it's a string
            if isinstance(context, str):
                context = json.loads(context)
            
            # Default context if not provided
            if context is None:
                context = {}
            
            # Get LLM invoker from session
            llm_invoker = self.session.model_invoker
            
            # Get LLM model from environment variable
            llm_model = os.environ.get("LLM_MODEL", "gpt-4o")
            
            # Parse query to rule set
            rule = parse_query_to_ruleset(query, context, llm_invoker=llm_invoker, llm_model=llm_model)
            
            return {
                "success": True,
                "error": None,
                "result": {
                    "query": query,
                    "rule": rule
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "result": None
            }
    
    def get_runtime_parameters(self) -> Dict[str, Any]:
        """
        Get runtime parameters for the tool.
        
        Returns:
            Runtime parameters
        """
        return {
            "query": {
                "type": "string",
                "required": True,
                "label": "Natural Language Query",
                "human_description": "Natural language query to convert to a rule",
                "description": "Natural language query to convert to a rule"
            },
            "context": {
                "type": "object",
                "required": False,
                "label": "Context Data Structure",
                "human_description": "Context data structure for the rule",
                "description": "Context data structure for the rule"
            }
        }