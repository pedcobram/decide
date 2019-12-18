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
from authentication.models import DecideUser
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

def census_display(request):
    template = 'census_display.html'
    census_list = Census.objects.all()
    voting_list = Voting.objects.all()
    user_list = DecideUser.objects.all()
    context = {'census_list': census_list,'voting_list':voting_list,'user_list':user_list}

    if request.method == 'GET':
        return render(request,template,context)

    voting_id = request.POST.get('voting_id')
    voter_id = request.POST.get('voter_id')
    if voting_id == None or voter_id == None:
        return render(request,template,context,status=ST_401)
    else:
        voting_exists = False
        for voting in voting_list:
            if voting.id == int(voting_id): 
                voting_exists = True
                break
        if voting_exists:
            user_exists = False
            for user in user_list:
                if user.id == int(voter_id):
                    user_exists = True
                    break
            if user_exists:
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
        else:
            messages.error(request, "This voting does not exist")

        return render(request,template,context)