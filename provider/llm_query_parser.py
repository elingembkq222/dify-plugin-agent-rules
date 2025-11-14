"""
LLM Query Parser Module

This module provides functionality to parse natural language queries using LLM
and convert them into structured rule expressions.
"""

import json
import os
import uuid
import requests
from typing import Any, Dict, List, Optional, Union
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMQueryParser:
    """    LLM Query Parser for converting natural language queries to rule expressions.    """
    
    def __init__(self, llm_model: str = "gpt-4o"):
        """
        Initialize the LLM Query Parser.
        
        Args:
            llm_model: LLM model to use for parsing
        """
        self.llm_model = llm_model
        # Load API configurations from environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.aliyun_access_key_id = os.getenv("ALIYUN_ACCESS_KEY_ID")
        self.aliyun_access_key_secret = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
        self.aliyun_llm_endpoint = os.getenv("ALIYUN_LLM_ENDPOINT", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.aliyun_llm_model = os.getenv("ALIYUN_LLM_MODEL", "qwen-7b-chat-turbo")
        # Load system prompt
        self.system_prompt = self._get_system_prompt()
    
    def parse_query_to_rule(self, query: str, context: Dict[str, Any], 
                           llm_invoker: Any = None) -> Dict[str, Any]:
        """
        Parse a natural language query into a rule expression.
        
        Args:
            query: Natural language query
            context: Context data for the query
            llm_invoker: Deprecated, kept for compatibility
            
        Returns:
            Rule expression dictionary
        """
        # Create a prompt for the LLM
        prompt = self._create_rule_generation_prompt(query, context)
        
        try:
            # Prepare prompt messages
            prompt_messages = [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Invoke LLM directly based on model type
            response_text = ""
            if self.llm_model.startswith("gpt-"):
                if not self.openai_api_key:
                    raise ValueError("OpenAI API key is required for GPT models")
                api_response = self._call_openai_api(prompt_messages, 0.1, 1000)
                response_text = api_response["choices"][0]["message"]["content"]
            elif self.llm_model.startswith("qwen-"):
                if not self.aliyun_access_key_id or not self.aliyun_access_key_secret:
                    raise ValueError("Alibaba Cloud API credentials are required for Qwen models")
                api_response = self._call_aliyun_api(prompt_messages, 0.1, 1000)
                response_text = api_response["choices"][0]["message"]["content"]
            else:
                # Unsupported model, use default rule
                return self._create_default_rule(query)
            
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
    
    def _call_openai_api(self, prompt_messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> Dict:
        """Call OpenAI API directly."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        data = {
            "model": self.llm_model,
            "messages": prompt_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        url = f"{self.openai_api_base}/chat/completions"
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raise an error for bad status codes
            return response.json()
        except Exception as e:
            return None
    
    def _call_aliyun_api(self, prompt_messages, temperature, max_tokens):
        """Call Alibaba Cloud LLM API directly."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.aliyun_access_key_id}:{self.aliyun_access_key_secret}"
        }
        data = {
            "model": self.aliyun_llm_model,
            "messages": prompt_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        response = requests.post(
            f"{self.aliyun_llm_endpoint}/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def parse_query_to_ruleset(self, query: str, context: Dict[str, Any], 
                              target: str = "default", llm_invoker: Any = None) -> Dict[str, Any]:
        """
        Parse a natural language query into a complete rule set.
        
        Args:
            query: Natural language query
            context: Context data for the query
            target: Target for the rule set
            llm_invoker: Deprecated, kept for compatibility
            
        Returns:
            Rule set dictionary
        """
        # Create a prompt for the LLM
        prompt = self._create_ruleset_generation_prompt(query, context)
        
        try:
            # Prepare prompt messages
            prompt_messages = [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Invoke LLM directly based on model type
            response_text = ""
            if self.llm_model.startswith("gpt-"):
                if not self.openai_api_key:
                    raise ValueError("OpenAI API key is required for GPT models")
                api_response = self._call_openai_api(prompt_messages, 0.1, 2000)
                response_text = api_response["choices"][0]["message"]["content"]
            elif self.llm_model.startswith("qwen-"):
                if not self.aliyun_access_key_id or not self.aliyun_access_key_secret:
                    raise ValueError("Alibaba Cloud API credentials are required for Qwen models")
                api_response = self._call_aliyun_api(prompt_messages, 0.1, 2000)
                response_text = api_response["choices"][0]["message"]["content"]
            else:
                # Unsupported model, use default rule
                return self._create_default_ruleset(query, target)
            
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
        prompt_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../prompts/system_prompt.txt"
        )
        with open(prompt_file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
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
        
        # Always generate a UUID for the ruleset
        ruleset['id'] = str(uuid.uuid4())
        
        if 'name' not in ruleset:
            ruleset['name'] = "Generated Rule Set"
        
        if 'description' not in ruleset:
            ruleset['description'] = "Rule set generated from natural language query"
        
        if 'target' not in ruleset:
            ruleset['target'] = target
        
        if 'applies_when' not in ruleset or not isinstance(ruleset['applies_when'], list):
            ruleset['applies_when'] = []
        
        if 'rules' not in ruleset or not isinstance(ruleset['rules'], list):
            ruleset['rules'] = []
        
        if 'on_fail' not in ruleset or not isinstance(ruleset['on_fail'], dict):
            ruleset['on_fail'] = { "action": "block", "notify": ["user"] }
        
        # Validate each rule
        for rule in ruleset['rules']:
            if not isinstance(rule, dict):
                continue
                
            # Always generate a UUID for each rule
            rule['id'] = str(uuid.uuid4())
            
            if 'name' not in rule:
                rule['name'] = f"Rule {rule['id'][:8]}"
            
            if 'type' not in rule:
                # Default to comparison if expression is a string, otherwise conditional
                rule['type'] = "comparison" if isinstance(rule.get('expression'), str) else "conditional"
            
            if 'expression' not in rule:
                rule['expression'] = "true"
            
            if 'message' not in rule:
                rule['message'] = "Rule validation failed"
            
            # Add requires if it's a conditional rule and not present
            if rule['type'] == "conditional" and 'requires' not in rule:
                rule['requires'] = []
        
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
            "applies_when": [],
            "rules": [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Default Comparison Rule",
                    "type": "comparison",
                    "expression": f"request.query contains '{query[:50]}'",
                    "message": "Default rule validation failed"
                }
            ],
            "on_fail": { "action": "block", "notify": ["user"] }
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