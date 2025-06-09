from django.urls import re_path
from app.views.common import *
from app.views.system import module, system_rol

urlpatterns = [
    re_path(r'^login/', HybridLoginView.as_view(), name='login'),
    re_path('logout/', HybridLogoutView.as_view(), name='logout'),
    re_path('home/', HomeView.as_view(), name='home'),
    re_path('module/',module.view , name='module'),
    re_path('system_rol/', system_rol.view, name='system_rol'),

]