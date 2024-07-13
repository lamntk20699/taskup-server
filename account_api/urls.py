from django.urls import path
from django.contrib import admin
from . import views
from .views import RegisterView, RetrieveUserView
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.HomeView.as_view(), name ='home'),
    path('logout/', views.LogoutView.as_view(), name ='logout'),
    path('register/', RegisterView.as_view()),
    path('me/', RetrieveUserView.as_view()),
    path(
        'token/',
        views.ObtainTokenResponseView.as_view(),
        name ='token_obtain_pair'
    ),
]