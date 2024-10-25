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
from django.urls import reverse

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



class All_Events(generic.ListView):
    model = Event
    template_name = 'all_events.html'
    context_object_name = 'events'
    paginate_by = 4
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        page_obj = Custom_Paginator(self.request, self.get_queryset(), self.paginate_by)
        queryset = page_obj.get_queryset()
        paginator = page_obj.paginator
        
        context['events'] = queryset
        context['paginator'] = paginator
        context['current_path'] = self.request.path
        
        return context


class Event_details(generic.DetailView):
    model = Event
    template_name = 'event_details.html'
    context_object_name = 'E'
    slug_url_kwarg = 'slug'



class Category_details(generic.DetailView):
    model = Category
    template_name = 'category_details.html'
    slug_url_kwarg = 'slug'
    paginate_by = 4
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        category = self.get_object()
        category_event = category.category_event.all()
        
        page_obj = Custom_Paginator(self.request, category_event, self.paginate_by)
        queryset = page_obj.get_queryset()
        
        context['events'] = queryset
        context['paginator'] = page_obj.paginator
        context['page_obj'] = queryset
        context['is_paginated'] = queryset.has_other_pages()
        context['category_event'] = category_event
        
        return context


class Search_Events(generic.View):
    
    def get(self, *args, **kwargs):
        key = self.request.GET.get('key', '')
        date = self.request.GET.get('date', '')
        location = self.request.GET.get('location', '')

        # Base query
        event = Event.objects.all()

        # Apply filters based on the inputs
        if key:
            event = event.filter(
                Q(title__icontains=key) |
                Q(category__title__icontains=key) |
                Q(user__username__icontains=key)
            )
        
        if date:
            event = event.filter(date=date)  # Ensure date is in 'YYYY-MM-DD' format
        
        if location:
            event = event.filter(location__icontains=location)

        
        context = {
            'events': event,
            'key': key,
            'date': date,
            'location': location
        }

        return render(self.request, 'search_events.html', context)



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
        return reverse_lazy('event_details', kwargs={'slug': self.object.slug})


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


class UpdateEvent(LoginRequiredMixin, generic.UpdateView):
    model = Event
    form_class = AddEventForm
    template_name = 'update_event.html'
    login_url = 'login'
    
    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug')
        event = get_object_or_404(Event, slug=slug)
        
        # Ensure that only the event owner can update it
        if event.user != self.request.user:
            messages.error(self.request, "You don't have permission to edit this event.")
            return redirect('home')
        
        return event
    
    def form_valid(self, form):
        # Update the category
        category = get_object_or_404(Category, pk=self.request.POST['category'])
        form.instance.category = category
        
        # Success message and redirect to the event details page
        messages.success(self.request, "Event updated successfully")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.get_object()  # Pass the event instance to the template
        return context

    def get_success_url(self):
        return reverse('event_details', kwargs={'slug': self.object.slug})

    