from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from xadmin import app_set_up
from xadmin.sites import site
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from xadmin import form_handle
from django.db.models import Q
import json
from xadmin import permissions

# xadmin一启动, 自动导入注册的每个app下的xadmin.py,
# 将app_name, table_name, table_admin想关联 生成enabled_admins字典
app_set_up.auto_discover()


# 打印admin_class内存地址
# for k, v in site.enabled_admins.items():
#     for model_name, admin_class in v.items():
#         print('%s : %s : %s' % (model_name, admin_class, id(admin_class)))


@login_required
def app_index(request):
    return render(request, 'xadmin/dashboard.html', {'site': site})


# @permissions.check_permission
@login_required
def app_table_list(request, app_name):
    return render(request, 'xadmin/app_table_list.html', {'app_name': app_name, 'site': site})


def get_filter_result(request, querysets):
    # print('request---', request.GET)  # <QueryDict: {'consultant': [''], 'status': [''], 'source': ['0']}>
    filter_conditions = {}
    for k, v in request.GET.items():
        if k in ('_page', '_o', '_q'):
            continue
        if v:
            filter_conditions[k] = v
    # filter_conditions = {'date__gte': '2018-11-1', 'consultant': '4', 'status': '0'}
    return querysets.filter(**filter_conditions), filter_conditions


def get_orderby_result(request, querysets, admin_class):
    orderby_index = request.GET.get('_o')
    current_ordered_column = {}
    if orderby_index:
        order_key = admin_class.list_display[abs(int(orderby_index))]  # 拿到排序字段  abs _o = -0
        current_ordered_column[order_key] = orderby_index  # 保存上次排序的条件, 让前端知道当前排序的列

        if orderby_index.startswith('-'):
            order_key = '-' + order_key

        return querysets.order_by(order_key), current_ordered_column
    else:
        return querysets, current_ordered_column


def get_searched_result(request, querysets, admin_class):
    search_value = request.GET.get('_q')
    if search_value:
        q = Q()
        q.connector = 'OR'
        for search_key in admin_class.search_fields:
            q.children.append(('%s__contains' % search_key, search_value))
        return querysets.filter(q)
    return querysets


# @permissions.check_permission
@login_required
def table_obj_list(request, app_name, model_name):
    """取出指定model里的数据返回给前端"""
    admin_class = site.enabled_admins[app_name][model_name]
    if request.method == 'POST':  # action
        selected_action = request.POST.get('action')  # 拿到action name
        selected_ids = json.loads(request.POST.get('selected_ids'))  # 获取选中的obj_id list
        print(' action post---', selected_action, selected_ids)

        # 通过action删除涉及到两次post(首先触发action函数, 其次提交删除表单)
        # 通过action参数判断是否删除
        if not selected_action:  # 如果是删除, 提交删除表单拿不到action name
            if selected_ids:  # 删除选中的数据
                admin_class.model.objects.filter(id__in=selected_ids).delete()
        else:  # 走action流程
            selected_objs = admin_class.model.objects.filter(id__in=selected_ids)
            admin_action_func = getattr(admin_class, selected_action)
            response = admin_action_func(request, selected_objs)
            if response:
                return response

    querysets = admin_class.model.objects.all().order_by('-id')  # 递减 方便查看添加的数据

    querysets, filter_conditions = get_filter_result(request, querysets)
    admin_class.filter_conditions = filter_conditions  # 保留过滤条件

    querysets = get_searched_result(request, querysets, admin_class)
    admin_class.search_key = request.GET.get('_q', '')

    querysets, sorted_column = get_orderby_result(request, querysets, admin_class)

    paginator = Paginator(querysets, admin_class.list_per_page)  # 每页几条数据 返回<Paginator obj>

    page = request.GET.get('_page')
    try:
        querysets = paginator.page(page)  # page obj
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        querysets = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        querysets = paginator.page(paginator.num_pages)

    return render(request, 'xadmin/table_obj_list.html', locals())


def acc_login(request):
    err_msg = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            print('=====', request.GET.get('next', '/xadmin'))
            return redirect('/xadmin')
        else:
            err_msg = 'Wrong username or password!'
    return render(request, 'xadmin/login.html', {'err_msg': err_msg})


def acc_logout(request):
    print('xadmin logout...')
    logout(request)
    return redirect('/xadmin/login/')


# @permissions.check_permission
@login_required
def table_obj_change(request, app_name, model_name, obj_id):
    # 数据修改页
    admin_class = site.enabled_admins[app_name][model_name]
    model_form = form_handle.create_dynamic_model_form(admin_class)
    obj = admin_class.model.objects.get(id=obj_id)
    if request.method == 'GET':
        form_obj = model_form(instance=obj)
    elif request.method == 'POST':
        form_obj = model_form(instance=obj, data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('/xadmin/%s/%s' % (app_name, model_name))
    return render(request, 'xadmin/table_obj_change.html', locals())  # locals() 返回包含当前范围的局部变量的字典


# @permissions.check_permission
@login_required
def table_obj_add(request, app_name, model_name):
    admin_class = site.enabled_admins[app_name][model_name]
    model_form = form_handle.create_dynamic_model_form(admin_class, form_add=True)

    if request.method == 'GET':
        form_obj = model_form()
    elif request.method == 'POST':
        form_obj = model_form(data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect('/xadmin/%s/%s' % (app_name, model_name))
    return render(request, 'xadmin/table_obj_add.html', locals())  # locals() 返回包含当前范围的局部变量的字典, 包括形参


# @permissions.check_permission
@login_required
def table_obj_delete(request, app_name, model_name, obj_id):
    admin_class = site.enabled_admins[app_name][model_name]
    obj = admin_class.model.objects.get(id=obj_id)
    if request.method == 'POST':
        obj.delete()
        return redirect('/xadmin/%s/%s' % (app_name, model_name))
    return render(request, 'xadmin/table_obj_delete.html', locals())
