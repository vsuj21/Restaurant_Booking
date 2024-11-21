from django.urls import path
from .views import *
from .views import owner_dashboard, customer_dashboard


urlpatterns = [
    path('owner-dashboard/', owner_dashboard, name='owner-dashboard'),
    path('register-restaurant/', RegisterRestaurantView.as_view(), name='register-restaurant'),
    path('add-slots/', AddSlotsView.as_view(), name='add-slots'),

    path('customer-dashboard/', customer_dashboard, name='customer-dashboard'),

    
    path('base/', Base.as_view() , name='base'),
    path('success/', success , name='success'),

]
