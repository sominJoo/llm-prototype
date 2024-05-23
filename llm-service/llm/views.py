# API에 대한 동작
from rest_framework.views import APIView

from llmapp.response import auto_response


class LlmAPIView(APIView):
    @auto_response
    def get(self, request):
        return "hello world"
