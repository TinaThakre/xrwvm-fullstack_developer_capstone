# Uncomment the imports before you add the code
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from djangoapp import views 

APP_NAME = 'djangoapp' # Changed to UPPER_CASE to fix C0103 warning
urlpatterns = [
    # AUTHENTICATION PATHS
    path(route='register', view=views.registration, name='register'),
    path(route='login', view=views.login_user, name='login'),
    path(route='logout', view=views.logout_request, name='logout'),

    # DEALER LIST PATHS (Task 19)
    path(route='get_dealers', view=views.get_dealers_list, name='get_dealers_list'),
    path(route='get_dealers/<str:state>', view=views.get_dealers_list, name='get_dealers_by_state'),

    # DEALER DETAILS & REVIEWS PATHS (Task 20)
    path(route='dealer/<int:dealer_id>', view=views.get_dealer_details, name='dealer_details'),
    path(route='reviews/dealer/<int:dealer_id>', view=views.get_dealer_reviews, name='dealer_reviews'),
    
    # ADD REVIEW PATH (Task 21/22)
    path(route='add_review', view=views.add_review, name='add_review'),
    
    path(route='get_cars', view=views.get_cars, name='get_cars'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Ensure one blank line is at the end of the file.