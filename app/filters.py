import datetime

import django_filters

from app.models import Girl, FollowUp, Appointment, MappingEncounter, Delivery, User, AppointmentEncounter


class SuperFilter(django_filters.FilterSet):
    created_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte',
                                                 help_text='Created at is greater than or equal to')
    created_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte',
                                               help_text='Created is less than or equal to', method='to_filter')

    class Meta:
        model = Girl
        fields = {
            'created_from', 'created_to'
        }

    def to_filter(self, queryset, name, value):
        value = value + datetime.timedelta(days=1)
        return queryset.filter(**{name: value})


class GirlFilter(SuperFilter):
    status = django_filters.BooleanFilter(field_name='completed_all_visits', lookup_expr='icontains',
                                          help_text='Girl who have completed all ANC visits')

    class Meta:
        model = Girl
        fields = {
            'created_from', 'created_to', 'status'
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
    status = django_filters.CharFilter(field_name='status', lookup_expr='icontains',
                                       help_text='Filter appointments by status: Missed, Attended, Expected, '
                                                 'Completed')

    date_from = django_filters.DateTimeFilter(field_name='date', lookup_expr='gte',
                                              help_text='Date is greater than or equal to')
    date_to = django_filters.DateTimeFilter(field_name='date', lookup_expr='lte',
                                            help_text='Date is less than or equal to')

    class Meta:
        model = Appointment
        fields = {
            'created_from', 'created_to', 'status', 'date_from', 'date_to'
        }


class DeliveryFilter(SuperFilter):
    delivery_location = django_filters.CharFilter(field_name='delivery_location', lookup_expr='icontains',
                                                  help_text='Filter girls who delivered from home or health facility')

    date_from = django_filters.DateTimeFilter(field_name='date', lookup_expr='gte',
                                              help_text='Date is greater than or equal to')
    date_to = django_filters.DateTimeFilter(field_name='date', lookup_expr='lte',
                                            help_text='Date is less than or equal to')

    class Meta:
        model = Delivery
        fields = {
            'created_from', 'created_to', 'delivery_location', 'date_from', 'date_to'
        }


class UserFilter(SuperFilter):
    role = django_filters.CharFilter(field_name='role', lookup_expr='icontains',
                                     help_text='Filter user by their role, developer - Developer, dho - DHO, chew - CHEW, '
                                               'midwife - Midwife, ambulance - Ambulance')

    midwife_id = django_filters.CharFilter(field_name='midwife__id', lookup_expr='icontains',
                                           help_text='Filter users(vhts) where the midwife is attached')

    class Meta:
        model = User
        fields = {
            'created_from', 'created_to', 'role', 'midwife_id'
        }


class AppointmentEncountersFilter(SuperFilter):
    trimester = django_filters.NumberFilter(field_name='girl__trimester', lookup_expr='equals',
                                            help_text='Filter appointments by trimester: 1, 2, 3, 4')

    class Meta:
        model = AppointmentEncounter
        fields = {
            'created_from', 'created_to', 'trimester'
        }
