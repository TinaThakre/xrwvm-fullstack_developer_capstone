# --- Python Standard Library Imports ---
import json
import logging

# --- Django Imports (Third-Party) ---
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# --- Local Imports ---
from .models import CarMake, CarModel
from .restapis import (
    get_dealer_details as get_dealer_details_from_api,
)
from .restapis import (
    get_dealers,
    get_reviews_for_dealer,
    post_review,
)

logger = logging.getLogger(__name__)


# --- STATIC PAGE VIEWS ---


def about(request):
    """Render static About page."""
    return render(request, "about.html")


def contact(request):
    """Render static Contact page."""
    return render(request, "contact.html")


# --- AUTHENTICATION VIEWS ---


@csrf_exempt
def login_user(request):
    """
    Authenticate a user and start a session.

    Expected JSON body:
    {
        "userName": "<username>",
        "password": "<password>"
    }
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "Error", "message": "Invalid JSON payload."},
            status=400,
        )

    username = data.get("userName", "")
    password = data.get("password", "")

    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse(
            {
                "userName": username,
                "status": "Authenticated",
            },
            status=200,
        )

    return JsonResponse(
        {
            "userName": username,
            "status": "Invalid credentials",
        },
        status=401,
    )


def logout_request(request):
    """Log out the current user."""
    logout(request)
    return JsonResponse({"userName": "", "status": "Logged out"}, status=200)


@csrf_exempt
def registration(request):
    """
    Register a new user.

    Expected JSON body:
    {
        "userName": "<username>",
        "password": "<password>",
        "firstName": "<first_name>",
        "lastName": "<last_name>",
        "email": "<email>"
    }
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "Error", "message": "Invalid JSON payload."},
            status=400,
        )

    username = data.get("userName", "")
    password = data.get("password", "")
    first_name = data.get("firstName", "")
    last_name = data.get("lastName", "")
    email = data.get("email", "")

    if not username or not password:
        return JsonResponse(
            {
                "status": "Error",
                "message": "Username and password are required.",
            },
            status=400,
        )

    try:
        # Check if user already exists; if found, raise a conflict response.
        User.objects.get(username=username)
        return JsonResponse(
            {
                "userName": username,
                "error": "Username already exists",
            },
            status=409,
        )
    except ObjectDoesNotExist:
        # Safe to create user
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email,
        )
        login(request, user)
        return JsonResponse(
            {
                "userName": username,
                "status": "Authenticated",
            },
            status=201,
        )


# --- PROXY SERVICE VIEWS ---


def get_dealers_list(request, state=None):
    """
    Return the list of dealers, optionally filtered by state.

    URL patterns:
    - /get_dealers
    - /get_dealers/<state>
    """
    dealerships = get_dealers(state=state)
    if dealerships:
        return JsonResponse(
            {
                "status": 200,
                "dealers": dealerships,
            },
            status=200,
        )

    return JsonResponse(
        {
            "status": 404,
            "message": "Could not fetch dealer list from API.",
        },
        status=404,
    )


def get_dealer_details(request, dealer_id):
    """
    Return details for a given dealer.

    URL pattern:
    - /dealer/<dealer_id>
    """
    if dealer_id is None:
        return JsonResponse(
            {
                "status": 400,
                "message": "Dealer ID is required.",
            },
            status=400,
        )

    dealer_details = get_dealer_details_from_api(dealer_id)
    if dealer_details:
        return JsonResponse(
            {
                "status": 200,
                "dealer": dealer_details,
            },
            status=200,
        )

    return JsonResponse(
        {
            "status": 404,
            "message": f"Dealer with ID {dealer_id} not found.",
        },
        status=404,
    )


def get_dealer_reviews(request, dealer_id):
    """
    Return reviews for a given dealer.

    URL pattern:
    - /reviews/dealer/<dealer_id>
    """
    if not dealer_id:
        return JsonResponse(
            {
                "status": 400,
                "message": "Dealer ID is required.",
            },
            status=400,
        )

    reviews = get_reviews_for_dealer(dealer_id)
    if reviews:
        return JsonResponse(
            {
                "status": 200,
                "reviews": reviews,
            },
            status=200,
        )

    # Always return a list; empty if no reviews.
    return JsonResponse(
        {
            "status": 200,
            "reviews": [],
        },
        status=200,
    )


@csrf_exempt
def add_review(request):
    """
    Add a review for a dealer via backend microservice.

    Requires authentication.
    """
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "status": 403,
                "message": "Login required to post a review.",
            },
            status=403,
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"status": 400, "message": "Invalid JSON format."},
            status=400,
        )

    # Safely set reviewer's name from authenticated user.
    data["name"] = request.user.username

    try:
        response = post_review(data)
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Error posting review: %s", exc)
        return JsonResponse(
            {
                "status": 500,
                "message": "Failed to submit review to external API.",
            },
            status=500,
        )

    if response:
        return JsonResponse(
            {
                "status": 200,
                "message": "Review submitted successfully.",
            },
            status=200,
        )

    return JsonResponse(
        {
            "status": 500,
            "message": "Failed to submit review to external API.",
        },
        status=500,
    )


# --- LOCAL DATA VIEWS ---


def get_cars(request):
    """
    Fetch CarMake and CarModel data from the local database.

    Response:
    {
        "status": 200,
        "cars": [
            {
                "id": <make_id>,
                "name": "<make_name>",
                "description": "<make_description>",
                "models": [
                    {
                        "id": <model_id>,
                        "name": "<model_name>",
                        "car_type": "<type>",
                        "year": <year>,
                        "dealer_id": <dealer_id>
                    },
                    ...
                ]
            },
            ...
        ]
    }
    """
    try:
        car_makes = CarMake.objects.all()
        dealer_cars = []

        for car_make in car_makes:
            models = CarModel.objects.filter(make=car_make)
            model_data = list(
                models.values(
                    "id",
                    "name",
                    "car_type",
                    "year",
                    "dealer_id",
                ),
            )
            dealer_cars.append(
                {
                    "id": car_make.id,
                    "name": car_make.name,
                    "description": car_make.description,
                    "models": model_data,
                },
            )

        return JsonResponse(
            {
                "status": 200,
                "cars": dealer_cars,
            },
            status=200,
        )
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Error fetching car data: %s", exc)
        return JsonResponse(
            {
                "status": 500,
                "message": f"Internal server error: {exc}",
            },
            status=500,
        )
