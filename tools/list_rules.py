"""
List Rules Tool

This tool lists all available rule sets in the rule engine.
"""

from typing import Any, Dict, List

from dify_plugin import Tool

from provider.rule_storage import list_all_rule_sets, get_rule_sets_by_target


class ListRules(Tool):
    """
    List Rules Tool
    """
    
    def run(self, rule_db_url: str, business_db_url: str, demo: str, target: str = None, **kwargs) -> Dict[str, Any]:
        """
        List all available rule sets.
        
        Args:
            rule_db_url: Rule database connection URL
            business_db_url: Business database connection URL
            demo: Demo parameter in a format similar to MySQL connection string
            target: Optional target filter
            **kwargs: Additional keyword arguments
            
        Returns:
            List of rule sets
        """
        try:
            # Initialize rule database
            from provider.rule_storage import init_rule_db
            init_rule_db(rule_db_url)
            
            # Get rule sets based on target filter
            if target:
                rule_sets = get_rule_sets_by_target(target)
            else:
                rule_sets = list_all_rule_sets()
            
            # Format the response
            formatted_rules = []
            for rule_set in rule_sets:
                formatted_rules.append({
                    "id": rule_set.get("id"),
                    "name": rule_set.get("name"),
                    "target": rule_set.get("target"),
                    "description": rule_set.get("description"),
                    "created_at": rule_set.get("created_at"),
                    "rule_count": len(rule_set.get("rules", []))
                })
            
            return {
                "success": True,
                "error": None,
                "result": {
                    "count": len(formatted_rules),
                    "rules": formatted_rules
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
            "target": {
                "type": "string",
                "required": False,
                "label": "Target Filter",
                "human_description": "Optional filter for rule sets by target",
                "description": "Optional filter for rule sets by target"
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