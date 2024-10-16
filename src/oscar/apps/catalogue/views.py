from urllib.parse import quote

from django.http import Http404, HttpResponsePermanentRedirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView

from oscar.apps.catalogue.signals import product_viewed
from oscar.core.loading import get_class, get_model
from oscar.core.compat import get_user_model
from oscar.core.utils import is_ajax
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
import random

User = get_user_model()
Product = get_model("catalogue", "product")
Category = get_model("catalogue", "category")
ProductCategory = get_model("catalogue", "ProductCategory")
ProductAlert = get_model("customer", "ProductAlert")
ProductAlertForm = get_class("customer.forms", "ProductAlertForm")
Favorite = get_model("catalogue", "Favorite")


class ProductDetailView(DetailView):
    context_object_name = "product"
    model = Product
    view_signal = product_viewed
    template_folder = "catalogue"

    # Whether to redirect to the URL with the right path
    enforce_paths = True

    # Whether to redirect child products to their parent's URL. If it's disabled,
    # we display variant product details on the separate page. Otherwise, details
    # displayed on parent product page.
    enforce_parent = False

    def get(self, request, *args, **kwargs):
        """
        Ensures that the correct URL is used before rendering a response
        """
        # pylint: disable=attribute-defined-outside-init
        self.object = product = self.get_object()

        if redirect_to := self.redirect_if_necessary(request.path, product):
            return redirect_to

        # Do allow staff members so they can test layout etc.
        if not self.is_viewable(product, request):
            raise Http404()

        response = super().get(request, *args, **kwargs)
        self.send_signal(request, response, product)
        return response

    def is_viewable(self, product, request):
        return product.is_public or request.user.is_staff

    def get_object(self, queryset=None):
        # Check if self.object is already set to prevent unnecessary DB calls
        if hasattr(self, "object"):
            return self.object
        else:
            return super().get_object(queryset)

    def redirect_if_necessary(self, current_path, product):
        if self.enforce_parent and product.is_child:
            return HttpResponsePermanentRedirect(product.parent.get_absolute_url())

        if self.enforce_paths:
            expected_path = product.get_absolute_url()
            if quote(expected_path) != quote(current_path):
                return HttpResponsePermanentRedirect(expected_path)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["alert_form"] = self.get_alert_form()
        ctx["has_active_alert"] = self.get_alert_status()
        return ctx

    def get_alert_status(self):
        # Check if this user already have an alert for this product
        has_alert = False
        if self.request.user.is_authenticated:
            alerts = ProductAlert.objects.filter(
                product=self.object, user=self.request.user, status=ProductAlert.ACTIVE
            )
            has_alert = alerts.exists()
        return has_alert

    def get_alert_form(self):
        return ProductAlertForm(user=self.request.user, product=self.object)

    def send_signal(self, request, response, product):
        self.view_signal.send(
            sender=self,
            product=product,
            user=request.user,
            request=request,
            response=response,
        )

    def get_template_names(self):
        """
        Return a list of possible templates.

        If an overriding class sets a template name, we use that. Otherwise,
        we try 2 options before defaulting to :file:`catalogue/detail.html`:

            1. :file:`detail-for-upc-{upc}.html`
            2. :file:`detail-for-class-{classname}.html`

        This allows alternative templates to be provided for a per-product
        and a per-item-class basis.
        """
        if self.template_name:
            return [self.template_name]

        return [
            "oscar/%s/detail-for-upc-%s.html" % (self.template_folder, self.object.upc),
            "oscar/%s/detail-for-class-%s.html"
            % (self.template_folder, self.object.get_product_class().slug),
            "oscar/%s/detail.html" % self.template_folder,
        ]

def favorites_add_or_remove(request, product_pk):
    user = User.objects.get(id=request.user.id)
    product = Product.objects.get(pk=product_pk)
    favorite_exists = Favorite.objects.filter(user=user, product=product)
    data={}
    title = product.parent.title if product.structure =='child' else product.title
    if not favorite_exists:
        Favorite.objects.create(user=user, product=product)
        data['added'] = True
        data['success_message'] = title + _(" was added to your favorites")
        data['display_text'] = _('Remove from favorites')
    else:
        Favorite.objects.filter(user=user, product=product).delete()
        data['removed'] = True
        data['success_message'] = title + _(" was removed from your favorites")
        data['display_text'] = _('Add to favorites')
    if is_ajax(request):
        return JsonResponse(data)
    return render(request, 'oscar/catalogue/partials/add_to_basket_form.html', {'product': product})

def category_occurencies_map(queryset):
    a = list(queryset.exclude(product__categories=None).values_list('product__categories', flat=True).distinct())
    b = list(queryset.exclude(product__parent__categories=None).values_list('product__parent__categories', flat=True).distinct())
    a.extend(b)
    c = a
    map = {id: queryset.filter(Q(product__categories__id=id) | Q(product__parent__categories__id=id)).distinct().count() for id in c} 
    return sorted(map.keys(), key=lambda x: map[x], reverse=True)

def favorite_products(request):
    user = request.user
    products = Product.objects.filter(id__in=Favorite.objects.filter(user=user) \
        .values_list('product_id', flat=True))
    return render(request, 'oscar/catalogue/favorites.html', {'favorite_products': products})

def recommendation_generator(target, products, recommended_products):
    for id in target:
        recommended = products.filter(Q(categories__id=id) | Q(parent__categories__id=id)). \
            exclude(id__in=[x.id for x in recommended_products])
        try:
            if len(recommended_products) < 5:
                random_index = random.randint(0, recommended.count() - 1)
                recommended_products.append(recommended[random_index])
        except Exception as e:
            print(e)
            pass
        if len(recommended_products) == 5:
            return recommended_products
    return recommendation_generator(target, products, recommended_products)

# Import catalogue and category view from search app
CatalogueView = get_class("search.views", "CatalogueView")
ProductCategoryView = get_class("search.views", "ProductCategoryView")
