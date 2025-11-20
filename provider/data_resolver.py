"""
Data Resolver Module

This module provides functionality to resolve data from various sources,
including databases, APIs, and context data.
"""

import json
import sqlite3
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
    
    def __init__(self, business_db_url: Optional[str] = None):
        """
        Initialize the Data Resolver.
        
        Args:
            business_db_url: Optional business database connection URL
        """
        # If no business_db_url is provided, try to get it from environment variables
        if not business_db_url:
            import os
            business_db_url = os.environ.get('BUSINESS_DB_URL')
        
        self.business_db_url = business_db_url
        self._business_db_connection = None
    
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
            print(f"Database resolution result: {result}")
            return result
        
        # Otherwise use 'type' field
        source_type = data_request.get('type', 'context')
        
        print(f"Resolving data with type: {source_type}, request: {data_request}")
        
        if source_type == 'context':
            result = self._resolve_from_context(data_request, context)
            print(f"Context resolution result: {result}")
            return result
        elif source_type == 'api':
            result = self._resolve_from_api(data_request, context)
            print(f"API resolution result: {result}")
            return result
        elif source_type == 'database':
            result = self._resolve_from_database(data_request, context)
            print(f"Database resolution result: {result}")
            return result
        elif source_type == 'static':
            result = data_request.get('value')
            print(f"Static resolution result: {result}")
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
        
        if not query:
            return None
        
        # Replace placeholders in query
        query = self._replace_placeholders(query, context)
        
        # Convert MySQL syntax to SQLite if needed
        if db_type == 'sqlite' and 'DATE_SUB(CURDATE(), INTERVAL 1 YEAR)' in query:
            query = query.replace('DATE_SUB(CURDATE(), INTERVAL 1 YEAR)', "date('now', '-1 year')")
        
        try:
            print(f"Executing {db_type} query: {query}")
            if db_type == 'sqlite':
                result = self._query_sqlite(query)
                print(f"Query result: {result}")
                return result
            elif db_type == 'postgresql' and self.business_db_url:
                result = self._query_postgresql(query)
                print(f"Query result: {result}")
                return result
            elif db_type == 'mysql' and self.business_db_url:
                result = self._query_mysql(query)
                print(f"Query result: {result}")
                return result
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
        except Exception as e:
            # Re-raise the exception to make database errors visible
            error_msg = f"Error resolving from database: {e}"
            print(error_msg)
            raise Exception(error_msg) from e
    
    def _query_sqlite(self, query: str) -> Any:
        """
        Execute a SQLite query.
        
        Args:
            query: SQL query to execute
            
        Returns:
            Query results
        """
        # Use the business database URL if provided
        if self.business_db_url and self.business_db_url.startswith('sqlite:///'):
            db_path = self.business_db_url[10:]  # Remove 'sqlite:///' prefix
        else:
            # Default to SQLite database
            db_path = "rule_engine.db"
        
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
    
    def _query_postgresql(self, query: str) -> Any:
        """
        Execute a PostgreSQL query.
        
        Args:
            query: SQL query to execute
            
        Returns:
            Query results
        """
        if not HAS_POSTGRESQL:
            return None
        
        conn = psycopg2.connect(self.business_db_url)
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
    
    def _query_mysql(self, query: str) -> Any:
        """
        Execute a MySQL query.
        
        Args:
            query: SQL query to execute
            
        Returns:
            Query results
        """
        try:
            import pymysql
        except ImportError:
            print("PyMySQL not installed, cannot execute MySQL query")
            return None
        
        conn = pymysql.connect(self.business_db_url)
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