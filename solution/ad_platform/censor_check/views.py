from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache



class CensorStatusView(APIView):
    def post(self, request, format=None):
        if "censor_status" not in request.data:
            return Response({"error": "censor_status is required"}, status=status.HTTP_400_BAD_REQUEST)
        if request.data["censor_status"] not in [True, False]:
            return Response({"error": "censor_status must be True or False"}, status=status.HTTP_400_BAD_REQUEST)
        cache.set('censor_status', request.data["censor_status"])
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def get(self, request, format=None):
        return Response({"censor_status": cache.get('censor_status', False)}, status=status.HTTP_200_OK)


class CensorWordsView(APIView):
    def get(self, request, format=None):
        return Response(cache.get('bad_words', []), status=status.HTTP_200_OK)

    def post(self, request, format=None):
        if "words" not in request.data:
            return Response({"error": "words is required"}, status=status.HTTP_400_BAD_REQUEST)
        cache.set('bad_words', request.data["words"])
        return Response(cache.get('bad_words', []), status=status.HTTP_200_OK)

