from django.urls import path
from . import views
from .views import RegisterView, RetrieveUserView

urlpatterns = [
    path('home/', views.HomeView.as_view(), name ='home'),
    path('logout/', views.LogoutView.as_view(), name ='logout'),
    path('register', RegisterView.as_view()),
    path('me', RetrieveUserView.as_view()),
]