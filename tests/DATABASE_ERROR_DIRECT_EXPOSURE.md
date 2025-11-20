# 数据库错误直接暴露功能

## 修改概述

我们修改了规则引擎，使其能够直接暴露数据库错误，而不是通过表达式评估错误间接暴露。这样用户可以更清楚地了解错误的根本原因。

## 修改内容

### 1. 修改了 `provider/rule_engine.py` 文件

在 `execute_rule_set` 方法中，我们添加了以下功能：

1. **规则集级别的数据库错误处理**：
   - 当解析 `requires` 部分的数据时，如果捕获到数据库错误，直接创建一个错误规则项并添加到结果中。
   - 错误规则项的 ID 格式为 `db_error_{req_name}`，其中 `{req_name}` 是数据需求的名称。
   - 错误消息包含原始数据库错误信息。

2. **规则级别的数据库错误处理**：
   - 当解析规则级别的 `requires` 部分的数据时，如果捕获到数据库错误，直接创建一个错误规则项并添加到结果中。
   - 错误规则项的 ID 格式为 `{rule_id}_db_error`，其中 `{rule_id}` 是规则的 ID。
   - 错误消息包含原始数据库错误信息。

### 2. 修改的关键代码

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

## 测试验证

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

## 效果对比

### 修改前
- 数据库错误通过表达式评估错误间接暴露
- 错误消息：`表达式评估错误: '<=' not supported between instances of 'NoneType' and 'int'`
- 用户无法直接了解错误的根本原因

### 修改后
- 数据库错误直接暴露
- 错误消息：`数据库错误: Error resolving from database: no such table: non_existent_table`
- 用户可以清楚地了解错误的根本原因是数据库表不存在

## 总结

通过这次修改，规则引擎现在能够直接暴露数据库错误，提供更清晰、更有用的错误信息，帮助用户快速定位和解决问题。