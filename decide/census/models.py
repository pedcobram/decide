from django.db import models

class Census(models.Model):
    voting_id = models.PositiveIntegerField()
    voter_id = models.PositiveIntegerField()
    fecha_nacimiento = models.DateField(null=True)
    genero = models.CharField(max_length=10, null=True,choices=(
        ('Masculino','Masculino'),
        ('Femenino','Femenino')
    ))
    provincia = models.CharField(max_length=20,null=True)
    localidad = models.CharField(max_length=20,null=True)

    class Meta:
        unique_together = (('voting_id', 'voter_id'),)
