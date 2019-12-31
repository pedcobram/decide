import random, csv
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Census
from base import mods
from base.tests import BaseTestCase


class CensusTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.census = Census(voting_id=1, voter_id=1)
        self.census.save()

    def tearDown(self):
        super().tearDown()
        self.census = None

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

    def test_csv_census_upload_success(self):

        # Creating a temporal valid csv
        myfile = open('test.csv', 'w')
        wr = csv.writer(myfile)
        wr.writerow(('voting_id','voter_id'))
        wr.writerow((1,2))
        wr.writerow((1,3))
        wr.writerow((1,4))
        myfile.close()

        myfile = open('test.csv','r') 
        response = self.client.post('/upload-csv/', {'file':myfile})
        self.assertEqual(response.status_code, 200)

    def test_csv_census_upload_incorrectDataType(self):

        # Creating a temporal invalid csv
        myfile = open('test_incorrect.csv', 'w')
        wr = csv.writer(myfile)
        wr.writerow(('voting_id','voter_id'))
        wr.writerow(('aaa','bbb'))
        wr.writerow(('aaa','ccc'))
        wr.writerow(('aaa','ddd'))
        myfile.close()

        myfile = open('test_incorrect.csv','r') 
        response = self.client.post('/upload-csv/', {'file':myfile})
        self.assertEqual(response.status_code, 302)

    def test_txt_census_upload_success(self):
        
        # Creating a temporal valid txt
        myfile = open('test.txt', 'w')
        wr = csv.writer(myfile)
        wr.writerow(('voting_id','voter_id'))
        wr.writerow((1,2))
        wr.writerow((1,3))
        wr.writerow((1,4))
        myfile.close()
        
        myfile = open('test.txt','r') 
        response = self.client.post('/upload-csv/', {'file':myfile})
        self.assertEqual(response.status_code, 200)

    def test_txt_census_upload_incorrectDataType(self):

        # Creating a temporal invalid txt
        myfile = open('test_incorrect.txt', 'w')
        wr = csv.writer(myfile)
        wr.writerow(('voting_id','voter_id'))
        wr.writerow(('aaa','bbb'))
        wr.writerow(('aaa','ccc'))
        wr.writerow(('aaa','ddd'))
        myfile.close()

        myfile = open('test_incorrect.txt','r') 
        response = self.client.post('/upload-csv/', {'file':myfile})
        self.assertEqual(response.status_code, 302)

    def test_census_upload_unsupportedFileType(self):

        # Creating a temporal invalid txt
        myfile = open('test.py', 'w')
        wr = csv.writer(myfile)
        wr.writerow(('voting_id','voter_id'))
        wr.writerow(('aaa','bbb'))
        wr.writerow(('aaa','ccc'))
        wr.writerow(('aaa','ddd'))
        myfile.close()

        myfile = open('test.py','r') 
        response = self.client.post('/upload-csv/', {'file':myfile})
        self.assertEqual(response.status_code, 302)