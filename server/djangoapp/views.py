# --- Python Standard Library Imports ---
import json
import logging
import os
# ---------------------------------------

# --- Django Imports (Third-Party) ---
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.db.models import ObjectDoesNotExist # E1101 Fix
# --------------------------------------

# --- Local Imports ---
from .models import CarMake, CarModel
from .restapis import get_dealers, get_reviews_for_dealer, post_review 
from .restapis import get_dealer_details as get_dealer_details_from_api
# ---------------------

logger = logging.getLogger(__name__)

# --- STATIC PAGE VIEWS (Cleaned) ---

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

# --- AUTHENTICATION VIEWS ---

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
        return JsonResponse(data)
    
    return JsonResponse(data) 

def logout_request(request):
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
        User.objects.get(username=username) 
        username_exist = True
    except ObjectDoesNotExist:
        user = User.objects.create_user(
            username=username, first_name=first_name, 
            last_name=last_name, password=password, 
            email=email
        )
        login(request, user)
        
    if username_exist:
        data = {"userName": username, "error": "Username already exists"}
        return JsonResponse(data)
    
    data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# --- PROXY SERVICE VIEWS ---

def get_dealers_list(request, state=None):
    dealerships = get_dealers(state=state)
    if dealerships:
        return JsonResponse({"status": 200, "dealers": dealerships})
    
    return JsonResponse({"status": 404, "message": "Could not fetch dealer list from API."})


def get_dealer_details(request, dealer_id):
    if dealer_id is not None:
        dealer_details = get_dealer_details_from_api(dealer_id)
        
        if dealer_details:
            return JsonResponse({"status": 200, "dealer": dealer_details})
        
        return JsonResponse({"status": 404, "message": f"Dealer with ID {dealer_id} not found."})
    
    return JsonResponse({"status": 400, "message": "Dealer ID is required."}) 


def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        reviews = get_reviews_for_dealer(dealer_id)
        if reviews:
            return JsonResponse({"status": 200, "reviews": reviews})
        
        return JsonResponse({"status": 200, "reviews": []})
    
    return JsonResponse({"status": 400, "message": "Dealer ID is required."})


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
        
        return JsonResponse({"status": 500, "message": "Failed to submit review to external API."})
            
    except json.JSONDecodeError:
        return JsonResponse({"status": 400, "message": "Invalid JSON format."})
    except Exception as e:
        logger.error("An error occurred during add_review: %s", str(e))
        return JsonResponse({"status": 500, "message": f"An error occurred: {str(e)}"})

# Local Data View (Car Dropdown Fix)
def get_cars(request):
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
        
    except Exception as e:
        logger.error("Error fetching car data: %s", str(e))
        return JsonResponse({"status": 500, "message": f"Internal server error: {e}"})
        
