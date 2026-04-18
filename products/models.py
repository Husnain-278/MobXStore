from django.db import models
from django.utils.text import slugify
from django.db.models import Q
from cloudinary.models import CloudinaryField
from accounts.models import User
# Create your models here.

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(unique=True, db_index=True, blank=True)
    logo = CloudinaryField(blank=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, db_index=True)
    
    def __str__(self):
        return self.name 
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    

class Mobile(models.Model):
    name = models.CharField(max_length=200)
    primary_image = CloudinaryField()
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    stock = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.name
    class Meta:
       indexes = [
         models.Index(fields=['slug']),
         models.Index(fields=['price']),
         models.Index(fields=['created_at']),
         ]
       
    def save(self, *args, **kwargs):
      if not self.slug:
        self.slug = slugify(self.name)
      super().save(*args, **kwargs)
    


class Specification(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class MobileSpecification(models.Model):
    mobile = models.ForeignKey(Mobile, on_delete=models.CASCADE, related_name='specs')
    specification = models.ForeignKey(Specification, on_delete=models.CASCADE  )
    value = models.CharField(max_length=190 )

    class Meta:
        unique_together = ['mobile', 'specification']
        indexes = [
            models.Index(fields=['mobile']),
            models.Index(fields=['specification']),
        ]

    def __str__(self):
        return f"{self.mobile.name} - {self.specification.name} - { self.value}"



class MobileImage(models.Model):
    mobile = models.ForeignKey(Mobile, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField()
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return self.mobile.name
    
    class Meta:
      constraints = [
        models.UniqueConstraint(
            fields=['mobile'],
            condition=Q(is_primary=True),
            name='unique_primary_image_per_mobile'
        )
      ]
      indexes = [
        models.Index(fields=['mobile']),
      ]




#Review Model
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Mobile, on_delete=models.CASCADE, related_name='reviews')

    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']  # still important

    def __str__(self):
        return f"{self.user} - {self.product} ({self.rating})"