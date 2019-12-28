from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import (
        HTTP_201_CREATED as ST_201,
        HTTP_204_NO_CONTENT as ST_204,
        HTTP_400_BAD_REQUEST as ST_400,
        HTTP_401_UNAUTHORIZED as ST_401,
        HTTP_409_CONFLICT as ST_409
)

from base.perms import UserIsStaff
from .models import Census
from authentication.models import DecideUser
from django.shortcuts import render
from django.contrib import messages
import datetime
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse

from datetime import datetime, date


class CensusCreate(generics.ListCreateAPIView):
    permission_classes = (UserIsStaff,)

    def create(self, request, *args, **kwargs):
        voting_id = request.data.get('voting_id')
        voters = request.data.get('voters')
        try:
            for voter in voters:
                census = Census(voting_id=voting_id, voter_id=voter)
                census.save()
        except IntegrityError:
            return Response('Error try to create census', status=ST_409)
        return Response('Census created', status=ST_201)

    def list(self, request, *args, **kwargs):
        voting_id = request.GET.get('voting_id')
        voters = Census.objects.filter(voting_id=voting_id).values_list('voter_id', flat=True)
        return Response({'voters': voters})


class CensusDetail(generics.RetrieveDestroyAPIView):

    def destroy(self, request, voting_id, *args, **kwargs):
        voters = request.data.get('voters')
        census = Census.objects.filter(voting_id=voting_id, voter_id__in=voters)
        census.delete()
        return Response('Voters deleted from census', status=ST_204)

    def retrieve(self, request, voting_id, *args, **kwargs):
        voter = request.GET.get('voter_id')
        try:
            Census.objects.get(voting_id=voting_id, voter_id=voter)
        except ObjectDoesNotExist:
            return Response('Invalid voter', status=ST_401)
        return Response('Valid voter')

@permission_required('admin.can_add_log_entry')
def census_display(request):
    template = 'census_display.html'
    census_list = Census.objects.all()
    user_list = DecideUser.objects.all()
    context = {'census_list': census_list,'user_list':user_list}

    if request.method == 'GET':
        return render(request,template,context)

    voting_id = request.POST.get('voting_id')
    voter_id = request.POST.get('voter_id')
    exists = False
    for user in user_list:
        if user.id == int(voter_id):
            exists = True
            break
    if exists:
        try:
            census = Census(voting_id = voting_id, voter_id = user.id, 
            fecha_nacimiento = user.fecha_nacimiento, genero = user.genero, 
            provincia = user.provincia, localidad = user.localidad)
            census.save()
            context['success'] = 'Census has been successfully stored'
            return render(request,template,context)
        except:
            messages.error(request, "This census already exists")
    else:
        messages.error(request, 'This user does not exist')

    return render(request,template,context)

@permission_required('admin.can_add_log_entry')
def census_create_by_city(request, voting_id, provincia):

    print("Provincia: "+provincia)

    users_set = DecideUser.objects.filter(provincia=provincia)


    for user in users_set:

        census = Census(voting_id = voting_id, voter_id = user.id, 
            fecha_nacimiento = user.fecha_nacimiento, genero = user.genero, 
            provincia = user.provincia, localidad = user.localidad)
        census.save()
    return HttpResponse('<h1>POST BY PROVINCIA</h1>')

@permission_required('admin.can_add_log_entry')
def census_create_by_localidad(request, voting_id, localidad):

    users_set = DecideUser.objects.filter(localidad=localidad)

    for user in users_set:

        census = Census(voting_id = voting_id, voter_id = user.id, 
            fecha_nacimiento = user.fecha_nacimiento, genero = user.genero, 
            provincia = user.provincia, localidad = user.localidad)
        census.save()
    return HttpResponse('<h1>POST BY LOCALIDAD</h1>')

'''
@permission_required('admin.can_add_log_entry')
def census_delete_by_city(request, voting_id, provincia):
'''
@permission_required('admin.can_add_log_entry')
def census_create_by_age(request, voting_id, edad_minima):

    print("Voting id: "+str(voting_id))

    users_set = DecideUser.objects.all()

    for user in users_set:
        fecha_nacimiento = user.fecha_nacimiento
        fecha_actual = date.today()
        #fd_a = user.fecha_nacimiento.strftime("%d/%m/%Y")
        #date_now = date.today().strftime("%d/%m/%Y")
        #print("Fecha de nacimiento: "+str(fd_a))
        #print("Date now: "+str(date_now))
        years = fecha_actual.year- fecha_nacimiento.year -((fecha_actual.month,fecha_actual.day)<(fecha_nacimiento.month,fecha_nacimiento.day))
        print("Years: "+str(years))
        print("Fecha de nacimiento: "+str(fecha_nacimiento))

        if years>=edad_minima:
            census = Census(voting_id = voting_id, voter_id = user.id, 
            fecha_nacimiento = user.fecha_nacimiento, genero = user.genero, 
            provincia = user.provincia, localidad = user.localidad)
            census.save()

    return HttpResponse('<h1>POST BY AGE</h1>')


@permission_required('admin.can_add_log_entry')
def census_create_by_genero(request, voting_id, genero):

    users_set = DecideUser.objects.filter(genero=genero)

    for user in users_set:

        census = Census(voting_id = voting_id, voter_id = user.id, 
            fecha_nacimiento = user.fecha_nacimiento, genero = user.genero, 
            provincia = user.provincia, localidad = user.localidad)
        census.save()
    return HttpResponse('<h1>POST BY GENERO</h1>')








