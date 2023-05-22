#from django.db import models
#from category.models import Category
#from django.urls import reverse

# Create your models here.

#class Product(models.Model):
#    product_name  = models.CharField(max_length=200, unique=True)
#    slug          = models.SlugField(max_length=200, unique=True)
#    description   = models.TextField(max_length=500, blank=True)
#    price         = models.IntegerField()
#    images        = models.ImageField(upload_to='photos/products')
#    stock         = models.IntegerField()
#    is_available  = models.BooleanField(default=True)
#    category      = models.ForeignKey(Category, on_delete=models.CASCADE)
#    created_date  = models.DateTimeField(auto_now_add=True)
#    modified_date = models.DateTimeField(auto_now=True)

#    def get_url(self):
#        return reverse('product_detail', args=[self.category.slug, self.slug])

#    def __str__(self):
#        return self.product_name
from django.db import models
from category.models import Category
from django.urls import reverse
from django import forms
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from PIL import Image

MAX_IMAGE_SIZE = 2 * 1024 * 1024  # Maximum file size: 2MB


def validate_image_size(image):
    file_size = image.size
    if file_size > MAX_IMAGE_SIZE:
        raise ValidationError('The image file size should be less than 2MB.')


def validate_image_extension(image):
    allowed_extensions = ['jpg', 'jpeg', 'png']
    extension = image.name.split('.')[-1].lower()
    if extension not in allowed_extensions:
        raise ValidationError('Only JPEG, JPG, and PNG files are allowed.')


class PriceFormField(forms.DecimalField):
    def to_python(self, value):
        if isinstance(value, str):
            value = value.replace(',', '')  # Remove commas from the input
        return super().to_python(value)


class PriceWidget(forms.TextInput):
    def format_value(self, value):
        if isinstance(value, str):
            try:
                value = float(value.replace(',', ''))  # Remove commas and convert to float
            except ValueError:
                value = ''
        return super().format_value(value)


class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    images = models.ImageField(upload_to='photos/products')
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

    def get_form(self, **kwargs):
        form = super().get_form(**kwargs)
        form.base_fields['price'] = forms.DecimalField(widget=PriceWidget)
        return form

    def save(self, *args, **kwargs):
        if self.images:
            validate_image_extension(self.images)
            validate_image_size(self.images)
        super().save(*args, **kwargs)
