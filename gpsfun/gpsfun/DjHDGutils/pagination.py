"""
pagination
"""
from django.core.paginator import Paginator, InvalidPage, EmptyPage


def paginate_page(request, objects_list, per_page):
    """ taking out similar code pieces to function to paginate objects """
    paginator = Paginator(objects_list, per_page) # Show 5 projects per page

    # Make sure page request is an int. If not, deliver first page.
    try:
        page_no = int(request.GET.get('page', '1'))
    except ValueError:
        page_no = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        page = paginator.page(page_no)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)

    return page
