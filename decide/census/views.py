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
from voting.models import Voting
from django.shortcuts import render
from django.contrib import messages
import datetime
from django.contrib.auth.decorators import permission_required


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
def census_copy(request):
    template = 'census_copy.html'
    census_list = Census.objects.all()
    fl = len(census_list)
    voting_list = Voting.objects.all()
    context = {'census_list': census_list, 'voting_list':voting_list}
 
    if request.method == 'GET':
        return render(request,template,context)
 
    new_voting_id = request.POST.get('new_voting_id')
    copy_voting_id = request.POST.get('copy_voting_id')
    genero = request.POST.get('genero')
    exists = False
    for c in census_list:
        if c.voting_id == int(new_voting_id):
            messages.error(request,"That census already exists")
            return render(request,template,context)
        if c.voting_id == int(copy_voting_id):
            if not exists:
                exists = True
            if genero == 'masculino' and c.genero == 'Masculino':
                census = Census(voting_id = new_voting_id, voter_id = c.voter_id,
                fecha_nacimiento = c.fecha_nacimiento, genero = c.genero,
                provincia = c.provincia, localidad = c.localidad)
                census.save()
            if genero == 'femenino' and c.genero == 'Femenino':
                census = Census(voting_id = new_voting_id, voter_id = c.voter_id,
                fecha_nacimiento = c.fecha_nacimiento, genero = c.genero,
                provincia = c.provincia, localidad = c.localidad)
                census.save()
            if genero == 'both':
                census = Census(voting_id = new_voting_id, voter_id = c.voter_id,
                fecha_nacimiento = c.fecha_nacimiento, genero = c.genero,
                provincia = c.provincia, localidad = c.localidad)
                census.save()
    
    if not exists:
        messages.error(request,"There is no census refered to that Voting_id")
 
    census_list2 = Census.objects.all()
    sl = len(census_list2)
    context = {'census_list': census_list2, 'voting_list':voting_list}
    if sl != fl:
        context['success'] = 'Census have been created successfully'
    else:
        context['warning'] = 'There are no users with that gender'
    return render(request, template, context)