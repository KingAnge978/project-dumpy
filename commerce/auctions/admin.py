from django.contrib import admin
from .models import Category, Listing, Bid, Comment

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)} 
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:  
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)
