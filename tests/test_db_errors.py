#!/usr/bin/env python3
"""
测试数据库错误处理脚本
验证不同数据库类型的连接错误和表不存在错误是否被正确识别
"""

import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from provider.data_resolver import DataResolver

def test_sqlite_errors():
    """测试SQLite错误处理"""
    print("=== 测试SQLite错误处理 ===")
    resolver = DataResolver()
    
    # 测试1: 连接不存在的数据库文件
    print("\n1. 测试连接不存在的数据库文件")
    try:
        result = resolver._query_sqlite('SELECT * FROM test_table', 'sqlite:///non_existent.db')
        print(f"结果: {result}")
    except Exception as e:
        print(f"错误: {str(e)}")
        assert "数据库连接错误" in str(e), "应该返回数据库连接错误"
    
    # 测试2: 连接存在的数据库但查询不存在的表
    print("\n2. 测试连接存在的数据库但查询不存在的表")
    try:
        # 先创建一个空的数据库文件
        import sqlite3
        empty_db_path = "empty_test.db"
        if os.path.exists(empty_db_path):
            os.remove(empty_db_path)
        conn = sqlite3.connect(empty_db_path)
        conn.close()
        
        result = resolver._query_sqlite('SELECT * FROM non_existent_table', f'sqlite:///{empty_db_path}')
        print(f"结果: {result}")
    except Exception as e:
        print(f"错误: {str(e)}")
        assert "数据库表不存在错误" in str(e), "应该返回数据库表不存在错误"
    finally:
        # 清理测试文件
        if os.path.exists(empty_db_path):
            os.remove(empty_db_path)

def test_mysql_errors():
    """测试MySQL错误处理"""
    print("\n=== 测试MySQL错误处理 ===")
    resolver = DataResolver()
    
    # 测试1: 连接不存在的MySQL服务器
    print("\n1. 测试连接不存在的MySQL服务器")
    try:
        result = resolver._query_mysql('SELECT * FROM test_table', 'mysql+pymysql://user:pass@localhost:9999/nonexistent_db')
        print(f"结果: {result}")
    except Exception as e:
        print(f"错误: {str(e)}")
        assert "数据库连接错误" in str(e), "应该返回数据库连接错误"
    
    # 测试2: 连接MySQL服务器但认证失败
    print("\n2. 测试连接MySQL服务器但认证失败")
    try:
        result = resolver._query_mysql('SELECT * FROM test_table', 'mysql+pymysql://wronguser:wrongpass@localhost/test')
        print(f"结果: {result}")
    except Exception as e:
        print(f"错误: {str(e)}")
        assert "数据库连接错误" in str(e), "应该返回数据库连接错误"

def test_postgresql_errors():
    """测试PostgreSQL错误处理"""
    print("\n=== 测试PostgreSQL错误处理 ===")
    resolver = DataResolver()
    
    # 测试1: 连接不存在的PostgreSQL服务器
    print("\n1. 测试连接不存在的PostgreSQL服务器")
    try:
        result = resolver._query_postgresql('SELECT * FROM test_table', 'postgresql://user:pass@localhost:9999/nonexistent_db')
        print(f"结果: {result}")
    except Exception as e:
        print(f"错误: {str(e)}")
        assert "数据库连接错误" in str(e), "应该返回数据库连接错误"
    
    # 测试2: 连接PostgreSQL服务器但认证失败
    print("\n2. 测试连接PostgreSQL服务器但认证失败")
    try:
        result = resolver._query_postgresql('SELECT * FROM test_table', 'postgresql://wronguser:wrongpass@localhost/test')
        print(f"结果: {result}")
    except Exception as e:
        print(f"错误: {str(e)}")
        assert "数据库连接错误" in str(e), "应该返回数据库连接错误"

if __name__ == "__main__":
    print("开始测试数据库错误处理...")
    
    try:
        test_sqlite_errors()
        test_mysql_errors()
        test_postgresql_errors()
        
        print("\n=== 所有测试通过 ===")
        print("数据库错误处理能够正确区分连接错误和表不存在错误")
    except AssertionError as e:
        print(f"\n测试失败: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程中发生意外错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)