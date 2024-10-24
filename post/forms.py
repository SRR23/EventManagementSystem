from django import forms

from .models import Event
from tinymce.models import HTMLField

class TextForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, required=True)
    


class AddEventForm(forms.ModelForm):
    description = HTMLField()
    
    class Meta:
        model = Event
        fields = (
            "title",
            "category",
            "date",
            "location",
            "description"
        )