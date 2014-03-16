from django.conf.urls import patterns, include, url

from app.views import DashboardView, NewTaskView, NewTasksView, InWorkTasksView, DoneTasksView, CompletedTasksView,\
TaskView, UpdatePasswordView, BalanceView
from registration.backends.default.views import RegistrationView
from registration.forms import RegistrationFormUniqueEmail

from django.views.generic import TemplateView

class RegistrationUniqEmailView(RegistrationView):
    form_class = RegistrationFormUniqueEmail

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    # url(r'^prog4h/', include('prog4h.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^dashboard/$', DashboardView.as_view(), name='dashboard'),
    url(r'^new_password/$', UpdatePasswordView.as_view(), name='new_password'),
    url(r'^balance/$', BalanceView.as_view(), name='balance'),

    url(r'^contacts/$', TemplateView.as_view(template_name='contacts.html'), name='contacts'),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'), name='about'),
    url(r'^terms/$', TemplateView.as_view(template_name='terms.html'), name='terms'),

    url(r'^task/add/$', NewTaskView.as_view(), name='add_task'),
    url(r'^task/(?P<pk>\d+)/$', TaskView.as_view(), name='task_detail'),

    url(r'^tasks/new/$', NewTasksView.as_view(), name='new_tasks'),
    url(r'^tasks/completed/$', CompletedTasksView.as_view(), name='completed_tasks'),
    url(r'^tasks/inwork/$', InWorkTasksView.as_view(), name='inwork_tasks'),
    url(r'^tasks/done/$', DoneTasksView.as_view(), name='done_tasks'),

    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',
     {'next_page': '/'}),
    url(r'^accounts/register/$', RegistrationUniqEmailView.as_view(), name='registration_register'),

    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^robokassa/', include('robokassa.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
