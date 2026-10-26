# ai_assistant/urls.py
from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    # پنل اصلی
    path('panel/', views.assistant_panel, name='panel'),
    
    # API endpoints
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/session/init/', views.init_session, name='init_session'),
    path('api/session/end/', views.end_session, name='end_session'),
    path('api/history/clear/', views.clear_history, name='clear_history'),
    path('api/history/', views.get_history, name='get_history'),
    path('api/quick-actions/', views.quick_actions, name='quick_actions'),
    
    # ویجت
    path('widget/', views.chat_widget, name='chat_widget'),
]