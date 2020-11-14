#!/usr/bin/env python
# -*- coding: utf-8 -*-
from xml.dom.minidom import parse
from xml.dom import Node
from reportlab.lib.styles import ParagraphStyle,getSampleStyleSheet
from paragraph import Paragraph
from reportlab.pdfgen.canvas import Canvas
import re

class IPage(object):
    def __init__(self):
        self.pageWidth=595
        self.pageHeight=842
	self.columnWidth=535
	self.columnSpacing=0
        self.leftMargin=30
        self.rightMargin=30
        self.topMargin=20
        self.bottomMargin=20
        
        self.offset_y = 0

    def get_viewpoint_height(self):
        return self.pageHeight-self.topMargin-self.bottomMargin

    def translate(self,ax,ay):
        x=self.leftMargin  + ax
        y=self.pageHeight - self.topMargin - self.offset_y - ay
        return (x,y)


    def set_bottom_offset(self,bottom_height):
        self.offset_y = self.pageHeight - self.topMargin - self.bottomMargin - bottom_height

class Element(object):
    local_name = 'element'
    attr_list = {}
    
    def __init__(self,node):
        self.node = node
        self.attr_list = dict()
        
        self.extract_attributes(Element)

    def __str__(self):
        out = ""
        for k,v in self.attr_list.iteritems():
            out += "%s: %s\n"%(k,str(v))
        return out


    def __setitem__(self,key,value):
        self.attr_list[key] = value

    def __getitem__(self,key):
        return self.attr_list[key]


    def find_node(self,node,name):
        if node.localName == name:
            return node

        node_list = node.getElementsByTagName(name)
        if len(node_list) > 0:
            return node_list[0]

        return node_list

    def extract_attributes(self,object):
        node = self.find_node(self.node,object.local_name)
        if node is None:
            return
        
        for key,default_value in object.attr_list.iteritems():
            value = node.getAttribute(key)

            if value is None or value == '':
                self.attr_list[key] = default_value
                continue
                
            if value == 'true':
                value = True
            elif value == 'false':
                value = False
            else:
                try:
                    value = int(value)
                except:
                    pass

            self.attr_list[key] = value

    def extract_text(self,object):
        text_node = self.find_node(self.node,object.local_name)
        if text_node:
            self.data = self.get_node_data(text_node)
        else:
            self.data = None
        return self.data
    
    def get_node_data(self,node):
        text = u""
        for child in node.childNodes:
            text += child.data

        return text

class PrintWhenExpression(Element):
    local_name = 'printWhenExpression'
    attr_list = {}

    def __init__(self,node):
        super(PrintWhenExpression,self).__init__(node)

        self.extract_text(PrintWhenExpression)


    def evaluate(self,content):
        if self.data is None:
            return True
        return eval(self.data,None,content)

        try:
            return eval(self.data,locals=content)
        except:
            return True

class ReportElement(Element):
    local_name = 'reportElement'
    attr_list = {'x': 0,
                 'y': 0,
                 'width': 100,
                 'height': 100}
    
    def __init__(self,node):
        super(ReportElement,self).__init__(node)
        self.extract_attributes(ReportElement)

        self.printWhenExpression = PrintWhenExpression(node)

    def is_printable(self,content):
        if self.printWhenExpression:
            return self.printWhenExpression.evaluate(content)
        return True
       

class Font(Element):
    local_name = 'font'

    attr_list = {'fontName': 'Helvetica',
                 'size': 10,
                 'isBold': False,
                 'isItalic': False,
                 'isUnderline': False }

    base_font_map = {'Times New Roman': 'Times-Roman',
                     'SansSerif': 'Helvetica'}

    style_map = {'Times-Roman': ['Times-Bold','Times-Italic','Times-BoldItalic'],
                 'Helvetica':  ['Helvetica-Bold','Helvetica-Oblique','Helvetica-BoldOblique'],
                 'Courier': ['Courier-Bold','Courier-Oblique','Courier-BoldOblique'],
                 }

    def __init__(self,node):
        super(Font,self).__init__(node)
        self.extract_attributes(Font)

    def remap_name(self,name):
        if self.base_font_map.has_key(name):
            return self.base_font_map[name]

        return self.attr_list['fontName']

    def get_fontname(self):
        base_font = self.remap_name(self['fontName'])
       
        if self['isBold'] and self['isItalic']:
            return self.style_map[base_font][2]
        elif self['isBold'] and self['isItalic'] == False:
            return self.style_map[base_font][0]
        elif self['isBold'] == False and self['isItalic']:
            return self.style_map[base_font][1]

        return base_font

class TextElement(Element):
    local_name = 'textElement'

    attr_list = {'textAlignment': 'Left',
                 'verticalAlignment': 'top'}
    
    def __init__(self,node):
        super(TextElement,self).__init__(node)

        self.extract_attributes(TextElement)
        self.font = Font(node)


    def get_style(self):
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

        style = ParagraphStyle('ParagraphStyle')
        
        style.fontName = self.font.get_fontname()
        style.fontSize = float(self.font['size'])

        if self['textAlignment'] == 'Center':
            style.alignment = TA_CENTER
        elif self['textAlignment'] == 'Right':
            style.alignment = TA_RIGHT
        else:
            style.alignment = TA_LEFT
        
        return style


class Text(Element):
    local_name = 'text'

    def __init__(self,node):
        super(Text,self).__init__(node)
        self.extract_text(Text)


class FieldExpression(Element):
    local_name = 'textFieldExpression'
    attr_list = {'class': 'java.lang.String',}

    def __init__(self,node):
        super(FieldExpression,self).__init__(node)

        self.extract_attributes(FieldExpression)

        text_node = self.find_node(node,FieldExpression.local_name)
        self.data = self.get_node_data(text_node)

   

class GraphicElement(Element):
    local_name = 'graphicElement'

    attr_list = {'pen': 'Thin',}

    def __init__(self,node):
        super(GraphicElement,self).__init__(node)
        self.extract_attributes(GraphicElement)



class BaseObject(Element):
    def __init__(self,node):
        super(BaseObject,self).__init__(node)

class StaticText(BaseObject):
    
    def __init__(self,node):
        super(StaticText,self).__init__(node)

        self.reportElement = ReportElement(node)
        self.textElement = TextElement(node)
        self.text = Text(node)

    def draw(self,page,context):
        if not self.reportElement.is_printable(context):
            return
        
        P=Paragraph(self.text.data,self.textElement.get_style())

        w,h = P.wrap(self.reportElement['width'],self.reportElement['height'])

        x,y = page.translate(self.reportElement['x'],self.reportElement['y'])
        P.drawOn(page.canvas,x,y)



ALLOWED_VARIABLE_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.'

#expr_re = re.compile(r".*([\w]+).*"%[re.escape(ALLOWED_VARIABLE_CHARS)], re.UNICODE)
expr_re = re.compile(r".([\w\d\_\.]+).*", re.UNICODE)


def resolve_recursive(idx,parts,ref):
    if idx >= len(parts):
        return ref

    if ref.has_key(parts[idx]):
        return resolve_recursive(idx+1,parts,ref[parts[idx]])

    if hasattr(ref,parts[idx]):
        newref = getattr(ref,parts[idx])
        if callable(newref):
            newref = newref()
        return resolve_recursive(idx+1,parts,newref)
        
    return None

class TextField(BaseObject):
    local_name = 'textField'

    attr_list = {'pattern': '',
                 'isBlankWhenNull': False}
    
    
    def __init__(self,node):
        super(TextField,self).__init__(node)

        self.extract_attributes(TextField)

        self.reportElement = ReportElement(node)
        self.textElement = TextElement(node)
        self.fieldExpression = FieldExpression(node)


    def format(self,value):
        import datetime
        
        if self.fieldExpression['class'] == 'java.lang.String':
            return unicode(value)

        if self.fieldExpression['class'] == 'java.math.BigDecimal':
            return u'%s%s'%(self['pattern'][0],str(value))

        if self.fieldExpression['class'] == 'java.util.Date' and isinstance(value,datetime.date):
            return value.strftime(str(self['pattern']))

        return unicode(value)

    def resolve_expression(self,raw_text,context):
        match = expr_re.search(raw_text)

        if match:
            parts = match.group(1).split(".")
            return resolve_recursive(0,parts,context)

        return raw_text


    def draw(self,page,context):
        if not self.reportElement.is_printable(context):
            return

        value = self.resolve_expression(self.fieldExpression.data,context)
        if value is None and self['isBlankWhenNull']:
            value = ''
        else:
            value = self.format(value)

        P=Paragraph(value,self.textElement.get_style())

        w,h = P.wrap(self.reportElement['width'], self.reportElement['height'])

        x,y = page.translate(self.reportElement['x'],self.reportElement['y'])
        P.drawOn(page.canvas,x,y)



class Line(BaseObject):
    def __init__(self,node):
        super(Line,self).__init__(node)

    
        self.reportElement = ReportElement(node)
        self.graphicElement = GraphicElement(node)

    def draw(self,page,context):
        page.canvas.push_state_stack()
        x,y = page.translate(self.reportElement['x'],self.reportElement['y'])

        if self.graphicElement['pen'] == 'Dotted':
            page.canvas.setDash(1,2)

        page.canvas.line(x,y,x+self.reportElement['width'],y-self.reportElement['height'])
        page.canvas.setDash()

        page.canvas.pop_state_stack()


class Rectangle(BaseObject):
    def __init__(self,node):
        super(Rectangle,self).__init__(node)
    
        self.reportElement = ReportElement(node)
        self.graphicElement = GraphicElement(node)

    def draw(self,page,context):
        page.canvas.push_state_stack()
        x,y = page.translate(self.reportElement['x'],self.reportElement['y'])

        if self.graphicElement['pen'] == 'Dotted':
            page.canvas.setDash(1,2)

        # translate origin Y coordinate
        page.canvas.rect(x,y-self.reportElement['height'],self.reportElement['width'],self.reportElement['height'])

        page.canvas.setDash()
        page.canvas.pop_state_stack()


class IReportPDF(object):

    element_map = {'rectangle': Rectangle,
                   'staticText': StaticText,
                   'line': Line,
                   'textField': TextField,
                   }

    def __init__(self,template):
        self.template = template
        self.dom = parse(template)



    def get_report_attr(self,attrname):
        report = self.dom.getElementsByTagName('jasperReport')[0]
        return report.getAttribute(attrname)
        

    def get_canvas(self,filename=None):
        out = filename or StringIO()

        pageWidth = int(self.get_report_attr('pageWidth'))
        pageHeight = int(self.get_report_attr('pageHeight'))

        return Canvas(out,pagesize=(pageWidth,pageHeight))


    def get_page(self,canvas):
        page = IPage()
        for attr_name in ['pageWidth','pageHeight','columnWidth',
                          'columnSpacing','leftMargin','rightMargin',
                          'topMargin','bottomMargin']:
            attr = int(self.get_report_attr(attr_name))
            setattr(page,attr_name,attr)

        page.canvas = canvas
        return page

    def _process_element(self,element_class,node,page,context):
        element = element_class(node)
        element.draw(page,context)


    def _recursive_walk(self,start_node,page,context):
        for node in start_node.childNodes:
            if node.nodeType != Node.ELEMENT_NODE:
                continue

            if node.localName == 'elementGroup':
                self._recursive_walk(node,page,context)


            if self.element_map.has_key(node.localName):
                self._process_element(self.element_map[node.localName],
                                      node,
                                      page,
                                      context)


    def get_band(self,band_name):
        bands = self.dom.getElementsByTagName(band_name)

        if len(bands) > 0:
            return bands[0].getElementsByTagName('band')[0]

        return None

    def get_band_height(self,band_name):
        band = self.get_band(band_name)
        try:
            height = int(band.getAttribute('height'))
        except:
            height = 0

        return height


    def process_band(self,band_name,page,context):
        band = self.get_band(band_name)

        
        self._recursive_walk(band,page,context)
        return self.get_band_height(band_name)
                             


    def _print_page_start(self,page,context):
        page.offset_y += self.process_band('pageHeader',page,context)
        page.offset_y += self.process_band('columnHeader',page,context)

    def _print_page_end(self,page,context,is_last=False):
        last_page_footer_h = self.get_band_height('lastPageFooter')
        page_footer_h = self.get_band_height('pageFooter')
        page.offset_y += self.process_band('columnFooter',page,context)


        # print page footer at the bottom of page

        if last_page_footer_h > 0 and is_last:
            page.set_bottom_offset(last_page_footer_h)
            page.offset_y += self.process_band('lastPageFooter',page,context)
        else:
            page.set_bottom_offset(page_footer_h)
            page.offset_y += self.process_band('pageFooter',page,context)
        

    def parse(self,stream,context=None,row_key=None,parent_canvas=None):
        canvas = parent_canvas or self.get_canvas(stream)

        # "row" is internally registered keyword for row_key, pls don't use it
        assert(row_key != 'row')

        context = context or {}

        page_num = 1

        # print Title page
        height = self.get_band_height('title')
        if height > 0:
            page = self.get_page(canvas)
            self.process_band('title',page,context)
            if self.get_report_attr('isTitleNewPage') == 'True':
                canvas.showPage()
                page_num += 1
                height = 0


        headers_h = self.get_band_height('pageHeader') + self.get_band_height('columnHeader')
        detail_h = self.get_band_height('detail')
        column_footer_h = self.get_band_height('columnFooter')
        page_footer_h = self.get_band_height('pageFooter')
        last_page_footer_h = self.get_band_height('lastPageFooter')


        if context.has_key(row_key):
            rowcount = len(context[row_key])
            row_idx = 0
            page_idx = 1

            while True:
                context['page_num'] = page_num
                page = self.get_page(canvas)
                # substract height(title) only one time
                page.offset_y += height

                self._print_page_start(page,context)
                detail_availabe_h = page.get_viewpoint_height() - headers_h - column_footer_h - page_footer_h - height
                height = 0

                while detail_h <= detail_availabe_h and row_idx < rowcount:
                    context['row_id0'] = row_idx
                    context['row_id'] = row_idx +1
                    context['row'] = context[row_key][row_idx]
                    page.offset_y += self.process_band('detail',page,context)

                    row_idx += 1

                    detail_availabe_h -= detail_h


                self._print_page_end(page,context,(row_idx == rowcount) )
                page_num += 1

                if row_idx == rowcount:
                    break

                canvas.showPage()

        else:
            # print "empty" iterator
            page = self.get_page(canvas)

            self._print_page_start(page,context)
            page.offset_y += self.process_band('detail',page,context)
            self._print_page_end(page,context,True)
            
            
        canvas.showPage()

        canvas.save()

        return canvas 





if __name__ == '__main__':
    report = IReportPDF('data/test_report.jrxml')

    context = {'testvalue': 'this is test value'}

    rows = []
    rows.append({'test_c1': 1, 'test_c2': 'column 2','test_c3': {'a': 'col a','b':'col b'}})
    rows.append({'test_c1': 1, 'test_c2': 'column 2','test_c3': {'a': 'col a','b':'col b'}})
    rows.append({'test_c1': 1, 'test_c2': 'column 2','test_c3': {'a': 'col a','b':'col b'}})
    rows.append({'test_c1': 1, 'test_c2': 'column 2','test_c3': {'a': 'col a','b':'col b'}})
    rows.append({'test_c1': 1, 'test_c2': 'column 2','test_c3': {'a': 'col a','b':'col b'}})
    
    context['items'] = rows


    report.parse('doc.pdf',context,'items')



    
    


        
