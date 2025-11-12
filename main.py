from dify_plugin import Plugin, DifyPluginEnv
from provider.rule_storage import init_rule_db

class RuleEnginePlugin(Plugin):
    def on_install(self, config):
        """Initialize the rule database when the plugin is installed."""
        rule_db_url = config.get("RULE_DB_URL", "sqlite:///rule_engine.db")
        init_rule_db(rule_db_url)
        print("✅ Rule DB initialized")
    
    def on_start(self, config):
        """Called when the plugin starts."""
        llm_model = config.get("LLM_MODEL", "gpt-4o")
        print(f"🚀 Rule Engine started with LLM: {llm_model}")
    
    def on_stop(self):
        """Called when the plugin stops."""
        print("🛑 Rule Engine stopped")

plugin = RuleEnginePlugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=120))

if __name__ == '__main__':
    plugin.run()
