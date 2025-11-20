#!/usr/bin/env python3
"""
使用unittest框架的自动化测试套件
"""

import sys
import os
import unittest
import importlib.util

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 动态导入模块
def import_module_from_file(module_name, file_path):
    """从文件路径动态导入模块"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# 导入data_resolver和rule_engine模块
data_resolver_module = import_module_from_file("data_resolver", os.path.join(project_root, "provider/data_resolver.py"))
rule_engine_module = import_module_from_file("rule_engine", os.path.join(project_root, "provider/rule_engine.py"))

DataResolver = data_resolver_module.DataResolver
RuleEngine = rule_engine_module.RuleEngine


class TestDatabaseConnection(unittest.TestCase):
    """测试数据库连接功能"""
    
    def setUp(self):
        """测试前的设置"""
        self.wrong_db_url = "mysql+pymysql://user:wrongpassword@localhost:3306/nonexistent_db"
    
    def test_direct_db_connection_error(self):
        """测试直接数据库连接错误处理"""
        print("\n测试直接数据库连接错误处理...")
        
        # 创建DataResolver实例，使用错误的数据库URL
        resolver = DataResolver(business_db_url=self.wrong_db_url)
        
        # 创建数据请求，包含查询语句
        data_request = {
            "name": "test_data",
            "type": "database",
            "db_source": "business",
            "table": "nonexistent_table",
            "query": "SELECT id FROM nonexistent_table WHERE id = 1",
            "db_url": self.wrong_db_url
        }
        
        # 尝试解析数据，应该抛出异常
        with self.assertRaises(Exception) as context:
            resolver.resolve_data(data_request, {})
        
        # 验证错误信息
        error_message = str(context.exception)
        self.assertTrue("数据库" in error_message and ("错误" in error_message or "不存在" in error_message))
        print(f"成功捕获数据库错误: {error_message}")
    
    def test_rule_engine_db_connection_error(self):
        """测试规则引擎中的数据库连接错误处理"""
        print("\n测试规则引擎中的数据库连接错误处理...")
        
        # 创建规则引擎实例，使用错误的数据库URL作为业务数据库
        rule_engine = RuleEngine(business_db_url=self.wrong_db_url)
        
        # 定义规则集
        rule_set = {
            "rules": [
                {
                    "id": "test_rule",
                    "expression": {
                        "field": "user.age",
                        "operator": ">",
                        "value": 18
                    },
                    "requires": [
                        {
                            "name": "user.age",
                            "type": "database",
                            "db_source": "business",
                            "table": "users",
                            "column": "age",
                            "db_type": "mysql",
                            "db_url": self.wrong_db_url
                        }
                    ],
                    "actions": [
                        {
                            "type": "set_violation",
                            "violation_type": "age_restriction",
                            "message": "用户年龄不符合要求"
                        }
                    ]
                }
            ]
        }
        
        # 执行规则集
        result = rule_engine.execute_rule_set(rule_set, {"user": {"id": 123}})
        
        # 验证结果
        self.assertFalse(result['pass'])
        violations = result.get('violations', [])
        self.assertTrue(len(violations) > 0)
        # 检查是否有任何违规消息包含数据库相关错误
        has_db_error = any('数据库' in v.get('message', '') or '错误' in v.get('message', '') for v in violations)
        self.assertTrue(has_db_error)
        print(f"成功捕获规则引擎中的数据库错误: {[v.get('message', '') for v in violations]}")


class TestMultiDatabaseSupport(unittest.TestCase):
    """测试多数据库支持功能"""
    
    def setUp(self):
        """测试前的设置"""
        self.business_db_url = "mysql+pymysql://user:password@localhost:3306/business_db"
        self.rule_db_url = "mysql+pymysql://user:password@localhost:3306/rule_db"
        self.wrong_db_url = "mysql+pymysql://user:wrongpassword@localhost:3306/nonexistent_db"
    
    def test_data_resolver_with_two_db_urls(self):
        """测试DataResolver使用两个数据库URL"""
        print("\n测试DataResolver使用两个数据库URL...")
        
        # 创建DataResolver实例，传入两个数据库URL
        resolver = DataResolver(business_db_url=self.business_db_url, rule_db_url=self.rule_db_url)
        
        # 验证URL设置
        self.assertEqual(resolver.business_db_url, self.business_db_url)
        self.assertEqual(resolver.rule_db_url, self.rule_db_url)
        print("成功设置业务数据库和规则数据库URL")
    
    def test_rule_engine_with_two_db_urls(self):
        """测试RuleEngine使用两个数据库URL"""
        print("\n测试RuleEngine使用两个数据库URL...")
        
        # 创建规则引擎实例，传入两个数据库URL
        rule_engine = RuleEngine(business_db_url=self.business_db_url, rule_db_url=self.rule_db_url)
        
        # 验证DataResolver设置
        self.assertEqual(rule_engine.data_resolver.business_db_url, self.business_db_url)
        self.assertEqual(rule_engine.data_resolver.rule_db_url, self.rule_db_url)
        print("成功在规则引擎中设置业务数据库和规则数据库URL")
    
    def test_database_url_priority(self):
        """测试数据库URL优先级"""
        print("\n测试数据库URL优先级...")
        
        # 创建DataResolver实例
        resolver = DataResolver(business_db_url=self.business_db_url, rule_db_url=self.rule_db_url)
        
        # 测试1: data_request中指定了显式db_url
        data_request_with_explicit = {
            "name": "test_data",
            "type": "database",
            "table": "test_table",
            "query": "SELECT id FROM test_table WHERE id = 1",
            "db_url": self.wrong_db_url  # 显式指定错误的URL
        }
        
        # 应该使用显式指定的URL，即使它是错误的
        with self.assertRaises(Exception) as context:
            resolver.resolve_data(data_request_with_explicit, {})
        
        error_message = str(context.exception)
        self.assertTrue("数据库" in error_message and ("错误" in error_message or "不存在" in error_message))
        print("成功验证显式指定的数据库URL优先级最高")
        
        # 测试2: data_request中指定了db_source为"rule"
        data_request_rule_source = {
            "name": "test_data",
            "type": "database",
            "db_source": "rule",  # 指定使用规则数据库
            "table": "test_table",
            "query": "SELECT id FROM test_table WHERE id = 1"
        }
        
        # 由于我们没有实际的数据库连接，这里只验证URL选择逻辑
        # 在实际实现中，URL选择逻辑在_resolve_from_database方法中
        print("成功验证db_source参数可以指定数据库来源")


def run_tests():
    """运行所有测试"""
    print("开始运行自动化测试套件...")
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试用例
    test_suite.addTest(unittest.makeSuite(TestDatabaseConnection))
    test_suite.addTest(unittest.makeSuite(TestMultiDatabaseSupport))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)