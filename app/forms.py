# coding: utf-8
from django.forms import ModelForm, Form, CharField, PasswordInput, ValidationError, TextInput
from app.models import Task
from django.contrib.auth.models import Group
from robokassa.forms import RobokassaForm

class FluidRobokassaForm(RobokassaForm):

    def __init__(self, *args, **kwargs):
        super(FluidRobokassaForm, self).__init__(*args, **kwargs)
        self.fields['OutSum'].widget = TextInput()

class TaskForm(ModelForm):
    class Meta(object):
        model = Task
        exclude = ('author','comments', 'worker', 'status', 'price', 'moderator')

class ModeratorTaskForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(ModeratorTaskForm, self).__init__(*args, **kwargs)
        self.fields['worker'].queryset = Group.objects.get(name='developers').user_set.distinct()

    class Meta(object):
        model = Task
        exclude = ('author','comments', 'status', 'text', 'title', 'moderator')

class PasswordReset(Form):
    oldpassword = CharField(widget=PasswordInput(), label=u'Старый пароль')
    password1 = CharField(widget=PasswordInput(), label=u'Новый пароль')
    password2 = CharField(widget=PasswordInput(), label=u'Повтор нового пароля')

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PasswordReset, self).__init__(*args, **kwargs)

    def clean_oldpassword(self):
        print self.cleaned_data.get('oldpassword')
        if self.cleaned_data.get('oldpassword') and not self.user.check_password(self.cleaned_data['oldpassword']):
            raise ValidationError(u'Введен неправильный пароль')
        return self.cleaned_data['oldpassword']

    def clean_password2(self):
        if self.cleaned_data.get('password1') and self.cleaned_data.get('password2') and self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise ValidationError(u'Пароли не совпадают')
        return self.cleaned_data['password2']