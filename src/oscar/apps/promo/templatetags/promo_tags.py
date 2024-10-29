from django import template
from oscar.core.loading import get_model
from oscar.apps.promo.utils import get_gifts, check_if_gift_is_in_basket, can_add_gift_in_basket, get_active_promos
from django.conf import settings

register = template.Library()
Product = get_model('catalogue','Product')

@register.simple_tag()
def active_promos():
    return get_active_promos() 

@register.simple_tag()
def promo_product_list(promo):
    return Product.objects.filter(id__in = get_gifts(promo)) if get_gifts(promo) else None  

@register.simple_tag()
def line_is_gift(line):
    if line.price_incl_tax == 0 and line.product.is_public == False:
        promos = get_active_promos()
        for promo in promos:
            gifts = get_gifts(promo)
            if gifts and line.product.id in gifts:
                return promo.id
    return None