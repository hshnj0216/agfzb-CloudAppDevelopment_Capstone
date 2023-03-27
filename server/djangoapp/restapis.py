import requests
import json
# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import SentimentOptions, Features


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    response = None
    try:
        # Call get method of requests library with URL and parameters
        if api_key:
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=params, auth=HTTPBasicAuth('apiKey', api_key))
            json_data = json.loads(response.text)
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
            json_data = json.loads(response)
    except:
        # If any error occurs
        print("Network exception occurred")
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    try:
        response = requests.post(url, headers={'Content-Type': 'application/json'}, 
                                 params=kwargs, json=payload)
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
    print("json_result:", json_result)
    if json_result:
        dealer = CarDealer(
            address=json_result.get("address"),
            city=json_result.get("city"),
            full_name=json_result.get("full_name"),
            id=json_result.get("id"),
            lat=json_result.get("lat"),
            long=json_result.get("long"),
            short_name=json_result.get("short_name"),
            st=json_result.get("st"),
            state=json_result.get("state"),
            zip=json_result.get("zip")
        )
        print(dealer)
        return dealer
    else:
        return redirect(reverse('djangoapp:not_found'))

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(dealer_review):
    api_key = "ZIYL7FkxhVIh7CDvitjeaB7cVBK5D4BRr3Yjsoj76MZl" 
    url = "https://api.jp-tok.natural-language-understanding.watson.cloud.ibm.com/instances/28389b6d-9bbc-49b5-b1d3-82f39dcdf997"
    features = {
        'sentiment': {},
        'emotion': {}
    }
# - Call get_request() with specified arguments
    response = get_request(url, api_key=api_key, text=dealer_review, version='2021-03-25',
                            features=features, return_analyzed_text=False)
    # - Get the returned sentiment label such as Positive or Negative
    sentiment_score = response['sentiment']['document']['score']
    return sentiment_score





