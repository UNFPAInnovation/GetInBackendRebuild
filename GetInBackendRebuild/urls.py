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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view

from app.views import GirlView, GirlDetailsView, UserCreateView, DistrictView, \
    CountyView, SubCountyView, ParishView, VillageView, HealthFacilityView, MappingEncounterWebhook, FollowUpView, \
    DeliveriesView
from django.views.decorators.csrf import csrf_exempt

schema_view = get_swagger_view(title='GetIN Django API')

urlpatterns = [
    url(r'^$', schema_view),
    path('admin/', admin.site.urls),
    path(r'auth/', include('djoser.urls.base')),
    path(r'auth/', include('djoser.urls.authtoken')),
    path(r'api/v1/girls', GirlView.as_view(), name='girls'),
    path(r'api/v1/girls/(?P<pk>[-\w]+)', GirlDetailsView.as_view(),name='girls-details'),
    path(r'api/v1/users', UserCreateView.as_view(), name='users'),
    path(r'api/v1/districts', DistrictView.as_view(), name='districts'),
    path(r'api/v1/countries', CountyView.as_view(), name='counties'),
    path(r'api/v1/subcounties', SubCountyView.as_view(), name='subcounties'),
    path(r'api/v1/parishes', ParishView.as_view(), name='parishes'),
    path(r'api/v1/villages', VillageView.as_view(), name='villages'),
    path(r'api/v1/healthfacilities', HealthFacilityView.as_view(), name='health_facilities'),
    path(r'api/v1/mapping_encounter_webhook', csrf_exempt(MappingEncounterWebhook.as_view()), name='mapping_encounter_webhook'),
    path(r'api/v1/followups', FollowUpView.as_view(), name='followups'),
    path(r'api/v1/deliveries', DeliveriesView.as_view(), name='deliveries'),

]
