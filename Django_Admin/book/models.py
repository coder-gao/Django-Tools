from django.db import models


# Create your models here.

class Book(models.Model):
    name = models.CharField(max_length=20, verbose_name='书名')
    price = models.CharField(max_length=10, verbose_name="价格", null=True, blank=True)

    author = models.ManyToManyField(to='Author', verbose_name='作者', null=True, blank=True)
    publish = models.ForeignKey(to='Publish', verbose_name='出版社', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '书籍'
        verbose_name_plural = verbose_name


class Publish(models.Model):
    name = models.CharField(max_length=20, verbose_name="出版社")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name ="出版社"
        verbose_name_plural=verbose_name

class Author(models.Model):
    name = models.CharField(max_length=20, verbose_name='作家')
    tel = models.CharField(max_length=11, verbose_name="电话", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '作者'
        verbose_name_plural = verbose_name


