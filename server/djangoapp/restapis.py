import os

import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("backend_url", default="http://localhost:3030")
SENTIMENT_ANALYZER_URL = os.getenv(
    "sentiment_analyzer_url",
    default="http://localhost:5002",
)


def get_request(endpoint, **kwargs):
    """
    Perform a GET request to the backend service.

    Returns parsed JSON on success, or None on error.
    """
    request_url = f"{BACKEND_URL}{endpoint}"
    print(f"GET from {request_url} with params: {kwargs}")

    try:
        response = requests.get(request_url, params=kwargs, timeout=10)
    except requests.exceptions.RequestException as exc:
        print(f"Network error occurred: {exc}")
        return None

    if response.status_code == 200:
        return response.json()

    print(f"HTTP Status {response.status_code} for URL: {request_url}")
    return None


# -------------------------------------------------------------
# REQUIRED PROXY FUNCTIONS FOR DEALER/REVIEW DATA
# -------------------------------------------------------------


def get_dealers(state=None):
    """
    Retrieve list of dealers.

    If state is provided, fetch by state; otherwise fetch all.
    """
    endpoint = "/fetchDealers"
    if state:
        endpoint = f"/fetchDealers/{state}"

    json_result = get_request(endpoint)
    if json_result and "dealers" in json_result:
        return json_result["dealers"]

    return json_result


def get_dealer_details(dealer_id):
    """
    Retrieve details for a specific dealer.
    """
    endpoint = f"/fetchDealer/{dealer_id}"
    json_result = get_request(endpoint)
    if json_result:
        return json_result
    return None


def get_reviews_for_dealer(dealer_id):
    """
    Retrieve reviews for a specific dealer.
    """
    endpoint = f"/fetchReviews/dealer/{dealer_id}"
    json_result = get_request(endpoint)
    if json_result:
        return json_result
    return None


# -------------------------------------------------------------
# REQUIRED PROXY FUNCTIONS FOR SENTIMENT & POSTING
# -------------------------------------------------------------


def analyze_review_sentiments(text):
    """
    Analyze sentiment for the given text using microservice.
    """
    request_url = f"{SENTIMENT_ANALYZER_URL}/analyze/{text}"
    try:
        response = requests.get(request_url, timeout=10)
    except requests.exceptions.RequestException as exc:
        print(f"Error connecting to sentiment API: {exc}")
        return {"sentiment": "N/A"}

    if response.status_code == 200:
        return response.json()

    print(f"Sentiment API failed with status: {response.status_code}")
    return {"sentiment": "N/A"}


def post_review(data_dict):
    """
    Post a review to the backend microservice.
    """
    request_url = f"{BACKEND_URL}/insert_review"
    print(f"POST to {request_url} with data: {data_dict}")
    try:
        response = requests.post(request_url, json=data_dict, timeout=10)
    except requests.exceptions.RequestException as exc:
        print(f"Network error during POST: {exc}")
        return None

    if response.status_code in (200, 201):
        return response.json()

    print(f"Post review failed with status: {response.status_code}")
    return None
