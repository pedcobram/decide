from django.contrib import admin

# Register your models here.

from .models import DecideUser

class DecideUserAdmin(admin.ModelAdmin):
    list_display = ('fecha_nacimiento','genero','provincia','localidad',)
    list_filter = ('fecha_nacimiento','genero','provincia','localidad',)

    search_fields = ('fecha_nacimiento','genero','provincia','localidad',)


admin.site.register(DecideUser, DecideUserAdmin)