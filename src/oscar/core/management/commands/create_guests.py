from django.core.management.base import BaseCommand
from oscar.core.loading import get_model
from oscar.core.compat import get_user_model
from oscar.apps.order.models import Guest

Order = get_model('order', 'Order')
User = get_user_model()

class Command(BaseCommand):
    help = (
        'Importing the guests so far as objects'
    )
    def handle(self, *args, **options):
        Guest.objects.all().delete()
        orders = Order.objects.filter(status="Completed").filter(user=None)
        guest_emails = set(orders.values_list('guest_email', flat=True).distinct())
        for email in guest_emails:
                try:
                    if not Guest.objects.filter(email=email):
                        order = orders.filter(guest_email=email).last()
                        name = order.shipping_address.first_name + ' ' + order.shipping_address.last_name
                        email = email
                        guest = Guest.objects.create(name=name, email=email)
                        guest_orders = orders.filter(guest_email=email)
                        for order in guest_orders:
                            guest.orders.add(order)
                        print(guest)
                except Exception as error:
                    print(error)