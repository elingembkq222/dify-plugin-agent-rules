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
    
    def run(self, ruleset_id: str, context: Dict[str, Any], rule_db_url: str, business_db_url: str, demo: str, **kwargs) -> Dict[str, Any]:
        """
        Validate user input using the rule engine.
        
        Args:
            ruleset_id: ID of the ruleset to validate against
            context: Context data to validate
            rule_db_url: Rule database connection URL
            business_db_url: Business database connection URL
            demo: Demo parameter in a format similar to MySQL connection string
            **kwargs: Additional keyword arguments
            
        Returns:
            Validation result
        """
        try:
            # Initialize rule database
            from provider.rule_storage import init_rule_db
            init_rule_db(rule_db_url)
            
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
            },
            "rule_db_url": {
                "type": "string",
                "required": True,
                "label": "Rule Database URL",
                "human_description": "Rule database connection URL (e.g., mysql+pymysql://root:password@localhost:3306/agent_rules?charset=utf8mb4)",
                "description": "Rule database connection URL for storing rules"
            },
            "business_db_url": {
                "type": "string",
                "required": True,
                "label": "Business Database URL",
                "human_description": "Business database connection URL (e.g., mysql+pymysql://root:password@localhost:3306/business_data?charset=utf8mb4)",
                "description": "Business database connection URL for accessing external data"
            },
            "demo": {
                "type": "string",
                "required": True,
                "label": "Demo Parameter",
                "human_description": "Demo parameter in a format similar to MySQL connection string",
                "description": "Demo parameter for testing purposes"
            }
        }