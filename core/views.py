from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import Restaurant, TimeSlot, Booking
from .serializers import RestaurantSerializer, TimeSlotSerializer, BookingSerializer
from django.shortcuts import render, redirect
from django.utils import timezone
from django.db import transaction
from datetime import timedelta


class Base(APIView):
    def get(self, request):
        return render(request, 'home.html')

# Register a new restaurant
class RegisterRestaurantView(APIView):
    def get(self, request):
        # if not request.user.is_authenticated:
        #     return redirect('login')  # Redirect to login if not authenticated
        return render(request, 'register_restaurant.html')
    
    def post(self, request):
        # Extracting data from the request
        name = request.data.get('name')
        city = request.data.get('city')
        area = request.data.get('area')

        # Check if a restaurant with the same name, city, and area exists
        existing_restaurant = Restaurant.objects.filter(name=name, city=city, area=area).exists()

        if existing_restaurant:
            return Response({"error": "Restaurant with the same name, city, and area already exists."}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        serializer = RestaurantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Restaurant Registered Successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Add slots for a restaurant
class AddSlotsView(APIView):
    def get(self, request):
        # Fetch all restaurants and pass them to the template
        restaurants = Restaurant.objects.all()
        return render(request, 'slot_dashboard.html', {'restaurants': restaurants})

    def post(self, request):
        # Extract data from the form
        restaurant_id = request.data.get('restaurant')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        capacity = request.data.get('capacity')

        # Convert `start_time` and `end_time` to datetime objects
        start_time = timezone.datetime.fromisoformat(start_time)
        end_time = timezone.datetime.fromisoformat(end_time)

        # 1. Validate slot duration (must be exactly 1 hour)
        if (end_time - start_time) != timedelta(hours=1):
            return Response(
                {"error": "The time slot must be exactly 1 hour long."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2. Restrict slots to `m` days in the future
        m = 7  # Adjust the value of `m` as needed
        future_limit = timezone.now() + timedelta(days=m)
        if start_time < timezone.now() or start_time > future_limit:
            return Response(
                {"error": f"Slots can only be added for the next {m} days."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3. Check if a conflicting slot already exists
        overlapping_slot = TimeSlot.objects.filter(
            restaurant_id=restaurant_id,
            start_time__lt=end_time,  # Overlaps if it starts before `end_time`
            end_time__gt=start_time,  # Overlaps if it ends after `start_time`
        ).exists()

        if overlapping_slot:
            return Response(
                {"error": "An overlapping time slot already exists for this restaurant."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 4. Save the time slot
        data = {
            "restaurant": restaurant_id,
            "start_time": start_time,
            "end_time": end_time,
            "capacity": capacity,
        }
        serializer = TimeSlotSerializer(data=data)

        if serializer.is_valid():
            # Transaction to maintain concurrency
            with transaction.atomic():
                serializer.save()
            return render(request, 'success.html', {"message": "Time Slot Added Successfully!"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.http import JsonResponse
from django.db.models import Q

def search_restaurant(request):
    # Get query parameters from the request
    name = request.GET.get('name', '').strip()
    city = request.GET.get('city', '').strip()
    area = request.GET.get('area', '').strip()
    cuisine = request.GET.get('cuisine', '').strip()
    max_cost = request.GET.get('cost', None)
    is_veg = request.GET.get('is_veg', None)

    # Build the query using Q objects for flexible filtering
    filters = Q()
    if name:
        filters &= Q(name__icontains=name)
    if city:
        filters &= Q(city__icontains=city)
    if area:
        filters &= Q(area__icontains=area)
    if cuisine:
        filters &= Q(cuisine__icontains=cuisine)
    if max_cost:
        filters &= Q(cost_for_two__lte=float(max_cost))
    if is_veg is not None:
        filters &= Q(is_veg=is_veg.lower() == 'true')  # Convert string to boolean

    # Query the database
    restaurants = Restaurant.objects.filter(filters)

    # Prepare the response data
    data = [
        {
            "id": restaurant.id,
            "name": restaurant.name,
            "city": restaurant.city,
            "area": restaurant.area,
            "cuisine": restaurant.cuisine,
            "cost_for_two": float(restaurant.cost_for_two),
            "is_veg": restaurant.is_veg,
        }
        for restaurant in restaurants
    ]

    return JsonResponse(data, safe=False)


# Book a table
class BookTableView(APIView):
    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            timeslot = TimeSlot.objects.get(id=request.data['timeslot'])
            if timeslot.capacity > 0:
                timeslot.capacity -= 1
                timeslot.save()
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"error": "Slot not available"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def owner_dashboard(request):
    return render(request, 'owner_dashboard.html')

def customer_dashboard(request):
    return render(request, 'customer_dashboard.html')

def success(request):
    return render(request, 'success.html', {"message": "Registration Successful!"})
