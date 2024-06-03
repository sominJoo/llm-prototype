# Response 처리
from rest_framework.response import Response
from functools import wraps

def auto_response(func):
    @wraps(func)
    def wrapped_view(*args, **kwargs):
        result = func(*args, **kwargs)

        if not isinstance(result, Response):
            responseData = setResponseData(result)
            result = Response(responseData)
        return result
    return wrapped_view

def setResponseData(result):
    data = {
        "result": 1,
        "data": result,
        "errorMessage": ""
    }

    # Exception 확인
    if isinstance(result, Exception):
        data["result"] = 0
        data["data"] = None
        data["errorMessage"] = "오류 발생, 관리자에게 문의하세요."

    return data