from django.shortcuts import render, redirect
from oscar.apps.promo.models import Promo
from .forms import PromoForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView


class PromoListView(ListView):
    queryset = Promo.objects.order_by('-pk')
    template_name = 'dashboard/promo/promo_list.html'
    title = 'Promo'


class PromoCreateView(CreateView):
    queryset = Promo.objects.order_by('-pk')
    form_class = PromoForm
    template_name = 'dashboard/promo/promo_form.html'
    success_url = reverse_lazy('promo-dashboard:dashboard-promo-list')
    title = 'Create Promo'


class PromoUpdateView(UpdateView):
    queryset = Promo.objects.order_by('-pk')
    form_class = PromoForm
    template_name = 'dashboard/promo/promo_form.html'
    success_url = reverse_lazy('promo-dashboard:dashboard-promo-list')
    title = 'Update Promo'


class PromoDeleteView(DeleteView):
    queryset = Promo.objects.order_by('-pk')
    template_name = 'dashboard/promo/promo_delete.html'
    success_url = reverse_lazy('promo-dashboard:dashboard-promo-list')
    title = 'Delete Promo'