# pylint: disable=wildcard-import, unused-wildcard-import

"""
Vanilla product models
"""
from oscar.apps.catalogue.abstract_models import *
from oscar.core.loading import is_model_registered
from django.utils.translation import gettext_lazy as _
from oscar.core.compat import AUTH_USER_MODEL

__all__ = ["ProductAttributesContainer"]


if not is_model_registered("catalogue", "ProductClass"):

    class ProductClass(AbstractProductClass):
        pass

    __all__.append("ProductClass")


if not is_model_registered("catalogue", "Category"):

    class Category(AbstractCategory):
        pass

    __all__.append("Category")


if not is_model_registered("catalogue", "ProductCategory"):

    class ProductCategory(AbstractProductCategory):
        pass

    __all__.append("ProductCategory")


if not is_model_registered("catalogue", "Product"):

    class Product(AbstractProduct):
        pass

    __all__.append("Product")


if not is_model_registered("catalogue", "ProductRecommendation"):

    class ProductRecommendation(AbstractProductRecommendation):
        pass

    __all__.append("ProductRecommendation")


if not is_model_registered("catalogue", "ProductAttribute"):

    class ProductAttribute(AbstractProductAttribute):
        pass

    __all__.append("ProductAttribute")


if not is_model_registered("catalogue", "ProductAttributeValue"):

    class ProductAttributeValue(AbstractProductAttributeValue):
        pass

    __all__.append("ProductAttributeValue")


if not is_model_registered("catalogue", "AttributeOptionGroup"):

    class AttributeOptionGroup(AbstractAttributeOptionGroup):
        pass

    __all__.append("AttributeOptionGroup")


if not is_model_registered("catalogue", "AttributeOption"):

    class AttributeOption(AbstractAttributeOption):
        pass

    __all__.append("AttributeOption")


if not is_model_registered("catalogue", "Option"):

    class Option(AbstractOption):
        pass

    __all__.append("Option")


if not is_model_registered("catalogue", "ProductImage"):

    class ProductImage(AbstractProductImage):
        pass

    __all__.append("ProductImage")

class Favorite(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name=_("User"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user} - {self.product}"
    
    __all__.append("Favorite")