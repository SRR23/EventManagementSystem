from django.urls import path
from .views import *
urlpatterns = [
    path('', Home.as_view(), name="home"),
    path('all_events/',All_Events.as_view(),name='all_events'),
    path('event_details/<str:slug>/', Event_details.as_view(), name='event_details'),
    path('category_events/<str:slug>/', Category_details.as_view(), name="category_events"),
    # path('tag_blogs/<str:slug>/', Tag_details.as_view(), name='tag_blogs'),
    path('search_events/', Search_Events.as_view(), name='search_events'),
    path('add_event/', AddEvent.as_view(), name='add_event'),
    path('my_events/', MyEvents.as_view(), name='my_event'),
    path('update_event/<str:slug>/', UpdateEvent.as_view(), name='update_event'),
    path('add_booking/<int:id>/', add_booking, name="add_booking"),
    path('booking_list/', Booking_list.as_view(), name="booking_list"),
]