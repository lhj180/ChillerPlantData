import datetime
from django.shortcuts import render,get_object_or_404,render_to_response,redirect
from django.utils import timezone
from django.core.paginator import Paginator
from .models import ChillerPlant
from ChillerPlantData.views import get_report_common_data
# Create your views here.

def report_list(request):
    
    report_all_list = ChillerPlant.objects.filter(id__isnull = False)
    #datelist = ChillerPlant.objects.datetimes('datetime','month')       #datetime_trunc_sql()几乎都不好使，只有year()
    '''report_list = ChillerPlant.objects.in_bulk([1,2,3])
    report_all_list = []
    for i in [1,2,3]:
        report_all_list.append(report_list[i])'''                      #测试in_bulk()可用
    #report_last = ChillerPlant.objects.last()                         #测试latest()/exists()可用
    exist_result = ChillerPlant.objects.filter(datetime__year = 2018, id__in=[350,338]).values('id','datetime') #values查询时放在get前面，要不然会报错;filter无所谓
    context = get_report_common_data(request,report_all_list)
    context['exist_result'] = exist_result
    #context['datelist'] = datelist

    return render(request,'report_list.html',context)

def report_detail(request,report_id):
    report = get_object_or_404(ChillerPlant,pk = report_id)
    #report = ChillerPlant.objects.get(pk = report_id)                #测试get()可用
    context = {}
    context['report'] = report
    context['xtext']=['室内温度','室外温度','送风温度','回风温度']
    context['yvalue'] = [round(report.indoor_temperature,2),round(report.outdoor_temperature,2),round(report.supply_temperature,2),round(report.return_temperature,2)]
    return render(request,'report_detail.html',context)

    
def each_system(request, plant_name):

    report_all_list = ChillerPlant.objects.filter(plant_name__startswith = plant_name)
    context = get_report_common_data(request,report_all_list)
    context['plant_name'] = plant_name


    if plant_name == 'N1':
        return render(request,'each_system1.html', context)
    if plant_name == 'N2':
        return render(request,'each_system2.html', context)

def each_month(request, year,month):

    #report_all_list = Ac_system.objects.filter(sys_time__year = year,sys_time__month = month)
    if  month in range(1,12):
        report_all_list = ChillerPlant.objects.filter(datetime__gte=datetime.datetime(year,month,1,0,0,0),datetime__lt=datetime.datetime(year,month+1,1,0,0,0))
        report_count = ChillerPlant.objects.filter(datetime__gte=datetime.datetime(year,month,1,0,0,0),datetime__lt=datetime.datetime(year,month+1,1,0,0,0)).count()
    if month == 12:
        report_all_list = ChillerPlant.objects.filter(datetime__gte=datetime.datetime(year,month,1,0,0,0),datetime__lt=datetime.datetime(year+1,1,1,0,0,0))
    #不能用aggregate的原因是$year操作符不能对sys_time，因为存储格式是bson？？
    
    context = get_report_common_data(request,report_all_list)

    context['with_date'] = "%s年%s月"%(year,month)
    context['report_count'] = report_count



    return render(request,'with_date.html', context)

def alert_with_temperature1(request):
    
    
    #report_all_list = Ac_system.objects.filter(compressor__gte ={ 'out_t' }) #并列条件能用，但是" 'in_t'+'out_t' :53 "不能
    #paginator可以对具有count属性的列表进行操作，aggregate聚合返回的是计算后的结果，不具有len属性。因此用list转化为列表继续使用。
    ##管道操作步骤：插入字段——进出口压力和，将字段更换成压力平均值，筛选结果，排序输出
    report_all_list = list(ChillerPlant.objects.mongo_aggregate([{'$addFields':{ 'minus_in_t':{'$multiply':[-1,'$indoor_temperature']}}}
                                                                ,{'$addFields':{ 'gap_t':{'$add':['$outdoor_temperature','$minus_in_t']}}}
                                                                ,{'$match':{'gap_t':{'$gte':8}}}
                                                                ,{'$sort':{'sys_time':-1}}]))
    
    context = get_report_common_data(request,report_all_list)
    alert1_date_list = ChillerPlant.objects.mongo_aggregate([{'$addFields':{ 'minus_in_t':{'$multiply':[-1,'$indoor_temperature']}}}
                                                                ,{'$addFields':{ 'gap_t':{'$add':['$outdoor_temperature','$minus_in_t']}}}
                                                                ,{'$match':{'gap_t':{'$gte':8}}}
                                                                ,{'$group':{'_id':{'year':{'$year':'$datetime'},'month':{'$month':'$datetime'},'day':{'$dayOfMonth':'$datetime'}},'count':{'$sum':1}}}
                                                                ,{'$addFields':{ 'date':{'$max':"$_id"}}}
                                                                ,{'$sort':{'date.day':1}}])
    date_time=[]
    date_count = []
    
    for date in alert1_date_list:
        date_year = int(date['date']['year'])
        date_month = int(date['date']['month'])
        date_day = int(date['date']['day'])
    
        date_time.append(datetime.datetime(date_year,date_month,date_day,0,0,0).strftime('%m/%d/%H'))
        date_count.append(date['count'])

    context = get_report_common_data(request,report_all_list)
    context['date_time'] = date_time
    context['date_count'] = date_count

    return render(request,'alert_with_temperature.html', context)

def alert_with_temperature2(request):
    
    
    #report_all_list = Ac_system.objects.filter(compressor__gte ={ 'out_t' }) #并列条件能用，但是" 'in_t'+'out_t' :53 "不能
    
    report_all_list = list(ChillerPlant.objects.mongo_aggregate([{'$match':{'return_temperature':{'$gte':28.6}}}
                                                                ,{'$sort':{'sys_time':-1}}]))
    alert2_date_list = ChillerPlant.objects.mongo_aggregate([{'$match':{'return_temperature':{'$gte':28.6}}}
                                                                ,{'$group':{'_id':{'year':{'$year':'$datetime'},'month':{'$month':'$datetime'},'day':{'$dayOfMonth':'$datetime'}},'count':{'$sum':1}}}
                                                                ,{'$addFields':{ 'date':{'$max':"$_id"}}}
                                                                ,{'$sort':{'date.day':1}}])
    date_time=[]
    date_count = []
    
    for date in alert2_date_list:
        date_year = int(date['date']['year'])
        date_month = int(date['date']['month'])
        date_day = int(date['date']['day'])
    
        date_time.append(datetime.datetime(date_year,date_month,date_day,0,0,0).strftime('%m/%d/%H'))
        date_count.append(date['count'])

    context = get_report_common_data(request,report_all_list)
    context['date_time'] = date_time
    context['date_count'] = date_count

    return render(request,'alert_with_pressure.html', context)

def click_with_date(request):
    start_date = request.POST.get('start_date','').split('-')
    start_date_year = int(start_date[0])
    start_date_month = int(start_date[1])
    start_date_day = int(start_date[2])
    start_date = datetime.datetime(start_date_year, start_date_month, start_date_day,0,0,0)
    end_date = request.POST.get('end_date','').split('-')
    end_date_year = int(end_date[0])
    end_date_month = int(end_date[1])
    end_date_day = int(end_date[2])
    end_date = datetime.datetime(end_date_year,end_date_month,end_date_day,23,59,59)

    if start_date >= timezone.now():
        return render(request,'error.html',{'message':'日期输入有误'})

    else:    
        if start_date < end_date :
            report_all_list = ChillerPlant.objects.filter(datetime__range=(start_date, end_date))
            click_date_list = ChillerPlant.objects.mongo_aggregate([{'$match':{'datetime':{'$gt':start_date,'$lte' : end_date}}}
                                                                    ,{'$group':{'_id':{'year':{'$year':'$datetime'},'month':{'$month':'$datetime'},'day':{'$dayOfMonth':'$datetime'}},'count':{'$sum':1}}}
                                                                    ,{'$addFields':{ 'date':{'$max':"$_id"}}}
                                                                    ,{'$sort':{'date.day':1}}])
            date_time=[]
            date_count = []
            
            for date in click_date_list:
                date_year = int(date['date']['year'])
                date_month = int(date['date']['month'])
                date_day = int(date['date']['day'])
            
                date_time.append(datetime.datetime(date_year,date_month,date_day,0,0,0).strftime('%m/%d/%H'))
                date_count.append(date['count'])
            context = get_report_common_data(request,report_all_list)
            context['date_time'] = date_time
            context['date_count'] = date_count
            context['start_date'] = start_date
            context['end_date'] = end_date
            return render(request,'click_with_date.html',context)
        
        else:
            return render(request,'error.html',{'message':'日期输入有误'})
    
def create_report(request):
    datetime = timezone.now()                                                    #测试create()可用
    indoor_temperature=float(request.POST.get('indoor_temperature',''))
    outdoor_temperature = float(request.POST.get('outdoor_temperature',''))
    plant_name = request.POST.get('plant_name','')
    return_temperature = float(request.POST.get('return_temperature',''))
    supply_temperature = float(request.POST.get('supply_temperature',''))
    try:
        C = ChillerPlant.objects.create(datetime=datetime,indoor_temperature=indoor_temperature,
                                    outdoor_temperature=outdoor_temperature,plant_name=plant_name,
                                    return_temperature=return_temperature,supply_temperature=supply_temperature)
    
        return redirect('report_list')
    except:
        
        return render(request,'error.html',{'message':'输入信息不正确'})

