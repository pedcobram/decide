import random, csv
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Census
from .admin import CensusAdmin
from base import mods
from base.tests import BaseTestCase
from .admin import export_csv,export_xml
import csv, io

class CensusTestCase(BaseTestCase):
    
    def setUp(self):
        super().setUp()
        self.census = Census(voting_id=1, voter_id=1)
        self.census.save()

    def tearDown(self):
        super().tearDown()
        self.census = None

    def generate_file(self,file_name, voting_id, voter_id1, voter_id2, voter_id3):        
        try:
            myfile = open(file_name, 'w')
            wr = csv.writer(myfile)
            wr.writerow(('voting_id','voter_id','fecha_nacimiento','genero','provincia','localidad'))
            wr.writerow((voting_id,voter_id1,'1990-12-20','Femenino','Sevilla','Sevilla'))
            wr.writerow((voting_id,voter_id2,'2000-12-20','Femenino','Sevilla','Sevilla'))
            wr.writerow((voting_id,voter_id3,'2013-12-20','Femenino','Cordoba','Cordoba'))
        finally:
            myfile.close()

        return myfile

    def test_check_vote_permissions(self):
        response = self.client.get('/census/{}/?voter_id={}'.format(1, 2), format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), 'Invalid voter')

        response = self.client.get('/census/{}/?voter_id={}'.format(1, 1), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Valid voter')

    def test_list_voting(self):
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'voters': [1]})

    def test_add_new_voters_conflict(self):
        data = {'voting_id': 1, 'voters': [1]}
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 409)

    def test_add_new_voters(self):
        data = {'voting_id': 2, 'voters': [1,2,3,4]}
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(data.get('voters')), Census.objects.count() - 1)

    def test_destroy_voter(self):
        data = {'voters': [1]}
        response = self.client.delete('/census/{}/'.format(1), data, format='json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(0, Census.objects.count())

    def test_export_csv_success(self):
        
        census1= Census(voting_id=1, voter_id=7,fecha_nacimiento="1995-05-02" ,genero="masculino",provincia="Sevilla",localidad="Sevilla")
        census2= Census(voting_id=2, voter_id=5,fecha_nacimiento="1998-05-08" ,genero="masculino",provincia="Sevilla",localidad="Sevilla")
        census3= Census(voting_id=3, voter_id=9,fecha_nacimiento="1999-10-02" ,genero="femenino",provincia="Sevilla",localidad="Sevilla")
        census4= Census(voting_id=8, voter_id=7,fecha_nacimiento="1993-07-04" ,genero="masculino",provincia="Málaga",localidad="Málaga")
        ls = [census1,census2,census3,census4]
       
        for census in ls:
            census.save()

        queryset = Census.objects.all()
        response = export_csv(None, None,queryset)
        
        reader= response.getvalue()
        #for row in reader:
            #created = Census.objects.update_or_create(
            #voting_id = row[0].all,
            #voter_id = row[1].all,
            #)
        
        self.assertEqual(response.status_code,200)

    def test_export_xml_success(self):
        
        census1= Census(voting_id=1, voter_id=7,fecha_nacimiento="1995-05-02" ,genero="masculino",provincia="Sevilla",localidad="Sevilla")
        census2= Census(voting_id=2, voter_id=5,fecha_nacimiento="1998-05-08" ,genero="masculino",provincia="Sevilla",localidad="Sevilla")
        census3= Census(voting_id=3, voter_id=9,fecha_nacimiento="1999-10-02" ,genero="femenino",provincia="Sevilla",localidad="Sevilla")
        census4= Census(voting_id=8, voter_id=7,fecha_nacimiento="1993-07-04" ,genero="masculino",provincia="Málaga",localidad="Málaga")
        ls = [census1,census2,census3,census4]
       
        for census in ls:
            census.save()

        queryset = Census.objects.all()
        response = export_xml(None, None,queryset)
        
        reader= response.getvalue()
        
        self.assertEqual(response.status_code,200)

    def test_census_copy_show_ok(self):
        response = self.client.get('/admin/census-copy/')
        self.assertEqual(response.status_code, 200)

    def test_census_copy_create_ok(self):
        data = {'new_voting_id':2,'copy_voting_id':3, 'genero':'both'}
        response = self.client.post('/admin/census-copy/',data)            
        self.assertEqual(response.status_code,200)

    def test_census_copy_create_fail_all_empty(self):
        response = self.client.post('/admin/census-copy/')            
        self.assertEqual(response.status_code,401)

    def test_census_copy_create_fail_new_voting_empty(self):
        data = {'copy_voting_id':2,'genero':'masculino'}
        response = self.client.post('/admin/census-copy/',data)            
        self.assertEqual(response.status_code,401)

    def test_census_copy_create_fail_copy_voting_empty(self):
        data = {'new_voting_id':2,'genero':'masculino'}
        response = self.client.post('/admin/census-copy/',data)            
        self.assertEqual(response.status_code,401)

    def test_census_copy_create_fail_genero_empty(self):
        data = {'copy_voting_id':2,'new_voting_id':4}
        response = self.client.post('/admin/census-copy/',data)            
        self.assertEqual(response.status_code,401)

    def test_census_display_show_ok(self):
        response = self.client.get('/admin/census-display/')
        self.assertEqual(response.status_code, 200)

    def test_census_display_create_ok(self):
        data = {'voting_id':2,'voter_id':3}
        response = self.client.post('/admin/census-display/',data)            
        self.assertEqual(response.status_code,200)

    def test_census_display_create_fail_both_empty(self):
        response = self.client.post('/admin/census-display/')            
        self.assertEqual(response.status_code,401)

    def test_census_display_create_fail_voter_empty(self):
        data = {'voting_id':2}
        response = self.client.post('/admin/census-display/',data)            
        self.assertEqual(response.status_code,401)

    def test_census_display_create_fail_voting_empty(self):
        data = {'voter_id':3}
        response = self.client.post('/admin/census-display/',data)            
        self.assertEqual(response.status_code,401)
        
    def test_csv_census_upload_success(self):

        census_number_preOp = Census.objects.count()
        # Creating a temporal valid csv
        myfile = self.generate_file('test.csv',1,2,3,4)
        file_path = myfile.name
        f = open(file_path, "r")

        response = self.client.post('/census-upload/', {'file':f})
        census_number_postOp = Census.objects.count()

        self.assertGreater(census_number_postOp, census_number_preOp)
        self.assertEqual(response.status_code, 200)

    def test_csv_census_upload_incorrectDataType(self):
        
        census_number_preOp = Census.objects.count()

        # Creating a temporal invalid csv
        myfile = self.generate_file('test_incorrect.csv','aaa','bbb','ccc','ddd')
        file_path = myfile.name
        f = open(file_path, "r")

        response = self.client.post('/census-upload/', {'file':f})
        census_number_postOp = Census.objects.count()

        self.assertEqual(census_number_postOp, census_number_preOp)
        self.assertEqual(response.status_code, 302)

    def test_txt_census_upload_success(self):
        
        census_number_preOp = Census.objects.count()

        # Creating a temporal valid txt
        myfile = self.generate_file('test.txt',1,2,3,4)
        file_path = myfile.name
        f = open(file_path, "r")
        
        response = self.client.post('/census-upload/', {'file':f})
        census_number_postOp = Census.objects.count()

        self.assertGreater(census_number_postOp, census_number_preOp)
        self.assertEqual(response.status_code, 200)

    def test_txt_census_upload_incorrectDataType(self):
        
        census_number_preOp = Census.objects.count()

        # Creating a temporal invalid txt
        myfile = self.generate_file('test_incorrect.txt','aaa','bbb','ccc','ddd')
        file_path = myfile.name
        f = open(file_path, "r")

        response = self.client.post('/census-upload/', {'file':f})
        census_number_postOp = Census.objects.count()

        self.assertEqual(census_number_postOp, census_number_preOp)
        self.assertEqual(response.status_code, 302)

    def test_census_upload_unsupportedFileType(self):

        census_number_preOp = Census.objects.count()

        # Creating a temporal invalid txt
        myfile = self.generate_file('test.py',1,2,3,4)
        file_path = myfile.name
        f = open(file_path, "r")

        response = self.client.post('/census-upload/', {'file':f})
        census_number_postOp = Census.objects.count()

        self.assertEqual(census_number_postOp, census_number_preOp)
        self.assertEqual(response.status_code, 302)

    def test_census_create (self):
        response = self.client.post('/census_create_by_city/')
        self.assertEqual(response.status_code, 404)

        response = self.client.post('/census_create_by_localidad/')
        self.assertEqual(response.status_code, 404)

        response = self.client.post('/census_create_by_age/')
        self.assertEqual(response.status_code, 404)

        response = self.client.post('/census_create_by_genero')
        self.assertEqual(response.status_code, 404)

    
    def test_census_duplicated_key(self):

        census_number_preOp = Census.objects.count()

        # Creating a temporal invalid txt
        myfile = self.generate_file('test.py',1,2,2,2)
        file_path = myfile.name
        f = open(file_path, "r")

        response = self.client.post('/census-upload/', {'file':f})
        census_number_postOp = Census.objects.count()

        self.assertEqual(census_number_postOp, census_number_preOp)
        self.assertEqual(response.status_code, 302)

