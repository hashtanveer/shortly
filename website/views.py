from django.shortcuts import render, redirect
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
            return Response({"success" : False,"errors" : form.errors}
                            ,status=status.HTTP_400_BAD_REQUEST)

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

        return Response({"success": True ,"code" : shortlink.code})
    
class ShortLinkView(APIView):
    def get(self, request,code ,format=None):
        qs = ShortLink.objects.filter(code=code)
        if not qs.count():
            return render(request,'website/404.html')

        shortlink = qs.first()
        if not shortlink.password_protected:
            return redirect(shortlink.url)
        return render(request, 'website/askPassword.html',context={'post_url' : f"/{shortlink.code}/"})

    def post(self, request, code, format=None):
        qs = ShortLink.objects.filter(code=code)
        if not qs.count():
            return render(request,'website/404.html')

        shortlink = qs.first()
        if shortlink.check_password(request.data.get('password')):
            return redirect(shortlink.url)

        return render(request,'website/askPassword.html', context={'error_message': "Incorrect Password"})


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