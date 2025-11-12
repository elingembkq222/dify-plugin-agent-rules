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
        self.business_db_url = business_db_url
        self._business_db_connection = None
    
    def resolve_data(self, data_request: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """
        Resolve data based on the data request configuration.
        
        Args:
            data_request: Data request configuration
            context: Context data
            
        Returns:
            Resolved data
        """
        if not isinstance(data_request, dict):
            return None
        
        source_type = data_request.get('type', 'context')
        
        if source_type == 'context':
            return self._resolve_from_context(data_request, context)
        elif source_type == 'api':
            return self._resolve_from_api(data_request, context)
        elif source_type == 'database':
            return self._resolve_from_database(data_request, context)
        elif source_type == 'static':
            return data_request.get('value')
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
        
        try:
            if db_type == 'sqlite':
                return self._query_sqlite(query)
            elif db_type == 'postgresql' and self.business_db_url:
                return self._query_postgresql(query)
            else:
                return None
        except Exception as e:
            # Log error in a real implementation
            return None
    
    def _query_sqlite(self, query: str) -> Any:
        """
        Execute a SQLite query.
        
        Args:
            query: SQL query to execute
            
        Returns:
            Query results
        """
        # Default to SQLite database if no business DB URL is provided
        db_url = self.business_db_url or "sqlite:///rule_engine.db"
        
        # Extract file path from SQLite URL
        if db_url.startswith('sqlite:///'):
            db_path = db_url[10:]  # Remove 'sqlite:///' prefix
        else:
            db_path = db_url
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        try:
            cursor.execute(query)
            
            # For SELECT queries, return the results
            if query.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
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
        return re.sub(r'\{\{([^}]+)\}\}', replace_match, text)
    
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