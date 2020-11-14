This is abstract attribute engine, which you can connect to any of your
Django models via foreign key and ManyToMany relation. For example,
we have model Product, which needs to store some user defined attributes.
To enable AttributeEngine:

class Product:
    ... your product fields ...
    attr_groups = models.ManyToManyField(AttributeGroup)


class ProductAttr(AttributeStorage):
    product = models.ForeignKey(Product)
