from django.contrib import admin

from perm import models


class PermissionCfg(admin.ModelAdmin):
    list_display = ["title", "url", "group", "action"]


admin.site.register(models.Permission, PermissionCfg)
admin.site.register(models.User)
admin.site.register(models.Role)
admin.site.register(models.PermissionGroup)
