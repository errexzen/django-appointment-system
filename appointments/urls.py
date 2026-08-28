from django.urls import path

from appointments.views import (
    AppointmentCreateView,
    AppointmentConfirmView,
    AppointmentCancelView,
    AppointmentCompleteView,
    AppointmentNoShowView,
    MyAppointmentListView,
)


urlpatterns = [
    path("appointments/", AppointmentCreateView.as_view(), name="appointment-create"),
    path("my-appointments/", MyAppointmentListView.as_view(), name="my-appointments"),
    path("appointments/<int:pk>/cancel/", AppointmentCancelView.as_view(), name="appointment-cancel"),
    path("appointments/<int:pk>/confirm/", AppointmentConfirmView.as_view(), name="appointment-confirm"),
    path("appointments/<int:pk>/complete/", AppointmentCompleteView.as_view(), name="appointment-complete"),
    path("appointments/<int:pk>/no-show/", AppointmentNoShowView.as_view(), name="appointment-no-show"),
]
