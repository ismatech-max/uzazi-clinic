from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal
from requests.auth import HTTPBasicAuth
import urllib3
import requests
from .models import Patient, VisitQueue, Appointment, DoctorConsultation, DailySale, MedicineInventory

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- NEXTSMS API ---
def send_nextsms(phone, message):
    try:
        clean_phone = str(phone).strip().replace(" ", "").replace("+", "")
        if clean_phone.startswith('0'): clean_phone = '255' + clean_phone[1:]
        elif len(clean_phone) == 9: clean_phone = '255' + clean_phone
            
        url = "https://messaging-service.co.tz/api/sms/v1/text/single"
        payload = {"from": "UZAZI CARE", "to": clean_phone, "text": message}
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        
        res = requests.post(url, json=payload, headers=headers, auth=HTTPBasicAuth('paulismail990.c0f', 'eagle345'), verify=False, timeout=15)
        print(f"SMS Sent Status: {res.status_code}")
    except Exception as e:
        print(f"SMS Error: {e}")

# --- ULINZI NA LOG-IN (RBAC) ---
def login_view(request):
    if request.user.is_authenticated:
        if not request.user.is_superuser:
            return redirect('doctor_dashboard')
        return redirect('reception_dashboard')
        
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user:
            login(request, user)
            if not user.is_superuser:
                return redirect('doctor_dashboard')
            return redirect('reception_dashboard')
        messages.error(request, "Jina au Nenosiri sio sahihi.")
    return render(request, 'clinic/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# --- MAPOKEZI (RECEPTION) ---
@login_required(login_url='login')
def reception_dashboard(request):
    if not request.user.is_superuser: return redirect('doctor_dashboard')
    context = {
        'total_patients': Patient.objects.count(),
        'todays_visits': VisitQueue.objects.filter(created_at__date=timezone.now().date()).count(),
        'waiting_patients': VisitQueue.objects.filter(status='Waiting').order_by('created_at'),
    }
    return render(request, 'clinic/reception_dashboard.html', context)

@login_required(login_url='login')
def patients_list(request):
    if not request.user.is_superuser: return redirect('doctor_dashboard')
    return render(request, 'clinic/patients.html', {'patients': Patient.objects.all().order_by('-created_at')})

@login_required(login_url='login')
def register_patient(request):
    if request.method == 'POST':
        name, phone = request.POST.get('name'), request.POST.get('phone')
        patient, created = Patient.objects.get_or_create(phone=phone, defaults={'name': name})
        if created:
            msg = f"Hello {name}, Karibu UZAZI CLINIC. Kituo bora kwa huduma za afya ya uzazi, magonjwa ya kina mama, na vipimo. ID yako ni {patient.patient_id_code}. WhatsApp: +255 750825834. Piga: 0697351104."
            send_nextsms(phone, msg)
            messages.success(request, f"{name} amesajiliwa na SMS ya Ukaribisho imetumwa!")
        else:
            messages.info(request, "Mgonjwa huyu tayari yupo kwenye mfumo.")
    return redirect('patients_list')

@login_required(login_url='login')
def delete_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    name = patient.name
    patient.delete()
    messages.success(request, f"Mteja {name} amefutwa kwenye mfumo.")
    return redirect('patients_list')

@login_required(login_url='login')
def checkin_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    VisitQueue.objects.create(patient=patient, status='Waiting', balance_paid=Decimal('80000.00'))
    messages.success(request, f"{patient.name} amepelekwa kwa Daktari.")
    return redirect('reception_dashboard')

# --- MIADI (APPOINTMENTS - YENYE MUDA) ---
@login_required(login_url='login')
def appointments_list(request):
    if not request.user.is_superuser: return redirect('doctor_dashboard')
    return render(request, 'clinic/appointments.html', {'patients': Patient.objects.all(), 'appointments': Appointment.objects.all().order_by('-appointment_date')})

@login_required(login_url='login')
def book_appointment(request):
    if request.method == 'POST':
        patient = Patient.objects.get(id=request.POST.get('patient_id'))
        date = request.POST.get('date')
        time = request.POST.get('time')
        
        Appointment.objects.create(patient=patient, appointment_date=date, appointment_time=time, booking_fee=Decimal('19000.00'))
        
        # SMS inachukua Muda uliochaguliwa
        msg = f"Hello {patient.name}, Karibu UZAZI CLINIC.\nAppointment Yako Ni: {date} Saa {time}\nID yako ni {patient.patient_id_code}.\nTafadhali fika On Time.\nKwa maswali WhatsApp +255 750825834 au Piga 0697351104."
        send_nextsms(patient.phone, msg)
        
        messages.success(request, f"Miadi imehifadhiwa na SMS ya Booking imetumwa!")
    return redirect('appointments_list')

@login_required(login_url='login')
def reschedule_appointment(request, app_id):
    if request.method == 'POST':
        app = get_object_or_404(Appointment, id=app_id)
        new_date = request.POST.get('new_date')
        new_time = request.POST.get('new_time')
        
        app.appointment_date = new_date
        app.appointment_time = new_time
        app.save()
        
        msg = f"Hello {app.patient.name}, Karibu UZAZI CLINIC.\nAppointment Yako Imebadilishwa Kuwa: {new_date} Saa {new_time}\nID yako ni {app.patient.patient_id_code}.\nTafadhali fika On Time.\nWhatsApp +255 750825834."
        send_nextsms(app.patient.phone, msg)
        messages.success(request, f"Miadi imebadilishwa na SMS mpya imetumwa!")
    return redirect('appointments_list')

# --- FOLLOW UP ---
@login_required(login_url='login')
def follow_up_dashboard(request):
    if not request.user.is_superuser: return redirect('doctor_dashboard')
    return render(request, 'clinic/follow_up.html', {'patients': Patient.objects.all()})

@login_required(login_url='login')
def send_follow_up(request):
    if request.method == 'POST':
        msg = request.POST.get('message')
        if request.POST.get('target') == 'all':
            for p in Patient.objects.all(): send_nextsms(p.phone, msg)
            messages.success(request, "Ujumbe umetumwa kwa wote!")
        else:
            p = Patient.objects.get(id=request.POST.get('patient_id'))
            send_nextsms(p.phone, msg)
            messages.success(request, f"Ujumbe umetumwa kwa {p.name}.")
    return redirect('follow_up_dashboard')

# --- DAKTARI (DOCTOR'S DESK) ---
@login_required(login_url='login')
def doctor_dashboard(request):
    query = request.GET.get('q')
    queue = VisitQueue.objects.filter(status='Waiting').order_by('created_at')
    if query:
        queue = queue.filter(Q(patient__name__icontains=query) | Q(patient__phone__icontains=query))
    return render(request, 'clinic/doctor_dashboard.html', {'queue': queue})

@login_required(login_url='login')
def save_consultation(request, visit_id):
    if request.method == 'POST':
        visit = get_object_or_404(VisitQueue, id=visit_id)
        DoctorConsultation.objects.create(
            visit=visit, patient=visit.patient, 
            clinical_findings=request.POST.get('findings'), 
            prescribed_medicines=request.POST.get('meds')
        )
        visit.status = 'Pharmacy'
        visit.save()
        messages.success(request, f"Fomu imehifadhiwa na kupelekwa Famasi.")
        return redirect('doctor_dashboard')

# --- FAMASI (PHARMACY) ---
@login_required(login_url='login')
def pharmacy_dashboard(request):
    if not request.user.is_superuser: return redirect('doctor_dashboard')
    return render(request, 'clinic/pharmacy_dashboard.html', {'pending_payments': DoctorConsultation.objects.filter(visit__status='Pharmacy').order_by('created_at')})

@login_required(login_url='login')
def pharmacy_stock(request):
    if not request.user.is_superuser: return redirect('doctor_dashboard')
    if request.method == 'POST':
        MedicineInventory.objects.create(
            name=request.POST.get('name'), stock_quantity=request.POST.get('qty'),
            price=request.POST.get('price'), pv_points=request.POST.get('pv')
        )
        messages.success(request, "Dawa imeongezwa stoo!")
    return render(request, 'clinic/pharmacy_stock.html', {'medicines': MedicineInventory.objects.all()})

@login_required(login_url='login')
def pharmacy_history(request):
    if not request.user.is_superuser: return redirect('doctor_dashboard')
    return render(request, 'clinic/pharmacy_history.html', {'sales': DailySale.objects.all().order_by('-created_at')})

@login_required(login_url='login')
def complete_payment(request, consultation_id):
    if request.method == 'POST':
        consultation = get_object_or_404(DoctorConsultation, id=consultation_id)
        consultation.total_cost = Decimal(request.POST.get('cost'))
        consultation.pv_points = Decimal(request.POST.get('pv'))
        consultation.save()

        DailySale.objects.create(patient=consultation.patient, consultation=consultation, amount_paid=consultation.total_cost, pv_earned=consultation.pv_points)
        consultation.visit.status = 'Completed'
        consultation.visit.save()

        msg = f"Asante {consultation.patient.name}. Malipo ya Dawa TSh {consultation.total_cost:,.0f} yamepokelewa. Afya Njema!\nWhatsApp: +255 750825834"
        send_nextsms(consultation.patient.phone, msg)
        messages.success(request, "Malipo yamekamilika na Risiti imetumwa!")
        return redirect('pharmacy_dashboard')