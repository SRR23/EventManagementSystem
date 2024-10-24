from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from account.models import CustomUser
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator, InvalidPage
from django.db.models import Q
from .models import *
from .forms import AddEventForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

class Custom_Paginator:
    def __init__(self, request, queryset, paginated_by):
        self.paginator = Paginator(queryset, paginated_by)
        self.paginated_by = paginated_by
        self.queryset = queryset
        self.page = request.GET.get('page', 1)
        
    def get_queryset(self):
        try:
            queryset = self.paginator.page(self.page)
        except PageNotAnInteger:
            queryset = self.paginator.page(1)
        except EmptyPage:
            queryset = self.paginator.page(1)
        except InvalidPage:
            queryset = self.paginator.page(1)
        
        return queryset


class Home(generic.TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                
                'events': Event.objects.order_by('-created_date'),
                
            }
        )
        
        context['current_path'] = self.request.path
        
        return context



class AddEvent(LoginRequiredMixin, generic.CreateView):
    model = Event
    form_class = AddEventForm
    template_name = 'add_event.html'
    login_url = 'login'

    def form_valid(self, form):
        # Handle tags and the user/category assignment
        
        user = get_object_or_404(CustomUser, pk=self.request.user.pk)
        category = get_object_or_404(Category, pk=self.request.POST.get('category'))
        
        event = form.save(commit=False)
        event.user = user
        event.category = category
        event.save()

        
        messages.success(self.request, "Event added successfully")
        return super().form_valid(form)


    def get_success_url(self):
        # Redirect to the blog details page after successful submission
        return reverse_lazy('my_event')


class MyEvents(LoginRequiredMixin, generic.ListView):
    model = Event
    template_name = 'my_events.html'
    paginate_by = 6
    login_url = 'login'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        userevent = self.request.user.user_event.all()
        page_obj = Custom_Paginator(self.request, userevent, self.paginate_by)
        queryset = page_obj.get_queryset()

        context['events'] = queryset
        context['paginator'] = page_obj.paginator
        context['page_obj'] = queryset
        context['is_paginated'] = queryset.has_other_pages()
        
        return context

    def dispatch(self, request, *args, **kwargs):
        delete = request.GET.get('delete', None)

        if delete:
            event = get_object_or_404(Event, pk=delete)

            if request.user.pk != event.user.pk:
                return redirect('home')

            event.delete()
            messages.success(request, "Your event has been deleted!")
            return redirect('my_event')

        return super().dispatch(request, *args, **kwargs)


def add_booking(request, id):
    event = get_object_or_404(Event, id=id)

    if request.user.is_authenticated:
        # Using Favorite model (for separate favorites list)
        if event.booking.filter(id=request.user.id).exists():
            # Already favorited, so do nothing (or display a message)
            messages.info(request, "You have already booked this event.")
        else:
            event.booking.add(request.user)
            messages.success(request, "Event added to booking list") 
    else:
        # User not authenticated, consider redirecting to login
        messages.warning(request, "Please login to add booking!!") 
        return redirect('login')

    return redirect('booking_list')


class Booking_list(LoginRequiredMixin, generic.ListView):
    model = Event
    template_name = 'my_booking.html'
    paginate_by = 6
    login_url = 'login'
    
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        booking_events = self.request.user.booking_events.all()
        page_obj = Custom_Paginator(self.request, booking_events, self.paginate_by)
        queryset = page_obj.get_queryset()
        
        # Add a flag for each event to indicate if it's booked
        booked_event_ids = self.request.user.booking_events.values_list('id', flat=True)
        for event in queryset:
            event.is_booked = event.id in booked_event_ids
            print(f"Event {event.id} is_booked: {event.is_booked}")

        context['events'] = queryset
        context['paginator'] = page_obj.paginator
        context['page_obj'] = queryset
        context['is_paginated'] = queryset.has_other_pages()
        
        return context
    

    def dispatch(self, request, *args, **kwargs):
        delete = request.GET.get('delete', None)

        if delete:
            event = get_object_or_404(Event, pk=delete)

            if event in request.user.booking_events.all():
                request.user.booking_events.remove(event)
                messages.success(request, "Event has been removed from your booking!")
            else:
                messages.error(request, "Event not found in your booking!")

            return redirect('booking_list')

        return super().dispatch(request, *args, **kwargs)

    