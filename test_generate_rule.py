import json
from provider.llm_query_parser import parse_query_to_ruleset

# Test query
query = "门诊病假一年7天"
context = {}

# Parse query to ruleset
result = parse_query_to_ruleset(query, context)

# Print the result
print(json.dumps(result, indent=2, ensure_ascii=False))