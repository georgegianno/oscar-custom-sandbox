from modeltranslation.translator import translator, TranslationOptions
from .models import Promo

class PromoTranslationOptions(TranslationOptions):
    fields = ['title', 'cart_text']

translator.register(Promo, PromoTranslationOptions)