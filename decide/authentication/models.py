from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class DecideUser(User):
    fecha_nacimiento = models.DateField(null=True)
    genero = models.CharField(max_length=10, null=True,choices=(
        ('Masculino','Masculino'),
        ('Femenino','Femenino')
    ))
    provincia = models.CharField(max_length=20,null=True)
    localidad = models.CharField(max_length=20,null=True)