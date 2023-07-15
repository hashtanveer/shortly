from django.shortcuts import render
from rest_framework.views import APIView

class HomePageView(APIView):
    def get(self, request, format=None):
        return render(request,'website/home.html')