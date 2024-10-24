from django.db.models import Count
from .models import Category

def categories(request):
    categories_with_counts = Category.objects.annotate(blogs_count=Count('category_event'))
    return {"categories": categories_with_counts}