import sys
import os
import uuid

# Add the provider directory to the path
provider_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'provider'))
sys.path.append(provider_dir)

# Import the modules
from rule_storage import init_rule_db, add_rule_set, get_rule_set, delete_rule_set
from llm_query_parser import LLMQueryParser

# Initialize the database (use in-memory SQLite for testing)
init_rule_db('sqlite:///:memory:')

# Create a test case with invalid ruleset ID
def test_invalid_ruleset_id():
    print("=== Testing invalid ruleset ID ===")
    invalid_ruleset = {
        'id': 'invalid_id_123',  # Not a UUID
        'name': '测试规则集',
        'target': 'generic',
        'rules': []
    }
    try:
        add_rule_set(invalid_ruleset)
        print("ERROR: Should have raised ValueError for invalid ruleset ID")
    except ValueError as e:
        print(f"SUCCESS: Got expected error: {e}")

def test_valid_ruleset_id():
    print("\n=== Testing valid ruleset ID ===")
    valid_ruleset = {
        'id': str(uuid.uuid4()),  # Valid UUID
        'name': '测试规则集',
        'target': 'generic',
        'rules': []
    }
    try:
        ruleset_id = add_rule_set(valid_ruleset)
        print(f"SUCCESS: Added ruleset with ID: {ruleset_id}")
        # Cleanup
        delete_rule_set(ruleset_id)
    except Exception as e:
        print(f"ERROR: Should have added ruleset: {e}")

def test_invalid_rule_id():
    print("\n=== Testing invalid rule ID ===")
    invalid_rule = {
        'name': '测试规则集',
        'target': 'generic',
        'rules': [
            {
                'id': 'invalid_rule_123',  # Not a UUID
                'name': '测试规则',
                'type': 'range',
                'expression': 'input.value >= 0',
                'message': '值必须大于等于0'
            }
        ]
    }
    try:
        add_rule_set(invalid_rule)
        print("ERROR: Should have raised ValueError for invalid rule ID")
    except ValueError as e:
        print(f"SUCCESS: Got expected error: {e}")

def test_auto_uuid_generation():
    print("\n=== Testing automatic UUID generation ===")
    ruleset = {
        'name': '自动生成UUID测试',
        'target': 'generic',
        'rules': [
            {
                'name': '测试规则1',
                'type': 'range',
                'expression': 'input.value >= 0',
                'message': '值必须大于等于0'
            },
            {
                'name': '测试规则2',
                'type': 'range',
                'expression': 'input.value <= 100',
                'message': '值必须小于等于100'
            }
        ]
    }
    try:
        # First add without IDs - should auto-generate
        ruleset_id = add_rule_set(ruleset)
        print(f"SUCCESS: Added ruleset with auto-generated ID: {ruleset_id}")
        
        # Get it back and check IDs
        retrieved_ruleset = get_rule_set(ruleset_id)
        print(f"SUCCESS: Retrieved ruleset: {retrieved_ruleset['id']}")
        
        # Check rule IDs
        for i, rule in enumerate(retrieved_ruleset['rules']):
            rule_id = rule.get('id', 'None')
            print(f"  Rule {i+1}: ID={rule_id} (auto-generated: {rule_id != 'None'})")
        
        # Cleanup
        delete_rule_set(ruleset_id)
    except Exception as e:
        print(f"ERROR: {e}")

def test_llm_query_parser():
    print("\n=== Testing LLM Query Parser ===")
    parser = LLMQueryParser()
    
    # Test with invalid IDs (should be replaced with valid UUIDs)
    input_ruleset = {
        'id': 'ruleset_001',  # Not a UUID
        'name': '手机销售价限制规则',
        'target': 'generic',
        'rules': [
            {
                'id': 'rule_001',  # Not a UUID
                'name': '最低销售价限制',
                'type': 'range',
                'expression': 'input.手机销售价 >= 2000',
                'message': '手机销售价不能低于2000元'
            }
        ]
    }
    
    try:
        validated_ruleset = parser._validate_ruleset(input_ruleset, 'generic')
        print(f"SUCCESS: Validated ruleset with new ID: {validated_ruleset['id']}")
        print(f"  Original ruleset ID: 'ruleset_001' -> New ID: {validated_ruleset['id']}")
        print(f"  Original rule ID: 'rule_001' -> New ID: {validated_ruleset['rules'][0]['id']}")
        
        # Now add it to the database - should work because IDs are now valid UUIDs
        ruleset_id = add_rule_set(validated_ruleset)
        print(f"SUCCESS: Added validated ruleset to database with ID: {ruleset_id}")
        
        # Cleanup
        delete_rule_set(ruleset_id)
    except Exception as e:
        print(f"ERROR: {e}")

# Run all tests
if __name__ == "__main__":
    test_invalid_ruleset_id()
    test_valid_ruleset_id()
    test_invalid_rule_id()
    test_auto_uuid_generation()
    test_llm_query_parser()
    print("\n=== All tests completed ===")