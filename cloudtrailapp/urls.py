# cloudtrailapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("update_data/<str:ENV>/", views.update_data, name="update_data"),
    path("cloudtrail_records/<str:ENV>/", views.cloudtrail_records, name="cloudtrail_records"),
]
