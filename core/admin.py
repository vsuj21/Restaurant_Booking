from django.contrib import admin
from .models import Restaurant, TimeSlot, Booking

admin.site.register(Restaurant)
admin.site.register(TimeSlot)
admin.site.register(Booking)
