"""
LLM Query Parser Module

This module provides functionality to parse natural language queries using LLM
and convert them into structured rule expressions.
"""

import json
import uuid
from typing import Any, Dict, List, Optional, Union

# Removed unused import LLMType


class LLMQueryParser:
    """
    LLM Query Parser for converting natural language queries to rule expressions.
    """
    
    def __init__(self, llm_model: str = "gpt-4o"):
        """
        Initialize the LLM Query Parser.
        
        Args:
            llm_model: LLM model to use for parsing
        """
        self.llm_model = llm_model
    
    def parse_query_to_rule(self, query: str, context: Dict[str, Any], 
                           llm_invoker: Any) -> Dict[str, Any]:
        """
        Parse a natural language query into a rule expression.
        
        Args:
            query: Natural language query
            context: Context data for the query
            llm_invoker: LLM invoker from Dify
            
        Returns:
            Rule expression dictionary
        """
        # Create a prompt for the LLM
        prompt = self._create_rule_generation_prompt(query, context)
        
        try:
            # Invoke the LLM
            response = llm_invoker.invoke(
                model_parameters={
                    "model": self.llm_model,
                    "prompt_messages": [
                        {
                            "role": "system",
                            "text": self._get_system_prompt()
                        },
                        {
                            "role": "user",
                            "text": prompt
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 1000
                }
            )
            
            # Extract the response text
            response_text = response.get("text", "")
            
            # Parse the JSON response
            try:
                rule_expression = json.loads(response_text)
                return self._validate_rule_expression(rule_expression)
            except json.JSONDecodeError:
                # Try to extract JSON from the response
                json_match = self._extract_json_from_text(response_text)
                if json_match:
                    rule_expression = json.loads(json_match)
                    return self._validate_rule_expression(rule_expression)
                else:
                    # Return a default rule if parsing fails
                    return self._create_default_rule(query)
        except Exception as e:
            # Return a default rule if LLM invocation fails
            return self._create_default_rule(query)
    
    def parse_query_to_ruleset(self, query: str, context: Dict[str, Any], 
                              target: str = "default", llm_invoker: Any = None) -> Dict[str, Any]:
        """
        Parse a natural language query into a complete rule set.
        
        Args:
            query: Natural language query
            context: Context data for the query
            target: Target for the rule set
            llm_invoker: LLM invoker from Dify
            
        Returns:
            Rule set dictionary
        """
        # Create a prompt for the LLM
        prompt = self._create_ruleset_generation_prompt(query, context)
        
        try:
            # Invoke the LLM
            response = llm_invoker.invoke(
                model_parameters={
                    "model": self.llm_model,
                    "prompt_messages": [
                        {
                            "role": "system",
                            "text": self._get_system_prompt()
                        },
                        {
                            "role": "user",
                            "text": prompt
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 2000
                }
            )
            
            # Extract the response text
            response_text = response.get("text", "")
            
            # Parse the JSON response
            try:
                ruleset = json.loads(response_text)
                return self._validate_ruleset(ruleset, target)
            except json.JSONDecodeError:
                # Try to extract JSON from the response
                json_match = self._extract_json_from_text(response_text)
                if json_match:
                    ruleset = json.loads(json_match)
                    return self._validate_ruleset(ruleset, target)
                else:
                    # Return a default rule set if parsing fails
                    return self._create_default_ruleset(query, target)
        except Exception as e:
            # Return a default rule set if LLM invocation fails
            return self._create_default_ruleset(query, target)
    
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for the LLM.
        
        Returns:
            System prompt string
        """
        return """
You are an AI assistant that converts natural language queries into structured rule expressions for a rule engine system.

Your task is to analyze the user's query and generate a valid JSON rule expression that can be evaluated by the rule engine.

The rule expression should follow this structure:
{
  "field": "path.to.field.in.context",
  "operator": "one_of_the_supported_operators",
  "value": "expected_value"
}

Supported operators include:
- eq: equals
- ne: not equals
- lt: less than
- le: less than or equal to
- gt: greater than
- ge: greater than or equal to
- in: in a list
- not_in: not in a list
- contains: contains a substring
- not_contains: does not contain a substring
- startswith: starts with a substring
- endswith: ends with a substring
- regex: matches a regular expression
- is_null: is null
- is_not_null: is not null
- is_empty: is empty
- is_not_empty: is not empty

For complex conditions, you can use logical operators:
{
  "and": [
    { "field": "age", "operator": "gt", "value": 18 },
    { "field": "status", "operator": "eq", "value": "active" }
  ]
}

{
  "or": [
    { "field": "role", "operator": "eq", "value": "admin" },
    { "field": "role", "operator": "eq", "value": "moderator" }
  ]
}

{
  "not": { "field": "deleted", "operator": "eq", "value": true }
}

For rule sets, the structure should be:
{
  "name": "Rule Set Name",
  "description": "Description of what this rule set does",
  "target": "target_entity",
  "rules": [
    {
      "id": "unique_rule_id",
      "expression": { ... rule expression ... },
      "message": "Message to display if this rule fails"
    }
  ]
}

Always respond with valid JSON only, without any additional text or explanation.
"""
    
    def _create_rule_generation_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """
        Create a prompt for generating a single rule.
        
        Args:
            query: Natural language query
            context: Context data for the query
            
        Returns:
            Prompt string
        """
        context_str = json.dumps(context, indent=2)
        
        return f"""
Convert the following natural language query into a rule expression:

Query: {query}

Context data structure:
{context_str}

Please generate a valid JSON rule expression that captures the intent of the query.
"""
    
    def _create_ruleset_generation_prompt(self, query: str, context: Dict[str, Any]) -> str:
        """
        Create a prompt for generating a rule set.
        
        Args:
            query: Natural language query
            context: Context data for the query
            
        Returns:
            Prompt string
        """
        context_str = json.dumps(context, indent=2)
        
        return f"""
Convert the following natural language query into a complete rule set:

Query: {query}

Context data structure:
{context_str}

Please generate a valid JSON rule set that captures the intent of the query.
The rule set should include a name, description, and one or more rules.
"""
    
    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """
        Extract JSON from text that may contain additional content.
        
        Args:
            text: Text that may contain JSON
            
        Returns:
            JSON string or None if not found
        """
        import re
        
        # Look for JSON blocks in the text
        json_pattern = r'```json\s*(.*?)\s*```'
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            return match.group(1)
        
        # Look for JSON objects in the text
        json_pattern = r'\{.*\}'
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            return match.group(0)
        
        return None
    
    def _validate_rule_expression(self, rule_expression: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and fix a rule expression.
        
        Args:
            rule_expression: Rule expression to validate
            
        Returns:
            Validated rule expression
        """
        # Basic validation
        if not isinstance(rule_expression, dict):
            return self._create_default_rule("Invalid rule expression")
        
        # Check for required fields in simple expressions
        if 'field' in rule_expression and 'operator' in rule_expression:
            if 'value' not in rule_expression and rule_expression['operator'] not in [
                'is_null', 'is_not_null', 'is_empty', 'is_not_empty'
            ]:
                rule_expression['value'] = None
        
        # Add ID if not present
        if 'id' not in rule_expression:
            rule_expression['id'] = str(uuid.uuid4())
        
        return rule_expression
    
    def _validate_ruleset(self, ruleset: Dict[str, Any], target: str = "default") -> Dict[str, Any]:
        """
        Validate and fix a rule set.
        
        Args:
            ruleset: Rule set to validate
            target: Target for the rule set
            
        Returns:
            Validated rule set
        """
        # Basic validation
        if not isinstance(ruleset, dict):
            return self._create_default_ruleset("Invalid rule set", target)
        
        # Add default values for required fields
        if 'name' not in ruleset:
            ruleset['name'] = "Generated Rule Set"
        
        if 'description' not in ruleset:
            ruleset['description'] = "Rule set generated from natural language query"
        
        if 'target' not in ruleset:
            ruleset['target'] = target
        
        if 'rules' not in ruleset or not isinstance(ruleset['rules'], list):
            ruleset['rules'] = []
        
        # Validate each rule
        for rule in ruleset['rules']:
            if not isinstance(rule, dict):
                continue
                
            if 'id' not in rule:
                rule['id'] = str(uuid.uuid4())
            
            if 'expression' not in rule:
                rule['expression'] = self._create_default_rule("Missing expression")
            
            if 'message' not in rule:
                rule['message'] = "Rule validation failed"
        
        return ruleset
    
    def _create_default_rule(self, query: str) -> Dict[str, Any]:
        """
        Create a default rule when parsing fails.
        
        Args:
            query: Original query
            
        Returns:
            Default rule expression
        """
        return {
            "id": str(uuid.uuid4()),
            "field": "query",
            "operator": "contains",
            "value": query[:50],  # Truncate if too long
            "message": f"Default rule generated from query: {query}"
        }
    
    def _create_default_ruleset(self, query: str, target: str = "default") -> Dict[str, Any]:
        """
        Create a default rule set when parsing fails.
        
        Args:
            query: Original query
            target: Target for the rule set
            
        Returns:
            Default rule set
        """
        return {
            "id": str(uuid.uuid4()),
            "name": "Generated Rule Set",
            "description": f"Rule set generated from query: {query}",
            "target": target,
            "rules": [
                {
                    "id": str(uuid.uuid4()),
                    "expression": {
                        "field": "query",
                        "operator": "contains",
                        "value": query[:50]  # Truncate if too long
                    },
                    "message": "Default rule validation failed"
                }
            ]
        }


# Global LLM query parser instance
llm_query_parser = LLMQueryParser()


def parse_query_to_rule(query: str, context: Dict[str, Any], 
                       llm_invoker: Any, llm_model: str = "gpt-4o") -> Dict[str, Any]:
    """
    Parse a natural language query into a rule expression.
    
    Args:
        query: Natural language query
        context: Context data for the query
        llm_invoker: LLM invoker from Dify
        llm_model: LLM model to use for parsing
        
    Returns:
        Rule expression dictionary
    """
    parser = LLMQueryParser(llm_model)
    return parser.parse_query_to_rule(query, context, llm_invoker)


def parse_query_to_ruleset(query: str, context: Dict[str, Any], 
                          target: str = "default", llm_invoker: Any = None,
                          llm_model: str = "gpt-4o") -> Dict[str, Any]:
    """
    Parse a natural language query into a complete rule set.
    
    Args:
        query: Natural language query
        context: Context data for the query
        target: Target for the rule set
        llm_invoker: LLM invoker from Dify
        llm_model: LLM model to use for parsing
        
    Returns:
        Rule set dictionary
    """
    parser = LLMQueryParser(llm_model)
    return parser.parse_query_to_ruleset(query, context, target, llm_invoker)