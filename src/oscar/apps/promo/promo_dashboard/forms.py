from django import forms
from oscar.apps.promo.models import Promo
from oscar.core.loading import get_model
from django.db.models import Q


Category = get_model('catalogue','Category')
Range = get_model('offer', 'Range')

class PromoForm(forms.ModelForm):
    promo_range = forms.ModelChoiceField(
        queryset=Range.objects.all(), 
        label="Gift range products", 
        required=False,
        help_text=("Select the range with the gift products. Gifts must be unpublished with price 0"),
        empty_label = 'No range selected'
    )
    included_range = forms.ModelChoiceField(
        queryset=Range.objects.all(), 
        label="Range products to include",
        required=False,
        help_text=("Select the range of products that must be included in the basket for the offer to be valid"), 
        empty_label = 'All products'
    )
    excluded_range = forms.ModelChoiceField(
        queryset=Range.objects.all(), 
        label="Range products to exclude",
        required=False,
        help_text=("Choose the specific range of products in the basket that will be excluded from the offer"),
        empty_label = 'Exclude nothing'
    )
    contained_range = forms.ModelChoiceField(
        queryset=Range.objects.all(), 
        label="Range specific products to contain",
        required=False,
        help_text=("Select the range of products that basket needs to contain for the offer to be applied \
            (at least one of them)."),
        empty_label = 'Any product'
    )
    required_amount = forms.IntegerField(
        label="Number of products",
        min_value=0,
        required=False,
        help_text=("Set the number of total products in basket above which the offer can be applied")
    )
    price_threshold = forms.IntegerField(
        label="Price Threshold",
        min_value=0,
        required=False,
        help_text=("Set the total price above which the offer can be applied")
    )
    show_price_progress_bar = forms.BooleanField(
        label="Show price progress bar",
        required=False,
        initial=False, 
        help_text=("Show progress bar for remaining price only if there is exactly one active promo")
    ) 
    is_active = forms.BooleanField(
        label="Active",
        required=False,
        initial=False, 
        help_text=("Activate the offer")
    )
    class Meta:
        model = Promo
        fields = [
            'title',
            'cart_text',
            'promo_range',
            'included_range',
            'excluded_range',
            'contained_range',
            'required_amount',
            'price_threshold',
            'show_price_progress_bar',
            'is_active',
        ]

    # def save(self, commit=True):
    #     instance = super().save(commit=False)
    #     if commit:
    #         if instance.promo_range:
    #             range = self.cleaned_data.get('promo_range')
    #             if range:
    #                 products = range.all_products()
    #                 for product in products.exclude(Q(is_public=False)&Q(stockrecords__price_retail=0)):
    #                     range.remove_product(product)
    #                 instance.promo_range = range
    #                 other_promo_ranges = Range.objects.filter(id__in=Promo.objects.values_list('promo_range_id', flat=True)).exclude(id=range.id)
    #                 for other in other_promo_ranges:
    #                     common = range.all_products().filter(id__in=other.all_products().values_list('id', flat=True))
    #                     if common:
    #                         for product in common:
    #                             other.remove_product(product) 
    #         instance.save()
    #     return instance 