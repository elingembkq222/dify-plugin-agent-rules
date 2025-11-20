#!/bin/bash
echo "运行所有测试..."

# 切换到项目根目录
cd "$(dirname "$0")/.."

echo "1. 运行自动化测试套件..."
python tests/test_automated.py
if [ $? -ne 0 ]; then
    echo "自动化测试套件失败"
    exit 1
fi

echo "2. 运行数据表不存在测试..."
python tests/test_missing_table.py
if [ $? -ne 0 ]; then
    echo "数据表不存在测试失败"
    exit 1
fi

echo "3. 运行全面数据库错误测试..."
python tests/test_comprehensive_db_errors.py
if [ $? -ne 0 ]; then
    echo "全面数据库错误测试失败"
    exit 1
fi

echo "4. 运行API测试..."
python tests/test_api.py
if [ $? -ne 0 ]; then
    echo "API测试失败"
    exit 1
fi

echo "5. 运行规则生成测试..."
python tests/test_generate_rule.py
if [ $? -ne 0 ]; then
    echo "规则生成测试失败"
    exit 1
fi

echo "6. 运行UUID生成测试..."
python tests/test_uuid_generation.py
if [ $? -ne 0 ]; then
    echo "UUID生成测试失败"
    exit 1
fi

echo "7. 运行UUID验证测试..."
python tests/test_uuid_validation.py
if [ $? -ne 0 ]; then
    echo "UUID验证测试失败"
    exit 1
fi

echo "所有测试完成！"
exit 0