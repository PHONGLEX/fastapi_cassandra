from fastapi import HTTPException, status


class LoginRequiredException(HTTPException):
    pass