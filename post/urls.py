from django.urls import path
from .views import *
urlpatterns = [
    path('', Home.as_view(), name="home"),
    # path('all_blogs/',All_Blogs.as_view(),name='all_blogs'),
    # path('blog_details/<str:slug>/', Blog_details.as_view(), name='blog_details'),
    # path('category_blogs/<str:slug>/', Category_details.as_view(), name="category_blogs"),
    # path('tag_blogs/<str:slug>/', Tag_details.as_view(), name='tag_blogs'),
    # path('search_blogs/', Search_Blogs.as_view(), name='search_blogs'),
    path('add_event/', AddEvent.as_view(), name='add_event'),
    path('my_events/', MyEvents.as_view(), name='my_event'),
    # path('update_blog/<str:slug>/', UpdateBlog.as_view(), name='update_blog'),
    path('add_booking/<int:id>/', add_booking, name="add_booking"),
    path('booking_list/', Booking_list.as_view(), name="booking_list"),
]