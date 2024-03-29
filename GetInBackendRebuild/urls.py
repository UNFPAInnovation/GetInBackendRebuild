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
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_swagger.views import get_swagger_view

from app.notifier import NotifierView
from app.views import GirlView, GirlDetailsView, UserCreateView, DistrictViewSet, \
    CountyView, SubCountyView, ParishView, VillageView, HealthFacilityView, FollowUpView, \
    DeliveriesView, MappingEncounterView, AppointmentView, DashboardStatsView, SmsView, \
    ExtractView, AirtimeDispatchView, UserGetUpdateView
from django.views.decorators.csrf import csrf_exempt

from app.webhook import ODKWebhook

schema_view = get_swagger_view(title='GetIN Django API')


class OptionalSlashRouter(DefaultRouter):
    def __init__(self):
        super(DefaultRouter, self).__init__()
        self.trailing_slash = "/?"


router = OptionalSlashRouter()
router.register(r'districts', DistrictViewSet, basename='districts')

urlpatterns = [
    url(r'^$', schema_view),
    path('admin/', admin.site.urls),
    path(r'auth/', include('djoser.urls.base')),
    path(r'auth/', include('djoser.urls.authtoken')),
    path(r'api/v1/girls', GirlView.as_view(), name='girls'),
    path(r'api/v1/mapping_encounters', MappingEncounterView.as_view(), name='mapping-encounters'),
    path(r'api/v1/girls/<uuid:pk>', GirlDetailsView.as_view(), name='girls-details'),
    path(r'api/v1/users', UserCreateView.as_view(), name='users'),
    path(r'api/v1/users/<uuid:pk>', UserGetUpdateView.as_view(), name='user-details'),
    # path(r'api/v1/districts', DistrictViewSet.as_view(), name='districts'),
    path(r'api/v1/counties', CountyView.as_view(), name='counties'),
    path(r'api/v1/subcounties', SubCountyView.as_view(), name='subcounties'),
    path(r'api/v1/parishes', ParishView.as_view(), name='parishes'),
    path(r'api/v1/villages', VillageView.as_view(), name='villages'),
    path(r'api/v1/healthfacilities', HealthFacilityView.as_view(), name='health_facilities'),
    path(r'api/v1/mapping_encounter_webhook', csrf_exempt(ODKWebhook.as_view()), name='mapping_encounter_webhook'),
    path(r'api/v1/followups', FollowUpView.as_view(), name='followups'),
    path(r'api/v1/deliveries', DeliveriesView.as_view(), name='deliveries'),
    path(r'api/v1/appointments', AppointmentView.as_view(), name='appointments'),
    path(r'api/v1/mapping_encounters_stats', DashboardStatsView.as_view(), name='mapping-encounters-stats'),
    path(r'api/v1/deliveries_stats', DashboardStatsView.as_view(), name='deliveries-stats'),
    path(r'api/v1/sms', SmsView.as_view(), name='sms'),
    path(r'api/v1/extractor', ExtractView.as_view(), name='extractor'),
    path(r'api/v1/notifier', NotifierView.as_view(), name='notifier'),
    path(r'api/v1/airtime_dispatcher', AirtimeDispatchView.as_view(), name='airtime-dispatcher'),
    re_path('^api/v1/', include(router.urls))
]
