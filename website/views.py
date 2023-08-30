from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .forms import ShortLinkCreateForm, ListShortLinkForm, ShortLinkEditor
from .models import ShortLink,Profile ,get_guest_profile
from .utils import get_short_code
from .serializers import ShortLinkSerializer

class HomePageView(APIView):
    def get(self, request, format=None):
        return render(request,'website/index.html')
    
class LoginPageView(APIView):
    def get(self, request, format=None):
        return render(request, 'account/signin.html')

class SignupView(APIView):
    def get(self, request, format=None):
        return render(request, 'account/signup.html')

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
        qs = ShortLink.objects.filter(profile=profile).order_by('-created_at')
        asked = qs[skip:skip+amount]
        shortlinks = ShortLinkSerializer(asked, many=True).data

        total = qs.count()
        prev_url, next_url = None, None
        if skip+amount < total:
            next_url = f"?amount={amount}&skip={skip+amount}"
        if skip !=0:
            prev_url = f"?amount={amount}&skip={skip-amount}"

        skips = range(0,total, amount)
        return render(request, 'website/urlList.html',{'shortlinks' : shortlinks, 'prev_url': prev_url, 'next_url': next_url, 'total': total, 'amount': amount, 'skips': skips, 'current' : skip})

class URLEditorView(APIView):
    permission_classes = [ IsAuthenticated ]
    def get(self, request, code ,format=None):
        qs = ShortLink.objects.filter(code=code, profile= request.user.profile)

        if not qs.count():
            return render(request, 'website/404.html')
        
        shortlink = qs[0]
        return render(request, 'website/UrlView.html', {'shortlink' : shortlink})
    
    def post(self, request, code ,format=None):
        qs = ShortLink.objects.filter(code=code, profile= request.user.profile)

        if not qs.count():
            return render(request, 'website/404.html')

        shortlink = qs[0]

        form = ShortLinkEditor(request.data)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

        action = form.cleaned_data.get('action')
        print(action)
        print(reverse('website:myurls'))
        if action == 'deleteUrl':
            shortlink.delete()
            return redirect(reverse('website:myurls'))
        elif action == 'removePassword':
            shortlink.remove_password()
        elif action == 'changePassword':
            #shortlink.set_password_requirement(form.cleaned_data.get('password_protected'))
            print(form.cleaned_data.get('password_protected'))
            print(form.cleaned_data.get('password'))
            shortlink.password = form.cleaned_data.get('password')
            shortlink.password_protected = form.cleaned_data.get('password_protected')
            shortlink.save()
            

        return redirect(request.path_info)


    
def URLDetail(request, code):
    return render(request, 'website/UrlViewHolder.html', {'code' : code})

def myUrls(request):
    form = ListShortLinkForm(request.GET)
    form.is_valid()
    skip = form.cleaned_data.get('skip')
    amount = form.cleaned_data.get('amount')

    return render(request, 'website/myUrls.html', {'amount' : amount, 'skip': skip})