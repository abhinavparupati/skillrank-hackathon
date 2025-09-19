"""
Error handler utility for consistent error management.
"""
import logging
from typing import Dict, Any, Optional
from flask import jsonify
import traceback
from datetime import datetime

class ErrorHandler:
    """Handles errors consistently across the application"""
    
    def __init__(self):
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def handle_error(self, error: Exception, context: str = "An error occurred",
                    include_traceback: bool = True) -> tuple:
        """Handle error and return standardized response"""
        error_message = str(error)
        error_type = self._classify_error(error)
        
        # Log the error
        self.logger.error(f"{context}: {error_message}")
        if include_traceback:
            self.logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Create response
        response = {
            'success': False,
            'error': error_message,
            'error_type': error_type,
            'context': context,
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'response_type': 'error'
            }
        }
        
        # Determine HTTP status code
        status_code = self._get_status_code(error_type)
        
        return jsonify(response), status_code
    
    def _classify_error(self, error: Exception) -> str:
        """Classify error type for consistent handling"""
        error_name = type(error).__name__
        error_message = str(error).lower()
        
        # Database errors
        if 'sqlite' in error_name.lower() or 'database' in error_message:
            if 'syntax' in error_message or 'near' in error_message:
                return 'sql_syntax_error'
            elif 'no such table' in error_message or 'no such column' in error_message:
                return 'sql_schema_error'
            elif 'locked' in error_message:
                return 'database_locked_error'
            else:
                return 'database_error'
        
        # API errors
        if 'timeout' in error_message:
            return 'timeout_error'
        elif 'connection' in error_message:
            return 'connection_error'
        elif 'authentication' in error_message or 'unauthorized' in error_message:
            return 'authentication_error'
        elif 'rate limit' in error_message:
            return 'rate_limit_error'
        
        # Validation errors
        if error_name in ['ValueError', 'TypeError']:
            return 'validation_error'
        
        # File errors
        if error_name in ['FileNotFoundError', 'PermissionError']:
            return 'file_error'
        
        # Network errors
        if 'requests' in error_name.lower() or 'http' in error_name.lower():
            return 'network_error'
        
        # JSON errors
        if 'json' in error_name.lower():
            return 'json_error'
        
        return 'general_error'
    
    def _get_status_code(self, error_type: str) -> int:
        """Get appropriate HTTP status code for error type"""
        status_codes = {
            'validation_error': 400,
            'authentication_error': 401,
            'authorization_error': 403,
            'not_found_error': 404,
            'rate_limit_error': 429,
            'sql_syntax_error': 400,
            'sql_schema_error': 400,
            'timeout_error': 408,
            'file_error': 404,
            'json_error': 400,
            'network_error': 502,
            'database_error': 500,
            'database_locked_error': 503,
            'connection_error': 503,
            'general_error': 500
        }
        
        return status_codes.get(error_type, 500)
    
    def validate_request_data(self, data: Dict, required_fields: list) -> Optional[str]:
        """Validate request data and return error message if invalid"""
        if not data:
            return "Request body is required"
        
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            return f"Missing required fields: {', '.join(missing_fields)}"
        
        return None
    
    def log_info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def log_warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def log_error(self, message: str):
        """Log error message"""
        self.logger.error(message)