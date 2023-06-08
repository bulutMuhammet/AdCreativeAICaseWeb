from django.db import models

# Create your models here.
class ImageRequest(models.Model):
    original_image = models.ImageField(upload_to='original_image', blank=True, null=True, verbose_name="Orijinal Görsel")
    bg_removed_image = models.ImageField(upload_to='bg_removed_image', blank=True, null=True, verbose_name="Arka Planı Silinmiş Görsel")
    processed_image = models.ImageField(upload_to='processed_image', blank=True, null=True, verbose_name="İşlenmiş Görsel")
    background_image = models.ImageField(upload_to='background_image', blank=True, null=True, verbose_name="Arkaplan")
    is_transparent = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)

