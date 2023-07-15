from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .forms import ShortLinkCreateForm, ListShortLinkForm
from .models import ShortLink,Profile ,get_guest_profile
from .utils import get_short_code
from .serializers import ShortLinkSerializer

class HomePageView(APIView):
    def get(self, request, format=None):
        return render(request,'website/home.html')
    
class LoginPageView(APIView):
    def get(self, request, format=None):
        return render(request, 'account/login.html')

class CreateShortLinkView(APIView):
    def post(self, request, format=None):
        form = ShortLinkCreateForm(request.data)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        kwargs = form.cleaned_data
        if request.user.is_authenticated:
            kwargs['profile'] = request.user.profile
        else:
            kwargs['profile']= Profile.objects.get(id=get_guest_profile())

        #Check qouta 
        if not kwargs['profile'].can_make_shortlink():
            return Response({"errors":["Your profile crossed limit for Link generation"]})

        shortcode = get_short_code()
        kwargs['code'] = shortcode
        shortlink = ShortLink.objects.create(**kwargs)

        return Response(shortlink.code)

class ListShortLinkView(APIView):
    permission_classes = [ IsAuthenticated ]

    def get(self, request, format=None):
        form = ListShortLinkForm(request.GET)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        skip = form.cleaned_data.get('skip')
        amount = form.cleaned_data.get('amount')

        profile = request.user.profile
        qs = ShortLink.objects.filter(profile=profile).order_by('created_at')[skip:skip+amount]
        shortlinks = ShortLinkSerializer(qs, many=True).data

        return Response({"shortlinks" : shortlinks}, status=status.HTTP_200_OK)