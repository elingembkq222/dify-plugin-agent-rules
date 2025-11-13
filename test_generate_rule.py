import json
import os
from dotenv import load_dotenv
from provider.llm_query_parser import parse_query_to_ruleset

# Load environment variables
load_dotenv()

# Debug: print environment variables
print("LLM_MODEL:", os.getenv("LLM_MODEL"))
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))
print("OPENAI_API_BASE:", os.getenv("OPENAI_API_BASE"))

# Test query
query = "门诊病假一年7天"
context = {}

# Parse query to ruleset
result = parse_query_to_ruleset(query, context)

# Print the result
print(json.dumps(result, indent=2, ensure_ascii=False))