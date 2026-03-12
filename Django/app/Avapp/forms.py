from django import forms
from .models import Host
from django.db import models
from django.db.models import Func


class JsonExtract(Func):
    function = 'jsonb_extract_path_text'
    output_field = models.TextField()

class MyForm(forms.Form):
    data_choices = forms.ModelChoiceField(queryset=Host.objects.all())


class DataForm(forms.Form):
    data = forms.ModelMultipleChoiceField(queryset=Host.objects.all())



class HostFilterForm(forms.Form):
    # Define the choices for the dropdown list
    FILTER_CHOICES = [
        ('idhost', 'idHost'),
        ('tag', 'Tag'),
        ('sex', 'Sex'),
        # Add more choices for other fields as needed
    ]

    # Define the fields for the form
    filter_field = forms.ChoiceField(choices=FILTER_CHOICES)
    filter_value = forms.CharField(max_length=100)

    def filter_hosts(self):
        # Get the selected filter field and value from the form data
        filter_field = self.cleaned_data['filter_field']
        filter_value = self.cleaned_data['filter_value']

        # Filter the hosts queryset based on the selected field and value
        if filter_field == 'idhost':
            hosts = Host.objects.filter(idhost__icontains=filter_value)
        elif filter_field == 'tag':
            hosts = Host.objects.filter(tag=int(filter_value))
        elif filter_field == 'sex':
            hosts = Host.objects.filter(sex=filter_value)
        # Add more cases for other fields as needed
        else:
            hosts = Host.objects.none()

        return hosts
