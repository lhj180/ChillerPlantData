import datetime
from django.shortcuts import render,render_to_response,redirect
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Avg,Max
from django.contrib import auth  
from django.contrib.auth.models import User
from chillerplant.models import ChillerPlant


def get_report_common_data(request,report_all_list):

    paginator = Paginator(report_all_list,10)
    page_num = request.GET.get('page',1)  #获取页码参数（GET请求）
    page_of_reports = paginator.get_page(page_num) #get_page这个函数自动识别调整参数类型
    current_page_num = page_of_reports.number #获取当前页码
    page_range = list(range(max(current_page_num-1,1),min(current_page_num+1,paginator.num_pages)+1))
    # 加上省略号
    if page_range[0]>2:
        page_range.insert(0,'...')
    # 加上首页
    if page_range[0]!=1:
        page_range.insert(0,1)
    # 加上省略号
    if page_range[-1]<paginator.num_pages-1:
        page_range.append('...')
    # 加上尾页
    if page_range[-1]!=paginator.num_pages:
        page_range.append(paginator.num_pages)

    
    '''blog_date_dict = {}
    blog_dates = Blog.objects.dates('created_time','month',order = "DESC")
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year = blog_date.year,created_time__month = blog_date.month).count()
        blog_date_dict[blog_date] = blog_count'''
    
    current_time = timezone.now().date()
    date_list = ChillerPlant.objects.mongo_aggregate([{'$group':{'_id':{'year':{'$year':'$datetime'},'month':{'$month':'$datetime'}},'count':{'$sum':1}}}
                                                    ,{'$addFields':{ 'date':{'$max':"$_id"}}}])
    context = {}
    context['plant_names'] = ChillerPlant.objects.mongo_distinct("plant_name")
    context['current_time'] = current_time
    context['page_of_reports'] = page_of_reports
    context['page_range'] = page_range
    context['date_list'] = date_list
    

    return context

def home(request):

    #取最近三十个时间数据然后按时间前后顺序排列
    plant_names = ChillerPlant.objects.mongo_distinct('plant_name')
    
    report_all_dict = {}
    recent_days = 30
    for plant_name in plant_names:
        
        #方法二
        report_each_system = list(ChillerPlant.objects.mongo_aggregate([{'$match':{'plant_name':plant_name}}
                                                                        ,{'$sort':{'datetime':-1}}
                                                                        ,{'$limit':recent_days}]))[::-1]
        times = []
        indoor_t = []
        outdoor_t = []
        supply_t = []
        return_t = []

        for i in range(0,recent_days):
            times.append(report_each_system[i]['datetime'].strftime('%m/%d/%H'))
            indoor_t.append(round(report_each_system[i]['indoor_temperature'],2) ) 
            outdoor_t.append(round(report_each_system[i]['outdoor_temperature'],2) )
            supply_t.append(round(report_each_system[i]['supply_temperature'],2) )  
            return_t.append(round(report_each_system[i]['return_temperature'],2) )
        inout_temp_calculate = list(ChillerPlant.objects.mongo_aggregate([{'$match':{'plant_name':plant_name}}
                                                                        ,{'$sort':{'datetime':-1}}
                                                                        ,{'$limit':recent_days}
                                                                        ,{'$group':{'_id':None,'av_in_t':{'$avg':'$indoor_temperature'},'av_out_t':{'$avg':'$outdoor_temperature'}}}]))
        supplyreturn_temp_calculate = list(ChillerPlant.objects.mongo_aggregate([{'$match':{'plant_name':plant_name}}
                                                                        ,{'$sort':{'datetime':-1}}
                                                                        ,{'$limit':recent_days}
                                                                        ,{'$group':{'_id':None,'max_supply_t':{'$max':'$supply_temperature'},'max_return_t':{'$max':'$return_temperature'},'min_supply_t':{'$min':'$supply_temperature'},'min_return_t':{'$min':'$return_temperature'}}}]))

        #方法三
        
        '''
        report_calculate = Ac_system.objects.filter(sys_name=sys_name)
        result = report_calculate.aggregate(max_time=Max('sys_time')) #1.不能用，因为Avg函数不能抓取embeddfield的数据; 2.换成正常的数据则聚合方法可用; 3.筛选之后可聚合，切片之后则不可聚合。
        report_list['max_time']= result['max_time']
        '''
        report_list = {}
        report_list['times']= times
        report_list['indoor_t'] =indoor_t
        report_list['outdoor_t'] =outdoor_t
        report_list['supply_t'] =supply_t
        report_list['return_t'] =return_t
        #report_list['report_calculat_list'] =report_calculat_list
        #report_list['average_in_t_list'] = average_in_t_list
        #report_list['average_out_t_list'] = average_out_t_list
        report_list['average_in_t'] = inout_temp_calculate[0]['av_in_t']
        report_list['average_out_t'] = inout_temp_calculate[0]['av_out_t']
        report_list['max_supply_t'] = supplyreturn_temp_calculate[0]['max_supply_t']
        report_list['max_return_t'] = supplyreturn_temp_calculate[0]['max_return_t']
        report_list['min_supply_t'] = supplyreturn_temp_calculate[0]['min_supply_t']
        report_list['min_return_t'] = supplyreturn_temp_calculate[0]['min_return_t']

    
        report_all_dict[plant_name]  = report_list
        
        #report_all_list = report_all_list[::-1]
    '''for i in range(0,len(report_all_list)):
        times.append(report_all_list[i].sys_time.strftime('%H/%M/%S'))  #时间的格式字母！！！
        compressor_in_t.append(round(report_all_list[i].compressor.in_t,2) or 0) '''
    
    context={}
    #context['times'] = times
    #context['compressor_in_t'] = compressor_in_t
    context['plant_names'] = plant_names

    context['report_all_dict'] =report_all_dict


    return render(request,'home.html',context)

def login(request):
    username = request.POST.get('username','')
    password = request.POST.get('password','')
    user = auth.authenticate(request,username = username,password = password)
    if user is not None:
        auth.login(request,user)
        return redirect('/')
    else:
        return render(request,'error.html',{'message':'用户名或密码不正确'})

def logout(request):
    auth.logout(request)
    return redirect('home')

def userRegister(request):
    
    username=request.POST.get('username','')
    password1 = request.POST.get('password1','')
    password2 = request.POST.get('password2','')
    email = request.POST.get('email','')
    errors=[]
    
    if password1 !=password2:
        errors.append("两次输入密码不同")
        return render(request,'userRegister.html',{'message':'两次输入密码不同'})
    filterResult = User.objects.filter(username = username)
    if len(filterResult)>0:
        return render(request,'userRegister.html',{'message':'用户名已存在'}) 

    user = User()
    user.username = username
    user.set_password(password1)
    user.email = email
    user.save()
    newUser = auth.authenticate(username = username,password=password1)
    if newUser is not None:
        auth.login(request,newUser)
        return redirect('/')
