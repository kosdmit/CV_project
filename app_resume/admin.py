from django.contrib import admin

from app_resume.models import Resume, MainEducation, Institution, \
    AdditionalEducation, ElectronicCertificate, Skill, WorkExpSection, Job


# Register your models here.
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'updated_date', 'is_primary', 'rating')

admin.site.register(Resume, ResumeAdmin)


class MainEducationAdmin(admin.ModelAdmin):
    list_display = ('resume', 'level', 'degree',)

admin.site.register(MainEducation, MainEducationAdmin)


class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('resume', 'title', 'completion_date', 'is_primary',)

admin.site.register(Institution, InstitutionAdmin)


class AdditionalEducationAdmin(admin.ModelAdmin):
    list_display = ('resume', 'title', 'completion_date',)

admin.site.register(AdditionalEducation, AdditionalEducationAdmin)


class ElectronicCertificateAdmin(admin.ModelAdmin):
    list_display = ('resume', 'title', 'completion_percentage', 'completion_date',)

admin.site.register(ElectronicCertificate, ElectronicCertificateAdmin)


class SkillAdmin(admin.ModelAdmin):
    list_display = ('resume', 'title', 'updated_date',)

admin.site.register(Skill, SkillAdmin)


class WorkExpSectionAdmin(admin.ModelAdmin):
    list_display = ('resume', 'title', 'start_date', 'finish_date')

admin.site.register(WorkExpSection, WorkExpSectionAdmin)


class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'finish_date', 'position', 'company')

admin.site.register(Job, JobAdmin)