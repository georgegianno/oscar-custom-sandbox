# pylint: disable=attribute-defined-outside-init
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, DetailView, FormView, ListView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin
from django_tables2 import SingleTableView

from oscar.core.compat import get_user_model
from oscar.core.loading import get_class, get_classes, get_model
from oscar.views.generic import BulkEditMixin
from oscar.apps.order.models import Guest
from itertools import chain
from operator import attrgetter
from django.db.models import Count, When, Case, Value, IntegerField, Min
from django.core.paginator import Paginator


UserSearchForm, ProductAlertSearchForm, ProductAlertUpdateForm = get_classes(
    "dashboard.users.forms",
    ("UserSearchForm", "ProductAlertSearchForm", "ProductAlertUpdateForm"),
)
PasswordResetForm = get_class("customer.forms", "PasswordResetForm")
UserTable = get_class("dashboard.users.tables", "UserTable")
ProductAlert = get_model("customer", "ProductAlert")
User = get_user_model()


class IndexView(BulkEditMixin, FormMixin, SingleTableView):
    template_name = "oscar/dashboard/users/index.html"
    model = User
    actions = (
        "make_active",
        "make_inactive",
    )
    form_class = UserSearchForm
    table_class = UserTable
    context_table_name = "users"
    desc_template = _("%(main_filter)s %(email_filter)s %(name_filter)s")
    description = ""
    
    def dispatch(self, request, *args, **kwargs):
        self.guest_context = None
        self.all_context = None
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)
        if 'search' in request.GET:
            if 'users' in request.GET:
                if request.GET['users'] == 'Guests':
                    self.guest_context = self.get_queryset()
                elif request.GET['users'] == 'All':
                    self.all_context = self.get_queryset()
        return super().dispatch(request, *args, **kwargs)

    def get_table_pagination(self, table):
        return dict(per_page=settings.OSCAR_DASHBOARD_ITEMS_PER_PAGE)

    def get_form_kwargs(self):
        """
        Only bind search form if it was submitted.
        """
        kwargs = super().get_form_kwargs()

        if "search" in self.request.GET:
            kwargs.update(
                {
                    "data": self.request.GET,
                }
            )

        return kwargs

    def get_queryset(self):
        if self.request.GET.get('users', None) == 'Guests':
            queryset = Guest.objects.annotate(count_orders=Count('orders')).order_by('-count_orders'). \
                annotate(date_joined=Min('orders__date_placed'))
        elif self.request.GET.get('users', None) == 'All':
            user_emails = User.objects.values('email')
            guest_orders_only = Guest.objects.annotate(count_orders=Count('orders')).exclude(email__in=user_emails). \
                annotate(date_joined=Min('orders__date_placed'))
            guest_orders_from_users = User.objects.filter(email__in=Guest.objects.values('email')).values_list('email', flat=True)
            guest_order_counts = Guest.objects.filter(email__in=guest_orders_from_users.values('email')). \
                annotate(order_count=Count('orders')).values('email', 'order_count')
            guest_order_count_dict = {guest['email']: guest['order_count'] for guest in guest_order_counts}
            q3 = User.objects.annotate(
                count_orders=Case(
                    *[
                        When(email=email, then=Value(order_count)+Count('orders'))
                        for email, order_count in guest_order_count_dict.items()
                    ],
                    default=Count('orders'),
                    output_field=IntegerField()
                )
            )
            queryset = sorted(list(chain(guest_orders_only, q3)), key=attrgetter('count_orders'), reverse=True)
        else:
            queryset = self.model.objects.all().order_by('-date_joined')
        return self.apply_search(queryset)

    def apply_search(self, queryset):
        # Set initial queryset description, used for template context
        self.desc_ctx = {
            "main_filter": _("All users"),
            "email_filter": "",
            "name_filter": "",
        }
        if self.form.is_valid():
            return self.apply_search_filters(queryset, self.form.cleaned_data)
        else:
            return queryset

    def apply_search_filters(self, queryset, data):
        """
        Function is split out to allow customisation with little boilerplate.
        """ 
        if data['email']:
            email = data['email']
            if  self.request.GET.get('users', None) == 'All':
                q1=Guest.objects.filter(email__istartswith=email).annotate(count=Count('orders'))
                q2=User.objects.filter(email__istartswith=email).annotate(count=Count('orders'))
                queryset = [obj for obj in queryset if obj in q1 or obj in q2]
            else:
                queryset = queryset.filter(email__istartswith=email)
            self.desc_ctx['email_filter'] \
                = _(" with email matching '%s'") % email
        if data['name']:
            # If the value is two words, then assume they are first name and
            # last name
            if self.request.GET.get('users', None) == 'Guests':
                condition = Q(name__icontains=data['name'])
                queryset = queryset.filter(condition).distinct()
            elif self.request.GET.get('users', None) == 'All':
                condition1 = Q(name__icontains=data['name'])
                condition2 = Q(first_name__icontains=data['name']) | Q(last_name__icontains=data['name'])
                q1=Guest.objects.filter(condition1).annotate(count=Count('orders'))
                q2=User.objects.filter(condition2).annotate(count=Count('orders'))
                queryset = [obj for obj in queryset if obj in q1 or obj in q2]
            else:
                parts = data['name'].split()
                # always true filter
                condition = Q()
                for part in parts:
                    condition &= Q(first_name__icontains=part) | Q(last_name__icontains=part)
                queryset = queryset.filter(condition).distinct()
            self.desc_ctx['name_filter'] = _(" with name matching '%s'") % data['name']
        return queryset

    def get_table(self, **kwargs):
        table = super().get_table(**kwargs)
        table.caption = self.desc_template % self.desc_ctx
        return table

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        if self.guest_context:
            context['guest_context'] =  self.guest_context
        if self.all_context:
            context['all_context'] =  self.all_context
        if self.guest_context or self.all_context:
            paginator = Paginator(self.get_queryset(), 25)
            page_number = self.request.GET.get("page")
            page_obj = paginator.get_page(page_number)
            context['page_obj']= page_obj
            context['paginator'] = paginator
        return context

    def make_inactive(self, request, users):
        return self._change_users_active_status(users, False)

    def make_active(self, request, users):
        return self._change_users_active_status(users, True)

    def _change_users_active_status(self, users, value):
        for user in users:
            if not user.is_superuser:
                user.is_active = value
                user.save()
        messages.info(self.request, _("Users' status successfully changed"))
        return redirect("dashboard:users-index")


class UserDetailView(DetailView):
    template_name = "oscar/dashboard/users/detail.html"
    model = User
    context_object_name = "customer"

    def get_queryset(self):
        queryset = self.model.objects.prefetch_related(
            "orders__lines", "orders__surcharges"
        )
        return queryset


class PasswordResetView(SingleObjectMixin, FormView):
    form_class = PasswordResetForm
    http_method_names = ["post"]
    model = User

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["data"] = {"email": self.object.email}
        return kwargs

    def form_valid(self, form):
        # The PasswordResetForm's save method sends the reset email
        form.save(request=self.request)
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, _("A password reset email has been sent"))
        return reverse("dashboard:user-detail", kwargs={"pk": self.object.id})


class ProductAlertListView(ListView):
    model = ProductAlert
    form_class = ProductAlertSearchForm
    context_object_name = "alerts"
    template_name = "oscar/dashboard/users/alerts/list.html"
    paginate_by = settings.OSCAR_DASHBOARD_ITEMS_PER_PAGE
    base_description = _("All Alerts")
    description = ""

    def get_queryset(self):
        queryset = self.model.objects.all().order_by("-date_created")
        self.description = self.base_description

        self.form = self.form_class(self.request.GET)
        if not self.form.is_valid():
            return queryset

        data = self.form.cleaned_data

        if data["status"]:
            queryset = queryset.filter(status=data["status"])
            self.description += _(" with status matching '%s'") % data["status"]

        if data["name"]:
            # If the value is two words, then assume they are first name and
            # last name
            parts = data["name"].split()
            if len(parts) >= 2:
                queryset = queryset.filter(
                    user__first_name__istartswith=parts[0],
                    user__last_name__istartswith=parts[1],
                ).distinct()
            else:
                queryset = queryset.filter(
                    Q(user__first_name__istartswith=parts[0])
                    | Q(user__last_name__istartswith=parts[-1])
                ).distinct()
            self.description += _(" with customer name matching '%s'") % data["name"]

        if data["email"]:
            queryset = queryset.filter(
                Q(user__email__icontains=data["email"])
                | Q(email__icontains=data["email"])
            )
            self.description += _(" with customer email matching '%s'") % data["email"]

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form
        context["queryset_description"] = self.description
        return context


class ProductAlertUpdateView(UpdateView):
    template_name = "oscar/dashboard/users/alerts/update.html"
    model = ProductAlert
    form_class = ProductAlertUpdateForm
    context_object_name = "alert"

    def get_success_url(self):
        messages.success(self.request, _("Product alert saved"))
        return reverse("dashboard:user-alert-list")


class ProductAlertDeleteView(DeleteView):
    model = ProductAlert
    template_name = "oscar/dashboard/users/alerts/delete.html"
    context_object_name = "alert"

    def get_success_url(self):
        messages.warning(self.request, _("Product alert deleted"))
        return reverse("dashboard:user-alert-list")
