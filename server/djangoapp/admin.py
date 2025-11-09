from django.contrib import admin
from .models import CarMake, CarModel # Import your models

# Register your models here.

# CarModelInline class
# This allows you to add/edit CarModels from the CarMake admin page
class CarModelInline(admin.StackedInline):
    model = CarModel
    extra = 1 # Number of extra blank forms to show

# CarModelAdmin class
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'make', 'car_type', 'year')
    list_filter = ['make', 'car_type', 'year']
    search_fields = ['name', 'make__name']

# CarMakeAdmin class with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline] # Add the CarModelInline here
    list_display = ('name', 'description')
    search_fields = ['name']

# Register models here
admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)