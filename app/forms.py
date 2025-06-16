from cProfile import label

from django import forms
from django.contrib.auth.models import Group
from django.forms import ClearableFileInput

from app.models import ModuleCategory, Module, AccessGroup, Language


class GroupForm(forms.Form):
    name = forms.CharField(label='Name',max_length=100,widget=forms.TextInput(attrs={'class': 'form-control', "col": "6"}),required=True,error_messages={'required': 'Please enter the group name.','max_length': 'Maximum of 100 characters allowed.'})

class AccessGroupForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.all(),label="Group",required=True,widget=forms.Select(attrs={'class': 'form-select', "col": "6"}))
    description = forms.CharField(label='Description',max_length=100,required=True,widget=forms.TextInput(attrs={'class': 'form-control', "col": "6"}),error_messages={'max_length': 'Maximum of 100 characters allowed.'})


class ModuleCategoryForm(forms.Form):
    name = forms.CharField(label='Name',max_length=100,widget=forms.TextInput(attrs={'class': 'form-control', "col": "6"}),required=True,error_messages={'required': 'Please enter the category name.','max_length': 'Maximum of 100 characters allowed.'})
    icon = forms.CharField(label='Icon', max_length=100,required=False,widget=forms.TextInput(attrs={'class': 'form-control', "col": "6"}),error_messages={'max_length': 'Maximum of 100 characters allowed.'})
    order = forms.IntegerField(label='Order',initial=0,required=True,widget=forms.TextInput(attrs={'class': 'form-control', "col": "4"}))
    is_active = forms.BooleanField(label='Is Active?', required=False,widget=forms.CheckboxInput(attrs={'form_checkbox': True, 'class': 'form-check-input', "col": "4"}))


class ModuleForm(forms.Form):
    category = forms.ModelChoiceField(queryset=ModuleCategory.objects.filter(status=True, is_active=True),label="Category",required=False,widget=forms.Select(attrs={'class': 'form-select', "col": "4"}))
    name = forms.CharField(label='Name',max_length=100,widget=forms.TextInput(attrs={'class': 'form-control', "col": "6"}),required=True,error_messages={'required': 'Please enter the name.','max_length': 'Maximum of 100 characters allowed.'})
    description = forms.CharField(label='Description',max_length=100,required=False,widget=forms.TextInput(attrs={'class': 'form-control', "col": "12"}),error_messages={'max_length': 'Maximum of 100 characters allowed.'})
    url = forms.CharField(label='URL',widget=forms.TextInput(attrs={'class': 'form-control', "col": "4"}),required=False)
    icon = forms.CharField(label='Icon', max_length=100,required=False,widget=forms.TextInput(attrs={'class': 'form-control', "col": "6"}),error_messages={'max_length': 'Maximum of 100 characters allowed.'})
    order = forms.IntegerField(label='Order',initial=0,required=True,widget=forms.TextInput(attrs={'class': 'form-control', "col": "4"}))
    is_active = forms.BooleanField(label='Is Active?', required=False,widget=forms.CheckboxInput(attrs={'form_checkbox': True, 'class': 'form-check-input', "col": "4"}))
    needs_permission = forms.BooleanField(label='Needs Permission?',required=False,widget=forms.CheckboxInput(attrs={'form_checkbox': True, 'class': 'form-check-input', "col": "4"}))


class SystemRolForm(forms.Form):
    name = forms.CharField(label='Name',max_length=100,widget=forms.TextInput(attrs={'class': 'form-control', "col": "6"}),required=True,error_messages={'required': 'Please enter the name.','max_length': 'Maximum of 100 characters allowed.'})
    name_key = forms.CharField(label='Name',max_length=100,widget=forms.TextInput(attrs={'class': 'form-control', "col": "6"}),required=True,error_messages={'required': 'Please enter the name.','max_length': 'Maximum of 100 characters allowed.'})
    description = forms.CharField(label='Description',max_length=100,required=False,widget=forms.TextInput(attrs={'class': 'form-control', "col": "12"}),error_messages={'max_length': 'Maximum of 100 characters allowed.'})
    is_active = forms.BooleanField(label='Is Active?', required=False,widget=forms.CheckboxInput(attrs={'form_checkbox': True, 'class': 'form-check-input', "col": "4"}))

class LanguageForm(forms.Form):
    code = forms.CharField(label='Language',max_length=20,widget=forms.TextInput(attrs={'class': 'form-control', "col": "6"}),required=True,error_messages={'required': 'Please enter the code.','max_length': 'Maximum of 20 characters allowed.'})
    name = forms.CharField(label='Name',max_length=100,widget=forms.TextInput(attrs={'class': 'form-control', "col": "6"}),required=True,error_messages={'required': 'Please enter the name.','max_length': 'Maximum of 100 characters allowed.'})
    icon = forms.CharField(label='Icon', max_length=100, required=False,widget=forms.TextInput(attrs={'class': 'form-control', "col": "6"}),error_messages={'max_length': 'Maximum of 100 characters allowed.'})
    order = forms.IntegerField(label='Order', initial=0, required=True,widget=forms.TextInput(attrs={'class': 'form-control', "col": "4"}))
    is_active = forms.BooleanField(label='Is Active?', required=False, widget=forms.CheckboxInput(attrs={'form_checkbox': True, 'class': 'form-check-input', "col": "4"}))

class LanguageLevelForm(forms.Form):
    language = forms.ModelChoiceField(queryset=Language.objects.filter(status=True),label="Language",required=True,widget=forms.Select(attrs={'class': 'form-select', "col": "6"}))
    name = forms.CharField(label='Name',max_length=100,widget=forms.TextInput(attrs={'class': 'form-control', "col": "6"}),required=True,error_messages={'required': 'Please enter the name.','max_length': 'Maximum of 100 characters allowed.'})
    thumbnail = forms.ImageField(label='Thumbnail',required=False,widget=ClearableFileInput(attrs={'class': 'form-control','accept': 'image/*','col': '6'}),error_messages={'invalid_image': 'El archivo subido no es una imagen válida.',})
    order = forms.IntegerField(label='Order', initial=0, required=True,widget=forms.TextInput(attrs={'class': 'form-control', "col": "4"}))
    is_active = forms.BooleanField(label='Is Active?', required=False, widget=forms.CheckboxInput(attrs={'form_checkbox': True, 'class': 'form-check-input', "col": "4"}))
    description = forms.CharField(label='Description',max_length=100,required=False,widget=forms.TextInput(attrs={'class': 'form-control', "col": "12"}),error_messages={'max_length': 'Maximum of 100 characters allowed.'})
    short_name = forms.CharField(label='Short Name',max_length=100,required=False,widget=forms.TextInput(attrs={'class': 'form-control', "col": "12"}),error_messages={'max_length': 'Maximum of 100 characters allowed.'})
