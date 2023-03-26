import requests
import json
# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url,payload, **kwargs):
    print(kwargs)
    try:
        response = requests.post(url, headers={'Content-Type': 'application/json'}, 
                            params=kwargs, json=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except request.exceptions.RequestException as e: 
        print("An error occured", e)
        

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["rows"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"], state=dealer_doc['state'],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealerId):
    reviews = []
    json_result = get_request(url, dealerId=dealerId)
    if json_result:
        for review in json_result:
            review_obj = DealerReview(id=review.id, name=review.name, dealership=review.dealership, purchase=review.purchase,
                                      review=review.review, purchase_date=review.purchase_date, car_make=review.car_make, 
                                      car_model=review.car_model, car_year=review.car_year)
            review.append(review_obj)
    return reviews
            
def get_dealer_by_id_from_cf(url, id):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
    json_result = get_request(url, id=id)
    print(json_result)
    dealer = CarDealer(address=json_result["address"], city=json_result["city"], full_name=json_result["full_name"],
                       id=json_result["id"], lat=json_result["lat"], long=json_result["long"],
                       short_name=json_result["short_name"], st=json_result["st"], zip=json_result["zip"])
    return json_result

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative



