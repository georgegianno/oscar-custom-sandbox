from django.urls import re_path
from .views import PromoListView, PromoCreateView, PromoUpdateView, PromoDeleteView

app_name = 'promo-dashboard'

urlpatterns = [
    re_path(r'^promos/$', PromoListView.as_view(), name="dashboard-promo-list"),
    re_path(r'^promos/create/$', PromoCreateView.as_view(), name="dashboard-promo-create"),
    re_path(r'^promos/(?P<pk>\d+)/$', PromoUpdateView.as_view(), name="dashboard-promo-update"),
    re_path(r'^promos/delete/(?P<pk>\d+)/$', PromoDeleteView.as_view(), name="dashboard-promo-delete"),
]
