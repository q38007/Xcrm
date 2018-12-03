from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout


# Create your views here.

def acc_login(request):
    err_msg = ""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # 1.验证, 返回认证对象 or None
        user_obj = authenticate(username=username, password=password)
        print('request.user-----', type(user_obj), user_obj)
        print('request.path-----', request.path)
        if user_obj:
            # 2.登录, login与db交互创建session, 前端通过request.user获取当前用户对象
            login(request, user_obj)

            # 用户未认证访问, @login_required会返回带有next参数
            # 默认会跳转到‘/accounts/login/’, 可以在settings文件中通过LOGIN_URL来设定
            # http://127.0.0.1:8000/login/?next=/<appname>/
            return redirect(request.GET.get('next', '/crm/'))    # url path
            # http://127.0.0.1:8000/crm
        else:
            err_msg = "Wrong username or password!"

    return render(request, 'login.html', {'err_msg': err_msg})  # file path


def acc_logout(request):
    logout(request)  # 清空session
    return redirect('/login')   # url path
