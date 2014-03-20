# coding: utf-8
import json
from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
# Create your models here.

STATUS_CHOICE = (
    ('D', u'Закрыта'),
    ('N', u'Новая'),
    ('I', u'В работе'),
    ('C', u'Выполнена')
)

class Balance(models.Model):
    user = models.OneToOneField(User, verbose_name=u'Пользователь', related_name='balance')
    summ = models.DecimalField(decimal_places=2, max_digits=8, verbose_name=u'Сумма')

    def __unicode__(self):
        return u'[{}]: {}'.format(self.summ, self.user.username)

    class Meta:
        verbose_name = u'Баланс пользователя'
        verbose_name_plural = u'Балансы пользователей'

class Bid(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'Дата создания')
    summ = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=u'Сумма', default=100.0)
    user = models.ForeignKey(User, verbose_name=u'Пользователь')
    status = models.BooleanField(verbose_name=u'Выполнена', default=False)

    def __unicode__(self):
        return u'[{}]: {}'.format(self.created, self.user.username)

    class Meta:
        verbose_name = u'Транзакция'
        verbose_name_plural = u'Транзакции'

class Task(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'Дата создания')
    title = models.CharField(max_length=512, verbose_name=u'Описание задачи')
    text = models.TextField(verbose_name=u'Текст задачи')
    author = models.ForeignKey(User, verbose_name=u'Автор задачи', related_name='created_tasks')
    moderator = models.ForeignKey(User, verbose_name=u'Менеджер задачи', related_name='moderated_tasks', null=True)
    worker = models.ForeignKey(User, verbose_name=u'Исполнитель задачи', related_name='work_tasks', null=True)
    status = models.CharField(choices=STATUS_CHOICE, verbose_name=u'Статус задачи', max_length=1, default='N')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=u'Цена задачи', default=0.0)

    def save(self, *args, **kwargs):
        msg = u'Создана новая задача:\n{}'.format(self.text)
        send_mail(u'Новая задача', msg, 'info@progernachas.ru', ['lifanov.a.v@gmail.com','philipp.spock@gmail.com'])
        super(Task, self).save(*args, **kwargs)

    def get_html_status(self):
        html = u'<span class="label label-{}">{}</span>'
        if self.status == 'N':
            return html.format(u'success', u'Новая')
        if self.status == 'D':
            return html.format(u'default', u'Закрыта')
        if self.status == 'I':
            return html.format(u'warning', u'В работе')
        if self.status == 'C':
            return html.format(u'primary', u'Выполнена')

    def in_work(self):
        if self.status != 'N': return True
        return False

    def get_comments(self, user):
        if user.groups.filter(name='clients').exists():
            return self.comments.filter(hidden=False).order_by('timestamp')
        if user.groups.filter(name='developers').exists():
            return self.comments.filter(hidden=True).order_by('timestamp')
        return self.comments.order_by('timestamp')

    def __unicode__(self):
        return u'[{}]:{}'.format(self.author.username, self.title)

    class Meta:
        verbose_name = u'Задача'
        verbose_name_plural = u'Задачи'

class Comment(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=u'Дата создания')
    user = models.ForeignKey(User, verbose_name=u'Автор')
    text = models.TextField(verbose_name=u'Текст комментария')
    hidden = models.BooleanField(default=False)
    task = models.ForeignKey(Task, related_name='comments', verbose_name=u'Задача')

    def save(self, *args, **kwargs):
        msg = u'Создан новый комментарий:\n{}'.format(self.text)
        send_mail(u'Новый комментарий', msg, 'info@progernachas.ru', ['lifanov.a.v@gmail.com','philipp.spock@gmail.com'])
        if not self.hidden:
            send_mail(u'Новый комментарий', msg, 'info@progernachas.ru', ['lifanov.a.v@gmail.com', self.task.author.email])
        super(Comment, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'[{}]: {}'.format(self.timestamp, self.user.username)

    class Meta:
        verbose_name = u'Комментарий'
        verbose_name_plural = u'Комментарии'

