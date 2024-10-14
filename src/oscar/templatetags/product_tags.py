from django import template
from django.template.loader import select_template
from django.db.models import Q
from oscar.core.loading import get_model
from oscar.core.compat import get_user_model
from oscar.apps.catalogue.views import category_occurencies_map, recommendation_generator
from django.db.models import Sum

User = get_user_model()
Product = get_model("catalogue", "product")
Category = get_model("catalogue", "category")
Favorite = get_model("catalogue", "Favorite")
Order = get_model('order', 'Order')


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
        latest_three = category_occurencies_map(latest)[:3]
        latest_three.extend(categories)
        target = latest_three
        recommended_products = recommendation_generator(target, products, recommended_products)
        return recommended_products 

@register.simple_tag()
def get_title(product):
    return product.get_title()

@register.simple_tag(takes_context=True)
def total_order_value(context, email, for_guests=None):
    # The count of the total of the orders the customer made as guest and as user
    orders = Order.objects.filter(Q(guest_email=email)|Q(user__email=email)).filter(status='Complete')
    if for_guests:
        orders = orders.filter(user=None)
    if orders:
        orders_total_value = float(orders.aggregate(Sum('total_incl_tax')).get('total_incl_tax__sum'))
    else: 
        orders_total_value = 0
    return orders_total_value
