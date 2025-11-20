#!/usr/bin/env python3
"""
测试各种数据库错误情况
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 使用importlib动态导入模块
import importlib.util

# 导入data_resolver模块
data_resolver_spec = importlib.util.spec_from_file_location("data_resolver", "./provider/data_resolver.py")
data_resolver_module = importlib.util.module_from_spec(data_resolver_spec)
data_resolver_spec.loader.exec_module(data_resolver_module)

# 导入rule_engine模块
rule_engine_spec = importlib.util.spec_from_file_location("rule_engine", "./provider/rule_engine.py")
rule_engine_module = importlib.util.module_from_spec(rule_engine_spec)
rule_engine_spec.loader.exec_module(rule_engine_module)

# 使用导入的模块
DataResolver = data_resolver_module.DataResolver
RuleEngine = rule_engine_module.RuleEngine

def test_missing_table():
    """测试数据表不存在的情况"""
    print("测试1: 数据表不存在的情况...")
    
    # 创建规则引擎实例，使用一个不存在的数据库文件
    engine = RuleEngine("sqlite:///tests/test_business.db")
    
    # 测试规则配置 - 查询不存在的表
    rule = {
        "id": "d4e6f7a8-9b0c-4d1e-8f2a-3b4c5d6e7f8g",
        "name": "Yearly Consumption Limit",
        "description": "限制用户一年内的消费次数",
        "applies_when": [],
        "requires": [
            {
                "name": "consumption_count",
                "source": "db",
                "type": "database",
                "query": "SELECT COUNT(*) FROM non_existent_table WHERE user_id = {{input.user_id}} AND date >= date('now', '-1 year')"
            }
        ],
        "rules": [
            {
                "id": "d4e6f7a8-9b0c-4d1e-8f2a-3b4c5d6e7f8g",
                "expression": "context.consumption_count <= 3",
                "message": "一年内消费次数不能超过三次。"
            }
        ],
        "on_fail": {
            "action": "block",
            "notify": ["user"]
        }
    }
    
    # 测试上下文
    context = {"user_id": 1}
    
    # 执行规则集
    result = engine.execute_rule_set(rule, context)
    
    print(f"规则执行结果: {result}")
    
    # 检查结果
    if not result['pass'] and len(result['violations']) > 0:
        # 查找数据库错误
        db_error_found = False
        for violation in result['violations']:
            message = violation.get('message', '')
            if '数据库错误' in message and 'no such table: non_existent_table' in message:
                db_error_found = True
                break
        
        if db_error_found:
            print("✓ 测试1通过: 数据表不存在错误正确暴露（直接暴露）")
            return True
        else:
            print(f"✗ 测试1失败: 数据表不存在错误未正确暴露")
            print(f"违规项: {result['violations']}")
            return False
    else:
        print("✗ 测试1失败: 规则执行结果不符合预期")
        return False

def test_invalid_sql():
    """测试无效SQL语句的情况"""
    print("\n测试2: 无效SQL语句的情况...")
    
    # 创建规则引擎实例
    engine = RuleEngine("sqlite:///tests/test_business.db")
    
    # 测试规则配置 - 使用无效SQL
    rule = {
        "id": "d4e6f7a8-9b0c-4d1e-8f2a-3b4c5d6e7f8g",
        "name": "Invalid SQL Test",
        "description": "测试无效SQL语句",
        "applies_when": [],
        "requires": [
            {
                "name": "invalid_result",
                "source": "db",
                "type": "database",
                "query": "SELECT COUNT(*) FROM invalid_table WHERE invalid_column = 'invalid'"
            }
        ],
        "rules": [
            {
                "id": "d4e6f7a8-9b0c-4d1e-8f2a-3b4c5d6e7f8g",
                "expression": "context.invalid_result > 0",
                "message": "测试无效SQL"
            }
        ],
        "on_fail": {
            "action": "block",
            "notify": ["user"]
        }
    }
    
    # 测试上下文
    context = {"user_id": 1}
    
    # 执行规则集
    result = engine.execute_rule_set(rule, context)
    
    print(f"规则执行结果: {result}")
    
    # 检查结果
    if not result['pass'] and len(result['violations']) > 0:
        violation = result['violations'][0]
        message = violation.get('message', '')
        if '数据库错误' in message and 'no such table: invalid_table' in message:
            print("✓ 测试2通过: 无效SQL错误正确暴露（直接暴露）")
            return True
        else:
            print(f"✗ 测试2失败: 无效SQL错误未正确暴露，消息: {message}")
            return False
    else:
        print("✗ 测试2失败: 规则执行结果不符合预期")
        return False

def test_rule_level_db_error():
    """测试规则级别的数据库错误"""
    print("\n测试3: 规则级别的数据库错误...")
    
    # 创建规则引擎实例
    engine = RuleEngine("sqlite:///tests/test_business.db")
    
    # 测试规则配置 - 规则级别的数据库错误
    rule = {
        "id": "d4e6f7a8-9b0c-4d1e-8f2a-3b4c5d6e7f8g",
        "name": "Rule Level DB Error Test",
        "description": "测试规则级别的数据库错误",
        "applies_when": [],
        "requires": [],  # 规则集级别没有数据库依赖
        "rules": [
            {
                "id": "d4e6f7a8-9b0c-4d1e-8f2a-3b4c5d6e7f8g",
                "expression": "context.rule_level_result > 0",
                "message": "测试规则级别的数据库错误",
                "requires": [  # 规则级别的数据库依赖
                    {
                        "name": "rule_level_result",
                        "source": "db",
                        "type": "database",
                        "query": "SELECT COUNT(*) FROM rule_level_table WHERE id = {{input.user_id}}"
                    }
                ]
            }
        ],
        "on_fail": {
            "action": "block",
            "notify": ["user"]
        }
    }
    
    # 测试上下文
    context = {"user_id": 1}
    
    # 执行规则集
    result = engine.execute_rule_set(rule, context)
    
    print(f"规则执行结果: {result}")
    
    # 检查结果
    if not result['pass'] and len(result['violations']) > 0:
        violation = result['violations'][0]
        message = violation.get('message', '')
        if '数据库错误' in message and 'no such table: rule_level_table' in message:
            print("✓ 测试3通过: 规则级别的数据库错误正确暴露（直接暴露）")
            return True
        else:
            print(f"✗ 测试3失败: 规则级别的数据库错误未正确暴露，消息: {message}")
            return False
    else:
        print("✗ 测试3失败: 规则执行结果不符合预期")
        return False

if __name__ == "__main__":
    test1_result = test_missing_table()
    test2_result = test_invalid_sql()
    test3_result = test_rule_level_db_error()
    
    print("\n测试总结:")
    print(f"测试1 (数据表不存在): {'通过' if test1_result else '失败'}")
    print(f"测试2 (无效SQL): {'通过' if test2_result else '失败'}")
    print(f"测试3 (规则级别数据库错误): {'通过' if test3_result else '失败'}")
    
    all_passed = test1_result and test2_result and test3_result
    print(f"\n总体结果: {'全部通过' if all_passed else '存在失败的测试'}")