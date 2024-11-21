from django.db import models
from django.contrib.auth.models import User



class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    cuisine = models.CharField(max_length=100)
    cost_for_two = models.DecimalField(max_digits=10, decimal_places=2)
    # rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    is_veg = models.BooleanField(default=True)
    # owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurants')

    def __str__(self):
        return f"{self.name} - {self.city}"


class TimeSlot(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='time_slots')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.restaurant.name} ({self.start_time} - {self.end_time})"




class Booking(models.Model):
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    people_count = models.IntegerField()
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking for {self.customer_name} on {self.time_slot.start_time}"