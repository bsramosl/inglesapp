from celery.worker.state import requests
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from app.forms import ExerciseForm, QuestionForm, ChoiceFormSet
from app.models import Exercise, Question
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
                form = ExerciseForm(request.POST)
                if form.is_valid():
                    Exercise.objects.create(**form.cleaned_data)
                    return JsonResponse({"result": True, "message": "Created successfully."})
                else:
                    return JsonResponse({"result": False, "message": "Invalid data.", "errors": form.errors})
            except Exception as ex:
                return JsonResponse({"result": False, "message": f"Error: {ex}"})

        if action == 'del':
            try:
                id = request.POST.get('id', None)
                module = Exercise.objects.get(pk=id)
                module.status = False
                module.save()
                return JsonResponse({"result": True, "message": "Delete successfully."})
            except Exception as ex:
                return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

        if action == 'edit':
            try:
                id = request.POST.get('id', None)
                module = Exercise.objects.get(pk=id)
                form = ExerciseForm(request.POST)
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
                    data['title'] = u'Exercise Module'
                    data['id'] = id = request.GET.get('id',None)
                    data['action'] = 'edit'
                    module = Exercise.objects.get(pk=id)
                    data['form'] =  ExerciseForm(initial=model_to_dict(module))
                    template = get_template("layout/form.html")
                    json_content = template.render(data)
                    return JsonResponse({"result": True, 'data': json_content})
                except Exception as ex:
                    return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

            if action == 'create':
                try:
                    data['title'] = u'Exercise Module'
                    data['form'] = ExerciseForm()
                    data['action'] = 'create'
                    template = get_template("layout/form.html")
                    json_content = template.render(data)
                    return JsonResponse({"result":True, "data":json_content})
                except Exception as ex:
                    return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

            if action == 'question':
                try:
                    data['id'] = id = request.GET.get('id', None)
                    data['tittle'] = u"Exercise Module"
                    data['page_subtitle'] = u"Question Management"
                    data['title_table'] = u"Question List"
                    data['modules'] = Question.objects.filter(status=True,exercise__id=id)
                    return render(request, "language/question_view.html", data)
                except Exception as ex:
                    return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

            if action == 'create_question':
                try:
                    id = request.GET.get('id', None)
                    data['title'] = u'Question'
                    data['form'] = QuestionForm(initial={'exercise': id})
                    data['formset'] = ChoiceFormSet()
                    data['action'] = 'create_question'
                    template = get_template("language/question_form.html")
                    json_content = template.render(data)
                    return JsonResponse({"result":True, "data":json_content})
                except Exception as ex:
                    return JsonResponse({"result": False, "mesagge": f"Error {ex}"})

        else:
            try:
                data['tittle'] = u"Exercise Module"
                data['page_subtitle'] = u"Exercise Module Management"
                data['title_table'] = u"Exercise Module List"
                data['modules'] = Exercise.objects.filter(status=True).order_by('order')
                return render(request, "language/exercises_view.html", data)
            except Exception as ex:
                return JsonResponse({"result": False, "mesagge": f"Error {ex}"})