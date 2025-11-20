# 测试列表

本文件列出了所有可用的测试脚本，方便自动化测试执行。

## 数据库错误测试

这些测试用于验证数据库错误直接暴露功能：

1. **test_missing_table.py**
   - 测试数据表不存在的情况
   - 验证数据库错误被直接暴露而不是通过表达式评估错误间接暴露
   - 运行方式：`python tests/test_missing_table.py`

2. **test_comprehensive_db_errors.py**
   - 全面测试各种数据库错误情况
   - 包括数据表不存在、无效SQL语句、规则级别的数据库错误等
   - 运行方式：`python tests/test_comprehensive_db_errors.py`

## API测试

3. **test_api.py**
   - 测试API接口功能
   - 运行方式：`python tests/test_api.py`

## 规则生成测试

4. **test_generate_rule.py**
   - 测试规则生成功能
   - 运行方式：`python tests/test_generate_rule.py`

## UUID测试

5. **test_uuid_generation.py**
   - 测试UUID生成功能
   - 运行方式：`python tests/test_uuid_generation.py`

6. **test_uuid_validation.py**
   - 测试UUID验证功能
   - 运行方式：`python tests/test_uuid_validation.py`

## 文档

7. **DATABASE_ERROR_DIRECT_EXPOSURE.md**
   - 数据库错误直接暴露功能的详细文档
   - 包括修改概述、修改内容、测试验证和效果对比

## 自动化测试脚本

可以使用以下脚本运行测试：

### 数据库错误测试脚本

运行所有数据库错误相关测试：

```bash
./tests/run_db_tests.sh
```

### 全部测试脚本

运行所有测试（包括需要服务器的API测试）：

```bash
./tests/run_all_tests.sh
```

### 手动运行所有测试

```bash
#!/bin/bash
echo "运行所有测试..."

echo "1. 运行数据表不存在测试..."
python tests/test_missing_table.py

echo "2. 运行全面数据库错误测试..."
python tests/test_comprehensive_db_errors.py

echo "3. 运行API测试..."
python tests/test_api.py

echo "4. 运行规则生成测试..."
python tests/test_generate_rule.py

echo "5. 运行UUID生成测试..."
python tests/test_uuid_generation.py

echo "6. 运行UUID验证测试..."
python tests/test_uuid_validation.py

echo "所有测试完成！"
```

## 注意事项

1. 运行测试前请确保已安装所有依赖：`pip install -r requirements.txt`
2. 确保数据库文件存在且可访问
3. 某些测试可能需要特定的数据库配置，请参考相关文档