from django.urls import path
from .views import HomePageView, LoginPageView

app_name = "website"

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('login/', LoginPageView.as_view(), name='login'),
]