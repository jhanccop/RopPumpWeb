from django.contrib import admin
from .models import well

class configWell(admin.ModelAdmin):
	def DateCreatedFormat(self, obj):
		return obj.DateCreate.strftime("%Y-%m-%d %H:%M:%S")
	DateCreatedFormat.admin_order_field = 'DateCreated'
	DateCreatedFormat.short_description = 'Date Created'
	list_display = ('id','PumpName',"FieldName",'GroupName','PumpType','DateCreatedFormat','UserAuthor')
	list_filter = ( 'FieldName', 'PumpType','UserAuthor')

admin.site.register(well, configWell)
