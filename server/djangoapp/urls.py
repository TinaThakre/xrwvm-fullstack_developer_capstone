# Uncomment the imports before you add the code
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from djangoapp import views 

app_name = 'djangoapp'
urlpatterns = [
    # AUTHENTICATION PATHS
    path(route='register', view=views.registration, name='register'),
    path(route='login', view=views.login_user, name='login'),
    path(route='logout', view=views.logout_request, name='logout'),

    # DEALER LIST PATHS (Task 19)
    # Handles /djangoapp/get_dealers/ and /djangoapp/get_dealers/Texas
    path(route='get_dealers', view=views.get_dealers_list, name='get_dealers_list'),
    path(route='get_dealers/<str:state>', view=views.get_dealers_list, name='get_dealers_by_state'),

    # DEALER DETAILS & REVIEWS PATHS (Task 20)
    path(route='dealer/<int:dealer_id>', view=views.get_dealer_details, name='dealer_details'),
    path(route='reviews/dealer/<int:dealer_id>', view=views.get_dealer_reviews, name='dealer_reviews'),
    
    # ADD REVIEW PATH (Task 21/22)
    path(route='add_review', view=views.add_review, name='add_review'),
    
    path(route='get_cars', view=views.get_cars, name='get_cars'),
    # You may optionally need paths for your static pages here if React isn't handling them
    # path('about/', views.about, name='about'),
    # path('contact/', views.contact, name='contact'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)