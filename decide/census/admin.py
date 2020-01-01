from django.contrib import admin

from .models import Census
from django.shortcuts import HttpResponse
import csv


def census_download(modeladmin,request, queryset):
    items = queryset

    response = HttpResponse(content_type='text/csv')
    response ['Content-Disposition'] = 'attachment; filename ="census.csv"'

    writer = csv.writer(response, delimiter=',')
    writer.writerow(['voting_id','voter_id'])

    for obj in items:
        writer.writerow([obj.voting_id, obj.voter_id])
    return response



class CensusAdmin(admin.ModelAdmin):
    list_display = ('voting_id', 'voter_id')
    list_filter = ('voting_id', )
    actions = [census_download]

    search_fields = ('voter_id', )


admin.site.register(Census, CensusAdmin)
