"""
统一异常处理模块

该模块提供统一的异常处理功能，将各种异常转换为标准化的JSON格式响应。
"""

import json
import traceback
from typing import Any, Dict, Optional, Union
from enum import Enum


class ErrorType(Enum):
    """错误类型枚举"""
    DATABASE_ERROR = "database_error"
    DATABASE_CONNECTION_ERROR = "database_connection_error"
    DATABASE_TABLE_NOT_FOUND = "database_table_not_found"
    DATABASE_QUERY_ERROR = "database_query_error"
    SQL_SYNTAX_ERROR = "sql_syntax_error"
    EXPRESSION_EVALUATION_ERROR = "expression_evaluation_error"
    RULE_EXECUTION_ERROR = "rule_execution_error"
    VALIDATION_ERROR = "validation_error"
    CONFIGURATION_ERROR = "configuration_error"
    AUTHENTICATION_ERROR = "authentication_error"
    PERMISSION_ERROR = "permission_error"
    GENERAL_ERROR = "general_error"


class ErrorResponse:
    """统一错误响应类"""
    
    def __init__(
        self,
        success: bool = False,
        error_type: Optional[Union[str, ErrorType]] = None,
        error_code: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[str] = None,
        original_exception: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        初始化错误响应
        
        Args:
            success: 是否成功，默认为False
            error_type: 错误类型
            error_code: 错误代码
            message: 错误消息
            details: 错误详细信息
            original_exception: 原始异常对象
            context: 错误上下文信息
        """
        self.success = success
        self.error_type = error_type.value if isinstance(error_type, ErrorType) else error_type
        self.error_code = error_code
        self.message = message
        self.details = details
        self.original_exception = original_exception
        self.context = context or {}
        
        # 如果提供了原始异常但没有指定消息，使用异常消息
        if original_exception and not message:
            self.message = str(original_exception)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将错误响应转换为字典
        
        Returns:
            错误响应字典
        """
        response = {
            "success": self.success
        }
        
        # 添加错误信息
        if self.error_type:
            response["error_type"] = self.error_type
        
        if self.error_code:
            response["error_code"] = self.error_code
            
        if self.message:
            response["message"] = self.message
            
        if self.details:
            response["details"] = self.details
            
        if self.context:
            response["context"] = self.context
            
        return response
    
    def to_json(self) -> str:
        """
        将错误响应转换为JSON字符串
        
        Returns:
            错误响应JSON字符串
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)


def handle_exception(
    exception: Exception,
    error_type: Optional[Union[str, ErrorType]] = None,
    error_code: Optional[str] = None,
    message: Optional[str] = None,
    details: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    include_traceback: bool = False
) -> ErrorResponse:
    """
    处理异常并返回统一的错误响应
    
    Args:
        exception: 要处理的异常
        error_type: 错误类型
        error_code: 错误代码
        message: 自定义错误消息
        details: 自定义错误详细信息
        context: 错误上下文信息
        include_traceback: 是否包含堆栈跟踪
        
    Returns:
        统一的错误响应对象
    """
    # 如果没有指定错误类型，根据异常类型推断
    if not error_type:
        error_type = infer_error_type(exception)
    
    # 如果没有指定详细信息，使用堆栈跟踪
    if not details and include_traceback:
        details = traceback.format_exc()
    
    # 创建错误响应
    error_response = ErrorResponse(
        success=False,
        error_type=error_type,
        error_code=error_code,
        message=message,
        details=details,
        original_exception=exception,
        context=context
    )
    
    return error_response


def infer_error_type(exception: Exception) -> ErrorType:
    """
    根据异常推断错误类型
    
    Args:
        exception: 异常对象
        
    Returns:
        推断的错误类型
    """
    error_message = str(exception).lower()
    
    # 数据库连接错误
    if any(keyword in error_message for keyword in [
        "connection", "连接", "unable to open", "无法打开", 
        "timeout", "超时", "could not connect", "无法连接"
    ]):
        return ErrorType.DATABASE_CONNECTION_ERROR
    
    # 数据库表不存在错误
    if any(keyword in error_message for keyword in [
        "no such table", "表不存在", "relation", "doesn't exist", 
        "table", "not found", "未找到"
    ]):
        return ErrorType.DATABASE_TABLE_NOT_FOUND
    
    # SQL语法错误
    if any(keyword in error_message for keyword in [
        "syntax error", "语法错误", "sql", "query"
    ]):
        return ErrorType.SQL_SYNTAX_ERROR
    
    # 数据库查询错误
    if any(keyword in error_message for keyword in [
        "database", "数据库", "sqlite", "mysql", "postgresql"
    ]):
        return ErrorType.DATABASE_ERROR
    
    # 表达式评估错误
    if any(keyword in error_message for keyword in [
        "expression", "表达式", "evaluation", "评估", "eval"
    ]):
        return ErrorType.EXPRESSION_EVALUATION_ERROR
    
    # 认证错误
    if any(keyword in error_message for keyword in [
        "authentication", "认证", "auth", "login", "登录"
    ]):
        return ErrorType.AUTHENTICATION_ERROR
    
    # 权限错误
    if any(keyword in error_message for keyword in [
        "permission", "权限", "access denied", "拒绝访问"
    ]):
        return ErrorType.PERMISSION_ERROR
    
    # 默认为一般错误
    return ErrorType.GENERAL_ERROR


def create_error_response(
    error_type: Union[str, ErrorType],
    message: str,
    error_code: Optional[str] = None,
    details: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """
    创建错误响应
    
    Args:
        error_type: 错误类型
        message: 错误消息
        error_code: 错误代码
        details: 错误详细信息
        context: 错误上下文信息
        
    Returns:
        错误响应对象
    """
    return ErrorResponse(
        success=False,
        error_type=error_type,
        error_code=error_code,
        message=message,
        details=details,
        context=context
    )


def create_database_error_response(
    message: str,
    error_code: Optional[str] = None,
    details: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """
    创建数据库错误响应
    
    Args:
        message: 错误消息
        error_code: 错误代码
        details: 错误详细信息
        context: 错误上下文信息
        
    Returns:
        数据库错误响应对象
    """
    return create_error_response(
        ErrorType.DATABASE_ERROR,
        message,
        error_code,
        details,
        context
    )


def create_database_connection_error_response(
    message: str,
    error_code: Optional[str] = None,
    details: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """
    创建数据库连接错误响应
    
    Args:
        message: 错误消息
        error_code: 错误代码
        details: 错误详细信息
        context: 错误上下文信息
        
    Returns:
        数据库连接错误响应对象
    """
    return create_error_response(
        ErrorType.DATABASE_CONNECTION_ERROR,
        message,
        error_code,
        details,
        context
    )


def create_database_table_not_found_response(
    message: str,
    error_code: Optional[str] = None,
    details: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """
    创建数据库表不存在错误响应
    
    Args:
        message: 错误消息
        error_code: 错误代码
        details: 错误详细信息
        context: 错误上下文信息
        
    Returns:
        数据库表不存在错误响应对象
    """
    return create_error_response(
        ErrorType.DATABASE_TABLE_NOT_FOUND,
        message,
        error_code,
        details,
        context
    )


def create_expression_evaluation_error_response(
    message: str,
    error_code: Optional[str] = None,
    details: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """
    创建表达式评估错误响应
    
    Args:
        message: 错误消息
        error_code: 错误代码
        details: 错误详细信息
        context: 错误上下文信息
        
    Returns:
        表达式评估错误响应对象
    """
    return create_error_response(
        ErrorType.EXPRESSION_EVALUATION_ERROR,
        message,
        error_code,
        details,
        context
    )


def create_sql_syntax_error_response(
    message: str,
    error_code: Optional[str] = None,
    details: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> ErrorResponse:
    """
    创建SQL语法错误响应
    
    Args:
        message: 错误消息
        error_code: 错误代码
        details: 错误详细信息
        context: 错误上下文信息
        
    Returns:
        SQL语法错误响应对象
    """
    return create_error_response(
        ErrorType.SQL_SYNTAX_ERROR,
        message,
        error_code,
        details,
        context
    )