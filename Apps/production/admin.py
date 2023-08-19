from django.contrib import admin

# Register your models here.
from .models import ProductionFluid

class confProduction(admin.ModelAdmin):
	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreated'
	DateCreatedFormat.short_description = 'Date Created' 
	list_display = ('PumpName','DateCreatedFormat','UserAuthor', 'OilProd','WaterProd')
	list_filter = ('PumpName',)
admin.site.register(ProductionFluid, confProduction)
