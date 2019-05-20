from django.contrib import admin

# Register your models here.
from django.contrib.admin import ModelAdmin

from book.models import Book, Author, Publish
class BookCfg(ModelAdmin):
    list_display = ('id', 'name', 'publish' )
    search_fields = ('name', 'id', )
    list_filter = ('name', 'price', 'id',)

admin.site.register(Book, BookCfg)
admin.site.register(Author)
admin.site.register(Publish)
print(admin.site._registry)