from cProfile import label

from django import forms
from django.contrib.auth.models import Group
from django.forms import ClearableFileInput, inlineformset_factory
from ckeditor.widgets import CKEditorWidget
from app.models import ModuleCategory, Module, AccessGroup, Language, Level, TopicCategory, LearningModule, \
    LearningContent, Exercise, Question, Choice


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
    api = forms.BooleanField(label='Api?',required=False,widget=forms.CheckboxInput(attrs={'form_checkbox': True, 'class': 'form-check-input', "col": "4"}))
    authenticated = forms.BooleanField(label='Needs Authenticated?',required=False,widget=forms.CheckboxInput(attrs={'form_checkbox': True, 'class': 'form-check-input', "col": "4"}))


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

class  TopicCategoryForm(forms.Form):
    language = forms.ModelChoiceField(queryset=Language.objects.filter(status=True),label="Language",required=True,widget=forms.Select(attrs={'class': 'form-select', "col": "6"}))
    name = forms.CharField(label='Name',max_length=100,widget=forms.TextInput(attrs={'class': 'form-control', "col": "6"}),required=True,error_messages={'required': 'Please enter the name.','max_length': 'Maximum of 100 characters allowed.'})
    description = forms.CharField(label='Description',max_length=100,required=False,widget=forms.TextInput(attrs={'class': 'form-control', "col": "12"}),error_messages={'max_length': 'Maximum of 100 characters allowed.'})
    icon = forms.CharField(label='Icon', max_length=100, required=False,widget=forms.TextInput(attrs={'class': 'form-control', "col": "6"}),error_messages={'max_length': 'Maximum of 100 characters allowed.'})
    order = forms.IntegerField(label='Order', initial=0, required=True,widget=forms.TextInput(attrs={'class': 'form-control', "col": "4"}))
    is_active = forms.BooleanField(label='Is Active?', required=False, widget=forms.CheckboxInput(attrs={'form_checkbox': True, 'class': 'form-check-input', "col": "4"}))

class  LearningModuleForm(forms.Form):
    level = forms.ModelChoiceField(queryset=Level.objects.filter(status=True),label="Language",required=True,widget=forms.Select(attrs={'class': 'form-select', "col": "6"}))
    topic_category = forms.ModelChoiceField(queryset=TopicCategory.objects.filter(status=True),label="Topic Category",required=True,widget=forms.Select(attrs={'class': 'form-select', "col": "6"}))
    title = forms.CharField(label='Tittle',max_length=100,widget=forms.TextInput(attrs={'class': 'form-control', "col": "6"}),required=True,error_messages={'required': 'Please enter the name.','max_length': 'Maximum of 100 characters allowed.'})
    description = forms.CharField(label='Description',max_length=100,required=False,widget=forms.TextInput(attrs={'class': 'form-control', "col": "12"}),error_messages={'max_length': 'Maximum of 100 characters allowed.'})
    thumbnail = forms.ImageField(label='Thumbnail',required=False,widget=ClearableFileInput(attrs={'class': 'form-control','accept': 'image/*','col': '6'}),error_messages={'invalid_image': 'El archivo subido no es una imagen válida.',})
    order = forms.IntegerField(label='Order', initial=0, required=True,widget=forms.TextInput(attrs={'class': 'form-control', "col": "4"}))
    is_active = forms.BooleanField(label='Is Active?', required=False, widget=forms.CheckboxInput(attrs={'form_checkbox': True, 'class': 'form-check-input', "col": "4"}))
    estimated_duration = forms.IntegerField(label="Estimated Duration (minutes)", min_value=1, required=True,initial=30,widget=forms.NumberInput(attrs={'class': 'form-control','placeholder': 'Estimated duration in minutes','col': '6'}),help_text='Estimated duration in minutes')
    is_premium = forms.BooleanField(label='Is Premium?', required=False, widget=forms.CheckboxInput(attrs={'form_checkbox': True, 'class': 'form-check-input', "col": "4"}))


class  ExerciseForm(forms.Form):
    module = forms.ModelChoiceField(queryset=LearningModule.objects.filter(status=True),label="Module",required=True,widget=forms.Select(attrs={'class': 'form-select', "col": "6"}))
    content = forms.ModelChoiceField(queryset=LearningContent.objects.filter(status=True),label="Content",required=True,widget=forms.Select(attrs={'class': 'form-select', "col": "6"}))
    title = forms.CharField(label='Tittle',max_length=100,widget=forms.TextInput(attrs={'class': 'form-control', "col": "6"}),required=True,error_messages={'required': 'Please enter the name.','max_length': 'Maximum of 100 characters allowed.'})
    description = forms.CharField(label='Description',max_length=100,required=False,widget=forms.TextInput(attrs={'class': 'form-control', "col": "12"}),error_messages={'max_length': 'Maximum of 100 characters allowed.'})
    max_score = forms.IntegerField(label='Score', initial=0, required=True,widget=forms.TextInput(attrs={'class': 'form-control', "col": "4"}))
    order = forms.IntegerField(label='Order', initial=0, required=True,widget=forms.TextInput(attrs={'class': 'form-control', "col": "4"}))
    exercise_type = forms.ChoiceField(label='Exercise Type',choices=Exercise.TYPE_CHOICES,initial='mcq',required=True,widget=forms.Select(attrs={'class': 'form-select', "col": "6"}))
    difficulty = forms.ChoiceField(label='Difficulty',choices=Exercise.DIFFICULTY_CHOICES,initial='medium',required=True,widget=forms.Select(attrs={'class': 'form-select', "col": "6"}))
    is_active = forms.BooleanField(label='Is Active?', required=False, widget=forms.CheckboxInput(attrs={'form_checkbox': True, 'class': 'form-check-input', "col": "4"}))
    is_premium = forms.BooleanField(label='Is Premium?', required=False, widget=forms.CheckboxInput(attrs={'form_checkbox': True, 'class': 'form-check-input', "col": "4"}))


class  QuestionForm(forms.Form):
    exercise = forms.ModelChoiceField(queryset=Exercise.objects.filter(status=True),label="Exercise",required=True,widget=forms.Select(attrs={'class': 'form-select', "col": "6"}))
    question_type = forms.ChoiceField(label='Question Type',choices=Question.QUESTION_TYPE_CHOICES,initial='mcq',required=True,widget=forms.Select(attrs={'class': 'form-select', "col": "6"}))
    text = forms.CharField(label='Text',max_length=1000,widget=forms.Textarea(attrs={'class': 'form-control', "col": "12"}),required=True)
    audio = forms.FileField(label='Audio', initial=0, required=False,widget=forms.ClearableFileInput(attrs={'class': 'form-control', "col": "6"}))
    image = forms.ImageField(label='Image', initial=0, required=False,widget=forms.ClearableFileInput(attrs={'class': 'form-control', "col": "6"}))
    explanation = forms.CharField(label='Explanation',max_length=1000,widget=forms.Textarea(attrs={'class': 'form-control', "col": "12"}),required=True)
    order = forms.IntegerField(label='Order', initial=0, required=True,widget=forms.TextInput(attrs={'class': 'form-control', "col": "4"}))
    points = forms.IntegerField(label='Points', initial=0, required=True,widget=forms.TextInput(attrs={'class': 'form-control', "col": "4"}))



class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct', 'feedback']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter choice text', "col": "8"}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input', "col": "2"}),
            'feedback': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional feedback', "col": "12"}),
        }

ChoiceFormSet = inlineformset_factory(Question,Choice,form=ChoiceForm,extra=4,min_num=2,validate_min=True,can_delete=True,)