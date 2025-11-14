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
    
    def run(self, ruleset_id: str, rule_db_url: str, business_db_url: str, demo: str, **kwargs) -> Dict[str, Any]:
        """
        Delete a rule set.
        
        Args:
            ruleset_id: ID of the ruleset to delete
            rule_db_url: Rule database connection URL
            business_db_url: Business database connection URL
            demo: Demo parameter in a format similar to MySQL connection string
            **kwargs: Additional keyword arguments
            
        Returns:
            Operation result
        """
        try:
            # Initialize rule database
            from provider.rule_storage import init_rule_db
            init_rule_db(rule_db_url)
            
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
                "label": {
                    "en_US": "Rule Set ID",
                    "zh_Hans": "规则集ID"
                },
                "form": "llm",
                "human_description": {
                    "en_US": "ID of the rule set to delete",
                    "zh_Hans": "要删除的规则集的ID"
                }
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