from django.urls import path
from .views import signpair_list, signpair_detail, vote_view, upload_label

app_name = 'gallery'

urlpatterns = [
    path('', signpair_list, name='signpair_list'),
    path('pair/<str:pk>/', signpair_detail, name='signpair_detail'),
    path('pair/<str:pk>/vote/', vote_view, name='vote'),
    path('upload/', upload_label, name='upload_label'),
]
