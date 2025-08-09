# whiteboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.whiteboard_view, name='whiteboard'),
    path('<uuid:board_id>/', views.whiteboard_view, name='whiteboard-room'),
]
