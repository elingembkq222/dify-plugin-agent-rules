"""
数据解析器模块

该模块负责根据规则配置解析和获取数据，支持多种数据源：
1. 本地数据源 (local)
2. 数据库数据源 (db)
3. 上下文数据源 (context)
4. API数据源 (api)
5. 数据库查询数据源 (database)
6. 静态数据源 (static)
"""

import json
import os
import sqlite3
from typing import Any, Dict, List, Optional, Union

# 导入错误处理模块
from .error_handler import (
    ErrorType,
    handle_exception,
    create_database_error_response,
    create_database_connection_error_response,
    create_database_table_not_found_response,
    create_sql_syntax_error_response
)

import urllib.request
import urllib.parse
from typing import Any, Dict, List, Optional, Union

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import psycopg2
    HAS_POSTGRESQL = True
except ImportError:
    HAS_POSTGRESQL = False


class DataResolver:
    """
    Data Resolver for fetching data from various sources.
    """
    
    def __init__(self, business_db_url: Optional[str] = None, rule_db_url: Optional[str] = None):
        """
        Initialize the Data Resolver.
        
        Args:
            business_db_url: Optional business database connection URL
            rule_db_url: Optional rule database connection URL
        """
        # If no business_db_url is provided, try to get it from environment variables
        if not business_db_url:
            import os
            business_db_url = os.environ.get('BUSINESS_DB_URL')
        
        # If no rule_db_url is provided, try to get it from environment variables
        if not rule_db_url:
            import os
            rule_db_url = os.environ.get('RULE_DB_URL')
        
        self.business_db_url = business_db_url
        self.rule_db_url = rule_db_url
        self._business_db_connection = None
        self._rule_db_connection = None
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """
        Get a nested value from a dictionary using dot notation.
        
        Args:
            data: Dictionary to get value from
            path: Dot-separated path to the value (e.g., "user.profile.age")
            
        Returns:
            The value at the path or None if not found
        """
        if not path:
            return None
            
        parts = path.split('.')
        value = data
        
        try:
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                elif isinstance(value, list) and part.isdigit() and int(part) < len(value):
                    value = value[int(part)]
                else:
                    return None
            return value
        except (KeyError, TypeError, AttributeError, IndexError):
            return None
    
    def resolve_data(self, data_request: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """
        Resolve data based on the request configuration.
        
        Args:
            data_request: Data request configuration
            context: Context data
            
        Returns:
            Resolved data
        """
        if not isinstance(data_request, dict):
            return None
        
        # Check for 'source' field first (for backward compatibility)
        source = data_request.get('source')
        if source == 'local':
            # For local source, use query as field path
            query = data_request.get('query', '')
            # Remove 'input.' prefix if present
            if query.startswith('input.'):
                query = query[6:]
            value = self._get_nested_value(context, query)
            
            # Try to convert to appropriate type if value is a string
            if isinstance(value, str):
                # Try to convert to int
                try:
                    return int(value)
                except ValueError:
                    pass
                
                # Try to convert to float
                try:
                    return float(value)
                except ValueError:
                    pass
                
                # Try to convert to bool
                if value.lower() in ('true', 'false'):
                    return value.lower() == 'true'
            
            return value
        elif source == 'db':
            # For db source, treat it as database type
            result = self._resolve_from_database(data_request, context)
            return result
        
        # Otherwise use 'type' field
        source_type = data_request.get('type', 'context')
        
        if source_type == 'context':
            result = self._resolve_from_context(data_request, context)
            return result
        elif source_type == 'api':
            result = self._resolve_from_api(data_request, context)
            return result
        elif source_type == 'database':
            result = self._resolve_from_database(data_request, context)
            return result
        elif source_type == 'static':
            result = data_request.get('value')
            return result
        else:
            return None
    
    def _resolve_from_context(self, data_request: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """
        Resolve data from the context.
        
        Args:
            data_request: Data request configuration
            context: Context data
            
        Returns:
            Resolved data from context
        """
        field = data_request.get('field')
        if not field:
            return None
        
        # Split field into parts for nested access
        parts = field.split('.')
        value = context
        
        try:
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                elif isinstance(value, list) and part.isdigit() and int(part) < len(value):
                    value = value[int(part)]
                else:
                    return None
            return value
        except (KeyError, TypeError, AttributeError, IndexError):
            return None
    
    def _resolve_from_api(self, data_request: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """
        Resolve data from an API endpoint.
        
        Args:
            data_request: Data request configuration
            context: Context data
            
        Returns:
            Resolved data from API
        """
        url = data_request.get('url')
        if not url:
            return None
        
        # Replace placeholders in URL with context values
        url = self._replace_placeholders(url, context)
        
        method = data_request.get('method', 'GET').upper()
        headers = data_request.get('headers', {})
        params = data_request.get('params', {})
        body = data_request.get('body')
        
        # Replace placeholders in params and body
        params = self._replace_placeholders_in_dict(params, context)
        if body:
            body = self._replace_placeholders_in_dict(body, context)
        
        try:
            if HAS_REQUESTS:
                # Use requests library if available
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params if method == 'GET' else None,
                    json=body if method in ['POST', 'PUT', 'PATCH'] else None
                )
                response.raise_for_status()
                
                # Try to parse JSON response
                try:
                    return response.json()
                except ValueError:
                    return response.text
            else:
                # Fall back to urllib
                if method == 'GET':
                    if params:
                        url = f"{url}?{urllib.parse.urlencode(params)}"
                    with urllib.request.urlopen(url) as response:
                        data = response.read().decode('utf-8')
                        try:
                            return json.loads(data)
                        except ValueError:
                            return data
                else:
                    # Other methods not implemented without requests
                    return None
        except Exception as e:
            # Log error in a real implementation
            return None
    
    def _resolve_from_database(self, data_request: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """
        Resolve data from a database.
        
        Args:
            data_request: Data request configuration
            context: Context data
            
        Returns:
            Resolved data from database
        """
        db_type = data_request.get('db_type', 'sqlite')
        query = data_request.get('query')
        
        # Determine which database URL to use
        # Priority: 1. Explicit db_url in data_request, 2. Default URL based on db_source
        explicit_db_url = data_request.get('db_url')
        
        if explicit_db_url:
            # Use the explicitly provided database URL
            db_url = explicit_db_url
        else:
            # Use the default database URL based on db_source (default to business)
            db_source = data_request.get('db_source', 'business')
            if db_source == 'rule':
                db_url = getattr(self, 'rule_db_url', self.business_db_url)
            else:  # Default to business database
                db_url = self.business_db_url
        
        if not query:
            return None
        
        # Replace placeholders in query
        query = self._replace_placeholders(query, context)
        
        # Convert MySQL syntax to SQLite if needed
        if db_type == 'sqlite' and 'DATE_SUB(CURDATE(), INTERVAL 1 YEAR)' in query:
            query = query.replace('DATE_SUB(CURDATE(), INTERVAL 1 YEAR)', "date('now', '-1 year')")
        
        try:
            if db_type == 'sqlite':
                result = self._query_sqlite(query, db_url)
                return result
            elif db_type == 'postgresql' and db_url:
                result = self._query_postgresql(query, db_url)
                return result
            elif db_type == 'mysql' and db_url:
                result = self._query_mysql(query, db_url)
                return result
            else:
                error_response = create_database_error_response(
                    message=f"不支持的数据库类型: {db_type}",
                    context={"db_type": db_type, "query": query, "db_url": db_url}
                )
                raise Exception(error_response.to_json())
        except Exception as e:
            # Re-raise the exception to make database errors visible
            error_msg = str(e)
            
            # 检查是否已经是JSON格式的错误（避免重复封装）
            if error_msg.startswith('{') and error_msg.endswith('}'):
                # 已经是JSON格式，直接抛出
                raise e
            
            # 封装为JSON格式错误
            if "no such table" in error_msg.lower():
                error_response = create_database_table_not_found_response(
                    message=f"数据库表不存在错误: {error_msg}",
                    context={"db_type": db_type, "query": query, "db_url": db_url}
                )
            elif "connection" in error_msg.lower() or "can't connect" in error_msg.lower():
                error_response = create_database_connection_error_response(
                    message=f"数据库连接错误: {error_msg}",
                    context={"db_type": db_type, "query": query, "db_url": db_url}
                )
            elif "syntax error" in error_msg.lower():
                error_response = create_sql_syntax_error_response(
                    message=f"SQL语法错误: {error_msg}",
                    context={"db_type": db_type, "query": query, "db_url": db_url}
                )
            else:
                error_response = create_database_error_response(
                    message=f"数据库错误: {error_msg}",
                    context={"db_type": db_type, "query": query, "db_url": db_url}
                )
            
            raise Exception(error_response.to_json()) from e
    
    def _query_sqlite(self, query: str, db_url: Optional[str] = None) -> Any:
        """
        Execute a SQLite query.
        
        Args:
            query: SQL query to execute
            db_url: Optional database URL, defaults to self.business_db_url
            
        Returns:
            Query results
        """
        # Use the provided db_url or fall back to business database URL
        if db_url and db_url.startswith('sqlite:///'):
            db_path = db_url[10:]  # Remove 'sqlite:///' prefix
        elif self.business_db_url and self.business_db_url.startswith('sqlite:///'):
            db_path = self.business_db_url[10:]  # Remove 'sqlite:///' prefix
        else:
            # Default to SQLite database
            db_path = "rule_engine.db"
        
        # Check if database file exists
        import os
        if not os.path.exists(db_path):
            # 创建统一的数据库连接错误响应
            error_response = create_database_connection_error_response(
                message=f"数据库连接错误: 数据库文件不存在: {db_path}",
                context={"db_path": db_path, "query": query}
            )
            # 抛出异常，包含JSON格式的错误信息
            raise Exception(error_response.to_json())
        
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            
            try:
                cursor.execute(query)
                
                # For SELECT queries, return the results
                if query.strip().upper().startswith('SELECT'):
                    rows = cursor.fetchall()
                    result = [dict(row) for row in rows]
                    
                    # If there are no results, return None
                    if not result:
                        return None
                    
                    # If there's only one row, return the dictionary directly
                    if len(result) == 1:
                        row = result[0]
                        # If it's a single column result (like COUNT(*), MAX(id), etc.), return the value directly
                        if len(row) == 1:
                            # Get the first (and only) column value
                            return list(row.values())[0]
                        # Otherwise return the full row dictionary
                        return row
                    
                    # If there are multiple rows, return the list of dictionaries
                    return result
                else:
                    # For other queries, return the number of affected rows
                    conn.commit()
                    return cursor.rowcount
            finally:
                conn.close()
        except sqlite3.Error as e:
            # Handle SQLite specific errors
            error_msg = str(e)
            
            # Check for table not found error
            if "no such table" in error_msg.lower():
                error_response = create_database_table_not_found_response(
                    message=f"数据库表不存在错误: {error_msg}",
                    context={"db_path": db_path, "query": query}
                )
            # Check for database connection errors
            elif "unable to open database file" in error_msg.lower():
                error_response = create_database_connection_error_response(
                    message=f"数据库连接错误: 无法打开数据库文件: {db_path}",
                    context={"db_path": db_path, "query": query}
                )
            # Check for permission errors
            elif "permission denied" in error_msg.lower():
                error_response = create_database_connection_error_response(
                    message=f"数据库连接错误: 权限不足，无法访问数据库文件: {db_path}",
                    context={"db_path": db_path, "query": query}
                )
            # General database error
            else:
                error_response = create_database_error_response(
                    message=f"数据库错误: {error_msg}",
                    context={"db_path": db_path, "query": query}
                )
            
            # 抛出异常，包含JSON格式的错误信息
            raise Exception(error_response.to_json()) from e
        except Exception as e:
            # Handle other exceptions
            error_msg = str(e)
            
            # 检查是否已经是JSON格式的错误（避免重复封装）
            if error_msg.startswith('{') and error_msg.endswith('}'):
                # 已经是JSON格式，直接抛出
                raise e
            
            if "no such table" in error_msg.lower():
                error_response = create_database_table_not_found_response(
                    message=f"数据库表不存在错误: {error_msg}",
                    context={"db_path": db_path, "query": query}
                )
            else:
                error_response = create_database_error_response(
                    message=f"数据库错误: {error_msg}",
                    context={"db_path": db_path, "query": query}
                )
            
            # 抛出异常，包含JSON格式的错误信息
            raise Exception(error_response.to_json()) from e
    
    def _query_postgresql(self, query: str, db_url: Optional[str] = None) -> Any:
        """
        Execute a PostgreSQL query.
        
        Args:
            query: SQL query to execute
            db_url: Optional database URL, defaults to self.business_db_url
            
        Returns:
            Query results
        """
        if not HAS_POSTGRESQL:
            return None
        
        # Use the provided db_url or fall back to business database URL
        connection_url = db_url if db_url else self.business_db_url
        if not connection_url:
            error_response = create_database_connection_error_response(
                message="No database URL provided for PostgreSQL connection",
                context={"query": query}
            )
            raise Exception(error_response.to_json())
        
        try:
            # Add connection timeout to avoid hanging
            conn = psycopg2.connect(
                connection_url,
                connect_timeout=5
            )
            cursor = conn.cursor()
            
            try:
                cursor.execute(query)
                
                # For SELECT queries, return the results
                if query.strip().upper().startswith('SELECT'):
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
                else:
                    # For other queries, return the number of affected rows
                    conn.commit()
                    return cursor.rowcount
            finally:
                conn.close()
        except psycopg2.Error as e:
            # Handle PostgreSQL specific errors with more detailed classification
            error_msg = str(e)
            error_code = getattr(e, 'pgcode', None)
            
            # Table doesn't exist error (PostgreSQL error code 42P01)
            if error_code == '42P01' or "relation" in error_msg.lower() and "does not exist" in error_msg.lower():
                error_response = create_database_table_not_found_response(
                    message=f"数据库表不存在错误: {error_msg}",
                    context={"connection_url": connection_url, "query": query, "error_code": error_code}
                )
            # Connection errors
            elif "connection" in error_msg.lower() or "could not connect" in error_msg.lower() or "timeout" in error_msg.lower():
                error_response = create_database_connection_error_response(
                    message=f"数据库连接错误: {error_msg}",
                    context={"connection_url": connection_url, "query": query, "error_code": error_code}
                )
            # Database doesn't exist error (PostgreSQL error code 08006)
            elif error_code == '08006' or "database" in error_msg.lower() and "does not exist" in error_msg.lower():
                error_response = create_database_connection_error_response(
                    message=f"数据库连接错误: 数据库不存在: {error_msg}",
                    context={"connection_url": connection_url, "query": query, "error_code": error_code}
                )
            # Authentication error (PostgreSQL error code 28P01)
            elif error_code == '28P01' or "password authentication failed" in error_msg.lower():
                error_response = create_database_connection_error_response(
                    message=f"数据库连接错误: 认证失败: {error_msg}",
                    context={"connection_url": connection_url, "query": query, "error_code": error_code}
                )
            # Syntax errors (PostgreSQL error code 42601)
            elif error_code == '42601' or "syntax error" in error_msg.lower():
                error_response = create_sql_syntax_error_response(
                    message=f"SQL语法错误: {error_msg}",
                    context={"connection_url": connection_url, "query": query, "error_code": error_code}
                )
            # Other PostgreSQL errors
            else:
                error_response = create_database_error_response(
                    message=f"数据库错误: {error_msg}",
                    context={"connection_url": connection_url, "query": query, "error_code": error_code}
                )
            
            # 抛出异常，包含JSON格式的错误信息
            raise Exception(error_response.to_json()) from e
        except Exception as e:
            # Handle other exceptions
            error_msg = str(e)
            
            # 检查是否已经是JSON格式的错误（避免重复封装）
            if error_msg.startswith('{') and error_msg.endswith('}'):
                # 已经是JSON格式，直接抛出
                raise e
                
            if "no such table" in error_msg.lower() or "relation" in error_msg.lower() and "does not exist" in error_msg.lower():
                error_response = create_database_table_not_found_response(
                    message=f"数据库表不存在错误: {error_msg}",
                    context={"connection_url": connection_url, "query": query}
                )
            elif "connection" in error_msg.lower() or "could not connect" in error_msg.lower():
                error_response = create_database_connection_error_response(
                    message=f"数据库连接错误: {error_msg}",
                    context={"connection_url": connection_url, "query": query}
                )
            else:
                error_response = create_database_error_response(
                    message=f"数据库错误: {error_msg}",
                    context={"connection_url": connection_url, "query": query}
                )
            
            # 抛出异常，包含JSON格式的错误信息
            raise Exception(error_response.to_json()) from e
    
    def _query_mysql(self, query: str, db_url: Optional[str] = None) -> Any:
        """
        Execute a MySQL query.
        
        Args:
            query: SQL query to execute
            db_url: Optional database URL, defaults to self.business_db_url
            
        Returns:
            Query results
        """
        try:
            import pymysql
        except ImportError:
            return None
        
        # Use the provided db_url or fall back to business database URL
        connection_url = db_url if db_url else self.business_db_url
        if not connection_url:
            error_response = create_database_connection_error_response(
                message="No database URL provided for MySQL connection",
                context={"query": query}
            )
            raise Exception(error_response.to_json())
        
        try:
            # Convert SQLAlchemy URL to pymysql compatible format
            if connection_url.startswith('mysql+pymysql://'):
                connection_url = connection_url.replace('mysql+pymysql://', 'mysql://')
            
            # Parse connection URL to extract components
            from urllib.parse import urlparse
            parsed = urlparse(connection_url)
            
            # Extract connection parameters
            host = parsed.hostname or 'localhost'
            port = parsed.port or 3306
            username = parsed.username
            password = parsed.password
            database = parsed.path.lstrip('/') if parsed.path else None
            
            # Add connection timeout to avoid hanging
            conn = pymysql.connect(
                host=host,
                port=port,
                user=username,
                password=password,
                database=database,
                connect_timeout=5,
                read_timeout=10,
                write_timeout=10
            )
            cursor = conn.cursor()
            
            try:
                cursor.execute(query)
                
                # For SELECT queries, return the results
                if query.strip().upper().startswith('SELECT'):
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
                else:
                    # For other queries, return the number of affected rows
                    conn.commit()
                    return cursor.rowcount
            finally:
                conn.close()
        except pymysql.Error as e:
            # Handle MySQL specific errors with more detailed classification
            error_msg = str(e)
            error_code = getattr(e, 'args', (0, ))[0] if hasattr(e, 'args') and e.args else 0
            
            # Table doesn't exist error (MySQL error code 1146)
            if error_code == 1146 or "no such table" in error_msg.lower() or "table" in error_msg.lower() and "doesn't exist" in error_msg.lower():
                error_response = create_database_table_not_found_response(
                    message=f"数据库表不存在错误: {error_msg}",
                    context={"connection_url": connection_url, "query": query, "error_code": error_code}
                )
            # Connection errors (MySQL error codes in 2000s)
            elif error_code >= 2000 or "connection" in error_msg.lower() or "can't connect" in error_msg.lower() or "access denied" in error_msg.lower() or "timeout" in error_msg.lower():
                error_response = create_database_connection_error_response(
                    message=f"数据库连接错误: {error_msg}",
                    context={"connection_url": connection_url, "query": query, "error_code": error_code}
                )
            # Syntax errors (MySQL error code 1064)
            elif error_code == 1064 or "syntax error" in error_msg.lower():
                error_response = create_sql_syntax_error_response(
                    message=f"SQL语法错误: {error_msg}",
                    context={"connection_url": connection_url, "query": query, "error_code": error_code}
                )
            # Database doesn't exist error (MySQL error code 1049)
            elif error_code == 1049 or "unknown database" in error_msg.lower():
                error_response = create_database_connection_error_response(
                    message=f"数据库连接错误: 数据库不存在: {error_msg}",
                    context={"connection_url": connection_url, "query": query, "error_code": error_code}
                )
            # Authentication error (MySQL error code 1045)
            elif error_code == 1045 or "access denied for user" in error_msg.lower():
                error_response = create_database_connection_error_response(
                    message=f"数据库连接错误: 认证失败: {error_msg}",
                    context={"connection_url": connection_url, "query": query, "error_code": error_code}
                )
            # Other MySQL errors
            else:
                error_response = create_database_error_response(
                    message=f"数据库错误: {error_msg}",
                    context={"connection_url": connection_url, "query": query, "error_code": error_code}
                )
            
            # 抛出异常，包含JSON格式的错误信息
            raise Exception(error_response.to_json()) from e
        except Exception as e:
            # Handle other exceptions
            error_msg = str(e)
            
            # 检查是否已经是JSON格式的错误（避免重复封装）
            if error_msg.startswith('{') and error_msg.endswith('}'):
                # 已经是JSON格式，直接抛出
                raise e
                
            if "no such table" in error_msg.lower():
                error_response = create_database_table_not_found_response(
                    message=f"数据库表不存在错误: {error_msg}",
                    context={"connection_url": connection_url, "query": query}
                )
            elif "connection" in error_msg.lower() or "can't connect" in error_msg.lower():
                error_response = create_database_connection_error_response(
                    message=f"数据库连接错误: {error_msg}",
                    context={"connection_url": connection_url, "query": query}
                )
            else:
                error_response = create_database_error_response(
                    message=f"数据库错误: {error_msg}",
                    context={"connection_url": connection_url, "query": query}
                )
            
            # 抛出异常，包含JSON格式的错误信息
            raise Exception(error_response.to_json()) from e
    
    def _replace_placeholders(self, text: str, context: Dict[str, Any]) -> str:
        """
        Replace placeholders in text with values from context.
        
        Args:
            text: Text containing placeholders
            context: Context data
            
        Returns:
            Text with placeholders replaced
        """
        # Replace {{field}} placeholders with context values
        def replace_match(match):
            field = match.group(1)
            parts = field.split('.')
            
            # Handle special case for input
            if parts[0] == 'input' and 'input' in context:
                value = context['input']
                for part in parts[1:]:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        return match.group(0)  # Keep original if not found
                return str(value)
            
            # Handle case where field is input.user_id but input is not in context
            # but user_id is directly in context
            if parts[0] == 'input' and len(parts) == 2 and parts[1] in context:
                value = context[parts[1]]
                return str(value)
            
            # Handle normal case
            value = context
            try:
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        return match.group(0)  # Keep original if not found
                return str(value)
            except (KeyError, TypeError, AttributeError):
                return match.group(0)  # Keep original if not found
        
        import re
        result = re.sub(r'\{\{([^}]+)\}\}', replace_match, text)
        return result
    
    def _replace_placeholders_in_dict(self, data: Any, context: Dict[str, Any]) -> Any:
        """
        Replace placeholders in a dictionary or list with values from context.
        
        Args:
            data: Dictionary, list, or string containing placeholders
            context: Context data
            
        Returns:
            Data with placeholders replaced
        """
        if isinstance(data, dict):
            return {k: self._replace_placeholders_in_dict(v, context) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._replace_placeholders_in_dict(item, context) for item in data]
        elif isinstance(data, str):
            return self._replace_placeholders(data, context)
        else:
            return data


# Global data resolver instance
data_resolver = DataResolver()


def resolve_data(data_request: Dict[str, Any], context: Dict[str, Any]) -> Any:
    """
    Resolve data based on the data request configuration.
    
    Args:
        data_request: Data request configuration
        context: Context data
        
    Returns:
        Resolved data
    """
    return data_resolver.resolve_data(data_request, context)


def resolve_data(request: Dict[str, Any], context: Dict[str, Any]) -> Any:
    """
    Resolve data based on the request configuration.
    
    Args:
        request: Data resolution request with 'name', 'type', and other parameters
        context: Context data to use for resolution
        
    Returns:
        Resolved data
    """
    data_type = request.get('type', 'context')
    
    if data_type == 'context':
        # Resolve from context
        field = request.get('field', request.get('name'))
        return self._resolve_from_context(field, context)
    elif data_type == 'database':
        # Resolve from database
        query = request.get('query')
        db_type = request.get('db_type', 'sqlite')  # Default to SQLite
        db_url = request.get('db_url', self.business_db_url)
        
        if not query:
            raise ValueError("Database query is required")
        
        try:
            if db_type.lower() == 'sqlite':
                return self._query_sqlite(query, db_url)
            elif db_type.lower() == 'postgresql':
                return self._query_postgresql(query, db_url)
            elif db_type.lower() == 'mysql':
                return self._query_mysql(query, db_url)
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
        except Exception as e:
            error_message = str(e)
            # Check if this is a specific database error type
            if "no such table" in error_message.lower():
                raise Exception(f"数据库表不存在错误: {error_message}")
            elif "connection" in error_message.lower():
                raise Exception(f"数据库连接错误: {error_message}")
            elif "syntax error" in error_message.lower():
                raise Exception(f"SQL语法错误: {error_message}")
            else:
                raise Exception(f"数据库查询错误: {error_message}")
    else:
        raise ValueError(f"Unsupported data type: {data_type}")