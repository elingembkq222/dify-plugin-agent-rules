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
    
    def run(self, rule_json: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Add or update a rule set.
        
        Args:
            rule_json: Complete RuleSet JSON
            **kwargs: Additional keyword arguments
            
        Returns:
            Operation result
        """
        try:
            # Parse rule_json if it's a string
            if isinstance(rule_json, str):
                rule_json = json.loads(rule_json)
            
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
                "description": "Complete RuleSet JSON to add or update"
            }
        }