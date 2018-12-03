from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from crm import models
from crm import forms
import os
import json
from django import conf
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.db.utils import IntegrityError


@login_required  # 用户未认证, 会返回带有next参数到login页面
def dashboard(request):
    return render(request, 'crm/dashboard.html')


@login_required
def contract_audit(request, enrollment_id):
    # 审核
    enrollment_obj = models.StudentEnrollment.objects.get(id=enrollment_id)
    if request.method == 'POST':
        enrollment_form = forms.EnrollmentForm(instance=enrollment_obj, data=request.POST)
        if enrollment_form.is_valid():
            enrollment_form.save()

            # 审核后 将学员加入班级
            stu_obj = models.Student.objects.get_or_create(customer=enrollment_obj.customer)[0]  # (obj, true/false)
            stu_obj.class_grades.add(enrollment_obj.class_grade_id)
            stu_obj.save()
            enrollment_obj.customer.status = 1  # 修改报名状态
            enrollment_obj.customer.save()
            return redirect("/xadmin/crm/customerinfo/%s/change/" % enrollment_obj.customer.id)
    else:
        customer_form = forms.CustomerForm(instance=enrollment_obj.customer)
        enrollment_form = forms.EnrollmentForm(instance=enrollment_obj)

    return render(request, 'crm/contract_audit.html', locals())


@login_required
def stu_enrollment(request):
    customers = models.CustomerInfo.objects.all()
    classlists = models.ClassList.objects.all()

    if request.method == 'POST':
        customerid = request.POST.get('customer_id')
        classid = request.POST.get('classgrade_id')

        print(customerid, classid)

        try:
            stu_enrollment_obj = models.StudentEnrollment.objects.create(
                customer_id=customerid,
                class_grade_id=classid,
                consultant_id=request.user.userprofile.id  # 当前用户
            )
        except IntegrityError as e:  # 联合唯一 已经生成过报名表了
            stu_enrollment_obj = models.StudentEnrollment.objects.get(customer_id=customerid,
                                                                      class_grade_id=classid, )
            if stu_enrollment_obj.contract_agreed:
                return redirect("/crm/enrollment/%s/contract_audit/" % stu_enrollment_obj.id)

        enrollment_link = "http://localhost:8000/crm/enrollment/%s/" % stu_enrollment_obj.id
    return render(request, 'crm/student_enrollment.html', locals())


def enrollment(request, enrollment_id):
    """学员在线报名表地址"""
    enrollment_obj = models.StudentEnrollment.objects.get(id=enrollment_id)

    if enrollment_obj.contract_agreed:
        return HttpResponse("报名合同正在审核中....")

    if request.method == 'POST':
        customer_form = forms.CustomerForm(instance=enrollment_obj.customer, data=request.POST)
        if customer_form.is_valid():  # 钩子 触发modelform的clean 防止提交的只读字段被前端修改
            print(customer_form.cleaned_data)
            customer_form.save()

            # 设置报名成功标志 待审核
            enrollment_obj.contract_agreed = True
            enrollment_obj.contract_signed_date = datetime.datetime.now()
            enrollment_obj.save()
            return HttpResponse("您已成功提交报名信息,请等待审核通过!")
    else:
        customer_form = forms.CustomerForm(instance=enrollment_obj.customer)

    # 列出已上传文件
    uploaded_files = []
    enrollment_upload_dir = os.path.join(conf.settings.CRM_FILE_UPLOAD_DIR, enrollment_id)
    if os.path.isdir(enrollment_upload_dir):
        uploaded_files = os.listdir(enrollment_upload_dir)

    return render(request, 'crm/enrollment.html', locals())


@csrf_exempt
def enrollment_fileupload(request, enrollment_id):
    # print(request.FILES)
    enrollment_upload_dir = os.path.join(conf.settings.CRM_FILE_UPLOAD_DIR, enrollment_id)
    if not os.path.isdir(enrollment_upload_dir):
        os.makedirs(enrollment_upload_dir)

    file_obj = request.FILES.get('file')
    if len(os.listdir(enrollment_upload_dir)) <= 2:
        with open(os.path.join(enrollment_upload_dir, file_obj.name), "wb") as f:
            for chunks in file_obj.chunks():
                f.write(chunks)

    else:
        return HttpResponse(json.dumps({'status': False, 'err_msg': 'max upload limit is 2'}))

    print(conf.settings.CRM_FILE_UPLOAD_DIR)

    return HttpResponse(json.dumps({'status': True, }))
