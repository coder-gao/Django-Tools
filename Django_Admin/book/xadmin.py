#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/15 20:07
# @Author  : gao
# @File    : xadmin.py
from django.http import HttpResponse

from book.models import Book, Author, Publish
from xadmin.service import xadmin

from xadmin.service.xadmin import ModelXadmin


class BookCfg(ModelXadmin):
    list_display = ('id', 'name', 'price', 'author', 'publish', )
    search_fields = ('name', )
    list_filter = ('name', 'price', 'id', )

    def patch_del(self, request, queryset):
        print(queryset)
        queryset.update(price=123)

        return HttpResponse("批量初始化OK")

    patch_del.short_description = "批量初始化"

    actions = [patch_del, ]

class AuthorCfg(ModelXadmin):
    # list_display = ('id', 'name', 'tel')
    pass


xadmin.site.register(Book, BookCfg)
xadmin.site.register(Author, AuthorCfg)
xadmin.site.register(Publish)
print(xadmin.site._registry)
