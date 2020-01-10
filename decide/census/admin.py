from django.contrib import admin

from .models import Census
from django.shortcuts import HttpResponse
import csv
import xlwt

#export del censo como csv

def export_csv(modeladmin,request, queryset):

    #print(f'queryset --> {queryset}')
   
   
    items = queryset

    response = HttpResponse(content_type='text/csv')
    response ['Content-Disposition'] = 'attachment; filename ="census.csv"'

    writer = csv.writer(response, delimiter=',')
    writer.writerow(['voting_id','voter_id','fecha_nacimiento','genero','provincia','localidad'])

    for obj in items:
        writer.writerow([obj.voting_id, obj.voter_id,obj.fecha_nacimiento, obj.genero, obj.provincia, obj.localidad])

    return response
    

#export del censo como xml

def export_xml(modeladmin,request, queryset):

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="census.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Census')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Voting_id', 'Voter_id','Fecha_nacimiento','Genero','Provincia','Localidad']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows

    font_style = xlwt.XFStyle()

    rows = queryset.values_list('voting_id', 'voter_id','fecha_nacimiento','genero','provincia','localidad')

    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response

class CensusAdmin(admin.ModelAdmin):
    
    list_display = ('voting_id', 'voter_id','fecha_nacimiento','genero','provincia','localidad',)
    list_filter = ('voting_id', 'fecha_nacimiento','genero','provincia','localidad',)
    
    actions = [export_csv,export_xml]

    search_fields = ('voter_id', 'fecha_nacimiento','genero','provincia','localidad',)

    change_list_template = 'census_create_by_parameter.html'


admin.site.register(Census, CensusAdmin)
