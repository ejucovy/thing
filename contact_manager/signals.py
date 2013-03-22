from django.dispatch import Signal

contact_confirmed = Signal(providing_args=['contact'])
