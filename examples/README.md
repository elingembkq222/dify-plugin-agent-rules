# Dify Agent Rules Plugin 使用示例

## 示例 1: 用户验证规则

这个示例展示了如何创建一个验证用户信息的规则集。

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
    },
    {
      "id": "name_check",
      "expression": {
        "field": "name",
        "operator": "length",
        "value": {
          "min": 2,
          "max": 50
        }
      },
      "message": "用户名长度必须在2到50个字符之间"
    }
  ]
}
```

### 测试数据

```json
{
  "name": "张三",
  "email": "zhangsan@example.com",
  "age": 25
}
```

## 示例 2: 产品验证规则

这个示例展示了如何创建一个验证产品信息的规则集。

```json
{
  "name": "产品验证规则",
  "description": "验证产品信息的规则",
  "target": "product",
  "rules": [
    {
      "id": "price_check",
      "expression": {
        "field": "price",
        "operator": "gte",
        "value": 0
      },
      "message": "产品价格不能为负数"
    },
    {
      "id": "stock_check",
      "expression": {
        "field": "stock",
        "operator": "gte",
        "value": 0
      },
      "message": "产品库存不能为负数"
    },
    {
      "id": "category_check",
      "expression": {
        "field": "category",
        "operator": "in",
        "value": ["电子产品", "服装", "食品", "图书", "家居"]
      },
      "message": "产品类别必须是预定义的类别之一"
    },
    {
      "id": "rating_check",
      "expression": {
        "field": "rating",
        "operator": "between",
        "value": [0, 5]
      },
      "message": "产品评分必须在0到5之间"
    }
  ]
}
```

### 测试数据

```json
{
  "name": "智能手机",
  "price": 2999,
  "stock": 100,
  "category": "电子产品",
  "rating": 4.5
}
```

## 示例 3: 复杂规则表达式

这个示例展示了如何使用更复杂的规则表达式。

```json
{
  "name": "订单验证规则",
  "description": "验证订单信息的复杂规则",
  "target": "order",
  "rules": [
    {
      "id": "total_amount_check",
      "expression": {
        "and": [
          {
            "field": "total_amount",
            "operator": "gte",
            "value": 0
          },
          {
            "field": "total_amount",
            "operator": "lte",
            "value": 10000
          }
        ]
      },
      "message": "订单总金额必须在0到10000之间"
    },
    {
      "id": "delivery_address_check",
      "expression": {
        "or": [
          {
            "field": "delivery_address.province",
            "operator": "eq",
            "value": "北京"
          },
          {
            "field": "delivery_address.province",
            "operator": "eq",
            "value": "上海"
          },
          {
            "field": "delivery_address.province",
            "operator": "eq",
            "value": "广州"
          },
          {
            "field": "delivery_address.province",
            "operator": "eq",
            "value": "深圳"
          }
        ]
      },
      "message": "目前只支持北京、上海、广州和深圳的配送"
    },
    {
      "id": "payment_method_check",
      "expression": {
        "field": "payment_method",
        "operator": "in",
        "value": ["支付宝", "微信支付", "银行卡", "货到付款"]
      },
      "message": "支付方式必须是支付宝、微信支付、银行卡或货到付款"
    }
  ]
}
```

### 测试数据

```json
{
  "order_id": "ORD123456",
  "total_amount": 299.99,
  "delivery_address": {
    "province": "北京",
    "city": "北京市",
    "district": "朝阳区",
    "street": "某某街道123号"
  },
  "payment_method": "支付宝"
}
```

## 示例 4: 使用自然语言生成规则

使用插件的"生成规则"功能，可以通过自然语言描述生成规则表达式。

### 示例查询

- "用户年龄必须大于18岁"
- "产品价格不能为负数"
- "邮箱地址必须包含@符号"
- "订单总金额必须在0到10000之间"
- "目前只支持北京、上海、广州和深圳的配送"

### 上下文数据

提供上下文数据可以帮助生成更准确的规则：

```json
{
  "user": {
    "fields": ["name", "email", "age", "address"]
  },
  "product": {
    "fields": ["name", "price", "category", "stock", "rating"]
  },
  "order": {
    "fields": ["order_id", "total_amount", "delivery_address", "payment_method"]
  }
}
```

## 操作符说明

### 基本操作符

- `eq`: 等于
- `ne`: 不等于
- `gt`: 大于
- `gte`: 大于等于
- `lt`: 小于
- `lte`: 小于等于
- `contains`: 包含
- `not_contains`: 不包含
- `in`: 在列表中
- `not_in`: 不在列表中
- `between`: 在范围内
- `length`: 字符串长度
- `regex`: 正则表达式匹配

### 逻辑操作符

- `and`: 逻辑与，所有条件都必须满足
- `or`: 逻辑或，至少一个条件满足
- `not`: 逻辑非，条件不满足

### 嵌套表达式

可以使用嵌套的 `and`、`or` 和 `not` 操作符创建复杂的规则表达式。

## 使用提示

1. 规则表达式中的字段路径可以使用点号表示法访问嵌套属性，如 `delivery_address.province`
2. 对于数值比较，确保字段值和比较值是相同的数据类型
3. 使用 `length` 操作符时，可以提供 `min` 和 `max` 值来指定长度范围
4. 复杂规则表达式可以使用嵌套的逻辑操作符组合多个条件
5. 自然语言生成规则功能需要配置正确的 LLM 模型