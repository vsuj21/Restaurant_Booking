from django.urls import path
from .views import *
from .views import owner_dashboard, customer_dashboard


urlpatterns = [
    path('owner-dashboard/', owner_dashboard, name='owner-dashboard'),
    path('register-restaurant/', RegisterRestaurantView.as_view(), name='register-restaurant'),
    path('add-slots/', AddSlotsView.as_view(), name='add-slots'),

    path('customer-dashboard/', customer_dashboard, name='customer-dashboard'),
    path('search/', search_restaurants, name='search_restaurants'),
    path('restaurant/<int:restaurant_id>/book/', book_table, name='book_table'),

    path('', home, name='home'),
    path('base/', Base.as_view() , name='base'),
    path('success/', success , name='success'),
    path('booking-success/', booking_success , name='booking-success'),

    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),

]
