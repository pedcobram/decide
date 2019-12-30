from django.urls import path, include
from . import views
from census.views import census_download

urlpatterns = [
    path('', views.CensusCreate.as_view(), name='census_create'),
    path('<int:voting_id>/', views.CensusDetail.as_view(), name='census_detail'),
    path('download-csv/', census_download, name='census_download'),
]
