from oscar.apps.promo.utils import remove_gift_if_needed

# This evaluates product removal in every request in the site, so we avoid expired or unqualified gifts
# to stick in the basket.
class PromoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        basket = request.basket
        if basket.pk:
            remove_gift_if_needed(basket)
        response = self.get_response(request)
        return response 
    
