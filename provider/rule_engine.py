"""
Rule Engine Module

This module provides the core logic for executing rule sets against context data.
It evaluates expressions and determines if rules pass or fail.
"""

import ast
import operator
import re
from typing import Any, Dict, List, Optional, Union

from .data_resolver import resolve_data


class RuleEngine:
    """
    Rule Engine for evaluating rule sets against context data.
    """
    
    # Mapping of operator strings to actual Python operators
    OPERATORS = {
        'eq': operator.eq,
        'ne': operator.ne,
        'lt': operator.lt,
        'le': operator.le,
        'gt': operator.gt,
        'ge': operator.ge,
        'and': operator.and_,
        'or': operator.or_,
        'not': operator.not_,
        'in': lambda x, y: x in y,
        'not_in': lambda x, y: x not in y,
        'contains': lambda x, y: y in x,
        'not_contains': lambda x, y: y not in x,
        'startswith': lambda x, y: x.startswith(y) if isinstance(x, str) else False,
        'endswith': lambda x, y: x.endswith(y) if isinstance(x, str) else False,
        'regex': lambda x, y: bool(re.search(y, str(x))),
        'is_null': lambda x: x is None,
        'is_not_null': lambda x: x is not None,
        'is_empty': lambda x: not bool(x),
        'is_not_empty': lambda x: bool(x),
    }
    
    def __init__(self):
        """Initialize the Rule Engine."""
        pass
    
    def evaluate_expression(self, expression: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Evaluate a rule expression against the provided context.
        
        Args:
            expression: Rule expression dictionary
            context: Context data to evaluate against
            
        Returns:
            True if the expression evaluates to True, False otherwise
        """
        if not expression:
            return True
            
        # Handle simple field-value comparison
        if 'field' in expression and 'operator' in expression and 'value' in expression:
            field = expression['field']
            op = expression['operator']
            value = expression['value']
            
            # Get the actual value from context
            actual_value = self._get_field_value(field, context)
            
            # Evaluate the operation
            return self._evaluate_operation(op, actual_value, value, context)
        
        # Handle logical operations (and, or, not)
        if 'and' in expression:
            return all(self.evaluate_expression(expr, context) for expr in expression['and'])
        
        if 'or' in expression:
            return any(self.evaluate_expression(expr, context) for expr in expression['or'])
        
        if 'not' in expression:
            return not self.evaluate_expression(expression['not'], context)
        
        # Handle custom expressions
        if 'custom' in expression:
            return self._evaluate_custom_expression(expression['custom'], context)
        
        # Default to True if expression format is not recognized
        return True
    
    def _get_field_value(self, field: str, context: Dict[str, Any]) -> Any:
        """
        Get the value of a field from the context, supporting nested fields.
        
        Args:
            field: Field name, can be nested (e.g., "user.address.city")
            context: Context data
            
        Returns:
            Field value or None if not found
        """
        # Split field into parts for nested access
        parts = field.split('.')
        value = context
        
        try:
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None
            return value
        except (KeyError, TypeError, AttributeError):
            return None
    
    def _evaluate_operation(self, op: str, actual: Any, expected: Any, context: Dict[str, Any]) -> bool:
        """
        Evaluate a single operation.
        
        Args:
            op: Operator name
            actual: Actual value from context
            expected: Expected value from rule
            context: Full context data
            
        Returns:
            True if the operation evaluates to True, False otherwise
        """
        if op not in self.OPERATORS:
            raise ValueError(f"Unknown operator: {op}")
        
        # Handle special operators that don't need expected value
        if op in ['is_null', 'is_not_null', 'is_empty', 'is_not_empty']:
            return self.OPERATORS[op](actual)
        
        # Handle operators that compare actual and expected values
        return self.OPERATORS[op](actual, expected)
    
    def _evaluate_custom_expression(self, custom_expr: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a custom Python expression.
        
        Args:
            custom_expr: Custom Python expression string
            context: Context data
            
        Returns:
            True if the expression evaluates to True, False otherwise
        """
        try:
            # Create a safe namespace for evaluation
            safe_globals = {
                '__builtins__': {},
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'abs': abs,
                'min': min,
                'max': max,
                'sum': sum,
                'any': any,
                'all': all,
                're': re,
            }
            
            # Add context variables to the local namespace
            safe_locals = dict(context)
            
            # Evaluate the expression
            result = eval(custom_expr, safe_globals, safe_locals)
            return bool(result)
        except Exception as e:
            # Log error in a real implementation
            return False
    
    def execute_rule_set(self, rule_set: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a rule set against the provided context.
        
        Args:
            rule_set: Rule set data dictionary
            context: Context data to evaluate against
            
        Returns:
            Dictionary containing execution results
        """
        if not rule_set or 'rules' not in rule_set:
            return {
                'pass': False,
                'violations': [],
                'error': 'Invalid rule set'
            }
        
        # Resolve any required data for the rule set
        resolved_context = dict(context)
        
        # Add any additional data required by the rules
        for req in rule_set.get('requires', []):
            if isinstance(req, dict) and 'name' in req:
                resolved_context[req['name']] = resolve_data(req, context)
        
        # Evaluate each rule in the rule set
        results = []
        for rule in rule_set['rules']:
            if not isinstance(rule, dict):
                continue
                
            rule_id = rule.get('id', 'unknown')
            rule_expression = rule.get('expression', {})
            rule_message = rule.get('message', 'Rule failed')
            
            try:
                passed = self.evaluate_expression(rule_expression, resolved_context)
                results.append({
                    'id': rule_id,
                    'pass': passed,
                    'message': rule_message
                })
            except Exception as e:
                results.append({
                    'id': rule_id,
                    'pass': False,
                    'message': f"Error evaluating rule: {str(e)}"
                })
        
        # Determine overall result
        violations = [r for r in results if not r['pass']]
        overall_pass = len(violations) == 0
        
        return {
            'pass': overall_pass,
            'violations': violations,
            'results': results,
            'rule_set_id': rule_set.get('id'),
            'rule_set_name': rule_set.get('name')
        }


# Global rule engine instance
rule_engine = RuleEngine()


def execute_rule_set(rule_set: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a rule set against the provided context.
    
    Args:
        rule_set: Rule set data dictionary
        context: Context data to evaluate against
        
    Returns:
        Dictionary containing execution results
    """
    return rule_engine.execute_rule_set(rule_set, context)