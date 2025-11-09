import os
import requests
from dotenv import load_dotenv
# import json # Removed unused import

load_dotenv()

backend_url = os.getenv(
    'backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="http://localhost:5002")

def get_request(endpoint, **kwargs):
    request_url = backend_url + endpoint
    print(f"GET from {request_url} with params: {kwargs}")
    
    try:
        # ADDED: timeout argument (W3101 Fix)
        response = requests.get(request_url, params=kwargs, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"HTTP Status {response.status_code} for URL: {request_url}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Network error occurred: {e}")
        return None

# -------------------------------------------------------------
# REQUIRED PROXY FUNCTIONS FOR DEALER/REVIEW DATA
# -------------------------------------------------------------

def get_dealers(state=None):
    endpoint = "/fetchDealers"
    if state:
        endpoint = f"/fetchDealers/{state}"
        
    json_result = get_request(endpoint)

    if json_result and 'dealers' in json_result:
        dealers = json_result['dealers']
        return dealers
    
    return json_result

def get_dealer_details(dealer_id): 
    endpoint = f"/fetchDealer/{dealer_id}"
    json_result = get_request(endpoint)
    
    if json_result:
        return json_result
    return None
    
def get_reviews_for_dealer(dealer_id):
    endpoint = f"/fetchReviews/dealer/{dealer_id}"
    json_result = get_request(endpoint)
    
    if json_result:
        return json_result
    return None

# -------------------------------------------------------------
# REQUIRED PROXY FUNCTIONS FOR SENTIMENT & POSTING
# -------------------------------------------------------------

def analyze_review_sentiments(text):
    request_url = f"{sentiment_analyzer_url}/analyze/{text}"
    
    try:
        # ADDED: timeout argument (W3101 Fix)
        response = requests.get(request_url, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Sentiment API failed with status: {response.status_code}")
            return {"sentiment": "N/A"}
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to sentiment API: {e}")
        return {"sentiment": "N/A"}


def post_review(data_dict):
    request_url = f"{backend_url}/insert_review"
    print(f"POST to {request_url} with data: {data_dict}")
    
    try:
        # ADDED: timeout argument (W3101 Fix)
        response = requests.post(request_url, json=data_dict, timeout=10)
        # R1714 Fix: Use 'in' operator
        if response.status_code in (200, 201):
            return response.json()
        else:
            print(f"Post review failed with status: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Network error during POST: {e}")
        return None
        


