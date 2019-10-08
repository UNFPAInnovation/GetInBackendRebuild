from django.conf.urls import url
from app.views import GirlView, GirlDetailsView

urlpatterns = [
    url(r'girls', GirlView.as_view(), name='girls'),
    url(r'girls/(?P<pk>[-\w]+)', GirlDetailsView.as_view(), name='girls-details'),
]
