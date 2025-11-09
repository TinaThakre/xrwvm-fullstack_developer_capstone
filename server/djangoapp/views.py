# Uncomment the required imports before adding the code

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import logout, login, authenticate 
from django.contrib import messages
from datetime import datetime
from .models import CarMake, CarModel # <--- CarMake/CarModel are needed for get_cars
from .restapis import get_dealers, get_reviews_for_dealer, post_review 
from .restapis import get_dealer_details as get_dealer_details_from_api # <-- Use alias for details proxy

# Utility imports
import logging
import json
from django.views.decorators.csrf import csrf_exempt


# Get an instance of a logger
logger = logging.getLogger(__name__)

# --- STATIC PAGE VIEWS (UNCHANGED) ---

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

# --- AUTHENTICATION VIEWS (UNCHANGED) ---

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
    except User.DoesNotExist:
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password, email=email)
        login(request, user)
        
    if username_exist:
        data = {"userName": username, "error": "Username already exists"}
    else:
        data = {"userName": username, "status": "Authenticated"}
        
    return JsonResponse(data)

# --- PROXY SERVICE VIEWS ---

# Express route to fetch all dealers (Task 19)
def get_dealers_list(request, state=None):
    dealerships = get_dealers(state=state)
    if dealerships:
        return JsonResponse({"status": 200, "dealers": dealerships})
    else:
        return JsonResponse({"status": 404, "message": "Could not fetch dealer list from API."})


# Task 20 Proxy - Fetch details for a specific dealer (FIXED RECURSION)
def get_dealer_details(request, dealer_id):
    if dealer_id:
        # CORRECT CALL: Uses the renamed proxy function to avoid calling itself
        dealer_details = get_dealer_details_from_api(dealer_id) 
        
        if dealer_details:
            # Note: React expects a key named 'dealer' here based on its fetch
            return JsonResponse({"status": 200, "dealer": dealer_details}) 
        else:
            return JsonResponse({"status": 404, "message": f"Dealer with ID {dealer_id} not found."})
    else:
        return JsonResponse({"status": 400, "message": "Dealer ID is required."})


# Task 20 Proxy - Fetch reviews for a specific dealer (Unchanged)
def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        reviews = get_reviews_for_dealer(dealer_id)
        if reviews:
            return JsonResponse({"status": 200, "reviews": reviews})
        else:
            return JsonResponse({"status": 200, "reviews": []})
    else:
        return JsonResponse({"status": 400, "message": "Dealer ID is required."})


# Task 21/22 Proxy - Submit a review (Unchanged)
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
        else:
            return JsonResponse({"status": 500, "message": "Failed to submit review to external API."})
            
    except json.JSONDecodeError:
        return JsonResponse({"status": 400, "message": "Invalid JSON format."})
    except Exception as e:
        return JsonResponse({"status": 500, "message": f"An error occurred: {str(e)}"})

# Local Data View (FIXED FOR CAR LIST)
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
        logger.error(f"Error fetching car data: {e}")
        return JsonResponse({"status": 500, "message": f"Internal server error: {e}"})