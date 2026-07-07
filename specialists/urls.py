from django.urls import path

from specialists.views import SpecialistDetailView, SpecialistListView, SpecialistWorkingHoursView


urlpatterns = [
    path("specialists/", SpecialistListView.as_view(), name="specialist-list"),
    path("specialists/<int:pk>/", SpecialistDetailView.as_view(), name="specialist-detail"),
    path(
        "specialists/<int:pk>/working-hours/",
        SpecialistWorkingHoursView.as_view(),
        name="specialist-working-hours",
    ),
]
