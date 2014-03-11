def permission_processor(request):
    is_client = False
    if request.user.groups.filter(name='clients').count() > 0: is_client = True
    return {'is_client': is_client}