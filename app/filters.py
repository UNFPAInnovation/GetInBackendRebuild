import django_filters

from app.models import Girl, FollowUp, Appointment, MappingEncounter


class SuperFilter(django_filters.FilterSet):
    created_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte',
                                                     help_text='Created at is greater than or equal to')
    created_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte',
                                                     help_text='Created is less than or equal to')

    class Meta:
        model = Girl
        fields = {
            'created_from', 'created_to'
        }


class GirlFilter(SuperFilter):
    class Meta:
        model = Girl
        fields = {
            'created_from', 'created_to'
        }


class FollowUpFilter(SuperFilter):
    class Meta:
        model = FollowUp
        fields = {
            'created_from', 'created_to'
        }


class MappingEncounterFilter(SuperFilter):
    class Meta:
        model = MappingEncounter
        fields = {
            'created_from', 'created_to'
        }


class AppointmentFilter(SuperFilter):
    class Meta:
        model = Appointment
        fields = {
            'created_from', 'created_to'
        }
