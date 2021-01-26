from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user import views

router = DefaultRouter()
router.register('login', views.LoginUserView)
# router.register('logout', views.LogouUsertView)
# router.register('profile', views.UserProfileView)
# router.register('change-password', views.ChangeUserPasswordView, 'change_password')
# router.register('users', views.ManageUserViewset)

app_name = 'user'

urlpatterns = [
    path('', include(router.urls))
]
