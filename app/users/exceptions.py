from fastapi import HTTPException, status


class LoginRequiredException(HTTPException):
    pass


class InvalidUserIDException(Exception):
    pass


class UserHasAccountException(Exception):
    """
    User already has account
    """
    
    
class InvalidEmailException(Exception):
    """
    Invalid email
    """
    
    
class InvalidUserIDException(Exception):
    """Invalid user id"""