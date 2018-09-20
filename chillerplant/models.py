import django.db.models as djangomodels
from djongo import models
from django.utils import timezone
# Create your models here.

class ChillerPlant(models.Model):

    
    datetime = models.DateTimeField()
    indoor_temperature = models.FloatField()
    outdoor_temperature = models.FloatField()
    plant_name = models.CharField(max_length = 15)
    return_temperature = models.FloatField()
    supply_temperature = models.FloatField()
 
    objects = models.DjongoManager()

    def __str__(self):
        return self.plant_name

    class Meta:
        ordering = ['-datetime']