"""
========================
Template aggreate tags
-----------------------

tags:
 - agg_init   - init variable
 - agg_sum    - sumator
 - agg_get    - retrive variable


Tags operate with Decimal values.

Description:
---------------
At the top of template use {% agg_init 'key' %}

then in loop you can use
{% agg_sum value_to_sum 'key' %}

when need print total value just output it with
{{ key }}


For some reason, key should be composite:
{% agg_init 'key' 'subkey' model.type %}
{% agg_sum value_to_sum 'key' 'subkey' model.type %}

Number of key part items not limited.

In this case key will be composite by call str() for each key item.


Retrive composite key value possible with agg_get:
{% agg_get 'key' 'subkey' model.id model.type %}


Typically, composite key using in cross-grid reports where you don't know
how many columns will be generated, but require to have total line with value for each column



===============================
Complete example:
-------------------------------
{% load aggregate %}



<table>
  <thead>
     <tr>
       <th>Date</th>
       <th>Sum</th>
     </tr>
  </thead>
  <tbody>
    {% for payment in all_payments %}
      <tr>
        <td>{{ payment.date }}</td>
        <td>{{ payment.sum }}</td>
      </tr>
      {% agg_sum payment.sum 'total_payments' %}
    {% endfor %}
    <tr>
      <td>Total sum</td>
      <td>{{ total_payments }}</td>
    </tr>

    {% comment %}
      Or get value with agg_get:
    {% endcomment %}
    <tr>
      <td>Total sum</td>
      <td>{% agg_get 'total_payments' %}</td>
    </tr>
  </tbody>
</table>
"""

from decimal import Decimal

from django import template
from django.template import Variable


register = template.Library()


def get_or_set_marker(context):
    for d in context.dicts:
        if 'agg_top' in d:
            return d
    context.dicts[-1]['agg_top'] = True
    return context.dicts[-1]


class AggInitNode(template.Node):
    def __init__(self, keys):
        self.keys = [ Variable(key) for key in keys]

    def render(self, context):
        key = "".join([ unicode(item.resolve(context)) for item in self.keys ])
        dicts = get_or_set_marker(context)
        dicts[key] = Decimal('0.0')
        return ''


@register.tag()
def agg_init(parset, token):
    items = token.split_contents()
    if len(items) < 2:
        raise template.TemplateSyntaxError(
            "%r tag requires at least 1 arguments" % items[0])
    return AggInitNode(items[1:])


class AggGetNode(template.Node):
    def __init__(self, keys, store_as):
        self.keys = [ Variable(key) for key in keys]
        self.store_as = store_as

    def render(self, context):
        key = "".join([ unicode(item.resolve(context)) for item in self.keys ])
        value = context.get(key)
        if self.store_as:
            context[self.store_as] = value
            return ''
        else:
            return value


@register.tag()
def agg_get(parset, token):
    args = token.split_contents()
    store_as = None

    if len(args) < 2:
        raise template.TemplateSyntaxError(
            "%r tag requires at least 1 arguments" % args[0])

    if len(args) >=4 and args[-2] == 'as':
        store_as = args[-1]
        args = args[:-2]

    return AggGetNode(args[1:], store_as)


class AggSumNode(template.Node):
    def __init__(self, value, keys):
        self.keys = [ Variable(key) for key in keys]
        self.value = Variable(value)

    def render(self, context):
        key = "".join([ unicode(item.resolve(context)) for item in self.keys ])
        value = context.get(key) or Decimal('0.0')
        value += self.value.resolve(context) or Decimal('0.0')
        dicts = get_or_set_marker(context)
        dicts[key] = value

        return ''


@register.tag()
def agg_sum(parset, token):
    items = token.split_contents()
    if len(items) < 3:
        raise template.TemplateSyntaxError(
            "%r tag requires at least 2 arguments" % items[0])
    return AggSumNode(items[1], items[2:])
