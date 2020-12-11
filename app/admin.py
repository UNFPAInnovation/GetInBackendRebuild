from django.contrib import admin

from app.models import User, District, County, SubCounty, Parish, Village, Girl, HealthFacility, FollowUp, Delivery, \
    MappingEncounter, Appointment, AppointmentEncounter, Referral, FamilyPlanning, Observation, NotificationLog, Region

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


admin.site.register(Girl, GirlAdmin)
admin.site.register(HealthFacility)
admin.site.register(FollowUp)
admin.site.register(Delivery)
admin.site.register(Appointment)
admin.site.register(MappingEncounter)
admin.site.register(AppointmentEncounter)
admin.site.register(Referral)
admin.site.register(FamilyPlanning)
admin.site.register(Observation)
admin.site.register(NotificationLog)