# cloudtrailapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("update_data/<str:ENV>/", views.update_data, name="update_data"),
    path("cloudtrailrecords/<str:ENV>/", views.cloudtrail_records, name="cloudtrail_records"),
    path("resource/<str:ENV>/", views.resource_view, name="resource_view"),
]
