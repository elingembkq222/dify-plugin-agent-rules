"""
Delete Rule Tool

This tool deletes a rule set from the rule engine.
"""

import json
from typing import Any, Dict

from dify_plugin import Tool

from provider.rule_storage import delete_rule_set


class DeleteRule(Tool):
    """
    Delete Rule Tool
    """
    
    def run(self, ruleset_id: str, **kwargs) -> Dict[str, Any]:
        """
        Delete a rule set.
        
        Args:
            ruleset_id: ID of the ruleset to delete
            **kwargs: Additional keyword arguments
            
        Returns:
            Operation result
        """
        try:
            # Delete the ruleset
            result = delete_rule_set(ruleset_id)
            
            if result:
                return {
                    "success": True,
                    "error": None,
                    "result": {
                        "message": f"Rule set with ID '{ruleset_id}' successfully deleted"
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Rule set with ID '{ruleset_id}' not found",
                    "result": None
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
                "label": "Rule Set ID",
                "human_description": "ID of the ruleset to delete",
                "description": "ID of the ruleset to delete"
            }
        }