from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from core import models


class UserAdmin(BaseUserAdmin):
    """
    User model administration
    """
    ordering = ['id']
    list_display = ['email', 'name', 'created_at', 'updated_at']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_cashier',
                    'is_manager',
                    'is_superuser'
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return False


class BaseAttrAdmin(ModelAdmin):
    """
    Base attributes administration
    """
    list_display = ['name', 'created_at', 'updated_at']

    def has_delete_permission(self, request, obj=None):
        return False


# Register
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Unit, BaseAttrAdmin)
admin.site.register(models.Category, BaseAttrAdmin)
admin.site.register(models.Product, BaseAttrAdmin)

admin.site.register(models.Supplier, BaseAttrAdmin)
admin.site.register(models.Customer, BaseAttrAdmin)
