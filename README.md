# Restaurant_Booking

Restaurant Booking System
A web application for restaurant management and table booking. This project allows restaurant owners to manage their restaurants and time slots, while customers can search for restaurants and book tables easily. Built using Django and Bootstrap.

**Features**
Restaurant Owner
Register a restaurant with details like name, city, area, and cuisine.
Add time slots with a specified capacity for table bookings.

**Customer**
Search for restaurants based on attributes like name, city, area, cuisine, cost for two, veg/non-veg, etc.
View detailed restaurant information.
Book tables for specific time slots with real-time availability validation.
Concurrency-safe table booking.

**Technical Highlights**
Django Framework for backend logic and database operations.
PostgreSQL (or SQLite by default) for data storage.
Bootstrap for responsive and user-friendly UI.
Concurrency handling during bookings using Django transactions.
Login required for customer actions; no authentication for restaurant owners.

**Models: Define the database schema.
Views: Handle logic, process data, and return a response (HTML, JSON, etc.).
Templates: Define the front-end (HTML) structure.**

In our project the restaurant model database schema is like this:

Restaurant is the parent model.
TimeSlot is linked to Restaurant (1 restaurant can have many slots).
Booking is linked to both Restaurant and TimeSlot (each booking is tied to a restaurant and a specific time slot).

models.ForeignKey
Purpose: Creates a relationship between two models.

Example in TimeSlot:
restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
ForeignKey means each TimeSlot is linked to one Restaurant.
This creates a column in the TimeSlot table (restaurant_id) to store the id of the related restaurant.
on_delete=models.CASCADE
Purpose: Defines what happens to related objects if the parent object is deleted.
Options:
CASCADE: Delete the related objects as well. 
Example: If a restaurant is deleted, all its time slots and bookings will also be deleted

Views
In Django, views handle the logic behind what happens when a user makes a request. They are responsible for interacting with models and returning a response (HTML, JSON, etc.).
In this project, we’re working with APIs, so we’ll define views using Django REST Framework (DRF), which makes creating APIs easier.

**RegisterRestaurantView**
Method: POST
Purpose: Allows a restaurant owner to register a new restaurant.
Logic: We accept the data from the request, validate it using the RestaurantSerializer, and save it to the database if valid.

**AddSlotView**
Method: POST
Purpose: Allows a restaurant owner to add available time slots for bookings.
Logic: Similar to the restaurant registration, the time slots are validated and stored in the database.

**SearchRestaurant**
Method: GET
Purpose: Allows customers to search for restaurants based on various filters (name, city, cuisine, etc.).
Logic: We check for query parameters and filter the Restaurant model accordingly, then return the filtered list as a JSON response.

**BookTable**
Method: POST
Purpose: Allows customers to book a table at a restaurant.
Logic: The user provides the restaurant, time slot, and number of people. We check if the slot is available. If it is, we create a booking.
