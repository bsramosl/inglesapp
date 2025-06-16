from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt


from app.forms import ModuleCategoryForm
from app.models import  ModuleCategory
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
                form = ModuleCategoryForm(request.POST)
                if form.is_valid():
                    ModuleCategory.objects.create(**form.cleaned_data)
                    return JsonResponse({"result": True, "message": "Category created successfully."})
                else:
                    return JsonResponse({"result": False, "message": "Invalid data.", "errors": form.errors})
            except Exception as ex:
                return JsonResponse({"result": False, "message": f"Error: {ex}"})

        if action == 'del':
            try:
                id = request.POST.get('id', None)
                module = ModuleCategory.objects.get(pk=id)
                module.status = False
                module.save()
                return JsonResponse({"result": True, "message": "Category delete successfully."})
            except Exception as ex:
                return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

        if action == 'edit':
            try:
                id = request.POST.get('id', None)
                module = ModuleCategory.objects.get(pk=id)
                form = ModuleCategoryForm(request.POST)
                if form.is_valid():
                    for field, value in form.cleaned_data.items():
                        setattr(module, field, value)
                    module.save()
                    return JsonResponse({"result": True, "message": "Category updated successfully."})
                else:
                    return JsonResponse({"result": False, "message": "Invalid form data.", "errors": form.errors})
            except Exception as ex:
                return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

        return JsonResponse({"result": False, 'mesagge':'Error'})
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'edit':
                try:
                    data['title'] = u'Edit Category'
                    data['id'] = id = request.GET.get('id',None)
                    data['action'] = 'edit'
                    module = ModuleCategory.objects.get(pk=id)
                    data['form'] =  ModuleCategoryForm(initial=model_to_dict(module))
                    template = get_template("layout/form.html")
                    json_content = template.render(data)
                    return JsonResponse({"result": True, 'data': json_content})
                except Exception as ex:
                    return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

            if action == 'create':
                data['title'] = u'Create Category'
                data['form'] = ModuleCategoryForm()
                data['action'] = 'create'
                template = get_template("layout/form.html")
                json_content = template.render(data)
                return JsonResponse({"result":True, "data":json_content})
        else:
            data['tittle'] = u"Categories"
            data['page_subtitle'] = u"Category Management"
            data['title_table'] = u"Category List"
            data['modules'] = ModuleCategory.objects.filter(status=True).order_by('order')
            return render(request, "system/category_view.html", data)