from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from app.forms import LanguageLevelForm
from app.models import  Level
from helpers.decorators import add_data

@csrf_exempt
@login_required(redirect_field_name='ret', login_url='/login')
@transaction.atomic()
def view(request):
    data = {}
    add_data(request, data)
    data['person'] = persona = request.session['person']
    if request.method == 'POST':
        action = request.POST['action']

        if action == 'create':
            try:
                form = LanguageLevelForm(request.POST)
                if form.is_valid():
                    Level.objects.create(**form.cleaned_data)
                    return JsonResponse({"result": True, "message": "Created successfully."})
                else:
                    return JsonResponse({"result": False, "message": "Invalid data.", "errors": form.errors})
            except Exception as ex:
                return JsonResponse({"result": False, "message": f"Error: {ex}"})

        if action == 'del':
            try:
                id = request.POST.get('id', None)
                module = Level.objects.get(pk=id)
                module.status = False
                module.save()
                return JsonResponse({"result": True, "message": "Delete successfully."})
            except Exception as ex:
                return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

        if action == 'edit':
            try:
                id = request.POST.get('id', None)
                module = Level.objects.get(pk=id)
                form = LanguageLevelForm(request.POST)
                if form.is_valid():
                    for field, value in form.cleaned_data.items():
                        setattr(module, field, value)
                    module.save()
                    return JsonResponse({"result": True, "message": "Updated successfully."})
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
                    data['title'] = u'Edit Language Level'
                    data['id'] = id = request.GET.get('id',None)
                    data['action'] = 'edit'
                    module = Level.objects.get(pk=id)
                    data['form'] =  LanguageLevelForm(initial=model_to_dict(module))
                    template = get_template("layout/form.html")
                    json_content = template.render(data)
                    return JsonResponse({"result": True, 'data': json_content})
                except Exception as ex:
                    return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

            if action == 'create':
                data['title'] = u'Create Language Level'
                data['form'] = LanguageLevelForm()
                data['action'] = 'create'
                template = get_template("layout/form.html")
                json_content = template.render(data)
                return JsonResponse({"result":True, "data":json_content})
        else:
            data['tittle'] = u"Language Levels"
            data['page_subtitle'] = u"Language Level Management"
            data['title_table'] = u"Language List"
            data['modules'] = Level.objects.filter(status=True).order_by('order')
            return render(request, "language/language_level_view.html", data)