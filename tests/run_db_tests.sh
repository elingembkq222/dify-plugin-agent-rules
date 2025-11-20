#!/bin/bash
echo "运行数据库错误相关测试..."

# 切换到项目根目录
cd "$(dirname "$0")/.."

echo "1. 运行数据表不存在测试..."
python tests/test_missing_table.py
if [ $? -ne 0 ]; then
    echo "数据表不存在测试失败"
    exit 1
fi

echo "2. 运行全面数据库错误测试..."
python tests/test_comprehensive_db_errors.py
if [ $? -ne 0 ]; then
    echo "全面数据库错误测试失败"
    exit 1
fi

echo "数据库错误相关测试完成！"
exit 0