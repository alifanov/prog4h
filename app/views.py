# coding: utf-8
from django.http import Http404
from django.views.generic import TemplateView, ListView, CreateView, FormView, DetailView
from app.models import Task, Comment, Bid, Balance
from app.forms import TaskForm, PasswordReset, FluidRobokassaForm, ModeratorTaskForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from robokassa.signals import result_received
from registration.signals import user_activated
from django.contrib.auth.models import Group
from django.db.models import Count

def add2group(sender, user, request, **kwargs):
    if not Balance.objects.filter(user=user).exists():
        Balance.objects.create(
            user=user,
            summ = 0.0
        )
    group = Group.objects.get(name='clients')
    group.user_set.add(user)

def payment(sender, **kwargs):
    if kwargs.get('InvId'):
        bid = Bid.objects.get(pk=kwargs.get('InvId'))
        balance = bid.user.balance
        balance.summ += bid.summ
        bid.status = True
        bid.save()
        balance.save()

result_received.connect(payment)
user_activated.connect(add2group)

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
        if self.request.user.groups.filter(name='clients').exists():
            return Task.objects.filter(author=self.request.user).order_by('-created')
        return Task.objects.order_by('-created')

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
    success_url = '/tasks/new/'

    def form_valid(self, form):
        args = form.cleaned_data
        args['author'] = self.request.user
        moderators_group = Group.objects.get(name='moderators')
        args['moderator'] = moderators_group.user_set.annotate(num_tasks=Count('moderated_tasks')).order_by('num_tasks')[0]
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
        return Bid.objects.filter(user=self.request.user, status=True).order_by('-created')

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
    need_more_money = False

    def is_client(self):
        return self.request.user.groups.filter(name='clients').exists()

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
        if request.POST and request.POST.get('price') and not self.is_client():
            task = self.get_object()
            form = ModeratorTaskForm(request.POST, instance=task)
            if form.is_valid():
                form.save()
        if request.POST and request.POST.get('start_work') and self.is_client():
            task = self.get_object()
            if request.user.balance.summ >= task.price:
                request.user.balance.summ -= task.price
                request.user.balance.save()
                task.status = 'I'
                task.save()
            else:
                self.need_more_money = True
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(TaskView, self).get_context_data(**kwargs)
        ctx['comments'] = self.get_object().get_comments(self.request.user)
        ctx['need_more_money'] = self.need_more_money
        if not self.is_client():
            ctx['task_form'] = ModeratorTaskForm(instance=self.get_object())
        return ctx

    def get_object(self, queryset=None):
        object = super(TaskView, self).get_object()
        if not self.request.user.is_authenticated():
            raise Http404
        return object