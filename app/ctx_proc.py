def permission_processor(request):
    ctx = {}
    is_client = False
    if request.user.groups.filter(name='clients').count() > 0:
        is_client = True
        ctx['balance'] = request.user.balance
    ctx['is_client'] = is_client
    return ctx