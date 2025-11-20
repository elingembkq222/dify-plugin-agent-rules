# 测试目录

本目录包含了项目的所有测试文件和测试文档。

## 快速开始

### 运行数据库错误相关测试

```bash
./tests/run_db_tests.sh
```

### 运行所有测试

```bash
./tests/run_all_tests.sh
```

## 测试文件说明

- `test_missing_table.py` - 测试数据表不存在的情况
- `test_comprehensive_db_errors.py` - 全面测试各种数据库错误情况
- `test_api.py` - 测试API接口功能
- `test_generate_rule.py` - 测试规则生成功能
- `test_uuid_generation.py` - 测试UUID生成功能
- `test_uuid_validation.py` - 测试UUID验证功能

## 文档

- `DATABASE_ERROR_DIRECT_EXPOSURE.md` - 数据库错误直接暴露功能的详细文档
- `TEST_LIST.md` - 完整的测试列表和说明

## 注意事项

1. 运行测试前请确保已安装所有依赖：`pip install -r requirements.txt`
2. 确保数据库文件存在且可访问
3. API测试需要服务器运行