"""
URL patterns for the maternal health app.
ENHANCED with Medical Records Vault & Appointments.
"""

from django.urls import path
from . import views

app_name = 'maternal_health'

urlpatterns = [
    # Main Pages
    path('', views.maternal_home_view, name='home'),
    
    # AI Chatbot
    path('chat/', views.chat_view, name='chat'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/rate-chat/', views.rate_chat, name='rate_chat'),
    path('chat/history/', views.chat_history_view, name='chat_history'),
    
    # Medical Records Vault
    path('vault/', views.medical_vault_view, name='medical_vault'),
    path('vault/upload/', views.upload_medical_record, name='upload_record'),
    path('vault/record/<int:record_id>/', views.record_detail_view, name='record_detail'),
    path('vault/record/<int:record_id>/delete/', views.delete_medical_record, name='delete_record'),
    path('vault/record/<int:record_id>/toggle-important/', views.toggle_important_record, name='toggle_important'),
    
    # Ultrasound Details
    path('vault/record/<int:record_id>/ultrasound-details/', views.add_ultrasound_details, name='add_ultrasound_details'),
    
    # Appointments
    path('appointments/', views.appointments_view, name='appointments'),
    path('appointments/add/', views.add_appointment, name='add_appointment'),
    path('appointments/<int:appointment_id>/complete/', views.mark_appointment_complete, name='mark_appointment_complete'),
]