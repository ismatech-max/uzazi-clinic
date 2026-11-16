from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('', views.reception_dashboard, name='reception_dashboard'),
    path('patients/', views.patients_list, name='patients_list'),
    path('register/', views.register_patient, name='register_patient'),
    path('delete-patient/<int:patient_id>/', views.delete_patient, name='delete_patient'), # Njia mpya ya kufuta
    
    path('appointments/', views.appointments_list, name='appointments_list'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('reschedule-appointment/<int:app_id>/', views.reschedule_appointment, name='reschedule_appointment'), # Njia mpya ya kubadili tarehe
    
    path('follow-up/', views.follow_up_dashboard, name='follow_up_dashboard'),
    path('send-follow-up/', views.send_follow_up, name='send_follow_up'),
    path('checkin/<int:patient_id>/', views.checkin_patient, name='checkin_patient'),
    
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('save-consultation/<int:visit_id>/', views.save_consultation, name='save_consultation'),
    
    path('pharmacy/', views.pharmacy_dashboard, name='pharmacy_dashboard'),
    path('pharmacy/stock/', views.pharmacy_stock, name='pharmacy_stock'),
    path('pharmacy/history/', views.pharmacy_history, name='pharmacy_history'),
    path('complete-payment/<int:consultation_id>/', views.complete_payment, name='complete_payment'),
]