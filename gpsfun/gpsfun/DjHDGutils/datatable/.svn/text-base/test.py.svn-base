from DjHDGutils.datatable.controller import Controller
from DjHDGutils.datatable.column import TextColumn
from djw.core.ProductCatalog.models import Category


class Data1(Controller):
    id = TextColumn("ID",align='center',is_sortable=True,width=50)
    name = TextColumn("Name",is_sortable=True,width='40%')
    value = TextColumn("Value")
    url = TextColumn("url",field="get_absolute_url")

    class Meta:
#        list_per_page = 2
        ordering = ('id','name')
        quicksearch_fields = ('name',)
        

    class Source:
        query = Category.objects.all()
#        sql_from = ("table a left outer join table b on (a.id = b.id)",)
#        sql_where = ("a.id = b.table_id",)
       

    


def test1():
    
    cnt = Data1()
#    for row in cnt.iter_rows():
#        print row
#    print cnt._meta
#    print cnt._meta.data_source
#    print id(cnt._meta.data_source.query)
#    t = cnt._meta.data_source.query._clone()
#    print id(t)
    
#    print dir(cnt)
    print cnt.as_html()
    

sin = """
1=i,2=n,3=v,4=e
1,2,4,-3
1,2,3,6
4=vic@stream.net.ua
"""

s2 = """
1=i,2=n,3=v,4=e
1,2,4,-3
1,2,3,6
"""

s3="r13rd53r2-123456"

def test2(str):
    print "------"
    from zlib import compress

    print len(str)
    print "".join(str.encode('base64_codec').splitlines())
    sout = compress(str,9)
    key=""
    for i in sout:
        key+="%02X"%(ord(i))
    print len(str.encode('base64_codec'))
    print len(sout.encode('base64_codec'))
    

if __name__ == "__main__":
    test2(sin)
    test2(s2)
#    test1()



