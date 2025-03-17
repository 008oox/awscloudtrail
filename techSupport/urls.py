from django.urls import path
from . import views

urlpatterns = [
    path('run_task/', views.run_task, name='run_task'),
    path('list_files/', views.list_files, name='list_files'),
    path('view_file/', views.view_file, name='view_file'),
    path('download_file/', views.download_file, name='download_file'),
]

