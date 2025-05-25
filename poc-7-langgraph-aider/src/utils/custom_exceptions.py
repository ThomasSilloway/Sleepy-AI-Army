from enum import Enum

class NodeOperation(Enum): 
    LLM_CALL = "LLM Call"
    FILE_WRITE = "File Write"
    CHANGELOG_UPDATE = "Changelog Update" 
    GIT_COMMIT = "Git Commit" 
    VALIDATION = "Validation"
    CONFIGURATION = "Configuration"
    UNEXPECTED = "Unexpected"
    # Add other specific operations as needed

class NodeOperationError(Exception):
    """Base class for custom exceptions in node operations."""
    def __init__(self, message: str, operation_type: NodeOperation, original_exception: Exception = None, **kwargs):
        super().__init__(message)
        self.message = message # The specific message for this instance
        self.operation_type = operation_type
        self.original_exception = original_exception
        self.additional_data = kwargs

    def __str__(self):
        return self.message

class LLMError(NodeOperationError): 
    def __init__(self, message: str, original_exception: Exception = None, **kwargs):
        super().__init__(message, NodeOperation.LLM_CALL, original_exception, **kwargs)

class FileError(NodeOperationError): 
    def __init__(self, message: str, original_exception: Exception = None, **kwargs):
        super().__init__(message, NodeOperation.FILE_WRITE, original_exception, **kwargs)

class ChangelogError(NodeOperationError): 
    def __init__(self, message: str, original_exception: Exception = None, **kwargs):
        super().__init__(message, NodeOperation.CHANGELOG_UPDATE, original_exception, **kwargs)

class GitError(NodeOperationError): 
    def __init__(self, message: str, original_exception: Exception = None, **kwargs):
        super().__init__(message, NodeOperation.GIT_COMMIT, original_exception, **kwargs)
        
class ValidationError(NodeOperationError):
     def __init__(self, message: str, original_exception: Exception = None, **kwargs): 
        super().__init__(message, NodeOperation.VALIDATION, original_exception, **kwargs)

class NodeConfigError(NodeOperationError): 
     def __init__(self, message: str, original_exception: Exception = None, **kwargs):
        super().__init__(message, NodeOperation.CONFIGURATION, original_exception, **kwargs)

# It might be useful to have a generic "ServiceCallError" or more specific ones
# if other services are frequently used and need distinct error handling.
# For now, the above cover the primary operations in manifest_create.py.
