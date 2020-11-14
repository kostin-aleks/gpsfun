from django.views.generic.simple import direct_to_template

def confirm_action(func):
    def wrapper(*args,**kwargs):
        table = args[0]
        request = args[1]
        if request.REQUEST.has_key('confirmed'):
            return func(*args,**kwargs)
        records_to_delete = request.POST.getlist('record_id')
        amount = len(records_to_delete)
        if not amount:
            amount = table.count()
        return direct_to_template(request,
                                  'AdminTable/confirm_action.html',
                                  dict(table=table,
                                       request = request,
                                       action = request.POST['runaction'],
                                       records = records_to_delete,
                                       amount=amount))

    return wrapper
