"""
form utils
"""


def get_records(request):
    """ get records """
    sequence = [n.split('=')[0].replace('%3A', ':')
                for n in request.raw_post_data.split('&')
                if n.find('%3Arecord') != -1]
    indexes = {}
    field_data = {}
    records = []
    prev_recname = None
    for var in sequence:
        recname = var.split('.')[0]
        fieldname = var.split('.')[1].split(':')[0]
        if recname in indexes:
            index = indexes[recname]
        else:
            index = 0
            indexes[recname] = 0
        if (prev_recname != recname) or (fieldname in field_data):
            if prev_recname:
                field_data['name'] = prev_recname
                records.append(field_data)
                indexes[prev_recname] += 1
            index = indexes[recname]
            field_data = {}
        field_data[fieldname] = request.POST.getlist(var)[index]
        prev_recname = recname

        field_data['name'] = recname
        records.append(field_data)
    return records


def update_from_request(object, data, mapping=None):
    """ update from request """
    for key in data:
        getkey = mapping.get(key, key) if mapping else key
        if hasattr(object, getkey):
            setattr(object, getkey, data[key])


def object_values(object, values_list):
    """ object values """
    dict = {}
    for v in values_list:
        dict[v] = object[v]
