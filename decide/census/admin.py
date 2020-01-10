from django.contrib import admin

from .models import Census


class CensusAdmin(admin.ModelAdmin):
    list_display = ('voting_id', 'voter_id')
    list_filter = ('voting_id', )
    change_list_template = 'buttons.html'

    search_fields = ('voter_id', )


admin.site.register(Census, CensusAdmin)
