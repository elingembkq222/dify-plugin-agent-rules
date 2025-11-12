"""
List Rules Tool

This tool lists all available rule sets in the rule engine.
"""

from typing import Any, Dict, List

from dify_plugin import Tool

from provider.rule_storage import list_rule_sets


class ListRules(Tool):
    """
    List Rules Tool
    """
    
    def run(self, target: str = None, **kwargs) -> Dict[str, Any]:
        """
        List all available rule sets.
        
        Args:
            target: Optional target filter
            **kwargs: Additional keyword arguments
            
        Returns:
            List of rule sets
        """
        try:
            # Get all rule sets
            rule_sets = list_rule_sets(target)
            
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
                "description": "Optional filter for rule sets by target"
            }
        }