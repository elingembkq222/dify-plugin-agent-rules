# 业务数据库配置指南

## 概述

本插件支持在Web环境中使用业务数据库，允许规则引擎从业务数据库中查询数据并在规则中使用。

## 配置方法

### 1. 环境变量配置

在`.env`文件中添加以下配置：

```bash
# 业务数据库配置（可选）
BUSINESS_DB_URL=mysql://username:password@localhost:3306/business_db
# 或者使用SQLite
# BUSINESS_DB_URL=sqlite:///business.db
```

### 2. 支持的数据库类型

- MySQL
- PostgreSQL
- SQLite

### 3. 在规则中使用业务数据库

在规则定义中，可以通过`requires`字段指定从业务数据库查询的数据：

```json
{
  "rule_id": "example_rule",
  "name": "示例规则",
  "description": "从业务数据库查询数据并应用规则",
  "applies_when": {
    "condition": "input.age > 18"
  },
  "requires": [
    {
      "name": "consumption_count",
      "source": "database",
      "query": "SELECT COUNT(*) as count FROM orders WHERE customer_id = {{customer_id}}"
    },
    {
      "name": "customer_info",
      "source": "database",
      "query": "SELECT * FROM customers WHERE id = {{customer_id}}"
    }
  ],
  "rule": "consumption_count.count > 5 AND customer_info.status == 'active'",
  "action": {
    "type": "return",
    "value": "高价值客户"
  }
}
```

## 注意事项

1. 如果未配置业务数据库URL，插件将使用默认配置
2. 查询语句中的占位符`{{field}}`将被替换为上下文中的对应值
3. 数据库查询结果将作为变量在规则中使用
4. 请确保数据库连接字符串格式正确，并且具有适当的访问权限

## 示例

### MySQL配置示例

```bash
BUSINESS_DB_URL=mysql://root:password@localhost:3306/my_business_db
```

### SQLite配置示例

```bash
BUSINESS_DB_URL=sqlite:///path/to/business.db
```

### 在规则中使用查询结果

```json
{
  "rule_id": "check_customer_status",
  "name": "检查客户状态",
  "applies_when": {
    "condition": "input.customer_id"
  },
  "requires": [
    {
      "name": "customer_data",
      "source": "database",
      "query": "SELECT status, level FROM customers WHERE id = {{input.customer_id}}"
    }
  ],
  "rule": "customer_data.status == 'active' AND customer_data.level >= 3",
  "action": {
    "type": "return",
    "value": "高级活跃客户"
  }
}
```