from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db import transaction
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from app.forms import GroupForm, AccessGroupForm
from app.models import AccessGroup
from helpers.decorators import add_data

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

        if action == 'create_group':
            try:
                form = GroupForm(request.POST)
                if form.is_valid():
                    Group.objects.create(**form.cleaned_data)
                    return JsonResponse({"result": True, "message": "Group created successfully."})
                else:
                    return JsonResponse({"result": False, "message": "Invalid data.", "errors": form.errors})
            except Exception as ex:
                return JsonResponse({"result": False, "message": f"Error: {ex}"})

        if action == 'edit_group':
            try:
                id = request.POST.get('id', None)
                module = Group.objects.get(pk=id)
                form = GroupForm(request.POST)
                if form.is_valid():
                    for field, value in form.cleaned_data.items():
                        setattr(module, field, value)
                    module.save()
                    return JsonResponse({"result": True, "message": "Group updated successfully."})
                else:
                    return JsonResponse({"result": False, "message": "Invalid form data.", "errors": form.errors})
            except Exception as ex:
                return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

        if action == 'create':
            try:
                form = AccessGroupForm(request.POST)
                if form.is_valid():
                    group = AccessGroup.objects.create(group=form.cleaned_data['group'],description=form.cleaned_data['description'])
                    return JsonResponse({"result": True, "message": "Group created successfully."})
                else:
                    return JsonResponse({"result": False, "message": "Invalid data.", "errors": form.errors})
            except Exception as ex:
                return JsonResponse({"result": False, "message": f"Error: {ex}"})

        if action == 'del':
            try:
                id = request.POST.get('id', None)
                module = AccessGroup.objects.get(pk=id)
                module.status = False
                module.save()
                return JsonResponse({"result": True, "message": "Category delete successfully."})
            except Exception as ex:
                return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

        if action == 'edit':
            try:
                group_id = request.POST.get('id')
                group = AccessGroup.objects.get(pk=group_id)
                group.description = request.POST.get('description')
                group.save()
                return JsonResponse({"result": True, "message": "Group updated successfully."})
            except Exception as ex:
                return JsonResponse({"result": False, "message": f"Error: {ex}"})


        return JsonResponse({"result": False, 'mesagge':'Error'})
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'edit_group':
                try:
                    data['title'] = u'Edit Group'
                    data['id'] = id = request.GET.get('id',None)
                    data['action'] = 'edit_group'
                    module = Group.objects.get(pk=id)
                    data['form'] =  GroupForm(initial=model_to_dict(module))
                    template = get_template("layout/form.html")
                    json_content = template.render(data)
                    return JsonResponse({"result": True, 'data': json_content})
                except Exception as ex:
                    return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

            if action == 'create_group':
                data['title'] = u'Create Group'
                data['form'] = GroupForm()
                data['action'] = 'create_group'
                template = get_template("layout/form.html")
                json_content = template.render(data)
                return JsonResponse({"result":True, "data":json_content})

            if action == 'edit':
                try:
                    data['title'] = u'Edit Group'
                    data['id'] = id = request.GET.get('id',None)
                    data['action'] = 'edit'
                    group = AccessGroup.objects.get(pk=id)
                    form = AccessGroupForm(
                        initial=model_to_dict(group))
                    form.fields['group'].disabled = True
                    data['form'] = form
                    template = get_template("layout/form.html")
                    json_content = template.render(data)
                    return JsonResponse({"result": True, 'data': json_content})
                except Exception as ex:
                    return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

            if action == 'create':
                try:
                    data['title'] = u'Create Group'
                    data['form'] = AccessGroupForm()
                    data['action'] = 'create'
                    template = get_template("layout/form.html")
                    json_content = template.render(data)
                    return JsonResponse({"result":True, "data":json_content})
                except Exception as ex:
                    return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

        else:
            try:
                data['tittle'] = u"Group"
                data['page_subtitle'] = u"Group Management"
                data['title_table'] = u"Group List"
                resultado = []
                groups = Group.objects.all()
                for group in groups:
                    access_groups = []
                    agms = AccessGroup.objects.filter(status=True,group=group)
                    for agm in agms:
                        access_groups.append({
                            "group_id": agm.id,
                            "description": agm.description
                        })
                    resultado.append({
                        "group": group,
                        "groups": access_groups
                    })

                data['list'] = resultado
                return render(request, "system/group_view.html", data)
            except Exception as ex:
                return JsonResponse({"result": False, "mesagge": f"Error {ex}"})
