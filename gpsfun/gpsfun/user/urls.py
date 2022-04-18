"""
urls for app user
"""

from django.urls import path
from gpsfun.user.views import (user_profile, user_profile_edit)


urlpatterns = [
    path('profile/', user_profile, name="user-profile"),
    path('my/profile/edit/', user_profile_edit,
        name="user-profile-edit"),
]
