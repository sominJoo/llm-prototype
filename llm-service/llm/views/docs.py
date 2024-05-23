from rest_framework.views import APIView
from llmapp.response import auto_response

class DocsAPIView(APIView):
    @auto_response
    def get(self, request):
        return "hello world"
