import os
import re
import requests
import sqlite3
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import create_engine, text

db_connections = {}
db_engines = {}

def get_db_engine(db_url: str):
    if db_url not in db_engines:
        try:
            db_engines[db_url] = create_engine(db_url)
        except Exception as e:
            raise ConnectionError(f"数据库连接错误: {db_url}, error: {e}")
    return db_engines[db_url]

class DataResolver:
    """
    负责从不同来源解析数据，例如数据库、API、上下文等
    """
    
    def __init__(self, business_db_url: Optional[str] = None, rule_db_url: Optional[str] = None):
        self.business_db_url = business_db_url or os.environ.get('BUSINESS_DB_URL')
        self.rule_db_url = rule_db_url or os.environ.get('RULE_DB_URL')

    def resolve(self, requirement: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """
        根据`requires`中的定义解析数据
        """
        source = requirement.get('source')
        
        if source == 'db' and self.business_db_url:
            return self._resolve_from_db(requirement, context, self.business_db_url)
        elif source == 'rule_db' and self.rule_db_url:
            return self._resolve_from_db(requirement, context, self.rule_db_url)
        elif source == 'api':
            return self._resolve_from_api(requirement, context)
        elif source == 'context':
            return self._resolve_from_context(requirement, context)
        
        return None

    def resolve_data(self, requirement: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """
        兼容接口：与`resolve`等价，用于适配调用方调用 `resolve_data`
        """
        return self.resolve(requirement, context)

    def _resolve_from_db(self, requirement: Dict[str, Any], context: Dict[str, Any], db_url: str) -> Any:
        query = requirement.get('query')
        if not query:
            return None

        final_query = self._replace_placeholders(query, context)

        try:
            engine = get_db_engine(db_url)
            with engine.connect() as conn:
                result = conn.execute(text(final_query))
                transform = requirement.get('transform', 'auto')

                if transform == 'one':
                    row = result.fetchone()
                    return dict(row._mapping) if row else None
                elif transform == 'all':
                    rows = result.fetchall()
                    return [dict(r._mapping) for r in rows]
                elif transform == 'count':
                    row = result.fetchone()
                    return row[0] if row else 0
                else:
                    rows = result.fetchall()
                    if len(rows) == 1:
                        row = rows[0]
                        try:
                            mapping = dict(row._mapping)
                        except Exception:
                            return row[0] if len(row) == 1 else row
                        if len(mapping) == 1:
                            return next(iter(mapping.values()))
                        return mapping
                    return [dict(r._mapping) for r in rows]
        except Exception as e:
            raise Exception(f"数据库错误: {e}")

    def _resolve_from_api(self, requirement: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """从API解析数据"""
        # ... (未来可以实现)
        return None

    def _resolve_from_context(self, requirement: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """从上下文解析数据"""
        field = requirement.get('field')
        if not field:
            return None
        return self._get_nested_value(context, field)
        
    def _replace_placeholders(self, text: str, context: Dict[str, Any]) -> str:
        """用上下文中的值替换占位符 {{...}}"""
        def replacer(match):
            key = match.group(1).strip()
            value = self._get_nested_value(context, key)
            return str(value) if value is not None else match.group(0)
            
        return re.sub(r'\{\{\s*(.*?)\s*\}\}', replacer, text)

    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Any:
        """获取嵌套字典中的值"""
        keys = key.split('.')
        value = data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                break
        else:
            return value
        if key.startswith('input.') and isinstance(data, dict):
            alt = key[len('input.'):]
            if alt in data:
                return data[alt]
        if key.startswith('context.') and isinstance(data, dict):
            alt = key[len('context.'):]
            if alt in data:
                return data[alt]
        return None

def resolve_data(requirement: Dict[str, Any], context: Dict[str, Any], business_db_url: Optional[str] = None, rule_db_url: Optional[str] = None) -> Any:
    """
    全局的数据解析函数
    """
    resolver = DataResolver(business_db_url, rule_db_url)
    return resolver.resolve(requirement, context)

def normalize_sql_result(result):
    """
    Normalize raw SQL results into predictable structure:
    - Scalar (COUNT, SUM, MAX, MIN…)
    - Single row (dict)
    - Multi rows (list of dict)
    - Affected rows (int)
    - Empty result
    """
    
    # 1. 空结果
    if result is None:
        return {
            "type": "empty",
            "data": None
        }

    # 2. INSERT/UPDATE/DELETE 受影响行数：int
    if isinstance(result, int) and not isinstance(result, bool):
        return {
            "type": "affected_rows",
            "data": result
        }

    # 3. 单行：dict
    if isinstance(result, dict):
        # 单字段 -> scalar
        if len(result) == 1:
            value = next(iter(result.values()))
            return {
                "type": "scalar",
                "data": value,
                "columns": list(result.keys())
            }
        # 多字段 -> row
        return {
            "type": "row",
            "data": result,
            "columns": list(result.keys())
        }

    # 4. 多行：list
    if isinstance(result, list):
        if len(result) == 0:
            return {"type": "empty", "data": None}

        first = result[0]
        if isinstance(first, dict):
            return {
                "type": "rows",
                "data": result,
                "columns": list(first.keys())
            }
        else:
            return {
                "type": "rows",
                "data": result,
                "columns": None
            }

    # 5. fallback
    return {
        "type": "unknown",
        "data": result
    }
