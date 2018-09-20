from django.contrib import admin
from .models import ChillerPlant
# Register your models here.
# Register your models here.
@admin.register(ChillerPlant)
class ChillerPlantAdmin(admin.ModelAdmin):
    list_display = ('id','plant_name','datetime')