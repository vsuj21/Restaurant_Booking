from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import Restaurant, TimeSlot, Booking
from .serializers import RestaurantSerializer, TimeSlotSerializer, BookingSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

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
        if restaurants.count() == 0:
            return Response({"message": "No restaurants found. Please register a restaurant first."}, status=status.HTTP_404_NOT_FOUND)
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

from django.shortcuts import render
from .models import Restaurant

def search_restaurants(request):
    query = request.GET.get('query', '')
    cuisine = request.GET.get('cuisine', '')
    cost_for_two_min = request.GET.get('cost_for_two_min', None)

    restaurants = Restaurant.objects.all()
    

    if query:
        restaurants = restaurants.filter(
            Q(name__icontains=query) | 
            Q(city__icontains=query) | 
            Q(area__icontains=query) | 
            Q(cuisine__icontains=query)
        )
    if cuisine:
        restaurants = restaurants.filter(cuisine__icontains=cuisine)
    if cost_for_two_min:
        restaurants = restaurants.filter(cost_for_two__gte=cost_for_two_min)

    return render(request, 'search_result.html', {'restaurants': restaurants})


M = 7

def book_table(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Get available time slots for the restaurant
    current_time = timezone.now()
    available_slots = TimeSlot.objects.filter(
        restaurant=restaurant,
        start_time__gte=current_time,
        start_time__lte=current_time + timedelta(days=M)
    )

    if request.method == 'POST':
        # Handle booking
        people_count = int(request.POST['people_count'])
        time_slot_id = request.POST['time_slot']
        try:
            with transaction.atomic():
                # Lock the selected time slot for update
                selected_slot = TimeSlot.objects.select_for_update().get(id=time_slot_id, restaurant=restaurant)

                # Validate availability of slot
                if selected_slot.capacity < people_count:
                    return render(request, 'booking_success.html', {
                        'message': 'Not enough capacity for the selected number of people.'
                    })

                # Create the booking
                booking = Booking(
                    customer_name=request.user.username,  # customer is logged in
                    customer_email=request.user.email,
                    time_slot=selected_slot,
                    people_count=people_count
                )
                booking.save()

                # Reduce the capacity of the time slot
                selected_slot.capacity -= people_count
                selected_slot.save()

            return redirect('booking-success')  # Redirect to a success page after booking

        except TimeSlot.DoesNotExist:
            return render(request, 'booking_success.html', {
                'message': 'The selected time slot no longer exists.'
            })

        except Exception as e:
            return render(request, 'booking_success.html', {
                'message': f"An error occurred: {str(e)}"
            })

    return render(request, 'book_table.html', {'restaurant': restaurant, 'time_slots': available_slots})

def home(request):
    return render(request, 'home.html')

def owner_dashboard(request):
    return render(request, 'owner_dashboard.html')

def customer_dashboard(request):
    return render(request, 'customer_dashboard.html')

def success(request):
    return render(request, 'success.html', {"message": "Registration Successful!"})

def booking_success(request):
    return render(request, 'booking_success.html', {"message": "Booking Successful!"})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('base')  # Redirect to the home page or another page
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')


def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, "Account created successfully. You can now log in!")
            return redirect('login')  # Redirect to the login page
    return render(request, 'signup.html')


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('base')