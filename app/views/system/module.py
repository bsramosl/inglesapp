from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from docutils.nodes import status

from app.forms import ModuleForm
from app.models import Module
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

        if action == 'create_module':
            try:
                form = ModuleForm(request.POST)
                if form.is_valid():
                    Module.objects.create(**form.cleaned_data)
                    return JsonResponse({"result": True, "message": "Module created successfully."})
                else:
                    return JsonResponse({"result": False, "message": "Invalid data.", "errors": form.errors})
            except Exception as ex:
                return JsonResponse({"result": False, "message": f"Error: {ex}"})

        if action == 'del_module':
            try:
                id = request.POST.get('id', None)
                module = Module.objects.get(pk=id)
                module.status = False
                module.save()
                return JsonResponse({"result": True, "message": "Module delete successfully."})
            except Exception as ex:
                return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

        if action == 'edit_module':
            try:
                id = request.POST.get('id', None)
                module = Module.objects.get(pk=id)
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
                    data['title'] = u'Edit Modules'
                    data['id'] = id = request.GET.get('id',None)
                    data['action'] = 'edit_module'
                    module = Module.objects.get(pk=id)
                    data['form'] =  ModuleForm(initial=model_to_dict(module))
                    template = get_template("layout/form.html")
                    json_content = template.render(data)
                    return JsonResponse({"result": True, 'data': json_content})
                except Exception as ex:
                    return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

            if action == 'create_module':
                data['title'] = u'Create Module'
                data['form'] = ModuleForm()
                data['action'] = 'create_module'
                template = get_template("layout/form.html")
                json_content = template.render(data)
                return JsonResponse({"result":True, "data":json_content})
        else:
            data['tittle'] = u"Modules"
            data['page_subtitle'] = u"Module Management"
            data['title_table'] = u"Modules List"
            data['modules'] = Module.objects.select_related('category').filter(status=True).all().order_by('category__order', 'order')
            return render(request, "system/module_view.html", data)