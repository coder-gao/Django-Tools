#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/15 20:08
# @Author  : gao
# @File    : xadmin.py
from django.db.models import ManyToManyField
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.forms import modelform_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import path, include, reverse
from django.utils.safestring import mark_safe


class ShowList(object):
    def __init__(self, config, data_list, request):
        self.config = config
        self.data_list = data_list
        self.request = request

        # 分页
        data_count = self.data_list.count()
        current_page = int(self.request.GET.get("page", 1))
        base_path = self.request.path

        self.pagination = Paginator(self.data_list, per_page=15, request=request)
        self.page_data = self.pagination.page(current_page)

        # actions
        self.actions = self.config.actions  # [patch_init,]

    def get_filter_linktags(self):
        print("list_filter:", self.config.list_filter)
        link_dic = {}
        import copy

        for filter_field in self.config.list_filter:
            params = copy.deepcopy(self.request.GET)
            cid = self.request.GET.get(filter_field, 0)

            print("filter_field", filter_field)
            filter_field_obj = self.config.model._meta.get_field(filter_field)
            print("filter_field_obj", filter_field_obj)
            print(type(filter_field_obj))
            from django.db.models.fields.related import ForeignKey
            from django.db.models.fields.related import ManyToManyField
            # print("rel...",filter_field_obj.rel.to.objects.all())

            if isinstance(filter_field_obj, ForeignKey) or isinstance(filter_field_obj, ManyToManyField):
                data_list = filter_field_obj.rel.to.objects.all()  # 【publish1,publish2...】
            else:
                data_list = self.config.model.objects.all().values("pk", filter_field)
                print("data_list", data_list)

            temp = []
            # 处理 全部标签
            if params.get(filter_field):
                del params[filter_field]
                temp.append("<a href='?%s'>全部</a>" % params.urlencode())
            else:
                temp.append("<a  class='active' href='#'>全部</a>")

            # 处理 数据标签
            for obj in data_list:
                if isinstance(filter_field_obj, ForeignKey) or isinstance(filter_field_obj, ManyToManyField):
                    pk = obj.pk
                    text = str(obj)
                    params[filter_field] = pk
                else:  # data_list= [{"pk":1,"title":"go"},....]
                    print("========")
                    pk = obj.get("pk")
                    text = obj.get(filter_field)
                    params[filter_field] = text

                _url = params.urlencode()
                if cid == str(pk) or cid == text:
                    link_tag = "<a class='active' href='?%s'>%s</a>" % (
                        _url, text)
                else:
                    link_tag = "<a href='?%s'>%s</a>" % (_url, text)
                temp.append(link_tag)

            link_dic[self.config.model._meta.get_field(filter_field).verbose_name.upper()] = temp

        return link_dic

    def get_action_list(self):
        temp = []
        for action in self.actions:
            temp.append({
                "name": action.__name__,
                "desc": action.short_description
            })  # [{"name":""patch_init,"desc":"批量初始化"}]

        return temp

    def get_header(self):
        # 构建表头
        header_list = []
        # print("header", self.config.new_list_play())

        for field in self.config.new_list_play():

            if callable(field):
                # header_list.append(field.__name__)
                val = field(self.config, header=True)
                header_list.append(val)

            else:
                if field == "__str__":
                    header_list.append(self.config.model._meta.verbose_name.title())
                else:
                    # header_list.append(field)
                    val = self.config.model._meta.get_field(field).verbose_name
                    header_list.append(val)

        return header_list

    def get_body(self):

        new_data_list = []
        for obj in self.page_data.object_list:
            temp = []
            for filed in self.config.new_list_play():

                if callable(filed):
                    val = filed(self.config, obj)
                else:
                    try:
                        field_obj = self.config.model._meta.get_field(filed)
                        if isinstance(field_obj, ManyToManyField):
                            ret = getattr(obj, filed).all()
                            t = []
                            for mobj in ret:
                                t.append(str(mobj))
                            val = ",".join(t)
                        else:
                            val = getattr(obj, filed)
                            if filed in self.config.list_display_links:
                                # "app01/userinfo/(\d+)/change"
                                _url = self.config.get_change_url(obj)

                                val = mark_safe("<a href='%s'>%s</a>" % (_url, val))

                    except Exception as e:
                        val = getattr(obj, filed)

                temp.append(val)

            new_data_list.append(temp)

        return new_data_list


class ModelXadmin(object):
    list_display = ("__str__",)
    list_display_links = ()
    modelform_class = None
    search_fields = ()
    list_filter = ()

    actions = []

    def __init__(self, model, site):
        self.model = model
        self.site = site
        self.actions.append(self.queryset_del)

    def add(self, request):

        return HttpResponse("add")

    def delete(self, request, object_id):
        return HttpResponse("delete")

    def change(self, request, object_id):
        return HttpResponse("change")

    # 删除 编辑，复选框
    def edit(self, obj=None, header=False):
        if header:
            return "操作"
        # return mark_safe("<a href='%s/change'>编辑</a>"%obj.pk)
        _url = self.get_change_url(obj)
        # print("_url", _url)
        return mark_safe("<a href='%s'>编辑</a>" % _url)

    def deletes(self, obj=None, header=False):
        if header:
            return "操作"
        # return mark_safe("<a href='%s/change'>编辑</a>"%obj.pk)
        _url = self.get_delete_url(obj)
        return mark_safe("<a href='%s'>删除</a>" % _url)

    def checkbox(self, obj=None, header=False):
        if header:
            return mark_safe('<input id="choice" type="checkbox">')

        return mark_safe('<input class="choice_item" type="checkbox" name="selected_pk" value="%s">' % obj.pk)

    def new_list_play(self):
        temp = []
        temp.append(ModelXadmin.checkbox)
        temp.extend(self.list_display)
        if not self.list_display_links:
            temp.append(ModelXadmin.edit)
        temp.append(ModelXadmin.deletes)
        return temp

    def add_view(self, request):
        ModelFormDemo = modelform_factory(self.model, fields='__all__')
        form = ModelFormDemo()

        for bfield in form:
            # from django.forms.boundfield import BoundField
            print(bfield.field)  # 字段对象
            print("name", bfield.name)  # 字段名（字符串）
            print(type(bfield.field))  # 字段类型
            from django.forms.models import ModelChoiceField
            if isinstance(bfield.field, ModelChoiceField):
                bfield.is_pop = True

                print("=======>", bfield.field.queryset.model)  # 一对多或者多对多字段的关联模型表

                related_model_name = bfield.field.queryset.model._meta.model_name
                related_app_label = bfield.field.queryset.model._meta.app_label

                _url = reverse("xadmin:%s_%s_add" % (related_app_label, related_model_name))
                bfield.url = _url + "?pop_res_id=id_%s" % bfield.name

        if request.method == "POST":
            form = ModelFormDemo(request.POST)
            if form.is_valid():
                obj = form.save()
                pop_res_id = request.GET.get("pop_res_id")
                if pop_res_id:
                    res = {"pk": obj.pk, "text": str(obj), "pop_res_id": pop_res_id}
                    import json
                    return render(request, "pop.html", {"res": res})
                else:
                    return redirect(self.get_list_url())
            return render(request, "add_view.html", locals())
        return render(request, "add_view.html", locals())

    def delete_view(self, request, object_id):
        url = self.get_list_url()
        if request.method == "POST":
            self.model.objects.filter(pk=object_id).delete()
            return redirect(url)

        return render(request, "delete_view.html", locals())

    def change_view(self, request, object_id):
        ModelFormDemo = modelform_factory(self.model, fields='__all__')
        edit_obj = self.model.objects.filter(pk=object_id).first()

        form = ModelFormDemo(instance=edit_obj)

        for bfield in form:
            # from django.forms.boundfield import BoundField
            print(bfield.field)  # 字段对象
            print("name", bfield.name)  # 字段名（字符串）
            print(type(bfield.field))  # 字段类型
            from django.forms.models import ModelChoiceField
            if isinstance(bfield.field, ModelChoiceField):
                bfield.is_pop = True

                print("=======>", bfield.field.queryset.model)  # 一对多或者多对多字段的关联模型表

                related_model_name = bfield.field.queryset.model._meta.model_name
                related_app_label = bfield.field.queryset.model._meta.app_label

                _url = reverse("xadmin:%s_%s_add" % (related_app_label, related_model_name))
                bfield.url = _url + "?pop_res_id=id_%s" % bfield.name

        if request.method == "POST":
            form = ModelFormDemo(request.POST, instance=edit_obj)
            if form.is_valid():
                obj = form.save()
                pop_res_id = request.GET.get("pop_res_id")
                if pop_res_id:
                    res = {"pk": obj.pk, "text": str(obj), "pop_res_id": pop_res_id}
                    import json
                    return render(request, "pop.html", {"res": res})
                else:
                    return redirect(self.get_list_url())

            return render(request, "change_view.html", locals())


        return render(request, "change_view.html", locals())

    def queryset_del(self, request, queryset):
        queryset.delete()
        url = request.path
        return redirect(url)

    queryset_del.short_description = '批量删除'

    def get_serach_conditon(self, request):
        key_word = request.GET.get("q", "")
        self.key_word = key_word
        from django.db.models import Q
        search_connection = Q()
        if key_word:
            # self.search_fields # ["title","price"]
            search_connection.connector = "or"
            for search_field in self.search_fields:
                search_connection.children.append((search_field + "__contains", key_word))
        return search_connection

    def get_filter_condition(self, request):
        from django.db.models import Q
        filter_condition = Q()

        for filter_field, val in request.GET.items():
            if filter_field in self.list_filter:
                filter_condition.children.append((filter_field, val))

        return filter_condition

    def list_view(self, request):
        print(self.model)
        print("list_dispaly", self.list_display)

        if request.method == "POST":  # action
            print("POST:", request.POST)
            action = request.POST.get("action")
            selected_pk = request.POST.getlist("selected_pk")
            action_func = getattr(self, action)
            queryset = self.model.objects.filter(pk__in=selected_pk)
            ret = action_func(request, queryset)

            return ret

        # 获取serach的Q对象
        search_connection = self.get_serach_conditon(request)

        filter_condition = self.get_filter_condition(request)

        # 筛选获取当前表所有数据
        data_list = self.model.objects.all().filter(search_connection).filter(filter_condition)

        showlist = ShowList(self, data_list, request)
        # header_list = showlist.get_header()
        # new_data_list = showlist.get_body()
        #
        # page_data_list = showlist.page_data

        # 构建一个添加数据的URL
        add_url = self.get_add_url()
        return render(request, "list_view.html", locals())

    def get_change_url(self, obj):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("xadmin:%s_%s_change" % (app_label, model_name), args=(obj.pk,))

        return _url

    def get_delete_url(self, obj):
        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("xadmin:%s_%s_delete" % (app_label, model_name), args=(obj.pk,))

        return _url

    def get_add_url(self):

        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("xadmin:%s_%s_add" % (app_label, model_name))

        return _url

    def get_list_url(self):

        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        _url = reverse("xadmin:%s_%s_list" % (app_label, model_name))

        return _url

    def get_urls(self):

        temp = []

        model_name = self.model._meta.model_name
        app_label = self.model._meta.app_label

        temp.append(path("add/", self.add_view, name="%s_%s_add" % (app_label, model_name)))
        temp.append(path("<path:object_id>/delete/", self.delete_view, name="%s_%s_delete" % (app_label, model_name)))
        temp.append(path("<path:object_id>/change/", self.change_view, name="%s_%s_change" % (app_label, model_name)))
        temp.append(path("", self.list_view, name="%s_%s_list" % (app_label, model_name)))

        return temp

    @property
    def urls(self):
        return self.get_urls()

    def get_list_display_links(self, request, list_display):
        """
        Return a sequence containing the fields to be displayed as links
        on the changelist. The list_display parameter is the list of fields
        returned by get_list_display().
        """
        if self.list_display_links or self.list_display_links is None or not list_display:
            return self.list_display_links
        else:
            # Use only the first item in list_display as link
            return list(list_display)[:1]


class XadminSite(object):
    def __init__(self, name="xadmin"):
        self._registry = {}
        self.name = name

    def register(self, model, xadmin_class=None):
        if not xadmin_class:
            xadmin_class = ModelXadmin

        self._registry[model] = xadmin_class(model, self)

    def get_urls(self):
        temp = []
        for model, xadmin_class_obj in self._registry.items():
            model_name = model._meta.model_name
            app_label = model._meta.app_label
            # 分发增删改查
            temp.append(path("%s/%s/" % (app_label, model_name), include(xadmin_class_obj.urls)))
        return temp

    @property
    def urls(self):
        return self.get_urls(), 'xadmin', self.name


site = XadminSite()
