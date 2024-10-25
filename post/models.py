from django.db import models
from account.models import CustomUser
from django.utils.text import slugify
from .slug import generate_unique_slug
from tinymce.models import HTMLField
# Create your models here.

class Category(models.Model):
    title=models.CharField(max_length=150, unique=True)
    slug=models.SlugField(null=True, blank=True)
    created_date=models.DateField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.title
    
    def save(self,*args,**kwargs):
        self.slug=slugify(self.title)
        super().save(*args,**kwargs)
        


class Event(models.Model):
    user=models.ForeignKey(CustomUser,related_name='user_event',on_delete=models.CASCADE)
    category=models.ForeignKey(Category,related_name='category_event',on_delete=models.CASCADE)
    title=models.CharField(max_length=250)
    date=models.DateField()
    location=models.CharField(max_length=500)
    seat=models.IntegerField(default=0)
    slug=models.SlugField(null=True, blank=True)
    description=HTMLField()
    created_date=models.DateField(auto_now_add=True)
    booking=models.ManyToManyField(CustomUser, related_name='booking_events', blank=True)
    
    
    def __str__(self) -> str:
        return self.title
    
    def save(self,*args,**kwargs):
        updating = self.pk is not None
        
        if updating:
            self.slug = generate_unique_slug(self, self.title, update=True)
            super().save(*args, **kwargs)
        else:
            self.slug=generate_unique_slug(self,self.title)
            super().save(*args,**kwargs)
    
    
    # @property
    # def related(self):
    #     return self.category.category_blogs.all().exclude(pk=self.pk)