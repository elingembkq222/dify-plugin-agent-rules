#!/usr/bin/env python3
"""
测试统一JSON格式异常处理功能
"""

import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 修改导入方式，避免相对导入问题
import importlib.util

# 导入error_handler模块
spec = importlib.util.spec_from_file_location(
    "error_handler", 
    os.path.join(os.path.dirname(__file__), '..', "provider", "error_handler.py")
)
error_handler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(error_handler)

# 导入data_resolver模块
spec = importlib.util.spec_from_file_location(
    "data_resolver", 
    os.path.join(os.path.dirname(__file__), '..', "provider", "data_resolver.py")
)
data_resolver = importlib.util.module_from_spec(spec)
# 修改data_resolver模块中的导入
data_resolver.error_handler = error_handler
spec.loader.exec_module(data_resolver)

# 导入rule_engine模块
spec = importlib.util.spec_from_file_location(
    "rule_engine", 
    os.path.join(os.path.dirname(__file__), '..', "provider", "rule_engine.py")
)
rule_engine = importlib.util.module_from_spec(spec)
# 修改rule_engine模块中的导入
rule_engine.error_handler = error_handler
spec.loader.exec_module(rule_engine)

# 从模块中导入需要的类和函数
DataResolver = data_resolver.DataResolver
RuleEngine = rule_engine.RuleEngine
execute_rule_set = rule_engine.execute_rule_set

create_database_connection_error_response = error_handler.create_database_connection_error_response
create_database_table_not_found_response = error_handler.create_database_table_not_found_response
create_database_error_response = error_handler.create_database_error_response
create_expression_error_response = error_handler.create_expression_error_response
create_rule_evaluation_error_response = error_handler.create_rule_evaluation_error_response


class TestJSONErrorHandling(unittest.TestCase):
    """测试JSON格式异常处理"""
    
    def setUp(self):
        """设置测试环境"""
        self.business_db_url = "sqlite:///tests/test_business.db"
        self.rule_db_url = "sqlite:///tests/rule_engine.db"
        self.data_resolver = DataResolver(self.business_db_url, self.rule_db_url)
        self.rule_engine = RuleEngine(self.business_db_url, self.rule_db_url)
    
    def test_database_connection_error_response(self):
        """测试数据库连接错误响应"""
        error_response = create_database_connection_error_response(
            message="无法连接到数据库",
            context={"test": "context"}
        )
        
        # 验证响应结构
        self.assertEqual(error_response.error_type, "database_connection_error")
        self.assertEqual(error_response.message, "无法连接到数据库")
        self.assertEqual(error_response.context["test"], "context")
        
        # 验证JSON格式
        json_str = error_response.to_json()
        self.assertTrue(json_str.startswith('{'))
        self.assertTrue(json_str.endswith('}'))
        
        # 验证可以解析回对象
        parsed = json.loads(json_str)
        self.assertEqual(parsed["error_type"], "database_connection_error")
        self.assertEqual(parsed["message"], "无法连接到数据库")
    
    def test_database_table_not_found_response(self):
        """测试数据库表不存在错误响应"""
        error_response = create_database_table_not_found_response(
            message="表不存在",
            context={"table": "non_existent_table"}
        )
        
        # 验证响应结构
        self.assertEqual(error_response.error_type, "database_table_not_found")
        self.assertEqual(error_response.message, "表不存在")
        
        # 验证JSON格式
        json_str = error_response.to_json()
        parsed = json.loads(json_str)
        self.assertEqual(parsed["error_type"], "database_table_not_found")
    
    def test_expression_error_response(self):
        """测试表达式错误响应"""
        error_response = create_expression_error_response(
            message="表达式语法错误",
            context={"expression": "invalid expr"}
        )
        
        # 验证响应结构
        self.assertEqual(error_response.error_type, "expression_error")
        self.assertEqual(error_response.message, "表达式语法错误")
        
        # 验证JSON格式
        json_str = error_response.to_json()
        parsed = json.loads(json_str)
        self.assertEqual(parsed["error_type"], "expression_error")
    
    def test_rule_evaluation_error_response(self):
        """测试规则评估错误响应"""
        error_response = create_rule_evaluation_error_response(
            message="规则评估失败",
            context={"rule_id": "test_rule"}
        )
        
        # 验证响应结构
        self.assertEqual(error_response.error_type, "rule_evaluation_error")
        self.assertEqual(error_response.message, "规则评估失败")
        
        # 验证JSON格式
        json_str = error_response.to_json()
        parsed = json.loads(json_str)
        self.assertEqual(parsed["error_type"], "rule_evaluation_error")
    
    def test_data_resolver_database_error_handling(self):
        """测试DataResolver中的数据库错误处理"""
        # 使用不存在的数据库URL测试连接错误
        resolver = DataResolver("sqlite:///tests/non_existent_path/non_existent.db", None)
        
        # 尝试查询应该返回JSON格式的错误
        result = resolver.resolve_data({
            'name': 'test',
            'source': 'database',
            'type': 'postgresql',
            'query': 'SELECT * FROM test'
        }, {})
        
        # 验证错误是JSON格式
        self.assertTrue(isinstance(result, str))
        self.assertTrue(result.startswith('{'))
        self.assertTrue(result.endswith('}'))
        
        # 验证可以解析
        parsed = json.loads(result)
        self.assertEqual(parsed["error_type"], "database_connection_error")
    
    def test_data_resolver_table_not_found_handling(self):
        """测试DataResolver中的表不存在错误处理"""
        # 尝试查询不存在的表
        result = self.data_resolver.resolve_data({
            'name': 'test',
            'source': 'database',
            'type': 'sqlite',
            'query': 'SELECT * FROM non_existent_table'
        }, {})
        
        # 验证错误是JSON格式
        self.assertTrue(isinstance(result, str))
        self.assertTrue(result.startswith('{'))
        self.assertTrue(result.endswith('}'))
        
        # 验证可以解析
        parsed = json.loads(result)
        self.assertEqual(parsed["error_type"], "database_table_not_found")
    
    def test_rule_engine_expression_error_handling(self):
        """测试RuleEngine中的表达式错误处理"""
        # 测试无效的表达式
        result = self.rule_engine.evaluate_expression({
            'operator': 'invalid_operator',
            'left': {'field': 'test'},
            'right': 'value'
        }, {})
        
        # 验证错误是JSON格式
        self.assertTrue(isinstance(result, dict))
        self.assertIn('error', result)
        self.assertTrue(result['error'].startswith('{'))
        self.assertTrue(result['error'].endswith('}'))
        
        # 验证可以解析
        parsed = json.loads(result['error'])
        self.assertEqual(parsed["error_type"], "expression_error")
    
    def test_rule_engine_rule_evaluation_error_handling(self):
        """测试RuleEngine中的规则评估错误处理"""
        # 创建一个会导致错误的规则集
        rule_set = {
            'id': 'test_rule_set',
            'name': 'Test Rule Set',
            'rules': [
                {
                    'id': 'test_rule',
                    'expression': {
                        'operator': 'invalid_operator',
                        'left': {'field': 'test'},
                        'right': 'value'
                    },
                    'message': 'Test rule failed'
                }
            ]
        }
        
        # 执行规则集
        result = self.rule_engine.execute_rule_set(rule_set, {})
        
        # 验证结果包含错误
        self.assertFalse(result['pass'])
        self.assertEqual(len(result['violations']), 1)
        
        # 验证错误是JSON格式
        violation = result['violations'][0]
        self.assertTrue(isinstance(violation['details'], str))
        self.assertTrue(violation['details'].startswith('{'))
        self.assertTrue(violation['details'].endswith('}'))
        
        # 验证可以解析
        parsed = json.loads(violation['details'])
        self.assertEqual(parsed["error_type"], "expression_error")
    
    def test_execute_rule_set_database_error_handling(self):
        """测试execute_rule_set函数中的数据库错误处理"""
        # 创建一个包含数据库查询的规则集
        rule_set = {
            'id': 'test_rule_set',
            'name': 'Test Rule Set',
            'requires': [
                {
                    'name': 'db_data',
                    'source': 'database',
                    'type': 'sqlite',
                    'query': 'SELECT * FROM non_existent_table'
                }
            ],
            'rules': [
                {
                    'id': 'test_rule',
                    'expression': {
                        'operator': 'equals',
                        'left': {'field': 'db_data'},
                        'right': 'value'
                    },
                    'message': 'Test rule failed'
                }
            ]
        }
        
        # 执行规则集
        result = execute_rule_set(rule_set, {}, self.business_db_url, self.rule_db_url)
        
        # 验证结果包含错误
        self.assertFalse(result['pass'])
        self.assertEqual(len(result['violations']), 1)
        
        # 验证错误是JSON格式
        violation = result['violations'][0]
        self.assertTrue(isinstance(violation['details'], str))
        self.assertTrue(violation['details'].startswith('{'))
        self.assertTrue(violation['details'].endswith('}'))
        
        # 验证可以解析
        parsed = json.loads(violation['details'])
        self.assertEqual(parsed["error_type"], "database_table_not_found")
    
    def test_no_duplicate_json_wrapping(self):
        """测试避免重复JSON封装"""
        # 创建一个已经是JSON格式的错误
        original_error = json.dumps({
            "error_type": "database_error",
            "message": "原始错误",
            "context": {}
        })
        
        # 模拟DataResolver处理已经是JSON格式的错误
        with patch.object(self.data_resolver, '_resolve_from_database') as mock_resolve:
            mock_resolve.side_effect = Exception(original_error)
            
            result = self.data_resolver.resolve_data({
                'name': 'test',
                'source': 'database',
                'type': 'sqlite',
                'query': 'SELECT * FROM test'
            }, {})
            
            # 验证结果没有重复封装
            self.assertEqual(result, original_error)
            
            # 验证可以解析
            parsed = json.loads(result)
            self.assertEqual(parsed["error_type"], "database_error")
            self.assertEqual(parsed["message"], "原始错误")


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)