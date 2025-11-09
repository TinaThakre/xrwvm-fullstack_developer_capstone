from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from djangoapp import views

APP_NAME = "djangoapp"

urlpatterns = [
    # Authentication paths
    path(
        route="register",
        view=views.registration,
        name="register",
    ),
    path(
        route="login",
        view=views.login_user,
        name="login",
    ),
    path(
        route="logout",
        view=views.logout_request,
        name="logout",
    ),
    # Dealer list paths
    path(
        route="get_dealers",
        view=views.get_dealers_list,
        name="get_dealers_list",
    ),
    path(
        route="get_dealers/<str:state>",
        view=views.get_dealers_list,
        name="get_dealers_by_state",
    ),
    # Dealer details & reviews paths
    path(
        route="dealer/<int:dealer_id>",
        view=views.get_dealer_details,
        name="dealer_details",
    ),
    path(
        route="reviews/dealer/<int:dealer_id>",
        view=views.get_dealer_reviews,
        name="dealer_reviews",
    ),
    # Add review path
    path(
        route="add_review",
        view=views.add_review,
        name="add_review",
    ),
    # Local car data
    path(
        route="get_cars",
        view=views.get_cars,
        name="get_cars",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
