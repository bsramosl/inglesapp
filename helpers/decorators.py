from django.core.exceptions import PermissionDenied

from app.models import Person, Module, Notification
from django.core.cache import cache
from django.db import transaction
from django.forms import model_to_dict

from config import settings


def add_data(request, data):
    try:
        if 'person_id' not in request.session:
            if not request.user.is_authenticated:
                raise PermissionDenied('User not authenticated in the system')

            with transaction.atomic():
                ePerson = Person.objects.select_related('user').get(user=request.user)
                request.session['person_id'] = ePerson.id
                request.session['person'] = ePerson
        else:
            cache_key = f'person_{request.session["person_id"]}'
            ePerson = cache.get(cache_key)

            if not ePerson:
                ePerson = Person.objects.select_related('user').get(id=request.session['person_id'])
                cache.set(cache_key, ePerson, timeout=3600)

        data['person'] = ePerson

        if 'profilemain' not in request.session:
            profilemain = ePerson.main_profile()
            if profilemain:
                request.session['profilemain'] = {
                    'id': profilemain.id,
                    'name': str(profilemain),
                    'is_main': profilemain.is_main
                }

        perfilprincipal = request.session.get('profilemain')
        data['perfilprincipal'] = perfilprincipal

        request.session.setdefault('route', [['/', 'Home']])
        data['route'] = request.session['route']

        url = request.path[1:]
        cache_key_module = f'module_{url}'
        modulo = cache.get(cache_key_module)

        if not modulo:
            modulo = Module.objects.filter(url=url, is_active=True, status=True) \
                .values("id", "url", "name").first()
            if modulo:
                cache.set(cache_key_module, modulo, timeout=3600)

        if modulo:
            data['module_active'] = modulo
            ruta_url = ['/' + modulo['url'], modulo['name']]

            if ruta_url not in data['route']:
                if len(data['route']) >= 8:
                    data['route'].pop(1)
                data['route'].append(ruta_url)
                request.session['route'] = data['route']

        if perfilprincipal:
            cache_key_menus = f'menus_{perfilprincipal.id}_{modulo["id"] if modulo else "none"}'
            data['menus'] = cache.get(cache_key_menus)

            if not data['menus']:
                data['menus'] = get_menus_with_permissions(perfilprincipal.id, modulo)
                cache.set(cache_key_menus, data['menus'], timeout=1800)  # 30 min
            data['totalNotifications'] = Notification.objects.filter(profile_id=perfilprincipal.id, is_read=False).count()
        else:
            data['menus'] = {"categories": []}
            data['totalNotifications'] = 0

        data["url_back"] = '/'
        request.session['url_back'] = [data["url_back"]]

        data.update({
            'can_edit': True,
            'can_delete': True,
            'active': True,
            'debug': settings.DEBUG
        })

        return data

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in add_data: {str(e)}", exc_info=True)
        return {
            'person': None,
            'perfilprincipal': None,
            'menus': {"categories": []},
            'route': [['/', 'Home']],
            'url_back': '/',
            'can_edit': False,
            'can_delete': False,
            'active': True,
            'totalNotifications': 0
        }


def get_menus_with_permissions(profile_id, active_module=None):
    from app.models import ProfileSystemRol, Module
    profile = ProfileSystemRol.objects.filter(id=profile_id).first()
    if not profile:
        return {"categories": []}

    accessible_modules = Module.objects.filter(
        accessgroupmodule__access_group__in=profile.profile.access_groups.all(),
        accessgroupmodule__can_view=True,
        is_active=True,
        status=True
    ).select_related('category').prefetch_related(
        'accessgroupmodule_set',
        'accessgroupmodule_set__permissions'
    ).order_by('category__order', 'order').distinct()

    categories_dict = {}
    for module in accessible_modules:
        agm = module.accessgroupmodule_set.filter(
            access_group__in=profile.profile.access_groups.all()
        ).first()

        if not agm:
            continue

        category = module.category
        if category.id not in categories_dict:
            categories_dict[category.id] = {
                "id": category.id,
                "name": category.name,
                "icon": category.icon or 'bx-home-circle',
                "order": category.order,
                "modules": []
            }

        categories_dict[category.id]["modules"].append({
            "id": module.id,
            "name": module.name,
            "url": module.url,
            "icon": module.icon or 'bx-file',
            "active": active_module and active_module.get('id') == module.id,
            "permissions": {
                'can_edit': agm.can_edit,
                'can_delete': agm.can_delete,
                'can_manage': agm.can_manage
            }
        })

    categories_sorted = sorted(categories_dict.values(), key=lambda x: x['order'])
    return {
        "categories": categories_sorted,
        "isActivePrincipal": True
    }
