from app.models import Task

def permission_processor(request):
    ctx = {}
    is_client = False
    if request.user.groups.filter(name='clients').count() > 0:
        is_client = True
        ctx['balance'] = request.user.balance
        ctx['all_tasks_cnt'] = request.user.created_tasks.count()
        ctx['new_tasks_cnt'] = request.user.created_tasks.filter(status='N').count()
        ctx['inwork_tasks_cnt'] = request.user.created_tasks.filter(status='I').count()
        ctx['completed_tasks_cnt'] = request.user.created_tasks.filter(status='C').count()
        ctx['done_tasks_cnt'] = request.user.created_tasks.filter(status='D').count()
    else:
        ctx['all_tasks_cnt'] = Task.objects.count()
        ctx['new_tasks_cnt'] = Task.objects.filter(status='N').count()
        ctx['inwork_tasks_cnt'] = Task.objects.filter(status='I').count()
        ctx['completed_tasks_cnt'] = Task.objects.filter(status='C').count()
        ctx['done_tasks_cnt'] = Task.objects.filter(status='D').count()
    ctx['is_client'] = is_client
    return ctx