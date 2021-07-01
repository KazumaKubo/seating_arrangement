from django.contrib import admin
from .models import NameManagement, SeatManagement, SeatHistory, Zone


class NameManagementAdmin(admin.ModelAdmin):
    list_display = ['student_number', 'last_name', 'first_name', 'active']
    list_filter = ['active']


class SeatManagementAdmin(admin.ModelAdmin):
    list_display = ['seat_number', 'name', 'weight', 'lk']
    list_filter = ['lk']

    def name(self, obj):
        return obj.namemanagement.last_name

    name.short_description = '苗字'
    name.admin_order_field = 'name'


class SeatHistoryAdmin(admin.ModelAdmin):
    list_filter = ['seat_number', 'h_name', 'save_date']
    list_display = ['seat_number', 'save_date']


admin.site.register(NameManagement, NameManagementAdmin)
admin.site.register(SeatManagement, SeatManagementAdmin)
admin.site.register(SeatHistory, SeatHistoryAdmin)
admin.site.register(Zone)

# Register your models here.
