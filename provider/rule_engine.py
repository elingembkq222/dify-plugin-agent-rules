"""
Rule Engine Module

This module provides the core logic for executing rule sets against context data.
It evaluates expressions and determines if rules pass or fail.
"""

import ast
import operator
import re
from typing import Any, Dict, List, Optional, Union

try:
    from .data_resolver import resolve_data, DataResolver
    from .error_handler import (
        ErrorType, 
        handle_exception, 
        create_expression_evaluation_error_response,
        create_sql_syntax_error_response,
        create_database_connection_error_response,
        create_database_table_not_found_response,
        create_database_error_response
    )
except ImportError:
    try:
        from data_resolver import resolve_data, DataResolver
        from error_handler import (
            ErrorType, 
            handle_exception, 
            create_expression_evaluation_error_response,
            create_sql_syntax_error_response,
            create_database_connection_error_response,
            create_database_table_not_found_response,
            create_database_error_response
        )
    except ImportError:
        # If running as a script, add the provider directory to the path
        import os
        import sys
        provider_dir = os.path.dirname(os.path.abspath(__file__))
        if provider_dir not in sys.path:
            sys.path.insert(0, provider_dir)
        from data_resolver import resolve_data, DataResolver
        from error_handler import (
            ErrorType, 
            handle_exception, 
            create_expression_evaluation_error_response,
            create_sql_syntax_error_response,
            create_database_connection_error_response,
            create_database_table_not_found_response,
            create_database_error_response
        )


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
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne,
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
    
    def __init__(self, business_db_url: Optional[str] = None, rule_db_url: Optional[str] = None):
        """Initialize the Rule Engine."""
        # Initialize the data resolver with optional business and rule database URLs
        try:
            from .data_resolver import DataResolver
        except ImportError:
            # 如果相对导入失败，尝试绝对导入
            from data_resolver import DataResolver
        
        self.data_resolver = DataResolver(business_db_url, rule_db_url)
    
    def evaluate_expression(self, expression: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a rule expression against the provided context.
        
        Args:
            expression: Rule expression dictionary or string
            context: Context data to evaluate against
            
        Returns:
            Dictionary containing 'result' (boolean) and 'error' (optional error message)
        """
        if not expression:
            return {'result': True}
        
        try:
            # Handle string expressions (custom expressions)
            if isinstance(expression, str):
                custom_result = self._evaluate_custom_expression(expression, context)
                if isinstance(custom_result, dict):
                    return custom_result
                return {'result': bool(custom_result)}
                
            # Handle dictionary expressions
            if not isinstance(expression, dict):
                return {'result': True}
                
            # Handle custom expressions in dictionary format
            if 'custom' in expression:
                return self._evaluate_custom_expression(expression['custom'], context)
            
            # Handle simple field-value comparison
            if 'field' in expression and 'operator' in expression and 'value' in expression:
                field = expression['field']
                op = expression['operator']
                value = expression['value']
                
                # Get the actual value from context
                actual_value = self._get_field_value(field, context)
                
                # Evaluate the operation
                result = self._evaluate_operation(op, actual_value, value, context)
                return {'result': result}
            
            # Handle logical operations (and, or, not)
            if 'and' in expression:
                results = [self.evaluate_expression(expr, context) for expr in expression['and']]
                # If any sub-expression has an error, return that error
                for r in results:
                    if 'error' in r:
                        return r
                # Otherwise, return the logical AND of all results
                return {'result': all(r['result'] for r in results)}
            
            if 'or' in expression:
                results = [self.evaluate_expression(expr, context) for expr in expression['or']]
                # If any sub-expression has an error, return that error
                for r in results:
                    if 'error' in r:
                        return r
                # Otherwise, return the logical OR of all results
                return {'result': any(r['result'] for r in results)}
            
            if 'not' in expression:
                result = self.evaluate_expression(expression['not'], context)
                if 'error' in result:
                    return result
                return {'result': not result['result']}
            
            # Default to True if expression format is not recognized
            return {'result': True}
        except Exception as e:
            error_msg = str(e)
            
            # 检查是否已经是JSON格式的错误（避免重复封装）
            if error_msg.startswith('{') and error_msg.endswith('}'):
                # 已经是JSON格式，直接返回
                return {'result': False, 'error': error_msg}
            
            # 封装为JSON格式错误
            error_response = create_expression_evaluation_error_response(
                message=f"表达式评估错误: {error_msg}",
                context={"expression": expression}
            )
            
            return {'result': False, 'error': error_response.to_json()}
    
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
    
    def _evaluate_custom_expression(self, custom_expr: str, context: Dict[str, Any]) -> Any:
        substituted_expr = custom_expr  # 初始化变量
        import re  # 在函数开头导入re模块
        try:
            # 创建安全评估命名空间
            safe_globals = {
                '__builtins__': {
                    'abs': abs,
                    'len': len,
                    'int': int,
                    'float': float,
                    'str': str,
                    'bool': bool,
                    'round': round,
                    'max': max,
                    'min': min,
                    'sum': sum,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                },
                're': re
            }

            # 将上下文数据转换为更友好的类型
            converted_context = {}
            for key, value in context.items():
                if isinstance(value, str):
                    # 尝试将字符串转换为数字
                    try:
                        converted_context[key] = int(value)
                    except ValueError:
                        try:
                            converted_context[key] = float(value)
                        except ValueError:
                            # 尝试将字符串转换为布尔值
                            if value.lower() == 'true':
                                converted_context[key] = True
                            elif value.lower() == 'false':
                                converted_context[key] = False
                            else:
                                converted_context[key] = value
                elif isinstance(value, list):
                    # 如果是列表，尝试提取第一个元素
                    if len(value) == 1:
                        converted_context[key] = value[0]
                    else:
                        converted_context[key] = value
                elif isinstance(value, dict):
                    # 对于字典类型，检查是否是数据库查询结果
                    # 如果是单字段查询结果，尝试提取实际值
                    if len(value) == 1:
                        # 检查是否是常见的数据库字段名
                        first_key = list(value.keys())[0]
                        if first_key.lower() in ['id', 'count', 'sum', 'avg', 'max', 'min', 'total', 'value', 'result']:
                            converted_context[key] = value[first_key]
                        else:
                            # 对于其他情况，保持原字典
                            converted_context[key] = value
                    else:
                        # 多字段字典，保持原样
                        converted_context[key] = value
                else:
                    converted_context[key] = value

            # 创建包装后的上下文，以便支持context.field语法
            wrapped_context = {
                'context': converted_context,
                'input': converted_context
            }

            # 替换表达式中的变量占位符
            substituted_expr = self.data_resolver._replace_placeholders(custom_expr, wrapped_context)

            # 去除常见单位词，确保比较表达式可被安全评估
            for unit in ['year', 'years', 'day', 'days', 'month', 'months']:
                substituted_expr = re.sub(rf'\b{unit}\b', '', substituted_expr)
            # 规范多余空格
            substituted_expr = re.sub(r'\s+', ' ', substituted_expr).strip()

            # 如果替换后仍有占位符，尝试直接使用上下文变量
            if '{{' in substituted_expr and '}}' in substituted_expr:
                # 创建一个包含所有上下文变量的字典
                context_vars = {}
                for key, value in converted_context.items():
                    context_vars[key] = value
                
                # 使用正则表达式替换剩余的占位符
                def replace_remaining(match):
                    var_name = match.group(1)
                    # 处理context.field格式
                    if var_name.startswith('context.'):
                        field_name = var_name[8:]  # 去掉'context.'前缀
                        if field_name in context_vars:
                            return str(context_vars[field_name])
                    # 处理input.field格式
                    elif var_name.startswith('input.'):
                        field_name = var_name[6:]  # 去掉'input.'前缀
                        if field_name in context_vars:
                            return str(context_vars[field_name])
                    # 处理直接字段名
                    elif var_name in context_vars:
                        return str(context_vars[var_name])
                    return match.group(0)
                
                substituted_expr = re.sub(r'\{\{([^}]+)\}\}', replace_remaining, substituted_expr)

            # 对于简单的比较表达式，直接使用上下文变量而不是包装器
            if 'context.' in substituted_expr and any(op in substituted_expr for op in ['<=', '>=', '==', '!=', '<', '>']):
                # 提取context.field名称
                context_match = re.search(r'context\.(\w+)', substituted_expr)
                if context_match:
                    field_name = context_match.group(1)
                    if field_name in converted_context:
                        # 直接替换为实际值
                        field_value = converted_context[field_name]
                        direct_expr = substituted_expr.replace(f'context.{field_name}', str(field_value))
                        
                        # 使用eval安全评估直接表达式
                        result = eval(direct_expr, safe_globals, {})
                        return result

            # 定义上下文访问包装器类
            class ContextWrapper:
                def __init__(self, data):
                    self.__dict__['data'] = data

                def __getattr__(self, name):
                    try:
                        value = self.data[name]
                        if isinstance(value, dict):
                            return ContextWrapper(value)
                        elif isinstance(value, list):
                            return [ContextWrapper(item) if isinstance(item, dict) else item for item in value]
                        # 确保返回原始值，而不是包装对象
                        return value
                    except KeyError:
                        return None

                def __getitem__(self, key):
                    try:
                        value = self.data[key]
                        if isinstance(value, dict):
                            return ContextWrapper(value)
                        elif isinstance(value, list):
                            return [ContextWrapper(item) if isinstance(item, dict) else item for item in value]
                        # 确保返回原始值，而不是包装对象
                        return value
                    except KeyError:
                        return None
                        
                def __repr__(self):
                    return f"ContextWrapper({self.data})"

            # 定义输入访问包装器类
            class InputWrapper:
                def __init__(self, data):
                    self.__dict__['data'] = data

                def __getattr__(self, name):
                    try:
                        value = self.data[name]
                        if isinstance(value, dict):
                            return InputWrapper(value)
                        elif isinstance(value, list):
                            return [InputWrapper(item) if isinstance(item, dict) else item for item in value]
                        # 确保返回原始值，而不是包装对象
                        return value
                    except KeyError:
                        return None

                def __getitem__(self, key):
                    try:
                        value = self.data[key]
                        if isinstance(value, dict):
                            return InputWrapper(value)
                        elif isinstance(value, list):
                            return [InputWrapper(item) if isinstance(item, dict) else item for item in value]
                        # 确保返回原始值，而不是包装对象
                        return value
                    except KeyError:
                        return None
                        
                def __repr__(self):
                    return f"InputWrapper({self.data})"

            # 创建安全的上下文变量
            safe_locals = {
                'context': ContextWrapper(converted_context),
                'input': InputWrapper(converted_context)
            }

            # 使用eval安全评估表达式
            result = eval(substituted_expr, safe_globals, safe_locals)
            return result
        except Exception as e:
            msg = str(e)
            if isinstance(e, (TypeError, AttributeError, IndexError, NameError)) or 'NoneType' in msg:
                return False
            error_response = create_expression_evaluation_error_response(
                message=f"自定义表达式评估错误: {msg}",
                context={"custom_expression": custom_expr, "substituted_expr": substituted_expr}
            )
            raise Exception(error_response.to_json()) from e
    
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
        
        # Check applies_when conditions (support requires + expression)
        applies_when = rule_set.get('applies_when', [])
        if applies_when is None:
            applies_when = []
        if applies_when:
            for condition in applies_when:
                if not isinstance(condition, dict):
                    continue
                # If condition provides requires + expression, resolve then evaluate
                cond_requires = condition.get('requires', [])
                cond_expr = condition.get('expression')
                cond_message = condition.get('message') or '规则集前置条件不满足'
                cond_id = condition.get('id', 'applies_condition')
                
                if cond_requires and cond_expr:
                    # Build a dedicated condition context based on the incoming context
                    condition_context = dict(context)
                    source_priority = {'function': 0, 'local': 1, 'context': 2, 'rule_db': 3, 'db': 4, 'api': 5}
                    cond_requires = sorted(cond_requires, key=lambda r: source_priority.get(r.get('source', 'context'), 9))
                    try:
                        for req in cond_requires:
                            if isinstance(req, dict) and 'name' in req:
                                if 'type' not in req:
                                    req['type'] = 'context'
                                req_result = self.data_resolver.resolve_data(req, condition_context)
                                if req_result is not None:
                                    condition_context[req['name']] = req_result
                        # Evaluate expression
                        passed = self.evaluate_expression(cond_expr, condition_context)
                        if not passed.get('result', False):
                            return {
                                'pass': False,
                                'violations': [{
                                    'id': cond_id,
                                    'pass': False,
                                    'message': cond_message,
                                }],
                                'results': [{
                                    'id': cond_id,
                                    'pass': False,
                                    'message': cond_message,
                                }],
                                'rule_set_id': rule_set.get('id'),
                                'rule_set_name': rule_set.get('name'),
                                'on_fail': rule_set.get('on_fail', {'action': 'block', 'notify': ['user']}),
                                'applies': False
                            }
                    except Exception as e:
                        # Treat condition evaluation failure as not applicable
                        return {
                            'pass': False,
                            'violations': [{
                                'id': cond_id,
                                'pass': False,
                                'message': cond_message,
                            }],
                            'results': [{
                                'id': cond_id,
                                'pass': False,
                                'message': cond_message,
                            }],
                            'rule_set_id': rule_set.get('id'),
                            'rule_set_name': rule_set.get('name'),
                            'on_fail': rule_set.get('on_fail', {'action': 'block', 'notify': ['user']}),
                            'applies': False
                        }
                else:
                    # Backward compatible: field/operator/value
                    field = condition.get('field')
                    operator = condition.get('operator')
                    value = condition.get('value')
                    if field and operator and value is not None:
                        actual_value = self.data_resolver.resolve_data({'name': 'field_value', 'source': 'context', 'field': field}, context)
                        if not self._evaluate_operation(operator, actual_value, value, context):
                            return {
                                'pass': False,
                                'violations': [{
                                    'id': cond_id,
                                    'pass': False,
                                    'message': cond_message,
                                }],
                                'results': [{
                                    'id': cond_id,
                                    'pass': False,
                                    'message': cond_message,
                                }],
                                'rule_set_id': rule_set.get('id'),
                                'rule_set_name': rule_set.get('name'),
                                'on_fail': rule_set.get('on_fail', {'action': 'block', 'notify': ['user']}),
                                'applies': False
                            }
        
        # Resolve any required data for the rule set
        resolved_context = dict(context)
        
        # Initialize results list early to capture any database errors
        results = []
        
        # Add any additional data required by the rules
        requires = rule_set.get('requires', [])
        if requires:
            source_priority = {'function': 0, 'local': 1, 'context': 2, 'rule_db': 3, 'db': 4, 'api': 5}
            requires = sorted(requires, key=lambda r: source_priority.get(r.get('source', 'context'), 9))
            for req in requires:
                if isinstance(req, dict) and 'name' in req:
                    # Ensure the request has a type, default to 'context' if not specified
                    if 'type' not in req:
                        req['type'] = 'context'
                    try:
                        req_result = self.data_resolver.resolve_data(req, context)
                        if req_result is not None:
                            resolved_context[req['name']] = req_result
                    except Exception as e:
                        # If there's an error resolving required data, add it to the context as an error
                        resolved_context[req['name']] = None
                        error_message = str(e)
                        
                        # 检查是否已经是JSON格式的错误（避免重复封装）
                        if not (error_message.startswith('{') and error_message.endswith('}')):
                            # 封装为JSON格式错误
                            if any(keyword in error_message.lower() for keyword in ['no such table']):
                                error_response = create_database_table_not_found_response(
                                    message=f"数据库表不存在错误: {error_message}",
                                    context={"requirement": req}
                                )
                            elif any(keyword in error_message.lower() for keyword in ['connection', 'can\'t connect']):
                                error_response = create_database_connection_error_response(
                                    message=f"数据库连接错误: {error_message}",
                                    context={"requirement": req}
                                )
                            else:
                                error_response = create_database_error_response(
                                    message=f"数据库错误: {error_message}",
                                    context={"requirement": req}
                                )
                            error_message = error_response.to_json()
                        
                        # Check if this is a database error and add a special rule violation
                        if any(keyword in error_message.lower() for keyword in ['database', 'sqlite', 'mysql', 'postgresql', 'no such table', 'connection']):
                            # Add a direct violation to the results
                            results.append({
                                'id': f"db_error_{req['name']}",
                                'pass': False,
                                'message': f"数据库错误: {error_message}",
                                'type': 'database_error',
                                'details': error_message
                            })
                        # Continue processing other requirements
        
        # Evaluate each rule in the rule set
        for rule in rule_set['rules']:
            if not isinstance(rule, dict):
                continue
                
            rule_id = rule.get('id', 'unknown')
            rule_expression = rule.get('expression', {})
            rule_message = rule.get('message', 'Rule failed')
            
            try:
                # Create a rule-specific context with resolved data
                rule_context = dict(resolved_context)
                
                # Resolve any required data for this specific rule
                rule_requires = rule.get('requires', [])
                if rule_requires:
                    # 优先解析非数据库来源，保证占位符有值
                    source_priority = {'function': 0, 'local': 1, 'context': 2, 'rule_db': 3, 'db': 4, 'api': 5}
                    rule_requires = sorted(rule_requires, key=lambda r: source_priority.get(r.get('source', 'context'), 9))
                    for req in rule_requires:
                        if isinstance(req, dict) and 'name' in req:
                            # Ensure the request has a type, default to 'context' if not specified
                            if 'type' not in req:
                                req['type'] = 'context'
                            try:
                                req_result = self.data_resolver.resolve_data(req, rule_context)
                                if req_result is not None:
                                    rule_context[req['name']] = req_result
                            except Exception as e:
                                # If there's an error resolving required data, add it to the context as an error
                                rule_context[req['name']] = None
                                error_message = str(e)
                                
                                # 检查是否已经是JSON格式的错误（避免重复封装）
                                if not (error_message.startswith('{') and error_message.endswith('}')):
                                    # 封装为JSON格式错误
                                    if any(keyword in error_message.lower() for keyword in ['no such table']):
                                        error_response = create_database_table_not_found_response(
                                            message=f"数据库表不存在错误: {error_message}",
                                            context={"rule_id": rule_id, "rule": rule}
                                        )
                                    elif any(keyword in error_message.lower() for keyword in ['connection', 'can\'t connect']):
                                        error_response = create_database_connection_error_response(
                                            message=f"数据库连接错误: {error_message}",
                                            context={"rule_id": rule_id, "rule": rule}
                                        )
                                    elif any(keyword in error_message.lower() for keyword in ['expression', 'syntax']):
                                        error_response = create_expression_evaluation_error_response(
                                            message=f"表达式评估错误: {error_message}",
                                            context={"rule_id": rule_id, "rule": rule}
                                        )
                                    else:
                                        error_response = create_expression_evaluation_error_response(
                                            message=f"规则评估错误: {error_message}",
                                            context={"rule_id": rule_id, "rule": rule}
                                        )
                                    error_message = error_response.to_json()
                                
                                results.append({
                                    'id': rule_id,
                                    'pass': False,
                                    'message': f"规则评估错误: {error_message}",
                                    'type': 'rule_evaluation_error',
                                    'details': error_message
                                })
                                # Check if the error is related to database resolution
                                if any(keyword in error_message.lower() for keyword in ['database', 'sqlite', 'mysql', 'postgresql', 'no such table', 'connection']):
                                    message = f"数据库错误: {error_message}"
                                    error_type = 'database_error'
                                else:
                                    message = f"表达式评估错误: {error_message}"
                                    error_type = 'expression_error'
                                
                                results.append({
                                    'id': rule_id,
                                    'pass': False,
                                    'message': message,
                                    'type': error_type,
                                    'details': error_message
                                })
                                continue
                
                passed = self.evaluate_expression(rule_expression, rule_context)
                
                # Check if the expression evaluation had an error
                if 'error' in passed:
                    error_message = passed['error']
                    
                    # 检查是否已经是JSON格式的错误（避免重复封装）
                    if not (error_message.startswith('{') and error_message.endswith('}')):
                        # 封装为JSON格式错误
                        if any(keyword in error_message.lower() for keyword in ['no such table']):
                            error_response = create_database_table_not_found_response(
                                message=f"数据库表不存在错误: {error_message}",
                                context={"rule_id": rule_id, "expression": rule_expression}
                            )
                        elif any(keyword in error_message.lower() for keyword in ['connection', 'can\'t connect']):
                            error_response = create_database_connection_error_response(
                                message=f"数据库连接错误: {error_message}",
                                context={"rule_id": rule_id, "expression": rule_expression}
                            )
                        elif any(keyword in error_message.lower() for keyword in ['expression', 'syntax']):
                            error_response = create_expression_evaluation_error_response(
                                message=f"表达式评估错误: {error_message}",
                                context={"rule_id": rule_id, "expression": rule_expression}
                            )
                        else:
                            error_response = create_expression_evaluation_error_response(
                                message=f"规则评估错误: {error_message}",
                                context={"rule_id": rule_id, "expression": rule_expression}
                            )
                        error_message = error_response.to_json()
                    
                    # Check if the error is related to database resolution
                    if any(keyword in error_message.lower() for keyword in ['database', 'sqlite', 'mysql', 'postgresql', 'no such table', 'connection']):
                        message = f"数据库错误: {error_message}"
                        error_type = 'database_error'
                    else:
                        message = f"表达式评估错误: {error_message}"
                        error_type = 'expression_error'
                    
                    results.append({
                        'id': rule_id,
                        'pass': False,
                        'message': message,
                        'type': error_type,
                        'details': error_message
                    })
                    continue
                
                # Use the result from the expression evaluation
                rule_passed = passed['result']
                results.append({
                    'id': rule_id,
                    'pass': rule_passed,
                    'message': rule_message if not rule_passed else None
                })
            except Exception as e:
                error_message = str(e)
                
                # 检查是否已经是JSON格式的错误（避免重复封装）
                if not (error_message.startswith('{') and error_message.endswith('}')):
                    # 封装为JSON格式错误
                    if any(keyword in error_message.lower() for keyword in ['no such table']):
                        error_response = create_database_table_not_found_response(
                            message=f"数据库表不存在错误: {error_message}",
                            context={"rule_id": rule_id, "rule": rule}
                        )
                    elif any(keyword in error_message.lower() for keyword in ['connection', 'can\'t connect']):
                        error_response = create_database_connection_error_response(
                            message=f"数据库连接错误: {error_message}",
                            context={"rule_id": rule_id, "rule": rule}
                        )
                    elif any(keyword in error_message.lower() for keyword in ['expression', 'syntax']):
                        error_response = create_expression_evaluation_error_response(
                            message=f"表达式评估错误: {error_message}",
                            context={"rule_id": rule_id, "rule": rule}
                        )
                    else:
                        error_response = create_expression_evaluation_error_response(
                            message=f"规则评估错误: {error_message}",
                            context={"rule_id": rule_id, "rule": rule}
                        )
                    error_message = error_response.to_json()
                
                results.append({
                    'id': rule_id,
                    'pass': False,
                    'message': f"规则评估错误: {error_message}",
                    'type': 'rule_evaluation_error',
                    'details': error_message
                })
        
        # Determine overall result
        violations = [r for r in results if not r['pass']]
        overall_pass = len(violations) == 0
        
        return {
            'pass': overall_pass,
            'violations': violations,
            'results': results,
            'rule_set_id': rule_set.get('id'),
            'rule_set_name': rule_set.get('name'),
            'on_fail': rule_set.get('on_fail', {'action': 'block', 'notify': ['user']}),
            'applies': True
        }


# Global rule engine instance
rule_engine = RuleEngine()


def execute_rule_set(rule_set: Dict[str, Any], context: Dict[str, Any], business_db_url: Optional[str] = None, rule_db_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute a rule set against the provided context.
    
    Args:
        rule_set: Rule set data dictionary
        context: Context data to evaluate against
        business_db_url: Optional business database connection URL
        rule_db_url: Optional rule database connection URL
        
    Returns:
        Dictionary containing execution results
    """
    # If a business_db_url is provided, create a new rule engine instance with it
    if business_db_url or rule_db_url:
        engine = RuleEngine(business_db_url, rule_db_url)
        return engine.execute_rule_set(rule_set, context)
    else:
        # Use the global rule engine instance
        return rule_engine.execute_rule_set(rule_set, context)