from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from perm.models import Role, User


class Per(object):
    def __init__(self,actions):
        self.actions=actions
    def add(self):
        return "add" in self.actions
    def delete(self):
        return "del" in self.actions
    def edit(self):
        return "change" in self.actions
    def list(self):
        return "list" in self.actions

def users(request):
    user_list = User.objects.all()
    # permission_list = request.session.get("permission_list")
    id = request.session.get("user_id")
    user = User.objects.filter(id=id).first()

    per = Per(request.actions)
    return render(request, "perm/users.html", locals())


def add_user(request):

    return HttpResponse("add user.....")


def roles(request):
    role_list = Role.objects.all()
    per = Per(request.actions)
    return render(request, "perm/roles.html", locals())


from perm.service.permissions import *


def login(request):
    if request.method == "POST":

        user = request.POST.get("user")
        pwd = request.POST.get("pwd")

        user = User.objects.filter(name=user, password=pwd).first()
        if user:
            ############################### 在session中注册用户ID######################
            request.session["user_id"] = user.pk

            ###############################在session注册权限列表##############################

            # 查询当前登录用户的所有角色
            # ret=user.roles.all()
            # print(ret)# <QuerySet [<Role: 保洁>, <Role: 销售>]>

            # 查询当前登录用户的所有权限
            initial_session(user, request)

            return HttpResponse("登录成功！")

    return render(request, "login.html")
