from django import template
from django.core.cache import cache

register = template.Library()

@register.filter(name='has_permission')
def has_permission(profile, permission_name):
    if not profile or not hasattr(profile, 'permissions'):
        return False

    if permission_name in ['can_view', 'can_edit', 'can_delete', 'can_manage']:
        return getattr(profile.permissions, permission_name, False)

    return permission_name in profile.permissions