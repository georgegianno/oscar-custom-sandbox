import django
from django.apps import apps
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import views
from django.urls import include, path
from oscar.views import handler403, handler404, handler500
from oscar.apps.basket.views import set_line_quantity_ajax
from oscar.apps.catalogue.views import favorites_add_or_remove, favorite_products
from oscar.apps.dashboard.catalogue.views import save_category_order
from oscar.apps.dashboard.ranges.views import save_range_order
from oscar.apps.dashboard.users.export import export_customers
from oscar.apps.promo.utils import select_gift

# from oscar.apps.promo import promo_dashboard

from apps.sitemaps import base_sitemaps

admin.autodiscover()

urlpatterns = [
    # Include admin as convenience. It's unsupported and only included
    # for developers.
    path('admin/', admin.site.urls),

    # i18n URLS need to live outside of i18n_patterns scope of Oscar
    path('i18n/', include(django.conf.urls.i18n)),

    # include a basic sitemap
    path('sitemap.xml', views.index,
        {'sitemaps': base_sitemaps}),
    path('sitemap-<slug:section>.xml', views.sitemap,
        {'sitemaps': base_sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
    path('quantity/set/<int:id>/<int:quantity>/', set_line_quantity_ajax,
        name='set-quantity',
    ),
    path('favorites/<int:product_pk>/', favorites_add_or_remove,
        name='favorites',
    ),
    path('category-save-order/<int:pk>/', save_category_order,
            name='category-save-order',
        ),
    path('range-save-order/<int:pk>/', save_range_order,
            name='range-save-order',
        ),
    path('select2/', include('django_select2.urls')),
    path('select_gift/', select_gift, name='select_gift'),
]

# Prefix Oscar URLs with language codes
urlpatterns += i18n_patterns(
    path('', include(apps.get_app_config('oscar').urls[0])),
    path('dashboard/promo/', include('oscar.apps.promo.promo_dashboard.urls', namespace='promo-dashboard')),
    path('favorite-products/', favorite_products, name='favorite-products'),
    path('dashboard/users/export/<str:customers>', export_customers, name='export_customers'),
)

if settings.DEBUG:
    import debug_toolbar

    # Server statics and uploaded media
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Allow error pages to be tested
    urlpatterns += [
        path('403', handler403, {'exception': Exception()}),
        path('404', handler404, {'exception': Exception()}),
        path('500', handler500),
        path('__debug__/', include(debug_toolbar.urls)),
    ]
