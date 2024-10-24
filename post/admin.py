from django.contrib import admin
from .models import *
# Register your models here.

class EventAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('title',)}
    
    
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('title',)}
    
    

    
admin.site.register(Category, CategoryAdmin)
admin.site.register(Event, EventAdmin)
