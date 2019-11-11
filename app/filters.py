import django_filters

from app.models import Girl, FollowUp, Appointment, MappingEncounter, Delivery, User


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

    class Meta:
        model = Appointment
        fields = {
            'created_from', 'created_to', 'status'
        }


class DeliveryFilter(SuperFilter):
    delivery_location = django_filters.CharFilter(field_name='delivery_location', lookup_expr='icontains',
                                                  help_text='Filter girls who delivered from home or health facility')

    class Meta:
        model = Delivery
        fields = {
            'created_from', 'created_to', 'delivery_location'
        }


class UserFilter(SuperFilter):
    role = django_filters.CharFilter(field_name='role', lookup_expr='icontains',
                                       help_text='Filter user by their role, developer - Developer, dho - DHO, chew - CHEW, '
                                                 'midwife - Midwife, ambulance - Ambulance')

    class Meta:
        model = User
        fields = {
            'created_from', 'created_to', 'role'
        }
