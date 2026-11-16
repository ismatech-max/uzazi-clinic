from django.db import models
from django.utils import timezone
from decimal import Decimal

class Patient(models.Model):
    patient_id_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.patient_id_code:
            last_id = Patient.objects.order_by('-id').first()
            next_id = (last_id.id + 1) if last_id else 1
            self.patient_id_code = f"UZ-{next_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.patient_id_code})"

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField(null=True, blank=True) # SEHEMU YA MUDA MPYA
    booking_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('19000.00'))
    status = models.CharField(max_length=50, default='Confirmed')
    created_at = models.DateTimeField(auto_now_add=True)

class VisitQueue(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    visit_number = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=50, default='Waiting')
    balance_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.visit_number:
            last_visit = VisitQueue.objects.order_by('-id').first()
            next_v = (last_visit.id + 1) if last_visit else 1
            self.visit_number = f"VIS-{timezone.now().year}-{next_v:06d}"
        super().save(*args, **kwargs)

class MedicineInventory(models.Model):
    name = models.CharField(max_length=200)
    stock_quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    pv_points = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    last_updated = models.DateTimeField(auto_now=True)

class DoctorConsultation(models.Model):
    visit = models.OneToOneField(VisitQueue, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    clinical_findings = models.TextField(blank=True, null=True)
    prescribed_medicines = models.TextField(blank=True, null=True)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    pv_points = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)

class DailySale(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
    consultation = models.OneToOneField(DoctorConsultation, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    pv_earned = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)