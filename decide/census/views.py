import csv
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
from django.shortcuts import HttpResponse
from base.perms import UserIsStaff
from .models import Census

from django.contrib.auth.decorators import permission_required

from voting.models import Voting

from authentication.models import DecideUser
from django.shortcuts import render
from django.contrib import messages
import datetime
from django.contrib.auth.decorators import permission_required

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

#@permission_required('admin.can_add_log_entry')
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

    if new_voting_id == None or copy_voting_id == None or genero == None:
        return render(request,template,context,status=ST_401)
    else:
        if new_voting_id == copy_voting_id:
            messages.error(request,'It is the same census')
            return render(request,template,context)
        voting_exists = False
        for voting in voting_list:
            if voting.id == int(new_voting_id):
                voting_exists = True
                break
        if voting_exists:
            census_exists = False
            for c in census_list:
                if c.voting_id == int(copy_voting_id):
                    if not census_exists:
                        census_exists = True
                    if genero == 'masculino' and c.genero == 'Masculino':
                        try:
                            census = Census(voting_id = new_voting_id, voter_id = c.voter_id,
                            fecha_nacimiento = c.fecha_nacimiento, genero = c.genero,
                            provincia = c.provincia, localidad = c.localidad)
                            census.save()
                        except:
                            context['warning'] = 'Some census already exists so they have not been created'
                    if genero == 'femenino' and c.genero == 'Femenino':
                        try:
                            census = Census(voting_id = new_voting_id, voter_id = c.voter_id,
                            fecha_nacimiento = c.fecha_nacimiento, genero = c.genero,
                            provincia = c.provincia, localidad = c.localidad)
                            census.save()
                        except:
                            context['warning'] = 'Some census already exists so they have not been created'
                    if genero == 'both':
                        try:
                            census = Census(voting_id = new_voting_id, voter_id = c.voter_id,
                            fecha_nacimiento = c.fecha_nacimiento, genero = c.genero,
                            provincia = c.provincia, localidad = c.localidad)
                            census.save()
                        except:
                            context['warning'] = 'Some census already exists so they have not been created'
            
            if not census_exists:
                messages.error(request,"There is no census refered to that copy_voting_id")
        else:
            messages.error(request,'There is no voting refered to that new_voting_id')
    
        census_list2 = Census.objects.all()
        sl = len(census_list2)
        context['census_list'] = census_list2
        if sl != fl:
            context['success'] = 'Census have been created successfully'
        return render(request, template, context)

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

def census_upload(request):
    template = "census_upload.html"

    prompt = {
        'supported_files': 'Supported files are: CSV, TXT',
        'order': 'Order of the uploaded file should be voting_id, voter_id'
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