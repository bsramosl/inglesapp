from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from app.forms import ModuleForm
from app.models import  ProfileSystemRol
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

        if action == 'create':
            try:
                form = ModuleForm(request.POST)
                if form.is_valid():
                    ProfileSystemRol.objects.create(**form.cleaned_data)
                    return JsonResponse({"result": True, "message": "Module created successfully."})
                else:
                    return JsonResponse({"result": False, "message": "Invalid data.", "errors": form.errors})
            except Exception as ex:
                return JsonResponse({"result": False, "message": f"Error: {ex}"})

        if action == 'del':
            try:
                id = request.POST.get('id', None)
                module = ProfileSystemRol.objects.get(pk=id)
                module.status = False
                module.save()
                return JsonResponse({"result": True, "message": "Profile delete successfully."})
            except Exception as ex:
                return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

        if action == 'edit':
            try:
                id = request.POST.get('id', None)
                module = ProfileSystemRol.objects.get(pk=id)
                form = ModuleForm(request.POST)
                if form.is_valid():
                    for field, value in form.cleaned_data.items():
                        setattr(module, field, value)
                    module.save()
                    return JsonResponse({"result": True, "message": "Module updated successfully."})
                else:
                    return JsonResponse({"result": False, "message": "Invalid form data.", "errors": form.errors})
            except Exception as ex:
                return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

        return JsonResponse({"result": False, 'mesagge':'Error'})
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'edit_module':
                try:
                    data['title'] = u'Edit Profile'
                    data['id'] = id = request.GET.get('id',None)
                    data['action'] = 'edit'
                    module = ProfileSystemRol.objects.get(pk=id)
                    data['form'] =  ModuleForm(initial=model_to_dict(module))
                    template = get_template("layout/form.html")
                    json_content = template.render(data)
                    return JsonResponse({"result": True, 'data': json_content})
                except Exception as ex:
                    return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

            if action == 'create':
                data['title'] = u'Profile management'
                data['form'] = ModuleForm()
                data['action'] = 'create'
                template = get_template("layout/form.html")
                json_content = template.render(data)
                return JsonResponse({"result":True, "data":json_content})
        else:
            data['tittle'] = u"Profiles"
            data['page_subtitle'] = u"Profile Management"
            data['title_table'] = u"Profile List"
            data['list'] = ProfileSystemRol.objects.filter(status=True).exclude(system_rol__pk=3).select_related('profile__person').order_by('profile__person').distinct('profile__person')
            return render(request, "system/users_profile.html", data)