import sys
import os
import json
import uuid

# Add the provider directory to the path
provider_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'provider'))
sys.path.append(provider_dir)

# Import the LLMQueryParser from the llm_query_parser module
from llm_query_parser import LLMQueryParser

# Create an instance of LLMQueryParser
parser = LLMQueryParser()

# Test with a sample ruleset that has hardcoded IDs
input_ruleset = {
    'id': 'ruleset_001',
    'name': '手机销售价限制规则',
    'description': '手机销售价不能低于2000元',
    'target': 'generic',
    'applies_when': [],
    'rules': [
        {
            'id': 'rule_001',
            'name': '最低销售价限制',
            'type': 'range',
            'description': '确保手机的销售价格不低于2000元',
            'expression': 'input.手机销售价 >= 2000',
            'message': '手机销售价不能低于2000元',
            'requires': []
        }
    ],
    'on_fail': {
        'action': 'block',
        'notify': ['user']
    }
}

# Validate the ruleset
target = 'generic'
validated_ruleset = parser._validate_ruleset(input_ruleset, target)

# Print the result
print('Original ruleset:', json.dumps(input_ruleset, ensure_ascii=False, indent=2))
print('\nValidated ruleset:', json.dumps(validated_ruleset, ensure_ascii=False, indent=2))
print('\nRuleset ID changed to UUID:', validated_ruleset['id'] != input_ruleset['id'])
print('Rule ID changed to UUID:', validated_ruleset['rules'][0]['id'] != input_ruleset['rules'][0]['id'])