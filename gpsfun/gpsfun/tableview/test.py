"""
test
"""

from gpsfun.tableview import table, widgets
from gpsfun.tableview.datasource import QSDataSource
from core.Dealer.models import Dealer


class Table1(table.TableView):
    id = widgets.LabelWidget('ID', refname='id', title_attr={'class': 'class1'})
    name = widgets.LabelWidget('Name', refname='name', cell_attr={'style': 'style1'})
    k2 = widgets.LabelWidget('Name2', refname='1')
    k3 = widgets.LabelWidget('Name_test', refname='0')

    class Meta:
        permanent = ('id', 'name')
        sortable = ('id', 'name', 'k2')

    def get_source(self):
        return QSDataSource(Dealer.objects.all())

    def custom_filter(qs):
        return qs


def test1():
    t1 = Table1()
    t1.show_column('k2')
    t1.set_sort('name', False)
    print(t1.as_html())


if __name__ == '__main__':
    test1()
