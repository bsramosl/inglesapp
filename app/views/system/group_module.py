import json
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from app.models import Module, AccessGroupModule, AccessGroup
from helpers.decorators import add_data
from django.core.cache import cache

@csrf_exempt
@login_required(redirect_field_name='ret', login_url='/login')
# @secure_module
# @last_access
@transaction.atomic()
def view(request):
    data = {}
    add_data(request, data)
    data['person'] = persona = request.session['person']
    if request.method == 'POST':
        action = request.POST['action']


        if action == 'del':
            try:
                id = request.POST.get('id', None)
                module = AccessGroupModule.objects.get(pk=id)
                module.status = False
                module.save()
                return JsonResponse({"result": True, "message": "Delete successfully."})
            except Exception as ex:
                return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

        if action == 'save_access_groups':
            try:
                id = request.POST.get('module_id', None)
                groups = json.loads(request.POST.get('config', '[]'))
                for acces in groups:
                    permission, created = AccessGroupModule.objects.get_or_create(module_id=id, access_group_id=acces['group_id'])
                    permission.can_view=acces['can_view']
                    permission.can_edit=acces['can_view']
                    permission.can_delete=acces['can_view']
                    permission.can_manage=acces['can_view']
                    permission.save()
                cache.delete_pattern('menus_*')

                return JsonResponse({"result": True, "message": "Updated successfully."})
            except Exception as ex:
                return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

        return JsonResponse({"result": False, 'mesagge':'Error'})
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'edit':
                try:
                    data['title'] = u'Edit Access Group'
                    data['id'] = id = request.GET.get('id',None)
                    data['action'] = 'edit'
                    module = Module.objects.get(pk=id)
                    groups = AccessGroup.objects.all()
                    groups_data = []
                    for group in groups:
                        agm = AccessGroupModule.objects.filter(module=module, access_group=group).first()
                        groups_data.append({
                            'id': group.id,
                            'name':group.group.name,
                            'description': group.description,
                            'can_view': agm.can_view if agm else False,
                            'can_edit': agm.can_edit if agm else False,
                            'can_delete': agm.can_delete if agm else False,
                            'can_manage': agm.can_manage if agm else False,
                        })

                    data['groups_data'] = groups_data
                    data['module'] = module
                    template = get_template("system/modal/form_access_module.html")
                    json_content = template.render(data)
                    return JsonResponse({"result": True, 'data': json_content})
                except Exception as ex:
                    return JsonResponse({"result": False, "mesagge": f"Error {ex}"})
        else:
            data['tittle'] = u"Groups of Modules"
            data['page_subtitle'] = u"Groups of Modules"
            data['title_table'] = u"Groups of Modules"
            result = []
            modulos = Module.objects.filter(status=True)
            for modulo in modulos:
                grupos_modulo = []
                agms = AccessGroupModule.objects.select_related('access_group__group').filter(module=modulo)
                for agm in agms:
                    permisos = [perm.code_name for perm in agm.permissions.all()]
                    grupos_modulo.append({
                        "group_id": agm.id,
                        "group": agm.access_group.group.name,
                        "description": agm.access_group.description,
                        "can_view": agm.can_view,
                        "can_edit": agm.can_edit,
                        "can_delete": agm.can_delete,
                        "can_manage": agm.can_manage,
                        "permissions": permisos,
                    })
                result.append({
                    "module": modulo,
                    "groups": grupos_modulo
                })
            data['list'] = result
            return render(request, "system/group_module_view.html", data)