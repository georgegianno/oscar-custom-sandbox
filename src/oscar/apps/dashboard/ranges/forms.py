import re

from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


from oscar.core.loading import get_model

Product = get_model("catalogue", "Product")
Category = get_model("catalogue", "Category")
Range = get_model("offer", "Range")
RangeProductFileUpload = get_model("offer", "RangeProductFileUpload")

UPC_SET_REGEX = re.compile(r"[^,\s]+")


class RangeForm(forms.ModelForm):
    class Meta:
        model = Range
        fields = [
            "name",
            "description",
            "is_public",
            "includes_all_products",
            "parents_only",
            "included_categories",
        ]
 
    def check_parents_only(self, instance):
        products = instance.all_products()
        parents = products.filter(structure='parent')
        children = products.filter(structure='child')
        if instance.parents_only is True:
            if children:
                for product in children:
                    instance.remove_product(product)
        elif products and parents and not children:
            for product in Product.objects.filter(parent__in=parents):
                instance.add_product(product)

    def add_or_remove_included_categories(self, instance, included_categories, cleaned_categories):
        remove_list = []
        add_list = []
        initial_remove = included_categories.exclude(id__in=cleaned_categories.values_list('id', flat=True))
        for x in initial_remove:
            remove_list.extend([y.id for y in x.get_descendants_and_self()])
        initial_add = cleaned_categories.exclude(id__in=included_categories.values_list('id', flat=True))
        for x in initial_add:
            add_list.extend([y.id for y in x.get_descendants_and_self()])
        included_list = [x.id for x in included_categories]
        for product in Product.objects.filter(categories__in=add_list):
            instance.add_product(product)
        for product in Product.objects.filter(categories__in=remove_list):
            instance.remove_product(product)
        set_categories = Category.objects.filter( \
            Q(id__in=included_list) | Q(id__in=add_list)).exclude(id__in=remove_list).distinct()
        instance.included_categories.set(set_categories)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        included_categories = instance.included_categories.all()
        cleaned_categories = self.cleaned_data.get('included_categories')
        if list(included_categories) != list(cleaned_categories):
            self.add_or_remove_included_categories( \
                instance, included_categories, cleaned_categories)
        self.check_parents_only(instance)
        return instance 

# pylint: disable=attribute-defined-outside-init
class RangeProductForm(forms.Form):
    query = forms.ModelMultipleChoiceField(
        label=_("Products"),
        queryset=Product.objects.all(),
        required=False,
        help_text=_("Select Products")
    )
    file_upload = forms.FileField(
        label=_("File of SKUs or UPCs"),
        required=False,
        max_length=255,
        help_text=_("Either comma-separated, or one identifier per line"),
    )

    def __init__(self, product_range, *args, **kwargs):
        self.product_range = product_range
        super().__init__(*args, **kwargs)

    def clean_query_with_upload_type(self, raw, upload_type):
        # Check that the search matches some products
        ids = set(UPC_SET_REGEX.findall(raw))
        # switch for included or excluded products
        if upload_type == RangeProductFileUpload.EXCLUDED_PRODUCTS_TYPE:
            products = self.product_range.excluded_products.all()
            action = _("excluded from this range")
        else:
            products = self.product_range.all_products()
            action = _("added to this range")
        existing_skus = set(
            products.values_list("stockrecords__partner_sku", flat=True)
        )
        existing_upcs = set(products.values_list("upc", flat=True))
        existing_ids = existing_skus.union(existing_upcs)
        new_ids = ids - existing_ids
        if len(new_ids) == 0:
            self.add_error(
                "query",
                _(
                    "The products with SKUs or UPCs matching %(skus)s have "
                    "already been %(action)s"
                )
                % {"skus": ", ".join(ids), "action": action},
            )
        else:
            self.products = Product._default_manager.filter(
                Q(stockrecords__partner_sku__in=new_ids) | Q(upc__in=new_ids)
            )
            if len(self.products) == 0:
                self.add_error(
                    "query",
                    _("No products exist with a SKU or UPC matching %s")
                    % ", ".join(ids),
                )
            found_skus = set(
                self.products.values_list("stockrecords__partner_sku", flat=True)
            )
            found_upcs = set(self.products.values_list("upc", flat=True))
            found_ids = found_skus.union(found_upcs)
            self.missing_skus = new_ids - found_ids
            self.duplicate_skus = existing_ids.intersection(ids)

    def clean(self):
        clean_data = super().clean()
        raw = clean_data["query"]
        return raw

    def get_products(self):
        return self.products if hasattr(self, "products") else []

    def get_missing_skus(self):
        return self.missing_skus

    def get_duplicate_skus(self):
        return self.duplicate_skus


# pylint: disable=attribute-defined-outside-init
class RangeExcludedProductForm(RangeProductForm):
    """
    Form to add products in range.excluded_products
    """

    def clean_query(self):
        raw = self.cleaned_data["query"]
        if not raw:
            return raw

        # Check that the search matches some products
        ids = set(UPC_SET_REGEX.findall(raw))
        products = self.product_range.excluded_products.all()
        existing_skus = set(
            products.values_list("stockrecords__partner_sku", flat=True)
        )
        existing_upcs = set(products.values_list("upc", flat=True))
        existing_ids = existing_skus.union(existing_upcs)
        new_ids = ids - existing_ids

        if len(new_ids) == 0:
            raise forms.ValidationError(
                _(
                    "The products with SKUs or UPCs matching %s are already in"
                    " this range"
                )
                % (", ".join(ids))
            )

        self.products = Product._default_manager.filter(
            Q(stockrecords__partner_sku__in=new_ids) | Q(upc__in=new_ids)
        )
        if len(self.products) == 0:
            raise forms.ValidationError(
                _("No products exist with a SKU or UPC matching %s") % ", ".join(ids)
            )

        found_skus = set(
            self.products.values_list("stockrecords__partner_sku", flat=True)
        )
        found_upcs = set(self.products.values_list("upc", flat=True))
        found_ids = found_skus.union(found_upcs)
        self.missing_skus = new_ids - found_ids
        self.duplicate_skus = existing_ids.intersection(ids)

        return raw
