"""
template tags mishelpers
"""

from django import template


def arrange_to_rows(array, cols):
    """
    very often we need to display data from a few records
    in same line. for example display 5 products per line, and
    on next line display images from same 5 products
    """
    cols = int(cols)
    row = []
    index = 0
    while True:
        row = list(array[index:index + cols])
        if len(row) != cols:
            row += [None] * (cols - len(row))
            break
        yield row
        index += cols
    yield row


register = template.Library()
register.filter('arrange_to_rows', arrange_to_rows)
