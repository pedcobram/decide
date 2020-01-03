from django.contrib import admin

from .models import Census


class CensusAdmin(admin.ModelAdmin):
    list_display = ('voting_id', 'voter_id','fecha_nacimiento','genero','provincia','localidad',)
    list_filter = ('voting_id', 'fecha_nacimiento','genero','provincia','localidad',)

    search_fields = ('voter_id', 'fecha_nacimiento','genero','provincia','localidad',)


admin.site.register(Census, CensusAdmin)
