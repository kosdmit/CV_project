from django.contrib import admin

from app_job_hunt.models import Employer


# Register your models here.
class EmployerAdmin(admin.ModelAdmin):
    list_display = ('user', 'raw_contact', 'company', 'position', 'name', 'email', 'phone_number')

admin.site.register(Employer, EmployerAdmin)
