import json, os, sys, traceback

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv

# Load environment variables before importing rule engine so global instances see them
load_dotenv()
from provider.rule_engine import execute_rule_set

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print(json.dumps({"success": False, "error": "Usage: python validate_ruleset.py <ruleset_json> <context_json> [business_db_url]"}), file=sys.stderr)
        sys.exit(1)

    try:
        ruleset = json.loads(sys.argv[1])
        context = json.loads(sys.argv[2])
        business_db_url = sys.argv[3] if (len(sys.argv) > 3 and sys.argv[3]) else os.environ.get('BUSINESS_DB_URL')

        result = execute_rule_set(ruleset, context, business_db_url=business_db_url)
        
        print(json.dumps({
          "success": True,
          "result": result
        }, ensure_ascii=False))
    except Exception as e:
        error_type = type(e).__name__
        error_message = str(e)
        traceback_str = traceback.format_exc()
        
        print(json.dumps({
          "success": False,
          "error": {
            "type": error_type,
            "message": error_message,
            "traceback": traceback_str
          }
        }, ensure_ascii=False), file=sys.stderr)
        
        sys.exit(1)