"""
Validate Ruleset Tool

This tool validates user input using the rule engine.
"""

import json
from typing import Any, Dict

from dify_plugin import Tool

from provider.rule_storage import get_rule_set
from provider.rule_engine import execute_rule_set


class ValidateRuleset(Tool):
    """
    Validate Ruleset Tool
    """
    
    def run(self, ruleset_id: str, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Validate user input using the rule engine.
        
        Args:
            ruleset_id: ID of the ruleset to validate against
            context: Context data to validate
            **kwargs: Additional keyword arguments
            
        Returns:
            Validation result
        """
        try:
            # Parse context if it's a string
            if isinstance(context, str):
                context = json.loads(context)
            
            # Get the ruleset
            ruleset = get_rule_set(ruleset_id)
            if not ruleset:
                return {
                    "success": False,
                    "error": f"Ruleset with ID '{ruleset_id}' not found",
                    "result": None
                }
            
            # Execute the ruleset
            result = execute_rule_set(ruleset, context)
            
            return {
                "success": True,
                "error": None,
                "result": result
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
            "ruleset_id": {
                "type": "string",
                "required": True,
                "label": "Ruleset ID",
                "human_description": "ID of the ruleset to validate against",
                "description": "ID of the ruleset to validate against"
            },
            "context": {
                "type": "object",
                "required": True,
                "label": "Context Data",
                "human_description": "Context data to validate",
                "description": "Context data to validate"
            }
        }