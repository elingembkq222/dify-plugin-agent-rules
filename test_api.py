import requests
import json
import time

# Test configuration
API_URL = 'http://localhost:3001'

# Test data
TEST_RULE_DATA = {
    "target": "product",
    "name": "Product Validation Rules",
    "description": "Rules for validating product information",
    "rules": [
        {
            "id": "rule-001",
            "expression": {
                "field": "product.price",
                "operator": ">=",
                "value": 0
            },
            "message": "Product price cannot be negative"
        },
        {
            "id": "rule-002",
            "expression": {
                "field": "product.stock",
                "operator": ">=",
                "value": 0
            },
            "message": "Product stock cannot be negative"
        }
    ]
}

TEST_QUERY = "门诊病假一年7天"


def test_add_rule():
    """Test the add_rule endpoint"""
    print("Testing add_rule endpoint...")
    url = f"{API_URL}/add_rule"
    response = requests.post(url, json=TEST_RULE_DATA)
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()


def test_validate_ruleset(ruleset_id):
    """Test the validate_ruleset endpoint"""
    print("\nTesting validate_ruleset endpoint...")
    url = f"{API_URL}/validate_ruleset"
    response = requests.post(url, json={"ruleset_id": ruleset_id, "context": {"product": {"price": 100, "stock": 50}}})
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()

def test_list_rules():
    """Test the list_rules endpoint"""
    print("\nTesting list_rules endpoint...")
    url = f"{API_URL}/list_rules"
    response = requests.get(url)
    print(f"Status code: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    return result


def test_generate_rule():
    """Test the generate_rule_from_query endpoint"""
    print("\nTesting generate_rule_from_query endpoint...")
    url = f"{API_URL}/generate_rule_from_query"
    response = requests.post(url, json={"query": TEST_QUERY})
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()


# Run the tests
if __name__ == "__main__":
    print("Starting API tests...")
    print(f"API URL: {API_URL}")
    print("=" * 50)

    # Test generate_rule_from_query
    generate_result = test_generate_rule()
    print("=" * 50)

    # Test add_rule
    add_result = test_add_rule()
    print("=" * 50)

    # Test list_rules
    list_result = test_list_rules()
    print("=" * 50)

    # Test validate_ruleset
    validate_result = test_validate_ruleset(add_result.get('ruleset_id'))
    print("=" * 50)

    # Summary
    print("Tests completed!")
    print(f"generate_rule_from_query: {'PASS' if generate_result.get('success') else 'FAIL'}")
    print(f"add_rule: {'PASS' if add_result.get('success') else 'FAIL'}")
    print(f"list_rules: {'PASS' if list_result.get('success') else 'FAIL'}")
    print(f"validate_ruleset: {'PASS' if validate_result.get('success') else 'FAIL'}")
    print(f"Total rules in database: {len(list_result.get('rules', []))}")