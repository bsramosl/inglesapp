from django.db.models import Q

from app.models import ProfileSystemRol, AccessGroupModule, ModuleCategory, ProfileUser, Person, Module
from config.settings import TOKEN_DEFAULT_APP_NAME
from datetime import datetime


def menus(perfil, modulo_activo=None):
    if not perfil:
        return {"categories": []}

    modulos = perfil.my_modules()

    categorias_dict = {}

    for modulo in modulos:
        categoria = modulo.category

        if categoria.id not in categorias_dict:
            categorias_dict[categoria.id] = {
                "id": categoria.id,
                "name": categoria.name,
                "icon": categoria.icon if categoria.icon else 'bx-home-circle',
                "order": categoria.order,
                "modules": []
            }
        categorias_dict[categoria.id]["modules"].append({
            "id": modulo.id,
            "name": modulo.name,
            "url": modulo.url,
            "icon": modulo.icon if modulo.icon else 'bx-file',
            "active": modulo_activo and modulo_activo.get('id') == modulo.id
        })
    categorias_ordenadas = sorted(categorias_dict.values(), key=lambda x: x['order'])

    return {
        "categories": categorias_ordenadas,
        "isActivePrincipal": True
    }


def add_data(request, data):
    if 'person_id' not in request.session:
        if not request.user.is_authenticated:
            raise Exception('User no authenticated in the system')
        ePerson = Person.objects.get(user=request.user)
        request.session['person_id'] = ePerson.id
    else:
        ePerson = Person.objects.get(id=request.session['person_id'])

    perfilprincipal = request.session.get('profilemain')
    data['perfilprincipal'] = perfilprincipal


    request.session.setdefault('route', [['/', 'Home']])
    data['route'] = request.session['route']


    modulo = None
    url = request.path[1:]

    modulo_qs = Module.objects.filter(url=url, is_active=True, status=True)
    if modulo_qs.exists():
        modulo = modulo_qs.values("id", "url", "name").first()
        data['module_active'] = modulo

        ruta_url = ['/' + modulo['url'], modulo['name']]
        if ruta_url not in data['route']:
            if len(data['route']) >= 8:
                data['route'].pop(1)
            data['route'].append(ruta_url)
            request.session['route'] = data['route']

    data["url_back"] = '/'
    request.session['url_back'] = [data["url_back"]]

    data['menus'] = menus(perfilprincipal, modulo) if perfilprincipal else {"categories": []}

    data['can_edit'] = True
    data['can_delete'] = True
    data['active'] = True
    eNotifications = perfilprincipal.my_notifications()
    data['eNotifications'] = eNotifications[:10]
    data['totalNotifications'] = eNotifications.count()

    return data
