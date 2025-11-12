# Dify Agent Rules Plugin

这是一个为 Dify Agent 设计的规则引擎插件，允许用户创建、管理和验证业务规则。

## 功能特性

- **规则存储**: 基于 SQLAlchemy 的规则存储系统，支持 SQLite 和 PostgreSQL
- **规则引擎**: 强大的规则引擎，支持多种操作符和逻辑组合
- **数据解析器**: 从多种来源解析数据，包括上下文、API、数据库和静态数据
- **LLM 查询解析器**: 使用 LLM 将自然语言查询转换为规则表达式
- **工具接口**: 提供 5 个工具接口，用于规则验证、添加、列表和生成
- **前端 UI**: 现代化的规则管理控制台，支持规则的创建、编辑和验证

## 安装和使用

1. 将插件安装到 Dify 环境中
2. 配置必要的参数：
   - `RULE_DB_URL`: 规则数据库 URL（默认: sqlite:///rule_engine.db）
   - `BUSINESS_DB_URL`: 业务数据库 URL（可选）
   - `LLM_MODEL`: 用于查询解析的 LLM 模型（默认: gpt-4o）

## 工具接口

### 1. validate_ruleset
验证用户输入是否符合指定的规则集。

参数:
- `ruleset_id`: 规则集 ID
- `context`: 上下文数据

### 2. add_rule
添加或更新规则集。

参数:
- `rule_json`: 完整的规则集 JSON

### 3. list_rules
列出所有可用的规则集。

参数:
- `target`: 可选的目标过滤器

### 4. generate_rule_from_query
使用 LLM 从自然语言查询生成规则。

参数:
- `query`: 自然语言查询
- `context`: 上下文数据结构（可选）

## 前端 UI

插件包含一个现代化的规则管理控制台，提供以下功能：

- 规则列表查看和过滤
- 添加和编辑规则集
- 验证规则集
- 从自然语言生成规则

访问 `web/index.html` 可以使用前端 UI。

## 示例规则集

```json
{
  "name": "用户验证规则",
  "description": "验证用户输入的规则",
  "target": "user",
  "rules": [
    {
      "id": "age_check",
      "expression": {
        "field": "age",
        "operator": "gt",
        "value": 18
      },
      "message": "用户年龄必须大于18岁"
    },
    {
      "id": "email_check",
      "expression": {
        "field": "email",
        "operator": "contains",
        "value": "@"
      },
      "message": "邮箱地址无效"
    }
  ]
}
```

## 开发和贡献

欢迎提交 Issue 和 Pull Request 来改进这个插件。

## 许可证

MIT License
