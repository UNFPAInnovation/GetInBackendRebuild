from django.contrib import admin

from app.models import User, District, County, SubCounty, Parish, Village, Girl, HealthFacility, FollowUp, Delivery, \
    MappingEncounter, Appointment, AppointmentEncounter, Referral, FamilyPlanning, Observation, NotificationLog, Region, \
    HealthMessage, SentSmsLog, MSIService

admin.site.register(User)
admin.site.register(Region)
admin.site.register(District)
admin.site.register(County)
admin.site.register(SubCounty)
admin.site.register(Parish)
admin.site.register(Village)


class GirlAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name')
    list_display = ['first_name', 'last_name', 'user', 'created_at']
    exclude = ('followup', 'mappingencounter', 'delivery', 'appointment', 'referral')


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['girl_first_name', 'girl_last_name', 'girl_phone_number', 'user', 'date', 'created_at']

    def girl_first_name(self, obj):
        return obj.girl.first_name

    def girl_last_name(self, obj):
        return obj.girl.last_name

    def girl_phone_number(self, obj):
        return obj.girl.phone_number

    girl_first_name.admin_order_field = 'girl__first_name'
    girl_last_name.admin_order_field = 'girl__last_name'


class MSIServiceAdmin(admin.ModelAdmin):
    search_fields = ('girl__first_name', 'girl__last_name', 'option')
    list_display = ['girl', 'option', 'created_at']


admin.site.register(Girl, GirlAdmin)
admin.site.register(HealthFacility)
admin.site.register(FollowUp)
admin.site.register(Delivery)
admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(MappingEncounter)
admin.site.register(AppointmentEncounter)
admin.site.register(Referral)
admin.site.register(FamilyPlanning)
admin.site.register(Observation)
admin.site.register(NotificationLog)
admin.site.register(HealthMessage)
admin.site.register(SentSmsLog)
admin.site.register(MSIService, MSIServiceAdmin)
