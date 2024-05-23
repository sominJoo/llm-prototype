# Response 처리
from rest_framework.response import Response
from functools import wraps

def auto_response(func):
    @wraps(func)
    def wrapped_view(*args, **kwargs):
        result = func(*args, **kwargs)
        if not isinstance(result, Response):
            result = Response(result)
        return result
    return wrapped_view