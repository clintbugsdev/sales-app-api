from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user import views

router = DefaultRouter()
router.register('users', views.ManageUserViewset)

app_name = 'user'

urlpatterns = [
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout/', views.LogoutUserView.as_view(), name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path(
        'change-password/',
        views.ChangePasswordView.as_view(),
        name='change-password'
    ),
    path('', include(router.urls))
]
