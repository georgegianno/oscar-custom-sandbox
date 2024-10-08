from django import template
from django.template.loader import select_template
from django.db.models import Q
from oscar.core.loading import get_model
from oscar.core.compat import get_user_model
from oscar.apps.catalogue.views import category_occurencies_map
import random


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

@register.simple_tag()
def get_recommended_products(request):
    user = request.user
    user_favorites = Favorite.objects.filter(user=user)
    recommended_products = []
    if user_favorites:
        products = Product.objects.exclude(id__in=user_favorites.values_list('product_id',flat=True))
        categories = category_occurencies_map(user_favorites)[:2][::-1]
        latest_two = user_favorites.order_by('-created_at')[:2]
        latest = user_favorites.filter(id__in=latest_two)
        latest = category_occurencies_map(latest)[:2]
        latest.extend(categories)
        latest.append(latest[-1])
        for id in latest:
            recommended = products.filter(Q(categories__id=id) | Q(parent__categories__id=id)). \
                exclude(id__in=[x.id for x in recommended_products])
            try:
                random_index = random.randint(0, recommended.count() - 1)
                recommended_products.append(recommended[random_index])
            except Exception as e:
                pass
    return recommended_products 
