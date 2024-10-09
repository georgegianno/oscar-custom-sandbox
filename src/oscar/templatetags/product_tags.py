from django import template
from django.template.loader import select_template
from django.db.models import Q
from oscar.core.loading import get_class, get_model
from oscar.core.compat import get_user_model
from oscar.core.utils import is_ajax
from django.shortcuts import render
from django.http import JsonResponse


User = get_user_model()
Product = get_model("catalogue", "product")
Category = get_model("catalogue", "category")
Favorite = get_model("catalogue", "Favorite")

register = template.Library()


@register.simple_tag(takes_context=True)
def render_product(context, product):
    """
    Render a product snippet as you would see in a browsing display.

    This templatetag looks for different templates depending on the UPC and
    product class of the passed product.  This allows alternative templates to
    be used for different product classes.
    """
    if not product:
        # Search index is returning products that don't exist in the
        # database...
        return ""

    names = [
        "oscar/catalogue/partials/product/upc-%s.html" % product.upc,
        "oscar/catalogue/partials/product/class-%s.html"
        % product.get_product_class().slug,
        "oscar/catalogue/partials/product.html",
    ]
    template_ = select_template(names)
    context = context.flatten()

    # Ensure the passed product is in the context as 'product'
    context["product"] = product
    return template_.render(context)

@register.simple_tag()
def is_in_favorites(request, pk):
    if Favorite.objects.filter(user=request.user, product__pk=pk):
        return True
    return False

def favorite_category_filtering(queryset):
    a = list(queryset.exclude(product__categories=None).values_list('product__categories', flat=True).distinct())
    b = list(queryset.exclude(product__parent__categories=None).values_list('product__parent__categories', flat=True).distinct())
    a.extend(b)
    c = a
    map = {id: queryset.filter(Q(product__categories__id=id) | Q(product__parent__categories__id=id)).distinct().count() for id in c} 
    return sorted(map.keys(), key=lambda x: map[x], reverse=True)

@register.simple_tag()
def get_recommended_products(request):
    user = request.user
    user_favorites = Favorite.objects.filter(user=user)
    categories = favorite_category_filtering(user_favorites)[:3]
    latest_two = user_favorites.order_by('-created_at')[:2]
    latest = user_favorites.filter(id__in=latest_two).order_by('created_at')
    latest = favorite_category_filtering(latest)[:2]
    categories.extend(latest)
    print(categories)
    recommended_products = Product.objects.filter( \
        Q(categories__id__in=categories) | Q(parent__categories__id__in=categories)).filter(is_public=True). \
            exclude(id__in=user_favorites.values('product_id'))[:5]
    return recommended_products