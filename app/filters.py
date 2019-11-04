import django_filters

from app.models import Girl, FollowUp, Appointment


class SuperFilter(django_filters.FilterSet):
    created_at__gte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte',
                                                     help_text='Created at is greater than or equal to')
    created_at__lte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte',
                                                     help_text='Created is less than or equal to')

    class Meta:
        model = Girl
        fields = {
            'created_at__gte', 'created_at__lte'
        }


class GirlFilter(SuperFilter):
    class Meta:
        model = Girl
        fields = {
            'created_at__gte', 'created_at__lte'
        }


class FollowUpFilter(SuperFilter):
    class Meta:
        model = FollowUp
        fields = {
            'created_at__gte', 'created_at__lte'
        }


class AppointmentFilter(SuperFilter):
    class Meta:
        model = Appointment
        fields = {
            'created_at__gte', 'created_at__lte'
        }
