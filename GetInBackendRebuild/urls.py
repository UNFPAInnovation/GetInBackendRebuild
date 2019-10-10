"""GetInBackendRebuild URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include

from app.views import GirlView, GirlDetailsView, UserView, DHOView, MidwifeView, ChewView, AmbulanceView, DistrictView, \
    CountyView, SubCountyView, ParishView, VillageView, HealthFacilityView

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'auth/', include('djoser.urls.base')),
    path(r'auth/', include('djoser.urls.authtoken')),
    path(r'api/v1/girls', GirlView.as_view(), name='girls'),
    path(r'api/v1/girls/(?P<pk>[-\w]+)', GirlDetailsView.as_view(),name='girls-details'),
    path(r'api/v1/users', UserView.as_view(), name='users'),
    path(r'api/v1/dhos', DHOView.as_view(), name='dho'),
    path(r'api/v1/midwives', MidwifeView.as_view(), name='midwife'),
    path(r'api/v1/chews', ChewView.as_view(), name='chew'),
    path(r'api/v1/ambulances', AmbulanceView.as_view(), name='ambulances'),
    path(r'api/v1/districts', DistrictView.as_view(), name='districs'),
    path(r'api/v1/countys', CountyView.as_view(), name='countys'),
    path(r'api/v1/subcountys', SubCountyView.as_view(), name='subcountys'),
    path(r'api/v1/parishes', ParishView.as_view(), name='parishes'),
    path(r'api/v1/villages', VillageView.as_view(), name='villages'),
    path(r'api/v1/healthfacilitys', HealthFacilityView.as_view(), name='health_facilitys'),

]
