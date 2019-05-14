from django import template

from perm.service.perm import reg

register = template.Library()


@register.simple_tag
def valid(link, request):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(link, "html.parser")
    print(soup.a.get('href'))
    path = soup.a.get('href')

    flag = reg(request, path)

    if flag:
        return link
    else:
        return ""


@register.inclusion_tag("perm/menu.html")
def get_menu(request, ):
    # 获取当前用户可以放到菜单栏中的权限
    menu_permission_list = request.session["menu_permission_list"]

    return {"menu_permission_list": menu_permission_list}
