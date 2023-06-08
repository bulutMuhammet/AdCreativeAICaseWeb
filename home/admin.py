from django.contrib import admin

# Register your models here.
from home.models import ImageRequest

@admin.register(ImageRequest)
class ImageRequestAdmin(admin.ModelAdmin):
    list_display = ('created_date', 'original_image', 'is_transparent')
    class Meta:
        model = ImageRequest


