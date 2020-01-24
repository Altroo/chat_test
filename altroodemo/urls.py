#! -*- coding: utf-8 -*-

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
 
urlpatterns = [

    path('admin/', admin.site.urls),
    path('altroochat/', include('altroochat.urls')),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), {'next_page': '/'}, name='logout', ),
    path('', login_required(TemplateView.as_view(template_name='core/chat.html')), name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
