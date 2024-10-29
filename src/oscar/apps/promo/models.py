from django.db import models
from django.utils.translation import gettext_lazy as _
from oscar.apps.offer.models import Range


class Promo(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    promo_range = models.ForeignKey('offer.Range', verbose_name=_('Promo products'), related_name='promo_range', blank=True, null=True, on_delete=models.SET_NULL)
    excluded_range = models.ForeignKey('offer.Range', verbose_name=_('Excluded products'), related_name='excluded_range', blank=True, null=True, on_delete=models.SET_NULL)
    contained_range = models.ForeignKey('offer.Range', verbose_name=_('Contained products'), related_name='contained_range', blank=True, null=True, on_delete=models.SET_NULL)
    included_range = models.ForeignKey('offer.Range', verbose_name=_('Included products'), related_name='included_range', blank=True, null=True, on_delete=models.SET_NULL)
    required_amount = models.IntegerField(default=0, null=True, blank=True, verbose_name='Required Amount')
    price_threshold = models.DecimalField(max_digits=19, decimal_places=2, null=True, blank=True, verbose_name='Price threshold')
    show_price_progress_bar = models.BooleanField(_('Is active'), default=False)
    cart_text = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(_('Is active'), default=False)

    def __str__(self):
        return self.title

