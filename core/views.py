from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.apps import apps
from django.forms import modelform_factory

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Module
from django.forms import modelform_factory

from .services.user_services import actualizar_datos_sesion

data={}

def module_list_view(request):
    actualizar_datos_sesion(request)
    modules = Module.objects.select_related('category').all().order_by('category__order', 'order')
    data['modules'] = modules
    return render(request, 'modules/module_list.html', data)

def module_modal_view(request):
    action = request.GET.get('action')
    module_id = request.GET.get('id')
    ModuleForm = modelform_factory(Module, exclude=('created', 'updated'))

    if action == 'create':
        form = ModuleForm(request.POST or None)
    else:
        module = get_object_or_404(Module, pk=module_id)
        form = ModuleForm(request.POST or None, instance=module)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponse('<script>location.reload();</script>')

    template = 'modules/module_modal_form.html' if action != 'delete' else 'modules/module_modal_delete.html'
    context = {'form': form, 'action': action, 'id': module_id}

    if action == 'delete' and request.method == 'POST':
        module.delete()
        return HttpResponse('<script>location.reload();</script>')

    return render(request, template, context)