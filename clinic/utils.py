from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", views.login_view, name="login"),
    path("reception/", views.reception_table, name="reception_table"),
    path("patients/register/", views.register_patient, name="register_patient"),
    path("appointments/book/", views.book_appointment, name="book_appointment"),
    path("appointments/<int:appointment_id>/check-in/", views.check_in, name="check_in"),
    path("doctor/", views.doctor_table, name="doctor_table"),
    path("doctor/visit/<int:visit_id>/save/", views.save_consultation, name="save_consultation"),
    path("pharmacy/", views.pharmacy_table, name="pharmacy_table"),
    path("pharmacy/visit/<int:visit_id>/complete/", views.complete_sale, name="complete_sale"),
    path("marketing/", views.marketing_dashboard, name="marketing_dashboard"),
]