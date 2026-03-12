import csv
import os
import re
from django.conf import settings  # Import settings
import itertools
from django.templatetags.static import static
import urllib
import plotly.express as px
import plotly.io as pio
import io
import base64
from cmath import pi
import json
import pandas
from bokeh.layouts import gridplot
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.core import serializers
from django.shortcuts import render, get_object_or_404, redirect
# Create your views here.
from django.http import HttpResponse
from Avapp.models import Analysis, Feature, Pen, PenHasFeature, Host, Sample, Study, Abundancefacttable, Taxons
from django.template import loader
from django.db.models import Prefetch
import matplotlib
from django.utils.baseconv import base64

from django.http.response import HttpResponseNotAllowed, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from rest_framework.decorators import authentication_classes

from django.views.decorators.http import require_POST

matplotlib.use('TkAgg')  # or 'QtAgg', or another backend that supports GUIs
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from bokeh.transform import dodge
import io
import plotly.graph_objs as go
from django.shortcuts import render
import plotly.offline as opy
import base64
import pandas as pd
from scipy.stats import ttest_ind
from .forms import MyForm, DataForm, HostFilterForm, JsonExtract
import numpy as np
import ipywidgets as widgets
from ipywidgets import interact, interactive, fixed, interact_manual
from IPython.display import display
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from bokeh.plotting import figure, show
from bokeh.embed import components
from django import template
from bokeh.resources import CDN
from bokeh.palettes import Category10, Category10_10, Viridis256, YlGnBu, RdYlBu, Magma256, Category20, Category20b, \
    Category20c
from django.shortcuts import render
from bokeh.embed import components
from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, HoverTool, Range1d, WheelZoomTool, DataRange1d, BoxZoomTool, PanTool
import seaborn as sns
from bokeh.embed import file_html
from numpy import mean, cumsum
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.models import ColorBar
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral6
from bokeh.transform import linear_cmap
from bokeh.models import LinearColorMapper
from bokeh.io import output_notebook

register = template.Library()

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
import subprocess
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token
from .models import Featurefacttable, Host, Feature
from django.shortcuts import render
from django.http import HttpResponseRedirect
import random
import string
import logging

@require_POST
@csrf_exempt
def django_shiny_login(request):
    # Retrieve the username and password from the request
    username = request.POST.get('username')
    password = request.POST.get('password')

    # Example debug print statements
    print("Received username:", username)
    print("Received password:", password)

    # Authenticate the user
    user = authenticate(request, username=username, password=password)
    print("Users matching condition:", user)

    if user is not None:
        # Login the user (optional, but recommended)
        login(request, user)

        # Generate and return a unique token for the authenticated user
        token, created = Token.objects.get_or_create(user=user)
        return JsonResponse({'token': token.key, 'status': 'success'})
    else:
        # Invalid login credentials
        return JsonResponse({'status': 'error', 'message': 'Invalid login credentials'})


@require_POST
@csrf_exempt
def validate_shiny_token(request):
    try:
        # Retrieve the username and token from the request
        username = request.POST.get('username')
        token_value = request.POST.get('token')

        # Ensure the user has a valid token
        if username and token_value and Token.objects.filter(user__username=username, key=token_value).exists():
            # Token is valid
            return JsonResponse({'status': 'valid'})
        else:
            # Token is not valid
            return JsonResponse({'status': 'invalid'})
    except Exception as e:
        # Handle exceptions (e.g., KeyError, AttributeError) as needed
        return JsonResponse({'status': 'error', 'message': str(e)})


def validate_token(request):
    if request.method == 'POST':
        token_value = request.POST.get('token')

        if token_value:
            try:
                token = Token.objects.get(key=token_value)
                user = authenticate(request, username=token.user.username)
                if user:
                    return JsonResponse({'status': 'valid'})
            except Token.DoesNotExist:
                pass

        return JsonResponse({'status': 'invalid'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def generate_session_key(request):
    characters = string.ascii_letters + string.digits
    session_key = ''.join(random.choice(characters) for i in range(32))

    refresh = RefreshToken.for_user(request.user)
    access_token = str(refresh.access_token)

    return JsonResponse({'session_key': session_key, 'access_token': access_token})



@login_required
@csrf_exempt
def generate_token(request):
    token, created = Token.objects.get_or_create(user=request.user)
    return JsonResponse({'token': token.key})


# def get_session_key(request):
#     session_key = generate_session_key()
#     return JsonResponse({'session_key': session_key})
@login_required
def streamlit_view(request):
    process = subprocess.Popen(
        ['streamlit', 'run', '/home/reda/Aviwell/Django/app/start_streamlit.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    # Capture the output and errors (if any)
    output, errors = process.communicate()
    # You can return the output or errors to the client if needed
    return HttpResponse(output)

@login_required
def dashboard(request):
    # Your code for the dashboard view goes here
    return render(request, 'avapp.html')

@login_required
def shiny_dashboard(request):
    # Your code for the dashboard view goes here
    return render(request, 'shiny_dashboard.html')

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('host')  # Redirect to dashboard for authenticated users
        else:
            error_message = 'Invalid login credentials. Please try again.'
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')


def custom_logout(request):
    logout(request)
    request.session.pop('session_key', None)  # Remove the session key
    return redirect('index')

@register.filter
def split_taxonomy(taxonomy_string):
    taxonomy_list = taxonomy_string.split(";")
    return {
        'domain': taxonomy_list[0],
        'phylum': taxonomy_list[1],
        'class': taxonomy_list[2],
        'order': taxonomy_list[3],
        'family': taxonomy_list[4],
        'genus': taxonomy_list[5],
        'species': taxonomy_list[6]
    }


@register.filter
def unique_taxonomies(taxonomies):
    seen_taxonomies = set()
    unique_list = []

    for taxonomy in taxonomies:
        if taxonomy not in seen_taxonomies:
            unique_list.append(taxonomy)
            seen_taxonomies.add(taxonomy)

    return unique_list


@login_required
def host_filter_view(request):
    # Get the selected filter values from the request.GET dictionary
    sex_filter = request.GET.get('sex')
    study_filter = request.GET.get('study')
    birdweight_d0 = request.GET.get('birdweight_d0')
    birdweight_d9 = request.GET.get('birdweight_d9')
    birdweight_d21 = request.GET.get('birdweight_d21')
    birdweight_d35 = request.GET.get('birdweight_d35')

    # Filter the host queryset based on the selected filter values
    hosts = Host.objects.all()
    if sex_filter:
        hosts = hosts.filter(sex=sex_filter)
    if study_filter:
        hosts = hosts.filter(study_idstudy=study_filter)
    if birdweight_d0:
        hosts = Host.objects.annotate(
            birdweight_d0=KeyTextTransform('BirdWeight_D0', 'weight')
        ).filter(birdweight_d0__gt=birdweight_d0)
    if birdweight_d9:
        hosts = Host.objects.annotate(
            birdweight_d9=KeyTextTransform('BirdWeight_D9', 'weight')
        ).filter(birdweight_d9__gt=birdweight_d9)
    if birdweight_d21:
        hosts = Host.objects.annotate(
            birdweight_d21=KeyTextTransform('birdweight_D21', 'weight')
        ).filter(birdweight_d21__gt=birdweight_d21)
    if birdweight_d35:
        hosts = Host.objects.annotate(
            birdweight_d35=KeyTextTransform('BirdWeight_D35', 'weight')
        ).filter(birdweight_d35__gt=birdweight_d35)

    # Render the template with the filtered hosts
    context = {'dataHost': hosts, 'lenhost': len(hosts)}
    return render(request, 'host.html', context)


@login_required
def analysis_data(request):
    selected_hosts = request.GET.getlist('selected_hosts')

    # Interesssssaaannnttt todo
    samples = Sample.objects.filter(host_idhost__in=selected_hosts).select_related('host_idhost')
    samples = Sample.objects.filter(host_idhost__in=selected_hosts).select_related('host_idhost')
    # Get the abundance and related
    # abundance_facts = Abundancefacttable.objects.select_related('sample_idsample__host_idhost', 'item_iditem', 'omics_idomics').\
    #     filter(sample_idsample__host_idhost__in=selected_hosts).select_related('item__taxons')

    # abundance_facts = Abundancefacttable.objects.select_related('sample_idsample__host_idhost', 'item_iditem', 'omics_idomics').filter(
    #     sample_idsample__host_idhost__in=selected_hosts)

    abundance_facts = Abundancefacttable.objects.select_related('sample_idsample__host_idhost', 'item_iditem',
                                                                'omics_idomics').prefetch_related(
        Prefetch('item_iditem__taxons_set', queryset=Taxons.objects.all())).filter(
        sample_idsample__host_idhost__in=selected_hosts)

    hosts = Host.objects.filter(idhost__in=selected_hosts)
    # # .prefetch_related('sample_set').all()
    # samples = hosts.sample_set.all()

    # Bring sample related to the select host

    # Convert the queryset to a dictionary-like representation
    hosts_dict = list(hosts.values())
    df = pd.DataFrame(hosts_dict)
    # import pdb
    # pdb.set_trace()
    return render(request, 'selected_hosts.html', {'sampleshosts': samples, 'abundancefacts': abundance_facts,
                                                   'lenabundancefacts': len(abundance_facts)})


@login_required
def download_csv(request):
    if request.method == 'POST':
        all_fields = [field.split('::') for field in request.POST.getlist('fields') if field]

        df = pd.DataFrame(all_fields,
                          columns=['idhost', 'tag', 'sex', 'idsample', 'samplename', 'abundance', 'itemname',
                                   'taxonomy'])

        df['abundance'] = df['abundance'].astype(float)
        df['idhost'] = df['idhost'].astype(int)
        df['tag'] = df['tag'].astype(str)
        df['sex'] = df['sex'].astype(str)
        df['idsample'] = df['idsample'].astype(int)
        df['samplename'] = df['samplename'].astype(str)
        df['itemname'] = df['itemname'].astype(str)
        df['taxonomy'] = df['taxonomy'].fillna('')
        df['taxonomy'] = df['taxonomy'].astype(str)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="checked_data.csv"'

        writer = csv.writer(response)
        writer.writerow(
            ['Id-host', 'tag', 'sex', 'ID-Sample', 'Sample Name', 'Abundance value', 'Item', 'TAX', 'Omics'])

        for index, row in df.iterrows():
            writer.writerow(
                [row['idhost'], row['tag'], row['sex'], row['idsample'], row['samplename'], row['abundance'],
                 row['itemname'], row['taxonomy'], ''])

        return response

    else:
        # Handle the case when the view is accessed with a different HTTP method
        return HttpResponseNotAllowed(['POST'])


@login_required
def graph_view(request):
    if 'action' in request.POST and request.POST['action'] == 'download':
        return download_csv(request)
    # if request.method == 'POST':
    selected_hosts = request.POST.getlist('host')
    selected_items = request.POST.getlist('item')
    selected_omics = request.POST.getlist('omics')
    abundance_facts = request.POST.getlist('abundance')
    all_field = request.POST.getlist('fields')
    selected_viz = request.POST.get('visualization')
    all_fields = [field.split('::') for fields in request.POST.getlist('fields') for field in fields]
    all_fields = [field.split('::') for field in request.POST.getlist('fields') if field]  # remove any empty elements

    df = pd.DataFrame(all_fields,
                      columns=['idhost', 'tag', 'sex', 'idsample', 'samplename', 'abundance', 'itemname', 'taxonomy'])

    df['abundance'] = df['abundance'].astype(float)
    df['idhost'] = df['idhost'].astype(int)
    df['tag'] = df['tag'].astype(str)
    df['sex'] = df['sex'].astype(str)
    df['idsample'] = df['idsample'].astype(int)
    df['samplename'] = df['samplename'].astype(str)
    df['itemname'] = df['itemname'].astype(str)
    df['taxonomy'] = df['taxonomy'].fillna('')
    df['taxonomy'] = df['taxonomy'].astype(str)

    # source = ColumnDataSource(df)
    # hover = HoverTool(tooltips=[('idhost', '@idhost')])
    #
    # p = figure(title='idhost Histogram', x_axis_label='idhost', y_axis_label='tag',
    #            tools=[hover])
    #
    # p.quad(top='tag', bottom=0, left='idhost', right='idhost', source=source,
    #        line_color='black', fill_color='red')

    # Create Bokeh figure based on the selected visualization type
    # Create a ColumnDataSource from your dataframe
    # import pdb
    # pdb.set_trace()
    #########################
    # Abundance vs.ID Sample
    #########################
    # Normalize abundance values to [0, 1]
    # Normalize abundance values to [0, 1]
    normalized_abundance = (df['abundance'] - df['abundance'].min()) / (
            df['abundance'].max() - df['abundance'].min())
    if selected_viz == "abdVSidsample":

        source = ColumnDataSource(data={
            'idsample': df['idsample'],
            'abundance': normalized_abundance,
            'tag': df['tag'],
            'idhost': df['idhost']
        })

        # Define hover tool
        hover = HoverTool(tooltips=[
            ('ID Sample', '@idsample'),
            ('Abundance', '@abundance{0.00}'),  # Format abundance tooltip
            ('Tag', '@tag'),
            ('Host', '@idhost')
        ])

        # Create figure with a single color (Viridis) for color variation
        color_palette = Viridis256  # You can choose a different palette if you prefer
        color_mapper = LinearColorMapper(palette=color_palette, low=0, high=1)

        p = figure(title='Abundance vs. ID Sample', tools=[hover], x_axis_label='ID Sample',
                   y_axis_label='Normalized Abundance')

        # Add scatter plot glyphs with color mapping
        p.scatter(x='idsample', y='abundance', source=source, size=10,
                  fill_color={'field': 'abundance', 'transform': color_mapper},
                  # legend_field='abundance'
                  line_color=None)

        # Add color bar legend
        color_bar = ColorBar(color_mapper=color_mapper, width=8, location=(0, 0))
        p.add_layout(color_bar, 'right')

        # Customize plot appearance
        p.legend.title = 'Normalized Abundance'
        p.legend.label_text_font_size = '10pt'
        p.xaxis.axis_label_text_font_size = '12pt'
        p.yaxis.axis_label_text_font_size = '12pt'
        p.legend.label_text_font_style = 'italic'

        #
        # source = ColumnDataSource(data={
        #     'idsample': df['idsample'],
        #     'abundance': df['abundance'],
        #     'tag': df['tag'],
        #     'idhost': df['idhost']
        # })
        #
        # # Define hover tool
        # hover = HoverTool(tooltips=[
        #     ('ID Sample', '@idsample'),
        #     ('Abundance', '@abundance'),
        #     ('Tag', '@tag'),
        #     ('Host', '@idhost')
        # ])
        # # Create figure
        # p = figure(title='Abundance vs. ID Sample', tools=[hover])
        # # Add scatter plot glyphs
        # p.scatter(x='idsample', y='abundance', source=source, color=Category10[10][0])

        # Set axis labels
        p.xaxis.axis_label = 'ID Sample'
        p.yaxis.axis_label = 'Abundance'
        script, div = components(p)

        return render(request, 'bokeh.html', {'script': script, 'div': div})

    elif selected_viz == 'line':
        p = figure(title='Line Plot of Abundance by Tag', x_axis_label='Tag', y_axis_label='Abundance')
        p.line(df['tag'], df['abundance'])
        script, div = components(p)

        return render(request, 'bokeh.html', {'script': script, 'div': div})
    elif selected_viz == 'bar':
        p = figure(title='Bar Plot of Abundance by Tag and Sex', x_axis_label='Tag', y_axis_label='Abundance')
        source = ColumnDataSource(df)
        p.vbar(x='tag', top='abundance', width=0.5, source=source, color='sex', legend_field='sex')
        script, div = components(p)

        return render(request, 'bokeh.html', {'script': script, 'div': div})

    elif selected_viz == 'barplot':
        # Version Normalize

        # Group and sum the data
        df_grouped = df.groupby(['samplename', 'sex'])['abundance'].sum().reset_index()

        # Normalize the abundance values using Min-Max normalization
        scaler = MinMaxScaler()
        df_grouped['abundance_normalized'] = scaler.fit_transform(df_grouped[['abundance']])

        # Create a list of samplenames and a dictionary mapping sex to a color
        samplenames = df_grouped['samplename'].unique().tolist()
        sex_color_map = {'M': Category10_10[0], 'F': Category10_10[1]}

        # Create a ColumnDataSource object
        source = ColumnDataSource(df_grouped)

        # Create the figure and configure its properties
        p = figure(x_range=samplenames, height=400, width=600, title='Normalized Abundance by Samplename and Sex',
                   toolbar_location=None, tools='')

        # Add the bars to the plot using dodge
        p.vbar(x=dodge('samplename', -0.2, range=p.x_range), top='abundance_normalized', width=0.4, source=source,
               line_color='white', fill_color=factor_cmap('sex',
                                                          palette=[sex_color_map[sex] for sex in
                                                                   df_grouped['sex'].unique()],
                                                          factors=df_grouped['sex'].unique()), legend_field='sex')

        # Add a legend to the plot
        p.legend.title = 'Sex'
        p.legend.location = 'top_right'
        p.legend.label_text_font_size = '12pt'

        # Configure the plot axis and labels
        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        p.yaxis.axis_label = 'Normalized Abundance'

        script, div = components(p)

        ######
        # df_grouped = df.groupby(['samplename', 'sex'])['abundance'].sum().reset_index()
        #
        # # Create a list of samplenames and a dictionary mapping sex to a color
        # samplenames = df_grouped['samplename'].unique().tolist()
        # sex_color_map = {'M': Category10_10[0], 'F': Category10_10[1]}
        #
        # # Create a ColumnDataSource object
        # source = ColumnDataSource(df_grouped)
        #
        # # Create the figure and configure its properties
        #
        # p = figure(x_range=samplenames, height=900, width=1200, title='Total Abundance by Samplename and Sex',
        #            toolbar_location=None, tools='')
        #
        # # Add the bars to the plot
        # p.vbar(x='samplename', top='abundance', width=0.4, source=source, line_color='white',
        #        fill_color=factor_cmap('sex', palette=[sex_color_map[sex] for sex in df_grouped['sex'].unique()],
        #                               factors=df_grouped['sex'].unique()), legend_field='sex')
        #
        # # Add a legend to the plot
        # p.legend.title = 'Sex'
        # p.legend.location = 'top_right'
        # p.legend.label_text_font_size = '12pt'
        # # Configure the plot axis and labels
        # p.xgrid.grid_line_color = None
        # p.y_range.start = 0
        # p.yaxis.axis_label = 'Total Abundance'
        #
        # script, div = components(p)

        return render(request, 'bokeh.html', {'script': script, 'div': div})

    elif selected_viz == 'AbundancebyTagandSampleName':
        # Normalized version

        # Normalize the abundance values by tag using Min-Max normalization
        scaler = MinMaxScaler()
        df['abundance_normalized'] = df.groupby('tag')['abundance'].transform(
            lambda x: scaler.fit_transform(x.values.reshape(-1, 1)).flatten())

        # Create a ColumnDataSource object
        source = ColumnDataSource(df)

        # Define the color palette with a single color shade
        color_palette = Viridis256  # You can choose a different palette if you prefer
        color_mapper = LinearColorMapper(palette=color_palette, low=0, high=1)

        # Create the figure
        p = figure(width=800, height=500, title='Normalized Abundance by Tag and Sample Name',
                   tools='pan,box_zoom,reset,hover', tooltips='@samplename: @abundance: @tag: @itemname')

        # Add the scatter plot with color mapping
        p.scatter(x='tag', y='abundance', source=source,
                  fill_color={'field': 'abundance_normalized', 'transform': color_mapper}, size=10)

        # Add a color bar legend
        color_bar = ColorBar(color_mapper=color_mapper, width=8, location=(0, 0))
        p.add_layout(color_bar, 'right')

        # Add legend and customize its appearance
        p.legend.title = 'Sex'
        p.legend.location = 'top_right'
        p.legend.label_text_font_size = '12pt'
        p.legend.margin = 20

        # Set the axis labels
        p.xaxis.axis_label = 'Tag'
        p.yaxis.axis_label = 'Abundance'

        script, div = components(p)

        # ###
        # source = ColumnDataSource(df)
        #
        # # Define the colors based on the 'sex' column
        # colors = factor_cmap('sex', palette=Category10_10, factors=df['sex'].unique())
        #
        # # Create the figure
        # p = figure(width=800, height=500, title='Abundance by Tag and Sample Name',
        #            tools='pan,box_zoom,reset,hover', tooltips='@samplename: @abundance: @tag: @itemname')
        #
        # # Add the scatter plot
        # p.scatter(x='tag', y='abundance', source=source, color=colors, legend_field='sex', size=10)
        #
        # # Add a legend to the plot
        # p.legend.title = 'Sex'
        # p.legend.location = 'top_right'
        # p.legend.label_text_font_size = '12pt'
        # p.legend.margin = 20
        #
        # # Set the axis labels
        # p.xaxis.axis_label = 'Tag'
        # p.yaxis.axis_label = 'Abundance'
        #
        # script, div = components(p)
        return render(request, 'bokeh.html', {'script': script, 'div': div})

    elif selected_viz == 'violin':
        # Aggregate the abundance values for each taxonomic group
        grouped_df = df.groupby('taxonomy')['abundance'].sum().reset_index()

        # Split the taxonomy column into different levels
        taxonomic_levels = grouped_df['taxonomy'].str.split(';').apply(pd.Series)

        # Add the abundance column to the taxonomic_levels dataframe
        taxonomic_levels['abundance'] = grouped_df['abundance']

        # Rename the columns for clarity
        taxonomic_levels.columns = ['domain', 'phylum', 'class', 'order', 'family', 'genus', 'species', 'item',
                                    'abundance']

        # Create the taxonomic group labels for the x-axis
        # x_labels = [f"{row[1]}-{row[2]}-{row[3]}-{row[5]}-{row[6]}" for row in df.values]
        x_labels = taxonomic_levels['genus'].unique()

        # Create a Bokeh figure
        p = figure(x_range=x_labels, height=400, width=800, title='Taxonomic Composition')
        p.vbar(x=x_labels, top=df['abundance'], width=0.9)

        p.xaxis.major_label_orientation = 1.2
        p.xaxis.axis_label = 'Taxonomic genus Group'
        p.yaxis.axis_label = 'Relative Abundance'

        # Create a Bokeh figure2
        x_labelss = taxonomic_levels['order'].unique()

        pp = figure(x_range=x_labelss, height=400, width=800, title='Taxonomic Composition')
        pp.vbar(x=x_labelss, top=df['abundance'], width=0.9)

        pp.xaxis.major_label_orientation = 1.2
        pp.xaxis.axis_label = 'Taxonomic order group'
        pp.yaxis.axis_label = 'Relative Abundance'

        # Create a Bokeh figure3
        x_labelss = taxonomic_levels['species'].unique()

        ppp = figure(x_range=x_labelss, height=400, width=800, title='Taxonomic Composition')
        ppp.vbar(x=x_labelss, top=df['abundance'], width=0.9)

        ppp.xaxis.major_label_orientation = 1.2
        ppp.xaxis.axis_label = 'Taxonomic species group'
        ppp.yaxis.axis_label = 'Relative Abundance'

        # Create a Bokeh figure3
        x_labels_item = taxonomic_levels['item'].unique()

        p_item = figure(x_range=x_labels_item, height=400, width=800, title='Taxonomic Composition')
        p_item.vbar(x=x_labels_item, top=df['abundance'], width=0.9)

        p_item.xaxis.major_label_orientation = 1.2
        p_item.xaxis.axis_label = 'Taxonomic Item group'
        p_item.yaxis.axis_label = 'Relative Abundance'

        script, div = components(p)
        script2, div2 = components(pp)
        script3, div3 = components(ppp)
        script4, div4 = components(p_item)

        return render(request, 'bokeh.html', {'script': script, 'div': div, 'script2': script2, 'div2': div2,
                                              'script3': script3, 'div3': div3, 'script4': script4, 'div4': div4})

    elif selected_viz == 'heatmap':
        # Split the taxonomy column into different levels
        taxonomic_levels = df['taxonomy'].str.split(';').apply(lambda x: x[3] if len(x) > 3 else '')

        # Create a DataFrame with taxonomic levels and abundance
        heatmap_df = pd.DataFrame(
            {'order': taxonomic_levels, 'abundance': df['abundance'], 'samplename': df['samplename']})

        # Pivot the DataFrame to create a matrix of abundance values for each taxonomic group and sample
        heatmap_df = heatmap_df.pivot_table(index='order', columns='samplename', values='abundance', aggfunc='sum')

        # tak Nan Value
        heatmap_df = heatmap_df.fillna(0)

        # Get the row and column indices of the heatmap DataFrame
        rows = heatmap_df.index.tolist()
        cols = heatmap_df.columns.tolist()

        # Create a meshgrid of coordinates for each rectangle
        x, y = np.meshgrid(cols, rows)

        # Flatten the arrays and the corresponding values for each rectangle
        x = x.flatten()
        y = y.flatten()
        values = heatmap_df.values.flatten()
        # values = np.log10(heatmap_df.values.flatten())

        # Define the color palette and adjust color intensity range
        palette = Viridis256  # Replace with the desired color palette
        low_value = np.percentile(values, 5)  # Adjust the percentile as needed
        high_value = np.percentile(values, 99)  # Adjust the percentile as needed

        # Define the color palette and adjust color intensity range
        # palette = Magma256
        palette = np.insert(Magma256, 0, '#FFFFFF')  # Change the palette to a hot color scheme
        low_value = np.min(values)  # Adjust the low value to the minimum abundance value in the dataset
        high_value = np.max(values)  # Adjust the high value to the maximum abunda
        # Create a color mapper using linear_cmap
        color_mapper = linear_cmap(field_name='values', palette=palette, low=low_value, high=high_value)

        # Create a LinearColorMapper to get color intensity
        color_intensity_mapper = LinearColorMapper(palette=palette, low=low_value, high=high_value)

        # Create a ColumnDataSource to store the rectangle data
        source = ColumnDataSource(data=dict(x=x, y=y, values=values))

        # Create the Bokeh figure
        p = figure(x_range=cols, y_range=list(reversed(rows)), width=800, height=400,
                   title='Taxonomy Order Heatmap', x_axis_location='above')

        # Add rectangles to the plot
        rect = p.rect(x='x', y='y', width=1, height=1, source=source, fill_color=color_mapper)

        # # Add color bar
        # color_bar = ColorBar(color_mapper=color_intensity_mapper, label_standoff=12, location=(0, 0))
        # p.add_layout(color_bar, 'right')
        # Add color bar
        color_bar = ColorBar(color_mapper=color_intensity_mapper, label_standoff=12, location=(0, 0))
        p.add_layout(color_bar, 'right')

        # Add color intensity values as hover tooltips
        p.add_tools(HoverTool(renderers=[rect], tooltips=[('Value', '@values'), ('Color Intensity', '@values{0.2f}')]))

        # Configure axis labels
        p.xaxis.axis_label = 'Sample ID'
        p.yaxis.axis_label = 'Order'

        script, div = components(p)
        # ------- For fAMILY HEATMAP -----
        # Split the taxonomy column into different levels
        taxonomic_levels = df['taxonomy'].str.split(';').apply(lambda x: x[4] if len(x) > 4 else '')

        # Create a DataFrame with taxonomic levels and abundance
        heatmap_df = pd.DataFrame(
            {'family': taxonomic_levels, 'abundance': df['abundance'], 'samplename': df['samplename']})

        # Pivot the DataFrame to create a matrix of abundance values for each taxonomic group and sample
        heatmap_df = heatmap_df.pivot_table(index='family', columns='samplename', values='abundance', aggfunc='sum')

        # tak Nan Value
        heatmap_df = heatmap_df.fillna(0)

        # Get the row and column indices of the heatmap DataFrame
        rows = heatmap_df.index.tolist()
        cols = heatmap_df.columns.tolist()

        # Create a meshgrid of coordinates for each rectangle
        x, y = np.meshgrid(cols, rows)

        # Flatten the arrays and the corresponding values for each rectangle
        x = x.flatten()
        y = y.flatten()
        values = heatmap_df.values.flatten()
        # values = np.log10(heatmap_df.values.flatten())

        # Define the color palette and adjust color intensity range
        # usuing the one on the top

        # Create a color mapper using linear_cmap
        color_mapper = linear_cmap(field_name='values', palette=palette, low=low_value, high=high_value)

        # Create a LinearColorMapper to get color intensity
        color_intensity_mapper = LinearColorMapper(palette=palette, low=low_value, high=high_value)

        # Create a ColumnDataSource to store the rectangle data
        source = ColumnDataSource(data=dict(x=x, y=y, values=values))

        # Create the Bokeh figure
        p_f = figure(x_range=cols, y_range=list(reversed(rows)), width=800, height=400,
                     title='Taxonomy family Heatmap', x_axis_location='above')

        # Add rectangles to the plot
        rect = p_f.rect(x='x', y='y', width=1, height=1, source=source, fill_color=color_mapper)

        # # Add color intensity values as hover tooltips
        # p_f.add_tools(
        #     HoverTool(renderers=[rect], tooltips=[('Value', '@values'), ('Color Intensity', '@values{0.2f}')]))
        # Add color bar
        color_bar = ColorBar(color_mapper=color_intensity_mapper, label_standoff=12, location=(0, 0))
        p_f.add_layout(color_bar, 'right')

        # Configure axis labels
        p_f.xaxis.axis_label = 'Sample ID'
        p_f.yaxis.axis_label = 'Family'

        script2, div2 = components(p_f)

        return render(request, 'bokeh.html', {'script': script, 'div': div, 'script2': script2, 'div2': div2})

    elif selected_viz == 'barplotTax':
        # Split the taxonomy column by semicolon (;) to extract the order
        df['Order'] = df['taxonomy'].str.split(';').str[3]

        # Group the dataframe by samplename and order to calculate the total abundance for each combination
        grouped = df.groupby(['samplename', 'Order']).sum().reset_index()

        # Create the bar plot
        plot = figure(height=500, width=800, title="Taxonomic Composition", toolbar_location=None,
                      x_range=grouped['samplename'].unique().tolist())

        custom_colors = ['#BF0000', '#00BF00', '#0000BF', '#BFBF00', '#BF00BF', '#00BFBF', '#BF6000', '#6000BF',
                         '#00BF60', '#BF0060', '#60BF00', '#0060BF', '#BF6060', '#60BF60', '#6060BF', '#BF60BF',
                         '#60BFBF', '#BFBF60', '#BF6000', '#6000BF', '#FF0000', '#00FF00', '#0000FF', '#FFFF00',
                         '#FF00FF', '#00FFFF', '#FF8000', '#8000FF', '#00FF80', '#FF0080', '#80FF00', '#0080FF',
                         '#FF8080', '#80FF80', '#8080FF', '#FF80FF', '#80FFFF', '#FFFF80', '#FF8000', '#8000FF']

        # Add more colors as needed
        orders = grouped['Order'].unique()

        colors = custom_colors[:max(len(orders), 20)]
        for i, order in enumerate(orders):
            data = grouped[grouped['Order'] == order]
            source = ColumnDataSource(data=dict(samplename=data['samplename'], abundance=data['abundance']))

            plot.vbar(x='samplename', top='abundance', width=0.6, source=source, legend_label=order,
                      color=colors[i % len(colors)])

        # Customize the plot
        plot.xgrid.grid_line_color = None
        plot.y_range.start = 0

        # Move the legend outside the graph
        plot.legend.location = "right"
        plot.legend.location = (580, -5)  # Adjust the values as per your preference

        # Add padding to the legend
        plot.legend.padding = 20  # Adjust the padding value as needed

        plot.xaxis.major_label_orientation = 0.3
        plot.xaxis.major_label_text_font_size = "8pt"

        # Enable zooming and panning
        wheel_zoom_tool = WheelZoomTool()
        pan_tool = PanTool(dimensions="width")
        plot.add_tools(wheel_zoom_tool, pan_tool)

        # Generate the plot components to embed in the HTML template
        script, div = components(plot)

        return render(request, 'bokeh.html', {'script': script, 'div': div})


@login_required
# Function to create a taxonomic composition bar plot for each samplename
def create_bar_plot(df, samplename):
    data = df[df['samplename'] == samplename]
    orders = data['order'].tolist()
    abundances = data['abundance'].tolist()

    angles = cumsum(abundances)
    colors = Category20[len(orders)]

    p = figure(height=400, width=600, title=f"Taxonomic Composition - {samplename}", toolbar_location=None,
               tools="hover", tooltips="@orders: @abundances", x_range=(-0.5, 1.0))

    p.wedge(x=0, y=0, radius=0.4, start_angle=cumsum([0] + abundances[:-1]) / sum(abundances) * 2 * pi,
            end_angle=angles / sum(abundances) * 2 * pi, line_color="white", fill_color=colors, legend_field='orders')

    hover = p.select(dict(type=HoverTool))
    hover.tooltips = [('order', '@orders'), ('Abundance', '@abundances')]

    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None

    return p


###### VIEWS DIGITAL MODEL

@login_required
def isabrown_detailv2(request):
    return render(request, 'isabrownv2.html')
@login_required
def isabrown_detail(request):
    return render(request, 'isabrown.html')
@login_required
def ross_detail(request):
    return render(request, 'ross.html')

@login_required
def process_datav2(request,  host_type, data_type):
    return render(request, f"{host_type}/ileum.html")

@login_required
def process_dataileumv2(request,  host_type, data_type):
    return render(request, f"{host_type}/ileum.html")

@login_required
def process_datamusclev2(request,  host_type, data_type):
    return render(request, f"{host_type}/muscle.html")

@login_required
def process_datamoleculev2(request,  host_type, data_type):
    return render(request, f"{host_type}/molecule.html")

@login_required
def process_dataliverv2(request,  host_type, data_type):
    return render(request, f"{host_type}/liver.html")

@login_required
def process_databacteryv2(request,  host_type, data_type):
    return render(request, f"{host_type}/bacterien.html")


@login_required
def process_data(request, host_type, data_type):

    """
    Handle the processing of specific data types based on the user's selection and host type.

    Args:
        request: The HTTP request object.
        host_type (str): The host type (e.g., 'ross', 'isabrown').
        data_type (str): The type of data selected (e.g., 'bacterien', 'molecule', etc.).

    Returns:
        Rendered HTML response or a message for debugging purposes.
    """
    # Create a mapping of data types to their descriptions or processing logic
    data_info = {
        "bacterien": {
            "title": "Bacterien Data Processing",
            "description": "Explore and analyze bacterial data for your research needs.",
        },
        "molecule": {
            "title": "Molecule Data Processing",
            "description": "Dive into molecular data for in-depth analysis.",
        },
        "ileum": {
            "title": "Ileum Data Processing",
            "description": "Analyze data related to helium and its properties.",
        },
        "muscle": {
            "title": "Muscle Data Processing",
            "description": "Focus on muscle-related data for detailed insights.",
        },
        "liver": {
            "title": "Liver Data Processing",
            "description": "Process liver data for health and scientific analysis.",
        },
    }

    # Check if the data_type exists in the mapping
    if data_type in data_info:
        # Get the details for the selected data type
        context = data_info[data_type]
        context['data_type'] = data_type.title()
        context['host_type'] = host_type.title()

        # Render a unique template for the combination of host_type and data_type
        template_name = f"{host_type}/{data_type}.html"
        return render(request, template_name, context)
    else:
        # If the data_type is invalid, return an error message
        return HttpResponse(f"Invalid data type: {data_type}", status=404)


## Molecule Isabrown
def molecule_data_analysis(request, host_type):
    # File paths
    peak_area_file = os.path.join("Avapp", "static", "Avapp", "csv", "peak_area.csv")
    peak_area_df = pd.read_csv(peak_area_file, sep="\t")

    # Top Samples Analysis
    top_n = 25  # Number of top samples to display
    melted_data = peak_area_df.melt(
        id_vars=["MS-Omics ID"], var_name="Sample", value_name="Peak Area"
    )
    top_samples = (
        melted_data.groupby("Sample")["Peak Area"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .index
    )
    top_samples_data = melted_data[melted_data["Sample"].isin(top_samples)]

    # Plot for Top Samples
    top_samples_plot = px.bar(
        top_samples_data,
        x="Sample",
        y="Peak Area",
        color="MS-Omics ID",
        title=f"Compostion of Samples by Ms-Omics Id Compound",
    )
    top_samples_plot_html = pio.to_html(top_samples_plot, full_html=False)

    # Available MS-Omics IDs for selection
    available_ids = peak_area_df["MS-Omics ID"].tolist()

    # Handle search input for sunburst
    selected_sunburst_id = request.GET.get("sunburst_ms_omics", "").strip()

    # Prepare data for sunburst (only if a valid ID is provided)
    sunburst_plot_html = None
    if selected_sunburst_id and selected_sunburst_id in available_ids:
        sunburst_data = peak_area_df[peak_area_df["MS-Omics ID"] == selected_sunburst_id]
        sunburst_data = sunburst_data.melt(
            id_vars=["MS-Omics ID"], var_name="Sample", value_name="Peak Area"
        )

        sunburst_plot = px.sunburst(
            sunburst_data,
            path=["MS-Omics ID", "Sample"],
            values="Peak Area",
            title=f"Sunburst Chart for {selected_sunburst_id}",
        )
        sunburst_plot_html = pio.to_html(sunburst_plot, full_html=False)

    # Pass context to the template
    context = {
        "host_type": host_type.title(),
        "data_type": "Molecule",
        "description": "Analyze the top samples by peak area and visualize the composition of MS-Omics IDs.",
        "top_n": top_n,
        "top_samples_plot": top_samples_plot_html,
        "available_ids": available_ids,
        "selected_sunburst_id": selected_sunburst_id,
        "sunburst_plot": sunburst_plot_html,
    }

    return render(request, f"{host_type}/molecule.html", context)


### Bacterien Isa & Ross
def bacterien_data_analysis(request, host_type):
    """
    View for analyzing bacterial data with enhanced individual-based chart functionality.
    """
    # Select the file based on host_type
    if host_type == "ross":
        file_path = os.path.join(settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "Sylph_MoARossFull_estimatedCounts.tsv")
    else:
        file_path = os.path.join(settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "Sylph_MoAIsaFull_estimatedCounts.tsv")

    # Load the data
    try:
        df = pd.read_csv(file_path, sep="\t")
        # Split Taxa into hierarchical levels
        taxonomy_levels = ["Domain", "Phylum", "Class", "Order", "Family", "Genus", "Species"]
        taxa_split = df["Taxa"].str.split(";", expand=True)
        taxa_split.columns = taxonomy_levels[:taxa_split.shape[1]]
        df = pd.concat([taxa_split, df.drop("Taxa", axis=1)], axis=1)
    except Exception as e:
        return HttpResponse(f"Error loading or processing file: {e}", status=500)

    # Get inputs from the user
    selected_taxonomic_level = request.GET.get("taxonomic_level", "Phylum")
    selected_taxonomic_entity = request.GET.get("taxonomic_entity", "")
    selected_individual = request.GET.get("individual", df.columns[-1])  # Default to the last sample
    top_n = int(request.GET.get("top_n", 10))

    # Get unique entities for the selected taxonomic level
    taxonomic_entities = df[selected_taxonomic_level].dropna().unique()

    rank_based_chart = None
    individual_based_chart = None
    sunburst_chart = None
    total_sunburst_chart = None

    try:
        # Total Sunburst Chart for All Data
        total_data = df.melt(id_vars=taxonomy_levels, var_name="Sample", value_name="Count")
        total_data = total_data[total_data["Count"] > 0]  # Filter out zero counts

        # Ensure only rows with complete taxonomy paths are included
        complete_paths = total_data.dropna(subset=taxonomy_levels)

        total_sunburst_chart = px.sunburst(
            complete_paths,
            path=taxonomy_levels,
            values="Count",
            title="Total Taxonomic Composition Across All Samples",
        ).to_html(full_html=False)
    except Exception as e:
        total_sunburst_chart = f"Error generating total sunburst chart: {e}"

    # Filter by selected taxonomic level and entity
    if selected_taxonomic_level in df.columns:
        if selected_taxonomic_entity:
            filtered_df = df[df[selected_taxonomic_level].str.contains(selected_taxonomic_entity, na=False)]
        else:
            filtered_df = df
    else:
        filtered_df = df

    try:
        # Top N Samples for Selected Taxonomic Entity
        top_samples = (
            filtered_df.drop(columns=taxonomy_levels)
            .sum()
            .sort_values(ascending=False)
            .head(top_n)
        )
        rank_based_chart = px.bar(
            top_samples,
            x=top_samples.index,
            y=top_samples.values,
            labels={"x": "Sample", "y": "Total Count"},
            title=f"Top {top_n} Samples for {selected_taxonomic_entity or selected_taxonomic_level}",
        ).to_html(full_html=False)
    except Exception as e:
        rank_based_chart = f"Error generating rank-based chart: {e}"

    try:
        # Individual-Based Chart
        if selected_individual in df.columns and selected_taxonomic_level in df.columns:
            individual_data = df.groupby(selected_taxonomic_level)[selected_individual].sum()
            top_taxa = individual_data.sort_values(ascending=False).head(top_n)
            individual_based_chart = px.bar(
                top_taxa,
                x=top_taxa.index,
                y=top_taxa.values,
                labels={"x": selected_taxonomic_level, "y": "Count"},
                title=f"Top {top_n} Taxonomic Entities for {selected_individual}",
            ).to_html(full_html=False)
        else:
            individual_based_chart = "Please select a valid individual and taxonomic level."
    except Exception as e:
        individual_based_chart = f"Error generating individual-based chart: {e}"

    try:
        # Full Sunburst Composition for Selected Individual
        if selected_individual:
            sample_data = df[[*taxonomy_levels, selected_individual]].copy()
            sample_data = sample_data[sample_data[selected_individual] > 0]
            sunburst_chart = px.sunburst(
                sample_data,
                path=taxonomy_levels,
                values=selected_individual,
                title=f"Taxonomic Composition of {selected_individual}",
            ).to_html(full_html=False)
    except Exception as e:
        sunburst_chart = f"Error generating sunburst chart: {e}"

    context = {
        "host_type": host_type.title(),
        "data_type": "Bacterial",
        "description": "Explore bacterial data with various interactive visualizations.",
        "rank_based_chart": rank_based_chart,
        "individual_based_chart": individual_based_chart,
        "sunburst_chart": sunburst_chart,
        "total_sunburst_chart": total_sunburst_chart,  # Add this to the context
        "taxonomic_levels": taxonomy_levels,
        "taxonomic_entities": sorted(taxonomic_entities),  # Sorted for better usability
        "selected_taxonomic_level": selected_taxonomic_level,
        "selected_taxonomic_entity": selected_taxonomic_entity,
        "top_n_options": [5, 10, 20],
        "top_n": top_n,
        "selected_individual": selected_individual,
    }

    return render(request, f"{host_type}/bacterien.html", context)
    ######

### Bacterien isabrown v2
# Set up logging
logger = logging.getLogger(__name__)

# def bacterien_data_analysisv2(request, host_type):
#     """
#     View for analyzing bacterial data with a two-step process:
#       1) User selects tissue type (file to load).
#       2) User applies existing filters (variable, accuracy, correlation).
#       3) Additionally, generate two Plotly Sunbursts (0.6 threshold & 0.5 threshold).
#     """
#
#     # -------------------------------------------------------------------
#     # 1) Load main bacterial data (unchanged)
#     # -------------------------------------------------------------------
#     if host_type == "ross":
#         file_path = os.path.join(
#             settings.BASE_DIR, "Avapp", "static", "Avapp", "csv",
#             "Sylph_MoARossFull_estimatedCounts.tsv"
#         )
#     else:
#         file_path = os.path.join(
#             settings.BASE_DIR, "Avapp", "static", "Avapp", "csv",
#             "Sylph_MoAIsaFull_estimatedCounts.tsv"
#         )
#
#     taxonomy_levels = ["Domain", "Phylum", "Class", "Order", "Family", "Genus", "Species"]
#     try:
#         df = pd.read_csv(file_path, sep="\t")
#         taxa_split = df["Taxa"].str.split(";", expand=True)
#         taxa_split.columns = taxonomy_levels[:taxa_split.shape[1]]
#         df = pd.concat([taxa_split, df.drop("Taxa", axis=1)], axis=1)
#     except Exception as e:
#         return JsonResponse({"error": f"Error loading bacterial data: {e}"}, status=500)
#
#     # -------------------------------------------------------------------
#     # 2) Tissue file logic mapping
#     # -------------------------------------------------------------------
#     tissue_files = {
#         "ileum": "otu_to_ileum.csv",
#         "muscle": "otu_to_muscle.csv",
#         "liver": "otu_to_liver.csv",
#         "otu": "otu_to_otu.csv",
#         "Metabolomic": "otu_to_metab.csv"
#     }
#
#     # -------------------------------------------------------------------
#     # 3) AJAX: Load Tissue Variables (unchanged)
#     # -------------------------------------------------------------------
#     if request.headers.get("x-requested-with") == "XMLHttpRequest" and "load_tissue" in request.GET:
#         tissue = request.GET.get("tissue")
#         if tissue not in tissue_files:
#             return JsonResponse({"error": f"Invalid tissue type: {tissue}"}, status=400)
#         try:
#             csv_file_path = os.path.join(
#                 settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
#                 tissue_files[tissue]
#             )
#             csv_df = pd.read_csv(csv_file_path)
#             variables = csv_df.columns[2:].tolist()
#             return JsonResponse({"variables": variables})
#         except Exception as e:
#             return JsonResponse({"error": f"Error loading CSV file: {e}"}, status=500)
#
#     # -------------------------------------------------------------------
#     # 4) AJAX: Perform Filtering or Min/Max Correlation (unchanged)
#     # -------------------------------------------------------------------
#     if request.headers.get("x-requested-with") == "XMLHttpRequest":
#         tissue = request.GET.get("tissue")
#         if tissue not in tissue_files:
#             return JsonResponse({"results": [], "error": "Missing or invalid tissue type."}, status=400)
#
#         csv_file_path = os.path.join(
#             settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
#             tissue_files[tissue]
#         )
#         try:
#             csv_df = pd.read_csv(csv_file_path)
#             variables = csv_df.columns[2:].tolist()
#         except Exception as e:
#             return JsonResponse({"error": f"Error loading CSV file: {e}"}, status=500)
#
#         selected_variable = request.GET.get("variable", variables[0] if variables else None)
#         if selected_variable not in variables:
#             return JsonResponse({"results": [], "error": "Invalid variable selected."}, status=400)
#
#         variable_index = csv_df.columns.get_loc(selected_variable)
#         correlation_values = csv_df.iloc[:, variable_index].dropna()
#
#         if "fetch_min_max" in request.GET:
#             try:
#                 return JsonResponse({
#                     "min_correlation": correlation_values.min(),
#                     "max_correlation": correlation_values.max(),
#                 })
#             except Exception as e:
#                 return JsonResponse({"error": f"Error fetching min/max: {e}"}, status=500)
#
#         # Filtering logic
#         try:
#             correlation_threshold = float(request.GET.get("correlation", -1))
#             min_accuracy = float(request.GET.get("accuracy", 0))
#
#             filtered_df = csv_df[
#                 (csv_df["accuracy"] >= min_accuracy) &
#                 (correlation_values >= correlation_threshold)
#             ]
#             filtered_results = filtered_df.apply(
#                 lambda row: {
#                     "variable": row[csv_df.columns[0]],
#                     "accuracy": row["accuracy"],
#                     "correlation": row[selected_variable],
#                 },
#                 axis=1,
#             ).tolist()
#             return JsonResponse({"results": filtered_results})
#         except Exception as e:
#             return JsonResponse({"error": f"Error during filtering: {e}"}, status=500)
#
#         # ---------------------- 5) Non-AJAX GET: Create TWO Sunbursts from two cluster lists ----------------------
#         # Example lists (threshold 0.6 and 0.5), each is a nested list of species
#         # In your real code, you'd use the lists you already have.
#     cluster_data_0_6 = [['s__Phocaeicola plebeius_A', 's__Phocaeicola sp900546355', 's__Parabacteroides sp002159645', 's__Prevotella lascolaii',
#     's__Limicola phocaeensis_A', 's__Desulfovibrio sp944327285', 's__Phocaeicola intestinalis', 's__Aphodousia secunda_A', 's__Phocaeicola_A sp900291465',
#     's__Phocaeicola barnesiae', 's__Phocaeicola_A sp003489705', 's__Mediterranea massiliensis'], ['s__Fournierella sp002161595',
#      's__Massilimicrobiota sp002160865', 's__Faecalitalea cylindroides', 's__Thomasclavelia spiroformis', 's__Pseudobutyricicoccus sp016901775',
#       's__Massilimicrobiota merdigallinarum', 's__Mediterraneibacter faecipullorum', 's__Dysosmobacter avistercoris', 's__Faecalicoccus acidiformans',
#       's__Agathobaculum intestinigallinarum', 's__Fusicatenibacter sp900543115', 's__Blautia ornithocaccae'], ['s__Lactobacillus gallinarum',
#       's__Phocaeicola dorei', 's__Mediterraneibacter excrementipullorum', 's__Fusobacterium_A sp900549465', 's__Avimicrobium caecorum',
#       's__Thomasclavelia merdavium', 's__Anaerofilum faecale', 's__Veillonella_A magna', 's__Odoribacter splanchnicus'],
#       ['s__Megamonas hypermegale_A', 's__Ligilactobacillus salivarius', 's__Brachyspira innocens', 's__CAG-266 sp000436095',
#       's__Megamonas funiformis', 's__Megamonas hypermegale'], ['s__Limosilactobacillus vaginalis', 's__Flavonifractor plautii',
#        's__Anaerotruncus colihominis', 's__Lactobacillus crispatus', 's__Coprobacillus cateniformis', 's__Enterococcus_D gallinarum'],
#         ['s__Lachnoclostridium_B sp000765215', 's__Butyricicoccus pullicaecorum', 's__Enterocloster aldenensis', 's__Sutterella massiliensis',
#          's__Phocaeicola sp002161765', 's__Blautia_A avistercoris'], ['s__Phocaeicola caecigallinarum_A', 's__Merdimonas massiliensis_A',
#          's__Prevotella massiliensis', 's__Phocaeicola coprophilus', 's__Alistipes cottocaccae'], ['s__Phocaeicola excrementipullorum',
#          's__Phocaeicola sp900551065', 's__Succinatimonas hippei', 's__Desulfovibrio sp900556755', 's__Phocaeicola faecium']]
#
#     cluster_data_0_5 = [['s__Lactobacillus gallinarum', 's__Phocaeicola dorei', 's__Anaerotignum lactatifermentans',
#                          's__Parabacteroides distasonis', 's__Mediterraneibacter excrementipullorum', 's__Fusobacterium_A sp900549465',
#                          's__Thomasclavelia merdavium', 's__Avimicrobium caecorum', 's__Anaerofilum faecale',
#                          's__Veillonella_A magna', 's__Anaeromassilibacillus stercoravium', 's__Odoribacter splanchnicus', 's__Akkermansia muciniphila'],
#                         ['s__Fournierella sp002161595', 's__Massilimicrobiota sp002160865', 's__Faecalitalea cylindroides', 's__Thomasclavelia spiroformis',
#                          's__Pseudobutyricicoccus sp016901775', 's__Massilimicrobiota merdigallinarum', 's__Mediterraneibacter faecipullorum',
#                          's__Dysosmobacter avistercoris','s__Faecalicoccus acidiformans', 's__Agathobaculum intestinigallinarum', 's__Fusicatenibacter sp900543115', 's__Blautia ornithocaccae'],
#                         ['s__Phocaeicola plebeius_A', 's__Phocaeicola sp900546355', 's__Parabacteroides sp002159645', 's__Prevotella lascolaii','s__Limicola phocaeensis_A', 's__Desulfovibrio sp944327285',
#                          's__Phocaeicola intestinalis', 's__Aphodousia secunda_A', 's__Phocaeicola_A sp900291465', 's__Phocaeicola barnesiae', 's__Phocaeicola_A sp003489705',
#                          's__Mediterranea massiliensis'], ['s__Phocaeicola sp002161765', 's__Lachnoclostridium_B sp000765215', 's__Butyricicoccus pullicaecorum',
#                         's__Enterocloster aldenensis', 's__Ligilactobacillus aviarius', 's__Sellimonas caecigallum', 's__Sutterella massiliensis', 's__Enorma massiliensis', 's__Fournierella sp002159185', 's__Blautia_A avistercoris'],
#                         ['s__Coprousia sp002159765', 's__Gemmiger formicilis_B', 's__Bifidobacterium pullorum_B', 's__Anaerobutyricum faecale', 's__Lawsonibacter sp900545895',
#                          's__Faecalibacterium avium', 's__Clostridium_Q saccharolyticum_A', 's__Limosilactobacillus ingluviei', 's__Megasphaera stantonii', 's__Helicobacter_D pullorum'],
#                         ['s__Flavonifractor avistercoris', 's__Megamonas hypermegale_A', 's__Faecalicoccus pleomorphus', 's__CAG-266 sp000436095', 's__Megamonas funiformis',
#                          's__Brachyspira innocens', 's__Megamonas hypermegale', 's__Ligilactobacillus salivarius', 's__Streptococcus alactolyticus', 's__Limosilactobacillus reuteri_E'],
#                         ['s__Caccocola sp002159945', 's__Alistipes excrementigallinarum', 's__Mediterranea pullorum', 's__Lachnoclostridium_B massiliensis_A', 's__Bacteroides xylanisolvens',
#                          's__Alistipes megaguti', 's__Desulfovibrio faecigallinarum', 's__Paraprevotella stercoravium', 's__Mediterranea ndongoniae'],
#                         ['s__Succinatimonas hippei', 's__Limosilactobacillus coleohominis', 's__Phocaeicola coprocola', 's__Butyricimonas paravirosa', 's__Phocaeicola excrementipullorum', 's__Phocaeicola sp900551065', 's__Desulfovibrio sp900556755', 's__Phocaeicola faecium'],
#                         ['s__Limosilactobacillus vaginalis','s__Flavonifractor plautii', 's__Anaerotruncus colihominis', 's__Lactobacillus crispatus', 's__Coprobacillus cateniformis', 's__An181 sp002160325', 's__Enterococcus_D gallinarum'],
#                         ['s__Phocaeicola caecigallinarum_A', 's__Merdimonas massiliensis_A','s__Prevotella massiliensis', 's__Phocaeicola coprophilus', 's__Alistipes cottocaccae']]
#
#     # We'll create two DataFrames from these lists
#     def clusters_to_df(cluster_data):
#         rows = []
#         for i, sublist in enumerate(cluster_data, start=1):
#             cluster_name = f"Cluster {i}"
#             for species in sublist:
#                 rows.append({"Cluster": cluster_name, "Species": species, "Value": 1})
#         return pd.DataFrame(rows)
#
#     df_0_6 = clusters_to_df(cluster_data_0_6)
#     df_0_5 = clusters_to_df(cluster_data_0_5)
#
#     # Build two Plotly sunbursts
#     try:
#         fig_0_6 = px.sunburst(
#             df_0_6,
#             path=["Cluster", "Species"],  # top-level: cluster, leaf-level: species
#             values="Value",
#             title="Threshold 0.6 Sunburst",
#             color="Cluster"
#         )
#         # Convert to HTML
#         sunburst_html_0_6 = fig_0_6.to_html(full_html=False, include_plotlyjs='cdn')
#     except Exception as e:
#         print(f"Error building sunburst 0.6: {e}")
#         sunburst_html_0_6 = ""
#
#     try:
#         fig_0_5 = px.sunburst(
#             df_0_5,
#             path=["Cluster", "Species"],
#             values="Value",
#             title="Threshold 0.5 Sunburst",
#             color="Cluster"
#         )
#         # We skip reloading Plotly JS here
#         sunburst_html_0_5 = fig_0_5.to_html(full_html=False, include_plotlyjs=False)
#     except Exception as e:
#         print(f"Error building sunburst 0.5: {e}")
#         sunburst_html_0_5 = ""
#
#     return render(
#         request,
#         f"{host_type}/bacterien.html",
#         {
#             "host_type": host_type.title(),
#             "data_type": "Bacterial",
#             "description": "Explore bacterial data. Step 1: select a tissue file. Step 2: apply filters.",
#             "variables": [],
#             "tissue_types": list(tissue_files.keys()),
#
#             # Pass the two sunburst HTML strings to the template
#             "sunburst_html_0_6": sunburst_html_0_6,
#             "sunburst_html_0_5": sunburst_html_0_5,
#         },
#     )
from django.core.cache import cache
import requests
from django.views.decorators.http import require_GET

#####################V2 ######################""""""
# Mapping Tissue -> CSV
tissue_files = {
    "ileum": "otu_to_ileum.csv",
    "muscle": "otu_to_muscle.csv",
    "liver": "otu_to_liver.csv",
    "otu": "otu_to_otu.csv",
    "Metabolomic": "otu_to_metab.csv",
    "functionnal": "otu_to_functionnal.csv",
    "acid":"otu_to_acid.csv"
}

tissue_files_ileum = {
        "ileum": "ileum_to_ileum.csv",
        "muscle": "ileum_to_muscle.csv",
        "liver": "ileum_to_liver.csv",
        "otu": "ileum_to_otu.csv",
        "Metabolomic": "ileum_to_metab.csv",
        "functionnal": "ileum_to_functionnal.csv",
        "acid":"ileum_to_acid.csv"

}

tissue_files_functionnel = {
        "ileum": "muscle_to_ileum.csv",
        "muscle": "muscle_to_muscle.csv",
        "liver": "muscle_to_liver.csv",
        "otu": "muscle_to_otu.csv",
        "Metabolomic": "muscle_to_metab.csv",
        "functionnal": "muscle_to_functionnal.csv",
        "acid": "muscle_to_acid.csv"

}

tissue_files_liver = {
        "ileum": "liver_to_ileum.csv",
        "muscle": "liver_to_muscle.csv",
        "liver": "liver_to_liver.csv",
        "otu": "liver_to_otu.csv",
        "Metabolomic": "liver_to_metab.csv",
        "functionnal": "liver_to_functionnal.csv",
        "acid": "liver_to_acid.csv"

}

tissue_files_molecule = {
        "ileum": "metab_to_ileum.csv",
        "muscle": "metab_to_muscle.csv",
        "liver": "metab_to_liver.csv",
        "otu": "metab_to_otu.csv",
        "Metabolomic": "metab_to_metab.csv",
        "functionnal": "metab_to_functionnal.csv",
        "acid":"metab_to_acid.csv"

}


tissue_files_functionnel = {
    "ileum": "functionnal_to_ileum.csv",
    "muscle": "functionnal_to_muscle.csv",
    "liver": "functionnal_to_liver.csv",
    "otu": "functionnal_to_otu.csv",
    "Metabolomic": "functionnal_to_metab.csv",
    "functionnal": "functionnal_to_functionnal.csv",
     "acid" : "functionnal_to_acid.csv"

}

tissue_files_acid = {
    "ileum": "acid_to_ileum.csv",
    "muscle": "acid_to_muscle.csv",
    "liver": "acid_to_liver.csv",
    "otu": "acid_to_muscle.csv",
    "Metabolomic": "acid_to_metab.csv",
    "functionnal": "acid_to_functionnal.csv",
     "acid" : "acid_to_acid.csv"
}


@csrf_exempt
def bacterien_data_analysisv2(request, host_type='isabrownv2'):
    """
    1) Creates two sunbursts (threshold 0.5 & 0.6).
    2) Handles AJAX for single-var & multi-var filtering => returns top 100 in JSON.
    3) No server-side gene info or CSV download. The gene info & CSV are fully client-side.
    """
    # 1) Load data for sunburst
    if host_type == "ross":
        big_tsv_path = os.path.join(
            settings.BASE_DIR, "Avapp", "static", "Avapp", "csv",
            "Sylph_MoARossFull_estimatedCounts.tsv"
        )
    else:
        big_tsv_path = os.path.join(
            settings.BASE_DIR, "Avapp", "static", "Avapp", "csv",
            "Sylph_MoAIsaFull_estimatedCounts.tsv"
        )

    try:
        df_sunburst = pd.read_csv(big_tsv_path, sep="\t")
        # Suppose 'Taxa' has a semi-colon separated taxonomy chain
        splitted = df_sunburst["Taxa"].str.split(";", expand=True)
        # Possibly up to 7 levels
        taxonomy_levels = ["Domain", "Phylum", "Class", "Order", "Family", "Genus", "Species"]
        splitted.columns = taxonomy_levels[:splitted.shape[1]]
        df_sunburst = pd.concat([splitted, df_sunburst.drop("Taxa", axis=1)], axis=1)
    except Exception as e:
        return JsonResponse({"error": f"Error loading sunburst data: {e}"}, status=500)

    # 2) Handle AJAX (single-var, multi-var) => top 100
    if request.headers.get("x-requested-with") == "XMLHttpRequest":

        # (A) load_tissue => returns list of variables
        if "load_tissue" in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files:
                return JsonResponse({"error": f"Invalid tissue: {tissue}"}, status=400)
            try:
                csv_path = os.path.join(
                    settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                    tissue_files[tissue]
                )
                df_small = pd.read_csv(csv_path)
                variables = df_small.columns[2:].tolist()
                return JsonResponse({"variables": variables})
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV: {e}"}, status=500)

        # (B) Single-var => includes fetch_min_max + filter
        elif "multi_variable" not in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files:
                return JsonResponse({"results": [], "error": "Missing or invalid tissue."}, status=400)
            csv_path = os.path.join(
                settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                tissue_files[tissue]
            )

            try:
                df_all = pd.read_csv(csv_path)
                variables = df_all.columns[2:].tolist()
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV: {e}"}, status=500)

            selected_variable = request.GET.get("variable", variables[0] if variables else None)
            if selected_variable not in variables:
                return JsonResponse({"results": [], "error": "Invalid variable selected."}, status=400)

            # B1) fetch_min_max
            if "fetch_min_max" in request.GET:
                try:
                    col_vals = df_all[selected_variable].dropna()
                    return JsonResponse({
                        "min_correlation": float(col_vals.min()),
                        "max_correlation": float(col_vals.max()),
                    })
                except Exception as e:
                    return JsonResponse({"error": f"Error fetching min/max: {e}"}, status=500)

            # B2) filter => top 100
            try:
                correlation_min = float(request.GET.get("correlation_min", -1))
                correlation_max = float(request.GET.get("correlation_max", 1))
                min_accuracy = float(request.GET.get("accuracy", 0))

                if correlation_min > correlation_max:
                    return JsonResponse({"error": "Min correlation cannot exceed max correlation."}, status=400)

                filtered = df_all[
                    (df_all["accuracy"] >= min_accuracy)
                    & (df_all[selected_variable] >= correlation_min)
                    & (df_all[selected_variable] <= correlation_max)
                ]
                if filtered.empty:
                    return JsonResponse({"results": [], "total_count": 0})

                filtered.sort_values(by=selected_variable, ascending=False, inplace=True)
                total_count = len(filtered)
                top_100 = filtered.head(100)

                first_col = df_all.columns[0]
                results_list = []
                for _, row in top_100.iterrows():
                    results_list.append({
                        "var1": row[first_col],
                        "var2": selected_variable,
                        "accuracy": row["accuracy"],
                        "correlation": row[selected_variable]
                    })

                return JsonResponse({"results": results_list, "total_count": total_count})
            except Exception as e:
                return JsonResponse({"error": f"Error during single-var filter: {e}"}, status=500)

        # (C) Multi-var => top 100
        elif "multi_variable" in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files:
                return JsonResponse({"results": [], "error": "Missing or invalid tissue."}, status=400)

            variables = request.GET.getlist("variables[]")
            if not variables:
                return JsonResponse({"results": [], "error": "No variables selected."}, status=400)

            csv_path = os.path.join(
                settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                tissue_files[tissue]
            )
            try:
                df_all = pd.read_csv(csv_path)
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV file: {e}"}, status=500)

            try:
                correlation_min = float(request.GET.get("correlation_min", -1))
                correlation_max = float(request.GET.get("correlation_max", 1))
                min_accuracy = float(request.GET.get("accuracy", 0))
                if correlation_min > correlation_max:
                    return JsonResponse({"error": "Min correlation cannot exceed max correlation."}, status=400)

                filtered_parts = []
                first_col = df_all.columns[0]
                for var in variables:
                    if var not in df_all.columns:
                        continue
                    sub = df_all[
                        (df_all["accuracy"] >= min_accuracy)
                        & (df_all[var] >= correlation_min)
                        & (df_all[var] <= correlation_max)
                    ].copy()
                    if not sub.empty:
                        sub["var2"] = var
                        filtered_parts.append(sub)

                if not filtered_parts:
                    return JsonResponse({"results": [], "total_count": 0})

                combined = pd.concat(filtered_parts, ignore_index=True)
                corvals = []
                for _, row in combined.iterrows():
                    corvals.append(row[row["var2"]])
                combined["correlation"] = corvals

                combined.drop_duplicates(subset=[first_col, "var2"], inplace=True)
                combined.sort_values(by="correlation", ascending=False, inplace=True)
                total_count = len(combined)

                top_100 = combined.head(100)
                results_list = []
                for _, row in top_100.iterrows():
                    results_list.append({
                        "var1": row[first_col],
                        "var2": row["var2"],
                        "accuracy": row["accuracy"],
                        "correlation": row["correlation"]
                    })

                return JsonResponse({"results": results_list, "total_count": total_count})
            except Exception as e:
                return JsonResponse({"error": f"Error during multi-var filter: {e}"}, status=500)

        # If none matched
        return JsonResponse({"error":"No recognized AJAX action."}, status=400)

    # 3) Build the sunbursts for 0.5 & 0.6
    cluster_data_0_6 = [['s__Ligilactobacillus salivarius', 's__Brachyspira innocens', 's__Limicola phocaeensis_A', 's__Bifidobacterium pullorum_B', 's__Phocaeicola intestinalis', 's__Succinatimonas hippei', 's__Lachnoclostridium_A stercorigallinarum', 's__Megamonas hypermegale_A'], ['s__Gemmiger faecavium', 's__Barnesiella merdipullorum', 's__Mediterraneibacter sp944383745', 's__Bradyrhizobium sp002831585', 's__Dysosmobacter faecalis', 's__Enterococcus_B hirae'], ['s__Anaerotruncus excrementipullorum', 's__Mediterraneibacter stercorigallinarum', 's__Mediterraneibacter excrementavium', 's__Alloclostridium intestinigallinarum', 's__Faecivivens stercoripullorum'], ['s__Lachnoclostridium_B sp000765215', 's__Enorma phocaeensis', 's__Dysosmobacter excrementavium', 's__Aphodousia secunda_A', 's__Caccocola sp002159945']]
    cluster_data_0_5 = [['s__Ligilactobacillus salivarius', 's__Brachyspira innocens', 's__Limicola phocaeensis_A', 's__Bifidobacterium pullorum_B', 's__Phocaeicola intestinalis', 's__Succinatimonas hippei', 's__Lachnoclostridium_A stercorigallinarum', 's__Megamonas hypermegale_A'], ['s__Enterocloster sp944383785', 's__Mediterraneibacter sp020687545', 's__Parachristensenella avicola', 's__Acutalibacter sp900755895', 's__Bariatricus faecipullorum', 's__Mediterraneibacter quadrami', 's__Blautia_A faecigallinarum'], ['s__Mediterranea ndongoniae', 's__Scatomorpha stercorigallinarum', 's__Faecalibacterium intestinigallinarum','s__Anaerotruncus sp944387965'], ['s__Lachnoclostridium_A avicola', 's__Gemmiger stercoravium', 's__RGIG4074 sp944376455', 's__Mediterraneibacter faecipullorum', 's__Aveggerthella excrementigallinarum', 's__Mediterraneibacter merdigallinarum'], ['s__Gallimonas caecicola', 's__Anaerostipes avistercoris', 's__Coprocola pullicola', 's__QANA01 sp900554725', 's__Angelakisella sp904420255', 's__Borkfalkia faecipullorum'], ['s__Gemmiger faecavium', 's__Barnesiella merdipullorum', 's__Mediterraneibacter sp944383745', 's__Bradyrhizobium sp002831585', 's__Dysosmobacter faecalis', 's__Enterococcus_B hirae'], ['s__Anaerotruncus excrementipullorum', 's__Mediterraneibacter stercorigallinarum', 's__Mediterraneibacter excrementavium', 's__Alloclostridium intestinigallinarum', 's__Faecivivens stercoripullorum'], ['s__Ventrenecus sp944355355', 's__Borkfalkia excrementavium', 's__Flavonifractor sp002159455', 's__Gallimonas intestinigallinarum', 's__Avoscillospira stercorigallinarum'], ['s__Lachnoclostridium_B sp000765215', 's__Enorma phocaeensis', 's__Dysosmobacter excrementavium', 's__Aphodousia secunda_A', 's__Caccocola sp002159945']]

    def clusters_to_df(data):
        rows = []
        for i, sublist in enumerate(data, start=1):
            cluster_name = f"Cluster {i}"
            for species in sublist:
                # remove s__ prefix for display
                clean_species = species.replace("s__", "")
                rows.append({"Cluster": cluster_name, "Species": clean_species, "Value": 1})
        return pd.DataFrame(rows)

    df_0_6 = clusters_to_df(cluster_data_0_6)
    df_0_5 = clusters_to_df(cluster_data_0_5)

    try:
        fig_0_6 = px.sunburst(df_0_6, path=["Cluster", "Species"], values="Value", title="Threshold 0.6")
        fig_0_6.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_6 = pio.to_html(
            fig_0_6,
            full_html=False,
            include_plotlyjs=False,
            config={"responsive": True},
            div_id="sunburst_06"
        )
    except:
        sunburst_html_0_6 = ""

    try:
        fig_0_5 = px.sunburst(df_0_5, path=["Cluster", "Species"], values="Value", title="Threshold 0.5")
        fig_0_5.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_5 = pio.to_html(
            fig_0_5,
            full_html=False,
            include_plotlyjs=False,
            config={"responsive": True},
            div_id="sunburst_05"
        )
    except:
        sunburst_html_0_5 = ""

    # 4) Render template
    return render(
        request,
        f"{host_type}/bacterien.html",  # e.g. "isabrownv2/bacterien.html"
        {
            "host_type": host_type.title(),
            "data_type": "Bacterial",
            "description": "Top 100 displayed only. Gene info from Ensembl REST.",
            "tissue_types": list(tissue_files.keys()),
            "sunburst_html_0_6": sunburst_html_0_6,
            "sunburst_html_0_5": sunburst_html_0_5,
        }
    )

def ileum_data_analysisv2(request, host_type='isabrownv2'):
    """
    1) Creates two sunbursts (threshold 0.5 & 0.6).
    2) Handles AJAX for single-var & multi-var filtering => returns top 100 in JSON.
    3) No server-side gene info or CSV download. The gene info & CSV are fully client-side.
    """
    # 1) Load data for sunburst
    if host_type == "ross":
        big_tsv_path = os.path.join(
            settings.BASE_DIR, "Avapp", "static", "Avapp", "csv",
            "Sylph_MoARossFull_estimatedCounts.tsv"
        )
    else:
        big_tsv_path = os.path.join(
            settings.BASE_DIR, "Avapp", "static", "Avapp", "csv",
            "Sylph_MoAIsaFull_estimatedCounts.tsv"
        )

    try:
        df_sunburst = pd.read_csv(big_tsv_path, sep="\t")
        # Suppose 'Taxa' has a semi-colon separated taxonomy chain
        splitted = df_sunburst["Taxa"].str.split(";", expand=True)
        # Possibly up to 7 levels
        taxonomy_levels = ["Domain", "Phylum", "Class", "Order", "Family", "Genus", "Species"]
        splitted.columns = taxonomy_levels[:splitted.shape[1]]
        df_sunburst = pd.concat([splitted, df_sunburst.drop("Taxa", axis=1)], axis=1)
    except Exception as e:
        return JsonResponse({"error": f"Error loading sunburst data: {e}"}, status=500)

    # 2) Handle AJAX (single-var, multi-var) => top 100
    if request.headers.get("x-requested-with") == "XMLHttpRequest":

        # (A) load_tissue => returns list of variables
        if "load_tissue" in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files_ileum:
                return JsonResponse({"error": f"Invalid tissue: {tissue}"}, status=400)
            try:
                csv_path = os.path.join(
                    settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                    tissue_files_ileum[tissue]
                )
                df_small = pd.read_csv(csv_path)
                variables = df_small.columns[2:].tolist()
                return JsonResponse({"variables": variables})
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV: {e}"}, status=500)

        # (B) Single-var => includes fetch_min_max + filter
        elif "multi_variable" not in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files_ileum:
                return JsonResponse({"results": [], "error": "Missing or invalid tissue."}, status=400)
            csv_path = os.path.join(
                settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                tissue_files_ileum[tissue]
            )

            try:
                df_all = pd.read_csv(csv_path)
                variables = df_all.columns[2:].tolist()
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV: {e}"}, status=500)

            selected_variable = request.GET.get("variable", variables[0] if variables else None)
            if selected_variable not in variables:
                return JsonResponse({"results": [], "error": "Invalid variable selected."}, status=400)

            # B1) fetch_min_max
            if "fetch_min_max" in request.GET:
                try:
                    col_vals = df_all[selected_variable].dropna()
                    return JsonResponse({
                        "min_correlation": float(col_vals.min()),
                        "max_correlation": float(col_vals.max()),
                    })
                except Exception as e:
                    return JsonResponse({"error": f"Error fetching min/max: {e}"}, status=500)

            # B2) filter => top 100
            try:
                correlation_min = float(request.GET.get("correlation_min", -1))
                correlation_max = float(request.GET.get("correlation_max", 1))
                min_accuracy = float(request.GET.get("accuracy", 0))

                if correlation_min > correlation_max:
                    return JsonResponse({"error": "Min correlation cannot exceed max correlation."}, status=400)

                filtered = df_all[
                    (df_all["accuracy"] >= min_accuracy)
                    & (df_all[selected_variable] >= correlation_min)
                    & (df_all[selected_variable] <= correlation_max)
                ]
                if filtered.empty:
                    return JsonResponse({"results": [], "total_count": 0})

                filtered.sort_values(by=selected_variable, ascending=False, inplace=True)
                total_count = len(filtered)
                top_100 = filtered.head(100)

                first_col = df_all.columns[0]
                results_list = []
                for _, row in top_100.iterrows():
                    results_list.append({
                        "var1": row[first_col],
                        "var2": selected_variable,
                        "accuracy": row["accuracy"],
                        "correlation": row[selected_variable]
                    })

                return JsonResponse({"results": results_list, "total_count": total_count})
            except Exception as e:
                return JsonResponse({"error": f"Error during single-var filter: {e}"}, status=500)

        # (C) Multi-var => top 100
        elif "multi_variable" in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files_ileum:
                return JsonResponse({"results": [], "error": "Missing or invalid tissue."}, status=400)

            variables = request.GET.getlist("variables[]")
            if not variables:
                return JsonResponse({"results": [], "error": "No variables selected."}, status=400)

            csv_path = os.path.join(
                settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                tissue_files_ileum[tissue]
            )
            try:
                df_all = pd.read_csv(csv_path)
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV file: {e}"}, status=500)

            try:
                correlation_min = float(request.GET.get("correlation_min", -1))
                correlation_max = float(request.GET.get("correlation_max", 1))
                min_accuracy = float(request.GET.get("accuracy", 0))
                if correlation_min > correlation_max:
                    return JsonResponse({"error": "Min correlation cannot exceed max correlation."}, status=400)

                filtered_parts = []
                first_col = df_all.columns[0]
                for var in variables:
                    if var not in df_all.columns:
                        continue
                    sub = df_all[
                        (df_all["accuracy"] >= min_accuracy)
                        & (df_all[var] >= correlation_min)
                        & (df_all[var] <= correlation_max)
                    ].copy()
                    if not sub.empty:
                        sub["var2"] = var
                        filtered_parts.append(sub)

                if not filtered_parts:
                    return JsonResponse({"results": [], "total_count": 0})

                combined = pd.concat(filtered_parts, ignore_index=True)
                corvals = []
                for _, row in combined.iterrows():
                    corvals.append(row[row["var2"]])
                combined["correlation"] = corvals

                combined.drop_duplicates(subset=[first_col, "var2"], inplace=True)
                combined.sort_values(by="correlation", ascending=False, inplace=True)
                total_count = len(combined)

                top_100 = combined.head(100)
                results_list = []
                for _, row in top_100.iterrows():
                    results_list.append({
                        "var1": row[first_col],
                        "var2": row["var2"],
                        "accuracy": row["accuracy"],
                        "correlation": row["correlation"]
                    })

                return JsonResponse({"results": results_list, "total_count": total_count})
            except Exception as e:
                return JsonResponse({"error": f"Error during multi-var filter: {e}"}, status=500)

        # If none matched
        return JsonResponse({"error":"No recognized AJAX action."}, status=400)

    # 3) Build the sunbursts for 0.5 & 0.6
    cluster_data_0_4 = [['ENSGALG00010000369', 'ENSGALG00010000239', 'ENSGALG00010000358', 'ENSGALG00010000246', 'ENSGALG00010000326', 'ENSGALG00010012336', 'ENSGALG00010000249', 'ENSGALG00010013702', 'ENSGALG00010011857', 'ENSGALG00010011555', 'ENSGALG00010000309'], ['ENSGALG00010005481', 'ENSGALG00010000318', 'ENSGALG00010012927', 'ENSGALG00010000354', 'ENSGALG00010012781', 'ENSGALG00010000313', 'ENSGALG00010000282', 'ENSGALG00010013706', 'ENSGALG00010011467'], ['ENSGALG00010003614', 'ENSGALG00010003644', 'ENSGALG00010003646', 'ENSGALG00010003635', 'ENSGALG00010003643', 'ENSGALG00010003623', 'ENSGALG00010003613', 'ENSGALG00010003625', 'ENSGALG00010003640'], ['ENSGALG00010003565', 'ENSGALG00010003584', 'ENSGALG00010003563', 'ENSGALG00010003575', 'ENSGALG00010003537', 'ENSGALG00010003598', 'ENSGALG00010003529', 'ENSGALG00010003576'], ['ENSGALG00010012212', 'ENSGALG00010006345', 'ENSGALG00010002814', 'ENSGALG00010000859', 'ENSGALG00010002437', 'ENSGALG00010007038'], ['ENSGALG00010013950', 'ENSGALG00010023025', 'ENSGALG00010019862', 'ENSGALG00010018778', 'ENSGALG00010007736', 'ENSGALG00010004169'], ['ENSGALG00010004938', 'ENSGALG00010015531', 'ENSGALG00010006725', 'ENSGALG00010018789', 'ENSGALG00010007061'], ['ENSGALG00010006935', 'ENSGALG00010007268', 'ENSGALG00010013049', 'ENSGALG00010003188', 'ENSGALG00010000968'], ['ENSGALG00010013151', 'ENSGALG00010009922', 'ENSGALG00010012494', 'ENSGALG00010006950', 'ENSGALG00010015775'], ['ENSGALG00010013567', 'ENSGALG00010015575', 'ENSGALG00010004208', 'ENSGALG00010012840', 'ENSGALG00010002797']]

    cluster_data_0_3 =  [['ENSGALG00010003644', 'ENSGALG00010003584', 'ENSGALG00010003646', 'ENSGALG00010003635', 'ENSGALG00010003643', 'ENSGALG00010003537', 'ENSGALG00010003598', 'ENSGALG00010003640', 'ENSGALG00010003576', 'ENSGALG00010003565', 'ENSGALG00010003614', 'ENSGALG00010003563', 'ENSGALG00010003575', 'ENSGALG00010003613', 'ENSGALG00010003623', 'ENSGALG00010003625', 'ENSGALG00010003529'], ['ENSGALG00010000369', 'ENSGALG00010000239', 'ENSGALG00010000358', 'ENSGALG00010000246', 'ENSGALG00010000326', 'ENSGALG00010012336', 'ENSGALG00010000249', 'ENSGALG00010013702', 'ENSGALG00010011857', 'ENSGALG00010011555', 'ENSGALG00010000309'], ['ENSGALG00010007147', 'ENSGALG00010020566', 'ENSGALG00010005005', 'ENSGALG00010013879', 'ENSGALG00010016272', 'ENSGALG00010004331', 'ENSGALG00010020188', 'ENSGALG00010014786', 'ENSGALG00010020349'], ['ENSGALG00010002269', 'ENSGALG00010012212', 'ENSGALG00010006345', 'ENSGALG00010002814', 'ENSGALG00010002437', 'ENSGALG00010021342', 'ENSGALG00010000859', 'ENSGALG00010007038', 'ENSGALG00010022098'], ['ENSGALG00010005481', 'ENSGALG00010000318', 'ENSGALG00010012927', 'ENSGALG00010000354', 'ENSGALG00010012781', 'ENSGALG00010000313', 'ENSGALG00010000282', 'ENSGALG00010013706', 'ENSGALG00010011467'], ['ENSGALG00010018845', 'ENSGALG00010004435', 'ENSGALG00010029472', 'ENSGALG00010010739', 'ENSGALG00010017298', 'ENSGALG00010027000', 'ENSGALG00010010563'], ['ENSGALG00010011821', 'ENSGALG00010014495', 'ENSGALG00010019286', 'ENSGALG00010013571', 'ENSGALG00010006303', 'ENSGALG00010011370', 'ENSGALG00010011219'], ['ENSGALG00010019749', 'ENSGALG00010008845', 'ENSGALG00010010249', 'ENSGALG00010011933', 'ENSGALG00010015609', 'ENSGALG00010009075', 'ENSGALG00010028505'], ['ENSGALG00010027048', 'ENSGALG00010021910', 'ENSGALG00010005343', 'ENSGALG00010004565', 'ENSGALG00010017014', 'ENSGALG00010019849'], ['ENSGALG00010013950', 'ENSGALG00010023025', 'ENSGALG00010019862', 'ENSGALG00010018778', 'ENSGALG00010007736', 'ENSGALG00010004169'], ['ENSGALG00010019707', 'ENSGALG00010025255', 'ENSGALG00010028699', 'ENSGALG00010017481', 'ENSGALG00010002392', 'ENSGALG00010000626'], ['ENSGALG00010012604', 'ENSGALG00010011339', 'ENSGALG00010013778', 'ENSGALG00010003609', 'ENSGALG00010020480', 'ENSGALG00010005593'], ['ENSGALG00010019133', 'ENSGALG00010021921', 'ENSGALG00010021299', 'ENSGALG00010004694', 'ENSGALG00010019251', 'ENSGALG00010019729'], ['ENSGALG00010014044', 'ENSGALG00010003482', 'ENSGALG00010005192', 'ENSGALG00010003556', 'ENSGALG00010009165', 'ENSGALG00010004945'], ['ENSGALG00010027127', 'ENSGALG00010007994', 'ENSGALG00010029632', 'ENSGALG00010024583', 'ENSGALG00010028467', 'ENSGALG00010005585'], ['ENSGALG00010009098', 'ENSGALG00010024989', 'ENSGALG00010023828', 'ENSGALG00010024548', 'ENSGALG00010013793', 'ENSGALG00010024563'], ['ENSGALG00010003587', 'ENSGALG00010003363', 'ENSGALG00010008539', 'ENSGALG00010005816', 'ENSGALG00010012306', 'ENSGALG00010018888'], ['ENSGALG00010021256', 'ENSGALG00010022747', 'ENSGALG00010006172', 'ENSGALG00010023172', 'ENSGALG00010003019', 'ENSGALG00010026316'], ['ENSGALG00010004692', 'ENSGALG00010019809', 'ENSGALG00010001039', 'ENSGALG00010013730', 'ENSGALG00010002731', 'ENSGALG00010006511'], ['ENSGALG00010013151', 'ENSGALG00010009293', 'ENSGALG00010009922', 'ENSGALG00010012494', 'ENSGALG00010006950', 'ENSGALG00010015775'], ['ENSGALG00010019528', 'ENSGALG00010016717', 'ENSGALG00010008868', 'ENSGALG00010016196', 'ENSGALG00010027456', 'ENSGALG00010014616'], ['ENSGALG00010020357', 'ENSGALG00010001901', 'ENSGALG00010008132', 'ENSGALG00010014944', 'ENSGALG00010005070', 'ENSGALG00010006069'], ['ENSGALG00010009046', 'ENSGALG00010025978', 'ENSGALG00010010540', 'ENSGALG00010006733', 'ENSGALG00010008611', 'ENSGALG00010006990'], ['ENSGALG00010013980', 'ENSGALG00010015205', 'ENSGALG00010020315', 'ENSGALG00010016119', 'ENSGALG00010006035', 'ENSGALG00010021522'], ['ENSGALG00010008908', 'ENSGALG00010016084', 'ENSGALG00010007291', 'ENSGALG00010007015', 'ENSGALG00010013738'], ['ENSGALG00010008043', 'ENSGALG00010010893', 'ENSGALG00010005314', 'ENSGALG00010012847', 'ENSGALG00010021983'], ['ENSGALG00010017162', 'ENSGALG00010019684', 'ENSGALG00010024003', 'ENSGALG00010014193', 'ENSGALG00010029255'], ['ENSGALG00010010328', 'ENSGALG00010015394', 'ENSGALG00010005967', 'ENSGALG00010024550', 'ENSGALG00010013496'], ['ENSGALG00010013718', 'ENSGALG00010023899', 'ENSGALG00010009845', 'ENSGALG00010023323', 'ENSGALG00010003093'], ['ENSGALG00010022369', 'ENSGALG00010004742', 'ENSGALG00010013059', 'ENSGALG00010002563', 'ENSGALG00010019044'], ['ENSGALG00010006695', 'ENSGALG00010019241', 'ENSGALG00010011083', 'ENSGALG00010022156', 'ENSGALG00010003421'], ['ENSGALG00010004938', 'ENSGALG00010015531', 'ENSGALG00010006725', 'ENSGALG00010018789', 'ENSGALG00010007061'], ['ENSGALG00010024121', 'ENSGALG00010025839', 'ENSGALG00010016164', 'ENSGALG00010014013', 'ENSGALG00010001538'], ['ENSGALG00010022350', 'ENSGALG00010011194', 'ENSGALG00010020372', 'ENSGALG00010013540', 'ENSGALG00010023619'], ['ENSGALG00010000956', 'ENSGALG00010013819', 'ENSGALG00010005781', 'ENSGALG00010006662', 'ENSGALG00010009729'], ['ENSGALG00010024126', 'ENSGALG00010024078', 'ENSGALG00010020613', 'ENSGALG00010017346', 'ENSGALG00010018823'], ['ENSGALG00010021499', 'ENSGALG00010009865', 'ENSGALG00010017370', 'ENSGALG00010015757', 'ENSGALG00010008061'], ['ENSGALG00010022963', 'ENSGALG00010008367', 'ENSGALG00010011411', 'ENSGALG00010024366', 'ENSGALG00010027708'], ['ENSGALG00010011911', 'ENSGALG00010009595', 'ENSGALG00010007847', 'ENSGALG00010006851', 'ENSGALG00010007765'], ['ENSGALG00010004563', 'ENSGALG00010010656', 'ENSGALG00010018798', 'ENSGALG00010013279', 'ENSGALG00010016226'], ['ENSGALG00010013567', 'ENSGALG00010015575', 'ENSGALG00010004208', 'ENSGALG00010012840', 'ENSGALG00010002797'], ['ENSGALG00010022101', 'ENSGALG00010028169', 'ENSGALG00010029527', 'ENSGALG00010023447', 'ENSGALG00010024427'], ['ENSGALG00010004201', 'ENSGALG00010007958', 'ENSGALG00010015154', 'ENSGALG00010009096', 'ENSGALG00010008676'], ['ENSGALG00010003520', 'ENSGALG00010026158', 'ENSGALG00010000094', 'ENSGALG00010006722', 'ENSGALG00010023006'], ['ENSGALG00010025478', 'ENSGALG00010005640', 'ENSGALG00010011877', 'ENSGALG00010002559', 'ENSGALG00010017474'], ['ENSGALG00010006729', 'ENSGALG00010007722', 'ENSGALG00010007652', 'ENSGALG00010014422', 'ENSGALG00010010583'], ['ENSGALG00010029113', 'ENSGALG00010019754', 'ENSGALG00010011771', 'ENSGALG00010020508', 'ENSGALG00010006938'], ['ENSGALG00010006935', 'ENSGALG00010007268', 'ENSGALG00010013049', 'ENSGALG00010003188', 'ENSGALG00010000968'], ['ENSGALG00010022416', 'ENSGALG00010023773', 'ENSGALG00010003761', 'ENSGALG00010023181', 'ENSGALG00010022406'], ['ENSGALG00010007790', 'ENSGALG00010025973', 'ENSGALG00010012789', 'ENSGALG00010004448', 'ENSGALG00010007119'], ['ENSGALG00010007429', 'ENSGALG00010021521', 'ENSGALG00010019051', 'ENSGALG00010002921', 'ENSGALG00010027337'], ['ENSGALG00010010598', 'ENSGALG00010001331', 'ENSGALG00010009751', 'ENSGALG00010003369', 'ENSGALG00010010314'], ['ENSGALG00010004915', 'ENSGALG00010004490', 'ENSGALG00010012319', 'ENSGALG00010001063', 'ENSGALG00010006114'], ['ENSGALG00010011539', 'ENSGALG00010012366', 'ENSGALG00010029147', 'ENSGALG00010021903', 'ENSGALG00010025341'], ['ENSGALG00010011111', 'ENSGALG00010026232', 'ENSGALG00010029259', 'ENSGALG00010013277', 'ENSGALG00010026088']]

    cluster_data_0_2 = [['ENSGALG00010003644', 'ENSGALG00010003584', 'ENSGALG00010003646', 'ENSGALG00010003635', 'ENSGALG00010003643', 'ENSGALG00010003537', 'ENSGALG00010003598', 'ENSGALG00010003640', 'ENSGALG00010003576', 'ENSGALG00010003565', 'ENSGALG00010003614', 'ENSGALG00010003563', 'ENSGALG00010003575', 'ENSGALG00010003613', 'ENSGALG00010003623', 'ENSGALG00010003625', 'ENSGALG00010003529'], ['ENSGALG00010011339', 'ENSGALG00010003287', 'ENSGALG00010005140', 'ENSGALG00010012860', 'ENSGALG00010020937', 'ENSGALG00010005593', 'ENSGALG00010012604', 'ENSGALG00010003605', 'ENSGALG00010014742', 'ENSGALG00010013134', 'ENSGALG00010013778', 'ENSGALG00010003609', 'ENSGALG00010011473', 'ENSGALG00010020480'], ['ENSGALG00010023640', 'ENSGALG00010003932', 'ENSGALG00010005556', 'ENSGALG00010029155', 'ENSGALG00010028831', 'ENSGALG00010020326', 'ENSGALG00010001357', 'ENSGALG00010009944', 'ENSGALG00010022940', 'ENSGALG00010023467', 'ENSGALG00010023370'], ['ENSGALG00010000369', 'ENSGALG00010000239', 'ENSGALG00010000358', 'ENSGALG00010000246', 'ENSGALG00010000326', 'ENSGALG00010012336', 'ENSGALG00010000249', 'ENSGALG00010013702', 'ENSGALG00010011857', 'ENSGALG00010011555', 'ENSGALG00010000309'], ['ENSGALG00010019528', 'ENSGALG00010016717', 'ENSGALG00010029981', 'ENSGALG00010006734', 'ENSGALG00010016196', 'ENSGALG00010012385', 'ENSGALG00010008868', 'ENSGALG00010023608', 'ENSGALG00010018065', 'ENSGALG00010027456', 'ENSGALG00010014616'], ['ENSGALG00010027765', 'ENSGALG00010026961', 'ENSGALG00010017016', 'ENSGALG00010024838', 'ENSGALG00010027472', 'ENSGALG00010014498', 'ENSGALG00010025332', 'ENSGALG00010012478', 'ENSGALG00010007845', 'ENSGALG00010014177', 'ENSGALG00010003359'], ['ENSGALG00010004504', 'ENSGALG00010023647', 'ENSGALG00010009189', 'ENSGALG00010012545', 'ENSGALG00010013188', 'ENSGALG00010023174', 'ENSGALG00010006555', 'ENSGALG00010002898', 'ENSGALG00010006186', 'ENSGALG00010028470', 'ENSGALG00010024684'], ['ENSGALG00010004938', 'ENSGALG00010006725', 'ENSGALG00010008601', 'ENSGALG00010007061', 'ENSGALG00010018789', 'ENSGALG00010021808', 'ENSGALG00010015531', 'ENSGALG00010026383', 'ENSGALG00010023988', 'ENSGALG00010002607'], ['ENSGALG00010000646', 'ENSGALG00010025666', 'ENSGALG00010002611', 'ENSGALG00010016860', 'ENSGALG00010005419', 'ENSGALG00010009978', 'ENSGALG00010003297', 'ENSGALG00010018098', 'ENSGALG00010027133', 'ENSGALG00010020591'], ['ENSGALG00010014176', 'ENSGALG00010029841', 'ENSGALG00010003215', 'ENSGALG00010020946', 'ENSGALG00010009619', 'ENSGALG00010007089', 'ENSGALG00010006119', 'ENSGALG00010014619', 'ENSGALG00010006726', 'ENSGALG00010016795'], ['ENSGALG00010000497', 'ENSGALG00010012448', 'ENSGALG00010000892', 'ENSGALG00010011168', 'ENSGALG00010014598', 'ENSGALG00010022564', 'ENSGALG00010007293', 'ENSGALG00010020347', 'ENSGALG00010011727', 'ENSGALG00010018850'], ['ENSGALG00010020357', 'ENSGALG00010017466', 'ENSGALG00010001901', 'ENSGALG00010023724', 'ENSGALG00010008132', 'ENSGALG00010023054', 'ENSGALG00010006069', 'ENSGALG00010028079', 'ENSGALG00010005070', 'ENSGALG00010014944'], ['ENSGALG00010013450', 'ENSGALG00010025925', 'ENSGALG00010016511', 'ENSGALG00010013315', 'ENSGALG00010016312', 'ENSGALG00010014347', 'ENSGALG00010023183', 'ENSGALG00010024892', 'ENSGALG00010003830', 'ENSGALG00010022322'], ['ENSGALG00010001231', 'ENSGALG00010013977', 'ENSGALG00010015616', 'ENSGALG00010014971', 'ENSGALG00010020106', 'ENSGALG00010012001', 'ENSGALG00010012163', 'ENSGALG00010006480', 'ENSGALG00010020568', 'ENSGALG00010009985'], ['ENSGALG00010002950', 'ENSGALG00010008597', 'ENSGALG00010013683', 'ENSGALG00010006925', 'ENSGALG00010015396', 'ENSGALG00010000896', 'ENSGALG00010015011', 'ENSGALG00010015223', 'ENSGALG00010011752', 'ENSGALG00010008777'], ['ENSGALG00010001288', 'ENSGALG00010009910', 'ENSGALG00010012964', 'ENSGALG00010026534', 'ENSGALG00010013086', 'ENSGALG00010006953', 'ENSGALG00010014244', 'ENSGALG00010011907', 'ENSGALG00010022695'], ['ENSGALG00010005813', 'ENSGALG00010025177', 'ENSGALG00010014845', 'ENSGALG00010005885', 'ENSGALG00010020600', 'ENSGALG00010025859', 'ENSGALG00010004084', 'ENSGALG00010005865', 'ENSGALG00010007271'], ['ENSGALG00010005481', 'ENSGALG00010000318', 'ENSGALG00010012927', 'ENSGALG00010000354', 'ENSGALG00010012781', 'ENSGALG00010000313', 'ENSGALG00010000282', 'ENSGALG00010013706', 'ENSGALG00010011467'], ['ENSGALG00010011486', 'ENSGALG00010005871', 'ENSGALG00010021536', 'ENSGALG00010017152', 'ENSGALG00010005743', 'ENSGALG00010016771', 'ENSGALG00010001883', 'ENSGALG00010013201', 'ENSGALG00010018807'], ['ENSGALG00010014207', 'ENSGALG00010025804', 'ENSGALG00010003538', 'ENSGALG00010010856', 'ENSGALG00010004815', 'ENSGALG00010008751', 'ENSGALG00010006984', 'ENSGALG00010026122', 'ENSGALG00010000192'], ['ENSGALG00010004321', 'ENSGALG00010022785', 'ENSGALG00010006565', 'ENSGALG00010023745', 'ENSGALG00010014524', 'ENSGALG00010003347', 'ENSGALG00010019562', 'ENSGALG00010027042', 'ENSGALG00010012374'], ['ENSGALG00010004915', 'ENSGALG00010023753', 'ENSGALG00010023302', 'ENSGALG00010004490', 'ENSGALG00010006114', 'ENSGALG00010019075', 'ENSGALG00010016162', 'ENSGALG00010012319', 'ENSGALG00010001063'], ['ENSGALG00010007147', 'ENSGALG00010020566', 'ENSGALG00010005005', 'ENSGALG00010013879', 'ENSGALG00010016272', 'ENSGALG00010004331', 'ENSGALG00010020188', 'ENSGALG00010014786', 'ENSGALG00010020349'], ['ENSGALG00010022101', 'ENSGALG00010028169', 'ENSGALG00010029527', 'ENSGALG00010024427', 'ENSGALG00010010051', 'ENSGALG00010011443', 'ENSGALG00010024759', 'ENSGALG00010023447', 'ENSGALG00010027388'], ['ENSGALG00010002269', 'ENSGALG00010012212', 'ENSGALG00010006345', 'ENSGALG00010002814', 'ENSGALG00010002437', 'ENSGALG00010021342', 'ENSGALG00010000859', 'ENSGALG00010007038', 'ENSGALG00010022098'], ['ENSGALG00010023667', 'ENSGALG00010004634', 'ENSGALG00010008463', 'ENSGALG00010009324', 'ENSGALG00010018366', 'ENSGALG00010020251', 'ENSGALG00010025483', 'ENSGALG00010009285', 'ENSGALG00010010114'], ['ENSGALG00010007794', 'ENSGALG00010012065', 'ENSGALG00010007219', 'ENSGALG00010023691', 'ENSGALG00010000847', 'ENSGALG00010003514', 'ENSGALG00010003284', 'ENSGALG00010004517', 'ENSGALG00010008851'], ['ENSGALG00010022963', 'ENSGALG00010011411', 'ENSGALG00010013701', 'ENSGALG00010024366', 'ENSGALG00010027708', 'ENSGALG00010008367', 'ENSGALG00010002981', 'ENSGALG00010022882', 'ENSGALG00010018178'], ['ENSGALG00010007857', 'ENSGALG00010016386', 'ENSGALG00010012030', 'ENSGALG00010002669', 'ENSGALG00010012743', 'ENSGALG00010000791', 'ENSGALG00010021372', 'ENSGALG00010013573', 'ENSGALG00010028872'], ['ENSGALG00010022007', 'ENSGALG00010025478', 'ENSGALG00010005640', 'ENSGALG00010011877', 'ENSGALG00010002559', 'ENSGALG00010011206', 'ENSGALG00010007205', 'ENSGALG00010002230', 'ENSGALG00010017474'], ['ENSGALG00010003587', 'ENSGALG00010018962', 'ENSGALG00010003363', 'ENSGALG00010008539', 'ENSGALG00010005816', 'ENSGALG00010023072', 'ENSGALG00010012306', 'ENSGALG00010018888', 'ENSGALG00010009599'], ['ENSGALG00010010731', 'ENSGALG00010008545', 'ENSGALG00010025124', 'ENSGALG00010012584', 'ENSGALG00010007738', 'ENSGALG00010003151', 'ENSGALG00010002695', 'ENSGALG00010014627', 'ENSGALG00010006605'], ['ENSGALG00010000956', 'ENSGALG00010013099', 'ENSGALG00010006662', 'ENSGALG00010009729', 'ENSGALG00010005781', 'ENSGALG00010011032', 'ENSGALG00010019338', 'ENSGALG00010013819', 'ENSGALG00010008591'], ['ENSGALG00010013567', 'ENSGALG00010004647', 'ENSGALG00010006385', 'ENSGALG00010002797', 'ENSGALG00010002021', 'ENSGALG00010015575', 'ENSGALG00010004208', 'ENSGALG00010009893', 'ENSGALG00010012840'], ['ENSGALG00010026550', 'ENSGALG00010015563', 'ENSGALG00010029673', 'ENSGALG00010003681', 'ENSGALG00010006387', 'ENSGALG00010021725', 'ENSGALG00010009486', 'ENSGALG00010005472', 'ENSGALG00010014928'], ['ENSGALG00010002861', 'ENSGALG00010027655', 'ENSGALG00010028331', 'ENSGALG00010002945', 'ENSGALG00010001005', 'ENSGALG00010025261', 'ENSGALG00010002297', 'ENSGALG00010023535', 'ENSGALG00010020647'], ['ENSGALG00010006879', 'ENSGALG00010029208', 'ENSGALG00010015120', 'ENSGALG00010027544', 'ENSGALG00010025675', 'ENSGALG00010014113', 'ENSGALG00010019651', 'ENSGALG00010008566', 'ENSGALG00010001670'], ['ENSGALG00010026158', 'ENSGALG00010006722', 'ENSGALG00010013957', 'ENSGALG00010000293', 'ENSGALG00010001827', 'ENSGALG00010003520', 'ENSGALG00010000094', 'ENSGALG00010023006'], ['ENSGALG00010006981', 'ENSGALG00010023986', 'ENSGALG00010011679', 'ENSGALG00010007269', 'ENSGALG00010010194', 'ENSGALG00010024455', 'ENSGALG00010012465', 'ENSGALG00010019877'], ['ENSGALG00010019873', 'ENSGALG00010013772', 'ENSGALG00010019012', 'ENSGALG00010019932', 'ENSGALG00010011359', 'ENSGALG00010004312', 'ENSGALG00010005404', 'ENSGALG00010009159'], ['ENSGALG00010022411', 'ENSGALG00010001779', 'ENSGALG00010020399', 'ENSGALG00010023955', 'ENSGALG00010027630', 'ENSGALG00010014048', 'ENSGALG00010021924', 'ENSGALG00010011274'], ['ENSGALG00010023828', 'ENSGALG00010018279', 'ENSGALG00010013793', 'ENSGALG00010009098', 'ENSGALG00010024563', 'ENSGALG00010024989', 'ENSGALG00010024548', 'ENSGALG00010000338'], ['ENSGALG00010008197', 'ENSGALG00010012919', 'ENSGALG00010022731', 'ENSGALG00010010547', 'ENSGALG00010024129', 'ENSGALG00010004684', 'ENSGALG00010016991', 'ENSGALG00010026350'], ['ENSGALG00010006695', 'ENSGALG00010007583', 'ENSGALG00010016032', 'ENSGALG00010022156', 'ENSGALG00010003421', 'ENSGALG00010019241', 'ENSGALG00010011083', 'ENSGALG00010005896'], ['ENSGALG00010004854', 'ENSGALG00010002741', 'ENSGALG00010029265', 'ENSGALG00010026627', 'ENSGALG00010002740', 'ENSGALG00010014540', 'ENSGALG00010014946', 'ENSGALG00010008084'], ['ENSGALG00010013280', 'ENSGALG00010019116', 'ENSGALG00010024668', 'ENSGALG00010017937', 'ENSGALG00010022400', 'ENSGALG00010012672', 'ENSGALG00010022149', 'ENSGALG00010016218'], ['ENSGALG00010019841', 'ENSGALG00010027817', 'ENSGALG00010003445', 'ENSGALG00010006115', 'ENSGALG00010004783', 'ENSGALG00010022017', 'ENSGALG00010008270', 'ENSGALG00010013978'], ['ENSGALG00010009595', 'ENSGALG00010001629', 'ENSGALG00010007847', 'ENSGALG00010011203', 'ENSGALG00010006851', 'ENSGALG00010011911', 'ENSGALG00010029279', 'ENSGALG00010007765'], ['ENSGALG00010013880', 'ENSGALG00010004868', 'ENSGALG00010013209', 'ENSGALG00010013299', 'ENSGALG00010008346', 'ENSGALG00010019257', 'ENSGALG00010011210', 'ENSGALG00010013964'], ['ENSGALG00010005028', 'ENSGALG00010018953', 'ENSGALG00010005928', 'ENSGALG00010011701', 'ENSGALG00010005754', 'ENSGALG00010026450', 'ENSGALG00010009134', 'ENSGALG00010029873'], ['ENSGALG00010008997', 'ENSGALG00010009462', 'ENSGALG00010015466', 'ENSGALG00010009874', 'ENSGALG00010007724', 'ENSGALG00010011795', 'ENSGALG00010024764', 'ENSGALG00010013117'], ['ENSGALG00010009780', 'ENSGALG00010005673', 'ENSGALG00010003890', 'ENSGALG00010013647', 'ENSGALG00010012098', 'ENSGALG00010010255', 'ENSGALG00010011200', 'ENSGALG00010028031'], ['ENSGALG00010030013', 'ENSGALG00010012330', 'ENSGALG00010016336', 'ENSGALG00010006393', 'ENSGALG00010023227', 'ENSGALG00010019561', 'ENSGALG00010020698', 'ENSGALG00010026749'], ['ENSGALG00010023088', 'ENSGALG00010006807', 'ENSGALG00010011542', 'ENSGALG00010020731', 'ENSGALG00010011199', 'ENSGALG00010006003', 'ENSGALG00010006258', 'ENSGALG00010019685'], ['ENSGALG00010011834', 'ENSGALG00010014036', 'ENSGALG00010011197', 'ENSGALG00010015586', 'ENSGALG00010015996', 'ENSGALG00010014271', 'ENSGALG00010015387', 'ENSGALG00010003493'], ['ENSGALG00010010225', 'ENSGALG00010001103', 'ENSGALG00010016318', 'ENSGALG00010001387', 'ENSGALG00010006656', 'ENSGALG00010003492', 'ENSGALG00010026728', 'ENSGALG00010008962'], ['ENSGALG00010020919', 'ENSGALG00010015794', 'ENSGALG00010024273', 'ENSGALG00010013507', 'ENSGALG00010008643', 'ENSGALG00010023735', 'ENSGALG00010020639', 'ENSGALG00010019765'], ['ENSGALG00010014702', 'ENSGALG00010028173', 'ENSGALG00010000302', 'ENSGALG00010023598', 'ENSGALG00010000427', 'ENSGALG00010002136', 'ENSGALG00010019799', 'ENSGALG00010014813'], ['ENSGALG00010016385', 'ENSGALG00010016894', 'ENSGALG00010029534', 'ENSGALG00010011883', 'ENSGALG00010006073', 'ENSGALG00010003271', 'ENSGALG00010020486', 'ENSGALG00010015614'], ['ENSGALG00010019931', 'ENSGALG00010029226', 'ENSGALG00010029418', 'ENSGALG00010020489', 'ENSGALG00010013679', 'ENSGALG00010028762', 'ENSGALG00010012670', 'ENSGALG00010018436'], ['ENSGALG00010021256', 'ENSGALG00010027634', 'ENSGALG00010006172', 'ENSGALG00010028022', 'ENSGALG00010022747', 'ENSGALG00010023172', 'ENSGALG00010003019', 'ENSGALG00010026316'], ['ENSGALG00010028894', 'ENSGALG00010023196', 'ENSGALG00010029583', 'ENSGALG00010009299', 'ENSGALG00010025252', 'ENSGALG00010021154', 'ENSGALG00010017349', 'ENSGALG00010001406'], ['ENSGALG00010012764', 'ENSGALG00010001565', 'ENSGALG00010016467', 'ENSGALG00010029083', 'ENSGALG00010026503', 'ENSGALG00010018169', 'ENSGALG00010019851', 'ENSGALG00010009014'], ['ENSGALG00010007778', 'ENSGALG00010026238', 'ENSGALG00010011624', 'ENSGALG00010000925', 'ENSGALG00010006703', 'ENSGALG00010011684', 'ENSGALG00010006349', 'ENSGALG00010001472'], ['ENSGALG00010028186', 'ENSGALG00010000341', 'ENSGALG00010000584', 'ENSGALG00010002432', 'ENSGALG00010003882', 'ENSGALG00010000398', 'ENSGALG00010002857', 'ENSGALG00010000581'], ['ENSGALG00010026555', 'ENSGALG00010006213', 'ENSGALG00010029096', 'ENSGALG00010009438', 'ENSGALG00010021547', 'ENSGALG00010026408', 'ENSGALG00010009604', 'ENSGALG00010014623'], ['ENSGALG00010025169', 'ENSGALG00010015262', 'ENSGALG00010015519', 'ENSGALG00010014652', 'ENSGALG00010001151', 'ENSGALG00010023463', 'ENSGALG00010007901', 'ENSGALG00010018347'], ['ENSGALG00010002978', 'ENSGALG00010002625', 'ENSGALG00010005535', 'ENSGALG00010000741', 'ENSGALG00010013403', 'ENSGALG00010012778', 'ENSGALG00010011294', 'ENSGALG00010011457'], ['ENSGALG00010027613', 'ENSGALG00010014239', 'ENSGALG00010004566', 'ENSGALG00010014978', 'ENSGALG00010024411', 'ENSGALG00010029819', 'ENSGALG00010019917', 'ENSGALG00010004909'], ['ENSGALG00010004692', 'ENSGALG00010019809', 'ENSGALG00010006511', 'ENSGALG00010002731', 'ENSGALG00010013730', 'ENSGALG00010001039', 'ENSGALG00010003618', 'ENSGALG00010018151'], ['ENSGALG00010027354', 'ENSGALG00010000273', 'ENSGALG00010010430', 'ENSGALG00010000418', 'ENSGALG00010029818', 'ENSGALG00010000692', 'ENSGALG00010021262', 'ENSGALG00010004090'], ['ENSGALG00010013833', 'ENSGALG00010023612', 'ENSGALG00010010110', 'ENSGALG00010003456', 'ENSGALG00010010599', 'ENSGALG00010003407', 'ENSGALG00010001470', 'ENSGALG00010024005'], ['ENSGALG00010019522', 'ENSGALG00010015273', 'ENSGALG00010029113', 'ENSGALG00010019672', 'ENSGALG00010019754', 'ENSGALG00010011771', 'ENSGALG00010020508', 'ENSGALG00010006938'], ['ENSGALG00010017719', 'ENSGALG00010025561', 'ENSGALG00010005507', 'ENSGALG00010017731', 'ENSGALG00010002935', 'ENSGALG00010026526', 'ENSGALG00010001908', 'ENSGALG00010017736'], ['ENSGALG00010021991', 'ENSGALG00010021499', 'ENSGALG00010000909', 'ENSGALG00010017370', 'ENSGALG00010015757', 'ENSGALG00010014322', 'ENSGALG00010008061', 'ENSGALG00010009865'], ['ENSGALG00010006922', 'ENSGALG00010010713', 'ENSGALG00010006342', 'ENSGALG00010004979', 'ENSGALG00010023714', 'ENSGALG00010005191', 'ENSGALG00010011757'], ['ENSGALG00010010526', 'ENSGALG00010015568', 'ENSGALG00010007062', 'ENSGALG00010013088', 'ENSGALG00010024248', 'ENSGALG00010004840', 'ENSGALG00010004998'], ['ENSGALG00010007899', 'ENSGALG00010027939', 'ENSGALG00010008143', 'ENSGALG00010028193', 'ENSGALG00010010768', 'ENSGALG00010013563', 'ENSGALG00010028966'], ['ENSGALG00010009220', 'ENSGALG00010014873', 'ENSGALG00010019269', 'ENSGALG00010012871', 'ENSGALG00010006134', 'ENSGALG00010029641', 'ENSGALG00010008831'], ['ENSGALG00010005367', 'ENSGALG00010001201', 'ENSGALG00010008141', 'ENSGALG00010022506', 'ENSGALG00010012756', 'ENSGALG00010001938', 'ENSGALG00010008313'], ['ENSGALG00010009446', 'ENSGALG00010024508', 'ENSGALG00010011326', 'ENSGALG00010014149', 'ENSGALG00010009362', 'ENSGALG00010005495', 'ENSGALG00010012918'], ['ENSGALG00010001094', 'ENSGALG00010012472', 'ENSGALG00010011940', 'ENSGALG00010007919', 'ENSGALG00010007586', 'ENSGALG00010001359', 'ENSGALG00010028895'], ['ENSGALG00010014147', 'ENSGALG00010003099', 'ENSGALG00010015526', 'ENSGALG00010015041', 'ENSGALG00010001533', 'ENSGALG00010003231', 'ENSGALG00010012392'], ['ENSGALG00010002963', 'ENSGALG00010001631', 'ENSGALG00010001609', 'ENSGALG00010025146', 'ENSGALG00010025239', 'ENSGALG00010002862', 'ENSGALG00010005693'], ['ENSGALG00010019104', 'ENSGALG00010009565', 'ENSGALG00010017488', 'ENSGALG00010015376', 'ENSGALG00010021619', 'ENSGALG00010017369', 'ENSGALG00010001577'], ['ENSGALG00010011089', 'ENSGALG00010004873', 'ENSGALG00010025166', 'ENSGALG00010007769', 'ENSGALG00010010181', 'ENSGALG00010025636', 'ENSGALG00010013243'], ['ENSGALG00010029167', 'ENSGALG00010007166', 'ENSGALG00010006009', 'ENSGALG00010010267', 'ENSGALG00010010832', 'ENSGALG00010018857', 'ENSGALG00010022105'], ['ENSGALG00010002647', 'ENSGALG00010007188', 'ENSGALG00010004791', 'ENSGALG00010025891', 'ENSGALG00010012456', 'ENSGALG00010024132', 'ENSGALG00010003152'], ['ENSGALG00010013569', 'ENSGALG00010012258', 'ENSGALG00010022106', 'ENSGALG00010021708', 'ENSGALG00010006275', 'ENSGALG00010008692', 'ENSGALG00010018918'], ['ENSGALG00010019550', 'ENSGALG00010019921', 'ENSGALG00010007796', 'ENSGALG00010013167', 'ENSGALG00010013254', 'ENSGALG00010014142', 'ENSGALG00010019793'], ['ENSGALG00010024696', 'ENSGALG00010029360', 'ENSGALG00010025907', 'ENSGALG00010025349', 'ENSGALG00010029782', 'ENSGALG00010028392', 'ENSGALG00010029383'], ['ENSGALG00010019472', 'ENSGALG00010022552', 'ENSGALG00010018095', 'ENSGALG00010009104', 'ENSGALG00010024285', 'ENSGALG00010006084', 'ENSGALG00010008298'], ['ENSGALG00010021874', 'ENSGALG00010012096', 'ENSGALG00010004308', 'ENSGALG00010018079', 'ENSGALG00010005548', 'ENSGALG00010021635', 'ENSGALG00010017628'], ['ENSGALG00010023819', 'ENSGALG00010010586', 'ENSGALG00010014418', 'ENSGALG00010027209', 'ENSGALG00010028649', 'ENSGALG00010008142', 'ENSGALG00010027635'], ['ENSGALG00010001540', 'ENSGALG00010022167', 'ENSGALG00010028528', 'ENSGALG00010023052', 'ENSGALG00010005430', 'ENSGALG00010001167', 'ENSGALG00010029390'], ['ENSGALG00010028170', 'ENSGALG00010022037', 'ENSGALG00010001505', 'ENSGALG00010016751', 'ENSGALG00010007941', 'ENSGALG00010013625', 'ENSGALG00010026388'], ['ENSGALG00010011102', 'ENSGALG00010009386', 'ENSGALG00010009730', 'ENSGALG00010005218', 'ENSGALG00010016620', 'ENSGALG00010007984', 'ENSGALG00010012854'], ['ENSGALG00010029541', 'ENSGALG00010018758', 'ENSGALG00010002566', 'ENSGALG00010023671', 'ENSGALG00010016809', 'ENSGALG00010015272', 'ENSGALG00010028891'], ['ENSGALG00010017796', 'ENSGALG00010008086', 'ENSGALG00010016984', 'ENSGALG00010016850', 'ENSGALG00010023008', 'ENSGALG00010018806', 'ENSGALG00010011814'], ['ENSGALG00010025964', 'ENSGALG00010017321', 'ENSGALG00010010464', 'ENSGALG00010006882', 'ENSGALG00010015385', 'ENSGALG00010015599', 'ENSGALG00010010673'], ['ENSGALG00010011821', 'ENSGALG00010014495', 'ENSGALG00010019286', 'ENSGALG00010013571', 'ENSGALG00010006303', 'ENSGALG00010011370', 'ENSGALG00010011219'], ['ENSGALG00010026829', 'ENSGALG00010023577', 'ENSGALG00010010229', 'ENSGALG00010004259', 'ENSGALG00010014879', 'ENSGALG00010004573', 'ENSGALG00010014782'], ['ENSGALG00010022369', 'ENSGALG00010009869', 'ENSGALG00010004742', 'ENSGALG00010013059', 'ENSGALG00010002563', 'ENSGALG00010019044', 'ENSGALG00010026863'], ['ENSGALG00010020466', 'ENSGALG00010028077', 'ENSGALG00010019347', 'ENSGALG00010019169', 'ENSGALG00010007860', 'ENSGALG00010006767', 'ENSGALG00010018549'], ['ENSGALG00010001678', 'ENSGALG00010002280', 'ENSGALG00010016582', 'ENSGALG00010001154', 'ENSGALG00010024496', 'ENSGALG00010004367', 'ENSGALG00010002760'], ['ENSGALG00010017742', 'ENSGALG00010016410', 'ENSGALG00010017477', 'ENSGALG00010015935', 'ENSGALG00010026740', 'ENSGALG00010020311', 'ENSGALG00010029645'], ['ENSGALG00010011686', 'ENSGALG00010023901', 'ENSGALG00010003548', 'ENSGALG00010022543', 'ENSGALG00010003518', 'ENSGALG00010006122', 'ENSGALG00010023599'], ['ENSGALG00010001049', 'ENSGALG00010015216', 'ENSGALG00010016718', 'ENSGALG00010029482', 'ENSGALG00010006121', 'ENSGALG00010029794', 'ENSGALG00010017853'], ['ENSGALG00010026359', 'ENSGALG00010010772', 'ENSGALG00010010660', 'ENSGALG00010014998', 'ENSGALG00010019465', 'ENSGALG00010010757', 'ENSGALG00010007858'], ['ENSGALG00010019909', 'ENSGALG00010003612', 'ENSGALG00010000500', 'ENSGALG00010012211', 'ENSGALG00010026622', 'ENSGALG00010011988', 'ENSGALG00010006326'], ['ENSGALG00010020028', 'ENSGALG00010018325', 'ENSGALG00010003076', 'ENSGALG00010006202', 'ENSGALG00010005012', 'ENSGALG00010011707', 'ENSGALG00010015167'], ['ENSGALG00010004023', 'ENSGALG00010011279', 'ENSGALG00010010196', 'ENSGALG00010010264', 'ENSGALG00010016813', 'ENSGALG00010007585', 'ENSGALG00010028236'], ['ENSGALG00010001621', 'ENSGALG00010028035', 'ENSGALG00010022740', 'ENSGALG00010027418', 'ENSGALG00010027452', 'ENSGALG00010000769', 'ENSGALG00010025990'], ['ENSGALG00010020645', 'ENSGALG00010011656', 'ENSGALG00010030078', 'ENSGALG00010000895', 'ENSGALG00010016791', 'ENSGALG00010030080', 'ENSGALG00010008350'], ['ENSGALG00010019749', 'ENSGALG00010008845', 'ENSGALG00010010249', 'ENSGALG00010011933', 'ENSGALG00010015609', 'ENSGALG00010009075', 'ENSGALG00010028505'], ['ENSGALG00010017568', 'ENSGALG00010002765', 'ENSGALG00010021254', 'ENSGALG00010017411', 'ENSGALG00010017805', 'ENSGALG00010019785', 'ENSGALG00010005035'], ['ENSGALG00010001958', 'ENSGALG00010001235', 'ENSGALG00010014419', 'ENSGALG00010005346', 'ENSGALG00010001152', 'ENSGALG00010026407', 'ENSGALG00010028358'], ['ENSGALG00010016541', 'ENSGALG00010013337', 'ENSGALG00010005695', 'ENSGALG00010003103', 'ENSGALG00010020036', 'ENSGALG00010022280', 'ENSGALG00010024314'], ['ENSGALG00010025076', 'ENSGALG00010012609', 'ENSGALG00010020322', 'ENSGALG00010030018', 'ENSGALG00010025567', 'ENSGALG00010017461', 'ENSGALG00010007498'], ['ENSGALG00010026415', 'ENSGALG00010026853', 'ENSGALG00010023606', 'ENSGALG00010011237', 'ENSGALG00010026487', 'ENSGALG00010010469', 'ENSGALG00010001662'], ['ENSGALG00010014044', 'ENSGALG00010003482', 'ENSGALG00010005192', 'ENSGALG00010003556', 'ENSGALG00010009165', 'ENSGALG00010004945', 'ENSGALG00010023366'], ['ENSGALG00010028261', 'ENSGALG00010000076', 'ENSGALG00010008018', 'ENSGALG00010003249', 'ENSGALG00010025159', 'ENSGALG00010010708', 'ENSGALG00010004957'], ['ENSGALG00010018845', 'ENSGALG00010004435', 'ENSGALG00010029472', 'ENSGALG00010010739', 'ENSGALG00010017298', 'ENSGALG00010027000', 'ENSGALG00010010563'], ['ENSGALG00010019040', 'ENSGALG00010007903', 'ENSGALG00010004717', 'ENSGALG00010029668', 'ENSGALG00010020008', 'ENSGALG00010004350', 'ENSGALG00010021745'], ['ENSGALG00010006843', 'ENSGALG00010025731', 'ENSGALG00010001625', 'ENSGALG00010023113', 'ENSGALG00010009700', 'ENSGALG00010010958', 'ENSGALG00010016340'], ['ENSGALG00010017463', 'ENSGALG00010028446', 'ENSGALG00010018884', 'ENSGALG00010009877', 'ENSGALG00010008744', 'ENSGALG00010017073', 'ENSGALG00010005239'], ['ENSGALG00010027048', 'ENSGALG00010021910', 'ENSGALG00010005343', 'ENSGALG00010004565', 'ENSGALG00010017014', 'ENSGALG00010019849'], ['ENSGALG00010004623', 'ENSGALG00010007580', 'ENSGALG00010006013', 'ENSGALG00010006173', 'ENSGALG00010022521', 'ENSGALG00010018672'], ['ENSGALG00010016326', 'ENSGALG00010001479', 'ENSGALG00010022005', 'ENSGALG00010011846', 'ENSGALG00010020520', 'ENSGALG00010019699'], ['ENSGALG00010007768', 'ENSGALG00010013216', 'ENSGALG00010026996', 'ENSGALG00010002618', 'ENSGALG00010026752', 'ENSGALG00010003853'], ['ENSGALG00010005236', 'ENSGALG00010003874', 'ENSGALG00010006246', 'ENSGALG00010018668', 'ENSGALG00010004952', 'ENSGALG00010013663'], ['ENSGALG00010010706', 'ENSGALG00010016925', 'ENSGALG00010019577', 'ENSGALG00010022032', 'ENSGALG00010026163', 'ENSGALG00010018532'], ['ENSGALG00010022220', 'ENSGALG00010025932', 'ENSGALG00010022081', 'ENSGALG00010023059', 'ENSGALG00010023161', 'ENSGALG00010029933'], ['ENSGALG00010018767', 'ENSGALG00010018556', 'ENSGALG00010024944', 'ENSGALG00010010869', 'ENSGALG00010001870', 'ENSGALG00010027713'], ['ENSGALG00010019696', 'ENSGALG00010008245', 'ENSGALG00010014922', 'ENSGALG00010022788', 'ENSGALG00010022873', 'ENSGALG00010008392'], ['ENSGALG00010025318', 'ENSGALG00010025115', 'ENSGALG00010021226', 'ENSGALG00010014645', 'ENSGALG00010027885', 'ENSGALG00010018401'], ['ENSGALG00010012017', 'ENSGALG00010022557', 'ENSGALG00010021345', 'ENSGALG00010000771', 'ENSGALG00010007437', 'ENSGALG00010011916'], ['ENSGALG00010005232', 'ENSGALG00010028834', 'ENSGALG00010015114', 'ENSGALG00010015868', 'ENSGALG00010017197', 'ENSGALG00010018934'], ['ENSGALG00010028559', 'ENSGALG00010029375', 'ENSGALG00010029207', 'ENSGALG00010028348', 'ENSGALG00010029249', 'ENSGALG00010000055'], ['ENSGALG00010003132', 'ENSGALG00010008516', 'ENSGALG00010018780', 'ENSGALG00010002345', 'ENSGALG00010014077', 'ENSGALG00010007883'], ['ENSGALG00010005291', 'ENSGALG00010012194', 'ENSGALG00010010788', 'ENSGALG00010025905', 'ENSGALG00010004746', 'ENSGALG00010024671'], ['ENSGALG00010021042', 'ENSGALG00010017670', 'ENSGALG00010009079', 'ENSGALG00010015040', 'ENSGALG00010026753', 'ENSGALG00010020003'], ['ENSGALG00010012541', 'ENSGALG00010027153', 'ENSGALG00010021103', 'ENSGALG00010011497', 'ENSGALG00010013301', 'ENSGALG00010011175'], ['ENSGALG00010003953', 'ENSGALG00010010696', 'ENSGALG00010004336', 'ENSGALG00010009307', 'ENSGALG00010005241', 'ENSGALG00010005011'], ['ENSGALG00010027530', 'ENSGALG00010000585', 'ENSGALG00010002837', 'ENSGALG00010028107', 'ENSGALG00010005263', 'ENSGALG00010027310'], ['ENSGALG00010013115', 'ENSGALG00010012775', 'ENSGALG00010013097', 'ENSGALG00010005050', 'ENSGALG00010005484', 'ENSGALG00010008994'], ['ENSGALG00010017668', 'ENSGALG00010013213', 'ENSGALG00010017365', 'ENSGALG00010016676', 'ENSGALG00010012924', 'ENSGALG00010010505'], ['ENSGALG00010006847', 'ENSGALG00010016588', 'ENSGALG00010009761', 'ENSGALG00010005316', 'ENSGALG00010015829', 'ENSGALG00010011973'], ['ENSGALG00010022974', 'ENSGALG00010025685', 'ENSGALG00010018233', 'ENSGALG00010026393', 'ENSGALG00010018068', 'ENSGALG00010027081'], ['ENSGALG00010020737', 'ENSGALG00010027204', 'ENSGALG00010009657', 'ENSGALG00010006155', 'ENSGALG00010005485', 'ENSGALG00010020940'], ['ENSGALG00010016964', 'ENSGALG00010016733', 'ENSGALG00010011389', 'ENSGALG00010019335', 'ENSGALG00010011061', 'ENSGALG00010005756'], ['ENSGALG00010007766', 'ENSGALG00010003824', 'ENSGALG00010025883', 'ENSGALG00010018721', 'ENSGALG00010017156', 'ENSGALG00010017006'], ['ENSGALG00010024667', 'ENSGALG00010026051', 'ENSGALG00010024693', 'ENSGALG00010015804', 'ENSGALG00010025126', 'ENSGALG00010029787'], ['ENSGALG00010020590', 'ENSGALG00010010305', 'ENSGALG00010009130', 'ENSGALG00010013890', 'ENSGALG00010025369', 'ENSGALG00010020285'], ['ENSGALG00010013151', 'ENSGALG00010009293', 'ENSGALG00010009922', 'ENSGALG00010012494', 'ENSGALG00010006950', 'ENSGALG00010015775'], ['ENSGALG00010021791', 'ENSGALG00010018140', 'ENSGALG00010017661', 'ENSGALG00010020967', 'ENSGALG00010021170', 'ENSGALG00010021588'], ['ENSGALG00010019681', 'ENSGALG00010004911', 'ENSGALG00010027095', 'ENSGALG00010005675', 'ENSGALG00010025254', 'ENSGALG00010012827'], ['ENSGALG00010029731', 'ENSGALG00010010333', 'ENSGALG00010000485', 'ENSGALG00010029314', 'ENSGALG00010017894', 'ENSGALG00010022928'], ['ENSGALG00010014187', 'ENSGALG00010010123', 'ENSGALG00010001848', 'ENSGALG00010001077', 'ENSGALG00010006610', 'ENSGALG00010008944'], ['ENSGALG00010020557', 'ENSGALG00010010351', 'ENSGALG00010020087', 'ENSGALG00010012049', 'ENSGALG00010011484', 'ENSGALG00010011211'], ['ENSGALG00010014114', 'ENSGALG00010024645', 'ENSGALG00010021021', 'ENSGALG00010012879', 'ENSGALG00010021046', 'ENSGALG00010022408'], ['ENSGALG00010017764', 'ENSGALG00010002633', 'ENSGALG00010019645', 'ENSGALG00010000422', 'ENSGALG00010019610', 'ENSGALG00010017543'], ['ENSGALG00010017238', 'ENSGALG00010022011', 'ENSGALG00010004213', 'ENSGALG00010005378', 'ENSGALG00010009789', 'ENSGALG00010025035'], ['ENSGALG00010001491', 'ENSGALG00010025204', 'ENSGALG00010001306', 'ENSGALG00010018006', 'ENSGALG00010010982', 'ENSGALG00010014649'], ['ENSGALG00010019580', 'ENSGALG00010015653', 'ENSGALG00010017285', 'ENSGALG00010003815', 'ENSGALG00010022652', 'ENSGALG00010011461'], ['ENSGALG00010019853', 'ENSGALG00010006870', 'ENSGALG00010019097', 'ENSGALG00010010241', 'ENSGALG00010007103', 'ENSGALG00010018610'], ['ENSGALG00010007143', 'ENSGALG00010016992', 'ENSGALG00010018790', 'ENSGALG00010016595', 'ENSGALG00010000230', 'ENSGALG00010002279'], ['ENSGALG00010018568', 'ENSGALG00010010059', 'ENSGALG00010001179', 'ENSGALG00010024656', 'ENSGALG00010000303', 'ENSGALG00010021329'], ['ENSGALG00010015127', 'ENSGALG00010023199', 'ENSGALG00010005158', 'ENSGALG00010006178', 'ENSGALG00010007539', 'ENSGALG00010006061'], ['ENSGALG00010010940', 'ENSGALG00010014462', 'ENSGALG00010004376', 'ENSGALG00010019276', 'ENSGALG00010011646', 'ENSGALG00010003549'], ['ENSGALG00010003797', 'ENSGALG00010008121', 'ENSGALG00010011915', 'ENSGALG00010004072', 'ENSGALG00010024280', 'ENSGALG00010020509'], ['ENSGALG00010002602', 'ENSGALG00010008665', 'ENSGALG00010004551', 'ENSGALG00010025352', 'ENSGALG00010013211', 'ENSGALG00010019678'], ['ENSGALG00010017970', 'ENSGALG00010025320', 'ENSGALG00010003921', 'ENSGALG00010007302', 'ENSGALG00010007360', 'ENSGALG00010010383'], ['ENSGALG00010009720', 'ENSGALG00010025216', 'ENSGALG00010024544', 'ENSGALG00010016415', 'ENSGALG00010010356', 'ENSGALG00010027241'], ['ENSGALG00010018402', 'ENSGALG00010021773', 'ENSGALG00010017501', 'ENSGALG00010011328', 'ENSGALG00010008626', 'ENSGALG00010007782'], ['ENSGALG00010007570', 'ENSGALG00010021899', 'ENSGALG00010004232', 'ENSGALG00010001648', 'ENSGALG00010004132', 'ENSGALG00010005200'], ['ENSGALG00010000029', 'ENSGALG00010000017', 'ENSGALG00010000020', 'ENSGALG00010000033', 'ENSGALG00010000034', 'ENSGALG00010000024'], ['ENSGALG00010016194', 'ENSGALG00010020380', 'ENSGALG00010017527', 'ENSGALG00010004637', 'ENSGALG00010006960', 'ENSGALG00010009405'], ['ENSGALG00010026320', 'ENSGALG00010013831', 'ENSGALG00010012362', 'ENSGALG00010014153', 'ENSGALG00010012769', 'ENSGALG00010028885'], ['ENSGALG00010006760', 'ENSGALG00010000081', 'ENSGALG00010015213', 'ENSGALG00010016808', 'ENSGALG00010029247', 'ENSGALG00010021251'], ['ENSGALG00010003810', 'ENSGALG00010006223', 'ENSGALG00010023762', 'ENSGALG00010008052', 'ENSGALG00010029750', 'ENSGALG00010003298'], ['ENSGALG00010016969', 'ENSGALG00010013282', 'ENSGALG00010005171', 'ENSGALG00010014362', 'ENSGALG00010018371', 'ENSGALG00010013085'], ['ENSGALG00010011191', 'ENSGALG00010016371', 'ENSGALG00010004349', 'ENSGALG00010022510', 'ENSGALG00010016608', 'ENSGALG00010009110'], ['ENSGALG00010019346', 'ENSGALG00010018057', 'ENSGALG00010014548', 'ENSGALG00010012776', 'ENSGALG00010015527', 'ENSGALG00010009248'], ['ENSGALG00010020957', 'ENSGALG00010021243', 'ENSGALG00010019263', 'ENSGALG00010018987', 'ENSGALG00010000787', 'ENSGALG00010002487'], ['ENSGALG00010018405', 'ENSGALG00010016671', 'ENSGALG00010005619', 'ENSGALG00010024737', 'ENSGALG00010008168', 'ENSGALG00010011077'], ['ENSGALG00010000590', 'ENSGALG00010014771', 'ENSGALG00010008957', 'ENSGALG00010012794', 'ENSGALG00010019365', 'ENSGALG00010011914'], ['ENSGALG00010022690', 'ENSGALG00010019117', 'ENSGALG00010019816', 'ENSGALG00010019270', 'ENSGALG00010015192', 'ENSGALG00010018822'], ['ENSGALG00010008336', 'ENSGALG00010029744', 'ENSGALG00010026726', 'ENSGALG00010018771', 'ENSGALG00010005154', 'ENSGALG00010025621'], ['ENSGALG00010022621', 'ENSGALG00010008531', 'ENSGALG00010022447', 'ENSGALG00010015559', 'ENSGALG00010025366', 'ENSGALG00010014202'], ['ENSGALG00010010037', 'ENSGALG00010016114', 'ENSGALG00010007375', 'ENSGALG00010009593', 'ENSGALG00010011979', 'ENSGALG00010014041'], ['ENSGALG00010008869', 'ENSGALG00010008922', 'ENSGALG00010017413', 'ENSGALG00010005876', 'ENSGALG00010002258', 'ENSGALG00010004064'], ['ENSGALG00010013351', 'ENSGALG00010007388', 'ENSGALG00010027036', 'ENSGALG00010005399', 'ENSGALG00010025740', 'ENSGALG00010024816'], ['ENSGALG00010021628', 'ENSGALG00010003524', 'ENSGALG00010021828', 'ENSGALG00010022392', 'ENSGALG00010014826', 'ENSGALG00010016166'], ['ENSGALG00010008872', 'ENSGALG00010009690', 'ENSGALG00010028489', 'ENSGALG00010009024', 'ENSGALG00010009289', 'ENSGALG00010015820'], ['ENSGALG00010019405', 'ENSGALG00010026640', 'ENSGALG00010014723', 'ENSGALG00010017863', 'ENSGALG00010024165', 'ENSGALG00010021150'], ['ENSGALG00010025862', 'ENSGALG00010027534', 'ENSGALG00010025389', 'ENSGALG00010009029', 'ENSGALG00010025368', 'ENSGALG00010028472'], ['ENSGALG00010017513', 'ENSGALG00010019250', 'ENSGALG00010013619', 'ENSGALG00010025342', 'ENSGALG00010014020', 'ENSGALG00010020696'], ['ENSGALG00010013349', 'ENSGALG00010012060', 'ENSGALG00010024644', 'ENSGALG00010029440', 'ENSGALG00010002712', 'ENSGALG00010025831'], ['ENSGALG00010014374', 'ENSGALG00010006786', 'ENSGALG00010003469', 'ENSGALG00010009630', 'ENSGALG00010002117', 'ENSGALG00010004816'], ['ENSGALG00010027645', 'ENSGALG00010027164', 'ENSGALG00010015893', 'ENSGALG00010024226', 'ENSGALG00010023666', 'ENSGALG00010028246'], ['ENSGALG00010006556', 'ENSGALG00010000786', 'ENSGALG00010003475', 'ENSGALG00010003683', 'ENSGALG00010002320', 'ENSGALG00010024066'], ['ENSGALG00010003133', 'ENSGALG00010011937', 'ENSGALG00010017849', 'ENSGALG00010029878', 'ENSGALG00010010734', 'ENSGALG00010018243'], ['ENSGALG00010007918', 'ENSGALG00010016363', 'ENSGALG00010010233', 'ENSGALG00010009023', 'ENSGALG00010001366', 'ENSGALG00010010235'], ['ENSGALG00010006973', 'ENSGALG00010014195', 'ENSGALG00010019880', 'ENSGALG00010008833', 'ENSGALG00010007008', 'ENSGALG00010015480'], ['ENSGALG00010015333', 'ENSGALG00010001513', 'ENSGALG00010004211', 'ENSGALG00010024513', 'ENSGALG00010026671', 'ENSGALG00010002916'], ['ENSGALG00010010905', 'ENSGALG00010009601', 'ENSGALG00010015866', 'ENSGALG00010015643', 'ENSGALG00010002247', 'ENSGALG00010010651'], ['ENSGALG00010011290', 'ENSGALG00010001656', 'ENSGALG00010019229', 'ENSGALG00010024390', 'ENSGALG00010025838', 'ENSGALG00010010294'], ['ENSGALG00010011549', 'ENSGALG00010014914', 'ENSGALG00010014039', 'ENSGALG00010019587', 'ENSGALG00010024123', 'ENSGALG00010001837'], ['ENSGALG00010019707', 'ENSGALG00010025255', 'ENSGALG00010028699', 'ENSGALG00010017481', 'ENSGALG00010002392', 'ENSGALG00010000626'], ['ENSGALG00010019133', 'ENSGALG00010021921', 'ENSGALG00010021299', 'ENSGALG00010004694', 'ENSGALG00010019251', 'ENSGALG00010019729'], ['ENSGALG00010002242', 'ENSGALG00010000987', 'ENSGALG00010012652', 'ENSGALG00010019665', 'ENSGALG00010014558', 'ENSGALG00010015078'], ['ENSGALG00010020327', 'ENSGALG00010021487', 'ENSGALG00010012013', 'ENSGALG00010025560', 'ENSGALG00010003718', 'ENSGALG00010027559'], ['ENSGALG00010025664', 'ENSGALG00010017378', 'ENSGALG00010028553', 'ENSGALG00010016963', 'ENSGALG00010005911', 'ENSGALG00010012145'], ['ENSGALG00010004228', 'ENSGALG00010008911', 'ENSGALG00010007124', 'ENSGALG00010004164', 'ENSGALG00010008953', 'ENSGALG00010015307'], ['ENSGALG00010005651', 'ENSGALG00010019239', 'ENSGALG00010027925', 'ENSGALG00010008745', 'ENSGALG00010011028', 'ENSGALG00010023063'], ['ENSGALG00010029341', 'ENSGALG00010001912', 'ENSGALG00010024206', 'ENSGALG00010027074', 'ENSGALG00010009474', 'ENSGALG00010018619'], ['ENSGALG00010025504', 'ENSGALG00010026052', 'ENSGALG00010000181', 'ENSGALG00010006117', 'ENSGALG00010005455', 'ENSGALG00010000601'], ['ENSGALG00010012461', 'ENSGALG00010016389', 'ENSGALG00010027647', 'ENSGALG00010018362', 'ENSGALG00010023475', 'ENSGALG00010022914'], ['ENSGALG00010000789', 'ENSGALG00010023399', 'ENSGALG00010018763', 'ENSGALG00010011285', 'ENSGALG00010028307', 'ENSGALG00010028890'], ['ENSGALG00010019275', 'ENSGALG00010026840', 'ENSGALG00010006295', 'ENSGALG00010005094', 'ENSGALG00010009589', 'ENSGALG00010018392'], ['ENSGALG00010027618', 'ENSGALG00010017248', 'ENSGALG00010019041', 'ENSGALG00010023053', 'ENSGALG00010014954', 'ENSGALG00010016796'], ['ENSGALG00010014355', 'ENSGALG00010004421', 'ENSGALG00010016807', 'ENSGALG00010023963', 'ENSGALG00010011205', 'ENSGALG00010006515'], ['ENSGALG00010000431', 'ENSGALG00010012583', 'ENSGALG00010006183', 'ENSGALG00010007798', 'ENSGALG00010010954', 'ENSGALG00010011076'], ['ENSGALG00010024164', 'ENSGALG00010005830', 'ENSGALG00010028669', 'ENSGALG00010016027', 'ENSGALG00010022152', 'ENSGALG00010003261'], ['ENSGALG00010024540', 'ENSGALG00010017490', 'ENSGALG00010028346', 'ENSGALG00010023242', 'ENSGALG00010023498', 'ENSGALG00010021529'], ['ENSGALG00010006356', 'ENSGALG00010002328', 'ENSGALG00010023747', 'ENSGALG00010018940', 'ENSGALG00010008071', 'ENSGALG00010013920'], ['ENSGALG00010013752', 'ENSGALG00010012700', 'ENSGALG00010028423', 'ENSGALG00010007981', 'ENSGALG00010005842', 'ENSGALG00010022658'], ['ENSGALG00010015613', 'ENSGALG00010010771', 'ENSGALG00010014997', 'ENSGALG00010015879', 'ENSGALG00010010809', 'ENSGALG00010015049'], ['ENSGALG00010009046', 'ENSGALG00010025978', 'ENSGALG00010010540', 'ENSGALG00010006733', 'ENSGALG00010008611', 'ENSGALG00010006990'], ['ENSGALG00010006089', 'ENSGALG00010013589', 'ENSGALG00010026631', 'ENSGALG00010014042', 'ENSGALG00010014196', 'ENSGALG00010008416'], ['ENSGALG00010027654', 'ENSGALG00010015939', 'ENSGALG00010025600', 'ENSGALG00010014576', 'ENSGALG00010017323', 'ENSGALG00010014026'], ['ENSGALG00010015082', 'ENSGALG00010019626', 'ENSGALG00010001484', 'ENSGALG00010024367', 'ENSGALG00010008826', 'ENSGALG00010003569'], ['ENSGALG00010012917', 'ENSGALG00010004777', 'ENSGALG00010023974', 'ENSGALG00010004533', 'ENSGALG00010015037', 'ENSGALG00010029728'], ['ENSGALG00010026615', 'ENSGALG00010024355', 'ENSGALG00010028675', 'ENSGALG00010017822', 'ENSGALG00010026242', 'ENSGALG00010021055'], ['ENSGALG00010008041', 'ENSGALG00010015639', 'ENSGALG00010015058', 'ENSGALG00010029885', 'ENSGALG00010016641', 'ENSGALG00010016713'], ['ENSGALG00010013950', 'ENSGALG00010023025', 'ENSGALG00010019862', 'ENSGALG00010018778', 'ENSGALG00010007736', 'ENSGALG00010004169'], ['ENSGALG00010017304', 'ENSGALG00010006068', 'ENSGALG00010023594', 'ENSGALG00010024026', 'ENSGALG00010028262', 'ENSGALG00010027146'], ['ENSGALG00010021573', 'ENSGALG00010011064', 'ENSGALG00010007781', 'ENSGALG00010000078', 'ENSGALG00010028603', 'ENSGALG00010016470'], ['ENSGALG00010025886', 'ENSGALG00010024769', 'ENSGALG00010026016', 'ENSGALG00010024820', 'ENSGALG00010029669', 'ENSGALG00010024738'], ['ENSGALG00010005639', 'ENSGALG00010015672', 'ENSGALG00010008778', 'ENSGALG00010018954', 'ENSGALG00010029678', 'ENSGALG00010003723'], ['ENSGALG00010009841', 'ENSGALG00010023920', 'ENSGALG00010010342', 'ENSGALG00010008818', 'ENSGALG00010024067', 'ENSGALG00010025122'], ['ENSGALG00010002860', 'ENSGALG00010012812', 'ENSGALG00010024499', 'ENSGALG00010008541', 'ENSGALG00010005092', 'ENSGALG00010008971'], ['ENSGALG00010015138', 'ENSGALG00010012175', 'ENSGALG00010020922', 'ENSGALG00010014394', 'ENSGALG00010021242', 'ENSGALG00010010844'], ['ENSGALG00010024801', 'ENSGALG00010002807', 'ENSGALG00010015131', 'ENSGALG00010021391', 'ENSGALG00010015199', 'ENSGALG00010027221'], ['ENSGALG00010025157', 'ENSGALG00010020374', 'ENSGALG00010023169', 'ENSGALG00010029227', 'ENSGALG00010029439', 'ENSGALG00010024363'], ['ENSGALG00010008292', 'ENSGALG00010020176', 'ENSGALG00010023710', 'ENSGALG00010008213', 'ENSGALG00010019878', 'ENSGALG00010016049'], ['ENSGALG00010023396', 'ENSGALG00010022829', 'ENSGALG00010026711', 'ENSGALG00010008721', 'ENSGALG00010029103', 'ENSGALG00010002024'], ['ENSGALG00010007653', 'ENSGALG00010008206', 'ENSGALG00010020795', 'ENSGALG00010015873', 'ENSGALG00010006586', 'ENSGALG00010019775'], ['ENSGALG00010008587', 'ENSGALG00010014008', 'ENSGALG00010022542', 'ENSGALG00010007424', 'ENSGALG00010014071', 'ENSGALG00010009723'], ['ENSGALG00010027127', 'ENSGALG00010007994', 'ENSGALG00010029632', 'ENSGALG00010024583', 'ENSGALG00010028467', 'ENSGALG00010005585'], ['ENSGALG00010029712', 'ENSGALG00010017464', 'ENSGALG00010004061', 'ENSGALG00010029765', 'ENSGALG00010025125', 'ENSGALG00010021045'], ['ENSGALG00010025843', 'ENSGALG00010023085', 'ENSGALG00010013190', 'ENSGALG00010005520', 'ENSGALG00010002204', 'ENSGALG00010000911'], ['ENSGALG00010008036', 'ENSGALG00010002485', 'ENSGALG00010017254', 'ENSGALG00010007390', 'ENSGALG00010010801', 'ENSGALG00010017302'], ['ENSGALG00010028427', 'ENSGALG00010000696', 'ENSGALG00010023758', 'ENSGALG00010022550', 'ENSGALG00010021935', 'ENSGALG00010016920'], ['ENSGALG00010000344', 'ENSGALG00010013260', 'ENSGALG00010011314', 'ENSGALG00010017875', 'ENSGALG00010025382', 'ENSGALG00010028136'], ['ENSGALG00010003355', 'ENSGALG00010018272', 'ENSGALG00010025356', 'ENSGALG00010018321', 'ENSGALG00010029460', 'ENSGALG00010026343'], ['ENSGALG00010027272', 'ENSGALG00010028015', 'ENSGALG00010003503', 'ENSGALG00010019226', 'ENSGALG00010003604', 'ENSGALG00010003320'], ['ENSGALG00010024106', 'ENSGALG00010027607', 'ENSGALG00010021782', 'ENSGALG00010026173', 'ENSGALG00010003136', 'ENSGALG00010021766'], ['ENSGALG00010010239', 'ENSGALG00010011766', 'ENSGALG00010006419', 'ENSGALG00010020290', 'ENSGALG00010024739', 'ENSGALG00010007216'], ['ENSGALG00010011985', 'ENSGALG00010005233', 'ENSGALG00010027633', 'ENSGALG00010015784', 'ENSGALG00010025855', 'ENSGALG00010010794'], ['ENSGALG00010003629', 'ENSGALG00010013489', 'ENSGALG00010005601', 'ENSGALG00010019304', 'ENSGALG00010016014', 'ENSGALG00010014932'], ['ENSGALG00010021312', 'ENSGALG00010017318', 'ENSGALG00010021821', 'ENSGALG00010021902', 'ENSGALG00010013079', 'ENSGALG00010011253'], ['ENSGALG00010029506', 'ENSGALG00010028752', 'ENSGALG00010027295', 'ENSGALG00010026240', 'ENSGALG00010023213', 'ENSGALG00010028129'], ['ENSGALG00010008097', 'ENSGALG00010003545', 'ENSGALG00010026607', 'ENSGALG00010014449', 'ENSGALG00010029100', 'ENSGALG00010026254'], ['ENSGALG00010027923', 'ENSGALG00010023809', 'ENSGALG00010001780', 'ENSGALG00010024772', 'ENSGALG00010028421', 'ENSGALG00010006285'], ['ENSGALG00010008214', 'ENSGALG00010000784', 'ENSGALG00010014658', 'ENSGALG00010001947', 'ENSGALG00010019038', 'ENSGALG00010017493'], ['ENSGALG00010012712', 'ENSGALG00010012631', 'ENSGALG00010015356', 'ENSGALG00010014220', 'ENSGALG00010015617', 'ENSGALG00010012975'], ['ENSGALG00010020958', 'ENSGALG00010018339', 'ENSGALG00010028298', 'ENSGALG00010006188', 'ENSGALG00010013596', 'ENSGALG00010008347'], ['ENSGALG00010002937', 'ENSGALG00010018255', 'ENSGALG00010009326', 'ENSGALG00010005396', 'ENSGALG00010020843', 'ENSGALG00010018752'], ['ENSGALG00010029372', 'ENSGALG00010024258', 'ENSGALG00010026672', 'ENSGALG00010024603', 'ENSGALG00010029331', 'ENSGALG00010028491'], ['ENSGALG00010016599', 'ENSGALG00010019738', 'ENSGALG00010020352', 'ENSGALG00010013930', 'ENSGALG00010022614', 'ENSGALG00010026090'], ['ENSGALG00010013980', 'ENSGALG00010015205', 'ENSGALG00010020315', 'ENSGALG00010016119', 'ENSGALG00010006035', 'ENSGALG00010021522'], ['ENSGALG00010018460', 'ENSGALG00010029945', 'ENSGALG00010018665', 'ENSGALG00010021094', 'ENSGALG00010022313'], ['ENSGALG00010027086', 'ENSGALG00010029956', 'ENSGALG00010028678', 'ENSGALG00010004198', 'ENSGALG00010025776'], ['ENSGALG00010010996', 'ENSGALG00010011944', 'ENSGALG00010005145', 'ENSGALG00010005531', 'ENSGALG00010012587'], ['ENSGALG00010007371', 'ENSGALG00010006629', 'ENSGALG00010005475', 'ENSGALG00010016215', 'ENSGALG00010018443'], ['ENSGALG00010007776', 'ENSGALG00010010704', 'ENSGALG00010001507', 'ENSGALG00010001443', 'ENSGALG00010009494'], ['ENSGALG00010008897', 'ENSGALG00010008057', 'ENSGALG00010007926', 'ENSGALG00010002582', 'ENSGALG00010024324'], ['ENSGALG00010006153', 'ENSGALG00010028715', 'ENSGALG00010005923', 'ENSGALG00010027656', 'ENSGALG00010022331'], ['ENSGALG00010023883', 'ENSGALG00010003777', 'ENSGALG00010022689', 'ENSGALG00010027582', 'ENSGALG00010023287'], ['ENSGALG00010020343', 'ENSGALG00010019621', 'ENSGALG00010013266', 'ENSGALG00010009225', 'ENSGALG00010011423'], ['ENSGALG00010006086', 'ENSGALG00010015603', 'ENSGALG00010024293', 'ENSGALG00010027887', 'ENSGALG00010027891'], ['ENSGALG00010006516', 'ENSGALG00010012755', 'ENSGALG00010006083', 'ENSGALG00010012878', 'ENSGALG00010005470'], ['ENSGALG00010018908', 'ENSGALG00010014951', 'ENSGALG00010021524', 'ENSGALG00010016009', 'ENSGALG00010013766'], ['ENSGALG00010013718', 'ENSGALG00010023899', 'ENSGALG00010009845', 'ENSGALG00010023323', 'ENSGALG00010003093'], ['ENSGALG00010015892', 'ENSGALG00010018482', 'ENSGALG00010026195', 'ENSGALG00010003352', 'ENSGALG00010000529'], ['ENSGALG00010003826', 'ENSGALG00010008026', 'ENSGALG00010028319', 'ENSGALG00010016840', 'ENSGALG00010002883'], ['ENSGALG00010003300', 'ENSGALG00010020429', 'ENSGALG00010025836', 'ENSGALG00010013464', 'ENSGALG00010004824'], ['ENSGALG00010013304', 'ENSGALG00010023852', 'ENSGALG00010029176', 'ENSGALG00010001839', 'ENSGALG00010006904'], ['ENSGALG00010028081', 'ENSGALG00010023837', 'ENSGALG00010015085', 'ENSGALG00010029663', 'ENSGALG00010016362'], ['ENSGALG00010002134', 'ENSGALG00010001843', 'ENSGALG00010024157', 'ENSGALG00010026770', 'ENSGALG00010027809'], ['ENSGALG00010017774', 'ENSGALG00010014197', 'ENSGALG00010001305', 'ENSGALG00010010577', 'ENSGALG00010001112'], ['ENSGALG00010001198', 'ENSGALG00010003914', 'ENSGALG00010019183', 'ENSGALG00010028394', 'ENSGALG00010015852'], ['ENSGALG00010021067', 'ENSGALG00010017165', 'ENSGALG00010002900', 'ENSGALG00010023878', 'ENSGALG00010026848'], ['ENSGALG00010015707', 'ENSGALG00010013090', 'ENSGALG00010008054', 'ENSGALG00010009374', 'ENSGALG00010013383'], ['ENSGALG00010019422', 'ENSGALG00010019411', 'ENSGALG00010018496', 'ENSGALG00010019693', 'ENSGALG00010020141'], ['ENSGALG00010024069', 'ENSGALG00010018990', 'ENSGALG00010013509', 'ENSGALG00010011536', 'ENSGALG00010029309'], ['ENSGALG00010018445', 'ENSGALG00010015781', 'ENSGALG00010007587', 'ENSGALG00010008854', 'ENSGALG00010028376'], ['ENSGALG00010003034', 'ENSGALG00010003692', 'ENSGALG00010003517', 'ENSGALG00010010986', 'ENSGALG00010006039'], ['ENSGALG00010002419', 'ENSGALG00010012071', 'ENSGALG00010017886', 'ENSGALG00010004430', 'ENSGALG00010001834'], ['ENSGALG00010014011', 'ENSGALG00010025570', 'ENSGALG00010006920', 'ENSGALG00010008048', 'ENSGALG00010025792'], ['ENSGALG00010008385', 'ENSGALG00010016774', 'ENSGALG00010009522', 'ENSGALG00010009540', 'ENSGALG00010008527'], ['ENSGALG00010008732', 'ENSGALG00010007704', 'ENSGALG00010018545', 'ENSGALG00010026442', 'ENSGALG00010005308'], ['ENSGALG00010023835', 'ENSGALG00010006038', 'ENSGALG00010029364', 'ENSGALG00010009059', 'ENSGALG00010021735'], ['ENSGALG00010023757', 'ENSGALG00010009810', 'ENSGALG00010026114', 'ENSGALG00010012833', 'ENSGALG00010017065'], ['ENSGALG00010014337', 'ENSGALG00010014420', 'ENSGALG00010023092', 'ENSGALG00010029174', 'ENSGALG00010009058'], ['ENSGALG00010019784', 'ENSGALG00010004035', 'ENSGALG00010019107', 'ENSGALG00010018659', 'ENSGALG00010002286'], ['ENSGALG00010020548', 'ENSGALG00010003583', 'ENSGALG00010008221', 'ENSGALG00010003331', 'ENSGALG00010012633'], ['ENSGALG00010002588', 'ENSGALG00010015374', 'ENSGALG00010003374', 'ENSGALG00010002540', 'ENSGALG00010001161'], ['ENSGALG00010004340', 'ENSGALG00010010761', 'ENSGALG00010005578', 'ENSGALG00010008999', 'ENSGALG00010005981'], ['ENSGALG00010004532', 'ENSGALG00010006266', 'ENSGALG00010008101', 'ENSGALG00010008340', 'ENSGALG00010002653'], ['ENSGALG00010005253', 'ENSGALG00010024826', 'ENSGALG00010005170', 'ENSGALG00010018037', 'ENSGALG00010010645'], ['ENSGALG00010029706', 'ENSGALG00010029297', 'ENSGALG00010028103', 'ENSGALG00010025449', 'ENSGALG00010014002'], ['ENSGALG00010001519', 'ENSGALG00010012012', 'ENSGALG00010009687', 'ENSGALG00010002221', 'ENSGALG00010010639'], ['ENSGALG00010020066', 'ENSGALG00010022860', 'ENSGALG00010019700', 'ENSGALG00010009146', 'ENSGALG00010024870'], ['ENSGALG00010018400', 'ENSGALG00010014189', 'ENSGALG00010022754', 'ENSGALG00010011893', 'ENSGALG00010017858'], ['ENSGALG00010015937', 'ENSGALG00010006328', 'ENSGALG00010015929', 'ENSGALG00010028033', 'ENSGALG00010011876'], ['ENSGALG00010006729', 'ENSGALG00010007722', 'ENSGALG00010007652', 'ENSGALG00010014422', 'ENSGALG00010010583'], ['ENSGALG00010021415', 'ENSGALG00010020626', 'ENSGALG00010024650', 'ENSGALG00010020383', 'ENSGALG00010029674'], ['ENSGALG00010029352', 'ENSGALG00010020101', 'ENSGALG00010020248', 'ENSGALG00010023065', 'ENSGALG00010005389'], ['ENSGALG00010023789', 'ENSGALG00010026750', 'ENSGALG00010024175', 'ENSGALG00010011895', 'ENSGALG00010006814'], ['ENSGALG00010005784', 'ENSGALG00010001895', 'ENSGALG00010025413', 'ENSGALG00010012685', 'ENSGALG00010000200'], ['ENSGALG00010006147', 'ENSGALG00010027240', 'ENSGALG00010005848', 'ENSGALG00010022551', 'ENSGALG00010011886'], ['ENSGALG00010026620', 'ENSGALG00010025704', 'ENSGALG00010003543', 'ENSGALG00010022048', 'ENSGALG00010028447'], ['ENSGALG00010013316', 'ENSGALG00010022809', 'ENSGALG00010009200', 'ENSGALG00010014626', 'ENSGALG00010016231'], ['ENSGALG00010028211', 'ENSGALG00010028165', 'ENSGALG00010028176', 'ENSGALG00010028132', 'ENSGALG00010027867'], ['ENSGALG00010007790', 'ENSGALG00010025973', 'ENSGALG00010012789', 'ENSGALG00010004448', 'ENSGALG00010007119'], ['ENSGALG00010017453', 'ENSGALG00010011531', 'ENSGALG00010005890', 'ENSGALG00010007893', 'ENSGALG00010021513'], ['ENSGALG00010009320', 'ENSGALG00010002367', 'ENSGALG00010002880', 'ENSGALG00010014345', 'ENSGALG00010008451'], ['ENSGALG00010022501', 'ENSGALG00010022570', 'ENSGALG00010018637', 'ENSGALG00010024348', 'ENSGALG00010014591'], ['ENSGALG00010024846', 'ENSGALG00010005303', 'ENSGALG00010021958', 'ENSGALG00010014883', 'ENSGALG00010024441'], ['ENSGALG00010008837', 'ENSGALG00010020369', 'ENSGALG00010001616', 'ENSGALG00010004715', 'ENSGALG00010012771'], ['ENSGALG00010016353', 'ENSGALG00010019246', 'ENSGALG00010023099', 'ENSGALG00010027743', 'ENSGALG00010022968'], ['ENSGALG00010006587', 'ENSGALG00010014681', 'ENSGALG00010019774', 'ENSGALG00010009999', 'ENSGALG00010020042'], ['ENSGALG00010024996', 'ENSGALG00010013290', 'ENSGALG00010016490', 'ENSGALG00010021889', 'ENSGALG00010009425'], ['ENSGALG00010011539', 'ENSGALG00010012366', 'ENSGALG00010029147', 'ENSGALG00010021903', 'ENSGALG00010025341'], ['ENSGALG00010010779', 'ENSGALG00010006445', 'ENSGALG00010011104', 'ENSGALG00010020109', 'ENSGALG00010010988'], ['ENSGALG00010024342', 'ENSGALG00010027363', 'ENSGALG00010002866', 'ENSGALG00010024473', 'ENSGALG00010020153'], ['ENSGALG00010017162', 'ENSGALG00010019684', 'ENSGALG00010024003', 'ENSGALG00010014193', 'ENSGALG00010029255'], ['ENSGALG00010010857', 'ENSGALG00010009118', 'ENSGALG00010010465', 'ENSGALG00010008099', 'ENSGALG00010009762'], ['ENSGALG00010016176', 'ENSGALG00010024229', 'ENSGALG00010017412', 'ENSGALG00010029078', 'ENSGALG00010007170'], ['ENSGALG00010019547', 'ENSGALG00010006988', 'ENSGALG00010022544', 'ENSGALG00010000806', 'ENSGALG00010008864'], ['ENSGALG00010021388', 'ENSGALG00010003968', 'ENSGALG00010018508', 'ENSGALG00010014482', 'ENSGALG00010003251'], ['ENSGALG00010027989', 'ENSGALG00010022505', 'ENSGALG00010029528', 'ENSGALG00010029498', 'ENSGALG00010029330'], ['ENSGALG00010014888', 'ENSGALG00010003534', 'ENSGALG00010013807', 'ENSGALG00010021392', 'ENSGALG00010012585'], ['ENSGALG00010025496', 'ENSGALG00010011866', 'ENSGALG00010024625', 'ENSGALG00010025572', 'ENSGALG00010029526'], ['ENSGALG00010013999', 'ENSGALG00010016217', 'ENSGALG00010014569', 'ENSGALG00010010795', 'ENSGALG00010014660'], ['ENSGALG00010029153', 'ENSGALG00010024086', 'ENSGALG00010024080', 'ENSGALG00010029686', 'ENSGALG00010025897'], ['ENSGALG00010019697', 'ENSGALG00010016677', 'ENSGALG00010013379', 'ENSGALG00010013592', 'ENSGALG00010021277'], ['ENSGALG00010006094', 'ENSGALG00010028356', 'ENSGALG00010007239', 'ENSGALG00010012589', 'ENSGALG00010001095'], ['ENSGALG00010023587', 'ENSGALG00010026778', 'ENSGALG00010011265', 'ENSGALG00010025681', 'ENSGALG00010015393'], ['ENSGALG00010015832', 'ENSGALG00010027888', 'ENSGALG00010021139', 'ENSGALG00010030073', 'ENSGALG00010022396'], ['ENSGALG00010011029', 'ENSGALG00010001803', 'ENSGALG00010007521', 'ENSGALG00010010963', 'ENSGALG00010008775'], ['ENSGALG00010024126', 'ENSGALG00010024078', 'ENSGALG00010020613', 'ENSGALG00010017346', 'ENSGALG00010018823'], ['ENSGALG00010026002', 'ENSGALG00010017503', 'ENSGALG00010000262', 'ENSGALG00010001143', 'ENSGALG00010027380'], ['ENSGALG00010008330', 'ENSGALG00010010077', 'ENSGALG00010004149', 'ENSGALG00010012441', 'ENSGALG00010014298'], ['ENSGALG00010023505', 'ENSGALG00010023117', 'ENSGALG00010022824', 'ENSGALG00010023171', 'ENSGALG00010023526'], ['ENSGALG00010021144', 'ENSGALG00010020886', 'ENSGALG00010019706', 'ENSGALG00010019625', 'ENSGALG00010021145'], ['ENSGALG00010005120', 'ENSGALG00010017532', 'ENSGALG00010023659', 'ENSGALG00010027514', 'ENSGALG00010023554'], ['ENSGALG00010013865', 'ENSGALG00010010829', 'ENSGALG00010004570', 'ENSGALG00010005196', 'ENSGALG00010023010'], ['ENSGALG00010009109', 'ENSGALG00010010215', 'ENSGALG00010004451', 'ENSGALG00010016581', 'ENSGALG00010012015'], ['ENSGALG00010012549', 'ENSGALG00010007012', 'ENSGALG00010009815', 'ENSGALG00010014110', 'ENSGALG00010015818'], ['ENSGALG00010027625', 'ENSGALG00010016645', 'ENSGALG00010011442', 'ENSGALG00010025284', 'ENSGALG00010026585'], ['ENSGALG00010007751', 'ENSGALG00010014334', 'ENSGALG00010011789', 'ENSGALG00010024663', 'ENSGALG00010023652'], ['ENSGALG00010021446', 'ENSGALG00010012676', 'ENSGALG00010005374', 'ENSGALG00010025301', 'ENSGALG00010016229'], ['ENSGALG00010020652', 'ENSGALG00010002455', 'ENSGALG00010008166', 'ENSGALG00010018433', 'ENSGALG00010011090'], ['ENSGALG00010004844', 'ENSGALG00010005763', 'ENSGALG00010007058', 'ENSGALG00010007190', 'ENSGALG00010005216'], ['ENSGALG00010015585', 'ENSGALG00010026211', 'ENSGALG00010007739', 'ENSGALG00010017460', 'ENSGALG00010016369'], ['ENSGALG00010022707', 'ENSGALG00010015018', 'ENSGALG00010015960', 'ENSGALG00010005203', 'ENSGALG00010015123'], ['ENSGALG00010000196', 'ENSGALG00010005361', 'ENSGALG00010000310', 'ENSGALG00010000316', 'ENSGALG00010016828'], ['ENSGALG00010002406', 'ENSGALG00010018865', 'ENSGALG00010016956', 'ENSGALG00010029319', 'ENSGALG00010029296'], ['ENSGALG00010008029', 'ENSGALG00010028055', 'ENSGALG00010003240', 'ENSGALG00010012998', 'ENSGALG00010008187'], ['ENSGALG00010019026', 'ENSGALG00010027864', 'ENSGALG00010019416', 'ENSGALG00010008334', 'ENSGALG00010011952'], ['ENSGALG00010020780', 'ENSGALG00010015106', 'ENSGALG00010005888', 'ENSGALG00010013764', 'ENSGALG00010023351'], ['ENSGALG00010021551', 'ENSGALG00010023108', 'ENSGALG00010020072', 'ENSGALG00010023327', 'ENSGALG00010024034'], ['ENSGALG00010002461', 'ENSGALG00010004106', 'ENSGALG00010023502', 'ENSGALG00010000560', 'ENSGALG00010029856'], ['ENSGALG00010003839', 'ENSGALG00010002377', 'ENSGALG00010029389', 'ENSGALG00010004962', 'ENSGALG00010000441'], ['ENSGALG00010004201', 'ENSGALG00010007958', 'ENSGALG00010015154', 'ENSGALG00010009096', 'ENSGALG00010008676'], ['ENSGALG00010008151', 'ENSGALG00010013312', 'ENSGALG00010005295', 'ENSGALG00010004577', 'ENSGALG00010015177'], ['ENSGALG00010018925', 'ENSGALG00010014974', 'ENSGALG00010013487', 'ENSGALG00010009518', 'ENSGALG00010009811'], ['ENSGALG00010019617', 'ENSGALG00010024638', 'ENSGALG00010023212', 'ENSGALG00010011873', 'ENSGALG00010009665'], ['ENSGALG00010012726', 'ENSGALG00010016746', 'ENSGALG00010027674', 'ENSGALG00010007575', 'ENSGALG00010001741'], ['ENSGALG00010002632', 'ENSGALG00010010106', 'ENSGALG00010005505', 'ENSGALG00010029684', 'ENSGALG00010020610'], ['ENSGALG00010029693', 'ENSGALG00010022500', 'ENSGALG00010029730', 'ENSGALG00010024804', 'ENSGALG00010023764'], ['ENSGALG00010021201', 'ENSGALG00010007232', 'ENSGALG00010023712', 'ENSGALG00010018092', 'ENSGALG00010029746'], ['ENSGALG00010017435', 'ENSGALG00010028150', 'ENSGALG00010014379', 'ENSGALG00010021610', 'ENSGALG00010029299'], ['ENSGALG00010009373', 'ENSGALG00010002341', 'ENSGALG00010009340', 'ENSGALG00010001897', 'ENSGALG00010013857'], ['ENSGALG00010024292', 'ENSGALG00010003221', 'ENSGALG00010003182', 'ENSGALG00010004498', 'ENSGALG00010003196'], ['ENSGALG00010021789', 'ENSGALG00010003201', 'ENSGALG00010020938', 'ENSGALG00010015449', 'ENSGALG00010015443'], ['ENSGALG00010022416', 'ENSGALG00010023773', 'ENSGALG00010003761', 'ENSGALG00010023181', 'ENSGALG00010022406'], ['ENSGALG00010022711', 'ENSGALG00010010226', 'ENSGALG00010025162', 'ENSGALG00010025791', 'ENSGALG00010021052'], ['ENSGALG00010029275', 'ENSGALG00010022562', 'ENSGALG00010025044', 'ENSGALG00010014547', 'ENSGALG00010029179'], ['ENSGALG00010007811', 'ENSGALG00010027790', 'ENSGALG00010016644', 'ENSGALG00010010116', 'ENSGALG00010006163'], ['ENSGALG00010011111', 'ENSGALG00010026232', 'ENSGALG00010029259', 'ENSGALG00010013277', 'ENSGALG00010026088'], ['ENSGALG00010009037', 'ENSGALG00010000105', 'ENSGALG00010029671', 'ENSGALG00010029229', 'ENSGALG00010013526'], ['ENSGALG00010023267', 'ENSGALG00010016892', 'ENSGALG00010023876', 'ENSGALG00010016441', 'ENSGALG00010013058'], ['ENSGALG00010013087', 'ENSGALG00010018536', 'ENSGALG00010012228', 'ENSGALG00010012340', 'ENSGALG00010012040'], ['ENSGALG00010024359', 'ENSGALG00010006669', 'ENSGALG00010005665', 'ENSGALG00010012294', 'ENSGALG00010027666'], ['ENSGALG00010010328', 'ENSGALG00010015394', 'ENSGALG00010005967', 'ENSGALG00010024550', 'ENSGALG00010013496'], ['ENSGALG00010013317', 'ENSGALG00010007472', 'ENSGALG00010009726', 'ENSGALG00010008348', 'ENSGALG00010011465'], ['ENSGALG00010001141', 'ENSGALG00010006249', 'ENSGALG00010009492', 'ENSGALG00010013550', 'ENSGALG00010005789'], ['ENSGALG00010026498', 'ENSGALG00010019967', 'ENSGALG00010018915', 'ENSGALG00010023346', 'ENSGALG00010029695'], ['ENSGALG00010023062', 'ENSGALG00010022172', 'ENSGALG00010014246', 'ENSGALG00010010971', 'ENSGALG00010011427'], ['ENSGALG00010019093', 'ENSGALG00010009170', 'ENSGALG00010027609', 'ENSGALG00010018867', 'ENSGALG00010028854'], ['ENSGALG00010009718', 'ENSGALG00010006596', 'ENSGALG00010026605', 'ENSGALG00010004666', 'ENSGALG00010027620'], ['ENSGALG00010007425', 'ENSGALG00010013667', 'ENSGALG00010022407', 'ENSGALG00010020925', 'ENSGALG00010003159'], ['ENSGALG00010024121', 'ENSGALG00010025839', 'ENSGALG00010016164', 'ENSGALG00010014013', 'ENSGALG00010001538'], ['ENSGALG00010012959', 'ENSGALG00010026044', 'ENSGALG00010011739', 'ENSGALG00010008264', 'ENSGALG00010006617'], ['ENSGALG00010022350', 'ENSGALG00010011194', 'ENSGALG00010020372', 'ENSGALG00010013540', 'ENSGALG00010023619'], ['ENSGALG00010005059', 'ENSGALG00010009938', 'ENSGALG00010011270', 'ENSGALG00010010787', 'ENSGALG00010015506'], ['ENSGALG00010018054', 'ENSGALG00010016919', 'ENSGALG00010018387', 'ENSGALG00010023448', 'ENSGALG00010023543'], ['ENSGALG00010013864', 'ENSGALG00010020134', 'ENSGALG00010013455', 'ENSGALG00010001996', 'ENSGALG00010014401'], ['ENSGALG00010000256', 'ENSGALG00010005822', 'ENSGALG00010019151', 'ENSGALG00010016401', 'ENSGALG00010003213'], ['ENSGALG00010022276', 'ENSGALG00010018453', 'ENSGALG00010024800', 'ENSGALG00010026697', 'ENSGALG00010021776'], ['ENSGALG00010008618', 'ENSGALG00010024596', 'ENSGALG00010005315', 'ENSGALG00010015606', 'ENSGALG00010021783'], ['ENSGALG00010012136', 'ENSGALG00010007434', 'ENSGALG00010011142', 'ENSGALG00010002352', 'ENSGALG00010002474'], ['ENSGALG00010009849', 'ENSGALG00010020676', 'ENSGALG00010002708', 'ENSGALG00010009749', 'ENSGALG00010018958'], ['ENSGALG00010012072', 'ENSGALG00010018564', 'ENSGALG00010021298', 'ENSGALG00010024953', 'ENSGALG00010018177'], ['ENSGALG00010004563', 'ENSGALG00010010656', 'ENSGALG00010018798', 'ENSGALG00010013279', 'ENSGALG00010016226'], ['ENSGALG00010017525', 'ENSGALG00010025955', 'ENSGALG00010019353', 'ENSGALG00010008898', 'ENSGALG00010007049'], ['ENSGALG00010026112', 'ENSGALG00010018726', 'ENSGALG00010008178', 'ENSGALG00010006250', 'ENSGALG00010020642'], ['ENSGALG00010001463', 'ENSGALG00010017603', 'ENSGALG00010009131', 'ENSGALG00010015039', 'ENSGALG00010029109'], ['ENSGALG00010029220', 'ENSGALG00010021214', 'ENSGALG00010015764', 'ENSGALG00010028422', 'ENSGALG00010013511'], ['ENSGALG00010025648', 'ENSGALG00010029597', 'ENSGALG00010026893', 'ENSGALG00010025861', 'ENSGALG00010028744'], ['ENSGALG00010017351', 'ENSGALG00010014190', 'ENSGALG00010023767', 'ENSGALG00010006019', 'ENSGALG00010005742'], ['ENSGALG00010015020', 'ENSGALG00010018417', 'ENSGALG00010025966', 'ENSGALG00010002274', 'ENSGALG00010018346'], ['ENSGALG00010007181', 'ENSGALG00010007404', 'ENSGALG00010008263', 'ENSGALG00010013617', 'ENSGALG00010010998'], ['ENSGALG00010024434', 'ENSGALG00010028072', 'ENSGALG00010029290', 'ENSGALG00010024070', 'ENSGALG00010026104'], ['ENSGALG00010018832', 'ENSGALG00010007238', 'ENSGALG00010022900', 'ENSGALG00010019299', 'ENSGALG00010027535'], ['ENSGALG00010028137', 'ENSGALG00010012219', 'ENSGALG00010018395', 'ENSGALG00010019067', 'ENSGALG00010026162'], ['ENSGALG00010025641', 'ENSGALG00010027509', 'ENSGALG00010012530', 'ENSGALG00010018744', 'ENSGALG00010024959'], ['ENSGALG00010008247', 'ENSGALG00010002376', 'ENSGALG00010004346', 'ENSGALG00010025558', 'ENSGALG00010001123'], ['ENSGALG00010010973', 'ENSGALG00010021711', 'ENSGALG00010003254', 'ENSGALG00010004375', 'ENSGALG00010004994'], ['ENSGALG00010010859', 'ENSGALG00010019477', 'ENSGALG00010007567', 'ENSGALG00010010766', 'ENSGALG00010005217'], ['ENSGALG00010023069', 'ENSGALG00010021412', 'ENSGALG00010024266', 'ENSGALG00010024598', 'ENSGALG00010029773'], ['ENSGALG00010026588', 'ENSGALG00010021632', 'ENSGALG00010017799', 'ENSGALG00010009440', 'ENSGALG00010019634'], ['ENSGALG00010023677', 'ENSGALG00010016993', 'ENSGALG00010025562', 'ENSGALG00010016465', 'ENSGALG00010018466'], ['ENSGALG00010017135', 'ENSGALG00010002576', 'ENSGALG00010009435', 'ENSGALG00010001680', 'ENSGALG00010028026'], ['ENSGALG00010014045', 'ENSGALG00010002348', 'ENSGALG00010018064', 'ENSGALG00010013797', 'ENSGALG00010024185'], ['ENSGALG00010013214', 'ENSGALG00010017703', 'ENSGALG00010019818', 'ENSGALG00010012993', 'ENSGALG00010018360'], ['ENSGALG00010017174', 'ENSGALG00010012865', 'ENSGALG00010002919', 'ENSGALG00010013081', 'ENSGALG00010016508'], ['ENSGALG00010016842', 'ENSGALG00010004481', 'ENSGALG00010027801', 'ENSGALG00010011515', 'ENSGALG00010000606'], ['ENSGALG00010016616', 'ENSGALG00010011905', 'ENSGALG00010003602', 'ENSGALG00010011001', 'ENSGALG00010004588'], ['ENSGALG00010007429', 'ENSGALG00010021521', 'ENSGALG00010019051', 'ENSGALG00010002921', 'ENSGALG00010027337'], ['ENSGALG00010026013', 'ENSGALG00010024519', 'ENSGALG00010009351', 'ENSGALG00010008310', 'ENSGALG00010028110'], ['ENSGALG00010010582', 'ENSGALG00010009095', 'ENSGALG00010001384', 'ENSGALG00010002833', 'ENSGALG00010020418'], ['ENSGALG00010002871', 'ENSGALG00010023211', 'ENSGALG00010018544', 'ENSGALG00010018379', 'ENSGALG00010003106'], ['ENSGALG00010010598', 'ENSGALG00010001331', 'ENSGALG00010009751', 'ENSGALG00010003369', 'ENSGALG00010010314'], ['ENSGALG00010002243', 'ENSGALG00010012943', 'ENSGALG00010003717', 'ENSGALG00010004012', 'ENSGALG00010020905'], ['ENSGALG00010023983', 'ENSGALG00010021106', 'ENSGALG00010019281', 'ENSGALG00010007819', 'ENSGALG00010015518'], ['ENSGALG00010008908', 'ENSGALG00010016084', 'ENSGALG00010007291', 'ENSGALG00010007015', 'ENSGALG00010013738'], ['ENSGALG00010025088', 'ENSGALG00010012874', 'ENSGALG00010025563', 'ENSGALG00010017723', 'ENSGALG00010000117'], ['ENSGALG00010027814', 'ENSGALG00010023510', 'ENSGALG00010022072', 'ENSGALG00010027183', 'ENSGALG00010017724'], ['ENSGALG00010008043', 'ENSGALG00010010893', 'ENSGALG00010005314', 'ENSGALG00010012847', 'ENSGALG00010021983'], ['ENSGALG00010024763', 'ENSGALG00010029048', 'ENSGALG00010001532', 'ENSGALG00010015814', 'ENSGALG00010018783'], ['ENSGALG00010003849', 'ENSGALG00010003401', 'ENSGALG00010001492', 'ENSGALG00010006829', 'ENSGALG00010029465'], ['ENSGALG00010012610', 'ENSGALG00010007998', 'ENSGALG00010029218', 'ENSGALG00010001191', 'ENSGALG00010012988'], ['ENSGALG00010016016', 'ENSGALG00010008866', 'ENSGALG00010012968', 'ENSGALG00010009000', 'ENSGALG00010014990'], ['ENSGALG00010016800', 'ENSGALG00010020612', 'ENSGALG00010025642', 'ENSGALG00010017580', 'ENSGALG00010008004'], ['ENSGALG00010017215', 'ENSGALG00010025806', 'ENSGALG00010016710', 'ENSGALG00010025077', 'ENSGALG00010025180'], ['ENSGALG00010011379', 'ENSGALG00010008368', 'ENSGALG00010018327', 'ENSGALG00010015112', 'ENSGALG00010002556'], ['ENSGALG00010006308', 'ENSGALG00010005096', 'ENSGALG00010013166', 'ENSGALG00010005204', 'ENSGALG00010004037'], ['ENSGALG00010018302', 'ENSGALG00010005408', 'ENSGALG00010021212', 'ENSGALG00010023311', 'ENSGALG00010011311'], ['ENSGALG00010025340', 'ENSGALG00010029727', 'ENSGALG00010000063', 'ENSGALG00010029676', 'ENSGALG00010016949'], ['ENSGALG00010020338', 'ENSGALG00010024149', 'ENSGALG00010027085', 'ENSGALG00010005254', 'ENSGALG00010020013'], ['ENSGALG00010020720', 'ENSGALG00010024585', 'ENSGALG00010029288', 'ENSGALG00010022954', 'ENSGALG00010029652'], ['ENSGALG00010022448', 'ENSGALG00010027115', 'ENSGALG00010001501', 'ENSGALG00010021064', 'ENSGALG00010001245'], ['ENSGALG00010002750', 'ENSGALG00010017419', 'ENSGALG00010021120', 'ENSGALG00010012803', 'ENSGALG00010025527'], ['ENSGALG00010001707', 'ENSGALG00010007069', 'ENSGALG00010010483', 'ENSGALG00010010395', 'ENSGALG00010003322'], ['ENSGALG00010001698', 'ENSGALG00010001654', 'ENSGALG00010024042', 'ENSGALG00010002855', 'ENSGALG00010020950'], ['ENSGALG00010022868', 'ENSGALG00010029531', 'ENSGALG00010015633', 'ENSGALG00010023384', 'ENSGALG00010020744'], ['ENSGALG00010014433', 'ENSGALG00010015593', 'ENSGALG00010009863', 'ENSGALG00010014021', 'ENSGALG00010014215'], ['ENSGALG00010012367', 'ENSGALG00010001187', 'ENSGALG00010011251', 'ENSGALG00010016346', 'ENSGALG00010029771'], ['ENSGALG00010023683', 'ENSGALG00010016770', 'ENSGALG00010022982', 'ENSGALG00010016596', 'ENSGALG00010000565'], ['ENSGALG00010026837', 'ENSGALG00010010732', 'ENSGALG00010015860', 'ENSGALG00010002399', 'ENSGALG00010010718'], ['ENSGALG00010013164', 'ENSGALG00010008832', 'ENSGALG00010029850', 'ENSGALG00010002113', 'ENSGALG00010014014'], ['ENSGALG00010022931', 'ENSGALG00010024113', 'ENSGALG00010027955', 'ENSGALG00010022042', 'ENSGALG00010026806'], ['ENSGALG00010004070', 'ENSGALG00010001127', 'ENSGALG00010001877', 'ENSGALG00010006410', 'ENSGALG00010024624'], ['ENSGALG00010018036', 'ENSGALG00010016773', 'ENSGALG00010026148', 'ENSGALG00010002492', 'ENSGALG00010004081'], ['ENSGALG00010019391', 'ENSGALG00010027427', 'ENSGALG00010014184', 'ENSGALG00010025386', 'ENSGALG00010007910'], ['ENSGALG00010028044', 'ENSGALG00010002982', 'ENSGALG00010013574', 'ENSGALG00010017638', 'ENSGALG00010010168'], ['ENSGALG00010015080', 'ENSGALG00010028106', 'ENSGALG00010020725', 'ENSGALG00010015124', 'ENSGALG00010012473'], ['ENSGALG00010015762', 'ENSGALG00010004719', 'ENSGALG00010025258', 'ENSGALG00010027606', 'ENSGALG00010023858'], ['ENSGALG00010015232', 'ENSGALG00010016243', 'ENSGALG00010016188', 'ENSGALG00010007387', 'ENSGALG00010015968'], ['ENSGALG00010020373', 'ENSGALG00010028589', 'ENSGALG00010005450', 'ENSGALG00010015298', 'ENSGALG00010004071'], ['ENSGALG00010008892', 'ENSGALG00010004196', 'ENSGALG00010023028', 'ENSGALG00010001729', 'ENSGALG00010005338'], ['ENSGALG00010014802', 'ENSGALG00010007976', 'ENSGALG00010000405', 'ENSGALG00010008475', 'ENSGALG00010000752'], ['ENSGALG00010005330', 'ENSGALG00010002197', 'ENSGALG00010025423', 'ENSGALG00010018937', 'ENSGALG00010026700'], ['ENSGALG00010006935', 'ENSGALG00010007268', 'ENSGALG00010013049', 'ENSGALG00010003188', 'ENSGALG00010000968'], ['ENSGALG00010027898', 'ENSGALG00010027906', 'ENSGALG00010026480', 'ENSGALG00010027929', 'ENSGALG00010026108'], ['ENSGALG00010015021', 'ENSGALG00010018634', 'ENSGALG00010027001', 'ENSGALG00010005104', 'ENSGALG00010022992'], ['ENSGALG00010013278', 'ENSGALG00010027951', 'ENSGALG00010029164', 'ENSGALG00010005922', 'ENSGALG00010027020'], ['ENSGALG00010023984', 'ENSGALG00010026137', 'ENSGALG00010025377', 'ENSGALG00010027984', 'ENSGALG00010027107'], ['ENSGALG00010000934', 'ENSGALG00010013342', 'ENSGALG00010027839', 'ENSGALG00010021526', 'ENSGALG00010010170'], ['ENSGALG00010005801', 'ENSGALG00010026773', 'ENSGALG00010020763', 'ENSGALG00010001936', 'ENSGALG00010025008']]

    def clusters_to_df(data):
        rows = []
        for i, sublist in enumerate(data, start=1):
            cluster_name = f"Cluster {i}"
            for species in sublist:
                # remove s__ prefix for display
                clean_species = species.replace("s__", "")
                rows.append({"Cluster": cluster_name, "Species": clean_species, "Value": 1})
        return pd.DataFrame(rows)

    df_0_4 = clusters_to_df(cluster_data_0_4)
    df_0_3 = clusters_to_df(cluster_data_0_3)
    df_0_2 = clusters_to_df(cluster_data_0_2)


    try:
        fig_0_4 = px.sunburst(df_0_4, path=["Cluster", "Species"], values="Value", title="Threshold 0.4")
        fig_0_4.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_4 = pio.to_html(
            fig_0_4,
            full_html=False,
            include_plotlyjs=False,
            config={"responsive": True},
            div_id="sunburst_04"
        )
    except:
        sunburst_html_0_4 = ""

    try:
        fig_0_3 = px.sunburst(df_0_3, path=["Cluster", "Species"], values="Value", title="Threshold 0.3")
        fig_0_3.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_3 = pio.to_html(
            fig_0_3,
            full_html=False,
            include_plotlyjs=False,
            config={"responsive": True},
            div_id="sunburst_03"
        )
    except:
        sunburst_html_0_3 = ""

    try:
        fig_0_2 = px.sunburst(df_0_2, path=["Cluster", "Species"], values="Value", title="Threshold 0.2")
        fig_0_2.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_2 = pio.to_html(
            fig_0_2,
            full_html=False,
            include_plotlyjs=False,
            config={"responsive": True},
            div_id="sunburst_02"
        )
    except:
        sunburst_html_0_2 = ""
    # 4) Render template
    return render(
        request,
        f"{host_type}/ileum.html",  # e.g. "isabrownv2/bacterien.html"
        {
            "host_type": host_type.title(),
            "data_type": "ileum",
            "description": "Top 100 displayed only. Gene info from Ensembl REST.",
            "tissue_types": list(tissue_files_ileum.keys()),
            "sunburst_html_0_4": sunburst_html_0_4,
            "sunburst_html_0_3": sunburst_html_0_3,
            "sunburst_html_0_2": sunburst_html_0_2,

        }
    )

def muscle_data_analysisv2(request, host_type='isabrownv2'):
    """
    1) Creates two sunbursts (threshold 0.5 & 0.6).
    2) Handles AJAX for single-var & multi-var filtering => returns top 100 in JSON.
    3) No server-side gene info or CSV download. The gene info & CSV are fully client-side.
    """
    # 1) Load data for sunburst
    if host_type == "ross":
        big_tsv_path = os.path.join(
            settings.BASE_DIR, "Avapp", "static", "Avapp", "csv",
            "Sylph_MoARossFull_estimatedCounts.tsv"
        )
    else:
        big_tsv_path = os.path.join(
            settings.BASE_DIR, "Avapp", "static", "Avapp", "csv",
            "Sylph_MoAIsaFull_estimatedCounts.tsv"
        )

    try:
        df_sunburst = pd.read_csv(big_tsv_path, sep="\t")
        # Suppose 'Taxa' has a semi-colon separated taxonomy chain
        splitted = df_sunburst["Taxa"].str.split(";", expand=True)
        # Possibly up to 7 levels
        taxonomy_levels = ["Domain", "Phylum", "Class", "Order", "Family", "Genus", "Species"]
        splitted.columns = taxonomy_levels[:splitted.shape[1]]
        df_sunburst = pd.concat([splitted, df_sunburst.drop("Taxa", axis=1)], axis=1)
    except Exception as e:
        return JsonResponse({"error": f"Error loading sunburst data: {e}"}, status=500)

    # 2) Handle AJAX (single-var, multi-var) => top 100
    if request.headers.get("x-requested-with") == "XMLHttpRequest":

        # (A) load_tissue => returns list of variables
        if "load_tissue" in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files_functionnel:
                return JsonResponse({"error": f"Invalid tissue: {tissue}"}, status=400)
            try:
                csv_path = os.path.join(
                    settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                    tissue_files_functionnel[tissue]
                )
                df_small = pd.read_csv(csv_path)
                variables = df_small.columns[2:].tolist()
                return JsonResponse({"variables": variables})
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV: {e}"}, status=500)

        # (B) Single-var => includes fetch_min_max + filter
        elif "multi_variable" not in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files_functionnel:
                return JsonResponse({"results": [], "error": "Missing or invalid tissue."}, status=400)
            csv_path = os.path.join(
                settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                tissue_files_functionnel[tissue]
            )

            try:
                df_all = pd.read_csv(csv_path)
                variables = df_all.columns[2:].tolist()
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV: {e}"}, status=500)

            selected_variable = request.GET.get("variable", variables[0] if variables else None)
            if selected_variable not in variables:
                return JsonResponse({"results": [], "error": "Invalid variable selected."}, status=400)

            # B1) fetch_min_max
            if "fetch_min_max" in request.GET:
                try:
                    col_vals = df_all[selected_variable].dropna()
                    return JsonResponse({
                        "min_correlation": float(col_vals.min()),
                        "max_correlation": float(col_vals.max()),
                    })
                except Exception as e:
                    return JsonResponse({"error": f"Error fetching min/max: {e}"}, status=500)

            # B2) filter => top 100
            try:
                correlation_min = float(request.GET.get("correlation_min", -1))
                correlation_max = float(request.GET.get("correlation_max", 1))
                min_accuracy = float(request.GET.get("accuracy", 0))

                if correlation_min > correlation_max:
                    return JsonResponse({"error": "Min correlation cannot exceed max correlation."}, status=400)

                filtered = df_all[
                    (df_all["accuracy"] >= min_accuracy)
                    & (df_all[selected_variable] >= correlation_min)
                    & (df_all[selected_variable] <= correlation_max)
                ]
                if filtered.empty:
                    return JsonResponse({"results": [], "total_count": 0})

                filtered.sort_values(by=selected_variable, ascending=False, inplace=True)
                total_count = len(filtered)
                top_100 = filtered.head(100)

                first_col = df_all.columns[0]
                results_list = []
                for _, row in top_100.iterrows():
                    results_list.append({
                        "var1": row[first_col],
                        "var2": selected_variable,
                        "accuracy": row["accuracy"],
                        "correlation": row[selected_variable]
                    })

                return JsonResponse({"results": results_list, "total_count": total_count})
            except Exception as e:
                return JsonResponse({"error": f"Error during single-var filter: {e}"}, status=500)

        # (C) Multi-var => top 100
        elif "multi_variable" in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files_functionnel:
                return JsonResponse({"results": [], "error": "Missing or invalid tissue."}, status=400)

            variables = request.GET.getlist("variables[]")
            if not variables:
                return JsonResponse({"results": [], "error": "No variables selected."}, status=400)

            csv_path = os.path.join(
                settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                tissue_files_functionnel[tissue]
            )
            try:
                df_all = pd.read_csv(csv_path)
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV file: {e}"}, status=500)

            try:
                correlation_min = float(request.GET.get("correlation_min", -1))
                correlation_max = float(request.GET.get("correlation_max", 1))
                min_accuracy = float(request.GET.get("accuracy", 0))
                if correlation_min > correlation_max:
                    return JsonResponse({"error": "Min correlation cannot exceed max correlation."}, status=400)

                filtered_parts = []
                first_col = df_all.columns[0]
                for var in variables:
                    if var not in df_all.columns:
                        continue
                    sub = df_all[
                        (df_all["accuracy"] >= min_accuracy)
                        & (df_all[var] >= correlation_min)
                        & (df_all[var] <= correlation_max)
                    ].copy()
                    if not sub.empty:
                        sub["var2"] = var
                        filtered_parts.append(sub)

                if not filtered_parts:
                    return JsonResponse({"results": [], "total_count": 0})

                combined = pd.concat(filtered_parts, ignore_index=True)
                corvals = []
                for _, row in combined.iterrows():
                    corvals.append(row[row["var2"]])
                combined["correlation"] = corvals

                combined.drop_duplicates(subset=[first_col, "var2"], inplace=True)
                combined.sort_values(by="correlation", ascending=False, inplace=True)
                total_count = len(combined)

                top_100 = combined.head(100)
                results_list = []
                for _, row in top_100.iterrows():
                    results_list.append({
                        "var1": row[first_col],
                        "var2": row["var2"],
                        "accuracy": row["accuracy"],
                        "correlation": row["correlation"]
                    })

                return JsonResponse({"results": results_list, "total_count": total_count})
            except Exception as e:
                return JsonResponse({"error": f"Error during multi-var filter: {e}"}, status=500)

        # If none matched
        return JsonResponse({"error":"No recognized AJAX action."}, status=400)

    # 3) Build the sunbursts for 0.5 & 0.6
    cluster_data_0_4 = [['ENSGALG00010003598', 'ENSGALG00010003613', 'ENSGALG00010003635', 'ENSGALG00010003537', 'ENSGALG00010003623',
      'ENSGALG00010003644', 'ENSGALG00010003640', 'ENSGALG00010003643', 'ENSGALG00010003575', 'ENSGALG00010003584',
      'ENSGALG00010003563', 'ENSGALG00010003614', 'ENSGALG00010003529', 'ENSGALG00010003576', 'ENSGALG00010003565'],
     ['ENSGALG00010016777', 'ENSGALG00010025092', 'ENSGALG00010003307', 'ENSGALG00010004096', 'ENSGALG00010007719',
      'ENSGALG00010023293', 'ENSGALG00010004980', 'ENSGALG00010026410', 'ENSGALG00010005860', 'ENSGALG00010023217',
      'ENSGALG00010001292', 'ENSGALG00010028177', 'ENSGALG00010026801', 'ENSGALG00010012839'],
     ['ENSGALG00010002289', 'ENSGALG00010003557', 'ENSGALG00010003549', 'ENSGALG00010002366', 'ENSGALG00010003626',
      'ENSGALG00010002378', 'ENSGALG00010003625', 'ENSGALG00010003633', 'ENSGALG00010003646', 'ENSGALG00010003542',
      'ENSGALG00010002050'],
     ['ENSGALG00010025592', 'ENSGALG00010018834', 'ENSGALG00010015793', 'ENSGALG00010029375', 'ENSGALG00010016869',
      'ENSGALG00010020572', 'ENSGALG00010017470'],
     ['ENSGALG00010014956', 'ENSGALG00010021130', 'ENSGALG00010014944', 'ENSGALG00010014972', 'ENSGALG00010014696',
      'ENSGALG00010005070', 'ENSGALG00010012708'],
     ['ENSGALG00010009327', 'ENSGALG00010029314', 'ENSGALG00010015031', 'ENSGALG00010013458', 'ENSGALG00010024116',
      'ENSGALG00010017715'],
     ['ENSGALG00010028434', 'ENSGALG00010023194', 'ENSGALG00010014389', 'ENSGALG00010014310', 'ENSGALG00010012362'],
     ['ENSGALG00010000353', 'ENSGALG00010023447', 'ENSGALG00010018767', 'ENSGALG00010028463', 'ENSGALG00010016500'],
     ['ENSGALG00010024828', 'ENSGALG00010026438', 'ENSGALG00010013416', 'ENSGALG00010024558', 'ENSGALG00010008731'],
     ['ENSGALG00010000476', 'ENSGALG00010010115', 'ENSGALG00010020517', 'ENSGALG00010025849', 'ENSGALG00010022969'],
     ['ENSGALG00010001654', 'ENSGALG00010002855', 'ENSGALG00010016040', 'ENSGALG00010024822', 'ENSGALG00010001698'],
     ['ENSGALG00010019673', 'ENSGALG00010014128', 'ENSGALG00010014324', 'ENSGALG00010009336', 'ENSGALG00010017540'],
     ['ENSGALG00010013805', 'ENSGALG00010011196', 'ENSGALG00010010749', 'ENSGALG00010002371', 'ENSGALG00010013186'],
     ['ENSGALG00010017724', 'ENSGALG00010021435', 'ENSGALG00010028171', 'ENSGALG00010013949', 'ENSGALG00010019896']]
    cluster_data_0_3 = [['ENSGALG00010003598', 'ENSGALG00010003613', 'ENSGALG00010003635', 'ENSGALG00010003537', 'ENSGALG00010003623',
      'ENSGALG00010003644', 'ENSGALG00010003640', 'ENSGALG00010003643', 'ENSGALG00010003575', 'ENSGALG00010003584',
      'ENSGALG00010003563', 'ENSGALG00010003614', 'ENSGALG00010003529', 'ENSGALG00010003576', 'ENSGALG00010003565'],
     ['ENSGALG00010016777', 'ENSGALG00010025092', 'ENSGALG00010003307', 'ENSGALG00010004096', 'ENSGALG00010007719',
      'ENSGALG00010023293', 'ENSGALG00010004980', 'ENSGALG00010026410', 'ENSGALG00010005860', 'ENSGALG00010023217',
      'ENSGALG00010001292', 'ENSGALG00010028177', 'ENSGALG00010026801', 'ENSGALG00010012839'],
     ['ENSGALG00010002289', 'ENSGALG00010003557', 'ENSGALG00010003549', 'ENSGALG00010002366', 'ENSGALG00010003626',
      'ENSGALG00010002378', 'ENSGALG00010003625', 'ENSGALG00010003633', 'ENSGALG00010003646', 'ENSGALG00010003542',
      'ENSGALG00010002050'],
     ['ENSGALG00010019246', 'ENSGALG00010027359', 'ENSGALG00010016500', 'ENSGALG00010000353', 'ENSGALG00010023447',
      'ENSGALG00010017207', 'ENSGALG00010018767', 'ENSGALG00010028463', 'ENSGALG00010028201', 'ENSGALG00010021558'],
     ['ENSGALG00010029731', 'ENSGALG00010017621', 'ENSGALG00010021123', 'ENSGALG00010022890', 'ENSGALG00010019335',
      'ENSGALG00010006835', 'ENSGALG00010004841', 'ENSGALG00010002374', 'ENSGALG00010007614', 'ENSGALG00010002886'],
     ['ENSGALG00010028434', 'ENSGALG00010017250', 'ENSGALG00010014389', 'ENSGALG00010014310', 'ENSGALG00010012362',
      'ENSGALG00010021177', 'ENSGALG00010023194', 'ENSGALG00010029162'],
     ['ENSGALG00010002817', 'ENSGALG00010000301', 'ENSGALG00010009603', 'ENSGALG00010011326', 'ENSGALG00010016303',
      'ENSGALG00010021118', 'ENSGALG00010010855', 'ENSGALG00010002752'],
     ['ENSGALG00010014956', 'ENSGALG00010021130', 'ENSGALG00010014944', 'ENSGALG00010014972', 'ENSGALG00010014696',
      'ENSGALG00010005070', 'ENSGALG00010012708'],
     ['ENSGALG00010004995', 'ENSGALG00010006069', 'ENSGALG00010005583', 'ENSGALG00010024717', 'ENSGALG00010003164',
      'ENSGALG00010001612', 'ENSGALG00010016067'],
     ['ENSGALG00010005356', 'ENSGALG00010029593', 'ENSGALG00010012195', 'ENSGALG00010012431', 'ENSGALG00010007430',
      'ENSGALG00010007137', 'ENSGALG00010001491'],
     ['ENSGALG00010029341', 'ENSGALG00010029440', 'ENSGALG00010006245', 'ENSGALG00010010014', 'ENSGALG00010014244',
      'ENSGALG00010024326', 'ENSGALG00010021187'],
     ['ENSGALG00010021749', 'ENSGALG00010029250', 'ENSGALG00010024582', 'ENSGALG00010012055', 'ENSGALG00010024437',
      'ENSGALG00010017344', 'ENSGALG00010027147'],
     ['ENSGALG00010002543', 'ENSGALG00010017421', 'ENSGALG00010021960', 'ENSGALG00010026046', 'ENSGALG00010012144',
      'ENSGALG00010005405', 'ENSGALG00010012052'],
     ['ENSGALG00010025592', 'ENSGALG00010018834', 'ENSGALG00010015793', 'ENSGALG00010029375', 'ENSGALG00010016869',
      'ENSGALG00010020572', 'ENSGALG00010017470'],
     ['ENSGALG00010004973', 'ENSGALG00010018075', 'ENSGALG00010023080', 'ENSGALG00010022526', 'ENSGALG00010021704',
      'ENSGALG00010027927'],
     ['ENSGALG00010015792', 'ENSGALG00010027698', 'ENSGALG00010024030', 'ENSGALG00010001512', 'ENSGALG00010024283',
      'ENSGALG00010006041'],
     ['ENSGALG00010027821', 'ENSGALG00010020015', 'ENSGALG00010017256', 'ENSGALG00010017393', 'ENSGALG00010012606',
      'ENSGALG00010012315'],
     ['ENSGALG00010028054', 'ENSGALG00010028019', 'ENSGALG00010021346', 'ENSGALG00010027609', 'ENSGALG00010027131',
      'ENSGALG00010029495'],
     ['ENSGALG00010007532', 'ENSGALG00010019646', 'ENSGALG00010022923', 'ENSGALG00010018319', 'ENSGALG00010027282',
      'ENSGALG00010021381'],
     ['ENSGALG00010007500', 'ENSGALG00010011293', 'ENSGALG00010015141', 'ENSGALG00010020723', 'ENSGALG00010002627',
      'ENSGALG00010015092'],
     ['ENSGALG00010019655', 'ENSGALG00010011440', 'ENSGALG00010009571', 'ENSGALG00010012100', 'ENSGALG00010024496',
      'ENSGALG00010021745'],
     ['ENSGALG00010009327', 'ENSGALG00010029314', 'ENSGALG00010015031', 'ENSGALG00010013458', 'ENSGALG00010024116',
      'ENSGALG00010017715'],
     ['ENSGALG00010015921', 'ENSGALG00010021564', 'ENSGALG00010000224', 'ENSGALG00010003248', 'ENSGALG00010019255',
      'ENSGALG00010000588'],
     ['ENSGALG00010001654', 'ENSGALG00010002855', 'ENSGALG00010016040', 'ENSGALG00010018036', 'ENSGALG00010024822',
      'ENSGALG00010001698'],
     ['ENSGALG00010002148', 'ENSGALG00010025368', 'ENSGALG00010011793', 'ENSGALG00010011984', 'ENSGALG00010021762',
      'ENSGALG00010003205'],
     ['ENSGALG00010022108', 'ENSGALG00010021635', 'ENSGALG00010021335', 'ENSGALG00010024024', 'ENSGALG00010012102',
      'ENSGALG00010001347'],
     ['ENSGALG00010013345', 'ENSGALG00010021013', 'ENSGALG00010025414', 'ENSGALG00010022764', 'ENSGALG00010002373',
      'ENSGALG00010014114'],
     ['ENSGALG00010023668', 'ENSGALG00010015029', 'ENSGALG00010011936', 'ENSGALG00010027969', 'ENSGALG00010011029'],
     ['ENSGALG00010020558', 'ENSGALG00010019451', 'ENSGALG00010021358', 'ENSGALG00010000407', 'ENSGALG00010025590'],
     ['ENSGALG00010028031', 'ENSGALG00010017221', 'ENSGALG00010021175', 'ENSGALG00010018623', 'ENSGALG00010016547'],
     ['ENSGALG00010016370', 'ENSGALG00010005383', 'ENSGALG00010021623', 'ENSGALG00010021071', 'ENSGALG00010000003'],
     ['ENSGALG00010012938', 'ENSGALG00010011746', 'ENSGALG00010003868', 'ENSGALG00010019732', 'ENSGALG00010019253'],
     ['ENSGALG00010022173', 'ENSGALG00010006178', 'ENSGALG00010013438', 'ENSGALG00010025974', 'ENSGALG00010019288'],
     ['ENSGALG00010013805', 'ENSGALG00010011196', 'ENSGALG00010010749', 'ENSGALG00010002371', 'ENSGALG00010013186'],
     ['ENSGALG00010027086', 'ENSGALG00010016932', 'ENSGALG00010023635', 'ENSGALG00010021121', 'ENSGALG00010016118'],
     ['ENSGALG00010002235', 'ENSGALG00010005772', 'ENSGALG00010017973', 'ENSGALG00010012436', 'ENSGALG00010016896'],
     ['ENSGALG00010013119', 'ENSGALG00010024472', 'ENSGALG00010018441', 'ENSGALG00010021229', 'ENSGALG00010012574'],
     ['ENSGALG00010009239', 'ENSGALG00010024164', 'ENSGALG00010001501', 'ENSGALG00010008960', 'ENSGALG00010016027'],
     ['ENSGALG00010020890', 'ENSGALG00010012988', 'ENSGALG00010020612', 'ENSGALG00010029218', 'ENSGALG00010015296'],
     ['ENSGALG00010003889', 'ENSGALG00010010447', 'ENSGALG00010008313', 'ENSGALG00010015984', 'ENSGALG00010018294'],
     ['ENSGALG00010023405', 'ENSGALG00010020179', 'ENSGALG00010001156', 'ENSGALG00010009197', 'ENSGALG00010026724'],
     ['ENSGALG00010023115', 'ENSGALG00010019212', 'ENSGALG00010026148', 'ENSGALG00010021741', 'ENSGALG00010027733'],
     ['ENSGALG00010000476', 'ENSGALG00010010115', 'ENSGALG00010020517', 'ENSGALG00010025849', 'ENSGALG00010022969'],
     ['ENSGALG00010024552', 'ENSGALG00010007891', 'ENSGALG00010014967', 'ENSGALG00010015085', 'ENSGALG00010014082'],
     ['ENSGALG00010029305', 'ENSGALG00010010905', 'ENSGALG00010025130', 'ENSGALG00010010528', 'ENSGALG00010015603'],
     ['ENSGALG00010000367', 'ENSGALG00010025247', 'ENSGALG00010001191', 'ENSGALG00010028021', 'ENSGALG00010028036'],
     ['ENSGALG00010000599', 'ENSGALG00010022886', 'ENSGALG00010025905', 'ENSGALG00010002741', 'ENSGALG00010022717'],
     ['ENSGALG00010016924', 'ENSGALG00010013551', 'ENSGALG00010020887', 'ENSGALG00010001426', 'ENSGALG00010004507'],
     ['ENSGALG00010017724', 'ENSGALG00010021435', 'ENSGALG00010028171', 'ENSGALG00010013949', 'ENSGALG00010019896'],
     ['ENSGALG00010009540', 'ENSGALG00010005695', 'ENSGALG00010024624', 'ENSGALG00010004639', 'ENSGALG00010009686'],
     ['ENSGALG00010026898', 'ENSGALG00010017577', 'ENSGALG00010003160', 'ENSGALG00010010351', 'ENSGALG00010018904'],
     ['ENSGALG00010013382', 'ENSGALG00010017475', 'ENSGALG00010011965', 'ENSGALG00010010706', 'ENSGALG00010024732'],
     ['ENSGALG00010024828', 'ENSGALG00010026438', 'ENSGALG00010013416', 'ENSGALG00010024558', 'ENSGALG00010008731'],
     ['ENSGALG00010019673', 'ENSGALG00010014128', 'ENSGALG00010014324', 'ENSGALG00010009336', 'ENSGALG00010017540'],
     ['ENSGALG00010002592', 'ENSGALG00010021240', 'ENSGALG00010005763', 'ENSGALG00010018123', 'ENSGALG00010017937'],
     ['ENSGALG00010021080', 'ENSGALG00010017741', 'ENSGALG00010027012', 'ENSGALG00010021102', 'ENSGALG00010018534'],
     ['ENSGALG00010005396', 'ENSGALG00010010347', 'ENSGALG00010016994', 'ENSGALG00010013191', 'ENSGALG00010003180']]

    cluster_data_0_5 =    [['ENSGALG00010003598', 'ENSGALG00010003613', 'ENSGALG00010003635', 'ENSGALG00010003537', 'ENSGALG00010003623',
      'ENSGALG00010003644', 'ENSGALG00010003640', 'ENSGALG00010003643', 'ENSGALG00010003575', 'ENSGALG00010003584',
      'ENSGALG00010003563', 'ENSGALG00010003614', 'ENSGALG00010003529', 'ENSGALG00010003576', 'ENSGALG00010003565'],
     ['ENSGALG00010016777', 'ENSGALG00010025092', 'ENSGALG00010003307', 'ENSGALG00010004096', 'ENSGALG00010007719',
      'ENSGALG00010023293', 'ENSGALG00010004980', 'ENSGALG00010028177', 'ENSGALG00010026801', 'ENSGALG00010012839'],
     ['ENSGALG00010003557', 'ENSGALG00010003625', 'ENSGALG00010003549', 'ENSGALG00010003646', 'ENSGALG00010003633',
      'ENSGALG00010003542'],
     ['ENSGALG00010028434', 'ENSGALG00010023194', 'ENSGALG00010014389', 'ENSGALG00010014310', 'ENSGALG00010012362'],
     ['ENSGALG00010017724', 'ENSGALG00010021435', 'ENSGALG00010028171', 'ENSGALG00010013949', 'ENSGALG00010019896'],
     ['ENSGALG00010002378', 'ENSGALG00010002289', 'ENSGALG00010002366', 'ENSGALG00010003626', 'ENSGALG00010002050']]
    def clusters_to_df(data):
        rows = []
        for i, sublist in enumerate(data, start=1):
            cluster_name = f"Cluster {i}"
            for species in sublist:
                # remove s__ prefix for display
                clean_species = species.replace("s__", "")
                rows.append({"Cluster": cluster_name, "Species": clean_species, "Value": 1})
        return pd.DataFrame(rows)

    df_0_4 = clusters_to_df(cluster_data_0_4)
    df_0_3 = clusters_to_df(cluster_data_0_3)
    df_0_5 = clusters_to_df(cluster_data_0_5)


    try:
        fig_0_4 = px.sunburst(df_0_4, path=["Cluster", "Species"], values="Value", title="Threshold 0.4")
        fig_0_4.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_4 = pio.to_html(
            fig_0_4,
            full_html=False,
            include_plotlyjs=False,
            config={"responsive": True},
            div_id="sunburst_04"
        )
    except:
        sunburst_html_0_4 = ""

    try:
        fig_0_3 = px.sunburst(df_0_3, path=["Cluster", "Species"], values="Value", title="Threshold 0.3")
        fig_0_3.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_3 = pio.to_html(
            fig_0_3,
            full_html=False,
            include_plotlyjs=False,
            config={"responsive": True},
            div_id="sunburst_03"
        )
    except:
        sunburst_html_0_3 = ""

    try:
        fig_0_5 = px.sunburst(df_0_5, path=["Cluster", "Species"], values="Value", title="Threshold 0.5")
        fig_0_5.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_5 = pio.to_html(
            fig_0_5,
            full_html=False,
            include_plotlyjs=False,
            config={"responsive": True},
            div_id="sunburst_05"
        )
    except:
        sunburst_html_0_5 = ""
    # 4) Render template
    return render(
        request,
        f"{host_type}/muscle.html",  # e.g. "isabrownv2/bacterien.html"
        {
            "host_type": host_type.title(),
            "data_type": "muscle",
            "description": "Top 100 displayed only. Gene info from Ensembl REST.",
            "tissue_types": list(tissue_files_functionnel.keys()),
            "sunburst_html_0_4": sunburst_html_0_4,
            "sunburst_html_0_3": sunburst_html_0_3,
            "sunburst_html_0_5": sunburst_html_0_5,

        }
    )

def process_data_scfa2(request, host_type='isabrownv2'):
    """
    1) Creates two sunbursts (threshold 0.5 & 0.6).
    2) Handles AJAX for single-var & multi-var filtering => returns top 100 in JSON.
    3) No server-side gene info or CSV download. The gene info & CSV are fully client-side.
    """
    # 1) Load data for sunburst
    if host_type == "ross":
        big_tsv_path = os.path.join(
            settings.BASE_DIR, "Avapp", "static", "Avapp", "csv",
            "Sylph_MoARossFull_estimatedCounts.tsv"
        )
    else:
        big_tsv_path = os.path.join(
            settings.BASE_DIR, "Avapp", "static", "Avapp", "csv",
            "Sylph_MoAIsaFull_estimatedCounts.tsv"
        )

    try:
        df_sunburst = pd.read_csv(big_tsv_path, sep="\t")
        # Suppose 'Taxa' has a semi-colon separated taxonomy chain
        splitted = df_sunburst["Taxa"].str.split(";", expand=True)
        # Possibly up to 7 levels
        taxonomy_levels = ["Domain", "Phylum", "Class", "Order", "Family", "Genus", "Species"]
        splitted.columns = taxonomy_levels[:splitted.shape[1]]
        df_sunburst = pd.concat([splitted, df_sunburst.drop("Taxa", axis=1)], axis=1)
    except Exception as e:
        return JsonResponse({"error": f"Error loading sunburst data: {e}"}, status=500)

    # 2) Handle AJAX (single-var, multi-var) => top 100
    if request.headers.get("x-requested-with") == "XMLHttpRequest":

        # (A) load_tissue => returns list of variables
        if "load_tissue" in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files_acid:
                return JsonResponse({"error": f"Invalid tissue: {tissue}"}, status=400)
            try:
                csv_path = os.path.join(
                    settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                    tissue_files_acid[tissue]
                )
                df_small = pd.read_csv(csv_path)
                variables = df_small.columns[2:].tolist()
                return JsonResponse({"variables": variables})
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV: {e}"}, status=500)

        # (B) Single-var => includes fetch_min_max + filter
        elif "multi_variable" not in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files_acid:
                return JsonResponse({"results": [], "error": "Missing or invalid tissue."}, status=400)
            csv_path = os.path.join(
                settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                tissue_files_acid[tissue]
            )

            try:
                df_all = pd.read_csv(csv_path)
                variables = df_all.columns[2:].tolist()
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV: {e}"}, status=500)

            selected_variable = request.GET.get("variable", variables[0] if variables else None)
            if selected_variable not in variables:
                return JsonResponse({"results": [], "error": "Invalid variable selected."}, status=400)

            # B1) fetch_min_max
            if "fetch_min_max" in request.GET:
                try:
                    col_vals = df_all[selected_variable].dropna()
                    return JsonResponse({
                        "min_correlation": float(col_vals.min()),
                        "max_correlation": float(col_vals.max()),
                    })
                except Exception as e:
                    return JsonResponse({"error": f"Error fetching min/max: {e}"}, status=500)

            # B2) filter => top 100
            try:
                correlation_min = float(request.GET.get("correlation_min", -1))
                correlation_max = float(request.GET.get("correlation_max", 1))
                min_accuracy = float(request.GET.get("accuracy", 0))

                if correlation_min > correlation_max:
                    return JsonResponse({"error": "Min correlation cannot exceed max correlation."}, status=400)

                filtered = df_all[
                    (df_all["accuracy"] >= min_accuracy)
                    & (df_all[selected_variable] >= correlation_min)
                    & (df_all[selected_variable] <= correlation_max)
                ]
                if filtered.empty:
                    return JsonResponse({"results": [], "total_count": 0})

                filtered.sort_values(by=selected_variable, ascending=False, inplace=True)
                total_count = len(filtered)
                top_100 = filtered.head(100)

                first_col = df_all.columns[0]
                results_list = []
                for _, row in top_100.iterrows():
                    results_list.append({
                        "var1": row[first_col],
                        "var2": selected_variable,
                        "accuracy": row["accuracy"],
                        "correlation": row[selected_variable]
                    })

                return JsonResponse({"results": results_list, "total_count": total_count})
            except Exception as e:
                return JsonResponse({"error": f"Error during single-var filter: {e}"}, status=500)

        # (C) Multi-var => top 100
        elif "multi_variable" in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files_functionnel:
                return JsonResponse({"results": [], "error": "Missing or invalid tissue."}, status=400)

            variables = request.GET.getlist("variables[]")
            if not variables:
                return JsonResponse({"results": [], "error": "No variables selected."}, status=400)

            csv_path = os.path.join(
                settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                tissue_files_acid[tissue]
            )
            try:
                df_all = pd.read_csv(csv_path)
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV file: {e}"}, status=500)

            try:
                correlation_min = float(request.GET.get("correlation_min", -1))
                correlation_max = float(request.GET.get("correlation_max", 1))
                min_accuracy = float(request.GET.get("accuracy", 0))
                if correlation_min > correlation_max:
                    return JsonResponse({"error": "Min correlation cannot exceed max correlation."}, status=400)

                filtered_parts = []
                first_col = df_all.columns[0]
                for var in variables:
                    if var not in df_all.columns:
                        continue
                    sub = df_all[
                        (df_all["accuracy"] >= min_accuracy)
                        & (df_all[var] >= correlation_min)
                        & (df_all[var] <= correlation_max)
                    ].copy()
                    if not sub.empty:
                        sub["var2"] = var
                        filtered_parts.append(sub)

                if not filtered_parts:
                    return JsonResponse({"results": [], "total_count": 0})

                combined = pd.concat(filtered_parts, ignore_index=True)
                corvals = []
                for _, row in combined.iterrows():
                    corvals.append(row[row["var2"]])
                combined["correlation"] = corvals

                combined.drop_duplicates(subset=[first_col, "var2"], inplace=True)
                combined.sort_values(by="correlation", ascending=False, inplace=True)
                total_count = len(combined)

                top_100 = combined.head(100)
                results_list = []
                for _, row in top_100.iterrows():
                    results_list.append({
                        "var1": row[first_col],
                        "var2": row["var2"],
                        "accuracy": row["accuracy"],
                        "correlation": row["correlation"]
                    })

                return JsonResponse({"results": results_list, "total_count": total_count})
            except Exception as e:
                return JsonResponse({"error": f"Error during multi-var filter: {e}"}, status=500)

        # If none matched
        return JsonResponse({"error":"No recognized AJAX action."}, status=400)

        # File paths
    peak_area_file = os.path.join("Avapp", "static", "Avapp", "csv", "peak_area_scfa.csv")
    peak_area_df = pd.read_csv(peak_area_file, sep=",")

    # Top Samples Analysis
    top_n = 25  # Number of top samples to display
    melted_data = peak_area_df.melt(
        id_vars=["MS-Omics ID"], var_name="Sample", value_name="Peak Area"
    )
    top_samples = (
        melted_data.groupby("Sample")["Peak Area"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .index
    )
    top_samples_data = melted_data[melted_data["Sample"].isin(top_samples)]

    # Plot for Top Samples
    top_samples_plot = px.bar(
        top_samples_data,
        x="Sample",
        y="Peak Area",
        color="MS-Omics ID",
        title=f"Composition of Samples based of Ms-Omics ID Compound",
    )
    top_samples_plot_html = pio.to_html(top_samples_plot, full_html=False)

    # Available MS-Omics IDs for selection
    available_ids = peak_area_df["MS-Omics ID"].tolist()

    # Handle search input for sunburst
    selected_sunburst_id = request.GET.get("sunburst_ms_omics", "").strip()

    # Prepare data for sunburst (only if a valid ID is provided)
    sunburst_plot_html = None
    if selected_sunburst_id and selected_sunburst_id in available_ids:
        sunburst_data = peak_area_df[peak_area_df["MS-Omics ID"] == selected_sunburst_id]
        sunburst_data = sunburst_data.melt(
            id_vars=["MS-Omics ID"], var_name="Sample", value_name="Peak Area"
        )

        sunburst_plot = px.sunburst(
            sunburst_data,
            path=["MS-Omics ID", "Sample"],
            values="Peak Area",
            title=f"Sunburst Chart for {selected_sunburst_id}",
        )
        sunburst_plot_html = pio.to_html(sunburst_plot, full_html=False)

        # Pass context to the template
        # context = {
        #     "host_type": host_type.title(),
        #     "data_type": "Molecule",
        #     "description": "Analyze the top samples by peak area and visualize the composition of MS-Omics IDs.",
        #     "top_n": top_n,
        #     "top_samples_plot": top_samples_plot_html,
        #     "available_ids": available_ids,
        #     "selected_sunburst_id": selected_sunburst_id,
        #     "sunburst_plot": sunburst_plot_html,
        # }
    # return render(
    #     request,
    #     f"{host_type}/molecule.html",  # e.g. "isabrownv2/bacterien.html"
    #     {
    #         "host_type": host_type.title(),
    #         "data_type": "scfa",
    #         "description": "Top 100 displayed only. Gene info from Ensembl REST.",
    #         "tissue_types": list(tissue_files_molecule.keys()),
    #         "top_samples_plot": top_samples_plot_html,
    #
    #     }
    # )
    return render(
            request,
            f"{host_type}/scfa.html",  # e.g. "isabrownv2/bacterien.html"
            {
                "host_type": host_type.title(),
                    "data_type": "Molecule",
                    "description": "Analyze the top samples by peak area and visualize the composition of MS-Omics IDs.",
                    "top_n": top_n,
                    "top_samples_plot": top_samples_plot_html,
                    "available_ids": available_ids,
                    "selected_sunburst_id": selected_sunburst_id,
                    "sunburst_plot": sunburst_plot_html,
            }
        )

def process_data_functionnal2(request, host_type='isabrownv2'):
    """
    1) Creates two sunbursts (threshold 0.5 & 0.6).
    2) Handles AJAX for single-var & multi-var filtering => returns top 100 in JSON.
    3) No server-side gene info or CSV download. The gene info & CSV are fully client-side.
    """
    # 1) Load data for sunburst
    if host_type == "ross":
        big_tsv_path = os.path.join(
            settings.BASE_DIR, "Avapp", "static", "Avapp", "csv",
            "Sylph_MoARossFull_estimatedCounts.tsv"
        )
    else:
        big_tsv_path = os.path.join(
            settings.BASE_DIR, "Avapp", "static", "Avapp", "csv",
            "Sylph_MoAIsaFull_estimatedCounts.tsv"
        )

    try:
        df_sunburst = pd.read_csv(big_tsv_path, sep="\t")
        # Suppose 'Taxa' has a semi-colon separated taxonomy chain
        splitted = df_sunburst["Taxa"].str.split(";", expand=True)
        # Possibly up to 7 levels
        taxonomy_levels = ["Domain", "Phylum", "Class", "Order", "Family", "Genus", "Species"]
        splitted.columns = taxonomy_levels[:splitted.shape[1]]
        df_sunburst = pd.concat([splitted, df_sunburst.drop("Taxa", axis=1)], axis=1)
    except Exception as e:
        return JsonResponse({"error": f"Error loading sunburst data: {e}"}, status=500)

    # 2) Handle AJAX (single-var, multi-var) => top 100
    if request.headers.get("x-requested-with") == "XMLHttpRequest":

        # (A) load_tissue => returns list of variables
        if "load_tissue" in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files_functionnel:
                return JsonResponse({"error": f"Invalid tissue: {tissue}"}, status=400)
            try:
                csv_path = os.path.join(
                    settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                    tissue_files_functionnel[tissue]
                )
                df_small = pd.read_csv(csv_path)
                variables = df_small.columns[2:].tolist()
                return JsonResponse({"variables": variables})
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV: {e}"}, status=500)

        # (B) Single-var => includes fetch_min_max + filter
        elif "multi_variable" not in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files_functionnel:
                return JsonResponse({"results": [], "error": "Missing or invalid tissue."}, status=400)
            csv_path = os.path.join(
                settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                tissue_files_functionnel[tissue]
            )

            try:
                df_all = pd.read_csv(csv_path)
                variables = df_all.columns[2:].tolist()
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV: {e}"}, status=500)

            selected_variable = request.GET.get("variable", variables[0] if variables else None)
            if selected_variable not in variables:
                return JsonResponse({"results": [], "error": "Invalid variable selected."}, status=400)

            # B1) fetch_min_max
            if "fetch_min_max" in request.GET:
                try:
                    col_vals = df_all[selected_variable].dropna()
                    return JsonResponse({
                        "min_correlation": float(col_vals.min()),
                        "max_correlation": float(col_vals.max()),
                    })
                except Exception as e:
                    return JsonResponse({"error": f"Error fetching min/max: {e}"}, status=500)

            # B2) filter => top 100
            try:
                correlation_min = float(request.GET.get("correlation_min", -1))
                correlation_max = float(request.GET.get("correlation_max", 1))
                min_accuracy = float(request.GET.get("accuracy", 0))

                if correlation_min > correlation_max:
                    return JsonResponse({"error": "Min correlation cannot exceed max correlation."}, status=400)

                filtered = df_all[
                    (df_all["accuracy"] >= min_accuracy)
                    & (df_all[selected_variable] >= correlation_min)
                    & (df_all[selected_variable] <= correlation_max)
                ]
                if filtered.empty:
                    return JsonResponse({"results": [], "total_count": 0})

                filtered.sort_values(by=selected_variable, ascending=False, inplace=True)
                total_count = len(filtered)
                top_100 = filtered.head(100)

                first_col = df_all.columns[0]
                results_list = []
                for _, row in top_100.iterrows():
                    results_list.append({
                        "var1": row[first_col],
                        "var2": selected_variable,
                        "accuracy": row["accuracy"],
                        "correlation": row[selected_variable]
                    })

                return JsonResponse({"results": results_list, "total_count": total_count})
            except Exception as e:
                return JsonResponse({"error": f"Error during single-var filter: {e}"}, status=500)

        # (C) Multi-var => top 100
        elif "multi_variable" in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files_functionnel:
                return JsonResponse({"results": [], "error": "Missing or invalid tissue."}, status=400)

            variables = request.GET.getlist("variables[]")
            if not variables:
                return JsonResponse({"results": [], "error": "No variables selected."}, status=400)

            csv_path = os.path.join(
                settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                tissue_files_functionnel[tissue]
            )
            try:
                df_all = pd.read_csv(csv_path)
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV file: {e}"}, status=500)

            try:
                correlation_min = float(request.GET.get("correlation_min", -1))
                correlation_max = float(request.GET.get("correlation_max", 1))
                min_accuracy = float(request.GET.get("accuracy", 0))
                if correlation_min > correlation_max:
                    return JsonResponse({"error": "Min correlation cannot exceed max correlation."}, status=400)

                filtered_parts = []
                first_col = df_all.columns[0]
                for var in variables:
                    if var not in df_all.columns:
                        continue
                    sub = df_all[
                        (df_all["accuracy"] >= min_accuracy)
                        & (df_all[var] >= correlation_min)
                        & (df_all[var] <= correlation_max)
                    ].copy()
                    if not sub.empty:
                        sub["var2"] = var
                        filtered_parts.append(sub)

                if not filtered_parts:
                    return JsonResponse({"results": [], "total_count": 0})

                combined = pd.concat(filtered_parts, ignore_index=True)
                corvals = []
                for _, row in combined.iterrows():
                    corvals.append(row[row["var2"]])
                combined["correlation"] = corvals

                combined.drop_duplicates(subset=[first_col, "var2"], inplace=True)
                combined.sort_values(by="correlation", ascending=False, inplace=True)
                total_count = len(combined)

                top_100 = combined.head(100)
                results_list = []
                for _, row in top_100.iterrows():
                    results_list.append({
                        "var1": row[first_col],
                        "var2": row["var2"],
                        "accuracy": row["accuracy"],
                        "correlation": row["correlation"]
                    })

                return JsonResponse({"results": results_list, "total_count": total_count})
            except Exception as e:
                return JsonResponse({"error": f"Error during multi-var filter: {e}"}, status=500)

        # If none matched
        return JsonResponse({"error":"No recognized AJAX action."}, status=400)

    # 3) Build the sunbursts for 0.5 & 0.6
    cluster_data_0_4 = [['fructose 2,6-bisphosphate biosynthesis', 'glycerol degradation I', 'formate oxidation to CO2', '3-dehydroquinate biosynthesis II (archaea)', 'nitrate reduction V (assimilatory)', 'pyrimidine deoxyribonucleotide phosphorylation', 'ulvan degradation', 'phosphatidylinositol biosynthesis I (bacteria)', 'CDP-4-dehydro-3,6-dideoxy-D-glucose biosynthesis', 'fluoroacetate degradation', 'volatile esters biosynthesis (during fruit ripening)', 'L-alanine biosynthesis I', 'heme b biosynthesis V (aerobic)', 'heme b biosynthesis II (oxygen-independent)', 'D-myo-inositol (1,4,5)-trisphosphate biosynthesis'], ['trehalose degradation VI (periplasmic)', 'Extracellular starch(27n) degradation', '(S)-lactate fermentation to propanoate', 'L-threonine degradation V', 'trehalose degradation II (cytosolic)', '2-aminoethylphosphonate degradation II', 'lipoate biosynthesis and incorporation II', '2-acetamido-4-amino-2,4,6-trideoxy-&alpha;-D-galactosyl-diphospho-ditrans,octacis-undecaprenol biosynthesis', 'L-N&delta;-acetylornithine biosynthesis', 'L-glutamate degradation IX (via 4-aminobutanoate)', 'L-arginine degradation I (arginase pathway)', 'luteolin triglucuronide degradation', 'C4 photosynthetic carbon assimilation cycle, NAD-ME type', 'betanidin degradation'], ['L-arginine degradation IV (arginine decarboxylase/agmatine deiminase pathway)', 'Agmatine extracellular biosynthesis', '&beta;-alanine biosynthesis III', 'NADH to cytochrome bd oxidase electron transfer I', 'adenine and adenosine salvage I', 'NAD biosynthesis from 2-amino-3-carboxymuconate semialdehyde', 'NADH to cytochrome bo oxidase electron transfer II', 'NAD de novo biosynthesis I (from aspartate)', 'L-lysine biosynthesis III', 'NADH to cytochrome bd oxidase electron transfer II', 'sulfate activation for sulfonation', 'folate transformations II (plants)', 'NADH to cytochrome bo oxidase electron transfer I', 'putrescine biosynthesis II'], ['Kdo transfer to lipid IVA I (E. coli)', 'aminopropylcadaverine biosynthesis', 'Kdo transfer to lipid IVA IV (P. putida)', 'tetrapyrrole biosynthesis I (from glutamate)', 'glycolate and glyoxylate degradation I', 'phenyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP', 'D-sorbitol degradation II', '6-hydroxymethyl-dihydropterin diphosphate biosynthesis I', '4-methylphenyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP', 'L-tryptophan biosynthesis', '6-hydroxymethyl-dihydropterin diphosphate biosynthesis III (Chlamydia)', 'allantoin degradation to ureidoglycolate II (ammonia producing)', 'dipyrromethane cofactor biosynthesis', 'TCA cycle III (animals)'], ['Bifidobacterium shunt', 'S-methyl-5-thio-&alpha;-D-ribose 1-phosphate degradation III', 'L-serine biosynthesis I', 'myo-inositol degradation I', 'protein Pupylation and dePupylation', 'adenosylcobinamide-GDP biosynthesis from cobyrinate a,c-diamide', 'Bifidobacterium shunt II', 'norspermidine biosynthesis', 'polyphosphate metabolism', 'isoniazid activation', 'glycerol degradation V', 'NAD phosphorylation and dephosphorylation', 'felinine and 3-methyl-3-sulfanylbutan-1-ol biosynthesis', 'D-xylose degradation I'], ['protein citrullination', 'trigonelline biosynthesis', 'glycerophosphodiester degradation', 'serotonin degradation', 'hydrogen to trimethylamine N-oxide electron transfer', 'mannitol degradation II', 'D-mannose degradation II', 'formate to trimethylamine N-oxide electron transfer', 'formate to dimethyl sulfoxide electron transfer', 'fatty acid biosynthesis initiation (mitochondria)', 'polymyxin A biosynthesis', 'molybdenum cofactor biosynthesis', 'putrescine degradation III'], ['flavin-N5-oxide biosynthesis', '(Kdo)2-lipid A biosynthesis II (P. putida)', 'methylphosphonate biosynthesis', 'methylphosphonate degradation III', 'chlorpyrifos degradation', 'sodorifen biosynthesis', '2-deoxy-D-ribose degradation II', '8-O-methylated benzoxazinoid glucoside biosynthesis', 'nepetalactone biosynthesis', '8-oxo-(d)GTP detoxification II', 'N-3-oxalyl-L-2,3-diaminopropanoate biosynthesis', 'pyruvoyl group formation from L-serine'], ['menaquinol-13 biosynthesis', 'menaquinol-12 biosynthesis', 'demethylmenaquinol-8 biosynthesis I', 'demethylmenaquinol-9 biosynthesis', 'demethylmenaquinol-6 biosynthesis I', 'menaquinol-11 biosynthesis', 'demethylmenaquinol-4 biosynthesis', 'menaquinol-10 biosynthesis', '&beta;-alanine biosynthesis II', 'menaquinol-7 biosynthesis', 'assimilatory sulfate reduction II', 'assimilatory sulfate reduction III'], ['methiin metabolism', 'notoamide C and D biosynthesis', 'stephacidin A biosynthesis', 'docosahexaenoate biosynthesis III (6-desaturase, mammals)', 'GDP-6-deoxy-D-manno-heptose biosynthesis', 'ricinoleate biosynthesis', 'meleagrin biosynthesis', 'neoxaline biosynthesis', 'juniperonate biosynthesis', 'pterocarpan phytoalexins modification (maackiain, medicarpin, pisatin, phaseollin)', 'chaetoglobosin A biosynthesis', 'roquefortine C biosynthesis'], ['5-N-acetylardeemin biosynthesis', 'ergothioneine biosynthesis II (fungi)', '(-)-dehydrodiconiferyl alcohol degradation', 'asperlicin E biosynthesis', '&alpha;-cyclopiazonate biosynthesis', 'heme d1 biosynthesis', '(-)-microperfuranone biosynthesis', 'prodigiosin biosynthesis', 'tenellin biosynthesis', '&alpha;-cyclopiazonate detoxification', 'diphthamide biosynthesis II (eukaryotes)', 'heme b biosynthesis III (from siroheme)'], ['creatinine degradation II', 'phytate degradation I', 'creatinine degradation III', 'arsenite oxidation I (respiratory)', 'wighteone and luteone biosynthesis', 'arsenate detoxification II (glutaredoxin)', 'kievitone biosynthesis', '1D-myo-inositol hexakisphosphate biosynthesis III (Spirodela polyrrhiza)', 'aloesone biosynthesis I', 'arsenate reduction (respiratory)', 'putrescine biosynthesis III', 'phytate degradation II'], ['phospholipid remodeling (phosphatidate, yeast)', 'narbomycin, pikromycin and novapikromycin biosynthesis', 'phospholipid remodeling (phosphatidylcholine, yeast)', 'bombykol biosynthesis', 'dTDP-&alpha;-D-mycaminose biosynthesis', 'tylosin biosynthesis', 'p-cymene degradation to p-cumate', 'methymycin, neomethymycin and novamethymycin biosynthesis', 'sterol:steryl ester interconversion (yeast)', 'monoacylglycerol metabolism (yeast)', 'FR-900098 and FR-33289 antibiotics biosynthesis'], ['trehalose biosynthesis III', 'toluene degradation to benzoate', '4-toluenesulfonate degradation I', 'diacylglycerol and triacylglycerol biosynthesis', 'thiosulfate oxidation I (to tetrathionate)', 'toluene degradation to 2-hydroxypentadienoate (via 4-methylcatechol)', 'L-threonine degradation III (to methylglyoxal)', 'toluene degradation to 4-methylphenol', 'toluene degradation to 2-hydroxypentadienoate I (via o-cresol)', 'trehalose biosynthesis I', 'toluene degradation to 2-hydroxypentadienoate (via toluene-cis-diol)'], ['rutin degradation (plants)', 'L-glucose degradation', 'CMP-legionaminate biosynthesis II', 'emetine biosynthesis', 'noscapine biosynthesis', 'quercetin glucoside biosynthesis (Allium)', '&beta; myrcene degradation', 'sesaminol glucoside biosynthesis', 'myricetin gentiobioside biosynthesis', 'quercetin glucoside degradation (Allium)', 'quercetin gentiotetraside biosynthesis'], ['4-hydroxyphenylacetate degradation', 'anthranilate degradation III (anaerobic)', 'phenylethylamine degradation I', '1,4-dichlorobenzene degradation', '4-hydroxymandelate degradation', 'orthanilate degradation', '1,8-cineole degradation', '1,2-dichloroethane degradation', 'L-methionine salvage from L-homocysteine', '4-toluenecarboxylate degradation', '2-oxobutanoate degradation II'], ['L-isoleucine degradation III (oxidative Stickland reaction)', 'platensimycin biosynthesis', 'L-leucine degradation V (oxidative Stickland reaction)', '10-methylstearate biosynthesis', '2-methyl-branched fatty acid &beta;-oxidation', 'nerol biosynthesis', 'geraniol biosynthesis (cytosol)', 'L-valine degradation III (oxidative Stickland reaction)', 'valproate &beta;-oxidation', 'L-alanine degradation VI (reductive Stickland reaction)', 'acrylate degradation II'], ['oleate biosynthesis III (cyanobacteria)', 'phycourobilin biosynthesis', 'phycoerythrobilin biosynthesis II', 'GDP-mycosamine biosynthesis', 'phycoviolobilin biosynthesis', 'docosahexaenoate biosynthesis II (bacteria)', 'nitrogen fixation II (flavodoxin)', 'arachidonate biosynthesis II (bacteria)', 'mercaptosuccinate degradation', 'lolitrem B biosynthesis', 'ferrichrome biosynthesis'], ['poly-hydroxy fatty acids biosynthesis', 'archaeosine biosynthesis I', 'L-rhamnose degradation II', 'ubiquinol-8 biosynthesis (early decarboxylation)', 'methylhalides biosynthesis (plants)', 'methylaspartate cycle', 'sangivamycin biosynthesis', 'starch degradation II', 'candicidin biosynthesis', 'L-rhamnose degradation III', 'toyocamycin biosynthesis'], ['CDP-diacylglycerol biosynthesis III', 'tRNA splicing I', 'isoprene biosynthesis II (engineered)', 'vancomycin resistance I', 'adenine and adenosine salvage II', 'nitric oxide biosynthesis I (plants)', 'mevalonate pathway I (eukaryotes and bacteria)', 'L-lysine biosynthesis II', 'citrate degradation', 'acyl carrier protein activation', 'mevalonate pathway IV (archaea)'], ['betacyanin biosynthesis (via dopamine)', 'oleoresin monoterpene volatiles biosynthesis', 'naphthalene degradation (aerobic)', 'benzene degradation', 'betaxanthin biosynthesis', '(3E)-4,8-dimethylnona-1,3,7-triene biosynthesis I', '1,3-dimethylbenzene degradation to 3-methylbenzoate', 'isopimaric acid biosynthesis', 'oleoresin sesquiterpene volatiles biosynthesis', '1,4-dimethylbenzene degradation to 4-methylbenzoate', 'aminopropanol phosphate biosynthesis I'], ['purine deoxyribonucleosides degradation I', 'Mucus glycans degradation', '2-amino-3-hydroxycyclopent-2-enone biosynthesis', "S-methyl-5'-thioadenosine degradation II", '&beta;-D-glucuronide and D-glucuronate degradation', 'adenine and adenosine salvage III', 'lipoate biosynthesis and incorporation I', '4-deoxy-L-threo-hex-4-enopyranuronate degradation', 'L-tyrosine biosynthesis I', 'L-homocysteine biosynthesis', 'purine deoxyribonucleosides degradation II'], ['heparan sulfate degradation', 'xyloglucan degradation II (exoglucanase)', '8-amino-7-oxononanoate biosynthesis III', 'pyruvate fermentation to isobutanol (engineered)', 'L-tryptophan degradation II (via pyruvate)', 'stachyose degradation', 'trehalose degradation V', 'trehalose degradation IV', 'UDP-N-acetyl-&alpha;-D-mannosaminouronate biosynthesis', 'L-valine biosynthesis', 'acetate and ATP formation from acetyl-CoA II'], ['gentiodelphin biosynthesis', 'calystegine biosynthesis', 'sulfur disproportionation II (aerobic)', 'thiosulfate oxidation II (via tetrathionate)', 'hyoscyamine and scopolamine biosynthesis', 'L-lysine degradation VII', 'N-methyl-&Delta;1-pyrrolinium cation biosynthesis', 'nicotine biosynthesis', 'bixin biosynthesis', 'L-lysine degradation VIII', 'ajmaline and sarpagine biosynthesis'], ['cyclobis-(1&rarr;6)-&alpha;-nigerosyl degradation', 'biosynthesis of Lewis epitopes (H. pylori)', 'i antigen and I antigen biosynthesis', 'gala-series glycosphingolipids biosynthesis', 'glycolipid desaturation', 'lacto-series glycosphingolipids biosynthesis', 'ABH and Lewis epitopes biosynthesis from type 1 precursor disaccharide', 'globo-series glycosphingolipids biosynthesis', 'ABH and Lewis epitopes biosynthesis from type 2 precursor disaccharide', 'ganglio-series glycosphingolipids biosynthesis'], ['cholesterol biosynthesis (algae, late side-chain reductase)', 'group B Salmonella O antigen biosynthesis', 'group E Salmonella O antigen biosynthesis', 'group D2 Salmonella O antigen biosynthesis', 'group A Salmonella O antigen biosynthesis', 'toluene degradation to benzoyl-CoA (anaerobic)', 'L-alanine degradation V (oxidative Stickland reaction)', 'group D1 Salmonella O antigen biosynthesis', 'L-glutamate degradation XI (reductive Stickland reaction)', 'group C2 Salmonella O antigen biosynthesis'], ['4-hydroxyindole-3-carbonyl nitrile biosynthesis', 'epiberberine biosynthesis', 'salmochelin degradation', 'cyanuric acid degradation I', 'sterol biosynthesis (methylotrophs)', 'limonene degradation IV (anaerobic)', 'parkeol biosynthesis', 'cycloartenol biosynthesis', 'salmochelin biosynthesis', 'coptisine biosynthesis'], ['furcatin degradation', 'ethene biosynthesis IV (engineered)', 'tea aroma glycosidic precursor bioactivation', '4-hydroxy-2-nonenal detoxification', 'esterified suberin biosynthesis', 'ceramide and sphingolipid recycling and degradation (yeast)', 'chitin deacetylation', 'nicotine degradation III (VPP pathway)', 'erythromycin A biosynthesis', 'megalomicin A biosynthesis'], ['D-erythronate degradation I', 'octaprenyl diphosphate biosynthesis', 'thiamine diphosphate biosynthesis II (Bacillus)', 'L-tryptophan degradation IV (via indole-3-lactate)', 'phosphatidylserine and phosphatidylethanolamine biosynthesis I', 'oleate biosynthesis IV (anaerobic)', 'thiazole component of thiamine diphosphate biosynthesis I', 'thiamine diphosphate biosynthesis I (E. coli)', 'adenosine nucleotides degradation III', 'nonaprenyl diphosphate biosynthesis I'], ['molybdopterin biosynthesis', 'spermidine biosynthesis III', 'gellan degradation', '6-gingerol biosynthesis', 'santalene biosynthesis II', 'justicidin B biosynthesis', 'tRNA methylation (yeast)', 'phosphatidylcholine biosynthesis V', 'phosphatidylcholine biosynthesis VI', 'pyrrolnitrin biosynthesis'], ["2,2'-bis-(4-hydroxy-3-methybut-2-enyl)-&beta;,&beta;-carotene monoglucoside biosynthesis", '5-oxo-L-proline metabolism', 'flexixanthin biosynthesis', '4-oxopentanoate degradation', 'sarcinaxanthin diglucoside biosynthesis', 'chlorobactene biosynthesis', 'bacterioruberin biosynthesis', 'lauryl-hydroxychlorobactene glucoside biosynthesis', 'lycopadiene biosynthesis', 'isorenieratene biosynthesis II (Chlorobiaceae)'], ['phospholipid desaturation', 'autoinducer CAI-1 biosynthesis', 'nystatin biosynthesis', '2,4-dinitroanisole degradation', '2,4,6-trinitrophenol and 2,4-dinitrophenol degradation', 'astaxanthin dirhamnoside biosynthesis', 'yatein biosynthesis II', 'naphthalene degradation (anaerobic)', 'rhizobactin 1021 biosynthesis', 'bacilysin biosynthesis'], ['menaquinol oxidase (cytochrom aa3-600)', 'Inulin degradation(11xFru,1xGlc) (extracellular)', 'iso-bile acids biosynthesis (NADH or NADPH dependent)', 'L-Tyrosine degradation to 4-hydroxyphenylacetate via tyramine', 'Ljungdahl-Wood pathway (gapseq)', 'H4SPT-SYN', 'thiazole biosynthesis I (facultative anaerobic bacteria) with tautomerase', 'Bile acid 7alpha-dehydroxylation', 'F420 Biosynthesis until 3 glutamine residues', 'Extracellular galactan(2n) degradation'], ['viridicatumtoxin biosynthesis', 'glycogen degradation III (via anhydrofructose)', 'dechlorogriseofulvin biosynthesis', 'dTDP-&beta;-L-digitoxose biosynthesis', 'griseofulvin biosynthesis', 'protein N-glycosylation (Haloferax volcanii)', 'protein N-glycosylation (Methanococcus voltae)', 'Spodoptera littoralis pheromone biosynthesis', '(8E,10E)-dodeca-8,10-dienol biosynthesis', 'tryptoquialanine biosynthesis'], ['cell-surface glycoconjugate-linked phosphocholine biosynthesis', 'protein SAMPylation and SAMP-mediated thiolation', 'tRNA-uridine 2-thiolation (yeast mitochondria)', 'procollagen hydroxylation and glycosylation', 'tRNA-uridine 2-thiolation (cytoplasmic)', 'tRNA-uridine 2-thiolation (mammalian mitochondria)', 'lipoprotein posttranslational modification', 'anhydromuropeptides recycling II', 'phosphatidylinositol mannoside biosynthesis', 'tRNA-uridine 2-thiolation and selenation (bacteria)'], ['2-aminoethylphosphonate degradation III', 'luteolin triglucuronide biosynthesis', '(4S)-carvone biosynthesis', 'acylated cyanidin galactoside biosynthesis', 'galloylated catechin biosynthesis', 'allopregnanolone biosynthesis', 'anthocyanidin modification (Arabidopsis)', 'sulfoquinovose degradation I', 'cyanidin dimalonylglucoside biosynthesis', 'sulfite oxidation V (SoeABC)'], ['dTDP-&beta;-L-evernitrose biosynthesis', 'dTDP-&beta;-L-4-epi-vancosamine biosynthesis', 'vitamin E biosynthesis (tocotrienols)', 'indole degradation to anthranil and anthranilate', 'mucin core 1 and core 2 O-glycosylation', 'aromatic biogenic amine degradation (bacteria)', 'mucin core 3 and core 4 O-glycosylation', 'drosopterin and aurodrosopterin biosynthesis', 'arsenite oxidation II (respiratory)', 'thiocyanate degradation II'], ['roseoflavin biosynthesis', 'nitric oxide biosynthesis III (bacteria)', 'coenzyme B/coenzyme M regeneration III (coenzyme F420-dependent)', 'coenzyme B/coenzyme M regeneration II (ferredoxin-dependent)', 'cis-alkene biosynthesis', 'jasmonoyl-L-isoleucine inactivation', 'D-altritol and galactitol degradation', 'N-hydroxy-L-pipecolate biosynthesis', 'coenzyme B/coenzyme M regeneration IV (H2-dependent)', 'coenzyme B/coenzyme M regeneration V (formate-dependent)'], ['(3R)-linalool biosynthesis', '4-methylphenol degradation to protocatechuate', 'viridicatin biosynthesis', '2,4-xylenol degradation to protocatechuate', 'sch210971 and sch210972 biosynthesis', '4-hydroxy-4-methyl-L-glutamate biosynthesis', 'dapdiamides biosynthesis', '2,5-xylenol and 3,5-xylenol degradation', 'lyngbyatoxin biosynthesis', "4'-methoxyviridicatin biosynthesis"], ['atromentin biosynthesis', 'CMP-N-acetyl-7-O-acetylneuraminate biosynthesis', '&beta;-D-galactosaminyl-(1&rarr;3)-N-acetyl-&alpha;-D-galactosamine biosynthesis', '(R)-canadine biosynthesis', '3-(4-sulfophenyl)butanoate degradation', 'fumitremorgin A biosynthesis', 'terrequinone A biosynthesis', 'fumitremorgin C biosynthesis', 'brassicicene C biosynthesis', 'mevalonate pathway III (Thermoplasma)'], ['hydrogen to dimethyl sulfoxide electron transfer', 'carbon tetrachloride degradation II', 'L-isoleucine biosynthesis III', 'CDP-D-arabitol biosynthesis', 'L-arginine degradation XIII (reductive Stickland reaction)', 'acetylene degradation (anaerobic)', 'reductive acetyl coenzyme A pathway I (homoacetogenic bacteria)', 'L-asparagine degradation III (mammalian)', 'methanogenesis from acetate', '&beta;-1,4-D-mannosyl-N-acetyl-D-glucosamine degradation'], ['heme b biosynthesis IV (Gram-positive bacteria)', 'benzimidazolyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP', '2-carboxy-1,4-naphthoquinol biosynthesis', 'NADH:menaquinone6 oxidoreductase', 'terminal olefins biosynthesis I', 'lactose and galactose degradation I', 'cinnamoyl-CoA biosynthesis', 'L-Fucose degradation (non-phosphorylating)', 'poly(glycerol phosphate) wall teichoic acid biosynthesis', 'phytol degradation'], ['palmitoleate biosynthesis II (plants and bacteria)', 'carbon tetrachloride degradation I', 'dimorphecolate biosynthesis', '&alpha;-eleostearate biosynthesis', 'A series fagopyritols biosynthesis', 'calendate biosynthesis', '&alpha;-amyrin biosynthesis', 'punicate biosynthesis', 'B series fagopyritols biosynthesis', 'petroselinate biosynthesis'], ['(R)- and (S)-3-hydroxybutanoate biosynthesis (engineered)', 'ubiquinol-6 biosynthesis from 4-aminobenzoate (yeast)', 'wogonin metabolism', 'baicalein metabolism', 'pyrimidine deoxyribonucleotides dephosphorylation', 'purine deoxyribonucleosides salvage', 'baicalein degradation (hydrogen peroxide detoxification)', 'nicotinate degradation I', '3-methylquinoline degradation', 'gibberellin biosynthesis V'], ['salicortin biosynthesis', 'hydrogen production IV', 'pinitol biosynthesis II', 'salicylate glucosides biosynthesis IV', 'o-diquinones biosynthesis', 'methane oxidation to methanol II', 'pinitol biosynthesis I', "S-methyl-5'-thioadenosine degradation I", 'nitrate reduction VII (denitrification)', 'D-xylose degradation III'], ['naphthomycin biosynthesis', 'saliniketal A biosynthesis', 'bryostatin biosynthesis', 'ophthalmate biosynthesis', 'ultra-long-chain fatty acid biosynthesis', 'mitomycin biosynthesis', 'cyclohexane-1-carboxyl-CoA biosynthesis', 'ansatrienin biosynthesis', 'acylceramide biosynthesis', 'cylindrospermopsin biosynthesis'], ['pinosylvin metabolism', 'D-sorbitol biosynthesis I', 'luteolin biosynthesis', 'rosmarinic acid biosynthesis I', 'theobromine biosynthesis II (via xanthine)', 'L-valine degradation II', 'pinobanksin biosynthesis', 'gibberellin biosynthesis IV (Gibberella fujikuroi)', 'rosmarinic acid biosynthesis II'], ['daidzin and daidzein degradation', '(-)-camphor biosynthesis', 'nicotine degradation II (pyrrolidine pathway)', 'furfural degradation', '5-hydroxymethylfurfural degradation', '1,5-anhydrofructose degradation', 'L-pyrrolysine biosynthesis', 'theophylline degradation', '(+)-camphor biosynthesis'], ['pyruvate fermentation to opines', 'daunorubicin biosynthesis', 'papaverine biosynthesis', 'aclacinomycin biosynthesis', 'jasmonic acid biosynthesis', 'thiamine phosphate formation from pyrithiamine and oxythiamine (yeast)', 'sucrose biosynthesis III', 'phosphatidylglycerol degradation', 'doxorubicin biosynthesis'], ['elloramycin biosynthesis', 'tetracenomycin C biosynthesis', 'oryzalide A biosynthesis', 'phytocassanes biosynthesis, shared reactions', '(+)-secoisolariciresinol diglucoside biosynthesis', 'oryzalexin A, B, and C biosynthesis', 'podophyllotoxin glucosides metabolism', 'cyclooctatin biosynthesis', 'patulin biosynthesis'], ['L-ascorbate biosynthesis II (plants, L-gulose pathway)', 'L-proline biosynthesis II (from arginine)', 'phosphatidylethanolamine biosynthesis II', 'extended VTC2 cycle', '&beta;-pyrazole-1-ylalanine biosynthesis', 'abscisic acid biosynthesis shunt', 'VTC2 cycle', 'phosphatidylcholine biosynthesis III', 'phosphatidylcholine biosynthesis IV'], ['L-serine biosynthesis II', 'L-cysteine biosynthesis IX (Trichomonas vaginalis)', 'staphylopine biosynthesis', 'trans-caffeate degradation (aerobic)', 'mupirocin biosynthesis', 'plant arabinogalactan type II degradation', 'L-cysteine biosynthesis VIII (Thermococcus kodakarensis)', '4-coumarate degradation (aerobic)', 'staphyloferrin B biosynthesis'], ['galactosylcyclitol biosynthesis', 'nitroethane degradation', 'stachyose biosynthesis', 'ajugose biosynthesis II (galactinol-independent)', 'ajugose biosynthesis I (galactinol-dependent)', 'arachidonate biosynthesis I (6-desaturase, lower eukaryotes)', 'kaempferol triglucoside biosynthesis', 'esculetin biosynthesis', "chalcone 2'-O-glucoside biosynthesis"], ['2&alpha;,7&beta;-dihydroxylation of taxusin', 'fumigaclavine biosynthesis', 'steviol biosynthesis', 'steviol glucoside biosynthesis (rebaudioside A biosynthesis)', 'esculetin modification', 'oleanolate biosynthesis', 'betulinate biosynthesis', 'glycyrrhetinate biosynthesis', 'ursolate biosynthesis'], ['dTDP-&alpha;-D-olivose, dTDP-&alpha;-D-oliose and dTDP-&alpha;-D-mycarose biosynthesis', 'oleandomycin biosynthesis', 'dTDP-&beta;-L-olivose biosynthesis', 'oleandomycin activation/inactivation', 'plastoquinol-9 biosynthesis II', 'trimethylamine degradation', 'umbelliferone biosynthesis', 'dTDP-&beta;-L-mycarose biosynthesis', 'threo-tetrahydrobiopterin biosynthesis'], ['pyrimidine deoxyribonucleosides degradation', 'quercetin diglycoside biosynthesis (pollen-specific)', 'linalool biosynthesis I', 'pinocembrin C-glucosylation', "pyridoxal 5'-phosphate salvage II (plants)", 'eriodictyol C-glucosylation', 'pyrimidine deoxyribonucleosides salvage', 'kaempferol diglycoside biosynthesis (pollen-specific)', 'UTP and CTP dephosphorylation I'], ['paspaline biosynthesis', 'phosphatidylserine biosynthesis II', 'paxilline and diprenylpaxilline biosynthesis', 'phosphatidylserine biosynthesis I', '3&beta;-hydroxysesquiterpene lactone biosynthesis', 'gossypetin metabolism', 'phenylpropanoids methylation (ice plant)', 'chelerythrine biosynthesis', 'linuron degradation'], ['2-heptyl-3-hydroxy-4(1H)-quinolone biosynthesis', '4-hydroxy-2(1H)-quinolone biosynthesis', 'dopamine degradation', 'fusicoccin A biosynthesis', 'anandamide degradation', 'pyocyanin biosynthesis', 'pterostilbene biosynthesis', 'di-myo-inositol phosphate biosynthesis', 'acetan biosynthesis'], ['pentaketide chromone biosynthesis', 'm-xylene degradation (anaerobic)', 'polyhydroxybutanoate biosynthesis', 'vitamin E biosynthesis (tocopherols)', 'benzoyl-CoA degradation I (aerobic)', 'fluorene degradation II', 'taurine degradation II', 'phenylacetate degradation II (anaerobic)', 'L-homomethionine biosynthesis'], ['zwittermicin A biosynthesis', 'citreoisocoumarin and bikisocoumarin biosynthesis', 'guadinomine B biosynthesis', 'geranyl &beta;-primeveroside biosynthesis', 'holomycin biosynthesis', 'aurofusarin biosynthesis', '10,13-epoxy-11-methyl-octadecadienoate biosynthesis', 'bikaverin biosynthesis', '8-O-methylfusarubin biosynthesis'], ['isopenicillin N biosynthesis', 'penicillin K biosynthesis', 'nucleoside and nucleotide degradation (archaea)', '3,8-divinyl-chlorophyllide a biosynthesis II (anaerobic)', 'acetone degradation II (to acetoacetate)', 'sorbitol biosynthesis II', 'cephalosporin C biosynthesis', 'propene degradation', 'deacetylcephalosporin C biosynthesis'], ['ammonia oxidation II (anaerobic)', 'benzoyl-CoA degradation III (anaerobic)', 'citrate lyase activation', 'orcinol degradation', 'aldoxime degradation', 'galena oxidation', 'L-sorbose degradation', 'glycolysis V (Pyrococcus)', 'resorcinol degradation'], ['L-lysine degradation V', 'sulfite oxidation III', 'sulfite oxidation II', 'L-lysine degradation IV', 'shisonin biosynthesis', 'sulfite oxidation I', 'thiosulfate disproportionation I (thiol-dependent)', 'sulfide oxidation II (flavocytochrome c)', 'sulfide oxidation III (to sulfite)'], ['androgen biosynthesis', 'salicylate degradation III', 'mineralocorticoid biosynthesis', 'pregnenolone biosynthesis', 'sulfolactate degradation II', 'estradiol biosynthesis I (via estrone)', 'leukotriene biosynthesis', 'C20 prostanoid biosynthesis', 'glucocorticoid biosynthesis'], ['L-leucine degradation II', 'chlorophyll cycle', 'very long chain fatty acid biosynthesis I', 'L-leucine degradation III', 'mevalonate degradation', 'L-isoleucine degradation II', 'L-tryptophan degradation VIII (to tryptophol)', 'gibberellin biosynthesis I (non C-3, non C-13 hydroxylation)', 'glycogen biosynthesis II (from UDP-D-Glucose)'], ['chlorzoxazone degradation', 'poly(3-O-&beta;-D-glucopyranosyl-N-acetylgalactosamine 1-phosphate) wall teichoic acid biosynthesis', 'Amaryllidacea alkaloids biosynthesis', 'type IV lipoteichoic acid biosynthesis (S. pneumoniae)', 'chitin degradation III (Serratia)', 'juglone degradation', 'prunasin and amygdalin biosynthesis', 'teichuronic acid biosynthesis (B. subtilis 168)', 'tunicamycin biosynthesis'], ['pectin degradation I', 'pelargonidin diglucoside biosynthesis (acyl-glucose dependent)', 'cyanidin diglucoside biosynthesis (acyl-glucose dependent)', 'apigeninidin 5-O-glucoside biosynthesis', '[2Fe-2S] iron-sulfur cluster biosynthesis', 'luteolinidin 5-O-glucoside biosynthesis', 'pectin degradation II', 'ergothioneine biosynthesis I (bacteria)', 'pentacyclic triterpene biosynthesis'], ['butane degradation', '2-methylpropene degradation', 'D-threitol degradation', 'L-threitol degradation', 'reductive acetyl coenzyme A pathway II (autotrophic methanogens)', 'plasmalogen degradation', 'plasmalogen biosynthesis', 'methyl tert-butyl ether degradation', '&omega;-sulfo-II-dihydromenaquinone-9 biosynthesis'], ['3,8-divinyl-chlorophyllide a biosynthesis III (aerobic, light independent)', 'L-phenylalanine degradation V', 'ergosterol biosynthesis II', 'polymethylated quercetin biosynthesis', 'grixazone biosynthesis', 'polymethylated myricetin biosynthesis (tomato)', 'pinolenate and coniferonate biosynthesis', 'eupatolitin 3-O-glucoside biosynthesis', '7-dehydroporiferasterol biosynthesis'], ["4,4'-diapolycopenedioate biosynthesis", '1,3-&beta;-D-glucan biosynthesis', 'hydrogen production VI', 'detoxification of reactive carbonyls in chloroplasts', 'salicin biosynthesis', 'cellulose and hemicellulose degradation (cellulolosome)', 'rhamnogalacturonan type I degradation I', 'chlorogenic acid degradation', 'hydrogen production V'], ['docosahexaenoate biosynthesis I (lower eukaryotes)', 'cichoriin interconversion', '4-coumarate degradation (anaerobic)', 'cyanophycin metabolism', 'N-acetylglutaminylglutamine amide biosynthesis', 'daphnin interconversion', 'daphnetin modification', 'icosapentaenoate biosynthesis II (6-desaturase, mammals)', 'icosapentaenoate biosynthesis IV (bacteria)'], ['cob(II)yrinate a,c-diamide biosynthesis II (late cobalt incorporation)', 'urate conversion to allantoin II', 'mRNA capping I', 'aminopropanol phosphate biosynthesis II', 'lipoate biosynthesis and incorporation IV (yeast)', 'naringenin biosynthesis (engineered)', 'butanol and isobutanol biosynthesis (engineered)', 'coumarins biosynthesis (engineered)', 'cob(II)yrinate a,c-diamide biosynthesis I (early cobalt insertion)'], ['anthocyanidin sophoroside metabolism', 'vindoline, vindorosine and vinblastine biosynthesis', 'ternatin C5 biosynthesis', 'canthaxanthin biosynthesis', 'secologanin and strictosidine biosynthesis', 'astaxanthin biosynthesis (bacteria, fungi, algae)', 'sanguinarine and macarpine biosynthesis', 'thiosulfate oxidation III (multienzyme complex)', 'siroheme amide biosynthesis'], ['L-lysine degradation II (L-pipecolate pathway)', 'glycolate and glyoxylate degradation III', 'hydrogen sulfide biosynthesis II (mammalian)', 'rhamnolipid biosynthesis', 'coenzyme M biosynthesis II', 'fluoroacetate and fluorothreonine biosynthesis', 'labdane-type diterpenes biosynthesis', '(R)-cysteate degradation', 'juvenile hormone III biosynthesis II'], ['sulfate reduction I (assimilatory)', 'viscosin biosynthesis', 'indole-3-acetate biosynthesis VI (bacteria)', 'L-tyrosine degradation I', 'L-valine degradation I', '2-fucosyllactose degradation', 'L-tryptophan degradation I (via anthranilate)', 'massetolide A biosynthesis', 'Lacto-N-tetraose degradation'], ['nocardicin A biosynthesis', 'terephthalate degradation', 'polyethylene terephthalate degradation', 'Arg/N-end rule pathway (eukaryotic)', 'erythritol degradation I', 'dimethyl sulfide biosynthesis from methionine', 'pentose phosphate pathway (oxidative branch) II', 'erythritol degradation II', 'protein S-nitrosylation and denitrosylation'], ['NAD biosynthesis III (from nicotinamide)', 'nitrogen fixation I (ferredoxin)', 'Entner-Doudoroff pathway II (non-phosphorylative)', 'methylgallate degradation', 'octopine degradation', 'nopaline degradation', 'ectoine biosynthesis', 'L-ornithine degradation I (L-proline biosynthesis)', 'NAD salvage pathway III (to nicotinamide riboside)'], ['betaxanthin biosynthesis (via dopaxanthin)', 'traumatin and (Z)-3-hexen-1-yl acetate biosynthesis', 'amaranthin biosynthesis', 'abietic acid biosynthesis', 'levopimaric acid biosynthesis', '9-lipoxygenase and 9-allene oxide synthase pathway', 'divinyl ether biosynthesis I', '9-lipoxygenase and 9-hydroperoxide lyase pathway', 'divinyl ether biosynthesis II'], ['CMP phosphorylation', 'triclosan resistance', '(1,4)-&beta;-D-xylan degradation', 'ppGpp metabolism', 'L-ornithine biosynthesis II', 'guanosine ribonucleotides de novo biosynthesis', 'TCA cycle I (prokaryotic)', 'UTP and CTP de novo biosynthesis', 'TCA cycle VII (acetate-producers)'], ['2-aminoethylphosphonate biosynthesis', 'hexaprenyl diphosphate biosynthesis', 'hydrogen production VIII', 'D-sorbitol degradation I', 'hydrogen production III', 'glycerol-3-phosphate shuttle', 'nitrate reduction IV (dissimilatory)', 'GDP-6-deoxy-D-altro-heptose biosynthesis', 'Oxidase test'], ['salinosporamide A biosynthesis', 'salicylate glucosides biosynthesis III', 'heptadecane biosynthesis', 'nicotine degradation V', 'bupropion degradation', 'nicotine degradation IV', 'catecholamine biosynthesis', 'adenine and adenosine salvage VI', 'salicylate glucosides biosynthesis II'], ['2,3-cis-flavanols biosynthesis', 'isovitexin glycosides biosynthesis', 'cardenolide glucosides biosynthesis', 'serotonin and melatonin biosynthesis', '2,3-trans-flavanols biosynthesis', 'glucosinolate biosynthesis from tryptophan', 'capsiconiate biosynthesis', 'digitoxigenin biosynthesis', 'nitrilotriacetate degradation'], ['CDP-diacylglycerol biosynthesis II', 'putrescine degradation II', 'NADH to fumarate electron transfer', 'N-acetylneuraminate and N-acetylmannosamine degradation I', 'pyrimidine ribonucleosides degradation', 'nitrate reduction III (dissimilatory)', 'protocatechuate degradation II (ortho-cleavage pathway)', 'chitobiose degradation', 'L-proline degradation I'], ['sulfur disproportionation I (anaerobic)', 'coenzyme B biosynthesis', 'nitroglycerin degradation', 'protocatechuate degradation I (meta-cleavage pathway)', 'octane oxidation', 'nicotine degradation I (pyridine pathway)', 'catechol degradation to 2-hydroxypentadienoate I', 'purine nucleobases degradation I (anaerobic)', 'coenzyme M biosynthesis I'], ['autoinducer AI-2 degradation', 'D-lactate to cytochrome bo oxidase electron transfer', 'muropeptide degradation', '5-(methoxycarbonylmethoxy)uridine biosynthesis', 'nitrate reduction VIIIb (dissimilatory)', 'methylphosphonate degradation I', 'proline to cytochrome bo oxidase electron transfer', 'cardiolipin biosynthesis III'], ['bacteriochlorophyll e biosynthesis', '3-hydroxy-4-methyl-anthranilate biosynthesis II', 'bacteriochlorophyll c biosynthesis', 'phosalacine biosynthesis', 'NAD salvage pathway II (PNC IV cycle)', 'L-leucine degradation IV (reductive Stickland reaction)', 'chlorophyll a biosynthesis III', 'bacteriochlorophyll b biosynthesis'], ['phosphate acquisition', 'guanosine deoxyribonucleotides de novo biosynthesis II', 'menaquinol-6 biosynthesis', 'menaquinol-4 biosynthesis I', 'ethene biosynthesis III (microbes)', 'menaquinol-9 biosynthesis', 'adenosine deoxyribonucleotides de novo biosynthesis II', 'queuosine biosynthesis I (de novo)'], ['tetracycline resistance', 'Ac/N-end rule pathway', 'N-end rule pathway II (prokaryotic)', 'tRNA splicing II', 'glyphosate degradation I', 'glyphosate degradation III', '(aminomethyl)phosphonate degradation', 'glyphosate degradation II'], ['diethylphosphate degradation', 'vitamin B6 degradation', 'paraoxon degradation', '4-nitrophenol degradation I', 'methanol oxidation to formaldehyde IV', 'reductive monocarboxylic acid cycle', '4-nitrophenol degradation II', 'L-arabinose degradation III'], ['formaldehyde oxidation I', 'glucosinolate biosynthesis from hexahomomethionine', 'indole glucosinolate activation (herbivore attack)', 'quinate degradation I', 'indole glucosinolate activation (intact plant cell)', 'ribitol degradation', 'TCA cycle VI (Helicobacter)', 'NAD salvage pathway I (PNC VI cycle)'], ['starch degradation V', '5-aminoimidazole ribonucleotide biosynthesis II', 'glycogen biosynthesis I (from ADP-D-Glucose)', 'L-proline biosynthesis I (from L-glutamate)', 'tetrahydrofolate salvage from 5,10-methenyltetrahydrofolate', '3-dehydroquinate biosynthesis I', '5-aminoimidazole ribonucleotide biosynthesis I', 'Entner-Doudoroff pathway III (semi-phosphorylative)'], ['methanogenesis from tetramethylammonium', 'methanogenesis from dimethylsulfide', 'methanogenesis from methylthiopropanoate', 'methanofuran biosynthesis', 'methanogenesis from trimethylamine', 'methanogenesis from methanethiol', 'salvianin biosynthesis', 'glucosinolate activation'], ['parathion degradation', 'phenylmercury acetate degradation', 'dibenzo-p-dioxin degradation', 'proline betaine degradation I', 'nylon-6 oligomer degradation', 'thiocyanate degradation I', 'glycine betaine biosynthesis IV (from glycine)', '(+)-camphor degradation'], ['ricinine degradation', 'pentalenolactone biosynthesis', 'sophoraflavanone G biosynthesis', 'pyrethrin I biosynthesis', 'neopentalenoketolactone and pentalenate biosynthesis', '6-gingerol analog biosynthesis (engineered)', 'methylbutenol biosynthesis', 'vernolate biosynthesis III'], ['N-cyclopropylmelamine degradation', 'lactucaxanthin biosynthesis', 'capsanthin and capsorubin biosynthesis', 'coumarin biosynthesis (via 2-coumarate)', 'factor 430 biosynthesis', 'artemisinin and arteannuin B biosynthesis', 'factor 420 biosynthesis II (mycobacteria)', 'lactate biosynthesis (archaea)'], ['acetylaszonalenin biosynthesis', 'aflatrem biosynthesis', 'gliotoxin inactivation', 'fumiquinazoline D biosynthesis', 'gliotoxin biosynthesis', 'lovastatin biosynthesis', 'mannojirimycin biosynthesis', '1,2-propanediol biosynthesis from lactate (engineered)'], ['4-aminophenol degradation', 'taxiphyllin bioactivation', 'neolinustatin bioactivation', 'taxiphyllin biosynthesis', 'triethylamine degradation', '2-methylisoborneol biosynthesis', 'geodin biosynthesis', 'linustatin bioactivation'], ["hispidol and hispidol 4'-O-&beta;-D-glucoside biosynthesis", 'melatonin degradation II', 'mycolyl-arabinogalactan-peptidoglycan complex biosynthesis', 'mono-trans, poly-cis decaprenyl phosphate biosynthesis', 'meso-butanediol biosynthesis II', 'melatonin degradation III', 'melatonin degradation I', 'Rapoport-Luebering glycolytic shunt'], ['2-methyladeninyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP', 'rhabduscin biosynthesis', '12-epi-hapalindole biosynthesis', 'adeninyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP', '3-[(E)-2-isocyanoethenyl]-1H-indole biosynthesis', '12-epi-fischerindole biosynthesis', 'hapalindole H biosynthesis', '5-methoxy-6-methylbenzimidazolyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP'], ['&gamma;-resorcylate degradation I', 'propane degradation I', 'indolmycin biosynthesis', 'propane degradation II', 'butachlor degradation', 'isoprene degradation', '&gamma;-resorcylate degradation II', 'ethene and chloroethene degradation'], ['thiosulfate oxidation IV (multienzyme complex)', 'cis-geranyl-CoA degradation', 'resveratrol degradation', '&delta;-guaiene biosynthesis', '(E,E)-4,8,12-trimethyltrideca-1,3,7,11-tetraene biosynthesis', 'sulfur oxidation IV (intracellular sulfur)', 'citronellol degradation', 'caffeoylglucarate biosynthesis'], ['ethene biosynthesis II (microbes)', 'all-trans-farnesol biosynthesis', 'retinol biosynthesis', 'chitin degradation I (archaea)', 'rutin degradation', 'pyruvate fermentation to hexanol (engineered)', 'the visual cycle I (vertebrates)', 'senecionine N-oxide biosynthesis'], ['acinetobactin biosynthesis', 'pinoresinol degradation', 'oxalate degradation VI', 'pseudomonine biosynthesis', 'baumannoferrin biosynthesis', '&alpha;-dystroglycan glycosylation', 'anguibactin biosynthesis', 'vanchrobactin biosynthesis'], ['4-amino-3-hydroxybenzoate degradation', 'GDP-L-fucose biosynthesis II (from L-fucose)', '2-propylphenol degradation', 'methyl ketone biosynthesis (engineered)', "2,2'-dihydroxybiphenyl degradation", '2-hydroxybiphenyl degradation', '4-hydroxyacetophenone degradation', 'brassinosteroid biosynthesis I'], ['flavonol acylglucoside biosynthesis I - kaempferol derivatives', 'L-ascorbate biosynthesis VIII (engineered pathway)', 'kaempferide triglycoside biosynthesis', 'polymethylated kaempferol biosynthesis', 'flavonol acylglucoside biosynthesis II - isorhamnetin derivatives', 'chlorophyll a degradation III', 'phytochromobilin biosynthesis', 'flavonol acylglucoside biosynthesis III - quercetin derivatives'], ['lotaustralin biosynthesis', '&alpha;-linolenate biosynthesis I (plants and red algae)', 'thalianol and derivatives biosynthesis', 'oleate biosynthesis II (animals and fungi)', 'canavanine biosynthesis', 'sorgoleone biosynthesis', '&gamma;-linolenate biosynthesis I (plants)', 'linoleate biosynthesis I (plants)'], ['carbaryl degradation', 'factor 420 biosynthesis I (archaea)', '3PG-factor 420 biosynthesis', 'colibactin biosynthesis', 'branched-chain polyamines biosynthesis', 'patellamide A and C biosynthesis', 'ochratoxin A biosynthesis', 'long-chain polyamine biosynthesis'], ['dTDP-L-daunosamine biosynthesis', 'tetracycline and oxytetracycline biosynthesis', 'poly(ribitol phosphate) wall teichoic acid biosynthesis II (S. aureus)', '6-methylpretetramide biosynthesis', 'poly(ribitol phosphate) wall teichoic acid biosynthesis I (B. subtilis)', 'type I lipoteichoic acid biosynthesis (S. aureus)', 'thiosulfate disproportionation III (quinone)', 'chlorotetracycline biosynthesis'], ['carbon disulfide oxidation III (metazoa)', 'polybrominated biphenyls and diphenyl ethers biosynthesis', 'pyoluteorin biosynthesis', 'sulfide oxidation IV (mitochondria)', 'rubber degradation II', 'nickel cofactor biosynthesis', 'polybrominated phenols biosynthesis', 'brominated pyrroles biosynthesis'], ['sulfite oxidation IV (sulfite oxidase)', 'kaempferol glycoside biosynthesis (Arabidopsis)', 'coumarin metabolism (to melilotic acid)', 'L-lysine degradation IX', 'quercetin glycoside biosynthesis (Arabidopsis)', 'taurine biosynthesis I', 'carbon disulfide oxidation II (aerobic)', 'L-cysteine degradation III'], ['homospermidine biosynthesis II', 'L-ascorbate biosynthesis VII (plants, D-galacturonate pathway)', 'cytochrome c biogenesis (system II type)', 'androsrtendione degradation II (anaerobic)', 'cholesterol degradation to androstenedione III (anaerobic)', 'L-ascorbate biosynthesis VI (plants, myo-inositol pathway)', 'cytochrome c biogenesis (system I type)', '9-decynoate biosynthesis'], ['flavonoid di-C-glucosylation', 'glycogen biosynthesis III (from &alpha;-maltose 1-phosphate)', 'glucosylglycerol biosynthesis', 'ethionamide activation', 'tRNA-uridine 2-thiolation (thermophilic bacteria)', "4,4'-disulfanediyldibutanoate degradation", 'protein NEDDylation', 'glucosinolate biosynthesis from tyrosine'], ['UDP-N-acetyl-&alpha;-D-fucosamine biosynthesis', '9-cis, 11-trans-octadecadienoyl-CoA degradation (isomerase-dependent, yeast)', '10-trans-heptadecenoyl-CoA degradation (MFE-dependent, yeast)', 'salvigenin biosynthesis', '10-trans-heptadecenoyl-CoA degradation (reductase-dependent, yeast)', '10-cis-heptadecenoyl-CoA degradation (yeast)', 'UDP-N-acetyl-&alpha;-D-quinovosamine biosynthesis', 'UDP-N-acetyl-&beta;-L-quinovosamine biosynthesis'], ['oxalate degradation III', 'D-galactose degradation IV', 'oxalate degradation V', 'plaunotol biosynthesis', 'Fe(II) oxidation', 'cinnamate and 3-hydroxycinnamate degradation to 2-hydroxypentadienoate', 'thyronamine and iodothyronamine metabolism', 'mannosylglucosylglycerate biosynthesis II'], ['diacylsucrose biosynthesis (Solanum)', 'cembratrienediol biosynthesis', 'indole-3-acetate activation II', '&alpha;-tomatine degradation', 'aurone biosynthesis', 'monoacylsucrose biosynthesis (Solanum)', 'indole-3-acetate inactivation I', 'decaprenoxanthin diglucoside biosynthesis'], ['L-tryptophan degradation VI (via tryptamine)', 'UDP-&beta;-L-rhamnose biosynthesis', 'choline biosynthesis I', 'cutin biosynthesis', 'sinapate ester biosynthesis', 'indole-3-acetate biosynthesis III (bacteria)', 'L-tryptophan degradation V (side chain pathway)', 'canavanine degradation'], ['coral bioluminescence', 'dinoflagellate bioluminescence', "6'-dechloromelleolide F biosynthesis", 'pheomelanin biosynthesis', 'squid bioluminescence', 'firefly bioluminescence', 'protein N-glycosylation processing phase (yeast)', 'jellyfish bioluminescence'], ['D-phenylglycine degradation', 'emodin biosynthesis', 'cytidylyl copper-molybdenum cofactor biosynthesis', 'phenylethanol degradation', 'bis(guanylyl tungstenpterin) cofactor biosynthesis', 'cytidylyl molybdenum cofactor sulfurylation', 'bis(tungstenpterin) cofactor biosynthesis', 'bis(guanylyl molybdopterin) cofactor sulfurylation'], ['zealexin biosynthesis', 'thiamine diphosphate salvage III', 'retinoate biosynthesis I', 'thiazole component of thiamine diphosphate biosynthesis II', 'long chain fatty acid ester synthesis (engineered)', 'thiamine diphosphate salvage I', 'isopropanol biosynthesis (engineered)', 'retinoate biosynthesis II'], ['1-tuberculosinyladenosine biosynthesis', '&beta;-carotene biosynthesis', 'streptomycin biosynthesis', 'zeaxanthin biosynthesis', '&alpha;-carotene biosynthesis', 'violaxanthin, antheraxanthin and zeaxanthin interconversion', 'xyloglucan biosynthesis', 'iron reduction and absorption'], ['L-phenylalanine degradation III', 'trehalose degradation III', 'phosphatidylcholine biosynthesis I', "inosine-5'-phosphate biosynthesis I", 'acetaldehyde biosynthesis II', 'maltose degradation', 'NAD phosphorylation and transhydrogenation', 'oxalate degradation II'], ['methylwyosine biosynthesis', 'fatty acid &beta;-oxidation VII (yeast peroxisome)', '4-amino-2-methyl-5-diphosphomethylpyrimidine biosynthesis II', '7-(3-amino-3-carboxypropyl)-wyosine biosynthesis', 'aerobic respiration II (cytochrome c) (yeast)', 'ternatin C3 biosynthesis', 'Escherichia coli serotype O86 O-antigen biosynthesis'], ['pyruvate fermentation to acetoin III', 'palmitoleate biosynthesis', 'L-tyrosine degradation III', 'ubiquinol-6 biosynthesis (late decarboxylation)', 'NAD salvage pathway IV (from nicotinamide riboside)', 'L-ascorbate biosynthesis IV (animals, D-glucuronate pathway)', 'ceramide de novo biosynthesis'], ['kaempferol gentiobioside biosynthesis', 'polymethylated quercetin glucoside biosynthesis II - quercetagetin series (Chrysosplenium)', '8-amino-7-oxononanoate biosynthesis II', 'cyanide detoxification II', 'polymethylated quercetin glucoside biosynthesis I - quercetin series (Chrysosplenium)', '(3S)-linalool biosynthesis', 'genistin gentiobioside biosynthesis'], ['L-arginine degradation II (AST pathway)', 'Calvin-Benson-Bassham cycle', 'glycine betaine biosynthesis I (Gram-negative bacteria)', 'L-phenylalanine degradation II (anaerobic)', 'L-arginine degradation VIII (arginine oxidase pathway)', 'ammonia oxidation I (aerobic)', 'L-arginine degradation VII (arginase 3 pathway)'], ['yatein biosynthesis I', 'p-HBAD biosynthesis', 'diphenyl ethers degradation', "(-)-4'-demethyl-epipodophyllotoxin biosynthesis", 'mycobacterial sulfolipid biosynthesis', 'carbon monoxide oxidation to CO2', 'dimycocerosyl phthiocerol biosynthesis'], ['starch degradation I', 'UDP-&beta;-L-arabinose biosynthesis II (from &beta;-L-arabinose)', 'fructan biosynthesis', 'resveratrol biosynthesis', 'monolignol glucosides biosynthesis', 'dhurrin biosynthesis', 'backdoor pathway of androgen biosynthesis'], ['dTDP-D-desosamine biosynthesis', 'cholesterol degradation to androstenedione II (cholesterol dehydrogenase)', 'androstenedione degradation I (aerobic)', 'styrene degradation', 'cholesterol degradation to androstenedione I (cholesterol oxidase)', 'testosterone and androsterone degradation to androstendione (aerobic)', 'NADH repair (eukaryotes)'], ['11-cis-3-hydroxyretinal biosynthesis', 'phosphatidate metabolism, as a signaling molecule', 'mithramycin biosynthesis', 'the visual cycle (insects)', 'the visual cycle II (molluscs)', '5-nitroanthranilate degradation', 'violacein biosynthesis'], ['anthocyanidin acylglucoside and acylsambubioside biosynthesis', '1-chloro-2-nitrobenzene degradation', 'carnosate bioynthesis', 'dTDP-&alpha;-D-ravidosamine and dTDP-4-acetyl-&alpha;-D-ravidosamine biosynthesis', 'arabidopyrone biosynthesis', 'nitrite reduction (hemoglobin)', 'stipitatate biosynthesis'], ['daurichromenate biosynthesis', 'ginkgotoxin biosynthesis', 'leucine-derived hydroxynitrile glucoside biosynthesis', 'kainate biosynthesis', 'picolinate degradation', 'quebrachitol biosynthesis', 'domoic acid biosynthesis'], ['bassianin and desmethylbassianin biosynthesis', '3,6-anhydro-&alpha;-L-galactopyranose degradation', 'arginomycin biosynthesis', 'aspyridone A biosynthesis', 'ferrichrome A biosynthesis', 'blasticidin S biosynthesis', 'bacimethrin and bacimethrin pyrophosphate biosynthesis'], ['apigenin glycosides biosynthesis', 'acyl carrier protein metabolism', 'baruol biosynthesis', 'marneral biosynthesis', '(3E)-4,8-dimethylnona-1,3,7-triene biosynthesis II', 'glycine betaine biosynthesis V (from glycine)', 'amygdalin and prunasin degradation'], ['pelargonidin conjugates biosynthesis', 'fatty acid &beta;-oxidation III (unsaturated, odd number)', 'oleate biosynthesis I (plants)', 'cannabinoid biosynthesis', 'acyl-[acyl-carrier protein] thioesterase pathway', 'acyl-CoA hydrolysis', 'fatty acid &beta;-oxidation IV (unsaturated, even number)'], ['betalamic acid biosynthesis', 'syringetin biosynthesis', 'reductive TCA cycle II', 'crocetin biosynthesis', 'crocetin esters biosynthesis', 'betacyanin biosynthesis', 'raspberry ketone biosynthesis'], ['erythromycin D biosynthesis', 'vanillin and vanillate degradation II', 'dTDP-&beta;-L-megosamine biosynthesis', '5-deoxystrigol biosynthesis', 'spinosyn A biosynthesis', 'bisabolene biosynthesis (engineered)', 'olivetol biosynthesis'], ['methyl phomopsenoate biosynthesis', 'actinomycin D biosynthesis', 'CMP-diacetamido-8-epilegionaminic acid biosynthesis', 'bacterial bioluminescence', 'ophiobolin F biosynthesis', 'sulfoquinovose degradation II', 'icosapentaenoate biosynthesis III (8-desaturase, mammals)'], ['folate transformations III (E. coli)', 'D-galactose detoxification', 'L-histidine degradation VI', 'GDP-D-perosamine biosynthesis', 'L-histidine degradation III', 'coenzyme A biosynthesis II (eukaryotic)', 'L-alanine degradation II (to D-lactate)'], ['calonectrin biosynthesis', 'penicillin G and penicillin V biosynthesis', '3-hydroxy-4-methyl-anthranilate biosynthesis I', 'nivalenol biosynthesis', 'FeMo cofactor biosynthesis', 'deoxynivalenol biosynthesis', 'harzianum A and trichodermin biosynthesis'], ['D-apiose degradation I', 'D-apionate degradation II (RLP decarboxylase)', '(S)-lactate fermentation to propanoate, acetate and hydrogen', 'indole-3-acetate degradation II', 'D-apionate degradation III (RLP transcarboxylase/hydrolase)', 'dipicolinate biosynthesis', 'D-apionate degradation I (xylose isomerase family decarboxylase)'], ['hydroxycinnamate sugar acid ester biosynthesis', 'N-methylanthraniloyl-&beta;-D-glucopyranose biosynthesis', "3,3'-thiodipropanoate degradation", 'cyanidin 3,7-diglucoside polyacylation biosynthesis', 'violdelphin biosynthesis', "3,3'-disulfanediyldipropannoate degradation", '2-O-acetyl-3-O-trans-coutarate biosynthesis'], ['arsenate detoxification III (thioredoxin)', 'tetrahydropteridine recycling', 'D-apiose degradation II (to D-apionate)', 'crotonosine biosynthesis', '5-methoxybenzimidazole biosynthesis (anaerobic)', 'cyclic 2,3-bisphosphoglycerate biosynthesis', '5-methoxy-6-methylbenzimidazole biosynthesis (anaerobic)'], ['lactose degradation II', 'L-histidine degradation IV', '(Kdo)2-lipid A biosynthesis I (E. coli)', 'trans-4-hydroxy-L-proline degradation I', 'triacylglycerol degradation', 'L-idonate degradation', 'lipid A-core biosynthesis (E. coli K-12)'], ['L-proline biosynthesis IV', 'S-methyl-5-thio-&alpha;-D-ribose 1-phosphate degradation I', 'arsenate detoxification I (mammalian)', 'curcumin glucoside biosynthesis', 'aerobic respiration III (alternative oxidase pathway)', 'L-glutamate degradation IV', 'DIMBOA-glucoside activation'], ['Ferredoxin:NAD+ oxidoreductase', 'D-fructuronate degradation', '(S)-propane-1,2-diol degradation', 'glycerol degradation III', 'S-methyl-L-methionine cycle', 'Entner-Doudoroff shunt', 'xylitol degradation'], ['glycolate degradation II', 'anandamide biosynthesis II', 'anandamide biosynthesis I', 'palmitoyl ethanolamide biosynthesis', 'pederin biosynthesis', 'anandamide lipoxygenation', '2-arachidonoylglycerol biosynthesis'], ['thymine degradation', 'sulfoacetate degradation', 'L-lysine degradation VI', 'uracil degradation I (reductive)', 'homotaurine degradation', "cytidine-5'-diphosphate-glycerol biosynthesis", 'yersiniabactin biosynthesis'], ['fatty acid &beta;-oxidation II (plant peroxisome)', 'cyanide detoxification I', 'fatty acid &beta;-oxidation VI (mammalian peroxisome)', 'propanoate fermentation to 2-methylbutanoate', 'methylglyoxal degradation III', 'glutaryl-CoA degradation', '3-hydroxybutyryl-CoA dehydrogenase'], ['lampranthin biosynthesis', 'rose anthocyanin biosynthesis II (via cyanidin 3-O-&beta;-D-glucoside)', 'delphinidin diglucoside biosynthesis (acyl-glucose dependent)', 'anthocyanin biosynthesis (pelargonidin 3-O-glucoside)', 'anthocyanidin 3-malylglucoside biosynthesis (acyl-glucose dependent)', 'D-cycloserine biosynthesis', 'L-homophenylalanine biosynthesis'], ['propanoyl CoA degradation I', 'L-phenylalanine degradation I (aerobic)', "pyridoxal 5'-phosphate salvage I", 'dibenzofuran degradation', 'phenol degradation II (anaerobic)', 'pentachlorophenol degradation', 'tetrachloroethene degradation'], ['acrylonitrile degradation I', 'dTDP-&beta;-D-fucofuranose biosynthesis', 'dTDP-N-acetylthomosamine biosynthesis', 'dTDP-N-acetylviosamine biosynthesis', 'dTDP-3-acetamido-3,6-dideoxy-&alpha;-D-glucose biosynthesis', 'D-glucosaminate degradation', 'ecdysteroid metabolism (arthropods)'], ['methanogenesis from H2 and CO2', 'phospholipases', 'm-cresol degradation', 'L-lysine degradation III', 'L-methionine degradation I (to L-homocysteine)', 'protein N-glycosylation initial phase (eukaryotic)', 'methyl-coenzyme M reduction to methane'], ["2,2'-dihydroxyketocarotenoids biosynthesis", "abscisic acid degradation to 7'-hydroxyabscisate", 'abscisic acid degradation to neophaseic acid', '5-hexynoate biosynthesis', 'echinenone and zeaxanthin biosynthesis (Synechocystis)', 'bis(guanylyl molybdenum cofactor) biosynthesis', 'astaxanthin biosynthesis (flowering plants)'], ['D-carnitine degradation II', 'oryzalexin D and E biosynthesis', 'avenacin A-2 biosynthesis', 'momilactone A biosynthesis', 'des-methyl avenacin A-1 biosynthesis', '2,3-dihydroxybenzoate degradation', 'avenacin A-1 biosynthesis'], ['heme degradation V', 'heme degradation VII', '6-hydroxymethyl-dihydropterin diphosphate biosynthesis V (Pyrococcus)', '6-hydroxymethyl-dihydropterin diphosphate biosynthesis IV (Plasmodium)', 'heme degradation VI', 'urate conversion to allantoin III', 'taurine biosynthesis II'], ['lupeol biosynthesis', 'suberin monomers biosynthesis', 'coniferin metabolism', 'glucosinolate biosynthesis from homomethionine', 'homogalacturonan biosynthesis', 'carbon disulfide oxidation I (anaerobic)', 'homogalacturonan degradation'], ['phenylphenalenone biosynthesis', 'hydroxylated fatty acid biosynthesis (plants)', '4-hydroxybenzoate biosynthesis IV (plants)', 'fenchol biosynthesis I', 'curcuminoid biosynthesis', '4-hydroxybenzoate biosynthesis III (plants)', 'perillyl aldehyde biosynthesis'], ['diacylglycerol biosynthesis (PUFA enrichment in oilseed)', 'carotenoid cleavage', 'dTDP-&alpha;-D-forosamine biosynthesis', 'cellulose degradation I (cellulosome)', 'salidroside biosynthesis', 'phosphatidylcholine acyl editing', 'xyloglucan degradation III (cellobiohydrolase)'], ['saframycin A biosynthesis', 'aureobasidin A biosynthesis', 'fusaridione A biosynthesis', 'apicidin biosynthesis', 'apicidin F biosynthesis', 'galactolipid biosynthesis II', 'equisetin biosynthesis'], ['CDP-6-deoxy-D-gulose biosynthesis', 'cell-surface glycoconjugate-linked phosphonate biosynthesis', 'chlorophyll b2 biosynthesis', 'biotin biosynthesis from 8-amino-7-oxononanoate III', 'bile acid 7&beta;-dehydroxylation', "5'-deoxyadenosine degradation II", 'NADPH repair (eukaryotes)'], ['abscisic acid biosynthesis', 'L-ascorbate degradation V', 'methanol oxidation to formaldehyde I', 'methylamine degradation II', 'methylamine degradation I', 'L-ascorbate degradation III', 'L-ascorbate degradation II (bacterial, aerobic)'], ['lathyrine biosynthesis', 'arsenate detoxification V', 'aerobic respiration in cyanobacteria (NDH-2 to cytochrome c oxidase via plastocyanin)', 'protective electron sinks in the thylakoid membrane (PSII to PTOX)', 'fructosyllysine and glucosyllysine metabolism', 'aerobic respiration (NDH-1 to cytochrome c oxidase via plastocyanin)', 'assimilatory sulfate reduction IV'], ['Kdo transfer to lipid IVA II (Haemophilus)', 'fusaric acid biosynthesis', 'CMP-8-amino-3,8-dideoxy-D-manno-octulosonate biosynthesis', 'Kdo8N transfer to lipid IVA', 'fusarin C biosynthesis', 'anthocyanidin sambubioside biosynthesis', 'rosamicin biosynthesis'], ['icosapentaenoate biosynthesis V (8-desaturase, lower eukaryotes)', 'peramine biosynthesis', 'anditomin biosynthesis', 'arachidonate biosynthesis IV (8-detaturase, lower eukaryotes)', '&gamma;-linolenate biosynthesis III (cyanobacteria)', '&alpha;-linolenate biosynthesis II (cyanobacteria)', 'stearidonate biosynthesis (cyanobacteria)'], ['geraniol and nerol degradation', 'mannosylglucosylglycerate biosynthesis I', 'aromatic  glucosinolate activation', 'neurosporaxanthin biosynthesis', 'dehydrophos biosynthesis', 'glucosylglycerate biosynthesis II', 'jadomycin biosynthesis'], ['sulfoacetaldehyde degradation IV', 'glycerol degradation II', 'L-ascorbate degradation I (bacterial, anaerobic)', 'L-proline degradation II (reductive Stickland reaction)', '2-deoxy-D-ribose degradation I', 'trans-3-hydroxy-L-proline degradation', 'glutathione biosynthesis'], ['kanosamine biosynthesis I', 'furaneol and mesifurane biosynthesis', 'rifamycin B biosynthesis', 'dhurrin degradation', '3-amino-5-hydroxybenzoate biosynthesis', 'trehalose biosynthesis VI', 'xylogalacturonan biosynthesis'], ['cuticular wax biosynthesis', 'cis-zeatin biosynthesis', 'glyceollin biosynthesis', 'glucosinolate biosynthesis from phenylalanine', 'alkane oxidation', '(-)-glycinol biosynthesis', 'cytokinins degradation'], ['2-deoxy-D-glucose 6-phosphate degradation', '&beta;-alanine degradation III', 'mycofactocin biosynthesis', 'microcin B17 biosynthesis', '(2-trimethylamino)ethylphosphonate degradation', 'chlorophyll a2 biosynthesis'], ['(-)-medicarpin biosynthesis', 'indole-3-acetate degradation I', '4-nitrobenzoate degradation', 'C4 photosynthetic carbon assimilation cycle, NADP-ME type', '3-oxoadipate degradation', '(-)-maackiain biosynthesis'], ['allantoin degradation to ureidoglycolate I (urea producing)', 'cardiolipin biosynthesis I', 'urate conversion to allantoin I', 'epoxysqualene biosynthesis', 'clavulanate biosynthesis', 'ginsenosides biosynthesis'], ['hinokiresinol biosynthesis', 'kievitone detoxification', 'vernolate biosynthesis II', 'hinokinin biosynthesis', 'arctigenin and isoarctigenin biosynthesis', 'calycosin 7-O-glucoside biosynthesis'], ['sapienate biosynthesis', 'tetrathionate reduction I (to thiosulfate)', 'chrysin biosynthesis', '(5Z)-icosenoate biosynthesis', 'tetrathionate reductiuon II (to trithionate)', 'linear furanocoumarin biosynthesis'], ['phenolic malonylglucosides biosynthesis', 'seleno-amino acid detoxification and volatilization III', 'icosapentaenoate biosynthesis VI (fungi)', 'seleno-amino acid detoxification and volatilization II', 'chlorophyll a degradation II', 'selenate reduction'], ['IM-2 type &gamma;-butyrolactones biosynthesis', 'D-erythronate degradation II', 'D-threonate degradation', 'virginiae butanolide type &gamma;-butyrolactones biosynthesis', 'coelimycin P1 biosynthesis', 'A-factor &gamma;-butyrolactone biosynthesis'], ['lupanine biosynthesis', 'bisbenzylisoquinoline alkaloid biosynthesis', 'hydroxycinnamic acid serotonin amides biosynthesis', 'palmatine biosynthesis', 'hydroxycinnamic acid tyramine amides biosynthesis', 'sesamin biosynthesis'], ['glutarate degradation', 'formaldehyde oxidation III (mycothiol-dependent)', 'mycothiol biosynthesis', 'mycothiol-mediated detoxification', 'flavonoid biosynthesis', 'mycothiol oxidation'], ['L-nicotianamine biosynthesis', 'acridone alkaloid biosynthesis', 'guanylyl molybdenum cofactor biosynthesis', 'aflatoxins B1 and G1 biosynthesis', 'molybdenum cofactor sulfulylation (eukaryotes)', 'aflatoxins B2 and G2 biosynthesis'], ['N-glucosylnicotinate metabolism', 'methylglyoxal degradation VIII', 'NAD salvage (plants)', 'rutin biosynthesis', 'methylglyoxal degradation I', '3-methylthiopropanoate biosynthesis'], ['ammonia oxidation III', 'myo-inositol biosynthesis', 'formononetin biosynthesis', 'genistein conjugates interconversion', 'ascorbate glutathione cycle', 'daidzein conjugates interconversion'], ['glycine betaine biosynthesis III (plants)', 'indole-3-acetate inactivation III', 'phenylpropanoid biosynthesis, initial reactions', 'leucopelargonidin and leucocyanidin biosynthesis', 'actinorhodin biosynthesis', 'indole-3-acetate inactivation II'], ['long-chain fatty acid activation', 'L-glutamine degradation I', 'menaquinol-8 biosynthesis', 'pyruvate fermentation to propanoate I', 'NAD salvage pathway V (PNC V cycle)', 'L-glutamate biosynthesis I'], ['brassinosteroid biosynthesis II', 'benzoate degradation I (aerobic)', '(+)-pisatin biosynthesis', 'fatty acid &alpha;-oxidation I (plants)', 'phytosterol biosynthesis (plants)', 'medicarpin conjugates interconversion'], ['thyroid hormone biosynthesis', '3-chlorobenzoate degradation III (via gentisate)', 'luteolin glycosides biosynthesis', 'jasmonoyl-amino acid conjugates biosynthesis II', 'chrysoeriol biosynthesis', 'bergamotene biosynthesis I'], ['&beta;-D-mannosyl phosphomycoketide biosynthesis', 'aucuparin biosynthesis', 'phthiocerol biosynthesis', 'polyacyltrehalose biosynthesis', 'phenolphthiocerol biosynthesis', 'dimycocerosyl triglycosyl phenolphthiocerol biosynthesis'], ['cytidylyl molybdenum cofactor biosynthesis', 'L-dopa and L-dopachrome biosynthesis', 'ceramide degradation (generic)', 'trans-lycopene biosynthesis II (oxygenic phototrophs and green sulfur bacteria)', 'diphthamide biosynthesis I (archaea)', 'gibberellin inactivation II (methylation)'], ['methanogenesis from methylamine', 'soybean saponin I biosynthesis', 'coenzyme B/coenzyme M regeneration I (methanophenazine-dependent)', 'methanogenesis from dimethylamine', 'methyl-coenzyme M oxidation to CO2', 'factor 420 polyglutamylation'], ['adenosylcobinamide-GDP salvage from cobinamide II', 'N-methylpyrrolidone degradation', 'adenosylcobalamin biosynthesis from adenosylcobinamide-GDP II', 'protein O-mannosylation III (mammals, core M3)', 'cobalamin salvage (eukaryotic)', 'adenosylcobinamide-GDP salvage from cobinamide I'], ['putrescine degradation V', "S-methyl-5'-thioadenosine degradation III", '&beta;-alanine degradation I', 'Electron bifurcating LDH/Etf complex', 'acrylonitrile degradation II', 'indole-3-acetate biosynthesis V (bacteria and fungi)'], ['L-lyxonate degradation', '3,5,6-trichloro-2-pyridinol degradation', 'flaviolin dimer and mompain biosynthesis', 'rhizocticin A and B biosynthesis', 'protein ubiquitination', 'L-tyrosine degradation IV (to 4-methylphenol)'], ['cephamycin C biosynthesis', '2-nitrophenol degradation', '2,4-dinitrotoluene degradation', 'nitrobenzene degradation II', '2-nitrotoluene degradation', 'nitrobenzene degradation I'], ['sitosterol degradation to androstenedione', 'lincomycin A biosynthesis', 'DIBOA-glucoside biosynthesis', 'DIMBOA-glucoside biosynthesis', 'dTDP-3-acetamido-&alpha;-D-fucose biosynthesis', 'icosapentaenoate biosynthesis I (lower eukaryotes)'], ['meso-butanediol biosynthesis I', 'L-threonine degradation IV', 'L-citrulline degradation', '(S,S)-butanediol biosynthesis', 'ethanol degradation I', '(S,S)-butanediol degradation'], ['sophorolipid biosynthesis', 'shikimate degradation I', 'thioredoxin pathway', 'sophorosyloxydocosanoate deacetylation', 'sucrose degradation VII (sucrose 3-dehydrogenase)', 'sphingolipid biosynthesis (yeast)'], ['achromobactin biosynthesis', 'chondroitin biosynthesis', 'dermatan sulfate biosynthesis (late stages)', 'chondroitin sulfate degradation I (bacterial)', 'chondroitin sulfate biosynthesis (late stages)', 'chondroitin sulfate degradation (metazoa)'], ['2-isopropylphenol degradation', 'neomycin biosynthesis', 'butirosin biosynthesis', 'paromomycin biosynthesis', 'ribostamycin biosynthesis', 'paromamine biosynthesis I'], ['phenylethanol glycoconjugate biosynthesis', 'N-acetyl-D-galactosamine degradation', '3,5-dimethoxytoluene biosynthesis', 'phenylethyl acetate biosynthesis', 'asterrate biosynthesis', 'hopanoid biosynthesis (bacteria)'], ['tetramethylpyrazine degradation', 'aurachin A, B, C and D biosynthesis', 'aurachin RE biosynthesis', 'phospholipid remodeling (phosphatidylethanolamine, yeast)', 'ceramide phosphoethanolamine biosynthesis', 'methylphosphonate degradation II'], ['phosphatidylcholine biosynthesis II', 'L-threonine degradation I', 'pyruvate fermentation to butanol I', 'sulfide oxidation I (to sulfur globules)', 'methyl parathion degradation', 'CDP-D-mannitol biosynthesis'], ['protein O-glycosylation (Neisseria)', 'alkane biosynthesis II', 'alkane biosynthesis I', 'protein N-glycosylation (bacterial)', '(9Z)-tricosene biosynthesis', 'very long chain fatty acid biosynthesis II'], ['methanogenesis from glycine betaine', 'glycine betaine degradation III', 'proline betaine degradation II', 'L-dopa degradation II (bacterial)', 'kavain biosynthesis', 'yangonin biosynthesis'], ['spermine and spermidine degradation III', 'trichome monoterpenes biosynthesis', 'fenchol biosynthesis II', 'benzoate biosynthesis II (CoA-independent, non-&beta;-oxidative)', 'spermidine hydroxycinnamic acid conjugates biosynthesis', 'spermine and spermidine degradation II'], ['hordatine biosynthesis', 'serinol biosynthesis', 'fenchone biosynthesis', 'benzoyl-CoA biosynthesis', '3-carene biosynthesis', 'stigma estolide biosynthesis'], ['3-(imidazol-5-yl)lactate salvage', 'L-histidine degradation V', 'nicotinate degradation II', 'L-histidine degradation II', 'phylloquinol biosynthesis', 'ent-kaurene biosynthesis I'], ['thiocoraline biosynthesis', 'echinomycin and triostin A biosynthesis', 'quinoxaline-2-carboxylate biosynthesis', 'stellatic acid biosynthesis', '3-hydroxyquinaldate biosynthesis', 'T-2 toxin biosynthesis'], ['p-cumate degradation to 2-hydroxypentadienoate', 'melamine degradation', 'ferulate and sinapate biosynthesis', '4-toluenesulfonate degradation II', 'cyanuric acid degradation II', '2-hydroxypenta-2,4-dienoate degradation'], ['anthocyanin biosynthesis', 'colupulone and cohumulone biosynthesis', 'lupulone and humulone biosynthesis', 'xanthohumol biosynthesis', 'acacetin biosynthesis', 'sphingolipid biosynthesis (plants)'], ['methylquercetin biosynthesis', 'bile acid biosynthesis, neutral pathway', 'dimethyl sulfone degradation', 'indican biosynthesis', 'dimethyl sulfide degradation II (oxidation)', 'indigo biosynthesis'], ['caffeine biosynthesis II (via paraxanthine)', 'theobromine biosynthesis I', 'GA12 biosynthesis', 'gibberellin biosynthesis II (early C-3 hydroxylation)', 'caffeine biosynthesis I', 'gibberellin biosynthesis III (early C-13 hydroxylation)'], ['resolvin D biosynthesis', 'homocarnosine biosynthesis', 'aspirin triggered resolvin E biosynthesis', 'carnosine biosynthesis', 'aspirin triggered resolvin D biosynthesis', 'salicylate degradation IV'], ['UDP-N-acetylmuramoyl-pentapeptide biosynthesis II (lysine-containing)', 'UDP-N-acetylmuramoyl-pentapeptide biosynthesis I (meso-diaminopimelate containing)', 'arginine deiminase test', 'peptidoglycan biosynthesis I (meso-diaminopimelate containing)', 'flavin salvage', 'peptidoglycan cross-bridge biosynthesis II (E. faecium)'], ['kanosamine biosynthesis II', 'CO2 fixation into oxaloacetate (anaplerotic)', 'indole-3-acetate biosynthesis I', 'salicylate biosynthesis II', 'mycolate biosynthesis', 'sulfoquinovosyl diacylglycerol biosynthesis'], ['iso-bile acids biosynthesis II', 'gadusol biosynthesis', 'bacteriochlorophyll d biosynthesis', 'shinorine biosynthesis', 'bile acid 7&alpha;-dehydroxylation', 'bisphenol A degradation'], ['alanine racemization', 'tRNA charging', 'Phosphate ABC transporter', 'oxalate degradation IV', 'palmitate biosynthesis (type I fatty acid synthase)', 'UDP-&alpha;-D-galactose biosynthesis'], ['biphenyl degradation', 'linoleate biosynthesis II (animals)', 'phthalate degradation (aerobic)', 'gramicidin S biosynthesis', '&gamma;-linolenate biosynthesis II (animals)', 'lotaustralin degradation'], ['ferroxidase', 'D-mannose degradation I', 'nitric oxide biosynthesis II (mammals)', 'sucrose degradation IV (sucrose phosphorylase)', 'heterolactic fermentation', 'guanine and guanosine salvage II'], ['3-hydroxy-L-homotyrosine biosynthesis', '3-hydroxy-4-methyl-proline biosynthesis', 'echinocandin B degradation', 'dermatan sulfate degradation I (bacterial)', 'echinocandin B biosynthesis', 'coniferyl alcohol 9-methyl ester biosynthesis'], ['dimethylsulfoniopropanoate degradation I (cleavage)', 'dimethyl sulfide degradation I', 'methylthiopropanonate degradation II (demethylation)', 'methylthiopropanoate degradation I (cleavage)', '2,4,6-trinitrotoluene degradation', 'dimethylsulfoniopropanoate degradation III (demethylation)'], ['leucodelphinidin biosynthesis', 'trans-4-hydroxy-L-proline degradation II', "6'-deoxychalcone metabolism", 'anthocyanin biosynthesis (delphinidin 3-O-glucoside)', 'L-tyrosine degradation II', 'rose anthocyanin biosynthesis I (via cyanidin 5-O-&beta;-D-glucoside)'], ['2-methylketone biosynthesis', 'manganese oxidation I', 'pyruvate fermentation to acetone', "spirilloxanthin and 2,2'-diketo-spirilloxanthin biosynthesis", 'manganese oxidation II', 'pyruvate fermentation to ethanol III'], ['willardiine and isowillardiine biosynthesis', 'tetrahydroxyxanthone biosynthesis (from benzoate)', 'UDP-&alpha;-D-galacturonate biosynthesis II (from D-galacturonate)', 'indole-3-acetate biosynthesis IV (bacteria)', 'L-arginine degradation XI', 'tetrahydroxyxanthone biosynthesis (from 3-hydroxybenzoate)'], ['diadinoxanthin and fucoxanthin biosynthesis', 'diadinoxanthin and diatoxanthin interconversion', 'UDP-N-acetylmuramoyl-pentapeptide biosynthesis III (meso-diaminopimelate containing)', 'ellagic acid degradation to urolithins', 'paerucumarin biosynthesis', 'tabtoxinine-&beta;-lactam biosynthesis'], ['thiamine diphosphate biosynthesis III (Staphylococcus)', 'thiazole component of thiamne diphosphate biosynthesis III', '(Z)-butanethial-S-oxide biosynthesis', 'chitin derivatives degradation', 'thiamine diphosphate biosynthesis IV (eukaryotes)', 'base-degraded thiamine salvage'], ['flavonol biosynthesis', 'L-lysine biosynthesis V', 'menthol biosynthesis', 'monoterpene biosynthesis', 'linamarin degradation', 'phaseollin biosynthesis'], ['sakuranetin biosynthesis', 'UDP-D-apiose biosynthesis (from UDP-D-glucuronate)', 'GDP-L-galactose biosynthesis', 'hesperitin glycoside biosynthesis', 'phytol salvage pathway', 'ponciretin biosynthesis'], ['menaquinol-4 biosynthesis II', 'dolabralexins biosynthesis', 'tricin biosynthesis', 'vitamin K degradation', 'vitamin K-epoxide cycle'], ['biochanin A conjugates interconversion', 'formononetin conjugates interconversion', 'cytokinin-O-glucosides biosynthesis', 'cytokinins 9-N-glucoside biosynthesis', 'cytokinins 7-N-glucoside biosynthesis'], ['(1,3)-&beta;-D-xylan degradation', 'xyloglucan degradation I (endoglucanase)', 'cellulose degradation II (fungi)', 'flavonoid biosynthesis (in equisetum)', 'L-arabinan degradation'], ['atrazine degradation I (aerobic)', '2-aminoethylphosphonate degradation I', 'D-xylose degradation II', 'mimosine biosynthesis', 'L-lysine degradation XI (mammalian)'], ['4-sulfocatechol degradation', 'ethanedisulfonate degradation', 'chlorogenic acid biosynthesis II', 'methanesulfonate degradation', 'chlorogenic acid biosynthesis I'], ['4-chloronitrobenzene degradation', '2-nitrobenzoate degradation II', 'L-tryptophan degradation to 2-amino-3-carboxymuconate semialdehyde', '4-nitrotoluene degradation II', '2,6-dinitrotoluene degradation'], ['indole-3-acetate inactivation IV', 'free phenylpropanoid acid biosynthesis', 'glutamate removal from folates', 'isoflavonoid biosynthesis I', 'isoflavonoid biosynthesis II'], ['methylglyoxal degradation VII', 'matairesinol biosynthesis', 'acetone degradation I (to methylglyoxal)', 'gramine biosynthesis', 'methylglyoxal degradation II'], ['4-hydroxycoumarin and dicoumarol biosynthesis', 'L-ascorbate biosynthesis V (euglena, D-galacturonate pathway)', 'quinate degradation II', 'ginsenoside degradation II', 'shikimate degradation II'], ['gibberellin inactivation III (epoxidation)', 'eumelanin biosynthesis', 'D-galacturonate degradation III', 'D-galacturonate degradation II', 'chanoclavine I aldehyde biosynthesis'], ['rhizobitoxine biosynthesis', 'Escherichia coli serotype O9a O-antigen biosynthesis', 'formaldehyde oxidation V (bacillithiol-dependent)', 'homofuraneol biosynthesis', '(2S,3E)-2-amino-4-methoxy-but-3-enoate biosynthesis'], ['diterpene phytoalexins precursors biosynthesis', 'sesquiterpenoid phytoalexins biosynthesis', 'putrescine degradation IV', 'capsidiol biosynthesis', 'linamarin biosynthesis'], ['pyruvate fermentation to ethanol II', 'pentagalloylglucose biosynthesis', 'cornusiin E biosynthesis', '6-methoxypodophyllotoxin biosynthesis', 'gallotannin biosynthesis'], ['acetyl-CoA biosynthesis from citrate', 'TCA cycle V (2-oxoglutarate synthase)', 'reductive TCA cycle I', 'D-arabitol degradation', 'pyrimidine deoxyribonucleotides de novo biosynthesis II'], ['tetradecanoate biosynthesis (mitochondria)', 'anteiso-branched-chain fatty acid biosynthesis', 'even iso-branched-chain fatty acid biosynthesis', 'octanoyl-[acyl-carrier protein] biosynthesis (mitochondria, yeast)', 'odd iso-branched-chain fatty acid biosynthesis'], ['hydroxymethylpyrimidine salvage', 'L-methionine degradation II', 'pyrimidine nucleobases salvage I', 'NADH repair (prokaryotes)', 'adenosine ribonucleotides de novo biosynthesis'], ['L-cysteine degradation I', 'cyclohexanol degradation', 'cyanate degradation', 'nitrate reduction I (denitrification)', 'D-arabinose degradation II'], ['taxol biosynthesis', 'mannosylglycerate biosynthesis II', 'erythro-tetrahydrobiopterin biosynthesis I', 'GDP-&alpha;-D-glucose biosynthesis', 'glucosylglycerate biosynthesis I'], ['NADH to hydrogen peroxide electron transfer', 'prenylated FMNH2 biosynthesis', 'D-gulosides conversion to D-glucosides', 'periplasmic disulfide bond reduction', 'periplasmic disulfide bond formation'], ['superoxide radicals degradation', 'chitin degradation II (Vibrio)', 'Catalase test', 'ethanol degradation IV', 'L-arabinose degradation I'], ["adenosine 5'-phosphoramidate biosynthesis", 'fatty acid biosynthesis initiation (plant mitochondria)', 'diacylglyceryl-N,N,N-trimethylhomoserine biosynthesis', 'scopoletin biosynthesis', '6-hydroxymethyl-dihydropterin diphosphate biosynthesis II (Methanocaldococcus)'], ['L-alanine biosynthesis II', 'L-asparagine biosynthesis II', 'L-asparagine biosynthesis I', 'L-alanine degradation III', 'melibiose degradation'], ['chaxamycin biosynthesis', 'spectinabilin biosynthesis', 'streptovaricin biosynthesis', 'chloramphenicol biosynthesis', 'aureothin biosynthesis'], ['phosphatidylcholine resynthesis via glycerophosphocholine', '1,4-dihydroxy-6-naphthoate biosynthesis II', 'thiamine triphosphate metabolism', 'demethylmenaquinol-6 biosynthesis II', '1,4-dihydroxy-6-naphthoate biosynthesis I'], ['3-sulfopropanediol degradation', 'caffeine degradation V (bacteria, via trimethylurate)', 'ketolysis', 'tricetin methylation', 'ketogenesis'], ['L-lactaldehyde degradation (aerobic)', 'TCA cycle IV (2-oxoglutarate decarboxylase)', 'choline degradation III', 'D-galactarate degradation II', '4-hydroxybenzoate biosynthesis I (eukaryotes)'], ['tetrahydromonapterin biosynthesis', 'curcumin degradation', 'nitrate reduction VIII (dissimilatory)', 'uracil degradation III', 'tRNA processing'], ['sterculate biosynthesis', '6-methoxymellein biosynthesis', 'nitrate reduction VI (assimilatory)', 'ethylbenzene degradation (anaerobic)', 'UDP-&alpha;-D-glucuronate biosynthesis (from myo-inositol)'], ['pyoverdine I biosynthesis', 'pyochelin biosynthesis', 'salicylate biosynthesis I', 'carrageenan biosynthesis', 'ginsenoside degradation I'], ['L-cysteine degradation II', 'glycine biosynthesis IV', 'L-asparagine degradation I', 'L-alanine biosynthesis III', 'PRPP biosynthesis'], ['neoabietic acid biosynthesis', 'dehydroabietic acid biosynthesis', 'phenol degradation I (aerobic)', 'palustric acid biosynthesis', 'catechol degradation to 2-hydroxypentadienoate II'], ['bacteriochlorophyll a biosynthesis', 'D-arabinose degradation III', 'D-glucuronate degradation I', 'L-ascorbate biosynthesis III (D-sorbitol pathway)', '5,6-dimethylbenzimidazole biosynthesis I (aerobic)'], ['dimethylsulfoniopropanoate biosynthesis III (algae and phytoplankton)', 'dimethylsulfoniopropanoate biosynthesis II (Spartina)', 'dimethylsulfoniopropanoate biosynthesis I (Wollastonia)', 'dimethylsulfoniopropanoate degradation II (cleavage)', 'dimethylsulfide to cytochrome c2 electron transfer'], ['alizarin biosynthesis', 'xylan biosynthesis', 'hyperforin and adhyperforin biosynthesis', 'heptaprenyl diphosphate biosynthesis', 'lawsone biosynthesis'], ['guanosine nucleotides degradation II', 'laminaribiose degradation', 'adenosine nucleotides degradation I', 'guanosine nucleotides degradation III', 'anhydromuropeptides recycling I'], ['isorenieratene biosynthesis I (actinobacteria)', 'spongiadioxin C biosynthesis', 'polybrominated dihydroxylated diphenyl ethers biosynthesis', 'fungal bioluminescence', 'psilocybin biosynthesis'], ['L-methionine biosynthesis I', 'L-homoserine biosynthesis', 'L-leucine biosynthesis', 'L-histidine biosynthesis', 'glycine biosynthesis III'], ['naringenin glycoside biosynthesis', 'chlorophyll a degradation I', 'L-glutamate degradation VI (to pyruvate)', 'L-methionine degradation III', 'chlorophyll a biosynthesis I'], ['N6-L-threonylcarbamoyladenosine37-modified tRNA biosynthesis', 'cyclopropane fatty acid (CFA) biosynthesis', 'D-gluconate degradation', 'fructose degradation', 'L-threonine biosynthesis'], ['complex N-linked glycan biosynthesis (plants)', 'archaeosine biosynthesis II', 'protein O-mannosylation II (mammals, core M1 and core M2)', 'rubber degradation I', 'protein O-mannosylation I (yeast)'], ['dTDP-4-O-demethyl-&beta;-L-noviose biosynthesis', '3-amino-4,7-dihydroxy-coumarin biosynthesis', 'oleate &beta;-oxidation (reductase-dependent, yeast)', '3-dimethylallyl-4-hydroxybenzoate biosynthesis', 'estradiol biosynthesis II'], ['pulcherrimin biosynthesis', 'trehalose biosynthesis II', 'fructan degradation', 'bacillithiol biosynthesis', 'L-ascorbate biosynthesis I (plants, L-galactose pathway)'], ['bile acids deconjugation', 'cellulose biosynthesis', 'anaerobic energy metabolism (invertebrates, cytosol)', 'gluconeogenesis III', 'siroheme biosynthesis'], ['bergamotene biosynthesis II', 'patchoulol biosynthesis', 'curcumene biosynthesis', 'santalene biosynthesis I', 'thyroid hormone metabolism I (via deiodination)'], ['sphingomyelin metabolism', 'phosphopantothenate biosynthesis II', '&beta;-alanine biosynthesis I', 'sphingosine and sphingosine-1-phosphate metabolism', 'berberine biosynthesis'], ['3-methyl-branched fatty acid &alpha;-oxidation', 'ceramide degradation by &alpha;-oxidation', 'sulfolactate degradation III', '15-epi-lipoxin biosynthesis', 'lipoxin biosynthesis'], ['(4Z,7Z,10Z,13Z,16Z)-docosa-4,7,10,13,16-pentaenoate biosynthesis II (4-desaturase)', 'arachidonate biosynthesis V (8-detaturase, mammals)', '5,6-dimethylbenzimidazole biosynthesis II (anaerobic)', '(4Z,7Z,10Z,13Z,16Z)-docosapentaenoate biosynthesis (6-desaturase)', 'docosahexaenoate biosynthesis IV (4-desaturase, mammals)'], ['aliphatic glucosinolate biosynthesis, side chain elongation cycle', 'glucosinolate biosynthesis from pentahomomethionine', 'glucosinolate biosynthesis from trihomomethionine', 'glucosinolate biosynthesis from dihomomethionine', 'glucosinolate biosynthesis from tetrahomomethionine'], ['dicranin biosynthesis', 'guanine and guanosine salvage III', 'ethanol degradation III', 'sulfolactate degradation I', 'adenine and adenosine salvage V'], ['indole-3-acetate inactivation V', 'malonate degradation I (biotin-independent)', 'malonate decarboxylase activation', 'maysin biosynthesis', '3-hydroxypropanoate/4-hydroxybutanate cycle'], ['adamantanone degradation', 'phosphonoacetate degradation', 'arsonoacetate degradation', 'incomplete reductive TCA cycle', '4-nitrotoluene degradation I'], ['palmitoleate biosynthesis III (cyanobacteria)', '(7Z,10Z,13Z)-hexadecatrienoate biosynthesis', 'okenone biosynthesis', 'ursodeoxycholate biosynthesis (bacteria)', 'linoleate biosynthesis III (cyanobacteria)'], ['spermine biosynthesis', 'L-arginine degradation III (arginine decarboxylase/agmatinase pathway)', 'L-arginine degradation X (arginine monooxygenase pathway)', 'linezolid resistance', 'putrescine biosynthesis I'], ['sucrose biosynthesis II', 'myo-inositol degradation II', 'mycocyclosin biosynthesis', "inosine-5'-phosphate biosynthesis III", 'alkylnitronates degradation'], ['hentriaconta-3,6,9,12,15,19,22,25,28-nonaene biosynthesis', 'paromamine biosynthesis II', 'terminal olefins biosynthesis II', "UDP-N,N'-diacetylbacillosamine biosynthesis", 'gentamicin biosynthesis'], ['UDP-N-acetyl-D-glucosamine biosynthesis I', 'L-asparagine biosynthesis III (tRNA-dependent)', 'S-adenosyl-L-methionine salvage II', 'CMP-3-deoxy-D-manno-octulosonate biosynthesis', 'cadaverine biosynthesis'], ['saponin biosynthesis II', '4-hydroxybenzoate biosynthesis II (bacteria)', 'fosfomycin biosynthesis', '&beta;-alanine biosynthesis IV', 'saponin biosynthesis III'], ['catechol degradation to &beta;-ketoadipate', 'benzoyl-CoA degradation II (anaerobic)', 'camalexin biosynthesis', '3,8-divinyl-chlorophyllide a biosynthesis I (aerobic, light-dependent)', 'L-carnitine degradation I'], ['1,3-dichlorobenzene degradation', 'chlorobenzene degradation', 'anthranilate degradation I (aerobic)', '4-ethylphenol degradation (anaerobic)', 'alginate biosynthesis II (bacterial)'], ["rot-2'-enonate biosynthesis", 'uracil degradation II (oxidative)', 'hemoglobin degradation', 'D-arginine degradation', 'rotenoid biosynthesis II'], ['lutein biosynthesis', 'sterigmatocystin biosynthesis', 'geosmin biosynthesis', 'versicolorin B biosynthesis', "(1'S,5'S)-averufin biosynthesis"], ['methylsalicylate degradation', "pyridoxal 5'-phosphate biosynthesis II", 'glycine betaine degradation I', 'benzoate degradation II (aerobic and anaerobic)', 'NAD(P)/NADPH interconversion'], ['heme degradation IV', 'heme degradation III', 'neolacto-series glycosphingolipids biosynthesis', 'UDP-yelosamine biosynthesis', 'heme degradation II'], ['D-carnitine degradation I', 'acetone degradation III (to propane-1,2-diol)', 'phosphatidylcholine biosynthesis VII', 'gentisate degradation II', 'benzoyl-&beta;-D-glucopyranose biosynthesis'], ['D-xylose degradation IV', 'L-cysteine biosynthesis V (mycobacteria)', 'oleate &beta;-oxidation (thioesterase-dependent, yeast)', 'oleate &beta;-oxidation (isomerase-dependent, yeast)', 'octopamine biosynthesis'], ['volatile benzenoid biosynthesis I (ester formation)', 'glutathione amide metabolism', 'glutathione-mediated detoxification I', 'volatile cinnamoic ester biosynthesis', 'glutathione-peroxide redox reactions'], ['agarose degradation', 'glucuronoarabinoxylan degradation', 'porphyran degradation', 'neoxanthin biosynthesis', '&lambda;-carrageenan degradation']]
    cluster_data_0_6 = [['menaquinol-13 biosynthesis', 'menaquinol-12 biosynthesis', 'demethylmenaquinol-8 biosynthesis I', 'demethylmenaquinol-9 biosynthesis', 'demethylmenaquinol-6 biosynthesis I', 'menaquinol-11 biosynthesis', 'demethylmenaquinol-4 biosynthesis', 'menaquinol-10 biosynthesis', '&beta;-alanine biosynthesis II', 'menaquinol-7 biosynthesis', 'assimilatory sulfate reduction II', 'assimilatory sulfate reduction III'], ['Bifidobacterium shunt', 'L-serine biosynthesis I', 'protein Pupylation and dePupylation', 'Bifidobacterium shunt II', 'polyphosphate metabolism', 'isoniazid activation', 'NAD phosphorylation and dephosphorylation', 'felinine and 3-methyl-3-sulfanylbutan-1-ol biosynthesis'], ['fructose 2,6-bisphosphate biosynthesis', 'formate oxidation to CO2', 'glycerol degradation I', '3-dehydroquinate biosynthesis II (archaea)', 'nitrate reduction V (assimilatory)', 'pyrimidine deoxyribonucleotide phosphorylation', 'L-alanine biosynthesis I', 'D-myo-inositol (1,4,5)-trisphosphate biosynthesis'], ['CDP-diacylglycerol biosynthesis III', 'tRNA splicing I', 'isoprene biosynthesis II (engineered)', 'adenine and adenosine salvage II', 'nitric oxide biosynthesis I (plants)', 'mevalonate pathway I (eukaryotes and bacteria)', 'acyl carrier protein activation', 'mevalonate pathway IV (archaea)'], ['2-aminoethylphosphonate biosynthesis', 'nitrate reduction IV (dissimilatory)', 'GDP-6-deoxy-D-altro-heptose biosynthesis', 'Oxidase test', 'hexaprenyl diphosphate biosynthesis', 'D-sorbitol degradation I', 'glycerol-3-phosphate shuttle'], ['trehalose degradation VI (periplasmic)', 'Extracellular starch(27n) degradation', '(S)-lactate fermentation to propanoate', 'L-threonine degradation V', 'trehalose degradation II (cytosolic)', 'C4 photosynthetic carbon assimilation cycle, NAD-ME type', '2-aminoethylphosphonate degradation II'], ['putrescine degradation V', "S-methyl-5'-thioadenosine degradation III", '&beta;-alanine degradation I', 'Electron bifurcating LDH/Etf complex', 'acrylonitrile degradation II', 'indole-3-acetate biosynthesis V (bacteria and fungi)'], ['trehalose degradation V', 'acetate and ATP formation from acetyl-CoA II', '8-amino-7-oxononanoate biosynthesis III', 'trehalose degradation IV', 'UDP-N-acetyl-&alpha;-D-mannosaminouronate biosynthesis', 'L-tryptophan degradation II (via pyruvate)'], ['phytol degradation', 'lactose and galactose degradation I', 'poly(glycerol phosphate) wall teichoic acid biosynthesis', 'NADH:menaquinone6 oxidoreductase', '2-carboxy-1,4-naphthoquinol biosynthesis', 'terminal olefins biosynthesis I'], ['L-phenylalanine degradation III', 'trehalose degradation III', 'phosphatidylcholine biosynthesis I', 'acetaldehyde biosynthesis II', 'maltose degradation', 'oxalate degradation II'], ['UDP-N-acetylmuramoyl-pentapeptide biosynthesis II (lysine-containing)', 'UDP-N-acetylmuramoyl-pentapeptide biosynthesis I (meso-diaminopimelate containing)', 'arginine deiminase test', 'peptidoglycan biosynthesis I (meso-diaminopimelate containing)', 'flavin salvage', 'peptidoglycan cross-bridge biosynthesis II (E. faecium)'], ['cyclobis-(1&rarr;6)-&alpha;-nigerosyl degradation', 'ABH and Lewis epitopes biosynthesis from type 2 precursor disaccharide', 'biosynthesis of Lewis epitopes (H. pylori)', 'ABH and Lewis epitopes biosynthesis from type 1 precursor disaccharide', 'glycolipid desaturation'], ['oleate biosynthesis IV (anaerobic)', 'thiamine diphosphate biosynthesis I (E. coli)', 'octaprenyl diphosphate biosynthesis', 'thiamine diphosphate biosynthesis II (Bacillus)', 'nonaprenyl diphosphate biosynthesis I'], ['flavonol acylglucoside biosynthesis II - isorhamnetin derivatives', 'flavonol acylglucoside biosynthesis I - kaempferol derivatives', 'phytochromobilin biosynthesis', 'flavonol acylglucoside biosynthesis III - quercetin derivatives', 'kaempferide triglycoside biosynthesis'], ['trigonelline biosynthesis', 'polymyxin A biosynthesis', 'glycerophosphodiester degradation', 'putrescine degradation III', 'serotonin degradation'], ['tetradecanoate biosynthesis (mitochondria)', 'anteiso-branched-chain fatty acid biosynthesis', 'even iso-branched-chain fatty acid biosynthesis', 'octanoyl-[acyl-carrier protein] biosynthesis (mitochondria, yeast)', 'odd iso-branched-chain fatty acid biosynthesis'], ['D-erythronate degradation I', 'phosphatidylserine and phosphatidylethanolamine biosynthesis I', 'thiazole component of thiamine diphosphate biosynthesis I', 'adenosine nucleotides degradation III', 'L-tryptophan degradation IV (via indole-3-lactate)'], ['triclosan resistance', 'CMP phosphorylation', 'ppGpp metabolism', 'guanosine ribonucleotides de novo biosynthesis', 'UTP and CTP de novo biosynthesis'], ['archaeosine biosynthesis I', 'L-rhamnose degradation II', 'ubiquinol-8 biosynthesis (early decarboxylation)', 'L-rhamnose degradation III', 'poly-hydroxy fatty acids biosynthesis'], ['Bile acid 7alpha-dehydroxylation', 'Inulin degradation(11xFru,1xGlc) (extracellular)', 'iso-bile acids biosynthesis (NADH or NADPH dependent)', 'L-Tyrosine degradation to 4-hydroxyphenylacetate via tyramine', 'Ljungdahl-Wood pathway (gapseq)'], ['folate transformations III (E. coli)', 'D-galactose detoxification', 'L-histidine degradation VI', 'L-histidine degradation III', 'L-alanine degradation II (to D-lactate)'], ['purine deoxyribonucleosides degradation I', '4-deoxy-L-threo-hex-4-enopyranuronate degradation', 'L-homocysteine biosynthesis', 'adenine and adenosine salvage III', 'purine deoxyribonucleosides degradation II']]
    cluster_data_0_5 =   [['menaquinol-13 biosynthesis', 'menaquinol-12 biosynthesis', 'demethylmenaquinol-8 biosynthesis I', 'demethylmenaquinol-9 biosynthesis', 'demethylmenaquinol-6 biosynthesis I', 'menaquinol-11 biosynthesis', 'demethylmenaquinol-4 biosynthesis', 'menaquinol-10 biosynthesis', '&beta;-alanine biosynthesis II', 'menaquinol-7 biosynthesis', 'assimilatory sulfate reduction II', 'assimilatory sulfate reduction III'], ['CDP-diacylglycerol biosynthesis III', 'tRNA splicing I', 'isoprene biosynthesis II (engineered)', 'vancomycin resistance I', 'adenine and adenosine salvage II', 'nitric oxide biosynthesis I (plants)', 'mevalonate pathway I (eukaryotes and bacteria)', 'L-lysine biosynthesis II', 'citrate degradation', 'acyl carrier protein activation', 'mevalonate pathway IV (archaea)'], ['D-erythronate degradation I', 'octaprenyl diphosphate biosynthesis', 'thiamine diphosphate biosynthesis II (Bacillus)', 'L-tryptophan degradation IV (via indole-3-lactate)', 'phosphatidylserine and phosphatidylethanolamine biosynthesis I', 'oleate biosynthesis IV (anaerobic)', 'thiazole component of thiamine diphosphate biosynthesis I', 'thiamine diphosphate biosynthesis I (E. coli)', 'adenosine nucleotides degradation III', 'nonaprenyl diphosphate biosynthesis I'], ['hydrogen to dimethyl sulfoxide electron transfer', 'carbon tetrachloride degradation II', 'L-isoleucine biosynthesis III', 'CDP-D-arabitol biosynthesis', 'L-arginine degradation XIII (reductive Stickland reaction)', 'acetylene degradation (anaerobic)', 'reductive acetyl coenzyme A pathway I (homoacetogenic bacteria)', 'L-asparagine degradation III (mammalian)', 'methanogenesis from acetate', '&beta;-1,4-D-mannosyl-N-acetyl-D-glucosamine degradation'], ['heme b biosynthesis IV (Gram-positive bacteria)', 'benzimidazolyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP', '2-carboxy-1,4-naphthoquinol biosynthesis', 'NADH:menaquinone6 oxidoreductase', 'terminal olefins biosynthesis I', 'lactose and galactose degradation I', 'cinnamoyl-CoA biosynthesis', 'L-Fucose degradation (non-phosphorylating)', 'poly(glycerol phosphate) wall teichoic acid biosynthesis', 'phytol degradation'], ['fructose 2,6-bisphosphate biosynthesis', 'formate oxidation to CO2', 'glycerol degradation I', '3-dehydroquinate biosynthesis II (archaea)', 'nitrate reduction V (assimilatory)', 'pyrimidine deoxyribonucleotide phosphorylation', 'ulvan degradation', 'phosphatidylinositol biosynthesis I (bacteria)', 'L-alanine biosynthesis I', 'D-myo-inositol (1,4,5)-trisphosphate biosynthesis'], ['L-arginine degradation IV (arginine decarboxylase/agmatine deiminase pathway)', 'Agmatine extracellular biosynthesis', 'NADH to cytochrome bd oxidase electron transfer I', 'adenine and adenosine salvage I', 'NADH to cytochrome bo oxidase electron transfer II', 'NADH to cytochrome bd oxidase electron transfer II', 'sulfate activation for sulfonation', 'folate transformations II (plants)', 'NADH to cytochrome bo oxidase electron transfer I', 'putrescine biosynthesis II'], ['4-hydroxyphenylacetate degradation', 'anthranilate degradation III (anaerobic)', 'phenylethylamine degradation I', '1,4-dichlorobenzene degradation', '4-hydroxymandelate degradation', 'orthanilate degradation', '1,2-dichloroethane degradation', '4-toluenecarboxylate degradation', '2-oxobutanoate degradation II'], ['trehalose biosynthesis III', 'toluene degradation to benzoate', 'diacylglycerol and triacylglycerol biosynthesis', 'toluene degradation to 2-hydroxypentadienoate (via 4-methylcatechol)', 'toluene degradation to 4-methylphenol', 'toluene degradation to 2-hydroxypentadienoate I (via o-cresol)', 'trehalose biosynthesis I', 'toluene degradation to 2-hydroxypentadienoate (via toluene-cis-diol)'], ['Bifidobacterium shunt', 'L-serine biosynthesis I', 'protein Pupylation and dePupylation', 'Bifidobacterium shunt II', 'polyphosphate metabolism', 'isoniazid activation', 'NAD phosphorylation and dephosphorylation', 'felinine and 3-methyl-3-sulfanylbutan-1-ol biosynthesis'], ['roseoflavin biosynthesis', 'nitric oxide biosynthesis III (bacteria)', 'coenzyme B/coenzyme M regeneration III (coenzyme F420-dependent)', 'coenzyme B/coenzyme M regeneration II (ferredoxin-dependent)', 'jasmonoyl-L-isoleucine inactivation', 'D-altritol and galactitol degradation', 'N-hydroxy-L-pipecolate biosynthesis', 'coenzyme B/coenzyme M regeneration IV (H2-dependent)'], ['bacteriochlorophyll e biosynthesis', '3-hydroxy-4-methyl-anthranilate biosynthesis II', 'bacteriochlorophyll c biosynthesis', 'phosalacine biosynthesis', 'NAD salvage pathway II (PNC IV cycle)', 'L-leucine degradation IV (reductive Stickland reaction)', 'chlorophyll a biosynthesis III', 'bacteriochlorophyll b biosynthesis'], ['N-cyclopropylmelamine degradation', 'lactucaxanthin biosynthesis', 'capsanthin and capsorubin biosynthesis', 'coumarin biosynthesis (via 2-coumarate)', 'factor 430 biosynthesis', 'artemisinin and arteannuin B biosynthesis', 'factor 420 biosynthesis II (mycobacteria)', 'lactate biosynthesis (archaea)'], ['L-phenylalanine degradation III', 'trehalose degradation III', 'phosphatidylcholine biosynthesis I', "inosine-5'-phosphate biosynthesis I", 'acetaldehyde biosynthesis II', 'maltose degradation', 'NAD phosphorylation and transhydrogenation', 'oxalate degradation II'], ['thymine degradation', 'sulfoacetate degradation', 'L-lysine degradation VI', 'uracil degradation I (reductive)', 'homotaurine degradation', "cytidine-5'-diphosphate-glycerol biosynthesis", 'yersiniabactin biosynthesis'], ['4-hydroxy-2-nonenal detoxification', 'furcatin degradation', 'ceramide and sphingolipid recycling and degradation (yeast)', 'chitin deacetylation', 'megalomicin A biosynthesis', 'erythromycin A biosynthesis', 'tea aroma glycosidic precursor bioactivation'], ['saframycin A biosynthesis', 'aureobasidin A biosynthesis', 'fusaridione A biosynthesis', 'apicidin biosynthesis', 'apicidin F biosynthesis', 'galactolipid biosynthesis II', 'equisetin biosynthesis'], ['CDP-6-deoxy-D-gulose biosynthesis', 'cell-surface glycoconjugate-linked phosphonate biosynthesis', 'chlorophyll b2 biosynthesis', 'biotin biosynthesis from 8-amino-7-oxononanoate III', 'bile acid 7&beta;-dehydroxylation', "5'-deoxyadenosine degradation II", 'NADPH repair (eukaryotes)'], ['bassianin and desmethylbassianin biosynthesis', '3,6-anhydro-&alpha;-L-galactopyranose degradation', 'arginomycin biosynthesis', 'aspyridone A biosynthesis', 'ferrichrome A biosynthesis', 'blasticidin S biosynthesis', 'bacimethrin and bacimethrin pyrophosphate biosynthesis'], ['L-arginine degradation II (AST pathway)', 'Calvin-Benson-Bassham cycle', 'glycine betaine biosynthesis I (Gram-negative bacteria)', 'L-phenylalanine degradation II (anaerobic)', 'L-arginine degradation VIII (arginine oxidase pathway)', 'ammonia oxidation I (aerobic)', 'L-arginine degradation VII (arginase 3 pathway)'], ['yatein biosynthesis I', 'p-HBAD biosynthesis', 'diphenyl ethers degradation', "(-)-4'-demethyl-epipodophyllotoxin biosynthesis", 'mycobacterial sulfolipid biosynthesis', 'carbon monoxide oxidation to CO2', 'dimycocerosyl phthiocerol biosynthesis'], ['mevalonate degradation', 'glycogen biosynthesis II (from UDP-D-Glucose)', 'L-leucine degradation II', 'gibberellin biosynthesis I (non C-3, non C-13 hydroxylation)', 'L-isoleucine degradation II', 'chlorophyll cycle', 'L-leucine degradation III'], ['abscisic acid biosynthesis', 'L-ascorbate degradation V', 'methanol oxidation to formaldehyde I', 'methylamine degradation II', 'methylamine degradation I', 'L-ascorbate degradation III', 'L-ascorbate degradation II (bacterial, aerobic)'], ["2,2'-dihydroxyketocarotenoids biosynthesis", "abscisic acid degradation to 7'-hydroxyabscisate", 'abscisic acid degradation to neophaseic acid', '5-hexynoate biosynthesis', 'echinenone and zeaxanthin biosynthesis (Synechocystis)', 'bis(guanylyl molybdenum cofactor) biosynthesis', 'astaxanthin biosynthesis (flowering plants)'], ['calonectrin biosynthesis', 'penicillin G and penicillin V biosynthesis', '3-hydroxy-4-methyl-anthranilate biosynthesis I', 'nivalenol biosynthesis', 'FeMo cofactor biosynthesis', 'deoxynivalenol biosynthesis', 'harzianum A and trichodermin biosynthesis'], ['D-apiose degradation I', 'D-apionate degradation II (RLP decarboxylase)', '(S)-lactate fermentation to propanoate, acetate and hydrogen', 'indole-3-acetate degradation II', 'D-apionate degradation III (RLP transcarboxylase/hydrolase)', 'dipicolinate biosynthesis', 'D-apionate degradation I (xylose isomerase family decarboxylase)'], ['2-aminoethylphosphonate biosynthesis', 'nitrate reduction IV (dissimilatory)', 'GDP-6-deoxy-D-altro-heptose biosynthesis', 'Oxidase test', 'hexaprenyl diphosphate biosynthesis', 'D-sorbitol degradation I', 'glycerol-3-phosphate shuttle'], ['heme degradation V', 'heme degradation VII', '6-hydroxymethyl-dihydropterin diphosphate biosynthesis V (Pyrococcus)', '6-hydroxymethyl-dihydropterin diphosphate biosynthesis IV (Plasmodium)', 'heme degradation VI', 'urate conversion to allantoin III', 'taurine biosynthesis II'], ['hyoscyamine and scopolamine biosynthesis', 'gentiodelphin biosynthesis', 'calystegine biosynthesis', 'N-methyl-&Delta;1-pyrrolinium cation biosynthesis', 'L-lysine degradation VII', 'nicotine biosynthesis', 'L-lysine degradation VIII'], ['&alpha;-cyclopiazonate biosynthesis', 'heme d1 biosynthesis', '(-)-microperfuranone biosynthesis', 'prodigiosin biosynthesis', 'ergothioneine biosynthesis II (fungi)', 'heme b biosynthesis III (from siroheme)', 'asperlicin E biosynthesis'], ['D-sorbitol degradation II', '6-hydroxymethyl-dihydropterin diphosphate biosynthesis I', '4-methylphenyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP', 'allantoin degradation to ureidoglycolate II (ammonia producing)', '6-hydroxymethyl-dihydropterin diphosphate biosynthesis III (Chlamydia)', 'glycolate and glyoxylate degradation I', 'phenyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP'], ['staphyloferrin B biosynthesis', 'plant arabinogalactan type II degradation', 'L-cysteine biosynthesis IX (Trichomonas vaginalis)', 'L-cysteine biosynthesis VIII (Thermococcus kodakarensis)', 'staphylopine biosynthesis', '4-coumarate degradation (aerobic)', 'trans-caffeate degradation (aerobic)'], ['Ferredoxin:NAD+ oxidoreductase', 'D-fructuronate degradation', '(S)-propane-1,2-diol degradation', 'glycerol degradation III', 'S-methyl-L-methionine cycle', 'Entner-Doudoroff shunt', 'xylitol degradation'], ['trehalose degradation VI (periplasmic)', 'Extracellular starch(27n) degradation', '(S)-lactate fermentation to propanoate', 'L-threonine degradation V', 'trehalose degradation II (cytosolic)', 'C4 photosynthetic carbon assimilation cycle, NAD-ME type', '2-aminoethylphosphonate degradation II'], ['anandamide degradation', '2-heptyl-3-hydroxy-4(1H)-quinolone biosynthesis', 'dopamine degradation', 'pyocyanin biosynthesis', 'pterostilbene biosynthesis', 'di-myo-inositol phosphate biosynthesis'], ['L-lysine degradation V', 'sulfite oxidation III', 'sulfite oxidation II', 'L-lysine degradation IV', 'sulfide oxidation III (to sulfite)', 'shisonin biosynthesis'], ['protein O-glycosylation (Neisseria)', 'alkane biosynthesis II', 'alkane biosynthesis I', 'protein N-glycosylation (bacterial)', '(9Z)-tricosene biosynthesis', 'very long chain fatty acid biosynthesis II'], ['nerol biosynthesis', 'geraniol biosynthesis (cytosol)', 'acrylate degradation II', 'platensimycin biosynthesis', '2-methyl-branched fatty acid &beta;-oxidation', '10-methylstearate biosynthesis'], ['methanogenesis from glycine betaine', 'glycine betaine degradation III', 'proline betaine degradation II', 'L-dopa degradation II (bacterial)', 'kavain biosynthesis', 'yangonin biosynthesis'], ['2-deoxy-D-glucose 6-phosphate degradation', '&beta;-alanine degradation III', 'mycofactocin biosynthesis', 'microcin B17 biosynthesis', '(2-trimethylamino)ethylphosphonate degradation', 'chlorophyll a2 biosynthesis'], ['brassinosteroid biosynthesis II', 'benzoate degradation I (aerobic)', '(+)-pisatin biosynthesis', 'fatty acid &alpha;-oxidation I (plants)', 'phytosterol biosynthesis (plants)', 'medicarpin conjugates interconversion'], ['hinokiresinol biosynthesis', 'kievitone detoxification', 'vernolate biosynthesis II', 'hinokinin biosynthesis', 'arctigenin and isoarctigenin biosynthesis', 'calycosin 7-O-glucoside biosynthesis'], ['&beta; myrcene degradation', 'sesaminol glucoside biosynthesis', 'myricetin gentiobioside biosynthesis', 'quercetin gentiotetraside biosynthesis', 'emetine biosynthesis', 'noscapine biosynthesis'], ['zealexin biosynthesis', 'thiamine diphosphate salvage III', 'thiamine diphosphate salvage I', 'thiazole component of thiamine diphosphate biosynthesis II', 'isopropanol biosynthesis (engineered)', 'retinoate biosynthesis II'], ['(R)- and (S)-3-hydroxybutanoate biosynthesis (engineered)', 'ubiquinol-6 biosynthesis from 4-aminobenzoate (yeast)', 'nicotinate degradation I', 'baicalein degradation (hydrogen peroxide detoxification)', 'gibberellin biosynthesis V', 'purine deoxyribonucleosides salvage'], ['sapienate biosynthesis', 'tetrathionate reduction I (to thiosulfate)', 'chrysin biosynthesis', '(5Z)-icosenoate biosynthesis', 'tetrathionate reductiuon II (to trithionate)', 'linear furanocoumarin biosynthesis'], ['leucodelphinidin biosynthesis', 'trans-4-hydroxy-L-proline degradation II', "6'-deoxychalcone metabolism", 'anthocyanin biosynthesis (delphinidin 3-O-glucoside)', 'L-tyrosine degradation II', 'rose anthocyanin biosynthesis I (via cyanidin 5-O-&beta;-D-glucoside)'], ['arsenate reduction (respiratory)', '1D-myo-inositol hexakisphosphate biosynthesis III (Spirodela polyrrhiza)', 'arsenite oxidation I (respiratory)', 'wighteone and luteone biosynthesis', 'arsenate detoxification II (glutaredoxin)', 'kievitone biosynthesis'], ['pyruvate fermentation to opines', 'daunorubicin biosynthesis', 'sucrose biosynthesis III', 'thiamine phosphate formation from pyrithiamine and oxythiamine (yeast)', 'aclacinomycin biosynthesis', 'doxorubicin biosynthesis'], ['IM-2 type &gamma;-butyrolactones biosynthesis', 'D-erythronate degradation II', 'D-threonate degradation', 'virginiae butanolide type &gamma;-butyrolactones biosynthesis', 'coelimycin P1 biosynthesis', 'A-factor &gamma;-butyrolactone biosynthesis'], ['lupanine biosynthesis', 'bisbenzylisoquinoline alkaloid biosynthesis', 'hydroxycinnamic acid serotonin amides biosynthesis', 'palmatine biosynthesis', 'hydroxycinnamic acid tyramine amides biosynthesis', 'sesamin biosynthesis'], ['nepetalactone biosynthesis', '(Kdo)2-lipid A biosynthesis II (P. putida)', 'methylphosphonate biosynthesis', 'methylphosphonate degradation III', 'N-3-oxalyl-L-2,3-diaminopropanoate biosynthesis', '8-O-methylated benzoxazinoid glucoside biosynthesis'], ['willardiine and isowillardiine biosynthesis', 'tetrahydroxyxanthone biosynthesis (from benzoate)', 'UDP-&alpha;-D-galacturonate biosynthesis II (from D-galacturonate)', 'indole-3-acetate biosynthesis IV (bacteria)', 'L-arginine degradation XI', 'tetrahydroxyxanthone biosynthesis (from 3-hydroxybenzoate)'], ['cob(II)yrinate a,c-diamide biosynthesis II (late cobalt incorporation)', 'urate conversion to allantoin II', 'aminopropanol phosphate biosynthesis II', 'lipoate biosynthesis and incorporation IV (yeast)', 'mRNA capping I', 'cob(II)yrinate a,c-diamide biosynthesis I (early cobalt insertion)'], ['group E Salmonella O antigen biosynthesis', 'group D2 Salmonella O antigen biosynthesis', 'group A Salmonella O antigen biosynthesis', 'group D1 Salmonella O antigen biosynthesis', 'group C2 Salmonella O antigen biosynthesis', 'toluene degradation to benzoyl-CoA (anaerobic)'], ['starch degradation II', 'candicidin biosynthesis', 'methylhalides biosynthesis (plants)', 'methylaspartate cycle', 'sangivamycin biosynthesis', 'toyocamycin biosynthesis'], ['plasmalogen degradation', 'butane degradation', 'methyl tert-butyl ether degradation', '&omega;-sulfo-II-dihydromenaquinone-9 biosynthesis', 'plasmalogen biosynthesis', '2-methylpropene degradation'], ['o-diquinones biosynthesis', 'methane oxidation to methanol II', 'pinitol biosynthesis I', 'pinitol biosynthesis II', "S-methyl-5'-thioadenosine degradation I", 'nitrate reduction VII (denitrification)'], ['thiocoraline biosynthesis', 'echinomycin and triostin A biosynthesis', 'quinoxaline-2-carboxylate biosynthesis', 'stellatic acid biosynthesis', '3-hydroxyquinaldate biosynthesis', 'T-2 toxin biosynthesis'], ['putrescine biosynthesis III', 'creatinine degradation II', 'phytate degradation I', 'creatinine degradation III', 'phytate degradation II', 'aloesone biosynthesis I'], ['&beta;-D-mannosyl phosphomycoketide biosynthesis', 'aucuparin biosynthesis', 'phthiocerol biosynthesis', 'polyacyltrehalose biosynthesis', 'phenolphthiocerol biosynthesis', 'dimycocerosyl triglycosyl phenolphthiocerol biosynthesis'], ['5-(methoxycarbonylmethoxy)uridine biosynthesis', 'methylphosphonate degradation I', 'proline to cytochrome bo oxidase electron transfer', 'D-lactate to cytochrome bo oxidase electron transfer', 'cardiolipin biosynthesis III', 'muropeptide degradation'], ['methanogenesis from methylamine', 'soybean saponin I biosynthesis', 'coenzyme B/coenzyme M regeneration I (methanophenazine-dependent)', 'methanogenesis from dimethylamine', 'methyl-coenzyme M oxidation to CO2', 'factor 420 polyglutamylation'], ['flavin-N5-oxide biosynthesis', '2-deoxy-D-ribose degradation II', '8-oxo-(d)GTP detoxification II', 'chlorpyrifos degradation', 'pyruvoyl group formation from L-serine', 'sodorifen biosynthesis'], ['p-cumate degradation to 2-hydroxypentadienoate', 'melamine degradation', 'ferulate and sinapate biosynthesis', '4-toluenesulfonate degradation II', 'cyanuric acid degradation II', '2-hydroxypenta-2,4-dienoate degradation'], ['adenosylcobinamide-GDP salvage from cobinamide II', 'N-methylpyrrolidone degradation', 'adenosylcobalamin biosynthesis from adenosylcobinamide-GDP II', 'protein O-mannosylation III (mammals, core M3)', 'cobalamin salvage (eukaryotic)', 'adenosylcobinamide-GDP salvage from cobinamide I'], ['putrescine degradation V', "S-methyl-5'-thioadenosine degradation III", '&beta;-alanine degradation I', 'Electron bifurcating LDH/Etf complex', 'acrylonitrile degradation II', 'indole-3-acetate biosynthesis V (bacteria and fungi)'], ['caffeine biosynthesis II (via paraxanthine)', 'theobromine biosynthesis I', 'GA12 biosynthesis', 'gibberellin biosynthesis II (early C-3 hydroxylation)', 'caffeine biosynthesis I', 'gibberellin biosynthesis III (early C-13 hydroxylation)'], ["6'-dechloromelleolide F biosynthesis", 'pheomelanin biosynthesis', 'firefly bioluminescence', 'coral bioluminescence', 'dinoflagellate bioluminescence', 'jellyfish bioluminescence'], ['resolvin D biosynthesis', 'homocarnosine biosynthesis', 'aspirin triggered resolvin E biosynthesis', 'carnosine biosynthesis', 'aspirin triggered resolvin D biosynthesis', 'salicylate degradation IV'], ['trehalose degradation V', 'acetate and ATP formation from acetyl-CoA II', '8-amino-7-oxononanoate biosynthesis III', 'trehalose degradation IV', 'UDP-N-acetyl-&alpha;-D-mannosaminouronate biosynthesis', 'L-tryptophan degradation II (via pyruvate)'], ['cephamycin C biosynthesis', '2-nitrophenol degradation', '2,4-dinitrotoluene degradation', 'nitrobenzene degradation II', '2-nitrotoluene degradation', 'nitrobenzene degradation I'], ['thiamine diphosphate biosynthesis III (Staphylococcus)', 'thiazole component of thiamne diphosphate biosynthesis III', '(Z)-butanethial-S-oxide biosynthesis', 'chitin derivatives degradation', 'thiamine diphosphate biosynthesis IV (eukaryotes)', 'base-degraded thiamine salvage'], ['sitosterol degradation to androstenedione', 'lincomycin A biosynthesis', 'DIBOA-glucoside biosynthesis', 'DIMBOA-glucoside biosynthesis', 'dTDP-3-acetamido-&alpha;-D-fucose biosynthesis', 'icosapentaenoate biosynthesis I (lower eukaryotes)'], ['procollagen hydroxylation and glycosylation', 'protein SAMPylation and SAMP-mediated thiolation', 'tRNA-uridine 2-thiolation (yeast mitochondria)', 'tRNA-uridine 2-thiolation (cytoplasmic)', 'tRNA-uridine 2-thiolation (mammalian mitochondria)', 'tRNA-uridine 2-thiolation and selenation (bacteria)'], ['nocardicin A biosynthesis', 'pentose phosphate pathway (oxidative branch) II', 'dimethyl sulfide biosynthesis from methionine', 'terephthalate degradation', 'protein S-nitrosylation and denitrosylation', 'Arg/N-end rule pathway (eukaryotic)'], ['2-fucosyllactose degradation', 'sulfate reduction I (assimilatory)', 'viscosin biosynthesis', 'massetolide A biosynthesis', 'Lacto-N-tetraose degradation', 'L-valine degradation I'], ['D-sorbitol biosynthesis I', 'L-valine degradation II', 'luteolin biosynthesis', 'pinobanksin biosynthesis', 'rosmarinic acid biosynthesis I', 'rosmarinic acid biosynthesis II'], ['sophorolipid biosynthesis', 'shikimate degradation I', 'thioredoxin pathway', 'sophorosyloxydocosanoate deacetylation', 'sucrose degradation VII (sucrose 3-dehydrogenase)', 'sphingolipid biosynthesis (yeast)'], ["pyridoxal 5'-phosphate salvage II (plants)", 'pyrimidine deoxyribonucleosides salvage', 'quercetin diglycoside biosynthesis (pollen-specific)', 'pinocembrin C-glucosylation', 'kaempferol diglycoside biosynthesis (pollen-specific)', 'UTP and CTP dephosphorylation I'], ['atromentin biosynthesis', '3-(4-sulfophenyl)butanoate degradation', 'terrequinone A biosynthesis', '(R)-canadine biosynthesis', 'brassicicene C biosynthesis', 'mevalonate pathway III (Thermoplasma)'], ['cutin biosynthesis', 'sinapate ester biosynthesis', 'canavanine degradation', 'L-tryptophan degradation VI (via tryptamine)', 'UDP-&beta;-L-rhamnose biosynthesis', 'choline biosynthesis I'], ['oleoresin monoterpene volatiles biosynthesis', 'naphthalene degradation (aerobic)', 'betaxanthin biosynthesis', '1,3-dimethylbenzene degradation to 3-methylbenzoate', 'isopimaric acid biosynthesis', 'oleoresin sesquiterpene volatiles biosynthesis'], ['UDP-N-acetylmuramoyl-pentapeptide biosynthesis II (lysine-containing)', 'UDP-N-acetylmuramoyl-pentapeptide biosynthesis I (meso-diaminopimelate containing)', 'arginine deiminase test', 'peptidoglycan biosynthesis I (meso-diaminopimelate containing)', 'flavin salvage', 'peptidoglycan cross-bridge biosynthesis II (E. faecium)'], ['kanosamine biosynthesis II', 'CO2 fixation into oxaloacetate (anaplerotic)', 'indole-3-acetate biosynthesis I', 'salicylate biosynthesis II', 'mycolate biosynthesis', 'sulfoquinovosyl diacylglycerol biosynthesis'], ['pentaketide chromone biosynthesis', 'L-homomethionine biosynthesis', 'taurine degradation II', 'phenylacetate degradation II (anaerobic)', 'benzoyl-CoA degradation I (aerobic)', 'fluorene degradation II'], ['iso-bile acids biosynthesis II', 'gadusol biosynthesis', 'bacteriochlorophyll d biosynthesis', 'shinorine biosynthesis', 'bile acid 7&alpha;-dehydroxylation', 'bisphenol A degradation'], ['biphenyl degradation', 'linoleate biosynthesis II (animals)', 'phthalate degradation (aerobic)', 'gramicidin S biosynthesis', '&gamma;-linolenate biosynthesis II (animals)', 'lotaustralin degradation'], ['phenylethanol glycoconjugate biosynthesis', 'N-acetyl-D-galactosamine degradation', '3,5-dimethoxytoluene biosynthesis', 'phenylethyl acetate biosynthesis', 'asterrate biosynthesis', 'hopanoid biosynthesis (bacteria)'], ['tetramethylpyrazine degradation', 'aurachin A, B, C and D biosynthesis', 'aurachin RE biosynthesis', 'phospholipid remodeling (phosphatidylethanolamine, yeast)', 'ceramide phosphoethanolamine biosynthesis', 'methylphosphonate degradation II'], ['cycloartenol biosynthesis', 'epiberberine biosynthesis', 'coptisine biosynthesis', 'sterol biosynthesis (methylotrophs)', 'limonene degradation IV (anaerobic)', 'parkeol biosynthesis'], ['N-glucosylnicotinate metabolism', 'methylglyoxal degradation VIII', 'NAD salvage (plants)', 'rutin biosynthesis', 'methylglyoxal degradation I', '3-methylthiopropanoate biosynthesis'], ['divinyl ether biosynthesis II', 'traumatin and (Z)-3-hexen-1-yl acetate biosynthesis', '9-lipoxygenase and 9-allene oxide synthase pathway', 'abietic acid biosynthesis', 'levopimaric acid biosynthesis', '9-lipoxygenase and 9-hydroperoxide lyase pathway'], ['erythromycin D biosynthesis', 'dTDP-&beta;-L-megosamine biosynthesis', '5-deoxystrigol biosynthesis', 'bisabolene biosynthesis (engineered)', 'olivetol biosynthesis'], ['menaquinol-4 biosynthesis II', 'dolabralexins biosynthesis', 'tricin biosynthesis', 'vitamin K degradation', 'vitamin K-epoxide cycle'], ['L-cysteine degradation I', 'cyclohexanol degradation', 'cyanate degradation', 'nitrate reduction I (denitrification)', 'D-arabinose degradation II'], ['bacteriochlorophyll a biosynthesis', 'D-arabinose degradation III', 'D-glucuronate degradation I', 'L-ascorbate biosynthesis III (D-sorbitol pathway)', '5,6-dimethylbenzimidazole biosynthesis I (aerobic)'], ['docosahexaenoate biosynthesis I (lower eukaryotes)', 'icosapentaenoate biosynthesis II (6-desaturase, mammals)', '4-coumarate degradation (anaerobic)', 'icosapentaenoate biosynthesis IV (bacteria)', 'cyanophycin metabolism'], ['(1,3)-&beta;-D-xylan degradation', 'xyloglucan degradation I (endoglucanase)', 'cellulose degradation II (fungi)', 'flavonoid biosynthesis (in equisetum)', 'L-arabinan degradation'], ['3-(imidazol-5-yl)lactate salvage', 'L-histidine degradation V', 'nicotinate degradation II', 'L-histidine degradation II', 'ent-kaurene biosynthesis I'], ['4-sulfocatechol degradation', 'ethanedisulfonate degradation', 'chlorogenic acid biosynthesis II', 'methanesulfonate degradation', 'chlorogenic acid biosynthesis I'], ['homospermidine biosynthesis II', 'cholesterol degradation to androstenedione III (anaerobic)', 'cytochrome c biogenesis (system I type)', 'cytochrome c biogenesis (system II type)', 'androsrtendione degradation II (anaerobic)'], ['aliphatic glucosinolate biosynthesis, side chain elongation cycle', 'glucosinolate biosynthesis from pentahomomethionine', 'glucosinolate biosynthesis from trihomomethionine', 'glucosinolate biosynthesis from dihomomethionine', 'glucosinolate biosynthesis from tetrahomomethionine'], ['4-chloronitrobenzene degradation', '2-nitrobenzoate degradation II', 'L-tryptophan degradation to 2-amino-3-carboxymuconate semialdehyde', '4-nitrotoluene degradation II', '2,6-dinitrotoluene degradation'], ['3,8-divinyl-chlorophyllide a biosynthesis III (aerobic, light independent)', 'L-phenylalanine degradation V', 'polymethylated quercetin biosynthesis', 'polymethylated myricetin biosynthesis (tomato)', '7-dehydroporiferasterol biosynthesis'], ['triclosan resistance', 'CMP phosphorylation', 'ppGpp metabolism', 'guanosine ribonucleotides de novo biosynthesis', 'UTP and CTP de novo biosynthesis'], ['Spodoptera littoralis pheromone biosynthesis', 'dechlorogriseofulvin biosynthesis', '(8E,10E)-dodeca-8,10-dienol biosynthesis', 'dTDP-&beta;-L-digitoxose biosynthesis', 'griseofulvin biosynthesis'], ['i antigen and I antigen biosynthesis', 'globo-series glycosphingolipids biosynthesis', 'gala-series glycosphingolipids biosynthesis', 'lacto-series glycosphingolipids biosynthesis', 'ganglio-series glycosphingolipids biosynthesis'], ['superoxide radicals degradation', 'chitin degradation II (Vibrio)', 'Catalase test', 'ethanol degradation IV', 'L-arabinose degradation I'], ['dimethylsulfoniopropanoate biosynthesis III (algae and phytoplankton)', 'dimethylsulfoniopropanoate biosynthesis II (Spartina)', 'dimethylsulfoniopropanoate biosynthesis I (Wollastonia)', 'dimethylsulfoniopropanoate degradation II (cleavage)', 'dimethylsulfide to cytochrome c2 electron transfer'], ['branched-chain polyamines biosynthesis', 'carbaryl degradation', 'factor 420 biosynthesis I (archaea)', '3PG-factor 420 biosynthesis', 'long-chain polyamine biosynthesis'], ['indole-3-acetate inactivation IV', 'free phenylpropanoid acid biosynthesis', 'glutamate removal from folates', 'isoflavonoid biosynthesis I', 'isoflavonoid biosynthesis II'], ["adenosine 5'-phosphoramidate biosynthesis", 'fatty acid biosynthesis initiation (plant mitochondria)', 'diacylglyceryl-N,N,N-trimethylhomoserine biosynthesis', 'scopoletin biosynthesis', '6-hydroxymethyl-dihydropterin diphosphate biosynthesis II (Methanocaldococcus)'], ['galloylated catechin biosynthesis', 'anthocyanidin modification (Arabidopsis)', '2-aminoethylphosphonate degradation III', 'cyanidin dimalonylglucoside biosynthesis', 'acylated cyanidin galactoside biosynthesis'], ['indole glucosinolate activation (intact plant cell)', 'glucosinolate biosynthesis from hexahomomethionine', 'NAD salvage pathway I (PNC VI cycle)', 'indole glucosinolate activation (herbivore attack)', 'quinate degradation I'], ['autoinducer CAI-1 biosynthesis', 'nystatin biosynthesis', 'naphthalene degradation (anaerobic)', 'astaxanthin dirhamnoside biosynthesis', 'rhizobactin 1021 biosynthesis'], ['2-methyladeninyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP', '5-methoxy-6-methylbenzimidazolyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP', 'rhabduscin biosynthesis', 'adeninyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP', '12-epi-fischerindole biosynthesis'], ['nitroethane degradation', 'ajugose biosynthesis II (galactinol-independent)', 'arachidonate biosynthesis I (6-desaturase, lower eukaryotes)', 'kaempferol triglucoside biosynthesis', 'esculetin biosynthesis'], ['&gamma;-resorcylate degradation I', 'propane degradation I', 'butachlor degradation', '&gamma;-resorcylate degradation II', 'indolmycin biosynthesis'], ['paspaline biosynthesis', '3&beta;-hydroxysesquiterpene lactone biosynthesis', 'gossypetin metabolism', 'linuron degradation', 'paxilline and diprenylpaxilline biosynthesis'], ['dTDP-&beta;-L-olivose biosynthesis', 'umbelliferone biosynthesis', 'plastoquinol-9 biosynthesis II', 'dTDP-&beta;-L-mycarose biosynthesis', 'threo-tetrahydrobiopterin biosynthesis'], ['gliotoxin biosynthesis', 'lovastatin biosynthesis', 'aflatrem biosynthesis', 'fumiquinazoline D biosynthesis', '1,2-propanediol biosynthesis from lactate (engineered)'], ['flavonol acylglucoside biosynthesis II - isorhamnetin derivatives', 'flavonol acylglucoside biosynthesis I - kaempferol derivatives', 'phytochromobilin biosynthesis', 'flavonol acylglucoside biosynthesis III - quercetin derivatives', 'kaempferide triglycoside biosynthesis'], ['methyl phomopsenoate biosynthesis', 'ophiobolin F biosynthesis', 'bacterial bioluminescence', 'sulfoquinovose degradation II', 'icosapentaenoate biosynthesis III (8-desaturase, mammals)'], ['pelargonidin diglucoside biosynthesis (acyl-glucose dependent)', 'cyanidin diglucoside biosynthesis (acyl-glucose dependent)', 'ergothioneine biosynthesis I (bacteria)', 'apigeninidin 5-O-glucoside biosynthesis', 'luteolinidin 5-O-glucoside biosynthesis'], ['methylglyoxal degradation VII', 'matairesinol biosynthesis', 'acetone degradation I (to methylglyoxal)', 'gramine biosynthesis', 'methylglyoxal degradation II'], ['anthocyanidin acylglucoside and acylsambubioside biosynthesis', '1-chloro-2-nitrobenzene degradation', 'carnosate bioynthesis', 'arabidopyrone biosynthesis', 'nitrite reduction (hemoglobin)'], ['adamantanone degradation', 'phosphonoacetate degradation', 'arsonoacetate degradation', 'incomplete reductive TCA cycle', '4-nitrotoluene degradation I'], ['&alpha;-carotene biosynthesis', '&beta;-carotene biosynthesis', 'violaxanthin, antheraxanthin and zeaxanthin interconversion', 'zeaxanthin biosynthesis', 'streptomycin biosynthesis'], ['palmitoleate biosynthesis III (cyanobacteria)', '(7Z,10Z,13Z)-hexadecatrienoate biosynthesis', 'okenone biosynthesis', 'ursodeoxycholate biosynthesis (bacteria)', 'linoleate biosynthesis III (cyanobacteria)'], ['archaeosine biosynthesis I', 'L-rhamnose degradation II', 'ubiquinol-8 biosynthesis (early decarboxylation)', 'L-rhamnose degradation III', 'poly-hydroxy fatty acids biosynthesis'], ['chaxamycin biosynthesis', 'spectinabilin biosynthesis', 'streptovaricin biosynthesis', 'chloramphenicol biosynthesis', 'aureothin biosynthesis'], ['Bile acid 7alpha-dehydroxylation', 'Inulin degradation(11xFru,1xGlc) (extracellular)', 'iso-bile acids biosynthesis (NADH or NADPH dependent)', 'L-Tyrosine degradation to 4-hydroxyphenylacetate via tyramine', 'Ljungdahl-Wood pathway (gapseq)'], ['(3R)-linalool biosynthesis', 'viridicatin biosynthesis', 'lyngbyatoxin biosynthesis', "4'-methoxyviridicatin biosynthesis", 'dapdiamides biosynthesis'], ['purine deoxyribonucleosides degradation I', '4-deoxy-L-threo-hex-4-enopyranuronate degradation', 'L-homocysteine biosynthesis', 'adenine and adenosine salvage III', 'purine deoxyribonucleosides degradation II'], ['guanosine nucleotides degradation II', 'laminaribiose degradation', 'adenosine nucleotides degradation I', 'guanosine nucleotides degradation III', 'anhydromuropeptides recycling I'], ['betacyanin biosynthesis (via dopamine)', 'aminopropanol phosphate biosynthesis I', 'benzene degradation', '1,4-dimethylbenzene degradation to 4-methylbenzoate', '(3E)-4,8-dimethylnona-1,3,7-triene biosynthesis I'], ['isorenieratene biosynthesis I (actinobacteria)', 'spongiadioxin C biosynthesis', 'polybrominated dihydroxylated diphenyl ethers biosynthesis', 'fungal bioluminescence', 'psilocybin biosynthesis'], ['L-valine degradation III (oxidative Stickland reaction)', 'valproate &beta;-oxidation', 'L-isoleucine degradation III (oxidative Stickland reaction)', 'L-alanine degradation VI (reductive Stickland reaction)', 'L-leucine degradation V (oxidative Stickland reaction)'], ['spermine biosynthesis', 'L-arginine degradation III (arginine decarboxylase/agmatinase pathway)', 'L-arginine degradation X (arginine monooxygenase pathway)', 'linezolid resistance', 'putrescine biosynthesis I'], ['methyl ketone biosynthesis (engineered)', '4-amino-3-hydroxybenzoate degradation', '4-hydroxyacetophenone degradation', 'GDP-L-fucose biosynthesis II (from L-fucose)', 'brassinosteroid biosynthesis I'], ['1,5-anhydrofructose degradation', '(-)-camphor biosynthesis', 'nicotine degradation II (pyrrolidine pathway)', 'L-pyrrolysine biosynthesis', '(+)-camphor biosynthesis'], ['naringenin glycoside biosynthesis', 'chlorophyll a degradation I', 'L-glutamate degradation VI (to pyruvate)', 'L-methionine degradation III', 'chlorophyll a biosynthesis I'], ['baumannoferrin biosynthesis', 'acinetobactin biosynthesis', 'anguibactin biosynthesis', 'oxalate degradation VI', 'vanchrobactin biosynthesis'], ['rhizobitoxine biosynthesis', 'Escherichia coli serotype O9a O-antigen biosynthesis', 'formaldehyde oxidation V (bacillithiol-dependent)', 'homofuraneol biosynthesis', '(2S,3E)-2-amino-4-methoxy-but-3-enoate biosynthesis'], ['apigenin glycosides biosynthesis', 'acyl carrier protein metabolism', 'baruol biosynthesis', '(3E)-4,8-dimethylnona-1,3,7-triene biosynthesis II', 'amygdalin and prunasin degradation'], ['glycolysis V (Pyrococcus)', 'benzoyl-CoA degradation III (anaerobic)', 'aldoxime degradation', 'orcinol degradation', 'resorcinol degradation'], ['N6-L-threonylcarbamoyladenosine37-modified tRNA biosynthesis', 'cyclopropane fatty acid (CFA) biosynthesis', 'D-gluconate degradation', 'fructose degradation', 'L-threonine biosynthesis'], ['A series fagopyritols biosynthesis', '&alpha;-amyrin biosynthesis', 'punicate biosynthesis', 'B series fagopyritols biosynthesis', '&alpha;-eleostearate biosynthesis'], ['sucrose biosynthesis II', 'myo-inositol degradation II', 'mycocyclosin biosynthesis', "inosine-5'-phosphate biosynthesis III", 'alkylnitronates degradation'], ['methanogenesis from tetramethylammonium', 'methanogenesis from methanethiol', 'salvianin biosynthesis', 'methanogenesis from methylthiopropanoate', 'glucosinolate activation'], ['complex N-linked glycan biosynthesis (plants)', 'archaeosine biosynthesis II', 'protein O-mannosylation II (mammals, core M1 and core M2)', 'rubber degradation I', 'protein O-mannosylation I (yeast)'], ['hentriaconta-3,6,9,12,15,19,22,25,28-nonaene biosynthesis', 'paromamine biosynthesis II', 'terminal olefins biosynthesis II', "UDP-N,N'-diacetylbacillosamine biosynthesis", 'gentamicin biosynthesis'], ['cyclobis-(1&rarr;6)-&alpha;-nigerosyl degradation', 'ABH and Lewis epitopes biosynthesis from type 2 precursor disaccharide', 'biosynthesis of Lewis epitopes (H. pylori)', 'ABH and Lewis epitopes biosynthesis from type 1 precursor disaccharide', 'glycolipid desaturation'], ['nitrate reduction III (dissimilatory)', 'pyrimidine ribonucleosides degradation', 'putrescine degradation II', 'protocatechuate degradation II (ortho-cleavage pathway)', 'L-proline degradation I'], ["3,3'-thiodipropanoate degradation", 'cyanidin 3,7-diglucoside polyacylation biosynthesis', 'N-methylanthraniloyl-&beta;-D-glucopyranose biosynthesis', "3,3'-disulfanediyldipropannoate degradation", '2-O-acetyl-3-O-trans-coutarate biosynthesis'], ['trigonelline biosynthesis', 'polymyxin A biosynthesis', 'glycerophosphodiester degradation', 'putrescine degradation III', 'serotonin degradation'], ['hydrogen production VI', 'salicin biosynthesis', 'rhamnogalacturonan type I degradation I', "4,4'-diapolycopenedioate biosynthesis", 'hydrogen production V'], ['quercetin glucoside biosynthesis (Allium)', 'rutin degradation (plants)', 'quercetin glucoside degradation (Allium)', 'L-glucose degradation', 'CMP-legionaminate biosynthesis II'], ['4-hydroxy-4-methyl-L-glutamate biosynthesis', '4-methylphenol degradation to protocatechuate', '2,5-xylenol and 3,5-xylenol degradation', '2,4-xylenol degradation to protocatechuate', 'sch210971 and sch210972 biosynthesis'], ['dTDP-4-O-demethyl-&beta;-L-noviose biosynthesis', '3-amino-4,7-dihydroxy-coumarin biosynthesis', 'oleate &beta;-oxidation (reductase-dependent, yeast)', '3-dimethylallyl-4-hydroxybenzoate biosynthesis', 'estradiol biosynthesis II'], ['UDP-N-acetyl-D-glucosamine biosynthesis I', 'L-asparagine biosynthesis III (tRNA-dependent)', 'S-adenosyl-L-methionine salvage II', 'CMP-3-deoxy-D-manno-octulosonate biosynthesis', 'cadaverine biosynthesis'], ['oleanolate biosynthesis', '2&alpha;,7&beta;-dihydroxylation of taxusin', 'glycyrrhetinate biosynthesis', 'fumigaclavine biosynthesis', 'esculetin modification'], ['CDP-4-dehydro-3,6-dideoxy-D-glucose biosynthesis', 'fluoroacetate degradation', 'volatile esters biosynthesis (during fruit ripening)', 'heme b biosynthesis V (aerobic)', 'heme b biosynthesis II (oxygen-independent)'], ['phosphatidylcholine resynthesis via glycerophosphocholine', '1,4-dihydroxy-6-naphthoate biosynthesis II', 'thiamine triphosphate metabolism', 'demethylmenaquinol-6 biosynthesis II', '1,4-dihydroxy-6-naphthoate biosynthesis I'], ['pyruvate fermentation to ethanol II', 'pentagalloylglucose biosynthesis', 'cornusiin E biosynthesis', '6-methoxypodophyllotoxin biosynthesis', 'gallotannin biosynthesis'], ['L-lysine degradation IX', 'sulfite oxidation IV (sulfite oxidase)', 'taurine biosynthesis I', 'carbon disulfide oxidation II (aerobic)', 'L-cysteine degradation III'], ['catechol degradation to &beta;-ketoadipate', 'benzoyl-CoA degradation II (anaerobic)', 'camalexin biosynthesis', '3,8-divinyl-chlorophyllide a biosynthesis I (aerobic, light-dependent)', 'L-carnitine degradation I'], ['folate transformations III (E. coli)', 'D-galactose detoxification', 'L-histidine degradation VI', 'L-histidine degradation III', 'L-alanine degradation II (to D-lactate)'], ['pulcherrimin biosynthesis', 'trehalose biosynthesis II', 'fructan degradation', 'bacillithiol biosynthesis', 'L-ascorbate biosynthesis I (plants, L-galactose pathway)'], ['pelargonidin conjugates biosynthesis', 'cannabinoid biosynthesis', 'acyl-[acyl-carrier protein] thioesterase pathway', 'fatty acid &beta;-oxidation III (unsaturated, odd number)', 'fatty acid &beta;-oxidation IV (unsaturated, even number)'], ['yatein biosynthesis II', '2,4-dinitroanisole degradation', '2,4,6-trinitrophenol and 2,4-dinitrophenol degradation', 'phospholipid desaturation', 'bacilysin biosynthesis'], ['methylsalicylate degradation', "pyridoxal 5'-phosphate biosynthesis II", 'glycine betaine degradation I', 'benzoate degradation II (aerobic and anaerobic)', 'NAD(P)/NADPH interconversion'], ['calendate biosynthesis', 'petroselinate biosynthesis', 'palmitoleate biosynthesis II (plants and bacteria)', 'carbon tetrachloride degradation I', 'dimorphecolate biosynthesis'], ['thiazole biosynthesis I (facultative anaerobic bacteria) with tautomerase', 'menaquinol oxidase (cytochrom aa3-600)', 'Extracellular galactan(2n) degradation', 'F420 Biosynthesis until 3 glutamine residues', 'H4SPT-SYN'], ['isovitexin glycosides biosynthesis', '2,3-trans-flavanols biosynthesis', 'nitrilotriacetate degradation', 'glucosinolate biosynthesis from tryptophan', 'capsiconiate biosynthesis'], ['tetrahydromonapterin biosynthesis', 'curcumin degradation', 'nitrate reduction VIII (dissimilatory)', 'uracil degradation III', 'tRNA processing'], ['sphingomyelin metabolism', 'phosphopantothenate biosynthesis II', '&beta;-alanine biosynthesis I', 'sphingosine and sphingosine-1-phosphate metabolism', 'berberine biosynthesis'], ['glucosylglycerol biosynthesis', 'glycogen biosynthesis III (from &alpha;-maltose 1-phosphate)', 'glucosinolate biosynthesis from tyrosine', 'protein NEDDylation', 'tRNA-uridine 2-thiolation (thermophilic bacteria)'], ['3-methyl-branched fatty acid &alpha;-oxidation', 'ceramide degradation by &alpha;-oxidation', 'sulfolactate degradation III', '15-epi-lipoxin biosynthesis', 'lipoxin biosynthesis'], ['heme degradation IV', 'heme degradation III', 'neolacto-series glycosphingolipids biosynthesis', 'UDP-yelosamine biosynthesis', 'heme degradation II'], ['fluoroacetate and fluorothreonine biosynthesis', 'labdane-type diterpenes biosynthesis', 'glycolate and glyoxylate degradation III', 'rhamnolipid biosynthesis', 'juvenile hormone III biosynthesis II'], ['D-carnitine degradation I', 'acetone degradation III (to propane-1,2-diol)', 'phosphatidylcholine biosynthesis VII', 'gentisate degradation II', 'benzoyl-&beta;-D-glucopyranose biosynthesis'], ['sterculate biosynthesis', '6-methoxymellein biosynthesis', 'nitrate reduction VI (assimilatory)', 'ethylbenzene degradation (anaerobic)', 'UDP-&alpha;-D-glucuronate biosynthesis (from myo-inositol)'], ['tetradecanoate biosynthesis (mitochondria)', 'anteiso-branched-chain fatty acid biosynthesis', 'even iso-branched-chain fatty acid biosynthesis', 'octanoyl-[acyl-carrier protein] biosynthesis (mitochondria, yeast)', 'odd iso-branched-chain fatty acid biosynthesis'], ['chlorzoxazone degradation', 'prunasin and amygdalin biosynthesis', 'Amaryllidacea alkaloids biosynthesis', 'juglone degradation', 'tunicamycin biosynthesis'], ['oxalate degradation III', 'Fe(II) oxidation', 'D-galactose degradation IV', 'oxalate degradation V', 'plaunotol biosynthesis'], ['androgen biosynthesis', 'mineralocorticoid biosynthesis', 'sulfolactate degradation II', 'glucocorticoid biosynthesis', 'estradiol biosynthesis I (via estrone)'], ['methanol oxidation to formaldehyde IV', 'vitamin B6 degradation', 'reductive monocarboxylic acid cycle', 'paraoxon degradation', 'L-arabinose degradation III'], ['4-aminophenol degradation', 'taxiphyllin biosynthesis', 'triethylamine degradation', '2-methylisoborneol biosynthesis', 'geodin biosynthesis'], ['viridicatumtoxin biosynthesis', 'glycogen degradation III (via anhydrofructose)', 'protein N-glycosylation (Haloferax volcanii)', 'protein N-glycosylation (Methanococcus voltae)', 'tryptoquialanine biosynthesis'], ['(4Z,7Z,10Z,13Z,16Z)-docosa-4,7,10,13,16-pentaenoate biosynthesis II (4-desaturase)', 'arachidonate biosynthesis V (8-detaturase, mammals)', '5,6-dimethylbenzimidazole biosynthesis II (anaerobic)', '(4Z,7Z,10Z,13Z,16Z)-docosapentaenoate biosynthesis (6-desaturase)', 'docosahexaenoate biosynthesis IV (4-desaturase, mammals)'], ['elloramycin biosynthesis', 'cyclooctatin biosynthesis', 'tetracenomycin C biosynthesis', 'oryzalide A biosynthesis', 'phytocassanes biosynthesis, shared reactions'], ['holomycin biosynthesis', '10,13-epoxy-11-methyl-octadecadienoate biosynthesis', 'zwittermicin A biosynthesis', 'bikaverin biosynthesis', '8-O-methylfusarubin biosynthesis'], ['dTDP-L-daunosamine biosynthesis', '6-methylpretetramide biosynthesis', 'tetracycline and oxytetracycline biosynthesis', 'thiosulfate disproportionation III (quinone)', 'chlorotetracycline biosynthesis'], ['phycoviolobilin biosynthesis', 'phycourobilin biosynthesis', 'nitrogen fixation II (flavodoxin)', 'phycoerythrobilin biosynthesis II', 'mercaptosuccinate degradation']]
    def clusters_to_df(data):
        rows = []
        for i, sublist in enumerate(data, start=1):
            cluster_name = f"Cluster {i}"
            for species in sublist:
                # remove s__ prefix for display
                clean_species = species.replace("s__", "")
                rows.append({"Cluster": cluster_name, "Species": clean_species, "Value": 1})
        return pd.DataFrame(rows)

    df_0_4 = clusters_to_df(cluster_data_0_4)
    df_0_6 = clusters_to_df(cluster_data_0_6)
    df_0_5 = clusters_to_df(cluster_data_0_5)


    try:
        fig_0_4 = px.sunburst(df_0_4, path=["Cluster", "Species"], values="Value", title="Threshold 0.4")
        fig_0_4.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_4 = pio.to_html(
            fig_0_4,
            full_html=False,
            include_plotlyjs=False,
            config={"responsive": True},
            div_id="sunburst_04"
        )
    except:
        sunburst_html_0_4 = ""

    try:
        fig_0_6 = px.sunburst(df_0_6, path=["Cluster", "Species"], values="Value", title="Threshold 0.6")
        fig_0_6.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_6 = pio.to_html(
            fig_0_6,
            full_html=False,
            include_plotlyjs=False,
            config={"responsive": True},
            div_id="sunburst_06"
        )
    except:
        sunburst_html_0_6 = ""

    try:
        fig_0_5 = px.sunburst(df_0_5, path=["Cluster", "Species"], values="Value", title="Threshold 0.5")
        fig_0_5.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_5 = pio.to_html(
            fig_0_5,
            full_html=False,
            include_plotlyjs=False,
            config={"responsive": True},
            div_id="sunburst_05"
        )
    except:
        sunburst_html_0_5 = ""
    # 4) Render template
    return render(
        request,
        f"{host_type}/functionnal2.html",  # e.g. "isabrownv2/bacterien.html"
        {
            "host_type": host_type.title(),
            "data_type": "functionnal",
            "description": "Top 100 displayed only. Gene info from Ensembl REST.",
            "tissue_types": list(tissue_files_functionnel.keys()),
            "sunburst_html_0_4": sunburst_html_0_4,
            "sunburst_html_0_6": sunburst_html_0_6,
            "sunburst_html_0_5": sunburst_html_0_5,

        }
    )


def molecule_data_analysisv2(request, host_type='isabrownv2'):
    """
    1) Creates two sunbursts (threshold 0.5 & 0.6).
    2) Handles AJAX for single-var & multi-var filtering => returns top 100 in JSON.
    3) No server-side gene info or CSV download. The gene info & CSV are fully client-side.
    """
    # 1) Load data for sunburst
    if host_type == "ross":
        big_tsv_path = os.path.join(
            settings.BASE_DIR, "Avapp", "static", "Avapp", "csv",
            "Sylph_MoARossFull_estimatedCounts.tsv"
        )
    else:
        big_tsv_path = os.path.join(
            settings.BASE_DIR, "Avapp", "static", "Avapp", "csv",
            "Sylph_MoAIsaFull_estimatedCounts.tsv"
        )

    try:
        df_sunburst = pd.read_csv(big_tsv_path, sep="\t")
        # Suppose 'Taxa' has a semi-colon separated taxonomy chain
        splitted = df_sunburst["Taxa"].str.split(";", expand=True)
        # Possibly up to 7 levels
        taxonomy_levels = ["Domain", "Phylum", "Class", "Order", "Family", "Genus", "Species"]
        splitted.columns = taxonomy_levels[:splitted.shape[1]]
        df_sunburst = pd.concat([splitted, df_sunburst.drop("Taxa", axis=1)], axis=1)
    except Exception as e:
        return JsonResponse({"error": f"Error loading sunburst data: {e}"}, status=500)

    # 2) Handle AJAX (single-var, multi-var) => top 100
    if request.headers.get("x-requested-with") == "XMLHttpRequest":

        # (A) load_tissue => returns list of variables
        if "load_tissue" in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files_molecule:
                return JsonResponse({"error": f"Invalid tissue: {tissue}"}, status=400)
            try:
                csv_path = os.path.join(
                    settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                    tissue_files_molecule[tissue]
                )
                df_small = pd.read_csv(csv_path)
                variables = df_small.columns[2:].tolist()
                return JsonResponse({"variables": variables})
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV: {e}"}, status=500)

        # (B) Single-var => includes fetch_min_max + filter
        elif "multi_variable" not in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files_molecule:
                return JsonResponse({"results": [], "error": "Missing or invalid tissue."}, status=400)
            csv_path = os.path.join(
                settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                tissue_files_molecule[tissue]
            )

            try:
                df_all = pd.read_csv(csv_path)
                variables = df_all.columns[2:].tolist()
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV: {e}"}, status=500)

            selected_variable = request.GET.get("variable", variables[0] if variables else None)
            if selected_variable not in variables:
                return JsonResponse({"results": [], "error": "Invalid variable selected."}, status=400)

            # B1) fetch_min_max
            if "fetch_min_max" in request.GET:
                try:
                    col_vals = df_all[selected_variable].dropna()
                    return JsonResponse({
                        "min_correlation": float(col_vals.min()),
                        "max_correlation": float(col_vals.max()),
                    })
                except Exception as e:
                    return JsonResponse({"error": f"Error fetching min/max: {e}"}, status=500)

            # B2) filter => top 100
            try:
                correlation_min = float(request.GET.get("correlation_min", -1))
                correlation_max = float(request.GET.get("correlation_max", 1))
                min_accuracy = float(request.GET.get("accuracy", 0))

                if correlation_min > correlation_max:
                    return JsonResponse({"error": "Min correlation cannot exceed max correlation."}, status=400)

                filtered = df_all[
                    (df_all["accuracy"] >= min_accuracy)
                    & (df_all[selected_variable] >= correlation_min)
                    & (df_all[selected_variable] <= correlation_max)
                ]
                if filtered.empty:
                    return JsonResponse({"results": [], "total_count": 0})

                filtered.sort_values(by=selected_variable, ascending=False, inplace=True)
                total_count = len(filtered)
                top_100 = filtered.head(100)

                first_col = df_all.columns[0]
                results_list = []
                for _, row in top_100.iterrows():
                    results_list.append({
                        "var1": row[first_col],
                        "var2": selected_variable,
                        "accuracy": row["accuracy"],
                        "correlation": row[selected_variable]
                    })

                return JsonResponse({"results": results_list, "total_count": total_count})
            except Exception as e:
                return JsonResponse({"error": f"Error during single-var filter: {e}"}, status=500)

        # (C) Multi-var => top 100
        elif "multi_variable" in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files_molecule:
                return JsonResponse({"results": [], "error": "Missing or invalid tissue."}, status=400)

            variables = request.GET.getlist("variables[]")
            if not variables:
                return JsonResponse({"results": [], "error": "No variables selected."}, status=400)

            csv_path = os.path.join(
                settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                tissue_files_molecule[tissue]
            )
            try:
                df_all = pd.read_csv(csv_path)
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV file: {e}"}, status=500)

            try:
                correlation_min = float(request.GET.get("correlation_min", -1))
                correlation_max = float(request.GET.get("correlation_max", 1))
                min_accuracy = float(request.GET.get("accuracy", 0))
                if correlation_min > correlation_max:
                    return JsonResponse({"error": "Min correlation cannot exceed max correlation."}, status=400)

                filtered_parts = []
                first_col = df_all.columns[0]
                for var in variables:
                    if var not in df_all.columns:
                        continue
                    sub = df_all[
                        (df_all["accuracy"] >= min_accuracy)
                        & (df_all[var] >= correlation_min)
                        & (df_all[var] <= correlation_max)
                    ].copy()
                    if not sub.empty:
                        sub["var2"] = var
                        filtered_parts.append(sub)

                if not filtered_parts:
                    return JsonResponse({"results": [], "total_count": 0})

                combined = pd.concat(filtered_parts, ignore_index=True)
                corvals = []
                for _, row in combined.iterrows():
                    corvals.append(row[row["var2"]])
                combined["correlation"] = corvals

                combined.drop_duplicates(subset=[first_col, "var2"], inplace=True)
                combined.sort_values(by="correlation", ascending=False, inplace=True)
                total_count = len(combined)

                top_100 = combined.head(100)
                results_list = []
                for _, row in top_100.iterrows():
                    results_list.append({
                        "var1": row[first_col],
                        "var2": row["var2"],
                        "accuracy": row["accuracy"],
                        "correlation": row["correlation"]
                    })

                return JsonResponse({"results": results_list, "total_count": total_count})
            except Exception as e:
                return JsonResponse({"error": f"Error during multi-var filter: {e}"}, status=500)

        # If none matched
        return JsonResponse({"error":"No recognized AJAX action."}, status=400)

    # 3) Build the sunbursts for 0.5 & 0.6
    cluster_data_0_5 =  [['Proline', 'Indoline_479', 'Piperidine_556', 'Deoxyguanosine', 'Thymidine', 'H01040'], ['X00736', 'X00394', 'H00524', 'H00277', 'X00151', 'H00079'], ['META-ETHYLPHENOL', 'Propyl gallate', '4-Vinylphenol', 'H00768', '3-Phenyllactic acid'], ['H00180', 'Urobilin', 'X01002', 'X00220', 'H00860'], ['Malic acid', 'Xanthine', 'Uracil', 'Thiamine', 'Pyruvic acid']]

    cluster_data_0_4 = [['Urobilin', 'Propyl gallate', '3-Phenyllactic acid', 'H00180', 'META-ETHYLPHENOL', 'X01002', 'X00220', 'H00860', '4-Vinylphenol', 'H00768'], ['Tetradecanedioic acid', 'X00087', 'Indole-3-carboxyaldehyde', '1-Aminocyclohexanecarboxylic acid', 'X00846', 'H00434', 'H02578', 'H02435'], ['H02583', '(+)-Costunolide_257', 'N8-Acetylspermidine', 'H00798', 'X00107', 'X00309', '4-Hydroxyhygric acid'], ['Stachyose', 'X02359', 'X03645', 'Creatinine', 'Hexose trimer', 'Pinitol', 'H03399'], ['Lactic acid', 'Ornithine', 'Arginine', 'Betaine', 'Creatine', 'Lysine', 'Carnosine'], ['X00842', 'Norepinephrine', 'DOPA', 'X10785', 'H03047', 'X03140'], ['H00890', 'X01182', '3-Hydroxybenzoic acid', 'X00637', 'H01305', '3-Hydroxycinnamic acid'], ['Proline', 'Indoline_479', 'Piperidine_556', 'Deoxyguanosine', 'Thymidine', 'H01040'], ['X00736', 'X00394', 'H00524', 'H00277', 'X00151', 'H00079'], ['Isoliquiritigenin', 'X04317', 'H00181', 'Verrucarol', 'X00590'], ['5-Hydroxyindole', 'Indole-3-glyoxylic acid', 'N-Acetylmethionine', 'X00146', 'Puerarin'], ['X06269', 'H00096', 'Glycylleucine', 'H00253', 'H02415'], ['Malic acid', 'Xanthine', 'Uracil', 'Thiamine', 'Pyruvic acid'], ['Acetylcarnitine', 'H00346', 'X00757', 'X00246', 'H01009']]

    cluster_data_0_3 = [['Xanthine', 'Allopurinol_421', '2-Picolinic acid', '3-Methyl-2-oxovaleric acid', 'Acetylmuramic acid', 'Uracil', 'Pyruvic acid', 'Hypoxanthine', 'Malic acid', 'Urocanic acid', 'Nicotinic acid ribonucleoside', 'Thiamine', 'N-(5-Aminopentyl)acetamide_184'], ['H00890', 'X01182', 'H00417', '3-Hydroxycinnamic acid', '3-Hydroxybenzoic acid', 'X00637', 'H00743', 'H01305', 'gamma-Aminobutyric acid', 'X00639'], ['Urobilin', 'Propyl gallate', '3-Phenyllactic acid', 'H00180', 'META-ETHYLPHENOL', 'X01002', 'X00220', 'H00860', '4-Vinylphenol', 'H00768'], ['X04860', 'H03558', 'gamma-Caprolactone', 'Vanillin', 'X04183', 'X05705', 'X08701', 'X06691', 'X05456'], ['X00043', '3-Methylglutaconic acid', 'H00346', 'X00455', 'Acetylcarnitine', 'X00246', 'X00757', 'H01009', 'beta-Muricholic acid'], ['5-Hydroxyindole', 'Indole-3-lactic acid', 'N-Acetylmethionine', 'X00225', 'Indole-3-glyoxylic acid', 'Puerarin', '5,6-Dihydrothymine', 'H00544', 'X00146'], ['X04317', 'H00181', 'Isoliquiritigenin', 'Verrucarol', 'Prostaglandin E2', 'scyllo-Inositol', 'Butein', '2-Oxo-3-phenylpropanoic acid', 'X00590'], ['Catechin', 'X00980', 'X09476', 'Gomisin J', 'X00382', 'Oridonin', '7beta-Hydroxylathyrol', 'H03845', 'X00100'], ['Tetradecanedioic acid', 'X00087', 'Indole-3-carboxyaldehyde', '1-Aminocyclohexanecarboxylic acid', 'X00846', 'H00434', 'H02578', 'H02435'], ['X06269', 'Leucylalanine', 'H00096', 'X00599', 'Glycylleucine', 'H00253', 'H02415', 'H01934'], ['Kirenol', 'Hexahydrocurcumin', 'X04156', 'H02615', 'N-Acetylhistidine', 'X05146', 'X08351', 'X00731'], ['Lactic acid', 'Ornithine', 'Arginine', 'Betaine', 'Creatine', 'Lysine', 'Carnosine'], ['X00508', 'X05149', 'H00162', 'H12871', 'H00117', 'H02755', 'Indole-3-carbinol'], ['N-Acetyl-5-hydroxytryptamine', 'Tryptamine', 'X08212', 'Inulicin', '2-Methylbutyrylglycine', 'H00207', 'Salicylic acid'], ['Leucine', 'Phosphocholine', 'Gulonic acid gamma-lactone', 'X00269', 'Piperidine_557', 'X03698', 'Isoleucine'], ['Stachyose', 'X02359', 'X03645', 'Creatinine', 'Hexose trimer', 'Pinitol', 'H03399'], ['H02583', '(+)-Costunolide_257', 'N8-Acetylspermidine', 'H00798', 'X00107', 'X00309', '4-Hydroxyhygric acid'], ['X00138', '5-Hydroxytryptamine creatinine sulfate monohydrate', 'Patulin_548', 'H00171', 'X04612', 'Pipecolinic acid', 'H00553'], ['H01685', 'H02971', 'H00025', 'H00265', 'H02475', 'Fucose', 'H00762'], ['2-Hydroxyphenylacetic acid', 'X07085', 'X01114', 'H01154', 'Vanillyl alcohol', 'X01498'], ['X00842', 'Norepinephrine', 'DOPA', 'X10785', 'H03047', 'X03140'], ['Proline', 'Indoline_479', 'Piperidine_556', 'Deoxyguanosine', 'Thymidine', 'H01040'], ['SL00115', 'X14123', 'X01733', 'X05003', 'H02794', 'X02808'], ['Anserine/Homocarnosine', '7-Methylguanine', 'Caffeic acid', 'Ribulose 5-phosphate', 'H03322', 'D-arabinose'], ['X00200', 'X01850', 'Imidazoleacetic acid', 'X01454', 'H00722', 'Citraconic acid'], ['Daurisoline', 'N-Acetylputrescine', 'X00018', 'X01275', 'Sulfuretin', 'Quinic acid'], ['Allopurinol_118', 'Phenylalanine', 'Inosine', 'Propionylcarnitine', 'Butyrylcarnitine', 'Indoline_480'], ['X00736', 'X00394', 'H00524', 'H00277', 'X00151', 'H00079'], ['X00905', 'Veratridine', 'H02163', 'H04645', 'X04102'], ['X06478', 'X14611', 'X04952', 'X00568', 'X06276'], ['Cyclo(L-Phe-L-Pro)', 'X02378', 'X01038', 'X01185', 'X05178'], ['1-Aminocyclopropanecarboxylic acid', 'N-Methylaspartic acid', '3-Hydroxybutyric acid', 'X01703', 'Valerylcarnitine'], ['O-Desmethylangolensin_545', 'X01578', 'H00035', 'Ononetin', 'Pantothenic acid'], ['X01099', 'Dimethylmalonic acid', 'H02108', 'H01407', 'X10202'], ['H03435', 'Argininosuccinic acid', 'H07398', 'X07540', 'H01019'], ['a Zearalenol', 'Blinin', 'X13463', 'X04161', 'Ingenol'], ['X03335', 'Transtorine', 'X00672', 'H01727', '3-Hydroxy-2-methyl-4-pyrone'], ['X01909', 'H10665', 'Isofraxidin', 'H02257', '5-Methyluridine']]

    cluster_data_0_2 =[['Tetradecanedioic acid', 'Hypaconitine', 'H02755', 'H02200', 'N1-Methyl-2-pyridone-5-carboxamide', 'X00508', 'X00059', 'H02233', 'H00434', 'H02578', 'X03124', 'X05149', 'Succinic acid', 'X00087', 'Indole-3-carboxyaldehyde', '1-Aminocyclohexanecarboxylic acid', 'Indole-3-carbinol', 'X00846', 'X00409', 'H00162', 'H12871', 'H00117', 'H02435'], ['Leucine', 'Phosphocholine', 'X00269', 'Betaine', 'Inosine', 'X03698', 'Propionylcarnitine', 'Carnosine', 'Allopurinol_118', 'Phenylalanine', 'Gulonic acid gamma-lactone', 'Isoleucine', 'Creatine', 'Butyrylcarnitine', 'Indoline_480', 'Lactic acid', 'Ornithine', 'Arginine', 'Piperidine_557', 'Lysine'], ['Caffeic acid', 'X00018', '4-Hydroxyhygric acid', 'X01275', 'D-arabinose', '(+)-Costunolide_257', 'N8-Acetylspermidine', 'H00798', 'N-Acetylputrescine', 'H03322', 'X00309', 'Daurisoline', 'Quinic acid', 'H02583', 'Anserine/Homocarnosine', '7-Methylguanine', 'X00107', 'Ribulose 5-phosphate', 'Sulfuretin'], ['2-Picolinic acid', '3-Methyl-2-oxovaleric acid', 'Uracil', 'Acetylmuramic acid', 'Hypoxanthine', 'Nicotinic acid ribonucleoside', 'Urocanic acid', 'X00394', 'X00151', 'Xanthine', 'H00524', 'Allopurinol_421', 'Pyruvic acid', 'H00079', 'Malic acid', 'X00736', 'Thiamine', 'H00277', 'N-(5-Aminopentyl)acetamide_184'], ['X00138', 'N-Acetyl-5-hydroxytryptamine', 'Tryptamine', '2-Methylbutyrylglycine', 'Patulin_548', 'H00171', 'H00207', 'Diethanolamine', '5-Hydroxytryptamine creatinine sulfate monohydrate', 'X00509', 'ectoine', 'X04612', 'Pipecolinic acid', 'Salicylic acid', 'H00553', 'Inulicin', 'Nordihydroguaiaretic acid', 'X08212'], ['H00890', 'X01182', 'H00417', '3-Hydroxycinnamic acid', '3-Hydroxybenzoic acid', 'X00637', 'H00579', 'X00514', 'H01305', 'gamma-Aminobutyric acid', 'X00639', 'Lotaustralin', 'beta-Hydroxyisovaleric acid', 'H00743', 'H00198', 'X03337', 'H00287'], ['X00462', 'Piperidine_556', '2-Aminoadipic acid', 'Deoxyuridine', '5-Aminovaleric acid', 'Proline', 'Cytosine', 'H00595', 'Thymidine', 'Lauramidopropyl betaine', 'Indoline_479', 'H00520', 'H01040', 'N-Acetylarginine', 'Deoxyguanosine', 'H00630'], ['Methyl gallate', 'Genipin', 'H03399', 'X00587', 'X02359', 'Hexose trimer', 'Stachyose', 'Proline/(R)-pyrrolidine-2-carboxylic acid', 'N-Acetylneuraminic acid', 'H00202', 'X03645', 'Creatinine', 'Pinitol', 'SL00418', 'L-Quebrachitol', 'H01387'], ['Catechin', 'X01738', 'X00980', 'X00708', 'X09476', 'Dihydrocucurbitacin B', 'Deoxyelephantopin', 'Enterolactone_458', 'Gomisin J', 'X00382', 'Oridonin', 'Enterolactone_459', '7beta-Hydroxylathyrol', 'H03845', 'X00100'], ['X02114', '2-Hydroxy-3-methylbutyric acid', 'Prolylhydroxyproline', 'H00823', 'Glucuronic acid', 'Pyroglutamic acid', '2-Hydroxy-2-methylbutanoic acid', 'N-Acetylgalactosamine', 'N-Acetylmannosamine', 'Adenosine', 'Galactosamine', 'Diaminopimelic acid', '2-Hydroxyisocaproic acid', 'N-Acetylornithine'], ['X07545', 'X03140', 'H03047', 'X00061', 'X00842', 'Norepinephrine', 'DOPA', 'X14186', 'X10785', 'Castanospermine', 'H00423', 'Bufotalin', 'X06638'], ['DL-Glutamine', 'Taurine', 'Alanine', 'Choline', 'Serine', 'H00270', 'Threonine', 'Asparagine', 'Histidine', 'Glutamine', 'X01010', 'Tryptophan'], ['H02971', 'H00025', 'H01685', 'H00265', 'Carnitine', 'H00572', 'H02475', 'Fucose', 'N-Acetylaspartic acid', 'H00762', '1-Methyladenosine', 'N-Acetylglutamic acid'], ['Pimelic acid', 'X03659', 'X01155', '4-Hydroxy-2,5-dimethyl-3(2H)-furanone', 'X00844', 'SL00035', 'Bicine', 'X06380', 'Hippuric acid', '3-hydroxy-4,5-dimethyl-3(5H)-furanone', 'X01565'], ['Rhodojaponin III', 'X01347', 'X01033', 'Pentoxifylline', 'X02741', 'Quinine', 'X00336', 'X05089', 'X05359', 'X12625', 'X00583'], ['H05669', 'H01450', 'X05466', 'X00927', 'H08607', 'X01605', 'X04291', 'H02554', 'H11880', 'X00775'], ['X05178', 'X06276', 'X00568', 'Cyclo(L-Phe-L-Pro)', 'X02378', 'X06478', 'X01038', 'X01185', 'X04952', 'X14611'], ['Shikimic acid', 'H05210', 'X02748', 'H03536', 'H00332', 'H01061', 'H05721', 'H02505', 'H02245', 'H03548'], ['H03505', '3,3-Dimethylglutaric acid', 'H00266', 'X05711', 'H04800', 'X01331', 'X02482', 'H00956', 'X02025', 'H03949'], ['X06643', 'X05760', 'H03349', 'X04161', 'H02768', 'a Zearalenol', 'Blinin', 'H02237', 'X13463', 'Ingenol'], ['Urobilin', 'Propyl gallate', '3-Phenyllactic acid', 'H00180', 'META-ETHYLPHENOL', 'X01002', 'X00220', 'H00860', '4-Vinylphenol', 'H00768'], ['X04860', 'H03558', 'gamma-Caprolactone', 'Vanillin', 'X04183', 'X05705', 'X08701', 'X06691', 'X05456'], ['X00022', 'H00534', 'Stachydrine', 'H07398', 'H01019', 'H03435', 'Argininosuccinic acid', 'H00646', 'X07540'], ['X00043', '3-Methylglutaconic acid', 'H00346', 'X00455', 'Acetylcarnitine', 'X00246', 'X00757', 'H01009', 'beta-Muricholic acid'], ['5-Hydroxyindole', 'Indole-3-lactic acid', 'N-Acetylmethionine', 'X00225', 'Indole-3-glyoxylic acid', 'Puerarin', '5,6-Dihydrothymine', 'H00544', 'X00146'], ['X00097', 'Pyridoxine', 'H03896', 'X00224', 'X01099', 'Dimethylmalonic acid', 'H02108', 'H01407', 'X10202'], ['X08198', 'X00041', 'H00930', 'Pinocembrin', 'X01242', 'Asymmetric dimethylarginine', 'X00660', 'SL00194', 'H00488'], ['N-Methylaspartic acid', '3-Hydroxybutyric acid', 'X01703', 'Valerylcarnitine', '1-Aminocyclopropanecarboxylic acid', 'Pyridoxamine', "Pyridoxal 5'-phosphate", 'Methionine', 'Aspartic acid'], ['X04317', 'H00181', 'Isoliquiritigenin', 'Verrucarol', 'Prostaglandin E2', 'scyllo-Inositol', 'Butein', '2-Oxo-3-phenylpropanoic acid', 'X00590'], ['X01909', 'Isofraxidin', 'H00447', 'X03744', 'H06253', 'H10665', 'H02257', '5-Methyluridine', 'H09307'], ['X06269', 'Leucylalanine', 'H00096', 'X00599', 'Glycylleucine', 'H00253', 'H02415', 'H01934'], ['Kirenol', 'Hexahydrocurcumin', 'X04156', 'H02615', 'N-Acetylhistidine', 'X05146', 'X08351', 'X00731'], ['2-Hydroxyphenylacetic acid', 'H01154', 'Vanillyl alcohol', 'X03155', 'X01498', 'X07085', 'X01114', 'Gibberellin A3'], ['X00443', 'X02611', 'H02424', '4-Guanidinobutyric acid', 'X00543', 'X05119', 'SL00091', 'X06373'], ['3-Methylhistidine/ 1-Methylhistidine', 'H00353', 'X01923', 'Acetylagmatine', 'X03182', '3-Indoxylsulfuric acid', 'Trigonelline', 'H00284'], ['delta-Gluconolactone/ delta-Gluconic acid delta-lactone', 'Decursinol', 'Kynurenine', 'X00834', 'N-Methyl-2-pyrrolidone', "4'-O-Methylpyridoxine", 'beta-Alanine'], ['X06608', '4-pyridoxic acid', 'H00543', 'X01683', 'O-Desmethylangolensin_94', 'Indole-3-acetic acid', '4-Hydroxybenzoic acid'], ['H01987', 'Guvacine hydrochloride', 'X01253', 'X00537', 'X02889', 'X00726', 'Traumatic acid'], ['Daidzein', 'Naringenin/Pinobanksin', '4-Hydroxyproline', 'Uridine', 'Glucose', 'Nicotinic acid', 'Pyridoxal'], ['SL00115', 'X14123', 'X01733', 'X05003', 'H02794', 'X02808'], ['X00528', 'Guanosine', 'X04006', 'Valine', 'H00547', 'HY-30220_(S)-2-Hydroxy-3-phenylpropanoic acid'], ['Dopamine', 'Tyrosine', 'H02734', '(+)-Costunolide_258', 'X03614', 'SL00069'], ['X00200', 'X01850', 'Imidazoleacetic acid', 'X01454', 'H00722', 'Citraconic acid'], ['H00517', 'X05938', 'Glaucocalyxin A', 'X01446', '4-Hydroxybenzaldehyde', 'H00451'], ['X00905', 'Veratridine', 'H02163', 'H04645', 'X04102'], ['H00276', 'H03656', 'Hexose dimer', 'Agmatine', 'Guanine'], ['O-Desmethylangolensin_545', 'X01578', 'H00035', 'Ononetin', 'Pantothenic acid'], ['X12234', 'X02147', 'Sebacic acid', 'X09130', 'H01633'], ['X03335', 'Transtorine', 'X00672', 'H01727', '3-Hydroxy-2-methyl-4-pyrone']]


    def clusters_to_df(data):
        rows = []
        for i, sublist in enumerate(data, start=1):
            cluster_name = f"Cluster {i}"
            for species in sublist:
                # remove s__ prefix for display
                clean_species = species.replace("s__", "")
                rows.append({"Cluster": cluster_name, "Species": clean_species, "Value": 1})
        return pd.DataFrame(rows)
    df_0_5 = clusters_to_df(cluster_data_0_5)
    df_0_4 = clusters_to_df(cluster_data_0_4)
    df_0_3 = clusters_to_df(cluster_data_0_3)
    df_0_2 = clusters_to_df(cluster_data_0_2)

    try:
        fig_0_5 = px.sunburst(df_0_5, path=["Cluster", "Species"], values="Value", title="Threshold 0.5")
        fig_0_5.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_5 = pio.to_html(
            fig_0_5,
            full_html=False,
            include_plotlyjs=False,
            config={"responsive": True},
            div_id="sunburst_05"
        )
    except:
        sunburst_html_0_5 = ""

    try:
        fig_0_4 = px.sunburst(df_0_4, path=["Cluster", "Species"], values="Value", title="Threshold 0.4")
        fig_0_4.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_4 = pio.to_html(
            fig_0_4,
            full_html=False,
            include_plotlyjs=False,
            config={"responsive": True},
            div_id="sunburst_04"
        )
    except:
        sunburst_html_0_4 = ""

    try:
        fig_0_3 = px.sunburst(df_0_3, path=["Cluster", "Species"], values="Value", title="Threshold 0.3")
        fig_0_3.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_3 = pio.to_html(
            fig_0_3,
            full_html=False,
            include_plotlyjs=False,
            config={"responsive": True},
            div_id="sunburst_03"
        )
    except:
        sunburst_html_0_3 = ""

    try:
        fig_0_2 = px.sunburst(df_0_2, path=["Cluster", "Species"], values="Value", title="Threshold 0.2")
        fig_0_2.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_2 = pio.to_html(
            fig_0_2,
            full_html=False,
            include_plotlyjs=False,
            config={"responsive": True},
            div_id="sunburst_02"
        )
    except:
        sunburst_html_0_2 = ""
    # 4) Render template
    return render(
        request,
        f"{host_type}/molecule.html",  # e.g. "isabrownv2/bacterien.html"
        {
            "host_type": host_type.title(),
            "data_type": "Molecule",
            "description": "Top 100 displayed only. Gene info from Ensembl REST.",
            "tissue_types": list(tissue_files_molecule.keys()),
            "sunburst_html_0_5": sunburst_html_0_5,
            "sunburst_html_0_4": sunburst_html_0_4,
            "sunburst_html_0_3": sunburst_html_0_3,
            "sunburst_html_0_2": sunburst_html_0_2,

        }
    )



def liver_data_analysisv2(request, host_type='isabrownv2'):
    """
    1) Creates two sunbursts (threshold 0.5 & 0.6).
    2) Handles AJAX for single-var & multi-var filtering => returns top 100 in JSON.
    3) No server-side gene info or CSV download. The gene info & CSV are fully client-side.
    """
    # 1) Load data for sunburst
    if host_type == "ross":
        big_tsv_path = os.path.join(
            settings.BASE_DIR, "Avapp", "static", "Avapp", "csv",
            "Sylph_MoARossFull_estimatedCounts.tsv"
        )
    else:
        big_tsv_path = os.path.join(
            settings.BASE_DIR, "Avapp", "static", "Avapp", "csv",
            "Sylph_MoAIsaFull_estimatedCounts.tsv"
        )

    try:
        df_sunburst = pd.read_csv(big_tsv_path, sep="\t")
        # Suppose 'Taxa' has a semi-colon separated taxonomy chain
        splitted = df_sunburst["Taxa"].str.split(";", expand=True)
        # Possibly up to 7 levels
        taxonomy_levels = ["Domain", "Phylum", "Class", "Order", "Family", "Genus", "Species"]
        splitted.columns = taxonomy_levels[:splitted.shape[1]]
        df_sunburst = pd.concat([splitted, df_sunburst.drop("Taxa", axis=1)], axis=1)
    except Exception as e:
        return JsonResponse({"error": f"Error loading sunburst data: {e}"}, status=500)

    # 2) Handle AJAX (single-var, multi-var) => top 100
    if request.headers.get("x-requested-with") == "XMLHttpRequest":

        # (A) load_tissue => returns list of variables
        if "load_tissue" in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files_liver:
                return JsonResponse({"error": f"Invalid tissue: {tissue}"}, status=400)
            try:
                csv_path = os.path.join(
                    settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                    tissue_files_liver[tissue]
                )
                df_small = pd.read_csv(csv_path)
                variables = df_small.columns[2:].tolist()
                return JsonResponse({"variables": variables})
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV: {e}"}, status=500)

        # (B) Single-var => includes fetch_min_max + filter
        elif "multi_variable" not in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files_liver:
                return JsonResponse({"results": [], "error": "Missing or invalid tissue."}, status=400)
            csv_path = os.path.join(
                settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                tissue_files_liver[tissue]
            )

            try:
                df_all = pd.read_csv(csv_path)
                variables = df_all.columns[2:].tolist()
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV: {e}"}, status=500)

            selected_variable = request.GET.get("variable", variables[0] if variables else None)
            if selected_variable not in variables:
                return JsonResponse({"results": [], "error": "Invalid variable selected."}, status=400)

            # B1) fetch_min_max
            if "fetch_min_max" in request.GET:
                try:
                    col_vals = df_all[selected_variable].dropna()
                    return JsonResponse({
                        "min_correlation": float(col_vals.min()),
                        "max_correlation": float(col_vals.max()),
                    })
                except Exception as e:
                    return JsonResponse({"error": f"Error fetching min/max: {e}"}, status=500)

            # B2) filter => top 100
            try:
                correlation_min = float(request.GET.get("correlation_min", -1))
                correlation_max = float(request.GET.get("correlation_max", 1))
                min_accuracy = float(request.GET.get("accuracy", 0))

                if correlation_min > correlation_max:
                    return JsonResponse({"error": "Min correlation cannot exceed max correlation."}, status=400)

                filtered = df_all[
                    (df_all["accuracy"] >= min_accuracy)
                    & (df_all[selected_variable] >= correlation_min)
                    & (df_all[selected_variable] <= correlation_max)
                ]
                if filtered.empty:
                    return JsonResponse({"results": [], "total_count": 0})

                filtered.sort_values(by=selected_variable, ascending=False, inplace=True)
                total_count = len(filtered)
                top_100 = filtered.head(100)

                first_col = df_all.columns[0]
                results_list = []
                for _, row in top_100.iterrows():
                    results_list.append({
                        "var1": row[first_col],
                        "var2": selected_variable,
                        "accuracy": row["accuracy"],
                        "correlation": row[selected_variable]
                    })

                return JsonResponse({"results": results_list, "total_count": total_count})
            except Exception as e:
                return JsonResponse({"error": f"Error during single-var filter: {e}"}, status=500)

        # (C) Multi-var => top 100
        elif "multi_variable" in request.GET:
            tissue = request.GET.get("tissue")
            if tissue not in tissue_files_liver:
                return JsonResponse({"results": [], "error": "Missing or invalid tissue."}, status=400)

            variables = request.GET.getlist("variables[]")
            if not variables:
                return JsonResponse({"results": [], "error": "No variables selected."}, status=400)

            csv_path = os.path.join(
                settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                tissue_files_liver[tissue]
            )
            try:
                df_all = pd.read_csv(csv_path)
            except Exception as e:
                return JsonResponse({"error": f"Error loading CSV file: {e}"}, status=500)

            try:
                correlation_min = float(request.GET.get("correlation_min", -1))
                correlation_max = float(request.GET.get("correlation_max", 1))
                min_accuracy = float(request.GET.get("accuracy", 0))
                if correlation_min > correlation_max:
                    return JsonResponse({"error": "Min correlation cannot exceed max correlation."}, status=400)

                filtered_parts = []
                first_col = df_all.columns[0]
                for var in variables:
                    if var not in df_all.columns:
                        continue
                    sub = df_all[
                        (df_all["accuracy"] >= min_accuracy)
                        & (df_all[var] >= correlation_min)
                        & (df_all[var] <= correlation_max)
                    ].copy()
                    if not sub.empty:
                        sub["var2"] = var
                        filtered_parts.append(sub)

                if not filtered_parts:
                    return JsonResponse({"results": [], "total_count": 0})

                combined = pd.concat(filtered_parts, ignore_index=True)
                corvals = []
                for _, row in combined.iterrows():
                    corvals.append(row[row["var2"]])
                combined["correlation"] = corvals

                combined.drop_duplicates(subset=[first_col, "var2"], inplace=True)
                combined.sort_values(by="correlation", ascending=False, inplace=True)
                total_count = len(combined)

                top_100 = combined.head(100)
                results_list = []
                for _, row in top_100.iterrows():
                    results_list.append({
                        "var1": row[first_col],
                        "var2": row["var2"],
                        "accuracy": row["accuracy"],
                        "correlation": row["correlation"]
                    })

                return JsonResponse({"results": results_list, "total_count": total_count})
            except Exception as e:
                return JsonResponse({"error": f"Error during multi-var filter: {e}"}, status=500)

        # If none matched
        return JsonResponse({"error":"No recognized AJAX action."}, status=400)

    # 3) Build the sunbursts for 0.5 & 0.6

    cluster_data_0_3 =  [['ENSGALG00010003557', 'ENSGALG00010003644', 'ENSGALG00010003584', 'ENSGALG00010003635', 'ENSGALG00010003643', 'ENSGALG00010003537', 'ENSGALG00010003598', 'ENSGALG00010003640', 'ENSGALG00010003576', 'ENSGALG00010003565', 'ENSGALG00010003614', 'ENSGALG00010003563', 'ENSGALG00010003575', 'ENSGALG00010003613', 'ENSGALG00010003623', 'ENSGALG00010003529'], ['ENSGALG00010004934', 'ENSGALG00010002376', 'ENSGALG00010008023', 'ENSGALG00010022971', 'ENSGALG00010002087', 'ENSGALG00010011456'], ['ENSGALG00010000029', 'ENSGALG00010000024', 'ENSGALG00010000011', 'ENSGALG00010000034', 'ENSGALG00010000023', 'ENSGALG00010000007'], ['ENSGALG00010007983', 'ENSGALG00010010849', 'ENSGALG00010021670', 'ENSGALG00010024961', 'ENSGALG00010021207', 'ENSGALG00010027146'], ['ENSGALG00010025790', 'ENSGALG00010028569', 'ENSGALG00010026982', 'ENSGALG00010014429', 'ENSGALG00010018142', 'ENSGALG00010011348'], ['ENSGALG00010017579', 'ENSGALG00010022050', 'ENSGALG00010017585', 'ENSGALG00010014739', 'ENSGALG00010019072'], ['ENSGALG00010015009', 'ENSGALG00010021627', 'ENSGALG00010023760', 'ENSGALG00010014990', 'ENSGALG00010001837'], ['ENSGALG00010002034', 'ENSGALG00010008134', 'ENSGALG00010004951', 'ENSGALG00010000818', 'ENSGALG00010005507'], ['ENSGALG00010021071', 'ENSGALG00010017848', 'ENSGALG00010003152', 'ENSGALG00010025339', 'ENSGALG00010003154'], ['ENSGALG00010018046', 'ENSGALG00010027175', 'ENSGALG00010016848', 'ENSGALG00010027348', 'ENSGALG00010029401'], ['ENSGALG00010005425', 'ENSGALG00010005499', 'ENSGALG00010024920', 'ENSGALG00010022662', 'ENSGALG00010023131'], ['ENSGALG00010015126', 'ENSGALG00010007916', 'ENSGALG00010021748', 'ENSGALG00010023052', 'ENSGALG00010028179'], ['ENSGALG00010027892', 'ENSGALG00010000571', 'ENSGALG00010027227', 'ENSGALG00010000205', 'ENSGALG00010022042'], ['ENSGALG00010018015', 'ENSGALG00010019441', 'ENSGALG00010028007', 'ENSGALG00010024885', 'ENSGALG00010019282'], ['ENSGALG00010011651', 'ENSGALG00010010906', 'ENSGALG00010007882', 'ENSGALG00010015695', 'ENSGALG00010027178'], ['ENSGALG00010018436', 'ENSGALG00010029384', 'ENSGALG00010023225', 'ENSGALG00010019298', 'ENSGALG00010028176'], ['ENSGALG00010010828', 'ENSGALG00010009498', 'ENSGALG00010012447', 'ENSGALG00010024694', 'ENSGALG00010018453'], ['ENSGALG00010021786', 'ENSGALG00010009016', 'ENSGALG00010017739', 'ENSGALG00010008098', 'ENSGALG00010010270'], ['ENSGALG00010006132', 'ENSGALG00010005407', 'ENSGALG00010009094', 'ENSGALG00010006134', 'ENSGALG00010006275'], ['ENSGALG00010029171', 'ENSGALG00010023179', 'ENSGALG00010020889', 'ENSGALG00010027289', 'ENSGALG00010023821'], ['ENSGALG00010009679', 'ENSGALG00010018583', 'ENSGALG00010028900', 'ENSGALG00010012362', 'ENSGALG00010026320'], ['ENSGALG00010023731', 'ENSGALG00010017815', 'ENSGALG00010004939', 'ENSGALG00010025910', 'ENSGALG00010011025'], ['ENSGALG00010004378', 'ENSGALG00010018519', 'ENSGALG00010018502', 'ENSGALG00010002581', 'ENSGALG00010010635'], ['ENSGALG00010018505', 'ENSGALG00010015795', 'ENSGALG00010016598', 'ENSGALG00010017147', 'ENSGALG00010018401'], ['ENSGALG00010010918', 'ENSGALG00010020343', 'ENSGALG00010000081', 'ENSGALG00010010922', 'ENSGALG00010024325'], ['ENSGALG00010022230', 'ENSGALG00010020080', 'ENSGALG00010022733', 'ENSGALG00010027383', 'ENSGALG00010022751'], ['ENSGALG00010017502', 'ENSGALG00010024229', 'ENSGALG00010015180', 'ENSGALG00010008476', 'ENSGALG00010008410'], ['ENSGALG00010010901', 'ENSGALG00010010475', 'ENSGALG00010028055', 'ENSGALG00010026588', 'ENSGALG00010027080'], ['ENSGALG00010029182', 'ENSGALG00010029705', 'ENSGALG00010026221', 'ENSGALG00010026081', 'ENSGALG00010027328'], ['ENSGALG00010029389', 'ENSGALG00010024883', 'ENSGALG00010004191', 'ENSGALG00010028453', 'ENSGALG00010029936']]
    cluster_data_0_2 = [['ENSGALG00010003557', 'ENSGALG00010003644', 'ENSGALG00010003584', 'ENSGALG00010003635', 'ENSGALG00010003643',
      'ENSGALG00010003537', 'ENSGALG00010003598', 'ENSGALG00010003640', 'ENSGALG00010003576', 'ENSGALG00010003565',
      'ENSGALG00010003614', 'ENSGALG00010003563', 'ENSGALG00010003575', 'ENSGALG00010003613', 'ENSGALG00010003623',
      'ENSGALG00010003529'],
     ['ENSGALG00010018015', 'ENSGALG00010019441', 'ENSGALG00010017922', 'ENSGALG00010004300', 'ENSGALG00010019282',
      'ENSGALG00010012747', 'ENSGALG00010017359', 'ENSGALG00010018354', 'ENSGALG00010020379', 'ENSGALG00010028007',
      'ENSGALG00010013162', 'ENSGALG00010028095', 'ENSGALG00010024885', 'ENSGALG00010023571'],
     ['ENSGALG00010028748', 'ENSGALG00010024475', 'ENSGALG00010028084', 'ENSGALG00010013084', 'ENSGALG00010023347',
      'ENSGALG00010023422', 'ENSGALG00010017873', 'ENSGALG00010025305', 'ENSGALG00010022659', 'ENSGALG00010027183',
      'ENSGALG00010029391', 'ENSGALG00010029547'],
     ['ENSGALG00010022917', 'ENSGALG00010018920', 'ENSGALG00010011965', 'ENSGALG00010024186', 'ENSGALG00010029755',
      'ENSGALG00010024516', 'ENSGALG00010003472', 'ENSGALG00010002090', 'ENSGALG00010009338', 'ENSGALG00010011885',
      'ENSGALG00010001234', 'ENSGALG00010015697'],
     ['ENSGALG00010001804', 'ENSGALG00010007781', 'ENSGALG00010011853', 'ENSGALG00010028603', 'ENSGALG00010006728',
      'ENSGALG00010022806', 'ENSGALG00010014789', 'ENSGALG00010022695', 'ENSGALG00010008325', 'ENSGALG00010000853'],
     ['ENSGALG00010015069', 'ENSGALG00010023733', 'ENSGALG00010008128', 'ENSGALG00010000603', 'ENSGALG00010004434',
      'ENSGALG00010027965', 'ENSGALG00010010262', 'ENSGALG00010011222', 'ENSGALG00010013375', 'ENSGALG00010025869'],
     ['ENSGALG00010023758', 'ENSGALG00010010007', 'ENSGALG00010024566', 'ENSGALG00010023041', 'ENSGALG00010014361',
      'ENSGALG00010018581', 'ENSGALG00010026874', 'ENSGALG00010006327', 'ENSGALG00010011246', 'ENSGALG00010011952'],
     ['ENSGALG00010020708', 'ENSGALG00010016410', 'ENSGALG00010002160', 'ENSGALG00010026220', 'ENSGALG00010027943',
      'ENSGALG00010008497', 'ENSGALG00010005264', 'ENSGALG00010021617', 'ENSGALG00010006254', 'ENSGALG00010004860'],
     ['ENSGALG00010004934', 'ENSGALG00010008023', 'ENSGALG00010022971', 'ENSGALG00010002087', 'ENSGALG00010011456',
      'ENSGALG00010017746', 'ENSGALG00010002376', 'ENSGALG00010004373', 'ENSGALG00010020981', 'ENSGALG00010023065'],
     ['ENSGALG00010005425', 'ENSGALG00010024035', 'ENSGALG00010014170', 'ENSGALG00010023131', 'ENSGALG00010027649',
      'ENSGALG00010005499', 'ENSGALG00010024920', 'ENSGALG00010019144', 'ENSGALG00010022662'],
     ['ENSGALG00010017664', 'ENSGALG00010016404', 'ENSGALG00010008130', 'ENSGALG00010006735', 'ENSGALG00010011819',
      'ENSGALG00010008028', 'ENSGALG00010026760', 'ENSGALG00010015643', 'ENSGALG00010007432'],
     ['ENSGALG00010001440', 'ENSGALG00010019221', 'ENSGALG00010021677', 'ENSGALG00010018172', 'ENSGALG00010018694',
      'ENSGALG00010005831', 'ENSGALG00010011133', 'ENSGALG00010012054', 'ENSGALG00010022172'],
     ['ENSGALG00010026403', 'ENSGALG00010000349', 'ENSGALG00010018750', 'ENSGALG00010025325', 'ENSGALG00010001852',
      'ENSGALG00010020646', 'ENSGALG00010025586', 'ENSGALG00010018627', 'ENSGALG00010022520'],
     ['ENSGALG00010027268', 'ENSGALG00010010284', 'ENSGALG00010018062', 'ENSGALG00010029767', 'ENSGALG00010013278',
      'ENSGALG00010017435', 'ENSGALG00010010850', 'ENSGALG00010012337', 'ENSGALG00010002904'],
     ['ENSGALG00010021071', 'ENSGALG00010017848', 'ENSGALG00010018154', 'ENSGALG00010022987', 'ENSGALG00010025339',
      'ENSGALG00010003154', 'ENSGALG00010003152', 'ENSGALG00010029213', 'ENSGALG00010025892'],
     ['ENSGALG00010029182', 'ENSGALG00010029536', 'ENSGALG00010026221', 'ENSGALG00010026081', 'ENSGALG00010019067',
      'ENSGALG00010027328', 'ENSGALG00010027893', 'ENSGALG00010029705', 'ENSGALG00010029626'],
     ['ENSGALG00010015356', 'ENSGALG00010029333', 'ENSGALG00010006342', 'ENSGALG00010009571', 'ENSGALG00010013488',
      'ENSGALG00010017437', 'ENSGALG00010021887', 'ENSGALG00010024425', 'ENSGALG00010022165'],
     ['ENSGALG00010010918', 'ENSGALG00010000081', 'ENSGALG00010023730', 'ENSGALG00010020343', 'ENSGALG00010020283',
      'ENSGALG00010027920', 'ENSGALG00010010922', 'ENSGALG00010024325', 'ENSGALG00010024351'],
     ['ENSGALG00010004352', 'ENSGALG00010021764', 'ENSGALG00010017657', 'ENSGALG00010028139', 'ENSGALG00010024675',
      'ENSGALG00010017826', 'ENSGALG00010020602', 'ENSGALG00010017752', 'ENSGALG00010016591'],
     ['ENSGALG00010021576', 'ENSGALG00010025360', 'ENSGALG00010018143', 'ENSGALG00010018543', 'ENSGALG00010025661',
      'ENSGALG00010023518', 'ENSGALG00010023526', 'ENSGALG00010018911', 'ENSGALG00010018655'],
     ['ENSGALG00010004378', 'ENSGALG00010018519', 'ENSGALG00010021754', 'ENSGALG00010011759', 'ENSGALG00010013472',
      'ENSGALG00010028500', 'ENSGALG00010018502', 'ENSGALG00010002581', 'ENSGALG00010010635'],
     ['ENSGALG00010028892', 'ENSGALG00010001551', 'ENSGALG00010028905', 'ENSGALG00010024848', 'ENSGALG00010006285',
      'ENSGALG00010022571', 'ENSGALG00010027162', 'ENSGALG00010028119', 'ENSGALG00010004099'],
     ['ENSGALG00010012865', 'ENSGALG00010015009', 'ENSGALG00010013299', 'ENSGALG00010009515', 'ENSGALG00010014990',
      'ENSGALG00010001837', 'ENSGALG00010023760', 'ENSGALG00010021627', 'ENSGALG00010004443'],
     ['ENSGALG00010010572', 'ENSGALG00010014617', 'ENSGALG00010011929', 'ENSGALG00010010769', 'ENSGALG00010015098',
      'ENSGALG00010020377', 'ENSGALG00010028897', 'ENSGALG00010017694', 'ENSGALG00010017263'],
     ['ENSGALG00010023513', 'ENSGALG00010008469', 'ENSGALG00010021950', 'ENSGALG00010023748', 'ENSGALG00010014244',
      'ENSGALG00010015043', 'ENSGALG00010014312', 'ENSGALG00010022171'],
     ['ENSGALG00010002280', 'ENSGALG00010026030', 'ENSGALG00010018573', 'ENSGALG00010018267', 'ENSGALG00010012926',
      'ENSGALG00010024517', 'ENSGALG00010017957', 'ENSGALG00010027414'],
     ['ENSGALG00010012329', 'ENSGALG00010019018', 'ENSGALG00010006134', 'ENSGALG00010023627', 'ENSGALG00010006275',
      'ENSGALG00010009094', 'ENSGALG00010005407', 'ENSGALG00010006132'],
     ['ENSGALG00010021098', 'ENSGALG00010008291', 'ENSGALG00010018950', 'ENSGALG00010016847', 'ENSGALG00010025742',
      'ENSGALG00010021716', 'ENSGALG00010011723', 'ENSGALG00010025554'],
     ['ENSGALG00010030105', 'ENSGALG00010020906', 'ENSGALG00010005362', 'ENSGALG00010014083', 'ENSGALG00010026005',
      'ENSGALG00010009833', 'ENSGALG00010001111', 'ENSGALG00010016569'],
     ['ENSGALG00010013440', 'ENSGALG00010013444', 'ENSGALG00010013514', 'ENSGALG00010011529', 'ENSGALG00010020316',
      'ENSGALG00010018296', 'ENSGALG00010007817', 'ENSGALG00010022149'],
     ['ENSGALG00010015523', 'ENSGALG00010019584', 'ENSGALG00010010270', 'ENSGALG00010019040', 'ENSGALG00010021786',
      'ENSGALG00010009016', 'ENSGALG00010017739', 'ENSGALG00010008098'],
     ['ENSGALG00010028052', 'ENSGALG00010028876', 'ENSGALG00010024509', 'ENSGALG00010023064', 'ENSGALG00010027231',
      'ENSGALG00010018808', 'ENSGALG00010027700', 'ENSGALG00010027775'],
     ['ENSGALG00010028039', 'ENSGALG00010026008', 'ENSGALG00010029723', 'ENSGALG00010013498', 'ENSGALG00010027244',
      'ENSGALG00010015889', 'ENSGALG00010011322', 'ENSGALG00010015149'],
     ['ENSGALG00010005119', 'ENSGALG00010006270', 'ENSGALG00010009130', 'ENSGALG00010012024', 'ENSGALG00010002504',
      'ENSGALG00010005436', 'ENSGALG00010018315', 'ENSGALG00010005482'],
     ['ENSGALG00010021264', 'ENSGALG00010008447', 'ENSGALG00010015809', 'ENSGALG00010019307', 'ENSGALG00010018420',
      'ENSGALG00010024764', 'ENSGALG00010027869', 'ENSGALG00010018514'],
     ['ENSGALG00010024440', 'ENSGALG00010029538', 'ENSGALG00010024350', 'ENSGALG00010029511', 'ENSGALG00010016875',
      'ENSGALG00010015095', 'ENSGALG00010021583', 'ENSGALG00010023336'],
     ['ENSGALG00010002285', 'ENSGALG00010003478', 'ENSGALG00010001471', 'ENSGALG00010002588', 'ENSGALG00010003713',
      'ENSGALG00010003383', 'ENSGALG00010004087', 'ENSGALG00010003719'],
     ['ENSGALG00010023252', 'ENSGALG00010010422', 'ENSGALG00010023073', 'ENSGALG00010028113', 'ENSGALG00010025753',
      'ENSGALG00010029405', 'ENSGALG00010028132', 'ENSGALG00010024879'],
     ['ENSGALG00010029298', 'ENSGALG00010014319', 'ENSGALG00010029495', 'ENSGALG00010020094', 'ENSGALG00010002206',
      'ENSGALG00010001991', 'ENSGALG00010029231', 'ENSGALG00010026873'],
     ['ENSGALG00010029857', 'ENSGALG00010028429', 'ENSGALG00010007975', 'ENSGALG00010029304', 'ENSGALG00010021415',
      'ENSGALG00010029691', 'ENSGALG00010025137', 'ENSGALG00010027966'],
     ['ENSGALG00010022050', 'ENSGALG00010014739', 'ENSGALG00010021619', 'ENSGALG00010019072', 'ENSGALG00010017250',
      'ENSGALG00010017579', 'ENSGALG00010016977', 'ENSGALG00010017585'],
     ['ENSGALG00010002308', 'ENSGALG00010001952', 'ENSGALG00010021064', 'ENSGALG00010024887', 'ENSGALG00010023767',
      'ENSGALG00010002983', 'ENSGALG00010001418', 'ENSGALG00010003714'],
     ['ENSGALG00010022348', 'ENSGALG00010016599', 'ENSGALG00010028191', 'ENSGALG00010018380', 'ENSGALG00010019684',
      'ENSGALG00010001877', 'ENSGALG00010016457', 'ENSGALG00010021719'],
     ['ENSGALG00010012339', 'ENSGALG00010011677', 'ENSGALG00010005253', 'ENSGALG00010011523', 'ENSGALG00010012343',
      'ENSGALG00010011997', 'ENSGALG00010012372', 'ENSGALG00010012426'],
     ['ENSGALG00010006091', 'ENSGALG00010027348', 'ENSGALG00010003882', 'ENSGALG00010018046', 'ENSGALG00010027175',
      'ENSGALG00010016848', 'ENSGALG00010003814', 'ENSGALG00010029401'],
     ['ENSGALG00010005445', 'ENSGALG00010007871', 'ENSGALG00010029659', 'ENSGALG00010015703', 'ENSGALG00010005485',
      'ENSGALG00010030102', 'ENSGALG00010022108', 'ENSGALG00010016629'],
     ['ENSGALG00010007457', 'ENSGALG00010029542', 'ENSGALG00010009543', 'ENSGALG00010009277', 'ENSGALG00010021394',
      'ENSGALG00010022242', 'ENSGALG00010026017', 'ENSGALG00010021452'],
     ['ENSGALG00010012767', 'ENSGALG00010021188', 'ENSGALG00010000148', 'ENSGALG00010008352', 'ENSGALG00010004888',
      'ENSGALG00010023850', 'ENSGALG00010008708', 'ENSGALG00010020866'],
     ['ENSGALG00010018348', 'ENSGALG00010029246', 'ENSGALG00010021122', 'ENSGALG00010017773', 'ENSGALG00010028604',
      'ENSGALG00010018971', 'ENSGALG00010019557', 'ENSGALG00010016562'],
     ['ENSGALG00010022167', 'ENSGALG00010024549', 'ENSGALG00010012977', 'ENSGALG00010014380', 'ENSGALG00010010386',
      'ENSGALG00010018883', 'ENSGALG00010026104'],
     ['ENSGALG00010007811', 'ENSGALG00010001776', 'ENSGALG00010010896', 'ENSGALG00010003344', 'ENSGALG00010020779',
      'ENSGALG00010018049', 'ENSGALG00010005472'],
     ['ENSGALG00010016982', 'ENSGALG00010014567', 'ENSGALG00010022513', 'ENSGALG00010002231', 'ENSGALG00010026128',
      'ENSGALG00010011124', 'ENSGALG00010002752'],
     ['ENSGALG00010023317', 'ENSGALG00010023744', 'ENSGALG00010003777', 'ENSGALG00010023431', 'ENSGALG00010008232',
      'ENSGALG00010023070', 'ENSGALG00010029412'],
     ['ENSGALG00010019767', 'ENSGALG00010017987', 'ENSGALG00010013244', 'ENSGALG00010001237', 'ENSGALG00010018517',
      'ENSGALG00010022489', 'ENSGALG00010024628'],
     ['ENSGALG00010011879', 'ENSGALG00010018176', 'ENSGALG00010016994', 'ENSGALG00010001518', 'ENSGALG00010012285',
      'ENSGALG00010001811', 'ENSGALG00010012097'],
     ['ENSGALG00010028419', 'ENSGALG00010021256', 'ENSGALG00010027634', 'ENSGALG00010023172', 'ENSGALG00010020810',
      'ENSGALG00010021272', 'ENSGALG00010026316'],
     ['ENSGALG00010020720', 'ENSGALG00010018670', 'ENSGALG00010009796', 'ENSGALG00010012962', 'ENSGALG00010001143',
      'ENSGALG00010018546', 'ENSGALG00010028085'],
     ['ENSGALG00010008448', 'ENSGALG00010002034', 'ENSGALG00010008418', 'ENSGALG00010008134', 'ENSGALG00010004951',
      'ENSGALG00010000818', 'ENSGALG00010005507'],
     ['ENSGALG00010028121', 'ENSGALG00010024858', 'ENSGALG00010028186', 'ENSGALG00010028871', 'ENSGALG00010000555',
      'ENSGALG00010008096', 'ENSGALG00010018611'],
     ['ENSGALG00010023819', 'ENSGALG00010017699', 'ENSGALG00010028163', 'ENSGALG00010016905', 'ENSGALG00010028467',
      'ENSGALG00010016920', 'ENSGALG00010003110'],
     ['ENSGALG00010028425', 'ENSGALG00010027865', 'ENSGALG00010013275', 'ENSGALG00010028578', 'ENSGALG00010024882',
      'ENSGALG00010020206', 'ENSGALG00010020806'],
     ['ENSGALG00010001292', 'ENSGALG00010013174', 'ENSGALG00010003388', 'ENSGALG00010003761', 'ENSGALG00010004095',
      'ENSGALG00010027975', 'ENSGALG00010013071'],
     ['ENSGALG00010028507', 'ENSGALG00010019302', 'ENSGALG00010014626', 'ENSGALG00010021254', 'ENSGALG00010018756',
      'ENSGALG00010021175', 'ENSGALG00010020059'],
     ['ENSGALG00010021027', 'ENSGALG00010007980', 'ENSGALG00010024974', 'ENSGALG00010001865', 'ENSGALG00010013152',
      'ENSGALG00010003958', 'ENSGALG00010000687'],
     ['ENSGALG00010004433', 'ENSGALG00010006123', 'ENSGALG00010022325', 'ENSGALG00010001225', 'ENSGALG00010010982',
      'ENSGALG00010005714', 'ENSGALG00010024931'],
     ['ENSGALG00010029290', 'ENSGALG00010022879', 'ENSGALG00010007581', 'ENSGALG00010024286', 'ENSGALG00010024534',
      'ENSGALG00010010472', 'ENSGALG00010024837'],
     ['ENSGALG00010003305', 'ENSGALG00010016911', 'ENSGALG00010024051', 'ENSGALG00010028683', 'ENSGALG00010027998',
      'ENSGALG00010000059', 'ENSGALG00010014047'],
     ['ENSGALG00010012574', 'ENSGALG00010014691', 'ENSGALG00010014997', 'ENSGALG00010024945', 'ENSGALG00010005637',
      'ENSGALG00010022152', 'ENSGALG00010014398'],
     ['ENSGALG00010017717', 'ENSGALG00010019334', 'ENSGALG00010025268', 'ENSGALG00010002432', 'ENSGALG00010002857',
      'ENSGALG00010001835', 'ENSGALG00010017307'],
     ['ENSGALG00010005512', 'ENSGALG00010021044', 'ENSGALG00010017712', 'ENSGALG00010005551', 'ENSGALG00010011361',
      'ENSGALG00010006486', 'ENSGALG00010016498'],
     ['ENSGALG00010005383', 'ENSGALG00010007866', 'ENSGALG00010016989', 'ENSGALG00010012062', 'ENSGALG00010008312',
      'ENSGALG00010005682', 'ENSGALG00010003589'],
     ['ENSGALG00010006229', 'ENSGALG00010020074', 'ENSGALG00010029367', 'ENSGALG00010013398', 'ENSGALG00010012407',
      'ENSGALG00010020554', 'ENSGALG00010021162'],
     ['ENSGALG00010004673', 'ENSGALG00010012796', 'ENSGALG00010014203', 'ENSGALG00010016834', 'ENSGALG00010027988',
      'ENSGALG00010002352', 'ENSGALG00010002760'],
     ['ENSGALG00010028887', 'ENSGALG00010024541', 'ENSGALG00010028743', 'ENSGALG00010015166', 'ENSGALG00010020075',
      'ENSGALG00010028485', 'ENSGALG00010014909'],
     ['ENSGALG00010013132', 'ENSGALG00010013236', 'ENSGALG00010016398', 'ENSGALG00010009593', 'ENSGALG00010011993',
      'ENSGALG00010021058', 'ENSGALG00010016970'],
     ['ENSGALG00010002750', 'ENSGALG00010005326', 'ENSGALG00010001639', 'ENSGALG00010005548', 'ENSGALG00010007879',
      'ENSGALG00010000911', 'ENSGALG00010011450'],
     ['ENSGALG00010004592', 'ENSGALG00010027015', 'ENSGALG00010028128', 'ENSGALG00010016414', 'ENSGALG00010012250',
      'ENSGALG00010017556', 'ENSGALG00010013170'],
     ['ENSGALG00010029171', 'ENSGALG00010023179', 'ENSGALG00010020889', 'ENSGALG00010021640', 'ENSGALG00010027289',
      'ENSGALG00010004962', 'ENSGALG00010023821'],
     ['ENSGALG00010009383', 'ENSGALG00010018915', 'ENSGALG00010008360', 'ENSGALG00010017349', 'ENSGALG00010014984',
      'ENSGALG00010015037', 'ENSGALG00010019399'],
     ['ENSGALG00010008149', 'ENSGALG00010028606', 'ENSGALG00010028187', 'ENSGALG00010027306', 'ENSGALG00010023127',
      'ENSGALG00010025523', 'ENSGALG00010027185'],
     ['ENSGALG00010014736', 'ENSGALG00010014900', 'ENSGALG00010012154', 'ENSGALG00010007997', 'ENSGALG00010009236',
      'ENSGALG00010010971', 'ENSGALG00010013551'],
     ['ENSGALG00010014418', 'ENSGALG00010018593', 'ENSGALG00010021506', 'ENSGALG00010002377', 'ENSGALG00010027635',
      'ENSGALG00010027575', 'ENSGALG00010012059'],
     ['ENSGALG00010027128', 'ENSGALG00010001599', 'ENSGALG00010021382', 'ENSGALG00010005252', 'ENSGALG00010003471',
      'ENSGALG00010020525', 'ENSGALG00010023830'],
     ['ENSGALG00010019008', 'ENSGALG00010024840', 'ENSGALG00010018371', 'ENSGALG00010015472', 'ENSGALG00010021513',
      'ENSGALG00010024897', 'ENSGALG00010024049'],
     ['ENSGALG00010009101', 'ENSGALG00010009103', 'ENSGALG00010004211', 'ENSGALG00010013374', 'ENSGALG00010004451',
      'ENSGALG00010005545', 'ENSGALG00010005181'],
     ['ENSGALG00010022541', 'ENSGALG00010014334', 'ENSGALG00010022737', 'ENSGALG00010002741', 'ENSGALG00010024086',
      'ENSGALG00010013041', 'ENSGALG00010024421'],
     ['ENSGALG00010006076', 'ENSGALG00010029220', 'ENSGALG00010023103', 'ENSGALG00010028107', 'ENSGALG00010027490',
      'ENSGALG00010025994', 'ENSGALG00010027346'],
     ['ENSGALG00010020473', 'ENSGALG00010028600', 'ENSGALG00010027236', 'ENSGALG00010020831', 'ENSGALG00010023476',
      'ENSGALG00010000286', 'ENSGALG00010027886'],
     ['ENSGALG00010005367', 'ENSGALG00010021759', 'ENSGALG00010022122', 'ENSGALG00010023392', 'ENSGALG00010017018',
      'ENSGALG00010010809', 'ENSGALG00010005335'],
     ['ENSGALG00010007992', 'ENSGALG00010018011', 'ENSGALG00010007924', 'ENSGALG00010009360', 'ENSGALG00010013228',
      'ENSGALG00010021091', 'ENSGALG00010018035'],
     ['ENSGALG00010027895', 'ENSGALG00010027475', 'ENSGALG00010019683', 'ENSGALG00010026010', 'ENSGALG00010028457',
      'ENSGALG00010029533', 'ENSGALG00010014159'],
     ['ENSGALG00010013393', 'ENSGALG00010022275', 'ENSGALG00010009541', 'ENSGALG00010025470', 'ENSGALG00010014186',
      'ENSGALG00010012693', 'ENSGALG00010025161'],
     ['ENSGALG00010024729', 'ENSGALG00010023854', 'ENSGALG00010025358', 'ENSGALG00010025527', 'ENSGALG00010021419',
      'ENSGALG00010016788', 'ENSGALG00010022363'],
     ['ENSGALG00010021362', 'ENSGALG00010018404', 'ENSGALG00010015094', 'ENSGALG00010027981', 'ENSGALG00010003830',
      'ENSGALG00010028872', 'ENSGALG00010024795'],
     ['ENSGALG00010014200', 'ENSGALG00010007624', 'ENSGALG00010012441', 'ENSGALG00010013173', 'ENSGALG00010011932',
      'ENSGALG00010014929', 'ENSGALG00010014476'],
     ['ENSGALG00010028572', 'ENSGALG00010028147', 'ENSGALG00010028171', 'ENSGALG00010013387', 'ENSGALG00010029926',
      'ENSGALG00010028002', 'ENSGALG00010013362'],
     ['ENSGALG00010023776', 'ENSGALG00010027141', 'ENSGALG00010027861', 'ENSGALG00010028593', 'ENSGALG00010020920',
      'ENSGALG00010012973', 'ENSGALG00010014963'],
     ['ENSGALG00010007965', 'ENSGALG00010010080', 'ENSGALG00010016051', 'ENSGALG00010012711', 'ENSGALG00010012121',
      'ENSGALG00010005462', 'ENSGALG00010015788'],
     ['ENSGALG00010029665', 'ENSGALG00010028912', 'ENSGALG00010017530', 'ENSGALG00010012108', 'ENSGALG00010020438',
      'ENSGALG00010029582', 'ENSGALG00010013414'],
     ['ENSGALG00010029634', 'ENSGALG00010022297', 'ENSGALG00010021290', 'ENSGALG00010029633', 'ENSGALG00010017955',
      'ENSGALG00010020375', 'ENSGALG00010015016'],
     ['ENSGALG00010018598', 'ENSGALG00010003585', 'ENSGALG00010003164', 'ENSGALG00010003762', 'ENSGALG00010023335',
      'ENSGALG00010022967', 'ENSGALG00010028099'],
     ['ENSGALG00010021239', 'ENSGALG00010017672', 'ENSGALG00010011323', 'ENSGALG00010021594', 'ENSGALG00010018837',
      'ENSGALG00010021498', 'ENSGALG00010021584'],
     ['ENSGALG00010024869', 'ENSGALG00010016916', 'ENSGALG00010023777', 'ENSGALG00010005310', 'ENSGALG00010018137',
      'ENSGALG00010029703', 'ENSGALG00010023764'],
     ['ENSGALG00010019104', 'ENSGALG00010008385', 'ENSGALG00010000292', 'ENSGALG00010027983', 'ENSGALG00010028881',
      'ENSGALG00010000452', 'ENSGALG00010015498'],
     ['ENSGALG00010024555', 'ENSGALG00010024697', 'ENSGALG00010017678', 'ENSGALG00010023380', 'ENSGALG00010018557',
      'ENSGALG00010017528', 'ENSGALG00010024925'],
     ['ENSGALG00010025353', 'ENSGALG00010024433', 'ENSGALG00010010780', 'ENSGALG00010022603', 'ENSGALG00010005402',
      'ENSGALG00010021652', 'ENSGALG00010004082'],
     ['ENSGALG00010025243', 'ENSGALG00010012244', 'ENSGALG00010019312', 'ENSGALG00010022467', 'ENSGALG00010027419',
      'ENSGALG00010027450'],
     ['ENSGALG00010001832', 'ENSGALG00010024940', 'ENSGALG00010002336', 'ENSGALG00010013561', 'ENSGALG00010012600',
      'ENSGALG00010018919'],
     ['ENSGALG00010015148', 'ENSGALG00010019269', 'ENSGALG00010024145', 'ENSGALG00010021070', 'ENSGALG00010013389',
      'ENSGALG00010017094'],
     ['ENSGALG00010012275', 'ENSGALG00010012219', 'ENSGALG00010010257', 'ENSGALG00010005170', 'ENSGALG00010016454',
      'ENSGALG00010020091'],
     ['ENSGALG00010025312', 'ENSGALG00010014171', 'ENSGALG00010013546', 'ENSGALG00010008316', 'ENSGALG00010016366',
      'ENSGALG00010005756'],
     ['ENSGALG00010024191', 'ENSGALG00010024003', 'ENSGALG00010010802', 'ENSGALG00010023368', 'ENSGALG00010008038',
      'ENSGALG00010023635'],
     ['ENSGALG00010014744', 'ENSGALG00010009678', 'ENSGALG00010015165', 'ENSGALG00010027327', 'ENSGALG00010023472',
      'ENSGALG00010009159'],
     ['ENSGALG00010024682', 'ENSGALG00010023880', 'ENSGALG00010028468', 'ENSGALG00010025954', 'ENSGALG00010024548',
      'ENSGALG00010024756'],
     ['ENSGALG00010017131', 'ENSGALG00010020999', 'ENSGALG00010020584', 'ENSGALG00010007382', 'ENSGALG00010013063',
      'ENSGALG00010022207'],
     ['ENSGALG00010016393', 'ENSGALG00010017962', 'ENSGALG00010012138', 'ENSGALG00010015027', 'ENSGALG00010019388',
      'ENSGALG00010017198'],
     ['ENSGALG00010027076', 'ENSGALG00010021438', 'ENSGALG00010014056', 'ENSGALG00010026947', 'ENSGALG00010026485',
      'ENSGALG00010024193'],
     ['ENSGALG00010020120', 'ENSGALG00010028067', 'ENSGALG00010004340', 'ENSGALG00010027363', 'ENSGALG00010016758',
      'ENSGALG00010009858'],
     ['ENSGALG00010009849', 'ENSGALG00010005588', 'ENSGALG00010023751', 'ENSGALG00010001702', 'ENSGALG00010013281',
      'ENSGALG00010009985'],
     ['ENSGALG00010014120', 'ENSGALG00010001752', 'ENSGALG00010021074', 'ENSGALG00010022811', 'ENSGALG00010022774',
      'ENSGALG00010020282'],
     ['ENSGALG00010010836', 'ENSGALG00010019962', 'ENSGALG00010001320', 'ENSGALG00010017830', 'ENSGALG00010017431',
      'ENSGALG00010017063'],
     ['ENSGALG00010007853', 'ENSGALG00010008276', 'ENSGALG00010005176', 'ENSGALG00010002349', 'ENSGALG00010025126',
      'ENSGALG00010000711'],
     ['ENSGALG00010001491', 'ENSGALG00010018419', 'ENSGALG00010009457', 'ENSGALG00010020130', 'ENSGALG00010011280',
      'ENSGALG00010025544'],
     ['ENSGALG00010029363', 'ENSGALG00010017346', 'ENSGALG00010029377', 'ENSGALG00010002522', 'ENSGALG00010017167',
      'ENSGALG00010026291'],
     ['ENSGALG00010003841', 'ENSGALG00010000729', 'ENSGALG00010003366', 'ENSGALG00010007719', 'ENSGALG00010004224',
      'ENSGALG00010003489'],
     ['ENSGALG00010024665', 'ENSGALG00010024143', 'ENSGALG00010019891', 'ENSGALG00010011742', 'ENSGALG00010024282',
      'ENSGALG00010027187'],
     ['ENSGALG00010006682', 'ENSGALG00010015869', 'ENSGALG00010006525', 'ENSGALG00010001465', 'ENSGALG00010018922',
      'ENSGALG00010016823'],
     ['ENSGALG00010000186', 'ENSGALG00010017774', 'ENSGALG00010027901', 'ENSGALG00010025585', 'ENSGALG00010017707',
      'ENSGALG00010016362'],
     ['ENSGALG00010025938', 'ENSGALG00010012708', 'ENSGALG00010011980', 'ENSGALG00010023673', 'ENSGALG00010021454',
      'ENSGALG00010012824'],
     ['ENSGALG00010023670', 'ENSGALG00010020533', 'ENSGALG00010005296', 'ENSGALG00010009398', 'ENSGALG00010013131',
      'ENSGALG00010023201'],
     ['ENSGALG00010006496', 'ENSGALG00010017597', 'ENSGALG00010001368', 'ENSGALG00010020096', 'ENSGALG00010019785',
      'ENSGALG00010013436'],
     ['ENSGALG00010007873', 'ENSGALG00010027409', 'ENSGALG00010014994', 'ENSGALG00010027609', 'ENSGALG00010025373',
      'ENSGALG00010023340'],
     ['ENSGALG00010028503', 'ENSGALG00010017039', 'ENSGALG00010021488', 'ENSGALG00010013915', 'ENSGALG00010017550',
      'ENSGALG00010021417'],
     ['ENSGALG00010002716', 'ENSGALG00010019337', 'ENSGALG00010005341', 'ENSGALG00010024596', 'ENSGALG00010024095',
      'ENSGALG00010018857'],
     ['ENSGALG00010004855', 'ENSGALG00010012750', 'ENSGALG00010022969', 'ENSGALG00010011001', 'ENSGALG00010002601',
      'ENSGALG00010012760'],
     ['ENSGALG00010001501', 'ENSGALG00010005255', 'ENSGALG00010003860', 'ENSGALG00010022881', 'ENSGALG00010007224',
      'ENSGALG00010017096'],
     ['ENSGALG00010025160', 'ENSGALG00010020374', 'ENSGALG00010023169', 'ENSGALG00010020493', 'ENSGALG00010021325',
      'ENSGALG00010029419'],
     ['ENSGALG00010002612', 'ENSGALG00010003183', 'ENSGALG00010009363', 'ENSGALG00010010085', 'ENSGALG00010021112',
      'ENSGALG00010008376'],
     ['ENSGALG00010012742', 'ENSGALG00010017496', 'ENSGALG00010009385', 'ENSGALG00010018259', 'ENSGALG00010027614',
      'ENSGALG00010024927'],
     ['ENSGALG00010022304', 'ENSGALG00010029791', 'ENSGALG00010018701', 'ENSGALG00010019602', 'ENSGALG00010021083',
      'ENSGALG00010024933'],
     ['ENSGALG00010024797', 'ENSGALG00010024809', 'ENSGALG00010021626', 'ENSGALG00010025005', 'ENSGALG00010024660',
      'ENSGALG00010026234'],
     ['ENSGALG00010005527', 'ENSGALG00010010321', 'ENSGALG00010023822', 'ENSGALG00010011673', 'ENSGALG00010003858',
      'ENSGALG00010021020'],
     ['ENSGALG00010028211', 'ENSGALG00010021082', 'ENSGALG00010025506', 'ENSGALG00010024843', 'ENSGALG00010029726',
      'ENSGALG00010021154'],
     ['ENSGALG00010021378', 'ENSGALG00010029596', 'ENSGALG00010001166', 'ENSGALG00010015917', 'ENSGALG00010020101',
      'ENSGALG00010002437'],
     ['ENSGALG00010000810', 'ENSGALG00010014205', 'ENSGALG00010020957', 'ENSGALG00010008160', 'ENSGALG00010002487',
      'ENSGALG00010009040'],
     ['ENSGALG00010021346', 'ENSGALG00010011650', 'ENSGALG00010029344', 'ENSGALG00010011184', 'ENSGALG00010026261',
      'ENSGALG00010009520'],
     ['ENSGALG00010021003', 'ENSGALG00010003171', 'ENSGALG00010021025', 'ENSGALG00010020770', 'ENSGALG00010012662',
      'ENSGALG00010028829'],
     ['ENSGALG00010014578', 'ENSGALG00010014935', 'ENSGALG00010014367', 'ENSGALG00010013017', 'ENSGALG00010029524',
      'ENSGALG00010016556'],
     ['ENSGALG00010027150', 'ENSGALG00010006287', 'ENSGALG00010025477', 'ENSGALG00010028904', 'ENSGALG00010029166',
      'ENSGALG00010021176'],
     ['ENSGALG00010007590', 'ENSGALG00010011998', 'ENSGALG00010014149', 'ENSGALG00010015025', 'ENSGALG00010010309',
      'ENSGALG00010009391'],
     ['ENSGALG00010010915', 'ENSGALG00010024451', 'ENSGALG00010029396', 'ENSGALG00010017452', 'ENSGALG00010026553',
      'ENSGALG00010027617'],
     ['ENSGALG00010027980', 'ENSGALG00010019789', 'ENSGALG00010019026', 'ENSGALG00010027218', 'ENSGALG00010011106',
      'ENSGALG00010017605'],
     ['ENSGALG00010000785', 'ENSGALG00010028889', 'ENSGALG00010013833', 'ENSGALG00010018533', 'ENSGALG00010019577',
      'ENSGALG00010005585'],
     ['ENSGALG00010000029', 'ENSGALG00010000024', 'ENSGALG00010000011', 'ENSGALG00010000034', 'ENSGALG00010000023',
      'ENSGALG00010000007'],
     ['ENSGALG00010002627', 'ENSGALG00010021243', 'ENSGALG00010020008', 'ENSGALG00010003894', 'ENSGALG00010007821',
      'ENSGALG00010008007'],
     ['ENSGALG00010002431', 'ENSGALG00010011424', 'ENSGALG00010022166', 'ENSGALG00010013385', 'ENSGALG00010017642',
      'ENSGALG00010012606'],
     ['ENSGALG00010014972', 'ENSGALG00010016474', 'ENSGALG00010003274', 'ENSGALG00010002894', 'ENSGALG00010017350',
      'ENSGALG00010011128'],
     ['ENSGALG00010011549', 'ENSGALG00010024708', 'ENSGALG00010011738', 'ENSGALG00010014400', 'ENSGALG00010024845',
      'ENSGALG00010010748'],
     ['ENSGALG00010026106', 'ENSGALG00010021762', 'ENSGALG00010026241', 'ENSGALG00010010461', 'ENSGALG00010028172',
      'ENSGALG00010026700'],
     ['ENSGALG00010018843', 'ENSGALG00010015932', 'ENSGALG00010010841', 'ENSGALG00010013815', 'ENSGALG00010018284',
      'ENSGALG00010000402'],
     ['ENSGALG00010020700', 'ENSGALG00010023229', 'ENSGALG00010023885', 'ENSGALG00010026889', 'ENSGALG00010005241',
      'ENSGALG00010003764'],
     ['ENSGALG00010007983', 'ENSGALG00010010849', 'ENSGALG00010021670', 'ENSGALG00010024961', 'ENSGALG00010021207',
      'ENSGALG00010027146'],
     ['ENSGALG00010009129', 'ENSGALG00010009157', 'ENSGALG00010009136', 'ENSGALG00010006055', 'ENSGALG00010004046',
      'ENSGALG00010006131'],
     ['ENSGALG00010026293', 'ENSGALG00010004883', 'ENSGALG00010024712', 'ENSGALG00010027027', 'ENSGALG00010004408',
      'ENSGALG00010026720'],
     ['ENSGALG00010000526', 'ENSGALG00010016378', 'ENSGALG00010010243', 'ENSGALG00010017122', 'ENSGALG00010004489',
      'ENSGALG00010013047'],
     ['ENSGALG00010012286', 'ENSGALG00010029537', 'ENSGALG00010003287', 'ENSGALG00010003609', 'ENSGALG00010003618',
      'ENSGALG00010003258'],
     ['ENSGALG00010017283', 'ENSGALG00010022974', 'ENSGALG00010029365', 'ENSGALG00010020109', 'ENSGALG00010021441',
      'ENSGALG00010019013'],
     ['ENSGALG00010021566', 'ENSGALG00010021186', 'ENSGALG00010023054', 'ENSGALG00010021648', 'ENSGALG00010021730',
      'ENSGALG00010017762'],
     ['ENSGALG00010004505', 'ENSGALG00010018021', 'ENSGALG00010014093', 'ENSGALG00010029835', 'ENSGALG00010016097',
      'ENSGALG00010018532'],
     ['ENSGALG00010009113', 'ENSGALG00010023334', 'ENSGALG00010002912', 'ENSGALG00010000050', 'ENSGALG00010017314',
      'ENSGALG00010002855'],
     ['ENSGALG00010001807', 'ENSGALG00010024722', 'ENSGALG00010001159', 'ENSGALG00010017613', 'ENSGALG00010019717',
      'ENSGALG00010015749'],
     ['ENSGALG00010002507', 'ENSGALG00010008083', 'ENSGALG00010013365', 'ENSGALG00010008862', 'ENSGALG00010005389',
      'ENSGALG00010008246'],
     ['ENSGALG00010023118', 'ENSGALG00010010322', 'ENSGALG00010022678', 'ENSGALG00010019227', 'ENSGALG00010021935',
      'ENSGALG00010022664'],
     ['ENSGALG00010004315', 'ENSGALG00010010967', 'ENSGALG00010008729', 'ENSGALG00010006803', 'ENSGALG00010010327',
      'ENSGALG00010005634'],
     ['ENSGALG00010014249', 'ENSGALG00010024798', 'ENSGALG00010029670', 'ENSGALG00010018490', 'ENSGALG00010026607',
      'ENSGALG00010013484'],
     ['ENSGALG00010025064', 'ENSGALG00010022770', 'ENSGALG00010007941', 'ENSGALG00010008017', 'ENSGALG00010007943',
      'ENSGALG00010025380'],
     ['ENSGALG00010024510', 'ENSGALG00010024179', 'ENSGALG00010024164', 'ENSGALG00010027119', 'ENSGALG00010022647',
      'ENSGALG00010024314'],
     ['ENSGALG00010001372', 'ENSGALG00010001283', 'ENSGALG00010029324', 'ENSGALG00010001244', 'ENSGALG00010008308',
      'ENSGALG00010017724'],
     ['ENSGALG00010023962', 'ENSGALG00010023087', 'ENSGALG00010010320', 'ENSGALG00010026097', 'ENSGALG00010024570',
      'ENSGALG00010024472'],
     ['ENSGALG00010022804', 'ENSGALG00010021041', 'ENSGALG00010023578', 'ENSGALG00010020011', 'ENSGALG00010020696',
      'ENSGALG00010022034'],
     ['ENSGALG00010025069', 'ENSGALG00010017038', 'ENSGALG00010017411', 'ENSGALG00010028501', 'ENSGALG00010028199',
      'ENSGALG00010015796'],
     ['ENSGALG00010025998', 'ENSGALG00010028888', 'ENSGALG00010024188', 'ENSGALG00010012079', 'ENSGALG00010024839',
      'ENSGALG00010021841'],
     ['ENSGALG00010028439', 'ENSGALG00010026046', 'ENSGALG00010006259', 'ENSGALG00010002492', 'ENSGALG00010015660',
      'ENSGALG00010005337'],
     ['ENSGALG00010008300', 'ENSGALG00010021621', 'ENSGALG00010009868', 'ENSGALG00010013051', 'ENSGALG00010009117',
      'ENSGALG00010005502'],
     ['ENSGALG00010009020', 'ENSGALG00010029525', 'ENSGALG00010027972', 'ENSGALG00010027276', 'ENSGALG00010027372',
      'ENSGALG00010024452'],
     ['ENSGALG00010020402', 'ENSGALG00010005008', 'ENSGALG00010025200', 'ENSGALG00010006108', 'ENSGALG00010001363',
      'ENSGALG00010022213'],
     ['ENSGALG00010028674', 'ENSGALG00010026566', 'ENSGALG00010024618', 'ENSGALG00010027229', 'ENSGALG00010024313',
      'ENSGALG00010024825'],
     ['ENSGALG00010017398', 'ENSGALG00010021490', 'ENSGALG00010018628', 'ENSGALG00010026601', 'ENSGALG00010014931',
      'ENSGALG00010020237'],
     ['ENSGALG00010007133', 'ENSGALG00010012667', 'ENSGALG00010012028', 'ENSGALG00010007925', 'ENSGALG00010014089',
      'ENSGALG00010011996'],
     ['ENSGALG00010001149', 'ENSGALG00010015778', 'ENSGALG00010024627', 'ENSGALG00010009635', 'ENSGALG00010009705',
      'ENSGALG00010023732'],
     ['ENSGALG00010023046', 'ENSGALG00010022516', 'ENSGALG00010024673', 'ENSGALG00010023377', 'ENSGALG00010023178',
      'ENSGALG00010022474'],
     ['ENSGALG00010025790', 'ENSGALG00010028569', 'ENSGALG00010026982', 'ENSGALG00010014429', 'ENSGALG00010018142',
      'ENSGALG00010011348'],
     ['ENSGALG00010014696', 'ENSGALG00010021196', 'ENSGALG00010010978', 'ENSGALG00010002062', 'ENSGALG00010013553',
      'ENSGALG00010000173'],
     ['ENSGALG00010020548', 'ENSGALG00010024542', 'ENSGALG00010026550', 'ENSGALG00010020569', 'ENSGALG00010001364',
      'ENSGALG00010003331'],
     ['ENSGALG00010017713', 'ENSGALG00010012986', 'ENSGALG00010025481', 'ENSGALG00010023837', 'ENSGALG00010023798',
      'ENSGALG00010020462'],
     ['ENSGALG00010009435', 'ENSGALG00010001712', 'ENSGALG00010016667', 'ENSGALG00010025982', 'ENSGALG00010008273',
      'ENSGALG00010017682'],
     ['ENSGALG00010019985', 'ENSGALG00010013184', 'ENSGALG00010017814', 'ENSGALG00010027410', 'ENSGALG00010007544',
      'ENSGALG00010002634'],
     ['ENSGALG00010016076', 'ENSGALG00010017662', 'ENSGALG00010012341', 'ENSGALG00010024800', 'ENSGALG00010020578',
      'ENSGALG00010001803'],
     ['ENSGALG00010001351', 'ENSGALG00010000346', 'ENSGALG00010017704', 'ENSGALG00010020648', 'ENSGALG00010003937',
      'ENSGALG00010008830'],
     ['ENSGALG00010010786', 'ENSGALG00010019948', 'ENSGALG00010024428', 'ENSGALG00010011904', 'ENSGALG00010016460',
      'ENSGALG00010026102'],
     ['ENSGALG00010014278', 'ENSGALG00010013282', 'ENSGALG00010017789', 'ENSGALG00010017756', 'ENSGALG00010025442',
      'ENSGALG00010013767'],
     ['ENSGALG00010015520', 'ENSGALG00010023547', 'ENSGALG00010027253', 'ENSGALG00010027863', 'ENSGALG00010010585',
      'ENSGALG00010029283'],
     ['ENSGALG00010025139', 'ENSGALG00010023188', 'ENSGALG00010013657', 'ENSGALG00010021048', 'ENSGALG00010014041',
      'ENSGALG00010004896'],
     ['ENSGALG00010010456', 'ENSGALG00010016482', 'ENSGALG00010009256', 'ENSGALG00010012247', 'ENSGALG00010008405',
      'ENSGALG00010008298'],
     ['ENSGALG00010029657', 'ENSGALG00010028642', 'ENSGALG00010025985', 'ENSGALG00010026917', 'ENSGALG00010028512',
      'ENSGALG00010027570'],
     ['ENSGALG00010013510', 'ENSGALG00010005313', 'ENSGALG00010018635', 'ENSGALG00010025553', 'ENSGALG00010010447',
      'ENSGALG00010005123'],
     ['ENSGALG00010015325', 'ENSGALG00010020934', 'ENSGALG00010026296', 'ENSGALG00010027083', 'ENSGALG00010016335',
      'ENSGALG00010002448'],
     ['ENSGALG00010009720', 'ENSGALG00010029265', 'ENSGALG00010029379', 'ENSGALG00010024904', 'ENSGALG00010023446',
      'ENSGALG00010026223'],
     ['ENSGALG00010026907', 'ENSGALG00010023857', 'ENSGALG00010024625', 'ENSGALG00010024604', 'ENSGALG00010024077',
      'ENSGALG00010021400'],
     ['ENSGALG00010029321', 'ENSGALG00010019706', 'ENSGALG00010010179', 'ENSGALG00010000443', 'ENSGALG00010011329',
      'ENSGALG00010020839'],
     ['ENSGALG00010024389', 'ENSGALG00010027307', 'ENSGALG00010024460', 'ENSGALG00010008486', 'ENSGALG00010023124',
      'ENSGALG00010023514'],
     ['ENSGALG00010024240', 'ENSGALG00010014104', 'ENSGALG00010011903', 'ENSGALG00010024338', 'ENSGALG00010014204',
      'ENSGALG00010027003'],
     ['ENSGALG00010029270', 'ENSGALG00010028380', 'ENSGALG00010028188', 'ENSGALG00010028368', 'ENSGALG00010028078',
      'ENSGALG00010028474'],
     ['ENSGALG00010026628', 'ENSGALG00010029950', 'ENSGALG00010017603', 'ENSGALG00010004018', 'ENSGALG00010024441',
      'ENSGALG00010014505'],
     ['ENSGALG00010012195', 'ENSGALG00010001306', 'ENSGALG00010022810', 'ENSGALG00010027929', 'ENSGALG00010013033',
      'ENSGALG00010002046'],
     ['ENSGALG00010029341', 'ENSGALG00010014553', 'ENSGALG00010026725', 'ENSGALG00010003754', 'ENSGALG00010029669',
      'ENSGALG00010003986'],
     ['ENSGALG00010011966', 'ENSGALG00010001201', 'ENSGALG00010015374', 'ENSGALG00010018313', 'ENSGALG00010021636',
      'ENSGALG00010005214'],
     ['ENSGALG00010012991', 'ENSGALG00010024129', 'ENSGALG00010024469', 'ENSGALG00010023421', 'ENSGALG00010005475',
      'ENSGALG00010014317'],
     ['ENSGALG00010011873', 'ENSGALG00010026536', 'ENSGALG00010022033', 'ENSGALG00010026830', 'ENSGALG00010009355',
      'ENSGALG00010024853'],
     ['ENSGALG00010001823', 'ENSGALG00010015645', 'ENSGALG00010009522', 'ENSGALG00010023478', 'ENSGALG00010013182',
      'ENSGALG00010017798'],
     ['ENSGALG00010027292', 'ENSGALG00010019931', 'ENSGALG00010018886', 'ENSGALG00010004907', 'ENSGALG00010001436',
      'ENSGALG00010018696'],
     ['ENSGALG00010013450', 'ENSGALG00010028194', 'ENSGALG00010014824', 'ENSGALG00010017601', 'ENSGALG00010021327',
      'ENSGALG00010021539'],
     ['ENSGALG00010005464', 'ENSGALG00010014748', 'ENSGALG00010025996', 'ENSGALG00010018287', 'ENSGALG00010012734',
      'ENSGALG00010013257'],
     ['ENSGALG00010021182', 'ENSGALG00010019967', 'ENSGALG00010028547', 'ENSGALG00010011413', 'ENSGALG00010020284',
      'ENSGALG00010028711'],
     ['ENSGALG00010016967', 'ENSGALG00010005518', 'ENSGALG00010009372', 'ENSGALG00010015392', 'ENSGALG00010017771'],
     ['ENSGALG00010027239', 'ENSGALG00010029718', 'ENSGALG00010027365', 'ENSGALG00010029772', 'ENSGALG00010021588'],
     ['ENSGALG00010022333', 'ENSGALG00010013307', 'ENSGALG00010025381', 'ENSGALG00010008380', 'ENSGALG00010005376'],
     ['ENSGALG00010018564', 'ENSGALG00010012483', 'ENSGALG00010019029', 'ENSGALG00010024144', 'ENSGALG00010004988'],
     ['ENSGALG00010009542', 'ENSGALG00010004230', 'ENSGALG00010016417', 'ENSGALG00010011384', 'ENSGALG00010011881'],
     ['ENSGALG00010013664', 'ENSGALG00010001195', 'ENSGALG00010024744', 'ENSGALG00010005087', 'ENSGALG00010018707'],
     ['ENSGALG00010004116', 'ENSGALG00010016384', 'ENSGALG00010002803', 'ENSGALG00010018396', 'ENSGALG00010008189'],
     ['ENSGALG00010010291', 'ENSGALG00010027105', 'ENSGALG00010016508', 'ENSGALG00010011499', 'ENSGALG00010024919'],
     ['ENSGALG00010022837', 'ENSGALG00010022343', 'ENSGALG00010022645', 'ENSGALG00010022990', 'ENSGALG00010022536'],
     ['ENSGALG00010000457', 'ENSGALG00010002138', 'ENSGALG00010023429', 'ENSGALG00010017918', 'ENSGALG00010017818'],
     ['ENSGALG00010003821', 'ENSGALG00010002434', 'ENSGALG00010015132', 'ENSGALG00010002196', 'ENSGALG00010018943'],
     ['ENSGALG00010027386', 'ENSGALG00010023910', 'ENSGALG00010020723', 'ENSGALG00010011662', 'ENSGALG00010020141'],
     ['ENSGALG00010028599', 'ENSGALG00010029253', 'ENSGALG00010027154', 'ENSGALG00010027722', 'ENSGALG00010029528'],
     ['ENSGALG00010029228', 'ENSGALG00010028473', 'ENSGALG00010022282', 'ENSGALG00010029480', 'ENSGALG00010023116'],
     ['ENSGALG00010023425', 'ENSGALG00010018730', 'ENSGALG00010019012', 'ENSGALG00010012707', 'ENSGALG00010011699'],
     ['ENSGALG00010018054', 'ENSGALG00010029351', 'ENSGALG00010029353', 'ENSGALG00010028088', 'ENSGALG00010001761'],
     ['ENSGALG00010021916', 'ENSGALG00010023332', 'ENSGALG00010029683', 'ENSGALG00010011992', 'ENSGALG00010013638'],
     ['ENSGALG00010023196', 'ENSGALG00010028456', 'ENSGALG00010022441', 'ENSGALG00010016672', 'ENSGALG00010022925'],
     ['ENSGALG00010012354', 'ENSGALG00010011448', 'ENSGALG00010013227', 'ENSGALG00010014558', 'ENSGALG00010025164'],
     ['ENSGALG00010002814', 'ENSGALG00010024973', 'ENSGALG00010008516', 'ENSGALG00010024871', 'ENSGALG00010011211'],
     ['ENSGALG00010029352', 'ENSGALG00010016891', 'ENSGALG00010013890', 'ENSGALG00010027919', 'ENSGALG00010015580'],
     ['ENSGALG00010015155', 'ENSGALG00010009573', 'ENSGALG00010013980', 'ENSGALG00010027166', 'ENSGALG00010027295'],
     ['ENSGALG00010016836', 'ENSGALG00010019259', 'ENSGALG00010008148', 'ENSGALG00010011400', 'ENSGALG00010016416'],
     ['ENSGALG00010027969', 'ENSGALG00010023266', 'ENSGALG00010012456', 'ENSGALG00010016542', 'ENSGALG00010029423'],
     ['ENSGALG00010001378', 'ENSGALG00010010710', 'ENSGALG00010011091', 'ENSGALG00010014704', 'ENSGALG00010019591'],
     ['ENSGALG00010013198', 'ENSGALG00010018704', 'ENSGALG00010021092', 'ENSGALG00010005172', 'ENSGALG00010007759'],
     ['ENSGALG00010011899', 'ENSGALG00010029686', 'ENSGALG00010024821', 'ENSGALG00010024136', 'ENSGALG00010021635'],
     ['ENSGALG00010027200', 'ENSGALG00010024342', 'ENSGALG00010016606', 'ENSGALG00010016651', 'ENSGALG00010002722'],
     ['ENSGALG00010024690', 'ENSGALG00010027160', 'ENSGALG00010024647', 'ENSGALG00010025438', 'ENSGALG00010028878'],
     ['ENSGALG00010009676', 'ENSGALG00010006269', 'ENSGALG00010010222', 'ENSGALG00010012436', 'ENSGALG00010006580'],
     ['ENSGALG00010001308', 'ENSGALG00010022799', 'ENSGALG00010012133', 'ENSGALG00010009724', 'ENSGALG00010015532'],
     ['ENSGALG00010004705', 'ENSGALG00010019956', 'ENSGALG00010024096', 'ENSGALG00010021720', 'ENSGALG00010027872'],
     ['ENSGALG00010029617', 'ENSGALG00010006085', 'ENSGALG00010002459', 'ENSGALG00010029756', 'ENSGALG00010019991'],
     ['ENSGALG00010013679', 'ENSGALG00010014328', 'ENSGALG00010013690', 'ENSGALG00010022460', 'ENSGALG00010015362'],
     ['ENSGALG00010009266', 'ENSGALG00010004245', 'ENSGALG00010009268', 'ENSGALG00010028270', 'ENSGALG00010027252'],
     ['ENSGALG00010006615', 'ENSGALG00010012021', 'ENSGALG00010022623', 'ENSGALG00010024426', 'ENSGALG00010006382'],
     ['ENSGALG00010013783', 'ENSGALG00010010463', 'ENSGALG00010028440', 'ENSGALG00010011649', 'ENSGALG00010010932'],
     ['ENSGALG00010004990', 'ENSGALG00010028870', 'ENSGALG00010014267', 'ENSGALG00010028096', 'ENSGALG00010029775'],
     ['ENSGALG00010017658', 'ENSGALG00010020033', 'ENSGALG00010019213', 'ENSGALG00010017264', 'ENSGALG00010003072'],
     ['ENSGALG00010027733', 'ENSGALG00010023115', 'ENSGALG00010023199', 'ENSGALG00010022427', 'ENSGALG00010027979'],
     ['ENSGALG00010019391', 'ENSGALG00010018312', 'ENSGALG00010013042', 'ENSGALG00010019059', 'ENSGALG00010024198'],
     ['ENSGALG00010015987', 'ENSGALG00010026132', 'ENSGALG00010012938', 'ENSGALG00010026088', 'ENSGALG00010004424'],
     ['ENSGALG00010004135', 'ENSGALG00010013814', 'ENSGALG00010026325', 'ENSGALG00010022957', 'ENSGALG00010027864'],
     ['ENSGALG00010001759', 'ENSGALG00010009378', 'ENSGALG00010005532', 'ENSGALG00010005660', 'ENSGALG00010028855'],
     ['ENSGALG00010029706', 'ENSGALG00010028602', 'ENSGALG00010002616', 'ENSGALG00010024890', 'ENSGALG00010023074'],
     ['ENSGALG00010020228', 'ENSGALG00010020118', 'ENSGALG00010018298', 'ENSGALG00010018819', 'ENSGALG00010018882'],
     ['ENSGALG00010012908', 'ENSGALG00010010977', 'ENSGALG00010008340', 'ENSGALG00010008075', 'ENSGALG00010021246'],
     ['ENSGALG00010007921', 'ENSGALG00010004471', 'ENSGALG00010020963', 'ENSGALG00010005012', 'ENSGALG00010021705'],
     ['ENSGALG00010003097', 'ENSGALG00010001461', 'ENSGALG00010003518', 'ENSGALG00010003077', 'ENSGALG00010003920'],
     ['ENSGALG00010027192', 'ENSGALG00010001756', 'ENSGALG00010027100', 'ENSGALG00010027616', 'ENSGALG00010026163'],
     ['ENSGALG00010029600', 'ENSGALG00010013945', 'ENSGALG00010025386', 'ENSGALG00010013241', 'ENSGALG00010012107'],
     ['ENSGALG00010017347', 'ENSGALG00010021505', 'ENSGALG00010001406', 'ENSGALG00010021425', 'ENSGALG00010021509'],
     ['ENSGALG00010010546', 'ENSGALG00010000688', 'ENSGALG00010003187', 'ENSGALG00010022302', 'ENSGALG00010003804'],
     ['ENSGALG00010015126', 'ENSGALG00010007916', 'ENSGALG00010021748', 'ENSGALG00010023052', 'ENSGALG00010028179'],
     ['ENSGALG00010026006', 'ENSGALG00010021573', 'ENSGALG00010019622', 'ENSGALG00010019291', 'ENSGALG00010017310'],
     ['ENSGALG00010016224', 'ENSGALG00010016345', 'ENSGALG00010004468', 'ENSGALG00010006344', 'ENSGALG00010003322'],
     ['ENSGALG00010024748', 'ENSGALG00010024434', 'ENSGALG00010023170', 'ENSGALG00010025976', 'ENSGALG00010023181'],
     ['ENSGALG00010016411', 'ENSGALG00010014603', 'ENSGALG00010023720', 'ENSGALG00010016303', 'ENSGALG00010009085'],
     ['ENSGALG00010020116', 'ENSGALG00010020084', 'ENSGALG00010019373', 'ENSGALG00010020843', 'ENSGALG00010003531'],
     ['ENSGALG00010027892', 'ENSGALG00010000571', 'ENSGALG00010027227', 'ENSGALG00010000205', 'ENSGALG00010022042'],
     ['ENSGALG00010020666', 'ENSGALG00010023794', 'ENSGALG00010022614', 'ENSGALG00010029938', 'ENSGALG00010027206'],
     ['ENSGALG00010001187', 'ENSGALG00010009551', 'ENSGALG00010029761', 'ENSGALG00010015388', 'ENSGALG00010009562'],
     ['ENSGALG00010017703', 'ENSGALG00010015624', 'ENSGALG00010012551', 'ENSGALG00010009461', 'ENSGALG00010015239'],
     ['ENSGALG00010012179', 'ENSGALG00010012144', 'ENSGALG00010018665', 'ENSGALG00010012696', 'ENSGALG00010021586'],
     ['ENSGALG00010020202', 'ENSGALG00010023746', 'ENSGALG00010027114', 'ENSGALG00010028157', 'ENSGALG00010023966'],
     ['ENSGALG00010021874', 'ENSGALG00010022416', 'ENSGALG00010023319', 'ENSGALG00010008289', 'ENSGALG00010022619'],
     ['ENSGALG00010005025', 'ENSGALG00010005244', 'ENSGALG00010012879', 'ENSGALG00010005412', 'ENSGALG00010021753'],
     ['ENSGALG00010025913', 'ENSGALG00010011496', 'ENSGALG00010026643', 'ENSGALG00010022981', 'ENSGALG00010026036'],
     ['ENSGALG00010029590', 'ENSGALG00010023135', 'ENSGALG00010008311', 'ENSGALG00010020184', 'ENSGALG00010024330'],
     ['ENSGALG00010017700', 'ENSGALG00010017831', 'ENSGALG00010015066', 'ENSGALG00010016807', 'ENSGALG00010016583'],
     ['ENSGALG00010014217', 'ENSGALG00010021137', 'ENSGALG00010007521', 'ENSGALG00010021623', 'ENSGALG00010001620'],
     ['ENSGALG00010021647', 'ENSGALG00010023110', 'ENSGALG00010012709', 'ENSGALG00010017595', 'ENSGALG00010023978'],
     ['ENSGALG00010016964', 'ENSGALG00010024462', 'ENSGALG00010017641', 'ENSGALG00010021661', 'ENSGALG00010004800'],
     ['ENSGALG00010020649', 'ENSGALG00010016394', 'ENSGALG00010017290', 'ENSGALG00010019130', 'ENSGALG00010021023'],
     ['ENSGALG00010024793', 'ENSGALG00010009715', 'ENSGALG00010007883', 'ENSGALG00010007584', 'ENSGALG00010007337'],
     ['ENSGALG00010006252', 'ENSGALG00010016677', 'ENSGALG00010000301', 'ENSGALG00010010855', 'ENSGALG00010010791'],
     ['ENSGALG00010016802', 'ENSGALG00010014329', 'ENSGALG00010023487', 'ENSGALG00010026434', 'ENSGALG00010022481'],
     ['ENSGALG00010015468', 'ENSGALG00010015603', 'ENSGALG00010017843', 'ENSGALG00010029150', 'ENSGALG00010016741'],
     ['ENSGALG00010023948', 'ENSGALG00010025824', 'ENSGALG00010017937', 'ENSGALG00010023126', 'ENSGALG00010025400'],
     ['ENSGALG00010015234', 'ENSGALG00010027925', 'ENSGALG00010018752', 'ENSGALG00010022280', 'ENSGALG00010022105'],
     ['ENSGALG00010028125', 'ENSGALG00010029336', 'ENSGALG00010029543', 'ENSGALG00010020705', 'ENSGALG00010028127'],
     ['ENSGALG00010027654', 'ENSGALG00010028486', 'ENSGALG00010027321', 'ENSGALG00010020257', 'ENSGALG00010029284'],
     ['ENSGALG00010020476', 'ENSGALG00010018306', 'ENSGALG00010005417', 'ENSGALG00010018604', 'ENSGALG00010019934'],
     ['ENSGALG00010000635', 'ENSGALG00010000444', 'ENSGALG00010010949', 'ENSGALG00010016452', 'ENSGALG00010006177'],
     ['ENSGALG00010029342', 'ENSGALG00010027443', 'ENSGALG00010027301', 'ENSGALG00010021528', 'ENSGALG00010029658'],
     ['ENSGALG00010021210', 'ENSGALG00010024623', 'ENSGALG00010020454', 'ENSGALG00010021088', 'ENSGALG00010015544'],
     ['ENSGALG00010017035', 'ENSGALG00010017174', 'ENSGALG00010028597', 'ENSGALG00010015931', 'ENSGALG00010016017'],
     ['ENSGALG00010005477', 'ENSGALG00010018529', 'ENSGALG00010018006', 'ENSGALG00010009367', 'ENSGALG00010009172'],
     ['ENSGALG00010018441', 'ENSGALG00010018288', 'ENSGALG00010000812', 'ENSGALG00010008285', 'ENSGALG00010016403'],
     ['ENSGALG00010021296', 'ENSGALG00010018199', 'ENSGALG00010026522', 'ENSGALG00010022221', 'ENSGALG00010021459'],
     ['ENSGALG00010011651', 'ENSGALG00010010906', 'ENSGALG00010007882', 'ENSGALG00010015695', 'ENSGALG00010027178'],
     ['ENSGALG00010020248', 'ENSGALG00010022783', 'ENSGALG00010022472', 'ENSGALG00010021514', 'ENSGALG00010024842'],
     ['ENSGALG00010019529', 'ENSGALG00010006634', 'ENSGALG00010003915', 'ENSGALG00010000720', 'ENSGALG00010007217'],
     ['ENSGALG00010008218', 'ENSGALG00010008399', 'ENSGALG00010024861', 'ENSGALG00010021529', 'ENSGALG00010021010'],
     ['ENSGALG00010020943', 'ENSGALG00010003887', 'ENSGALG00010022030', 'ENSGALG00010009275', 'ENSGALG00010015314'],
     ['ENSGALG00010024439', 'ENSGALG00010024496', 'ENSGALG00010025113', 'ENSGALG00010024590', 'ENSGALG00010026078'],
     ['ENSGALG00010017312', 'ENSGALG00010001136', 'ENSGALG00010018649', 'ENSGALG00010014940', 'ENSGALG00010018831'],
     ['ENSGALG00010023058', 'ENSGALG00010022827', 'ENSGALG00010023042', 'ENSGALG00010023215', 'ENSGALG00010022831'],
     ['ENSGALG00010018436', 'ENSGALG00010029384', 'ENSGALG00010023225', 'ENSGALG00010019298', 'ENSGALG00010028176'],
     ['ENSGALG00010024888', 'ENSGALG00010020246', 'ENSGALG00010029782', 'ENSGALG00010023408', 'ENSGALG00010020117'],
     ['ENSGALG00010007796', 'ENSGALG00010024644', 'ENSGALG00010010997', 'ENSGALG00010015810', 'ENSGALG00010003923'],
     ['ENSGALG00010012093', 'ENSGALG00010010706', 'ENSGALG00010018001', 'ENSGALG00010008343', 'ENSGALG00010020582'],
     ['ENSGALG00010021593', 'ENSGALG00010021978', 'ENSGALG00010024757', 'ENSGALG00010014167', 'ENSGALG00010014494'],
     ['ENSGALG00010013027', 'ENSGALG00010021345', 'ENSGALG00010013686', 'ENSGALG00010016913', 'ENSGALG00010009795'],
     ['ENSGALG00010015946', 'ENSGALG00010016139', 'ENSGALG00010022709', 'ENSGALG00010017980', 'ENSGALG00010029446'],
     ['ENSGALG00010027803', 'ENSGALG00010029187', 'ENSGALG00010028108', 'ENSGALG00010026335', 'ENSGALG00010000055'],
     ['ENSGALG00010023304', 'ENSGALG00010003260', 'ENSGALG00010026507', 'ENSGALG00010024598', 'ENSGALG00010008013'],
     ['ENSGALG00010016580', 'ENSGALG00010011377', 'ENSGALG00010028060', 'ENSGALG00010023909', 'ENSGALG00010027928'],
     ['ENSGALG00010017494', 'ENSGALG00010017880', 'ENSGALG00010029534', 'ENSGALG00010014122', 'ENSGALG00010015013'],
     ['ENSGALG00010010828', 'ENSGALG00010009498', 'ENSGALG00010012447', 'ENSGALG00010024694', 'ENSGALG00010018453'],
     ['ENSGALG00010025508', 'ENSGALG00010029307', 'ENSGALG00010029491', 'ENSGALG00010016763', 'ENSGALG00010021461'],
     ['ENSGALG00010017856', 'ENSGALG00010021746', 'ENSGALG00010008136', 'ENSGALG00010008426', 'ENSGALG00010008441'],
     ['ENSGALG00010016568', 'ENSGALG00010019149', 'ENSGALG00010019646', 'ENSGALG00010020667', 'ENSGALG00010019690'],
     ['ENSGALG00010006038', 'ENSGALG00010000134', 'ENSGALG00010003251', 'ENSGALG00010004591', 'ENSGALG00010003985'],
     ['ENSGALG00010027263', 'ENSGALG00010029278', 'ENSGALG00010023059', 'ENSGALG00010029573', 'ENSGALG00010016673'],
     ['ENSGALG00010013494', 'ENSGALG00010018904', 'ENSGALG00010026909', 'ENSGALG00010016177', 'ENSGALG00010001640'],
     ['ENSGALG00010005394', 'ENSGALG00010003551', 'ENSGALG00010005323', 'ENSGALG00010009447', 'ENSGALG00010027502'],
     ['ENSGALG00010024820', 'ENSGALG00010026213', 'ENSGALG00010027537', 'ENSGALG00010025621', 'ENSGALG00010029274'],
     ['ENSGALG00010013320', 'ENSGALG00010008386', 'ENSGALG00010000047', 'ENSGALG00010008047', 'ENSGALG00010024391'],
     ['ENSGALG00010021259', 'ENSGALG00010017778', 'ENSGALG00010016787', 'ENSGALG00010016904', 'ENSGALG00010016340'],
     ['ENSGALG00010012536', 'ENSGALG00010012893', 'ENSGALG00010013238', 'ENSGALG00010013412', 'ENSGALG00010012899'],
     ['ENSGALG00010014324', 'ENSGALG00010029492', 'ENSGALG00010014980', 'ENSGALG00010016209', 'ENSGALG00010012829'],
     ['ENSGALG00010010853', 'ENSGALG00010003606', 'ENSGALG00010011326', 'ENSGALG00010016614', 'ENSGALG00010009170'],
     ['ENSGALG00010018539', 'ENSGALG00010021655', 'ENSGALG00010028448', 'ENSGALG00010029677', 'ENSGALG00010021903'],
     ['ENSGALG00010001286', 'ENSGALG00010016279', 'ENSGALG00010014703', 'ENSGALG00010024776', 'ENSGALG00010002978'],
     ['ENSGALG00010013206', 'ENSGALG00010028893', 'ENSGALG00010021077', 'ENSGALG00010007938', 'ENSGALG00010018616'],
     ['ENSGALG00010018552', 'ENSGALG00010020027', 'ENSGALG00010020030', 'ENSGALG00010019811', 'ENSGALG00010020952'],
     ['ENSGALG00010017272', 'ENSGALG00010018064', 'ENSGALG00010020231', 'ENSGALG00010021087', 'ENSGALG00010019001'],
     ['ENSGALG00010016751', 'ENSGALG00010016041', 'ENSGALG00010023791', 'ENSGALG00010026900', 'ENSGALG00010001657'],
     ['ENSGALG00010008183', 'ENSGALG00010006283', 'ENSGALG00010008258', 'ENSGALG00010005817', 'ENSGALG00010007765'],
     ['ENSGALG00010001154', 'ENSGALG00010012812', 'ENSGALG00010024836', 'ENSGALG00010012648', 'ENSGALG00010000788'],
     ['ENSGALG00010016993', 'ENSGALG00010007867', 'ENSGALG00010005772', 'ENSGALG00010004760', 'ENSGALG00010005610'],
     ['ENSGALG00010014878', 'ENSGALG00010004890', 'ENSGALG00010003582', 'ENSGALG00010016878', 'ENSGALG00010006606'],
     ['ENSGALG00010002991', 'ENSGALG00010013808', 'ENSGALG00010028046', 'ENSGALG00010016383', 'ENSGALG00010016953'],
     ['ENSGALG00010024761', 'ENSGALG00010023160', 'ENSGALG00010018512', 'ENSGALG00010024438', 'ENSGALG00010025592'],
     ['ENSGALG00010004798', 'ENSGALG00010011539', 'ENSGALG00010024106', 'ENSGALG00010003348', 'ENSGALG00010001301'],
     ['ENSGALG00010026898', 'ENSGALG00010011359', 'ENSGALG00010016281', 'ENSGALG00010021679', 'ENSGALG00010020912'],
     ['ENSGALG00010012439', 'ENSGALG00010012880', 'ENSGALG00010029291', 'ENSGALG00010013787', 'ENSGALG00010011653'],
     ['ENSGALG00010023925', 'ENSGALG00010014907', 'ENSGALG00010015895', 'ENSGALG00010023327', 'ENSGALG00010020460'],
     ['ENSGALG00010007601', 'ENSGALG00010007169', 'ENSGALG00010008282', 'ENSGALG00010008072', 'ENSGALG00010001760'],
     ['ENSGALG00010009679', 'ENSGALG00010018583', 'ENSGALG00010028900', 'ENSGALG00010012362', 'ENSGALG00010026320'],
     ['ENSGALG00010029327', 'ENSGALG00010015877', 'ENSGALG00010015839', 'ENSGALG00010015923', 'ENSGALG00010025897'],
     ['ENSGALG00010005208', 'ENSGALG00010003358', 'ENSGALG00010002817', 'ENSGALG00010005154', 'ENSGALG00010005143'],
     ['ENSGALG00010026237', 'ENSGALG00010019087', 'ENSGALG00010022771', 'ENSGALG00010025512', 'ENSGALG00010022575'],
     ['ENSGALG00010017621', 'ENSGALG00010017571', 'ENSGALG00010001178', 'ENSGALG00010002401', 'ENSGALG00010017400'],
     ['ENSGALG00010011659', 'ENSGALG00010028548', 'ENSGALG00010015676', 'ENSGALG00010026061', 'ENSGALG00010007243'],
     ['ENSGALG00010014390', 'ENSGALG00010018025', 'ENSGALG00010016907', 'ENSGALG00010026686', 'ENSGALG00010028434'],
     ['ENSGALG00010016541', 'ENSGALG00010016399', 'ENSGALG00010020989', 'ENSGALG00010014272', 'ENSGALG00010015413'],
     ['ENSGALG00010005317', 'ENSGALG00010004285', 'ENSGALG00010015046', 'ENSGALG00010004650', 'ENSGALG00010021086'],
     ['ENSGALG00010011372', 'ENSGALG00010012078', 'ENSGALG00010008196', 'ENSGALG00010006903', 'ENSGALG00010015742'],
     ['ENSGALG00010018302', 'ENSGALG00010021144', 'ENSGALG00010009246', 'ENSGALG00010022698', 'ENSGALG00010023311'],
     ['ENSGALG00010022093', 'ENSGALG00010021167', 'ENSGALG00010024655', 'ENSGALG00010023460', 'ENSGALG00010013175'],
     ['ENSGALG00010020903', 'ENSGALG00010009557', 'ENSGALG00010013502', 'ENSGALG00010018618', 'ENSGALG00010021427'],
     ['ENSGALG00010021687', 'ENSGALG00010021575', 'ENSGALG00010003189', 'ENSGALG00010021798', 'ENSGALG00010022715'],
     ['ENSGALG00010029764', 'ENSGALG00010012327', 'ENSGALG00010026948', 'ENSGALG00010025103', 'ENSGALG00010029771'],
     ['ENSGALG00010017538', 'ENSGALG00010010994', 'ENSGALG00010006785', 'ENSGALG00010009491', 'ENSGALG00010016049'],
     ['ENSGALG00010019515', 'ENSGALG00010024786', 'ENSGALG00010022219', 'ENSGALG00010025245', 'ENSGALG00010020405'],
     ['ENSGALG00010009330', 'ENSGALG00010021315', 'ENSGALG00010010869', 'ENSGALG00010021741', 'ENSGALG00010013446'],
     ['ENSGALG00010023731', 'ENSGALG00010017815', 'ENSGALG00010004939', 'ENSGALG00010025910', 'ENSGALG00010011025'],
     ['ENSGALG00010018505', 'ENSGALG00010015795', 'ENSGALG00010016598', 'ENSGALG00010017147', 'ENSGALG00010018401'],
     ['ENSGALG00010013797', 'ENSGALG00010006546', 'ENSGALG00010008429', 'ENSGALG00010014399', 'ENSGALG00010017284'],
     ['ENSGALG00010004379', 'ENSGALG00010022809', 'ENSGALG00010028134', 'ENSGALG00010002391', 'ENSGALG00010000684'],
     ['ENSGALG00010000140', 'ENSGALG00010000263', 'ENSGALG00010000092', 'ENSGALG00010000306', 'ENSGALG00010000215'],
     ['ENSGALG00010018917', 'ENSGALG00010017970', 'ENSGALG00010027583', 'ENSGALG00010002348', 'ENSGALG00010007360'],
     ['ENSGALG00010024700', 'ENSGALG00010015855', 'ENSGALG00010013476', 'ENSGALG00010022345', 'ENSGALG00010025949'],
     ['ENSGALG00010022230', 'ENSGALG00010020080', 'ENSGALG00010022733', 'ENSGALG00010027383', 'ENSGALG00010022751'],
     ['ENSGALG00010011839', 'ENSGALG00010003006', 'ENSGALG00010013720', 'ENSGALG00010008431', 'ENSGALG00010008542'],
     ['ENSGALG00010025039', 'ENSGALG00010028738', 'ENSGALG00010004188', 'ENSGALG00010024910', 'ENSGALG00010010577'],
     ['ENSGALG00010017502', 'ENSGALG00010024229', 'ENSGALG00010015180', 'ENSGALG00010008476', 'ENSGALG00010008410'],
     ['ENSGALG00010025428', 'ENSGALG00010024826', 'ENSGALG00010025348', 'ENSGALG00010025980', 'ENSGALG00010025582'],
     ['ENSGALG00010024593', 'ENSGALG00010024645', 'ENSGALG00010024785', 'ENSGALG00010025960', 'ENSGALG00010024104'],
     ['ENSGALG00010010901', 'ENSGALG00010010475', 'ENSGALG00010028055', 'ENSGALG00010026588', 'ENSGALG00010027080'],
     ['ENSGALG00010027814', 'ENSGALG00010024607', 'ENSGALG00010024784', 'ENSGALG00010026484', 'ENSGALG00010025080'],
     ['ENSGALG00010021448', 'ENSGALG00010010646', 'ENSGALG00010026673', 'ENSGALG00010024502', 'ENSGALG00010021260'],
     ['ENSGALG00010003034', 'ENSGALG00010016472', 'ENSGALG00010009431', 'ENSGALG00010015124', 'ENSGALG00010007416'],
     ['ENSGALG00010020775', 'ENSGALG00010020797', 'ENSGALG00010020773', 'ENSGALG00010020486', 'ENSGALG00010020620'],
     ['ENSGALG00010021646', 'ENSGALG00010021664', 'ENSGALG00010001697', 'ENSGALG00010026143', 'ENSGALG00010026195'],
     ['ENSGALG00010013579', 'ENSGALG00010026344', 'ENSGALG00010009472', 'ENSGALG00010011726', 'ENSGALG00010007830'],
     ['ENSGALG00010003570', 'ENSGALG00010003538', 'ENSGALG00010007082', 'ENSGALG00010007339', 'ENSGALG00010027217'],
     ['ENSGALG00010010889', 'ENSGALG00010023972', 'ENSGALG00010027309', 'ENSGALG00010023981', 'ENSGALG00010022439'],
     ['ENSGALG00010029515', 'ENSGALG00010027533', 'ENSGALG00010025983', 'ENSGALG00010024474', 'ENSGALG00010023086'],
     ['ENSGALG00010021595', 'ENSGALG00010021749', 'ENSGALG00010021510', 'ENSGALG00010021435', 'ENSGALG00010021251'],
     ['ENSGALG00010009948', 'ENSGALG00010027896', 'ENSGALG00010021140', 'ENSGALG00010027130', 'ENSGALG00010027968'],
     ['ENSGALG00010029389', 'ENSGALG00010024883', 'ENSGALG00010004191', 'ENSGALG00010028453', 'ENSGALG00010029936'],
     ['ENSGALG00010029518', 'ENSGALG00010027876', 'ENSGALG00010025899', 'ENSGALG00010007114', 'ENSGALG00010022058'],
     ['ENSGALG00010029227', 'ENSGALG00010019999', 'ENSGALG00010022203', 'ENSGALG00010011345', 'ENSGALG00010025891'],
     ['ENSGALG00010029884', 'ENSGALG00010029408', 'ENSGALG00010029173', 'ENSGALG00010029466', 'ENSGALG00010029932']]

    cluster_data_0_4 = [['ENSGALG00010003614', 'ENSGALG00010003644', 'ENSGALG00010003584', 'ENSGALG00010003635', 'ENSGALG00010003575', 'ENSGALG00010003643', 'ENSGALG00010003613', 'ENSGALG00010003623', 'ENSGALG00010003598', 'ENSGALG00010003640'], ['ENSGALG00010003557', 'ENSGALG00010003565', 'ENSGALG00010003537', 'ENSGALG00010003563', 'ENSGALG00010003529', 'ENSGALG00010003576'], ['ENSGALG00010000029', 'ENSGALG00010000024', 'ENSGALG00010000011', 'ENSGALG00010000034', 'ENSGALG00010000023', 'ENSGALG00010000007'], ['ENSGALG00010015126', 'ENSGALG00010007916', 'ENSGALG00010021748', 'ENSGALG00010023052', 'ENSGALG00010028179']]
    def clusters_to_df(data):
        rows = []
        for i, sublist in enumerate(data, start=1):
            cluster_name = f"Cluster {i}"
            for species in sublist:
                # remove s__ prefix for display
                clean_species = species.replace("s__", "")
                rows.append({"Cluster": cluster_name, "Species": clean_species, "Value": 1})
        return pd.DataFrame(rows)

    df_0_4 = clusters_to_df(cluster_data_0_4)
    df_0_3 = clusters_to_df(cluster_data_0_3)
    df_0_2 = clusters_to_df(cluster_data_0_2)


    try:
        fig_0_4 = px.sunburst(df_0_4, path=["Cluster", "Species"], values="Value", title="Threshold 0.4")
        fig_0_4.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_4 = pio.to_html(
            fig_0_4,
            full_html=False,
            include_plotlyjs=False,
            config={"responsive": True},
            div_id="sunburst_04"
        )
    except:
        sunburst_html_0_4 = ""

    try:
        fig_0_3 = px.sunburst(df_0_3, path=["Cluster", "Species"], values="Value", title="Threshold 0.3")
        fig_0_3.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_3 = pio.to_html(
            fig_0_3,
            full_html=False,
            include_plotlyjs=False,
            config={"responsive": True},
            div_id="sunburst_03"
        )
    except:
        sunburst_html_0_3 = ""

    try:
        fig_0_2 = px.sunburst(df_0_2, path=["Cluster", "Species"], values="Value", title="Threshold 0.2")
        fig_0_2.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_2 = pio.to_html(
            fig_0_2,
            full_html=False,
            include_plotlyjs=False,
            config={"responsive": True},
            div_id="sunburst_02"
        )
    except:
        sunburst_html_0_2 = ""
    # 4) Render template
    return render(
        request,
        f"{host_type}/liver.html",  # e.g. "isabrownv2/bacterien.html"
        {
            "host_type": host_type.title(),
            "data_type": "liver",
            "description": "Top 100 displayed only. Gene info from Ensembl REST.",
            "tissue_types": list(tissue_files_liver.keys()),
            "sunburst_html_0_4": sunburst_html_0_4,
            "sunburst_html_0_3": sunburst_html_0_3,
            "sunburst_html_0_2": sunburst_html_0_2,

        }
    )



#### Muscle Ross
def ross_muscle_data_analysis(request):
    """
    Analyze transcriptomics data (muscle) for a given host type.
    """
    """
       Analyze transcriptomics data (ileum) for a given host type.
       """
    host_type ="ross"

    # Select the file based on host_type
    file_path = os.path.join(
        settings.BASE_DIR,
        "Avapp",
        "static",
        "Avapp",
        "csv",
        "Ross_Muscle_Final_50samples_salmon.merged.gene_counts_length_scaled.tsv"
    )

    # Initialize variables before the try block
    top_n = int(request.GET.get("top_n", 50))
    data_preview = None
    columns_preview = None
    bar_chart_html = None
    sunburst_chart_html = None
    total_sunburst_chart_html = None
    heatmap_fig_html = None
    violin_fig_html = None
    scatter_fig_html = None
    aggregate_bar_chart_html = None
    summary_stats = None
    sample_columns = []
    sample_x = None
    sample_y = None
    errors = {}
    cluster_sunburst_html = None
    highlight_immuno = False

    try:
        # Load the data
        df = pd.read_csv(file_path, sep="\t")

        # Convert all column names to strings
        df.columns = df.columns.astype(str)

        # Extract the head and first few rows as a preview
        data_preview = df.head(3).to_html(classes="table table-striped", index=False)
        columns_preview = df.columns.tolist()  # For debugging

        # Select sample columns (excluding non-sample columns)
        exclude_cols = ['gene_id', 'gene_name']
        sample_columns = [col for col in df.columns if col not in exclude_cols]

        # Compute average quantification for each gene
        df["Average"] = df[sample_columns].mean(axis=1)

        # **Add Summary Statistics**
        total_genes = df.shape[0]
        average_expression = df["Average"].mean()
        median_expression = df["Average"].median()
        max_expression = df["Average"].max()
        summary_stats = {
            "total_genes": total_genes,
            "average_expression": average_expression,
            "median_expression": median_expression,
            "max_expression": max_expression
        }

        # Now, select only the top N genes based on average expression
        df_top = df.nlargest(top_n, 'Average').copy()

        # Ensure that there are non-zero expressions in the data
        df_top = df_top[df_top["Average"] > 0]
        if df_top.empty:
            raise ValueError("No genes with non-zero average expression found in top N selection.")

        # Now, generate the total sunburst chart
        try:
            # **Reduce the number of genes further to 100**
            total_sunburst_genes = df.nlargest(100, 'Average').copy()

            # Ensure that there are non-zero expressions in the data
            total_sunburst_genes = total_sunburst_genes[total_sunburst_genes["Average"] > 0]
            if total_sunburst_genes.empty:
                raise ValueError("No genes with non-zero average expression found for total sunburst chart.")

            # Prepare data for the total sunburst chart
            melted_data_total = total_sunburst_genes.melt(
                id_vars=["gene_id", "gene_name"],
                value_vars=sample_columns,
                var_name="Sample",
                value_name="Expression"
            )
            # Remove zero expressions
            melted_data_total = melted_data_total[melted_data_total["Expression"] > 0]

            # Merge average expression into melted_data_total
            melted_data_total = melted_data_total.merge(
                total_sunburst_genes[['gene_id', 'Average']],
                on='gene_id',
                how='left'
            )

            # Check if the sum of "Expression" is greater than zero
            if melted_data_total["Expression"].sum() == 0:
                raise ValueError("Sum of Expression values is zero. Cannot normalize.")

            # Total sunburst chart with color representing average expression
            total_sunburst_chart = px.sunburst(
                melted_data_total,
                path=["gene_name", "Sample"],
                values="Expression",
                color="Average",
                color_continuous_scale="Viridis",
                color_continuous_midpoint=np.mean(melted_data_total["Average"]),
                title="Total Gene Expression Overview",
                maxdepth=2  # Reduce depth for performance
            )
            total_sunburst_chart.update_layout(
                height=600,
                width=600,
            )
            total_sunburst_chart_html = total_sunburst_chart.to_html(full_html=False)
            print("Total sunburst chart generated successfully.")
        except Exception as e:
            total_sunburst_chart_html = None
            error_message = f"Error generating total sunburst chart: {e}"
            errors['total_sunburst_error'] = error_message
            print(error_message)

        # Bar chart for top genes
        try:
            bar_chart = px.bar(
                df_top,
                x="gene_name",
                y="Average",
                hover_data=["gene_id"],
                title=f"Top {top_n} Genes by Average Quantification",
                labels={"gene_name": "Gene Name", "Average": "Average Quantification"},
            )
            bar_chart.update_layout(
                xaxis_tickangle=-45,
                template='plotly_white',
                height=600,
                width=800,
            )
            bar_chart_html = bar_chart.to_html(full_html=False)
        except Exception as e:
            bar_chart_html = None
            error_message = f"Error generating bar chart: {e}"
            errors['bar_chart_error'] = error_message
            print(error_message)

        # Sunburst chart for top N genes
        try:
            # Prepare data for sunburst chart
            melted_data_top = df_top.melt(
                id_vars=["gene_name"],
                value_vars=sample_columns,
                var_name="Sample",
                value_name="Expression"
            )
            # Remove zero expressions
            melted_data_top = melted_data_top[melted_data_top["Expression"] > 0]

            # Check if the sum of "Expression" is greater than zero
            if melted_data_top["Expression"].sum() == 0:
                raise ValueError("Sum of Expression values is zero. Cannot normalize.")

            sunburst_chart = px.sunburst(
                melted_data_top,
                path=["gene_name", "Sample"],
                values="Expression",
                color="Expression",
                color_continuous_scale="Plasma",
                title=f"Gene Expression by Sample (Top {top_n} Genes)",
                maxdepth=2  # Reduce depth for performance
            )
            sunburst_chart.update_layout(
                height=600,
                width=600,
            )
            sunburst_chart_html = sunburst_chart.to_html(full_html=False)
        except Exception as e:
            sunburst_chart_html = None
            error_message = f"Error generating sunburst chart: {e}"
            errors['sunburst_error'] = error_message
            print(error_message)

        # Heatmap
        try:
            heatmap_data = df_top.set_index("gene_name")[sample_columns]
            heatmap_fig = px.imshow(
                heatmap_data,
                labels=dict(x="Sample", y="Gene", color="Expression"),
                x=heatmap_data.columns,
                y=heatmap_data.index,
                color_continuous_scale="Viridis",
                aspect="auto",
                title=f"Heatmap of Top {top_n} Gene Expressions Across Samples"
            )
            heatmap_fig.update_layout(
                height=600,
                width=800,
            )
            heatmap_fig_html = heatmap_fig.to_html(full_html=False)
        except Exception as e:
            heatmap_fig_html = None
            error_message = f"Error generating heatmap: {e}"
            errors['heatmap_error'] = error_message
            print(error_message)

        # Violin plot
        try:
            melted_violin_data = df_top.melt(
                id_vars=["gene_id", "gene_name"],
                value_vars=sample_columns,
                var_name="Sample",
                value_name="Expression"
            )
            if melted_violin_data.empty:
                raise ValueError("Melted violin data is empty.")
            # Sample data to reduce size, if necessary
            n_sample = min(10000, len(melted_violin_data))
            melted_violin_data_sample = melted_violin_data.sample(n=n_sample, random_state=1)
            violin_fig = px.violin(
                melted_violin_data_sample,
                x="Sample",
                y="Expression",
                box=True,
                points='outliers',
                title="Distribution of Gene Expression Across Samples",
                color="Sample",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            violin_fig.update_layout(
                height=600,
                width=800,
            )
            violin_fig_html = violin_fig.to_html(full_html=False)
        except Exception as e:
            violin_fig_html = None
            error_message = f"Error generating violin plot: {e}"
            errors['violin_error'] = error_message
            print(error_message)

        # Aggregate Bar Chart
        try:
            expression_levels = df.groupby('gene_name')['Average'].sum().nlargest(10).reset_index()
            aggregate_bar_chart = px.bar(
                expression_levels,
                x='gene_name',
                y='Average',
                title='Top 10 Genes by Total Expression',
                labels={'gene_name': 'Gene Name', 'Average': 'Total Expression'},
            )
            aggregate_bar_chart.update_layout(
                xaxis_tickangle=-45,
                height=600,
                width=800,
            )
            aggregate_bar_chart_html = aggregate_bar_chart.to_html(full_html=False)
        except Exception as e:
            aggregate_bar_chart_html = None
            error_message = f"Error generating aggregate bar chart: {e}"
            errors['aggregate_bar_chart_error'] = error_message
            print(error_message)

        # Scatter plot
        try:
            if len(sample_columns) >= 2:
                # Get selected samples from GET parameters
                sample_x = request.GET.get('sample_x')
                sample_y = request.GET.get('sample_y')

                # If not provided or invalid, set defaults
                if sample_x not in sample_columns:
                    sample_x = sample_columns[0]
                if sample_y not in sample_columns:
                    sample_y = sample_columns[1]

                scatter_fig = px.scatter(
                    df_top,
                    x=sample_x,
                    y=sample_y,
                    hover_name="gene_name",
                    title=f"Gene Expression: {sample_x} vs {sample_y}",
                    labels={sample_x: f"Expression in {sample_x}", sample_y: f"Expression in {sample_y}"},
                    color="Average",
                    color_continuous_scale="Plasma"
                )
                scatter_fig.update_layout(
                    height=600,
                    width=800,
                )
                scatter_fig_html = scatter_fig.to_html(full_html=False)
            else:
                scatter_fig_html = None
                sample_x = None
                sample_y = None
                error_message = "Not enough sample columns for scatter plot."
                errors['scatter_error'] = error_message
                print(error_message)
        except Exception as e:
            scatter_fig_html = None
            error_message = f"Error generating scatter plot: {e}"
            errors['scatter_error'] = error_message
            print(error_message)

    except Exception as e:
        # Handle exceptions
        data_preview = f"<p class='text-danger'>Error processing file: {e}</p>"
        columns_preview = None
        error_message = f"Error in ileum_data_analysis: {e}"
        errors['data_error'] = error_message
        print(error_message)

    # Initialize variables
    """
       Render the muscle ross data analysis page with static options for pathways.
       """
    # List of all pathways for the dropdown
    systems = [
        "Cytoskeleton in muscle cells",
        "Ribosome",
        "Carbon metabolism",
        "Glycolysis / Gluconeogenesis",
        "Cardiac Muscle contraction",
        "Byosynthesis of amino acids",
        "Citrate cycle(TCA cycle)",
        "Motor",
        "proteins",
        "ECM - receptor",
        "interaction",
        "Focal",
        "adhesion",
        "Adrenergic",
        "signaling in cardiomyocytes",
        "Insulin",
        "signaling",
        "pathway",
        "Pentose",
        "phosphate",
        "pathway",
        "Calcium",
        "singaling",
        "pathway",
        "Starch and sucrose",
        "metabolism",
        "Fructose and mannose",
        "metabolism",
        "Pyruvate",
        "metabolism"
        ]

    # Context for rendering
    context = {
        "host_type": host_type.title(),
        "data_type": "Transcriptomics",
        "description": "Analyze transcriptomics data for Ileum samples.",
        "bar_chart": bar_chart_html,
        "total_sunburst_chart_html": total_sunburst_chart_html,
        "sunburst_chart": sunburst_chart_html,
        "heatmap_fig": heatmap_fig_html,
        "aggregate_bar_chart_html": aggregate_bar_chart_html,
        "violin_fig": violin_fig_html,
        "scatter_fig": scatter_fig_html,
        "data_preview": data_preview,
        "columns_preview": columns_preview,
        "top_n": top_n,
        "top_n_options": [10, 20, 50, 100],
        "sample_columns": sample_columns,
        "sample_x": sample_x,
        "sample_y": sample_y,
        "summary_stats": summary_stats,  # Include summary statistics in context
        "cluster_sunburst_html": cluster_sunburst_html,
        "systems": systems,
        "errors": errors,
    }

    return render(request, f"{host_type}/muscle.html", context)


# utils.py
import requests
from difflib import get_close_matches

def fetch_ensembl_id(gene_name):
    """
    Récupère l'identifiant Ensembl pour un nom de gène donné.
    """
    base_url = "https://rest.ensembl.org"
    endpoint = f"/xrefs/symbol/gallus_gallus/{gene_name}"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.get(base_url + endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Vérifier si des correspondances exactes sont trouvées
        if data:
            return data[0]['id']
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Ensembl API: {e}")
        return None

def search_with_fuzzy_matching(gene_name):
    """
    Recherche des correspondances approximatives en utilisant l'API Ensembl et le fuzzy matching.
    """
    base_url = "https://rest.ensembl.org"
    endpoint = "/xrefs/symbol/gallus_gallus"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.get(base_url + endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Extraire les noms de gènes disponibles
        gene_names = [item['display_id'] for item in data]

        # Trouver les correspondances les plus proches
        closest_matches = get_close_matches(gene_name, gene_names, n=1, cutoff=0.6)

        if closest_matches:
            closest_gene = closest_matches[0]
            return fetch_ensembl_id(closest_gene)
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Ensembl API: {e}")
        return None

def ensembl_id_lookup(request):
    gene_name = request.GET.get('gene_name', '').strip()
    if not gene_name:
        return JsonResponse({'error': 'Aucun nom de gène fourni.'}, status=400)

    # Essayer d'abord une correspondance exacte
    ensembl_id = fetch_ensembl_id(gene_name)

    # Si aucune correspondance exacte, tenter la correspondance floue
    if not ensembl_id:
        ensembl_id = search_with_fuzzy_matching(gene_name)

    if ensembl_id:
        return JsonResponse({'ensembl_id': ensembl_id})
    else:
        return JsonResponse({'error': f"Aucun identifiant Ensembl trouvé pour le gène '{gene_name}'."}, status=404)



###### muscle Isabrown
def muscle_data_analysis(request):
    """
    Analyze transcriptomics data (muscle) for a given host type.
    """
    # Select the file based on host_type
    host_type ="isabrown"
    if host_type == "ross":
        file_path = os.path.join(
            settings.BASE_DIR,
            "Avapp",
            "static",
            "Avapp",
            "csv",
            "Ross_Muscle_Final_50samples_salmon.merged.gene_counts_length_scaled.tsv"
        )
    else:
        file_path = os.path.join(
            settings.BASE_DIR,
            "Avapp",
            "static",
            "Avapp",
            "csv",
            "Isabrown_Muscle_Final_194samples_salmon.merged.gene_counts_length_scaled.tsv"
        )

    # Initialize variables before the try block
    top_n = int(request.GET.get("top_n", 50))
    data_preview = None
    columns_preview = None
    bar_chart_html = None
    sunburst_chart_html = None
    total_sunburst_chart_html = None
    heatmap_fig_html = None
    violin_fig_html = None
    scatter_fig_html = None
    summary_stats = None  # New variable for summary statistics
    sample_columns = []
    sample_x = None
    sample_y = None
    errors = {}

    try:
        # Load the data
        df = pd.read_csv(file_path, sep="\t")

        # Convert all column names to strings
        df.columns = df.columns.astype(str)

        # Extract the head and first few rows as a preview
        data_preview = df.head(3).to_html(classes="table table-striped", index=False)
        columns_preview = df.columns.tolist()  # For debugging

        # Select sample columns (excluding non-sample columns)
        exclude_cols = ['gene_id', 'gene_name']
        sample_columns = [col for col in df.columns if col not in exclude_cols]

        # Compute average quantification for each gene
        df["Average"] = df[sample_columns].mean(axis=1)

        # **Add Summary Statistics**
        total_genes = df.shape[0]
        average_expression = df["Average"].mean()
        median_expression = df["Average"].median()
        max_expression = df["Average"].max()
        summary_stats = {
            "total_genes": total_genes,
            "average_expression": average_expression,
            "median_expression": median_expression,
            "max_expression": max_expression
        }

        # Now, select only the top N genes based on average expression
        # This creates a smaller DataFrame representing the diversity
        df_top = df.nlargest(top_n, 'Average').copy()

        # Ensure that there are non-zero expressions in the data
        df_top = df_top[df_top["Average"] > 0]
        if df_top.empty:
            raise ValueError("No genes with non-zero average expression found in top N selection.")

        # Now, generate the total sunburst chart
        try:
            # **Reduce the number of genes further to 100**
            total_sunburst_genes = df.nlargest(100, 'Average').copy()

            # Ensure that there are non-zero expressions in the data
            total_sunburst_genes = total_sunburst_genes[total_sunburst_genes["Average"] > 0]
            if total_sunburst_genes.empty:
                raise ValueError("No genes with non-zero average expression found for total sunburst chart.")

            # Prepare data for the total sunburst chart
            melted_data_total = total_sunburst_genes.melt(
                id_vars=["gene_id", "gene_name"],
                value_vars=sample_columns,
                var_name="Sample",
                value_name="Expression"
            )
            # Remove zero expressions
            melted_data_total = melted_data_total[melted_data_total["Expression"] > 0]

            # Merge average expression into melted_data_total
            melted_data_total = melted_data_total.merge(
                total_sunburst_genes[['gene_id', 'Average']],
                on='gene_id',
                how='left'
            )

            # Check if the sum of "Expression" is greater than zero
            if melted_data_total["Expression"].sum() == 0:
                raise ValueError("Sum of Expression values is zero. Cannot normalize.")

            # Total sunburst chart with color representing average expression
            total_sunburst_chart = px.sunburst(
                melted_data_total,
                path=["gene_name", "Sample"],
                values="Expression",
                color="Average",
                color_continuous_scale="Viridis",
                color_continuous_midpoint=np.mean(melted_data_total["Average"]),
                title="Total Gene Expression Overview",
                maxdepth=2  # Reduce depth for performance
            )
            total_sunburst_chart.update_layout(
                height=600,
                width=600,
            )
            total_sunburst_chart_html = total_sunburst_chart.to_html(full_html=False)
            print("Total sunburst chart generated successfully.")
        except Exception as e:
            total_sunburst_chart_html = None
            error_message = f"Error generating total sunburst chart: {e}"
            errors['total_sunburst_error'] = error_message
            print(error_message)

        # Bar chart for top genes
        try:
            bar_chart = px.bar(
                df_top,
                x="gene_name",
                y="Average",
                hover_data=["gene_id"],
                title=f"Top {top_n} Genes by Average Quantification",
                labels={"gene_name": "Gene Name", "Average": "Average Quantification"},
            )
            bar_chart.update_layout(
                xaxis_tickangle=-45,
                template='plotly_white',
                height=600,
                width=800,
            )
            bar_chart_html = bar_chart.to_html(full_html=False)
        except Exception as e:
            bar_chart_html = None
            error_message = f"Error generating bar chart: {e}"
            errors['bar_chart_error'] = error_message
            print(error_message)

        # Sunburst chart for top N genes
        try:
            # Prepare data for sunburst chart
            melted_data_top = df_top.melt(
                id_vars=["gene_name"],
                value_vars=sample_columns,
                var_name="Sample",
                value_name="Expression"
            )
            # Remove zero expressions
            melted_data_top = melted_data_top[melted_data_top["Expression"] > 0]

            # Check if the sum of "Expression" is greater than zero
            if melted_data_top["Expression"].sum() == 0:
                raise ValueError("Sum of Expression values is zero. Cannot normalize.")

            sunburst_chart = px.sunburst(
                melted_data_top,
                path=["gene_name", "Sample"],
                values="Expression",
                color="Expression",
                color_continuous_scale="Plasma",
                title=f"Gene Expression by Sample (Top {top_n} Genes)",
                maxdepth=2  # Reduce depth for performance
            )
            sunburst_chart.update_layout(
                height=600,
                width=600,
            )
            sunburst_chart_html = sunburst_chart.to_html(full_html=False)
        except Exception as e:
            sunburst_chart_html = None
            error_message = f"Error generating sunburst chart: {e}"
            errors['sunburst_error'] = error_message
            print(error_message)

        # Heatmap
        try:
            heatmap_data = df_top.set_index("gene_name")[sample_columns]
            heatmap_fig = px.imshow(
                heatmap_data,
                labels=dict(x="Sample", y="Gene", color="Expression"),
                x=heatmap_data.columns,
                y=heatmap_data.index,
                color_continuous_scale="Viridis",
                aspect="auto",
                title=f"Heatmap of Top {top_n} Gene Expressions Across Samples"
            )
            heatmap_fig.update_layout(
                height=600,
                width=800,
            )
            heatmap_fig_html = heatmap_fig.to_html(full_html=False)
        except Exception as e:
            heatmap_fig_html = None
            error_message = f"Error generating heatmap: {e}"
            errors['heatmap_error'] = error_message
            print(error_message)

        # Violin plot
        try:
            melted_violin_data = df_top.melt(
                id_vars=["gene_id", "gene_name"],
                value_vars=sample_columns,
                var_name="Sample",
                value_name="Expression"
            )
            if melted_violin_data.empty:
                raise ValueError("Melted violin data is empty.")
            # Sample data to reduce size, if necessary
            n_sample = min(10000, len(melted_violin_data))
            melted_violin_data_sample = melted_violin_data.sample(n=n_sample, random_state=1)
            violin_fig = px.violin(
                melted_violin_data_sample,
                x="Sample",
                y="Expression",
                box=True,
                points='outliers',
                title="Distribution of Gene Expression Across Samples",
                color="Sample",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            violin_fig.update_layout(
                height=600,
                width=800,
            )
            violin_fig_html = violin_fig.to_html(full_html=False)
        except Exception as e:
            violin_fig_html = None
            error_message = f"Error generating violin plot: {e}"
            errors['violin_error'] = error_message
            print(error_message)
        # Aggregate Bar Chart
        try:
            expression_levels = df.groupby('gene_name')['Average'].sum().nlargest(10).reset_index()
            aggregate_bar_chart = px.bar(
                expression_levels,
                x='gene_name',
                y='Average',
                title='Top 10 Genes by Total Expression',
                labels={'gene_name': 'Gene Name', 'Average': 'Total Expression'},
            )
            aggregate_bar_chart.update_layout(
                xaxis_tickangle=-45,
                height=600,
                width=800,
            )
            aggregate_bar_chart_html = aggregate_bar_chart.to_html(full_html=False)
        except Exception as e:
            aggregate_bar_chart_html = None
            error_message = f"Error generating aggregate bar chart: {e}"
            errors['aggregate_bar_chart_error'] = error_message
            print(error_message)
        # Scatter plot
        try:
            if len(sample_columns) >= 2:
                # Get selected samples from GET parameters
                sample_x = request.GET.get('sample_x')
                sample_y = request.GET.get('sample_y')

                # If not provided or invalid, set defaults
                if sample_x not in sample_columns:
                    sample_x = sample_columns[0]
                if sample_y not in sample_columns:
                    sample_y = sample_columns[1]

                scatter_fig = px.scatter(
                    df_top,
                    x=sample_x,
                    y=sample_y,
                    hover_name="gene_name",
                    title=f"Gene Expression: {sample_x} vs {sample_y}",
                    labels={sample_x: f"Expression in {sample_x}", sample_y: f"Expression in {sample_y}"},
                    color="Average",
                    color_continuous_scale="Plasma"
                )
                scatter_fig.update_layout(
                    height=600,
                    width=800,
                )
                scatter_fig_html = scatter_fig.to_html(full_html=False)
            else:
                scatter_fig_html = None
                sample_x = None
                sample_y = None
                error_message = "Not enough sample columns for scatter plot."
                errors['scatter_error'] = error_message
                print(error_message)
        except Exception as e:
            scatter_fig_html = None
            error_message = f"Error generating scatter plot: {e}"
            errors['scatter_error'] = error_message
            print(error_message)

    except Exception as e:
        # Handle exceptions
        data_preview = f"<p class='text-danger'>Error processing file: {e}</p>"
        columns_preview = None
        error_message = f"Error in muscle_data_analysis: {e}"
        errors['data_error'] = error_message
        print(error_message)

    # Context for rendering
    context = {
        "host_type": host_type.title(),
        "data_type": "Transcriptomics",
        "description": "Analyze transcriptomics data for muscle samples.",
        "bar_chart": bar_chart_html,
        "total_sunburst_chart_html": total_sunburst_chart_html,
        "sunburst_chart": sunburst_chart_html,
        "heatmap_fig": heatmap_fig_html,
        "aggregate_bar_chart_html": aggregate_bar_chart_html,
        "violin_fig": violin_fig_html,
        "scatter_fig": scatter_fig_html,
        "data_preview": data_preview,
        "columns_preview": columns_preview,
        "top_n": top_n,
        "top_n_options": [10, 20, 50, 100],
        "sample_columns": sample_columns,
        "sample_x": sample_x,
        "sample_y": sample_y,
        "errors": errors,
        "summary_stats": summary_stats,  # Include summary statistics in context
    }

    return render(request, f"{host_type}/muscle.html", context)


############
####Liver
def liver_data_analysis(request, host_type):
    """
    Analyze transcriptomics data (muscle) for a given host type.
    """
    # Select the file based on host_type
    file_path = os.path.join(
            settings.BASE_DIR,
            "Avapp",
            "static",
            "Avapp",
            "csv",
            "Isabrown_Liver_Final_193samples_salmon.merged.gene_counts_length_scaled.tsv"
        )


    # Initialize variables before the try block
    top_n = int(request.GET.get("top_n", 50))
    data_preview = None
    columns_preview = None
    bar_chart_html = None
    sunburst_chart_html = None
    total_sunburst_chart_html = None
    heatmap_fig_html = None
    violin_fig_html = None
    scatter_fig_html = None
    summary_stats = None  # New variable for summary statistics
    sample_columns = []
    sample_x = None
    sample_y = None
    errors = {}

    try:
        # Load the data
        df = pd.read_csv(file_path, sep="\t")

        # Convert all column names to strings
        df.columns = df.columns.astype(str)

        # Extract the head and first few rows as a preview
        data_preview = df.head(3).to_html(classes="table table-striped", index=False)
        columns_preview = df.columns.tolist()  # For debugging

        # Select sample columns (excluding non-sample columns)
        exclude_cols = ['gene_id', 'gene_name']
        sample_columns = [col for col in df.columns if col not in exclude_cols]

        # Compute average quantification for each gene
        df["Average"] = df[sample_columns].mean(axis=1)

        # **Add Summary Statistics**
        total_genes = df.shape[0]
        average_expression = df["Average"].mean()
        median_expression = df["Average"].median()
        max_expression = df["Average"].max()
        summary_stats = {
            "total_genes": total_genes,
            "average_expression": average_expression,
            "median_expression": median_expression,
            "max_expression": max_expression
        }

        # Now, select only the top N genes based on average expression
        # This creates a smaller DataFrame representing the diversity
        df_top = df.nlargest(top_n, 'Average').copy()

        # Ensure that there are non-zero expressions in the data
        df_top = df_top[df_top["Average"] > 0]
        if df_top.empty:
            raise ValueError("No genes with non-zero average expression found in top N selection.")

        # Now, generate the total sunburst chart
        try:
            # **Reduce the number of genes further to 100**
            total_sunburst_genes = df.nlargest(100, 'Average').copy()

            # Ensure that there are non-zero expressions in the data
            total_sunburst_genes = total_sunburst_genes[total_sunburst_genes["Average"] > 0]
            if total_sunburst_genes.empty:
                raise ValueError("No genes with non-zero average expression found for total sunburst chart.")

            # Prepare data for the total sunburst chart
            melted_data_total = total_sunburst_genes.melt(
                id_vars=["gene_id", "gene_name"],
                value_vars=sample_columns,
                var_name="Sample",
                value_name="Expression"
            )
            # Remove zero expressions
            melted_data_total = melted_data_total[melted_data_total["Expression"] > 0]

            # Merge average expression into melted_data_total
            melted_data_total = melted_data_total.merge(
                total_sunburst_genes[['gene_id', 'Average']],
                on='gene_id',
                how='left'
            )

            # Check if the sum of "Expression" is greater than zero
            if melted_data_total["Expression"].sum() == 0:
                raise ValueError("Sum of Expression values is zero. Cannot normalize.")

            # Total sunburst chart with color representing average expression
            total_sunburst_chart = px.sunburst(
                melted_data_total,
                path=["gene_name", "Sample"],
                values="Expression",
                color="Average",
                color_continuous_scale="Viridis",
                color_continuous_midpoint=np.mean(melted_data_total["Average"]),
                title="Total Gene Expression Overview",
                maxdepth=2  # Reduce depth for performance
            )
            total_sunburst_chart.update_layout(
                height=600,
                width=600,
            )
            total_sunburst_chart_html = total_sunburst_chart.to_html(full_html=False)
            print("Total sunburst chart generated successfully.")
        except Exception as e:
            total_sunburst_chart_html = None
            error_message = f"Error generating total sunburst chart: {e}"
            errors['total_sunburst_error'] = error_message
            print(error_message)

        # Bar chart for top genes
        try:
            bar_chart = px.bar(
                df_top,
                x="gene_name",
                y="Average",
                hover_data=["gene_id"],
                title=f"Top {top_n} Genes by Average Quantification",
                labels={"gene_name": "Gene Name", "Average": "Average Quantification"},
            )
            bar_chart.update_layout(
                xaxis_tickangle=-45,
                template='plotly_white',
                height=600,
                width=800,
            )
            bar_chart_html = bar_chart.to_html(full_html=False)
        except Exception as e:
            bar_chart_html = None
            error_message = f"Error generating bar chart: {e}"
            errors['bar_chart_error'] = error_message
            print(error_message)

        # Sunburst chart for top N genes
        try:
            # Prepare data for sunburst chart
            melted_data_top = df_top.melt(
                id_vars=["gene_name"],
                value_vars=sample_columns,
                var_name="Sample",
                value_name="Expression"
            )
            # Remove zero expressions
            melted_data_top = melted_data_top[melted_data_top["Expression"] > 0]

            # Check if the sum of "Expression" is greater than zero
            if melted_data_top["Expression"].sum() == 0:
                raise ValueError("Sum of Expression values is zero. Cannot normalize.")

            sunburst_chart = px.sunburst(
                melted_data_top,
                path=["gene_name", "Sample"],
                values="Expression",
                color="Expression",
                color_continuous_scale="Plasma",
                title=f"Gene Expression by Sample (Top {top_n} Genes)",
                maxdepth=2  # Reduce depth for performance
            )
            sunburst_chart.update_layout(
                height=600,
                width=600,
            )
            sunburst_chart_html = sunburst_chart.to_html(full_html=False)
        except Exception as e:
            sunburst_chart_html = None
            error_message = f"Error generating sunburst chart: {e}"
            errors['sunburst_error'] = error_message
            print(error_message)

        # Heatmap
        try:
            heatmap_data = df_top.set_index("gene_name")[sample_columns]
            heatmap_fig = px.imshow(
                heatmap_data,
                labels=dict(x="Sample", y="Gene", color="Expression"),
                x=heatmap_data.columns,
                y=heatmap_data.index,
                color_continuous_scale="Viridis",
                aspect="auto",
                title=f"Heatmap of Top {top_n} Gene Expressions Across Samples"
            )
            heatmap_fig.update_layout(
                height=600,
                width=800,
            )
            heatmap_fig_html = heatmap_fig.to_html(full_html=False)
        except Exception as e:
            heatmap_fig_html = None
            error_message = f"Error generating heatmap: {e}"
            errors['heatmap_error'] = error_message
            print(error_message)

        # Violin plot
        try:
            melted_violin_data = df_top.melt(
                id_vars=["gene_id", "gene_name"],
                value_vars=sample_columns,
                var_name="Sample",
                value_name="Expression"
            )
            if melted_violin_data.empty:
                raise ValueError("Melted violin data is empty.")
            # Sample data to reduce size, if necessary
            n_sample = min(10000, len(melted_violin_data))
            melted_violin_data_sample = melted_violin_data.sample(n=n_sample, random_state=1)
            violin_fig = px.violin(
                melted_violin_data_sample,
                x="Sample",
                y="Expression",
                box=True,
                points='outliers',
                title="Distribution of Gene Expression Across Samples",
                color="Sample",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            violin_fig.update_layout(
                height=600,
                width=800,
            )
            violin_fig_html = violin_fig.to_html(full_html=False)
        except Exception as e:
            violin_fig_html = None
            error_message = f"Error generating violin plot: {e}"
            errors['violin_error'] = error_message
            print(error_message)
        # Aggregate Bar Chart
        try:
            expression_levels = df.groupby('gene_name')['Average'].sum().nlargest(10).reset_index()
            aggregate_bar_chart = px.bar(
                expression_levels,
                x='gene_name',
                y='Average',
                title='Top 10 Genes by Total Expression',
                labels={'gene_name': 'Gene Name', 'Average': 'Total Expression'},
            )
            aggregate_bar_chart.update_layout(
                xaxis_tickangle=-45,
                height=600,
                width=800,
            )
            aggregate_bar_chart_html = aggregate_bar_chart.to_html(full_html=False)
        except Exception as e:
            aggregate_bar_chart_html = None
            error_message = f"Error generating aggregate bar chart: {e}"
            errors['aggregate_bar_chart_error'] = error_message
            print(error_message)
        # Scatter plot
        try:
            if len(sample_columns) >= 2:
                # Get selected samples from GET parameters
                sample_x = request.GET.get('sample_x')
                sample_y = request.GET.get('sample_y')

                # If not provided or invalid, set defaults
                if sample_x not in sample_columns:
                    sample_x = sample_columns[0]
                if sample_y not in sample_columns:
                    sample_y = sample_columns[1]

                scatter_fig = px.scatter(
                    df_top,
                    x=sample_x,
                    y=sample_y,
                    hover_name="gene_name",
                    title=f"Gene Expression: {sample_x} vs {sample_y}",
                    labels={sample_x: f"Expression in {sample_x}", sample_y: f"Expression in {sample_y}"},
                    color="Average",
                    color_continuous_scale="Plasma"
                )
                scatter_fig.update_layout(
                    height=600,
                    width=800,
                )
                scatter_fig_html = scatter_fig.to_html(full_html=False)
            else:
                scatter_fig_html = None
                sample_x = None
                sample_y = None
                error_message = "Not enough sample columns for scatter plot."
                errors['scatter_error'] = error_message
                print(error_message)
        except Exception as e:
            scatter_fig_html = None
            error_message = f"Error generating scatter plot: {e}"
            errors['scatter_error'] = error_message
            print(error_message)

    except Exception as e:
        # Handle exceptions
        data_preview = f"<p class='text-danger'>Error processing file: {e}</p>"
        columns_preview = None
        error_message = f"Error in Liver_data_analysis: {e}"
        errors['data_error'] = error_message
        print(error_message)

    # Context for rendering
    context = {
        "host_type": host_type.title(),
        "data_type": "Transcriptomics",
        "description": "Analyze transcriptomics data for Liver samples.",
        "bar_chart": bar_chart_html,
        "total_sunburst_chart_html": total_sunburst_chart_html,
        "sunburst_chart": sunburst_chart_html,
        "heatmap_fig": heatmap_fig_html,
    "aggregate_bar_chart_html": aggregate_bar_chart_html,
        "violin_fig": violin_fig_html,
        "scatter_fig": scatter_fig_html,
        "data_preview": data_preview,
        "columns_preview": columns_preview,
        "top_n": top_n,
        "top_n_options": [10, 20, 50, 100],
        "sample_columns": sample_columns,
        "sample_x": sample_x,
        "sample_y": sample_y,
        "errors": errors,
        "summary_stats": summary_stats,  # Include summary statistics in context
    }

    return render(request, f"{host_type}/liver.html", context)

#######
####Ileum


def ileum_data_analysis(request, host_type='isabrown'):
    """
    Analyze transcriptomics data (ileum) for a given host type.
    """
    # Select the file based on host_type
    file_path = os.path.join(
        settings.BASE_DIR,
        "Avapp",
        "static",
        "Avapp",
        "csv",
        "Isabrown_Ileum_Final_195samples_salmon.merged.gene_counts_length_scaled.tsv"
    )

    # Initialize variables before the try block
    top_n = int(request.GET.get("top_n", 50))
    data_preview = None
    columns_preview = None
    bar_chart_html = None
    sunburst_chart_html = None
    total_sunburst_chart_html = None
    heatmap_fig_html = None
    violin_fig_html = None
    scatter_fig_html = None
    aggregate_bar_chart_html = None
    summary_stats = None
    sample_columns = []
    sample_x = None
    sample_y = None
    errors = {}
    cluster_sunburst_html = None
    highlight_immuno = False

    try:
        # Load the data
        df = pd.read_csv(file_path, sep="\t")

        # Convert all column names to strings
        df.columns = df.columns.astype(str)

        # Extract the head and first few rows as a preview
        data_preview = df.head(3).to_html(classes="table table-striped", index=False)
        columns_preview = df.columns.tolist()  # For debugging

        # Select sample columns (excluding non-sample columns)
        exclude_cols = ['gene_id', 'gene_name']
        sample_columns = [col for col in df.columns if col not in exclude_cols]

        # Compute average quantification for each gene
        df["Average"] = df[sample_columns].mean(axis=1)

        # **Add Summary Statistics**
        total_genes = df.shape[0]
        average_expression = df["Average"].mean()
        median_expression = df["Average"].median()
        max_expression = df["Average"].max()
        summary_stats = {
            "total_genes": total_genes,
            "average_expression": average_expression,
            "median_expression": median_expression,
            "max_expression": max_expression
        }

        # Now, select only the top N genes based on average expression
        df_top = df.nlargest(top_n, 'Average').copy()

        # Ensure that there are non-zero expressions in the data
        df_top = df_top[df_top["Average"] > 0]
        if df_top.empty:
            raise ValueError("No genes with non-zero average expression found in top N selection.")

        # Now, generate the total sunburst chart
        try:
            # **Reduce the number of genes further to 100**
            total_sunburst_genes = df.nlargest(100, 'Average').copy()

            # Ensure that there are non-zero expressions in the data
            total_sunburst_genes = total_sunburst_genes[total_sunburst_genes["Average"] > 0]
            if total_sunburst_genes.empty:
                raise ValueError("No genes with non-zero average expression found for total sunburst chart.")

            # Prepare data for the total sunburst chart
            melted_data_total = total_sunburst_genes.melt(
                id_vars=["gene_id", "gene_name"],
                value_vars=sample_columns,
                var_name="Sample",
                value_name="Expression"
            )
            # Remove zero expressions
            melted_data_total = melted_data_total[melted_data_total["Expression"] > 0]

            # Merge average expression into melted_data_total
            melted_data_total = melted_data_total.merge(
                total_sunburst_genes[['gene_id', 'Average']],
                on='gene_id',
                how='left'
            )

            # Check if the sum of "Expression" is greater than zero
            if melted_data_total["Expression"].sum() == 0:
                raise ValueError("Sum of Expression values is zero. Cannot normalize.")

            # Total sunburst chart with color representing average expression
            total_sunburst_chart = px.sunburst(
                melted_data_total,
                path=["gene_name", "Sample"],
                values="Expression",
                color="Average",
                color_continuous_scale="Viridis",
                color_continuous_midpoint=np.mean(melted_data_total["Average"]),
                title="Total Gene Expression Overview",
                maxdepth=2  # Reduce depth for performance
            )
            total_sunburst_chart.update_layout(
                height=600,
                width=600,
            )
            total_sunburst_chart_html = total_sunburst_chart.to_html(full_html=False)
            print("Total sunburst chart generated successfully.")
        except Exception as e:
            total_sunburst_chart_html = None
            error_message = f"Error generating total sunburst chart: {e}"
            errors['total_sunburst_error'] = error_message
            print(error_message)

        # Bar chart for top genes
        try:
            bar_chart = px.bar(
                df_top,
                x="gene_name",
                y="Average",
                hover_data=["gene_id"],
                title=f"Top {top_n} Genes by Average Quantification",
                labels={"gene_name": "Gene Name", "Average": "Average Quantification"},
            )
            bar_chart.update_layout(
                xaxis_tickangle=-45,
                template='plotly_white',
                height=600,
                width=800,
            )
            bar_chart_html = bar_chart.to_html(full_html=False)
        except Exception as e:
            bar_chart_html = None
            error_message = f"Error generating bar chart: {e}"
            errors['bar_chart_error'] = error_message
            print(error_message)

        # Sunburst chart for top N genes
        try:
            # Prepare data for sunburst chart
            melted_data_top = df_top.melt(
                id_vars=["gene_name"],
                value_vars=sample_columns,
                var_name="Sample",
                value_name="Expression"
            )
            # Remove zero expressions
            melted_data_top = melted_data_top[melted_data_top["Expression"] > 0]

            # Check if the sum of "Expression" is greater than zero
            if melted_data_top["Expression"].sum() == 0:
                raise ValueError("Sum of Expression values is zero. Cannot normalize.")

            sunburst_chart = px.sunburst(
                melted_data_top,
                path=["gene_name", "Sample"],
                values="Expression",
                color="Expression",
                color_continuous_scale="Plasma",
                title=f"Gene Expression by Sample (Top {top_n} Genes)",
                maxdepth=2  # Reduce depth for performance
            )
            sunburst_chart.update_layout(
                height=600,
                width=600,
            )
            sunburst_chart_html = sunburst_chart.to_html(full_html=False)
        except Exception as e:
            sunburst_chart_html = None
            error_message = f"Error generating sunburst chart: {e}"
            errors['sunburst_error'] = error_message
            print(error_message)

        # Heatmap
        try:
            heatmap_data = df_top.set_index("gene_name")[sample_columns]
            heatmap_fig = px.imshow(
                heatmap_data,
                labels=dict(x="Sample", y="Gene", color="Expression"),
                x=heatmap_data.columns,
                y=heatmap_data.index,
                color_continuous_scale="Viridis",
                aspect="auto",
                title=f"Heatmap of Top {top_n} Gene Expressions Across Samples"
            )
            heatmap_fig.update_layout(
                height=600,
                width=800,
            )
            heatmap_fig_html = heatmap_fig.to_html(full_html=False)
        except Exception as e:
            heatmap_fig_html = None
            error_message = f"Error generating heatmap: {e}"
            errors['heatmap_error'] = error_message
            print(error_message)

        # Violin plot
        try:
            melted_violin_data = df_top.melt(
                id_vars=["gene_id", "gene_name"],
                value_vars=sample_columns,
                var_name="Sample",
                value_name="Expression"
            )
            if melted_violin_data.empty:
                raise ValueError("Melted violin data is empty.")
            # Sample data to reduce size, if necessary
            n_sample = min(10000, len(melted_violin_data))
            melted_violin_data_sample = melted_violin_data.sample(n=n_sample, random_state=1)
            violin_fig = px.violin(
                melted_violin_data_sample,
                x="Sample",
                y="Expression",
                box=True,
                points='outliers',
                title="Distribution of Gene Expression Across Samples",
                color="Sample",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            violin_fig.update_layout(
                height=600,
                width=800,
            )
            violin_fig_html = violin_fig.to_html(full_html=False)
        except Exception as e:
            violin_fig_html = None
            error_message = f"Error generating violin plot: {e}"
            errors['violin_error'] = error_message
            print(error_message)

        # Aggregate Bar Chart
        try:
            expression_levels = df.groupby('gene_name')['Average'].sum().nlargest(10).reset_index()
            aggregate_bar_chart = px.bar(
                expression_levels,
                x='gene_name',
                y='Average',
                title='Top 10 Genes by Total Expression',
                labels={'gene_name': 'Gene Name', 'Average': 'Total Expression'},
            )
            aggregate_bar_chart.update_layout(
                xaxis_tickangle=-45,
                height=600,
                width=800,
            )
            aggregate_bar_chart_html = aggregate_bar_chart.to_html(full_html=False)
        except Exception as e:
            aggregate_bar_chart_html = None
            error_message = f"Error generating aggregate bar chart: {e}"
            errors['aggregate_bar_chart_error'] = error_message
            print(error_message)

        # Scatter plot
        try:
            if len(sample_columns) >= 2:
                # Get selected samples from GET parameters
                sample_x = request.GET.get('sample_x')
                sample_y = request.GET.get('sample_y')

                # If not provided or invalid, set defaults
                if sample_x not in sample_columns:
                    sample_x = sample_columns[0]
                if sample_y not in sample_columns:
                    sample_y = sample_columns[1]

                scatter_fig = px.scatter(
                    df_top,
                    x=sample_x,
                    y=sample_y,
                    hover_name="gene_name",
                    title=f"Gene Expression: {sample_x} vs {sample_y}",
                    labels={sample_x: f"Expression in {sample_x}", sample_y: f"Expression in {sample_y}"},
                    color="Average",
                    color_continuous_scale="Plasma"
                )
                scatter_fig.update_layout(
                    height=600,
                    width=800,
                )
                scatter_fig_html = scatter_fig.to_html(full_html=False)
            else:
                scatter_fig_html = None
                sample_x = None
                sample_y = None
                error_message = "Not enough sample columns for scatter plot."
                errors['scatter_error'] = error_message
                print(error_message)
        except Exception as e:
            scatter_fig_html = None
            error_message = f"Error generating scatter plot: {e}"
            errors['scatter_error'] = error_message
            print(error_message)

    except Exception as e:
        # Handle exceptions
        data_preview = f"<p class='text-danger'>Error processing file: {e}</p>"
        columns_preview = None
        error_message = f"Error in ileum_data_analysis: {e}"
        errors['data_error'] = error_message
        print(error_message)

    # Initialize variables
    """
       Render the Ileum data analysis page with static options for pathways.
       """
    # List of all pathways for the dropdown
    systems = [
        "PPAR signaling pathway",
        "Influenza A",
        "Salmonella infection",
        "Cytoskeleton in muscle cells",
        "Ribosome",
        "Carbon metabolism",
        "Glycolysis / Gluconeogenesis",
        "Biosynthesis of amino acids",
        "Citrate cycle (TCA cycle)",
        "Focal adhesion",
        "Adherens junction",
        "Regulation of actin cytoskeleton",
        "Protein processing in endoplasmic reticulum",
        "Tight junction"
    ]

    # Context for rendering
    context = {
        "host_type": host_type.title(),
        "data_type": "Transcriptomics",
        "description": "Analyze transcriptomics data for Ileum samples.",
        "bar_chart": bar_chart_html,
        "total_sunburst_chart_html": total_sunburst_chart_html,
        "sunburst_chart": sunburst_chart_html,
        "heatmap_fig": heatmap_fig_html,
        "aggregate_bar_chart_html": aggregate_bar_chart_html,
        "violin_fig": violin_fig_html,
        "scatter_fig": scatter_fig_html,
        "data_preview": data_preview,
        "columns_preview": columns_preview,
        "top_n": top_n,
        "top_n_options": [10, 20, 50, 100],
        "sample_columns": sample_columns,
        "sample_x": sample_x,
        "sample_y": sample_y,
        "summary_stats": summary_stats,  # Include summary statistics in context
        "cluster_sunburst_html": cluster_sunburst_html,
        "systems": systems,
        "errors": errors,
    }

    return render(request, f"{host_type}/ileum.html", context)

#######
##Hilight sunburst
def plotly_sunburst(file, title, highlight=[]):
    """
    Create a Plotly Sunburst chart from a CSV file, with an option to highlight certain genes.

    Parameters:
    - file (str): Path to the CSV file containing the data.
    - title (str): Title of the Sunburst chart.
    - highlight (list): List of genes to highlight.

    Returns:
    - dict: Data and layout dictionaries for Plotly Sunburst chart.
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file, sep=',', header=0)
        df.columns = ['Cluster', 'Genes']  # Assuming 'Cluster' and 'Genes' as columns

        # Prepare data for the sunburst chart
        fig = px.sunburst(
            df,
            path=['Cluster', 'Genes'],
            color='Genes',
            color_discrete_sequence=px.colors.qualitative.Set3,
            title=title,
        )

        # Highlight genes
        if highlight:
            colors = ['red' if gene in highlight else 'lightgrey' for gene in df['Genes']]
            fig.update_traces(marker=dict(colors=colors))

        # Convert the figure to JSON data
        sunburst_data = fig.to_plotly_json()
        return {"status": "success", "data": sunburst_data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

### fetch selection system suburst illeum
def fetch_sunburst_data_ross_muscle(request):
    """
    Handle AJAX requests to fetch Sunburst chart data dynamically.
    """
    # List of immune pathways
    immune_pathways = ["Cytoskeleton in muscle cells"]

    # Get the selected option from query parameters
    selected_option = request.GET.get('selected_option', None)

    # Initialize pathway Sunburst data
    pathway_sunburst_data = None

    try:
        # File path for the immune cluster file
        immuno_file_path = os.path.join(
            settings.BASE_DIR,
            "Avapp",
            "static",
            "Avapp",
            "csv",
            "select_muscleross.csv"
        )

        # Load the immune cluster file
        if os.path.exists(immuno_file_path):
            clusters_df = pd.read_csv(immuno_file_path)

            # Ensure required columns exist
            cluster_gene_column = 'Genes'
            cluster_cluster_column = 'Cluster'

            if cluster_gene_column not in clusters_df.columns or cluster_cluster_column not in clusters_df.columns:
                raise ValueError(f"File must contain '{cluster_gene_column}' and '{cluster_cluster_column}' columns.")

            # Generate Sunburst chart only for immune pathways
            if selected_option in immune_pathways:
                cluster_sunburst = px.sunburst(
                    clusters_df,
                    path=[cluster_cluster_column, cluster_gene_column],
                    title=f"{selected_option} - Ross muscle Cluster Sunburst",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                )
                cluster_sunburst.update_layout(
                    height=600,
                    width=600,
                    margin=dict(t=40, l=0, r=0, b=0)
                )

                # Ensure JSON serialization compatibility by converting NumPy objects to lists
                pathway_sunburst_data = json.loads(json.dumps(cluster_sunburst.to_dict(), default=lambda x: x.tolist() if isinstance(x, np.ndarray) else x))
                return JsonResponse({"status": "success", "data": pathway_sunburst_data})

    except Exception as e:
        print(f"Error generating pathway sunburst: {e}")
        return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "No data found for the selected pathway."})

### fetch selection system suburst illeum
def fetch_sunburst_data(request):
    """
    Handle AJAX requests to fetch Sunburst chart data dynamically.
    """
    # List of immune pathways
    immune_pathways = ["PPAR signaling pathway", "Influenza A", "Salmonella infection"]

    # Get the selected option from query parameters
    selected_option = request.GET.get('selected_option', None)

    # Initialize pathway Sunburst data
    pathway_sunburst_data = None

    try:
        # File path for the immune cluster file
        immuno_file_path = os.path.join(
            settings.BASE_DIR,
            "Avapp",
            "static",
            "Avapp",
            "csv",
            "select_immuno_clusters.csv"
        )

        # Load the immune cluster file
        if os.path.exists(immuno_file_path):
            clusters_df = pd.read_csv(immuno_file_path)

            # Ensure required columns exist
            cluster_gene_column = 'Genes'
            cluster_cluster_column = 'Cluster'

            if cluster_gene_column not in clusters_df.columns or cluster_cluster_column not in clusters_df.columns:
                raise ValueError(f"File must contain '{cluster_gene_column}' and '{cluster_cluster_column}' columns.")

            # Generate Sunburst chart only for immune pathways
            if selected_option in immune_pathways:
                cluster_sunburst = px.sunburst(
                    clusters_df,
                    path=[cluster_cluster_column, cluster_gene_column],
                    title=f"{selected_option} - Immune Cluster Sunburst",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                )
                cluster_sunburst.update_layout(
                    height=600,
                    width=600,
                    margin=dict(t=40, l=0, r=0, b=0)
                )

                # Ensure JSON serialization compatibility by converting NumPy objects to lists
                pathway_sunburst_data = json.loads(json.dumps(cluster_sunburst.to_dict(), default=lambda x: x.tolist() if isinstance(x, np.ndarray) else x))
                return JsonResponse({"status": "success", "data": pathway_sunburst_data})

    except Exception as e:
        print(f"Error generating pathway sunburst: {e}")
        return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "No data found for the selected pathway."})
###########
@login_required
def generate_scatterplot(df):
    # Generate scatter plot using Bokeh
    p = figure(title="Scatter Plot", x_axis_label='X', y_axis_label='Y')
    p.scatter(df['x'], df['y'], size=10, color='navy')

    # Generate the HTML and JavaScript code for the plot
    plot_script, plot_div = components(p)

    # Generate a dictionary containing the plot HTML
    plot_html = {
        'plot_script': plot_script,
        'plot_div': plot_div,
        'bokeh_js': CDN.render_js(),
        'bokeh_css': CDN.render_css()
    }
    return plot_html


@login_required
def plot(request):
    # Retrieve data from PostgreSQL using Django's ORM
    data = Host.objects.all().values('idhost', 'growthroom')
    #
    # Create a bar chart
    x = [d['idhost'] for d in data]
    y = [d['growthroom'] for d in data]
    #
    trace = go.Scatter(x=x, y=y, mode='lines', name='My Data')
    layout = go.Layout(title='My Plot', xaxis={'title': 'IdHost'}, yaxis={'title': 'Growthroom'})
    #
    fig = go.Figure(data=[trace], layout=layout)
    div = opy.plot(fig, auto_open=False, output_type='div')
    #
    return render(request, 'bar_chart.html', {'plot_div': div})


def index(request):
    return render(request, 'avapp.html')
    # return HttpResponse("AvApp is running!!!")


@login_required
def showdata_analysis(request):
    results = Analysis.objects.all()
    return render(request, 'analysis.html', {"dataAnalysis": results})


@login_required
def showdata_study(request):
    results = Study.objects.all()
    return render(request, 'study.html', {"dataAnalysis": results})


@login_required
def showdata_feature(request):
    results = Feature.objects.all()
    # results = Feature.objects.get(pk=1)
    return render(request, 'features.html', {"dataFeature": results})


@login_required
def showdata_penhasfeature(request, entry_id):
    # pen = get_object_or_404(Pen, idpen=entry_id)
    pen = Pen.objects.get(idpen=entry_id)
    penhasfeature = pen.penhasfeature_set.all().select_related('feature_idfeature')
    # pens = Pen.objects.prefetch_related('penhasfeature_set__feature_idfeature').all()
    # related_data = penhasfeature.related_data
    # context = {'penhasfeature': penhasfeature, 'related_data': related_data}
    context = {'penhasfeature': penhasfeature}
    return render(request, 'penhasfeature.html', context)


@login_required
def showdata_hostsample(request, entry_id):
    # pen = get_object_or_404(Pen, idpen=entry_id)
    host = Host.objects.get(idhost=entry_id)
    samples = host.sample_set.all()
    # related_data = penhasfeature.related_data
    context = {'samples': samples, 'host': host}
    return render(request, 'hostsample.html', context)


@login_required
def showdata_pen(request):
    results = Pen.objects.all()
    entries = Pen.objects.all()
    data = {'idpen': [], 'trt': [], 'donorhen': [], 'dietstarter': []}
    for entry in entries:
        data['idpen'].append(entry.idpen)
        data['trt'].append(entry.trt)
        data['donorhen'].append(entry.donorhen)
        data['dietstarter'].append(entry.dietstarter)
    df = pandas.DataFrame(data)
    # results = Feature.objects.get(pk=1)

    # Convert the DataFrame to an HTML table
    table_html = df.to_html(index=False)

    return render(request, 'pen.html', {"dataPen": results, "table_html": table_html})


@login_required
def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


class HostFilterView(LoginRequiredMixin, View):
    # def showdata_host(request):
    #     results = Host.objects.all()
    #     # results = Feature.objects.get(pk=1)
    #     return render(request, 'host.html', {"dataHost": results, "lenhost": len(results)})
    def get(self, request):
        results = Host.objects.all()
        return render(request, 'host.html', {"dataHost": results, "lenhost": len(results)})


# test digital host
class DigitalHostFilterView(LoginRequiredMixin, View):
    # def showdata_host(request):
    #     results = Host.objects.all()
    #     # results = Feature.objects.get(pk=1)
    #     return render(request, 'host.html', {"dataHost": results, "lenhost": len(results)})
    def get(self, request):
        results = Host.objects.all()
        return render(request, 'Digitalhost.html', {"dataHost": results, "lenhost": len(results)})

class DigitalHostFilterViewv2(LoginRequiredMixin, View):
    # def showdata_host(request):
    #     results = Host.objects.all()
    #     # results = Feature.objects.get(pk=1)
    #     return render(request, 'host.html', {"dataHost": results, "lenhost": len(results)})
    def get(self, request):
        results = Host.objects.all()
        return render(request, 'Digitalhostv2.html', {"dataHost": results, "lenhost": len(results)})

def host_detail(request, host_type):
    # Define study features
    study_features = {
        "Poc1": [
            "Block", "FCR_D0_7", "FCR_D0_14", "FCR_D0_21", "FCR_D0_28", "FCR_D0_35"
        ],
        "Poc2": [
            "FCR_D0_7", "FCR_D0_14", "FCR_D0_21", "FCR_D0_28", "FCR_D0_35",
            "Study_Day", "Feed_consumed_D0_D7", "Feed_consumed_D0_D14", "Feed_consumed_D0_D21",
            "Feed_consumed_D0_D28", "Feed_consumed_D0_D35", "Feed_consumed_D0_D42", "FCR_D0_42"
        ],
        "Disco1": [
            "Adj_Feed_Gain_D0_D9", "Adj_Feed_Gain_D0_D14", "Adj_Feed_Gain_D0_D21", "Adj_Feed_Gain_D0_D28",
            "Adj_Feed_Gain_D0_D35", "Adj_Feed_Gain_D14_D21", "Adj_Feed_Gain_D14_D28", "Adj_Feed_Gain_D14_D35"
        ]
    }

    # Feature ranges with all min values set to 0
    feature_ranges = {
        "AvgBirdWeight_D0": {"min": 0, "max": 1.0},
        "AvgBirdWeight_D14": {"min": 0, "max": 2.0},
        "AvgBirdWeight_D21": {"min": 0, "max": 2.5},
        "AvgBirdWeight_D28": {"min": 0, "max": 3.0},
        "AvgBirdWeight_D35": {"min": 0, "max": 3.5},
        "AvgBirdWeight_D7": {"min": 0, "max": 0.5},
        "Bird_weight_D36": {"min": 0, "max": 4.0},

        "AvgBW_D14": {"min": 0, "max": 1.5},
        "AvgBW_D21": {"min": 0, "max": 2.0},
        "AvgBW_D28": {"min": 0, "max": 3.0},
        "AvgBW_D35": {"min": 0, "max": 3.5},
        "AvgBW_D42": {"min": 0, "max": 4.0},
        "AvgBW_D7": {"min": 0, "max": 0.5},
        "IndBW_D14": {"min": 0, "max": 1.5},
        "IndBW_D28": {"min": 0, "max": 3.0},
        "IndBW_D42": {"min": 0, "max": 4.0},

        "BirdWeight_D0": {"min": 0, "max": 1.0},
        "BirdWeight_D9": {"min": 0, "max": 1.5},
        "BirdWeight_D21": {"min": 0, "max": 2.0},
        "BirdWeight_D35": {"min": 0, "max": 3.0},
    }

    return render(request, "host_detail.html", {
        "host_type": host_type,
        "study_features": study_features,
        "feature_ranges": feature_ranges
    })
## host details html  ###

def construct_query(request):
    if request.method == "POST":
        # Définir les filtres de caractéristiques pour chaque étude
        study_features = {
            "Poc1": [
                "Block", "FCR_D0_7", "FCR_D0_14", "FCR_D0_21", "FCR_D0_28", "FCR_D0_35"
            ],
            "Poc2": [
                "FCR_D0_7", "FCR_D0_14", "FCR_D0_21", "FCR_D0_28", "FCR_D0_35",
                "Study_Day", "Feed_consumed_D0_D7", "Feed_consumed_D0_D14", "Feed_consumed_D0_D21",
                "Feed_consumed_D0_D28", "Feed_consumed_D0_D35", "Feed_consumed_D0_D42", "FCR_D0_42"
            ],
            "Disco1": [
                "Adj_Feed_Gain_D0_D9", "Adj_Feed_Gain_D0_D14", "Adj_Feed_Gain_D0_D21", "Adj_Feed_Gain_D0_D28",
                "Adj_Feed_Gain_D0_D35", "Adj_Feed_Gain_D14_D21", "Adj_Feed_Gain_D14_D28", "Adj_Feed_Gain_D14_D35"
            ]
        }

        # Récupérer les études sélectionnées
        selected_studies = request.POST.getlist("studies")
        filters = {}

        for study in selected_studies:
            selected_features = request.POST.getlist(f"{study}_features")
            filters[study] = []

            for feature in selected_features:
                # Capturer les valeurs min et max pour chaque caractéristique
                min_value = request.POST.get(f"{study}_{feature}_min")
                max_value = request.POST.get(f"{study}_{feature}_max")

                # Si les valeurs min et max ne sont pas spécifiées, omettre les plages
                if min_value and max_value:
                    filters[study].append({
                        "feature": feature,
                        "min": min_value,
                        "max": max_value
                    })
                else:
                    filters[study].append({
                        "feature": feature,
                        "min": None,
                        "max": None
                    })

        # Construire la chaîne de requête
        query_params = [f"studies={'|'.join(selected_studies)}"]

        for study, feature_details in filters.items():
            feature_queries = []
            for detail in feature_details:
                if detail['min'] and detail['max']:
                    feature_query = f"{detail['feature']}:{detail['min']}-{detail['max']}"
                else:
                    feature_query = detail['feature']
                feature_queries.append(feature_query)

            if feature_queries:
                query_params.append(f"{study}_features={'|'.join(feature_queries)}")

        query_string = "&".join(query_params)

        # Redirection vers Streamlit
        return HttpResponseRedirect(f"http://localhost:8502/?{query_string}")

    return HttpResponse("Invalid request method", status=405)



####
def get_features_by_study(request):
    study_ids = request.GET.getlist('study_ids[]')  # Get multiple study IDs from the AJAX request

    if study_ids:
        # Filter hosts by selected study IDs
        hosts_in_study = Host.objects.filter(study_idstudy__in=study_ids).values_list('idhost', flat=True)

        # Use hosts to filter relevant Featurefacttable entries and fetch associated features
        features = Featurefacttable.objects.filter(host_idhost__in=hosts_in_study).values(
            'feature_idfeature__featurename', 'feature_idfeature__idfeature'
        ).distinct()

        # Prepare a response with unique feature names and their IDs
        feature_data = [
            {'name': feature['feature_idfeature__featurename'], 'id': feature['feature_idfeature__idfeature']}
            for feature in features
        ]

        return JsonResponse(feature_data, safe=False)

    return JsonResponse({'error': 'No valid study IDs provided'}, status=400)

def filter_data_by_features(request):
    if request.method == "POST":
        data = json.loads(request.body)
        filters = data.get('filters', [])

        # Start with an initial queryset and filter based on each feature's min and max values
        queryset = Featurefacttable.objects.all()

        # Apply each filter as a chained queryset filter
        for f in filters:
            feature_id = f.get('feature_id')
            min_value = f.get('min')
            max_value = f.get('max')

            # Apply range filter
            if min_value and max_value:
                queryset = queryset.filter(feature_idfeature=feature_id, value__gte=min_value, value__lte=max_value)
            elif min_value:
                queryset = queryset.filter(feature_idfeature=feature_id, value__gte=min_value)
            elif max_value:
                queryset = queryset.filter(feature_idfeature=feature_id, value__lte=max_value)

        # Convert queryset to a list of dictionaries
        data = list(queryset.values('host_idhost__tag', 'feature_idfeature__featurename', 'value'))

        return JsonResponse(data, safe=False)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
#######################
def filter_data_by_feature(request):
    feature_id = request.GET.get('feature_id')

    if feature_id:
        # Filter data based on the selected feature ID
        filtered_data = Featurefacttable.objects.filter(feature_idfeature=feature_id).values(
            'host_idhost__tag', 'feature_idfeature__featurename', 'value'
        )

        # Convert queryset to a list of dictionaries
        data = list(filtered_data)

        return JsonResponse(data, safe=False)

    return JsonResponse({'error': 'Invalid feature ID provided'}, status=400)

class SchemaOverview(LoginRequiredMixin, View):
    # def showdata_host(request):
    #     results = Host.objects.all()
    #     # results = Feature.objects.get(pk=1)
    #     return render(request, 'host.html', {"dataHost": results, "lenhost": len(results)})
    def get(self, request):
        return render(request, 'schemaoverview.html')

# def index1(request):
@login_required
def showdata_hosthaspen(request, entry_id):
    host = get_object_or_404(Host, idhost=entry_id)
    # host = Host.objects.get(idhost=entry_id)
    hosthaspen = host.hosthaspen_set.all().select_related('pen_idpen')
    samples = host.sample_set.all()
    # related_data = penhasfeature.related_data
    # related_data = penhasfeature.related_data
    # context = {'penhasfeature': penhasfeature, 'related_data': related_data}
    context = {'hosthaspen': hosthaspen, 'dataHost': host, 'samples': samples}
    return render(request, 'hosthaspen.html', context)


#     latest_question_list = Feature.objects.all()
#     template = loader.get_template("templates/Index.html")
#     context = {
#         "latest_question_list": latest_question_list,
#     }
#     return HttpResponse(template.render(context, request))


# def visualize_data(request):
#     if request.method == 'POST':
#         form = MyForm(request.POST)
#         if form.is_valid():
#             selected_data = request.cleaned_data('idhost','tag')
#             import pdb
#             pdb.set_trace()
#             # Assume 'selected_data' is a list of strings representing the selected data
#             # Here, we're just using a dummy dataset and generating a bar chart
#             print(selected_data)
#             # data = pandas.DataFrame({
#             #     'Data': ['Data 1', 'Data 2', 'Data 3', 'Data 4', 'Data 5'],
#             #     'Values': [10, 7, 15, 12, 9]
#             # })
#             # data_to_visualize = data[data['Data']]
#             plt.bar(selected_data['idhost'], selected_data['tag'])
#             plt.xlabel('idhost')
#             plt.ylabel('tag')
#             plt.title('Selected Data Visualization')
#             plt.show()
#             return render(request, 'visualization.html')
#     else:
#         return render(request, 'data_form.html')
@login_required
def visualize_data(request):
    if request.method == 'POST':
        form = DataForm(request.POST)
        #   import pdb
        #         pdb.set_trace()
        if form.is_valid():
            data = form.cleaned_data
            # do something with selected_data
            # for example, use it to filter a query to retrieve the desired data
            # or retrieve the data from a previously retrieved dataframe
            # then create a visualization based on the selected data
            # and pass it to the template as a base64-encoded image
            fig = plt.figure(figsize=(6, 4))
            plt.plot([1, 2, 3, 4], [1, 4, 2, 3])
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            string = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()

            data = Host.objects.all().values('idhost', 'tag')

            x = [d['idhost'] for d in data]
            y = [d['tag'] for d in data]
            p = figure(title="Your Bokeh Graph Title")
            p.line(x, y)
            script, div = components(p)

            return render(request, 'bokeh.html', {'script': script, 'form': form, 'plot': string, 'div': div})

            # return render(request, 'visualization.html', {'form': form, 'selected_data': selected_data, 'plot': string})
    else:
        form = DataForm()
    return render(request, 'data_form.html', {'form': form})


@login_required
def my_view(request):
    if request.method == 'POST':
        form = MyForm(request.POST)
        if form.is_valid():
            my_field_value = form.cleaned_data['idhost']
            # do something with my_field_value
            return render(request, 'success.html')
    else:
        form = MyForm()
    return render(request, 'data_form.html', {'form': form})
