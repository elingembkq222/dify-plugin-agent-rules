#!/usr/bin/env python3
"""
测试统一JSON格式异常处理功能 - 简化版本
"""

import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 直接测试error_handler模块
from provider.error_handler import (
    ErrorResponse,
    ErrorType,
    create_database_connection_error_response,
    create_database_table_not_found_response,
    create_database_error_response,
    create_expression_evaluation_error_response,
    create_sql_syntax_error_response
)


class TestJSONErrorHandling(unittest.TestCase):
    """测试JSON格式异常处理"""
    
    def test_error_response_creation(self):
        """测试错误响应创建"""
        # 测试基本错误响应
        error_response = ErrorResponse(
            error_type=ErrorType.DATABASE_CONNECTION_ERROR,
            message="测试错误消息",
            context={"key": "value"}
        )
        
        # 验证响应结构
        self.assertEqual(error_response.error_type, "database_connection_error")  # error_type是字符串
        self.assertEqual(error_response.message, "测试错误消息")
        self.assertEqual(error_response.context["key"], "value")
        
        # 验证JSON格式
        json_str = error_response.to_json()
        self.assertTrue(json_str.startswith('{'))
        self.assertTrue(json_str.endswith('}'))
        
        # 验证可以解析回对象
        parsed = json.loads(json_str)
        self.assertEqual(parsed["error_type"], "database_connection_error")
        self.assertEqual(parsed["message"], "测试错误消息")
        self.assertEqual(parsed["context"]["key"], "value")
    
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
    
    def test_database_error_response(self):
        """测试数据库错误响应"""
        error_response = create_database_error_response(
            message="数据库错误",
            context={"operation": "query"}
        )
        
        # 验证响应结构
        self.assertEqual(error_response.error_type, "database_error")
        self.assertEqual(error_response.message, "数据库错误")
        
        # 验证JSON格式
        json_str = error_response.to_json()
        parsed = json.loads(json_str)
        self.assertEqual(parsed["error_type"], "database_error")
    
    def test_expression_error_response(self):
        """测试表达式错误响应"""
        error_response = create_expression_evaluation_error_response(
            message="表达式语法错误",
            context={"expression": "invalid expr"}
        )
        
        # 验证响应结构
        self.assertEqual(error_response.error_type, "expression_evaluation_error")
        self.assertEqual(error_response.message, "表达式语法错误")
        
        # 验证JSON格式
        json_str = error_response.to_json()
        parsed = json.loads(json_str)
        self.assertEqual(parsed["error_type"], "expression_evaluation_error")
    
    def test_sql_syntax_error_response(self):
        """测试SQL语法错误响应"""
        error_response = create_sql_syntax_error_response(
            message="SQL语法错误",
            context={"sql": "invalid sql"}
        )
        
        # 验证响应结构
        self.assertEqual(error_response.error_type, "sql_syntax_error")
        self.assertEqual(error_response.message, "SQL语法错误")
        
        # 验证JSON格式
        json_str = error_response.to_json()
        parsed = json.loads(json_str)
        self.assertEqual(parsed["error_type"], "sql_syntax_error")
    
    def test_json_format_consistency(self):
        """测试JSON格式一致性"""
        # 创建不同类型的错误响应
        responses = [
            create_database_connection_error_response("连接错误"),
            create_database_table_not_found_response("表不存在"),
            create_database_error_response("数据库错误"),
            create_expression_evaluation_error_response("表达式错误"),
            create_sql_syntax_error_response("SQL语法错误")
        ]
        
        # 验证所有响应都是有效的JSON
        for response in responses:
            json_str = response.to_json()
            self.assertTrue(json_str.startswith('{'))
            self.assertTrue(json_str.endswith('}'))
            
            # 验证可以解析
            parsed = json.loads(json_str)
            self.assertIn("error_type", parsed)
            self.assertIn("message", parsed)
            # context可能不存在，如果为空字典的话
            # self.assertIn("context", parsed)
    
    def test_error_type_values(self):
        """测试错误类型枚举值"""
        # 验证错误类型枚举值
        self.assertEqual(ErrorType.DATABASE_CONNECTION_ERROR.value, "database_connection_error")
        self.assertEqual(ErrorType.DATABASE_TABLE_NOT_FOUND.value, "database_table_not_found")
        self.assertEqual(ErrorType.DATABASE_ERROR.value, "database_error")
        self.assertEqual(ErrorType.EXPRESSION_EVALUATION_ERROR.value, "expression_evaluation_error")
        self.assertEqual(ErrorType.SQL_SYNTAX_ERROR.value, "sql_syntax_error")


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)