from django.urls import path
from .views import get_network_coverage

urlpatterns = [
    path('', get_network_coverage, name='network_coverage'),
]
