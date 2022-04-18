"""gpsfun URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.views.i18n import JavaScriptCatalog
from gpsfun.main.views import homepage, update


urlpatterns = [
    path('', homepage),
    path('login/', LoginView.as_view(
        template_name='registration/login.html'), name="login"),
    path('logout/', LogoutView.as_view(
        next_page='home'), name='log-out'),
    path('admin/', admin.site.urls),
    path('home/', homepage, name='home'),
    path('update/', update, name='update'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('auth/', include('django.contrib.auth.urls')),
    path('geocaching/su/', include('gpsfun.geocaching_su_stat.urls')),
    path('geocaching/map/', include('gpsfun.map.urls')),
    path('geokrety/map/', include('gpsfun.geokret.urls')),
    path('geokrety/api/', include('gpsfun.geokret.urls')),
    path('user/', include('gpsfun.user.urls')),
    path('geoname/', include('gpsfun.geoname.urls')),
    path('gpsfun-admin/', include('gpsfun.gpsfun_admin.urls')),
    path('accounts/', include('django_registration.backends.activation.urls')),

    path('carpathians/routes/', include('gpsfun.carpathians.urls')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
