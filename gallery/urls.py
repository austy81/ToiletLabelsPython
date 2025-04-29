from django.urls import path
from .views import signpair_list, vote_view, upload_label

app_name = 'gallery'

urlpatterns = [
    path('', signpair_list, name='signpair_list'),
    path('pair/<str:pk>/vote/', vote_view, name='vote'),
    path('upload/', upload_label, name='upload_label'),
]
