"""
Add Rule Tool

This tool adds or updates a rule set in the rule engine.
"""

import json
from typing import Any, Dict

from dify_plugin import Tool

from provider.rule_storage import add_rule_set, update_rule_set, get_rule_set


class AddRule(Tool):
    """
    Add Rule Tool
    """
    
    def run(self, rule_json: Dict[str, Any], rule_db_url: str, business_db_url: str, demo: str, **kwargs) -> Dict[str, Any]:
        """
        Add or update a rule set.
        
        Args:
            rule_json: Complete RuleSet JSON
            rule_db_url: Rule database connection URL
            business_db_url: Business database connection URL
            demo: Demo parameter in a format similar to MySQL connection string
            **kwargs: Additional keyword arguments
            
        Returns:
            Operation result
        """
        try:
            # Parse rule_json if it's a string
            if isinstance(rule_json, str):
                rule_json = json.loads(rule_json)
            
            # Initialize rule database
            from provider.rule_storage import init_rule_db
            init_rule_db(rule_db_url)
            
            # Check if ruleset already exists
            existing_ruleset = None
            if 'id' in rule_json:
                existing_ruleset = get_rule_set(rule_json['id'])
            
            # Add or update the ruleset
            if existing_ruleset:
                # Update existing ruleset
                update_rule_set(rule_json['id'], rule_json)
                operation = "updated"
                ruleset_id = rule_json['id']
            else:
                # Add new ruleset
                ruleset_id = add_rule_set(rule_json)
                operation = "added"
            
            return {
                "success": True,
                "error": None,
                "result": {
                    "operation": operation,
                    "ruleset_id": ruleset_id,
                    "message": f"Rule set successfully {operation} with ID: {ruleset_id}"
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
            "rule_json": {
                "type": "object",
                "required": True,
                "label": "Rule Set JSON",
                "human_description": "Complete RuleSet JSON to add or update",
                "description": "Complete RuleSet JSON to add or update"
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