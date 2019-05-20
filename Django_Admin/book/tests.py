
from django.test import TestCase

# Create your tests here.

# func = lambda x: x**x
#
# print(callable(func))
#
# class A:
#     pass
#
# print(A().__repr__())

# from django.core.paginator import Paginator
# from book.models import Author, Book
#
# data_list = Book.objects.all()
#
# p = Paginator(data_list, per_page=1)

# def func():
#     pass
#
# func.desc = "测试"
#
# print(func.__name__)
# print(func.desc)

# Q()
# from django.db.models import Q, Avg
# from book.models import Book, Author
#
# books = Book.objects.annotate(Avg("price"))
#
# set().intersection()


from book.models import *
from django import forms


class BookForm(forms.Form):
    name = forms.CharField()
    price = forms.CharField()
    author = forms.MultipleChoiceField()

book_form= BookForm()

for x in book_form:
    print(x)