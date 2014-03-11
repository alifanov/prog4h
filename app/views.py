# coding: utf-8
from django.http import Http404
from django.views.generic import TemplateView, ListView, CreateView, FormView, DetailView
from app.models import Task, Comment, Bid, Balance
from app.forms import TaskForm, PasswordReset, FluidRobokassaForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from robokassa.signals import result_received

def payment(sender, **kwargs):
    if kwargs.get('InvId'):
        bid = Bid.objects.get(pk=kwargs.get('InvId'))
        balance = bid.user.balance
        balance.summ += bid.summ
        bid.status = True
        bid.save()
        balance.save()
    print kwargs

result_received.connect(payment)

class DashboardView(ListView):
    template_name = 'dashboard.html'
    context_object_name = 'tasks'
    title = u'Все задачи'
    active = 'all'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        """
        Декорируем диспетчер функцией login_required, чтобы запретить просмотр отображения неавторизованными
        пользователями
        """
        return super(DashboardView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Task.objects.filter(author=self.request.user).order_by('-created')

    def get_context_data(self, **kwargs):
        ctx = super(DashboardView, self).get_context_data(**kwargs)
        ctx['title'] = self.title
        ctx['active'] = self.active
        return ctx

class NewTasksView(DashboardView):
    title = u'Новые задачи'
    active = 'new'

    def get_queryset(self):
        qs = super(NewTasksView, self).get_queryset()
        qs = qs.filter(status='N')
        return qs

class InWorkTasksView(DashboardView):
    title = u'Задачи в работе'
    active = 'inwork'

    def get_queryset(self):
        qs = super(InWorkTasksView, self).get_queryset()
        qs = qs.filter(status='I')
        return qs

class CompletedTasksView(DashboardView):
    title = u'Выполненные'
    active = 'completed'

    def get_queryset(self):
        qs = super(CompletedTasksView, self).get_queryset()
        qs = qs.filter(status='C')
        return qs

class DoneTasksView(DashboardView):
    title = u'Закрытые задачи'
    active = 'done'

    def get_queryset(self):
        qs = super(DoneTasksView, self).get_queryset()
        qs = qs.filter(status='D')
        return qs

class NewTaskView(CreateView):
    form_class = TaskForm
    template_name = 'task_create.html'
    success_url = '/new_tasks/'

    def form_valid(self, form):
        args = form.cleaned_data
        args['author'] = self.request.user
        Task.objects.create(**args)
        return redirect(self.success_url)

class UpdatePasswordView(FormView):
    form_class = PasswordReset
    template_name = 'new_password.html'
    success_url = '/new_password/'
    success = False

    def get_context_data(self, **kwargs):
        ctx = super(UpdatePasswordView, self).get_context_data(**kwargs)
        ctx['success'] = self.success
        return ctx

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdatePasswordView, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class):
        ars = self.get_form_kwargs()
        ars.update({
            'user': self.request.user
        })
        return form_class(**ars)

    def form_valid(self, form):
        new_password = form.cleaned_data.get('password1')
        self.request.user.set_password(new_password)
        self.request.user.save()
        return self.render_to_response(self.get_context_data())

class BalanceView(ListView):
    model = Bid
    context_object_name = 'bids'
    template_name = 'balance.html'

    def get_queryset(self):
        return Bid.objects.filter(user=self.request.user).order_by('-created')

    def get_context_data(self, **kwargs):
        ctx = super(BalanceView, self).get_context_data(**kwargs)
        bid = Bid.objects.create(
            user=self.request.user
        )
        # TODO: del old bids
        ctx['form'] = FluidRobokassaForm(initial={
            'OutSum': bid.summ,
            'InvId': bid.pk,
        })
        return ctx

class TaskView(DetailView):
    template_name = 'task_detail.html'
    model = Task
    context_object_name = 'task'

    def post(self, request, *args, **kwargs):
        if request.POST and request.POST.get('comment_text'):
            a = {
                'text': request.POST.get('comment_text'),
                'user': request.user,
                'task': self.get_object()
            }
            if request.POST.get('hidden') == '1':
                a['hidden'] = True
            Comment.objects.create(**a)
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(TaskView, self).get_context_data(**kwargs)
        ctx['comments'] = self.get_object().get_comments(self.request.user)
        return ctx

    def get_object(self, queryset=None):
        object = super(TaskView, self).get_object()
        if not self.request.user.is_authenticated():
            raise Http404
        return object