# 测试指南

本项目提供了多种测试方式，确保代码质量和功能正确性。

## 测试文件结构

```
tests/
├── run_all_tests.sh          # 运行所有测试的Shell脚本
├── test_automated.py         # 使用unittest框架的自动化测试套件
├── test_missing_table.py     # 数据表不存在测试
├── test_comprehensive_db_errors.py  # 全面数据库错误测试
├── test_api.py               # API测试
├── test_generate_rule.py     # 规则生成测试
├── test_uuid_generation.py   # UUID生成测试
└── test_uuid_validation.py   # UUID验证测试
```

## 运行测试的方法

### 1. 使用Makefile (推荐)

```bash
# 安装依赖
make install

# 运行所有测试
make test

# 运行特定测试
make test-db-connection
make test-automated
make test-coverage
```

### 2. 使用Shell脚本

```bash
# 运行所有测试
./tests/run_all_tests.sh

# 运行特定测试
python tests/test_automated.py
```

### 3. 使用Python unittest

```bash
# 运行自动化测试套件
python tests/test_automated.py

# 使用pytest运行测试
pytest tests/
```

## 测试内容

### 数据库连接测试

- **test_automated.py**: 使用unittest框架的自动化测试套件
  - 测试多数据库支持功能
  - 测试数据库URL优先级逻辑
  - 测试数据库连接错误处理

- **test_missing_table.py**: 测试数据表不存在的情况
  - 验证数据库错误被直接暴露而不是通过表达式评估错误间接暴露
  - 运行方式：`python tests/test_missing_table.py`

- **test_comprehensive_db_errors.py**: 全面测试各种数据库错误情况
  - 包括数据表不存在、无效SQL语句、规则级别的数据库错误等
  - 运行方式：`python tests/test_comprehensive_db_errors.py`

### 其他功能测试

- **test_api.py**: 测试API接口功能
- **test_generate_rule.py**: 测试规则生成功能
- **test_uuid_generation.py**: 测试UUID生成功能
- **test_uuid_validation.py**: 测试UUID验证功能

## 数据库错误直接暴露功能

我们修改了规则引擎，使其能够直接暴露数据库错误，而不是通过表达式评估错误间接暴露。这样用户可以更清楚地了解错误的根本原因。

### 修改内容

在 `provider/rule_engine.py` 文件的 `execute_rule_set` 方法中，我们添加了以下功能：

1. **规则集级别的数据库错误处理**：
   - 当解析 `requires` 部分的数据时，如果捕获到数据库错误，直接创建一个错误规则项并添加到结果中。
   - 错误规则项的 ID 格式为 `db_error_{req_name}`，其中 `{req_name}` 是数据需求的名称。
   - 错误消息包含原始数据库错误信息。

2. **规则级别的数据库错误处理**：
   - 当解析规则级别的 `requires` 部分的数据时，如果捕获到数据库错误，直接创建一个错误规则项并添加到结果中。
   - 错误规则项的 ID 格式为 `{rule_id}_db_error`，其中 `{rule_id}` 是规则的 ID。
   - 错误消息包含原始数据库错误信息。

### 修改的关键代码

```python
# 在规则集级别的数据解析中
except Exception as e:
    error_message = str(e)
    print(f"Error resolving required data '{req['name']}': {error_message}")
    
    # 检查是否是数据库错误
    if "Error resolving from database" in error_message:
        # 直接添加数据库错误到结果中
        results.append({
            'id': f"db_error_{req['name']}", 
            'pass': False, 
            'message': f"数据库错误: {error_message}"
        })

# 在规则级别的数据解析中
except Exception as e:
    error_message = str(e)
    print(f"Error resolving required data '{req['name']}' for rule '{rule['id']}': {error_message}")
    
    # 检查是否是数据库错误
    if "Error resolving from database" in error_message:
        # 直接添加数据库错误到结果中
        results.append({
            'id': f"{rule['id']}_db_error", 
            'pass': False, 
            'message': f"数据库错误: {error_message}"
        })
        continue
```

### 测试验证

我们创建了三个测试用例来验证修改效果：

1. **测试1：数据表不存在的情况**
   - 查询不存在的表 `non_existent_table`
   - 验证数据库错误被直接暴露

2. **测试2：无效SQL语句的情况**
   - 查询不存在的表 `invalid_table`
   - 验证无效SQL错误被直接暴露

3. **测试3：规则级别的数据库错误**
   - 在规则级别的 `requires` 中查询不存在的表
   - 验证规则级别的数据库错误被直接暴露

所有测试都通过了，证明数据库错误现在能够被直接暴露，而不是通过表达式评估错误间接暴露。

### 效果对比

#### 修改前
- 数据库错误通过表达式评估错误间接暴露
- 错误消息：`表达式评估错误: '<=' not supported between instances of 'NoneType' and 'int'`
- 用户无法直接了解错误的根本原因

#### 修改后
- 数据库错误直接暴露
- 错误消息：`数据库错误: Error resolving from database: no such table: non_existent_table`
- 用户可以清楚地了解错误的根本原因是数据库表不存在

## 多数据库支持

本项目支持业务数据库和规则数据库的分离：

1. **DataResolver类**:
   - 接受`business_db_url`和`rule_db_url`两个参数
   - 根据`data_request`中的参数选择使用哪个数据库

2. **数据库URL优先级**:
   1. `data_request`中的`explicit_db_url` (最高优先级)
   2. 根据`db_source`选择对应的数据库URL
   3. 默认使用业务数据库URL

3. **RuleEngine类**:
   - 支持传递两个数据库URL给DataResolver

## 持续集成

项目配置了GitHub Actions工作流，在以下情况下自动运行测试：

- 代码推送到`main`或`develop`分支
- 创建针对`main`或`develop`分支的Pull Request
- 每天凌晨2点定时运行

## 测试覆盖率

可以使用以下命令生成测试覆盖率报告：

```bash
make test-coverage
```

报告将生成在`htmlcov/`目录中。

## 故障排除

如果测试失败，请检查：

1. 是否安装了所有必要的依赖
2. 数据库连接配置是否正确
3. 环境变量是否设置正确
4. 测试数据是否准备就绪

## 添加新测试

要添加新的测试：

1. 在`tests/`目录下创建新的测试文件
2. 使用`unittest`框架编写测试用例
3. 更新`run_all_tests.sh`脚本以包含新测试
4. 更新`Makefile`以添加新的测试命令
5. 更新本README文件以说明新测试