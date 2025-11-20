#!/usr/bin/env python3
"""
测试用户报告的问题：数据表不存在
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
    print("测试数据表不存在的情况...")
    
    # 创建规则引擎实例，使用一个不存在的数据库文件
    engine = RuleEngine("sqlite:///test_business.db")
    
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
        violation = result['violations'][0]
        message = violation.get('message', '')
        if '表达式评估错误' in message and "'<=' not supported between instances of 'NoneType' and 'int'" in message:
            print("✓ 测试通过: 数据表不存在错误正确暴露（通过表达式评估错误间接暴露）")
            return True
        elif '数据库错误' in message:
            print("✓ 测试通过: 数据表不存在错误正确暴露（直接暴露）")
            return True
        else:
            print(f"✗ 测试失败: 数据表不存在错误未正确暴露，消息: {message}")
            return False
    else:
        print("✗ 测试失败: 规则执行结果不符合预期")
        return False

if __name__ == "__main__":
    test_missing_table()
    print("测试完成!")