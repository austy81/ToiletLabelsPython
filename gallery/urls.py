from django.urls import path
from .views import signpair_list, upload_label, edit_label

app_name = 'gallery'

urlpatterns = [
    path('', signpair_list, name='signpair_list'),
    path('pair/<str:pk>/edit/', edit_label, name='edit_label'),
    path('upload/', upload_label, name='upload_label'),
]
