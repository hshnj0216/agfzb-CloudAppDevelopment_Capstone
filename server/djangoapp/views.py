from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .restapis import get_dealers_from_cf, get_dealer_by_id_from_cf, get_dealer_reviews_from_cf, post_request
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def home(request):
    return render(request, 'djangoapp/home.html')

# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html')

# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    #Check if the request method is post
    if request.method == "POST":
        #Get the username and password from the request.POST dictionary
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        #If user is valid, call the login method and pass the user
        if user is not None:
            login(request, user)
            return redirect(reverse('djangoapp:home'))
        #If not, return to the login page
        else:
            return render(request, 'djangoapp/home.html', context)
    else:
        return render(request, 'djangoapp/home.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect(reverse('djangoapp:home'))

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    #If the method is GET, render the registration page
    if request.method == "GET":
        return render(request, 'djangoapp/registration.html', context)
    #If method is POST, process the registration
    elif request.method == "POST":
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        user_exists = False
        try:
            #Check if the user already exists
            User.objects.get(username=username)
            user_exists = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        #If it is a new user
        if not user_exists:
            #Create user
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            #Login the user and redirect to home page
            login(request, user)
            return redirect(reverse('djangoapp:home'))
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://jp-tok.functions.appdomain.cloud/api/v1/web/3c735b53-57df-4e94-b2ca-02d700b31481/dealership-package/get_dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        context['dealerships'] = dealerships 
        print(dealer_names)
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)
    else:
        message: "There was a problem fetching the data"
        context['message'] = message
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
# ...
    context = {}
    if request.method == "GET":
        get_dealer_url = "https://jp-tok.functions.appdomain.cloud/api/v1/web/3c735b53-57df-4e94-b2ca-02d700b31481/dealership-package/get_dealership"
        get_review_url = "https://jp-tok.functions.appdomain.cloud/api/v1/web/3c735b53-57df-4e94-b2ca-02d700b31481/dealership-package/get_review"
        dealer = get_dealer_by_id_from_cf(get_dealer_url, id=dealer_id)
        print(dealer)
        reviews =  get_dealer_reviews_from_cf(get_review_url, dealerId=dealer_id)
        context['dealer'] = dealer
        context['reviews'] = reviews
        return render(request, 'djangoapp/dealer_details.html', context)
    else:
        return redirect(reverse('djangoapp:not_found'))

# Create a `add_review` view to submit a review
@login_required
def add_review(request, dealer_id):
    url = "https://jp-tok.functions.appdomain.cloud/api/v1/web/3c735b53-57df-4e94-b2ca-02d700b31481/dealership-package/post_review"
    print("from add review: " + str(dealer_id))
    context = {}
    if request.method == "POST":
        if request.POST['purchase'] == "yes":
             review = {
                'name': request.user.username,
                'time': datetime.utcnow().isoformat(),
                'dealership': dealer_id,
                'review': request.POST['review'],
                'purchase': request.POST['purchase']
            }
        else: 
            review = {
                'name': request.user.username,
                'time': datetime.utcnow().isoformat(),
                'dealership': dealer_id,
                'review': request.POST['review'],
                'purchase': request.POST['purchase'],
                'car_make': request.POST['car_make'],
                'car_model': request.POST['car_model'],
                'car_year': request.POST['car_year']
            }
        json_payload = {}
        json_payload['review'] = review
        response = post_request(url, json_payload, dealerId=dealer_id)
        print(response)
        return redirect(reverse('djangoapp:dealer_details', args=[dealer_id]))
    elif request.method == "GET":
        context['dealer_id'] = dealer_id
        return render(request, 'djangoapp/add_review.html', context)

def not_found(request):
    return render(request, 'djangoapp/not_found.html')


