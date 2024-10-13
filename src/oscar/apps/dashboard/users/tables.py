from django.utils.translation import gettext_lazy as _
from django_tables2 import A, Column, LinkColumn, TemplateColumn

from oscar.core.loading import get_class

DashboardTable = get_class("dashboard.tables", "DashboardTable")


from django.utils.translation import gettext_lazy as _

from django_tables2 import A, Column, LinkColumn, TemplateColumn

from oscar.core.compat import get_user_model
from oscar.core.loading import get_class, get_model
from django.db.models import F, Count, Sum, Q, Case, When, FloatField
from django.conf import settings


User = get_user_model()
DashboardTable = get_class('dashboard.tables', 'DashboardTable')

class UserTable(DashboardTable):
    check = TemplateColumn(
        template_name='oscar/dashboard/users/user_row_checkbox.html',
        verbose_name=' ', orderable=False)
    email = LinkColumn('dashboard:user-detail', args=[A('id')],
                       accessor='email')
    name = Column(accessor='get_full_name',
                  order_by=('last_name', 'first_name'))
    active = Column(accessor='is_active')
    staff = Column(accessor='is_staff')
    date_registered = Column(accessor='date_joined')
    num_orders = Column(accessor='orders.count', verbose_name=_('Number of Orders'))
    orders_total_value = Column(accessor='pk')
    
    actions = TemplateColumn(
        template_name='oscar/dashboard/users/user_row_actions.html',
        verbose_name=' ')

    icon = "group"
    users_count = User.objects.all().count()
    
    
    class Meta(DashboardTable.Meta):
        template = 'oscar/dashboard/users/table.html'

    def order_num_orders(self, queryset, is_descending):
        queryset = queryset.annotate(count = Count('orders'))
        queryset = queryset.order_by('-count') if is_descending else queryset.order_by('count')
        return queryset, True
    
    def render_orders_total_value(self, value, record):
        total = record.orders.filter(status='Complete').aggregate(Sum('total_incl_tax')).get('total_incl_tax__sum')
        if settings.OSCAR_DEFAULT_CURRENCY == 'GBP':
            coin =  '£'
        else: 
            coin = '€'
        if total:
            return coin + str(float(total))
        else:
            return coin + 0  
    
    def order_orders_total_value(self, queryset, is_descending):
        queryset = queryset.annotate(
            orders_sum=Sum(
                Case(
                    When(orders__status='Complete', then=F('orders__total_incl_tax')),
                    default=0, 
                    output_field=FloatField()
                )
            )
        )
        queryset = queryset.order_by('-orders_sum') if is_descending else queryset.order_by('orders_sum')
        return queryset, True
