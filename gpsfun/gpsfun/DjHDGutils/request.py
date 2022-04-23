"""
request
"""


def get_records_from_request(request, recordsize):
    res = []
    for i in range(0, recordsize):
        attrs = {}
        for var in request.POST:
            if len(request.POST.getlist(var)) == recordsize:
                attrs[var] = request.POST.getlist(var)[i]
        res.append(attrs)
    return res
