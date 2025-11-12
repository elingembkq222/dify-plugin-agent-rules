from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class DifyPluginAgentRulesProvider(ToolProvider):
    
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # Validate required configuration
            if not credentials.get("RULE_DB_URL"):
                raise ToolProviderCredentialValidationError("Rule Database URL is required")
            
            # Initialize rule database if needed
            from .rule_storage import init_rule_db
            init_rule_db(credentials["RULE_DB_URL"])
            
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
