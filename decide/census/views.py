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

from django.shortcuts import render
from django.contrib import messages
import csv, io, argparse
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, HttpResponseRedirect


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

def census_upload(request):
    template = "census_upload.html"

    prompt = {
        'order': 'Order of the CSV should be voting_id, voter_id'
    }

    if request.method == "GET":
        return render(request, template, prompt)

    uploaded_file = request.FILES['file']

    if not(uploaded_file.name.endswith(".csv") or uploaded_file.name.endswith(".txt")):
        messages.error(request, 'This is not a csv or txt file, try again with a valid file format')
        return HttpResponseRedirect('../upload-csv/')      

    data_set = uploaded_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)

    if(uploaded_file.name.endswith(".csv")):
        for column in csv.reader(io_string, delimiter=',', quotechar='|'):

            if(column[0].isdigit() == False or column[1].isdigit() == False ): # or  column[2].isdigit == False or column[3].isdigit == True or column[4].isdigit == True or column[5].isdigit == True ):
                        messages.error(request, 'Columns do not have the correct data type. Please correct the error and try again.')
                        return HttpResponseRedirect('../upload-csv/') 

            _, created = Census.objects.update_or_create(
                voting_id = column[0],
                voter_id = column[1]                
                # birth_date = column[2],
                # gender = column[3],
                # city = column[4],
                # town = column[5]
            )

    if(uploaded_file.name.endswith(".txt")):
        for column in csv.reader(io_string, delimiter=',', quotechar='|'):

            if(column[0].isdigit() == False or column[1].isdigit() == False ): # or  column[2].isdigit == False or column[3].isdigit == True or column[4].isdigit == True or column[5].isdigit == True ):
                        messages.error(request, 'Columns do not have the correct data type. Please correct the error and try again.')
                        return HttpResponseRedirect('../upload-csv/') 

            _, created = Census.objects.update_or_create(
                voting_id = column[0],
                voter_id = column[1]                
                # birth_date = column[2],
                # gender = column[3],
                # city = column[4],
                # town = column[5]
                
            )

    context = {}
    return render(request, template, context)