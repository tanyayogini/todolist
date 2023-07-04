from django.contrib import admin

from core.models import User


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    exclude = ['password']
    list_display = ('username', 'email', 'first_name', 'last_name',)
    list_filter = ('is_staff', 'is_active', 'is_superuser',)
    search_fields = ('username', 'first_name', 'last_name',)
    readonly_fields = ('last_login', 'date_joined',)


#admin.site.register(User)

