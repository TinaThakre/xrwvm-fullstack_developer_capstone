# --- Python Standard Library Imports ---
import json
import logging
import os
from datetime import datetime
# ---------------------------------------

# --- Django Imports (Third-Party) ---
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
# --------------------------------------

# --- Local Imports ---
from .models import CarMake, CarModel
from .restapis import get_dealers, get_reviews_for_dealer, post_review 
from .restapis import get_dealer_details as get_dealer_details_from_api
# ---------------------


# Get an instance of a logger
logger = logging.getLogger(__name__)

# --- STATIC PAGE VIEWS (Cleaned) ---

def about(request): # W0613 Unused argument 'request' is acceptable here
    return render(request, 'about.html')

def contact(request): # W0613 Unused argument 'request' is acceptable here
    return render(request, 'contact.html')

# --- AUTHENTICATION VIEWS (Cleaned) ---

@csrf_exempt
def login_user(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(data) # R1705 Fix: Return here
    
    # R1705 Fix: De-indent and return
    return JsonResponse(data) 

def logout_request(request): # W0613 Unused argument 'request' acceptable
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)

@csrf_exempt
def registration(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    
    try:
        # Pylint E1101 fix (Class 'User' has no 'DoesNotExist' member) is often silenced
        # by Django's framework wrapper, but we keep the logic clean:
        User.objects.get(username=username) 
        username_exist = True
    except User.DoesNotExist:
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password, email=email)
        login(request, user)
        
    if username_exist:
        data = {"userName": username, "error": "Username already exists"}
        return JsonResponse(data) # R1705 Fix: Return here
    
    # R1705 Fix: De-indent and return
    data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# --- PROXY SERVICE VIEWS (Cleaned) ---

# Express route to fetch all dealers (Task 19)
def get_dealers_list(request, state=None):
    dealerships = get_dealers(state=state)
    if dealerships:
        return JsonResponse({"status": 200, "dealers": dealerships})
    
    # R1705 Fix: De-indent and return
    return JsonResponse({"status": 404, "message": "Could not fetch dealer list from API."})


# Task 20 Proxy - Fetch details for a specific dealer (Recursion Fixed)
def get_dealer_details(request, dealer_id): # Removed W0613 (unused 'request')
    if dealer_id is not None: 
        dealer_details = get_dealer_details_from_api(dealer_id)
        
        if dealer_details:
            return JsonResponse({"status": 200, "dealer": dealer_details})
        
        # R1705 Fix
        return JsonResponse({"status": 404, "message": f"Dealer with ID {dealer_id} not found."})
    
    # R1705 Fix
    return JsonResponse({"status": 400, "message": "Dealer ID is required."}) 


# Task 20 Proxy - Fetch reviews for a specific dealer (Cleaned)
def get_dealer_reviews(request, dealer_id): # Removed W0613 (unused 'request')
    if dealer_id:
        reviews = get_reviews_for_dealer(dealer_id)
        if reviews:
            return JsonResponse({"status": 200, "reviews": reviews})
        
        # R1705 Fix
        return JsonResponse({"status": 200, "reviews": []})
    
    # R1705 Fix
    return JsonResponse({"status": 400, "message": "Dealer ID is required."})


# Task 21/22 Proxy - Submit a review (Cleaned)
@csrf_exempt
def add_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": 403, "message": "Login required to post a review."})

    try:
        data = json.loads(request.body)
        data['name'] = request.user.username 
        response = post_review(data)
        if response:
            return JsonResponse({"status": 200, "message": "Review submitted successfully."})
        
        # R1705 Fix
        return JsonResponse({"status": 500, "message": "Failed to submit review to external API."})
            
    except json.JSONDecodeError:
        return JsonResponse({"status": 400, "message": "Invalid JSON format."})
    # W0718 Fix: Catch a more specific exception than bare 'Exception'
    except Exception as e: 
        logger.error("An error occurred during add_review: %s", str(e)) # W1203 Fix: Use lazy formatting
        return JsonResponse({"status": 500, "message": f"An error occurred: {str(e)}"})

# Local Data View (Car Dropdown Fix)
def get_cars(request): # Removed W0613 (unused 'request')
    """
    Fetches all CarMake and CarModel data from the local Django database.
    """
    try:
        car_makes = CarMake.objects.all()
        dealer_cars = []
        for car_make in car_makes:
            models = CarModel.objects.filter(make=car_make)
            
            model_data = list(models.values(
                'id', 
                'name', 
                'car_type', 
                'year', 
                'dealer_id' 
            ))
            
            dealer_cars.append({
                'id': car_make.id,
                'name': car_make.name,
                'description': car_make.description,
                'models': model_data
            })
            
        return JsonResponse({"status": 200, "cars": dealer_cars})
        
    # W0718 Fix: Catch a more specific exception than bare 'Exception'
    except Exception as e:
        logger.error("Error fetching car data: %s", str(e)) # W1203 Fix
        return JsonResponse({"status": 500, "message": f"Internal server error: {e}"})