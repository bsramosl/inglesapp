from django import forms
from app.models import ModuleCategory

class ModuleForm(forms.Form):
    category = forms.ModelChoiceField(queryset=ModuleCategory.objects.filter(status=True, is_active=True),label="Category",required=False,widget=forms.Select(attrs={'class': 'form-select', "col": "4"}))
    name = forms.CharField(label='Name',max_length=100,widget=forms.TextInput(attrs={'class': 'form-control', "col": "6"}),required=True,error_messages={'required': 'Please enter the module name.','max_length': 'Maximum of 100 characters allowed.'})
    description = forms.CharField(label='Description',max_length=100,required=False,widget=forms.TextInput(attrs={'class': 'form-control', "col": "12"}),error_messages={'max_length': 'Maximum of 100 characters allowed.'})
    url = forms.CharField(label='URL',widget=forms.TextInput(attrs={'class': 'form-control', "col": "4"}),required=False)
    icon = forms.CharField(label='Icon', max_length=100,required=False,widget=forms.TextInput(attrs={'class': 'form-control', "col": "6"}),error_messages={'max_length': 'Maximum of 100 characters allowed.'})
    order = forms.IntegerField(label='Order',initial=0,required=True,widget=forms.TextInput(attrs={'class': 'form-control', "col": "4"}))
    is_active = forms.BooleanField(label='Is Active?', required=False,widget=forms.CheckboxInput(attrs={'form_checkbox': True, 'class': 'form-check-input', "col": "4"}))
    needs_permission = forms.BooleanField(label='Needs Permission?',required=False,widget=forms.CheckboxInput(attrs={'form_checkbox': True, 'class': 'form-check-input', "col": "4"}))



class SystemRolForm(forms.Form):
    name = forms.CharField(label='Name',max_length=100,widget=forms.TextInput(attrs={'class': 'form-control', "col": "6"}),required=True,error_messages={'required': 'Please enter the module name.','max_length': 'Maximum of 100 characters allowed.'})
    name_key = forms.CharField(label='Name',max_length=100,widget=forms.TextInput(attrs={'class': 'form-control', "col": "6"}),required=True,error_messages={'required': 'Please enter the module name.','max_length': 'Maximum of 100 characters allowed.'})
    description = forms.CharField(label='Description',max_length=100,required=False,widget=forms.TextInput(attrs={'class': 'form-control', "col": "12"}),error_messages={'max_length': 'Maximum of 100 characters allowed.'})
    is_active = forms.BooleanField(label='Is Active?', required=False,widget=forms.CheckboxInput(attrs={'form_checkbox': True, 'class': 'form-check-input', "col": "4"}))
