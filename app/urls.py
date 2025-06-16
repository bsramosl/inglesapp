from django.urls import re_path

from app.views.common import *
from app.views.language import language, language_level
from app.views.system import module, system_rol, profile_users, category, access_group, group_module

urlpatterns = [
    re_path(r'^login/', HybridLoginView.as_view(), name='login'),
    re_path('logout/', HybridLogoutView.as_view(), name='logout'),
    re_path(r'^module/$',module.view , name='module'),
    re_path(r'^system_rol/$', system_rol.view, name='system_rol'),
    re_path(r'^user_profile/$', profile_users.view, name='user_profile'),
    re_path(r'^module_category/$', category.view, name='module_categoty'),
    re_path(r'^access_group/$', access_group.view, name='access_group'),
    re_path(r'^group_module/$', group_module.view, name='group_module'),
    re_path(r'^language/$', language.view, name='language'),
    re_path(r'^language_level/$', language_level.view, name='language_level'),

    re_path('', HomeView.as_view(), name='home'),

]