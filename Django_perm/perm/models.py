from django.db import models


class Permission(models.Model):
    """
    权限表
    """
    title = models.CharField(verbose_name='标题', max_length=32)
    url = models.CharField(verbose_name='含正则的URL', max_length=128)

    action = models.CharField(max_length=32, default="", verbose_name="动作", help_text="add, del, change等")
    group = models.ForeignKey("PermissionGroup", blank=True, null=True, verbose_name="权限组", on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "权限"
        verbose_name_plural = verbose_name


class PermissionGroup(models.Model):
    title = models.CharField(max_length=32, verbose_name="权限组名称")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "权限组"
        verbose_name_plural = verbose_name


class Role(models.Model):
    """
    角色
    """
    title = models.CharField(verbose_name='角色名称', max_length=32)
    permissions = models.ManyToManyField(verbose_name='拥有的所有权限', to='Permission', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "角色"
        verbose_name_plural = verbose_name


class User(models.Model):
    """
    用户表
    """
    name = models.CharField(verbose_name='用户名', max_length=32)
    password = models.CharField(verbose_name='密码', max_length=64)
    email = models.CharField(verbose_name='邮箱', max_length=32)
    roles = models.ManyToManyField(verbose_name='拥有的所有角色', to='Role', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name
