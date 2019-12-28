"""decide URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view
from census.views import census_display, census_create_by_city,census_create_by_localidad ,census_create_by_age, census_create_by_genero, census_delete_by_city, census_delete_by_localidad ,census_delete_by_genero, get_all_provincias


schema_view = get_swagger_view(title='Decide API')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('doc/', schema_view),
    path('gateway/', include('gateway.urls')),
    path('admin/census-display/',census_display),
    #adding census
    path('census_create_by_city/<int:voting_id>/<str:provincia>/', census_create_by_city, name='census_create_by_city'),
    path('census_create_by_localidad/<int:voting_id>/<str:localidad>/', census_create_by_localidad, name='census_create_by_localidad'),
    path('census_create_by_age/<int:voting_id>/<int:edad_minima>/', census_create_by_age, name='census_create_by_age'),
    path('census_create_by_genero/<int:voting_id>/<str:genero>/', census_create_by_genero, name='census_create_by_age'),
    #deleting census
    path('census_delete_by_city/<str:provincia>/', census_delete_by_city, name='census_delete_by_city'),
    path('census_delete_by_localidad/<str:localidad>/', census_delete_by_localidad, name='census_delete_by_localidad'),
    path('census_delete_by_genero/<str:genero>/', census_delete_by_genero, name='census_delete_by_genero'),
    #get elements
    path('get_all_provincias/', get_all_provincias, name='get_all_provincias'),
]

for module in settings.MODULES:
    urlpatterns += [
        path('{}/'.format(module), include('{}.urls'.format(module)))
    ]
