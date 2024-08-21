from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile
from nested_admin import NestedModelAdmin, NestedTabularInline, NestedStackedInline
# Register your models here.




class UserProfileAdmin(NestedStackedInline):
    
    model = UserProfile
    extra = 1
    max_num = 1  
    can_delete = False  
    
    list_display = ['user', 'address_line_1', 'address_line_2', 'city', 'state', 'country',]




@admin.register(CustomUser)
class CustomUserAdmin(NestedModelAdmin):
    
    inlines = [UserProfileAdmin]
    
    list_display = ('id', 'email', 'first_name', 'last_name', 'last_login', 'date_joined', 'is_active',)
    list_display_links = ('email', 'first_name', 'last_name',)
    readonly_fields = ('last_login', 'date_joined',)
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

