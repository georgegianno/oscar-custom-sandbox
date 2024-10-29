from decimal import Decimal as D
from django.utils.translation import gettext_lazy as _
from oscar.core.loading import get_model
from django.db.models import Q, Sum
from .models import Promo
import json
from django.http import JsonResponse
from django.template.loader import render_to_string

Product = get_model('catalogue', 'Product')
Category = get_model('catalogue', 'Category')

def get_active_promos():
    return Promo.objects.filter(is_active=True).exclude(price_threshold=0).exclude(promo_range=None)

# This is the main identifier of whether a promo is active and valid or not. It return the list of product
# ids that can actually be added as gifts.
def get_gifts(promo):
    if promo in get_active_promos():
        gift_list = promo.promo_range.all_products().values_list('id', flat=True)
        gift_products = Product.objects.filter(id__in=gift_list).filter(stockrecords__num_in_stock__gt=0)
        for gift in gift_products:
            stockrecord = gift.stockrecords.first()
            if stockrecord.num_allocated and int(stockrecord.num_allocated) >= int(stockrecord.num_in_stock):
                gift_products = gift_products.exclude(id=gift.id)
        gift_products = gift_products.values_list('id', flat=True)
        return list(gift_products) if len(gift_products)>0 else None
    return None

# If an active promo has no threshold set, we ignore it
def get_gift_threshold(promo):
    if get_gifts(promo):
        return promo.price_threshold
    return None

# This returns the products that are excluded from promo and their existence will not affect promo applications 
def products_to_exclude_for_gift(basket, promo, included_products=None, contained_products=None,  \
        excluded_products=None, required_amount=0):
    products = Product.objects.none()
    exclude_all_products = Product.objects.all()
    products_in_basket = Product.objects.filter(id__in=basket.lines.values_list('product_id',flat=True))
    if promo.contained_range:
        contained_products = promo.contained_range.all_products().values_list('id',flat=True) 
    if promo.included_range:
        included_products = promo.included_range.all_products().values_list('id',flat=True)
    if promo.excluded_range:
        excluded_products = promo.excluded_range.all_products().values_list('id',flat=True)
    if promo.required_amount:
        required_amount = promo.required_amount
    if contained_products and not products_in_basket.filter(id__in=contained_products): 
        return exclude_all_products
    if required_amount and basket.num_items < required_amount:
        return exclude_all_products
    if included_products:
        products = Product.objects.exclude(id__in=included_products)
    if excluded_products:
        products = Product.objects.filter(Q(id__in=products.values_list('id', flat=True) ) | Q(id__in=excluded_products))
    if required_amount and required_amount > 1:
        valid_products = products_in_basket.filter(is_public=True).filter(stockrecords__price__gt=0). \
        exclude(id__in=products.values_list('id', flat=True))
        valid_lines = basket.lines.filter(product__in=valid_products)
        number_of_valid_items = valid_lines.aggregate(number=Sum('quantity')).get('number')
        if number_of_valid_items and number_of_valid_items < required_amount:
            return exclude_all_products
    return products

# This is the sum of the products in basket after exclusions
def sum_of_valid_products_in_basket(basket, promo):
    if get_gifts(promo):
            excluded_products = products_to_exclude_for_gift(basket, promo)
            products_in_basket = Product.objects.filter(id__in=basket.lines.values('product_id'))
            total_price_ex_products = D('0.00')
            for product in products_in_basket.filter(id__in=excluded_products):
                product_line = basket.lines.get(product=product)
                if product.is_parent:
                    product_strategy = basket.strategy.fetch_for_parent(product)
                    total_price_ex_products += product_strategy.price.incl_tax * product_line.quantity
                else:
                    product_strategy = basket.strategy.fetch_for_product(product)
                    total_price_ex_products += product_strategy.price.incl_tax * product_line.quantity
            sum_of_valid_products_in_basket = basket.total_incl_tax - total_price_ex_products
            return sum_of_valid_products_in_basket
    return False   

# This decides if a basket qualifies for a gift, regardless if it contains one or not 
def can_add_gift_in_basket(basket, promo):
    if get_gifts(promo) and sum_of_valid_products_in_basket(basket, promo) >= get_gift_threshold(promo):
        return True
    return False

# Returns the line id that has any available gift as product 
def check_if_gift_is_in_basket(basket, promo, return_line=None):
    products_in_basket = Product.objects.filter(id__in=basket.lines.values_list(('product_id'), flat=True))
    gifts_in_basket = products_in_basket.filter(is_public=False).filter(stockrecords__price=0) \
        .filter(id__in = promo.promo_range.all_products().values_list('id',flat=True) )
    if gifts_in_basket:
        gift=gifts_in_basket.first()
        if return_line:
            gift_line = basket.lines.get(product_id=gift.id)
            return gift_line.id
        return gift.id
    return False

# The endpoint where javascript fetches data to do the selection of a gift
def select_gift(request):
    data = {}
    for promo in get_active_promos():
        gifts = get_gifts(promo)
        data[promo.id] = {}
        data[promo.id]['gifts'] = gifts
        if gifts and request.method == 'POST':
            gift_id = json.loads(request.body.decode('utf-8')).get('gift')
            if gift_id and int(gift_id) in gifts:
                basket = request.basket
                if basket.lines.filter(product_id=int(gift_id)) and basket.lines.filter(product_id=int(gift_id)).first().quantity==1:
                    product = Product.objects.get(id=gift_id)
                    line = basket.lines.get(product=product)
                    print(line, 'aaaaaaaaaa')
                    gift_list = render_to_string('promo/promo_product_list.html', {'gifts': Product.objects.filter(id__in = gifts), 'promo': promo})
                    gift_line_html = render_to_string('promo/basket_gift_line.html', {'line': line,'product': product, 'promo':promo.id})
                    data['gift_line_html'] = gift_line_html
                    data['gift_line_id'] = line.id
                    data['gift_list'] = gift_list
    return JsonResponse(data)

# When the promo is activated, we add a gift in the baskets that qualify for it, if the user has not triggered
# gift addition(i.e. with add product in basket or quantity change in basket)
def add_gift_if_needed(basket):
        for promo in get_active_promos():
            gifts = get_gifts(promo)
            if gifts:
                gift_in_basket = check_if_gift_is_in_basket(basket, promo)
                can_add_gift = can_add_gift_in_basket(basket, promo)
                if gift_in_basket is False and can_add_gift is True:
                    product_to_add = Product.objects.get(id=gifts[0])
                    basket.add_product(product_to_add)

def remove_gift_if_needed(basket):
    # The removal is tricky because it happens with middleware. First we check the promos with specific conditions and then
    # we check for any other products that could possibly be gifts in the past and now they are left in the basket
    zeros = Product.objects.filter(is_public=False).filter(stockrecords__price=0)
    for promo in Promo.objects.all():
        gifts = get_gifts(promo)
        if gifts:
            zeros = zeros.exclude(id__in=gifts)
        gift_in_basket_id = check_if_gift_is_in_basket(basket, promo)
        if gift_in_basket_id is not False:
            if not promo.is_active or not gifts or (gifts and gift_in_basket_id not in gifts) \
                or can_add_gift_in_basket(basket, promo) is False:
                basket.lines.filter(product_id=gift_in_basket_id).delete()
    if zeros:
        basket.lines.filter(product__in=zeros).delete()

# We update the BasketView get_context_data() method with a progress bar and cart_texts for every promo in cart_notification.html
def update_basket_for_promo_if_needed(basket, context):
    promos = get_active_promos()
    if promos and promos.count()==1 and promos.first().show_price_progress_bar is True:
        promo  = promos.first()
        gift_threshold = get_gift_threshold(promo)
        sum_of_valid_products_total = sum_of_valid_products_in_basket(basket, promo)
        away_from_gift = round(float(gift_threshold - sum_of_valid_products_total), 2)
        context['show_progress_bar'] = True
        context['promo'] = promo
        context['away_from_gift_as_number'] = round(away_from_gift, 2)
        context['away_from_gift_as_string'] = str(round(away_from_gift, 2)).replace(",", ".")
        context['gift_threshold'] = int(gift_threshold)
        context['sum_of_valid_products_total'] = str(round(float(sum_of_valid_products_total), 2)).replace(",", ".")
    elif promos:
            context['promos'] = promos
    return context

# We update the basket method get_basket_info() with the data for every promo
def get_promo_data(basket, data):
    for promo in get_active_promos():
        gift_in_basket = check_if_gift_is_in_basket(basket, promo, return_line = True)
        can_add = can_add_gift_in_basket(basket, promo)
        available_gifts = get_gifts(promo)
        data[promo.id] = {}
        data[promo.id]['gift_product'] = gift_in_basket
        data[promo.id]['can_add_gift'] = can_add
        data[promo.id]['sum_of_valid_products_in_basket'] = sum_of_valid_products_in_basket(basket, promo)
        data[promo.id]['gift_product_price_threshold'] = get_gift_threshold(promo)
        if available_gifts:
            data[promo.id]['gifts'] = available_gifts
        num_items = int(basket.num_items)
        if gift_in_basket is not False and can_add is False:
            num_items -= 1
        data['num_items'] = num_items
    return data
