from django.contrib import admin
from django.urls import path
from . import views
from ChillerPlantData.views import login,logout,userRegister

urlpatterns = [
    path('',views.report_list,name = 'report_list'),
    path('<int:report_id>',views.report_detail,name = 'report_detail'),
    path('<plant_name>',views.each_system,name='plant_system'), 
    path('date/<int:year>/<int:month>',views.each_month,name='each_month'), 
    path('alert/alert_with_temperature1',views.alert_with_temperature1, name = 'alert_with_temperature1'),
    path('alert/alert_with_temperature2',views.alert_with_temperature2, name = 'alert_with_temperature2'),
    path('login/',login, name = 'login'),
    path('logout/',logout, name = 'logout'),
    path('userRegister/',userRegister, name = 'userRegister'),
    path('click_with_date/',views.click_with_date,name = 'click_with_date'),
    path('create_report/',views.create_report,name = 'create_report')
    #path('ac_monitor/', include('ac_monitor.urls')),
    #path('ckeditor', include('ckeditor_uploader.urls')),
]