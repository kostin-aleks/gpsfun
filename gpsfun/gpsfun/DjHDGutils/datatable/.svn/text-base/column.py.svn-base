


class Column(object):
    creation_counter = 0

    def __init__(self,title,field=None,is_sortable=False,align='left',filter=None,width=None,is_href=False):
        self.name = None
        self.title = title
        self.field = field 
        self.is_sortable = is_sortable
        self.filter = filter
        self.align = align
        self.width = width
        self.is_href = is_href

        # flags for template to thisplay order mode for column
        self.ordered_asc = False
        self.ordered_desc = False

        # Increase the creation counter, and save our local copy.
        self.creation_counter = Column.creation_counter
        Column.creation_counter += 1

    def is_ordered_asc(self):
        return self.ordered_asc

    def is_ordered_desc(self):
        return self.ordered_desc

    def print_head(self):
        return self.title

    def print_column(self,data,controller):
        return data

class TextColumn(Column):
    pass
