from django.urls import re_path
from oscar.core.application import OscarDashboardConfig

class PromoDashboardConfig(OscarDashboardConfig):
    name = 'oscar.apps.promo.promo_dashboard'
    label = 'promo_dashboard'
    namespace = 'promo-dashboard'
        
    # def get_urls(self):
    #     from .import views
    #     # self.promo_dashboard_view = views.promo_dashboard_view
    #     self.promo_list_view = views.PromoListView
    #     self.promo_create_view = views.PromoCreateView
    #     self.promo_update_view = views.PromoUpdateView
    #     self.promo_delete_view = views.PromoDeleteView
    #     urls = [
    #         # url(r'^$', self.promo_dashboard_view, name='promo'),
    #         re_path(r'^promos/$',
    #             self.promo_list_view.as_view(),
    #             name="dashboard-promo-list"),
    #         re_path(r'^promos/create/$',
    #             self.promo_create_view.as_view(),
    #             name="dashboard-promo-create"),
    #         re_path(r'^promos/(?P<pk>\d+)/$',
    #             self.promo_update_view.as_view(),
    #             name="dashboard-promo-update"),
    #         re_path(r'^promos/delete/(?P<pk>\d+)/$',
    #             self.promo_delete_view.as_view(),
    #             name="dashboard-promo-delete"),
    #     ] 
    #     return self.post_process_urls(urls)