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
from django.db.models.fields.json import KeyTextTransform
from django.core import serializers
from django.shortcuts import render, get_object_or_404, redirect
# Create your views here.
from django.http import HttpResponse
from Avapp.models import Analysis, Feature, Pen, PenHasFeature, Host, Sample, Study, Abundancefacttable, Taxons
from django.template import loader
from django.db.models import Prefetch
import matplotlib
#from django.utils.baseconv import base64

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
from .models import Featurefacttable, Host, Feature, MetabCorrelation, AcidCorrelation
from django.shortcuts import render

# Nk Network imports
import time
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
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
def ross_detailv2(request):
    return render(request, 'rossv2.html')

@login_required
def isabrown_detail(request):
    return render(request, 'isabrown.html')


@login_required
def ross_detail(request):
    return render(request, 'ross.html')


@login_required
def process_datav2(request, host_type, data_type):
    return render(request, f"{host_type}/ileum.html")


@login_required
def process_dataileumv2(request, host_type, data_type):
    return render(request, f"{host_type}/ileum.html")


@login_required
def process_datamusclev2(request, host_type, data_type):
    return render(request, f"{host_type}/muscle.html")


@login_required
def process_datamoleculev2(request, host_type, data_type):
    return render(request, f"{host_type}/molecule.html")


@login_required
def process_dataliverv2(request, host_type, data_type):
    return render(request, f"{host_type}/liver.html")


@login_required
def process_databacteryv2(request, host_type, data_type):
    return render(request, f"{host_type}/bacterien.html")

@login_required
def process_databacteryv2_ross(request, host_type, data_type):
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
        file_path = os.path.join(settings.BASE_DIR, "Avapp", "static", "Avapp", "csv",
                                 "Sylph_MoARossFull_estimatedCounts.tsv")
    else:
        file_path = os.path.join(settings.BASE_DIR, "Avapp", "static", "Avapp", "csv",
                                 "Sylph_MoAIsaFull_estimatedCounts.tsv")

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


#####################V2 ######################""""""
# Mapping Tissue -> CSV
tissue_files = {
    "Ileum": "otu_to_ileum.csv",
    "Muscle": "otu_to_muscle.csv",
    "Liver": "otu_to_liver.csv",
    "Otu": "otu_to_otu.csv",
    "Metabolomic": "otu_to_metab.csv",
    "Functionnal": "otu_to_functionnal.csv",
    "Acid": "otu_to_acid.csv"
}

tissue_files_ross =  {
    "Muscle": "otu_to_muscle.csv",
    "Otu": "otu_to_otu.csv"

}

tissue_files_muscle_ross  = {
    "Muscle": "muscle_to_muscle.csv",
    "Otu": "muscle_to_otu.csv"
}

tissue_files_ileum = {
    "Ileum": "ileum_to_ileum.csv",
    "Muscle": "ileum_to_muscle.csv",
    "Liver": "ileum_to_liver.csv",
    "Otu": "ileum_to_otu.csv",
    "Metabolomic": "ileum_to_metab.csv",
    "Functionnal": "ileum_to_functionnal.csv",
    "Acid": "ileum_to_acid.csv"

}

tissue_files_muscle = {
    "Ileum": "muscle_to_ileum.csv",
    "Muscle": "muscle_to_muscle.csv",
    "Liver": "muscle_to_liver.csv",
    "Otu": "muscle_to_otu.csv",
    "Metabolomic": "muscle_to_metab.csv",
    "Functionnal": "muscle_to_functionnal.csv",
    "Acid": "muscle_to_acid.csv"

}

tissue_files_liver = {
    "Ileum": "liver_to_ileum.csv",
    "Muscle": "liver_to_muscle.csv",
    "Liver": "liver_to_liver.csv",
    "Otu": "liver_to_otu.csv",
    "Metabolomic": "liver_to_metab.csv",
    "Functionnal": "liver_to_functionnal.csv",
    "Acid": "liver_to_acid.csv"

}

tissue_files_molecule = {
    "Ileum": "metab_to_ileum.csv",
    "Muscle": "metab_to_muscle.csv",
    "Liver": "metab_to_liver.csv",
    "Otu": "metab_to_otu.csv",
    "Metabolomic": "metab_to_metab.csv",
    "Functionnal": "metab_to_functionnal.csv",
    "Acid": "metab_to_acid.csv"

}

tissue_files_functionnel = {
    "Ileum": "functionnal_to_ileum.csv",
    "Muscle": "functionnal_to_muscle.csv",
    "Liver": "functionnal_to_liver.csv",
    "Otu": "functionnal_to_otu.csv",
    "Metabolomic": "functionnal_to_metab.csv",
    "Functionnal": "functionnal_to_functionnal.csv",
    "Acid": "functionnal_to_acid.csv"

}

tissue_files_acid = {
    "Ileum": "acid_to_ileum.csv",
    "Muscle": "acid_to_muscle.csv",
    "Liver": "acid_to_liver.csv",
    "Otu": "acid_to_otu.csv",
    "Metabolomic": "acid_to_metab.csv",
    "Functionnal": "acid_to_functionnal.csv",
    "Acid": "acid_to_acid.csv"
}

####################################
# Version of databse pg Otu
####################################
@csrf_exempt
def bacterien_data_analysisv2(request, host_type='isabrownv2'):
    """
    1) Creates three sunbursts (thresholds 0.4, 0.3 & 0.2).

    """
    import os, pandas as pd, plotly.express as px, plotly.io as pio
    from django.http import JsonResponse
    from django.shortcuts import render
    from django.conf import settings
    from Avapp.models import OtuCorrelation

    # --- AJAX Handling ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # (A) Load tissue: list distinct var2 (variables)
        if 'load_tissue' in request.GET:
            tissue = request.GET.get('tissue')
            vars_qs = OtuCorrelation.objects.filter(
                Q(from_tissue=tissue) | Q(to_tissue=tissue)
            ).values_list('var2', flat=True).distinct().order_by('var2')
            return J({'variables': list(vars_qs)})

        # (D) Cluster Lookup branch remains unchanged
        if  "cluster_lookup" in request.GET:
            selected_bacteria = request.GET.get("bacteria", "").strip()
            if not selected_bacteria:
                return JsonResponse({"found": False})

            found = False
            cluster_found = None
            threshold = None
            cluster_data_0_5 = [
                ['s__Ligilactobacillus salivarius', 's__Brachyspira innocens', 's__Limicola phocaeensis_A',
                 's__Bifidobacterium pullorum_B', 's__Phocaeicola intestinalis', 's__Succinatimonas hippei',
                 's__Lachnoclostridium_A stercorigallinarum', 's__Megamonas hypermegale_A'],
                ['s__Enterocloster sp944383785', 's__Mediterraneibacter sp020687545',
                 's__Parachristensenella avicola', 's__Acutalibacter sp900755895',
                 's__Bariatricus faecipullorum', 's__Mediterraneibacter quadrami',
                 's__Blautia_A faecigallinarum'],
                ['s__Mediterranea ndongoniae', 's__Scatomorpha stercorigallinarum',
                 's__Faecalibacterium intestinigallinarum', 's__Faecousia intestinavium',
                 's__UBA1405 sp002305685', 's__Anaerotruncus sp944387965'],
                ['s__Lachnoclostridium_A avicola', 's__Gemmiger stercoravium', 's__RGIG4074 sp944376455',
                 's__Mediterraneibacter faecipullorum', 's__Aveggerthella excrementigallinarum',
                 's__Mediterraneibacter merdigallinarum'],
                ['s__Gallimonas caecicola', 's__Anaerostipes avistercoris', 's__Coprocola pullicola',
                 's__QANA01 sp900554725', 's__Angelakisella sp904420255', 's__Borkfalkia faecipullorum'],
                ['s__Gemmiger faecavium', 's__Barnesiella merdipullorum', 's__Mediterraneibacter sp944383745',
                 's__Bradyrhizobium sp002831585', 's__Dysosmobacter faecalis', 's__Enterococcus_B hirae'],
                ['s__Anaerotruncus excrementipullorum', 's__Mediterraneibacter stercorigallinarum',
                 's__Mediterraneibacter excrementavium', 's__Alloclostridium intestinigallinarum',
                 's__Faecivivens stercoripullorum'],
                ['s__Ventrenecus sp944355355', 's__Borkfalkia excrementavium', 's__Flavonifractor sp002159455',
                 's__Gallimonas intestinigallinarum', 's__Avoscillospira stercorigallinarum'],
                ['s__Lachnoclostridium_B sp000765215', 's__Enorma phocaeensis',
                 's__Dysosmobacter excrementavium', 's__Aphodousia secunda_A', 's__Caccocola sp002159945']]
            cluster_data_0_4 = [
                ['s__CALXCQ01 sp944386835', 's__Flemingibacterium merdigallinarum', 's__UMGS1264 sp944384815',
                 's__Faecenecus gallistercoris', 's__Limosilactobacillus sp012843675',
                 's__JAGTTR01 sp944381745', 's__Metalachnospira gallinarum', 's__Fimimorpha sp904420225',
                 's__Faecousia faecigallinarum', 's__CAJFUR01 sp904420215', 's__CAJFPI01 sp904398675',
                 's__RGIG7193 sp944383835'], ['s__Heteroclostridium caecigallinarum', 's__Gallimonas caecicola',
                                              's__Anaerostipes avistercoris', 's__QANA01 sp900554725',
                                              's__Coprocola pullicola', 's__Angelakisella sp904420255',
                                              's__Thermophilibacter stercoravium',
                                              's__Borkfalkia faecipullorum', 's__Scatosoma pullicola',
                                              's__Borkfalkia faecigallinarum',
                                              's__Scatomorpha merdigallinarum'],
                ['s__QAMM01 sp900762715', 's__Butyricimonas paravirosa', 's__Lawsonibacter sp944385075',
                 's__CALWWS01 sp944385305', 's__Caccousia avistercoris', 's__Pseudobutyricicoccus sp016901775',
                 's__Lawsonibacter sp944385645', 's__Ruthenibacterium merdigallinarum',
                 's__Holdemania sp904395815'],
                ['s__Phocaeicola sp900546355', 's__Parabacteroides sp002159645', 's__Prevotella lascolaii',
                 's__Paraprevotella stercoravium', 's__Phocaeicola barnesiae', 's__Mediterranea sp900553815',
                 's__Desulfovibrio sp944327285', 's__Phocaeicola_A sp900291465',
                 's__Mediterranea massiliensis'],
                ['s__Borkfalkia excrementavium', 's__Eisenbergiella pullicola', 's__Ruthenibacterium avium',
                 's__Avoscillospira stercorigallinarum', 's__Ventrenecus sp944355355',
                 's__Flavonifractor sp002159455', 's__Pseudoscilispira falkowii',
                 's__Gallimonas intestinigallinarum'],
                ['s__Eubacterium_R faecale', 's__Mediterraneibacter tabaqchaliae',
                 's__Pseudoflavonifractor capillosus', 's__Pygmaiobacter sp944386485',
                 's__Egerieimonas_A faecigallinarum', 's__Dysosmobacter sp904393855',
                 's__Scatomonas merdigallinarum', 's__Neoanaerotignum_B sp944378105'],
                ['s__Ligilactobacillus salivarius', 's__Brachyspira innocens', 's__Limicola phocaeensis_A',
                 's__Bifidobacterium pullorum_B', 's__Phocaeicola intestinalis', 's__Succinatimonas hippei',
                 's__Lachnoclostridium_A stercorigallinarum', 's__Megamonas hypermegale_A'],
                ['s__Acutalibacter pullicola', 's__Faecalibacterium gallinarum', 's__SIG471 sp905199135',
                 's__Avoscillospira_A avistercoris', 's__CAJFPI01 sp904420435', 's__Borkfalkia sp904419945',
                 's__Gallimonas sp944367465', 's__Avoscillospira stercoripullorum'],
                ['s__Caccosoma faecigallinarum', 's__Borkfalkia stercoripullorum', 's__UMGS1623 sp900553525',
                 's__Anaerobutyricum stercoris', 's__CALWPC01 sp944383325', 's__Acutalibacter ornithocaccae',
                 's__Coproplasma stercorigallinarum', 's__CAG-273 sp944392105'],
                ['s__CALXSR01 sp944391215', 's__Caccocola faecigallinarum', 's__Merdivicinus faecavium',
                 's__Desulfovibrio faecigallinarum', 's__UBA3402 sp944380605', 's__Bacteroides xylanisolvens',
                 's__Aveggerthella stercoripullorum'],
                ['s__Enterocloster sp944383785', 's__Mediterraneibacter sp020687545',
                 's__Parachristensenella avicola', 's__Acutalibacter sp900755895',
                 's__Bariatricus faecipullorum', 's__Mediterraneibacter quadrami',
                 's__Blautia_A faecigallinarum'],
                ['s__Lachnoclostridium_A avicola', 's__Gemmiger stercoravium', 's__RGIG4074 sp944376455',
                 's__Mediterraneibacter faecipullorum', 's__Aveggerthella excrementigallinarum',
                 's__Mediterraneibacter glycyrrhizinilyticus_A', 's__Mediterraneibacter merdigallinarum'],
                ['s__Mediterraneibacter norwichensis', 's__CALXCT01 sp944386055',
                 's__Ruthenibacterium sp944386555', 's__Limosilactobacillus coleohominis',
                 's__Alectryocaccomicrobium excrementavium', 's__Faecimonas intestinavium'],
                ['s__Eisenbergiella sp900555195', 's__Limosilactobacillus gallistercoris',
                 's__Borkfalkia excrementipullorum', 's__Scatomonas merdavium',
                 's__Ruthenibacterium merdipullorum', 's__Scatomorpha pullicola'],
                ['s__Blautia merdavium', 's__Copromonas faecavium', 's__Anaeromassilibacillus stercoravium',
                 's__Neoanaerotignum_B galli', 's__Ornithomonoglobus sp904420525',
                 's__Gordonibacter urolithinfaciens'],
                ['s__Mediterranea ndongoniae', 's__Scatomorpha stercorigallinarum',
                 's__Faecalibacterium intestinigallinarum', 's__Faecousia intestinavium',
                 's__UBA1405 sp002305685', 's__Anaerotruncus sp944387965'],
                ['s__Gemmiger faecavium', 's__Barnesiella merdipullorum', 's__Mediterraneibacter sp944383745',
                 's__Bradyrhizobium sp002831585', 's__Dysosmobacter faecalis', 's__Enterococcus_B hirae'],
                ['s__Anaerotruncus excrementipullorum', 's__Mediterraneibacter stercorigallinarum',
                 's__Mediterraneibacter excrementavium', 's__Alloclostridium intestinigallinarum',
                 's__Faecivivens stercoripullorum'],
                ['s__Blautia_A gallistercoris', 's__Evtepia excrementipullorum', 's__UMGS1591 sp900553255',
                 's__Paralachnospira caecorum', 's__Avispirillum faecium'],
                ['s__Agathobaculum intestinigallinarum', 's__Avimicrobium caecorum',
                 's__Scybalocola faecipullorum', 's__Pullilachnospira stercoravium',
                 's__Thermophilibacter provencensis'],
                ['s__Flavonifractor plautii', 's__Clostridium_Q saccharolyticum_A',
                 's__Onthovicinus excrementipullorum', 's__Gordonibacter pamelaeae',
                 's__Eubacterium_R faecavium'], ['s__Lachnoclostridium_B sp000765215', 's__Enorma phocaeensis',
                                                 's__Dysosmobacter excrementavium', 's__Aphodousia secunda_A',
                                                 's__Caccocola sp002159945'],
                ['s__CAJFPI01 sp904419145', 's__Faecalicoccus acidiformans',
                 's__Merdiplasma excrementigallinarum', 's__Collinsella tanakaei_B',
                 's__Ruminococcus_G avistercoris'],
                ['s__Alloscillospira gallinarum', 's__Lawsonibacter sp019424865',
                 's__Avoscillospira_A sp904395905', 's__Avimonas merdigallinarum',
                 's__Limosilactobacillus intestinipullorum'],
                ['s__Eisenbergiella merdavium', 's__Choladousia intestinigallinarum', 's__Merdimonas faecis',
                 's__Ventricola intestinavium', 's__Blautia_A intestinavium']]

            cluster_data_0_6 = [
                ['s__Ligilactobacillus salivarius', 's__Brachyspira innocens', 's__Limicola phocaeensis_A',
                 's__Bifidobacterium pullorum_B', 's__Phocaeicola intestinalis', 's__Succinatimonas hippei',
                 's__Lachnoclostridium_A stercorigallinarum', 's__Megamonas hypermegale_A'],
                ['s__Gemmiger faecavium', 's__Barnesiella merdipullorum', 's__Mediterraneibacter sp944383745',
                 's__Bradyrhizobium sp002831585', 's__Dysosmobacter faecalis', 's__Enterococcus_B hirae'],
                ['s__Anaerotruncus excrementipullorum', 's__Mediterraneibacter stercorigallinarum',
                 's__Mediterraneibacter excrementavium', 's__Alloclostridium intestinigallinarum',
                 's__Faecivivens stercoripullorum'],
                ['s__Lachnoclostridium_B sp000765215', 's__Enorma phocaeensis',
                 's__Dysosmobacter excrementavium', 's__Aphodousia secunda_A', 's__Caccocola sp002159945']]
            # some entry can be appearing in more than one clustter so  ...
            if selected_bacteria.endswith("_otu"):
                selected_bacteria = selected_bacteria[:-4]
            for cluster in cluster_data_0_6:
                if selected_bacteria in cluster:
                    found = True
                    cluster_found = cluster
                    threshold = "0.6"
                    break
            if not found:
                for cluster in cluster_data_0_5:
                    if selected_bacteria in cluster:
                        found = True
                        cluster_found = cluster
                        threshold = "0.5"
                        break
            if not found:
                for cluster in cluster_data_0_4:
                    if selected_bacteria in cluster:
                        found = True
                        cluster_found = cluster
                        threshold = "0.4"
                        break
            if found:
                cleaned_cluster = [s.replace("s__", "") for s in cluster_found]
                return JsonResponse({
                    "found": True,
                    "threshold": threshold,
                    "cluster_members": cleaned_cluster,
                })
            else:
                return JsonResponse({"found": False})


        # ----- Common filters (only for branches that need tissue) -----
        # Common filters
        tissue = request.GET.get('tissue')
        if tissue is None:
            return J({'error': 'Missing tissue.'}, status=400)
        # base_tissue_q = Q(from_tissue=tissue) | Q(to_tissue=tissue)
        # here tissue is otu to adapat for each case
        base_tissue_q = Q(from_tissue='otu') & Q(to_tissue=tissue)

        # (B) Single-var filtering
        if ('multi_variable' not in request.GET
                and 'table_filter' not in request.GET
                and 'cluster_lookup' not in request.GET
                and 'explore_table_filter' not in request.GET
                and 'explore_distribution' not in request.GET):
            var = request.GET.get('variable')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = OtuCorrelation.objects.filter(
                base_tissue_q,
                var2=var,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({'results': [], 'total_count': 0})
            top = filt.order_by('-correlation')[:100]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count})

        # (C) Multi-var filtering
        if 'multi_variable' in request.GET:
            variables = request.GET.getlist('variables[]')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = OtuCorrelation.objects.filter(
                base_tissue_q,
                var2__in=variables,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({'results': [], 'total_count': 0})
            top = filt.order_by('-correlation')[:100]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count})



        # (E) Table Filtering
        if 'table_filter' in request.GET:
            var = request.GET.get('variable')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = OtuCorrelation.objects.filter(
                base_tissue_q,
                var2=var,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({
                    'results': [],
                    'total_count': 0,
                    'overview': {'median': None, 'q1': None, 'q3': None}
                })
            top = filt.order_by('-correlation')[:200]

            results = []
            vals = [o.correlation for o in filt]
            overview = {
                'median': r3(np.median(vals)),
                'q1': r3(np.quantile(vals, 0.25)),
                'q3': r3(np.quantile(vals, 0.75)),
            }
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'Coefficient': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count, 'overview': overview})

        # (F) Explore distribution
        if 'explore_distribution' in request.GET:
            # qs = MuscleCorrelation.objects.filter(base_tissue_q).values_list('correlation', flat=True)
            qs = (OtuCorrelation.objects
                 .filter(base_tissue_q, correlation__isnull=False)
                 .values_list('correlation', flat=True)
                )
            series = list(qs)
            if not series:
                return J({'error': 'No data found.'}, status=400)
            stats = {
                'min': r3(min(series)),
                'q1': r3(np.quantile(series, 0.25)),
                'median': r3(np.median(series)),
                'q3': r3(np.quantile(series, 0.75)),
                'max': r3(max(series)),
            }
            return J({'distribution': {'correlation_values': series, 'stats': stats}})

        # (G) Explore table filter
        if 'explore_table_filter' in request.GET:
            try:
                corr_min = float(request.GET.get('corrMin', -1))
                corr_max = float(request.GET.get('corrMax', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = OtuCorrelation.objects.filter(
                base_tissue_q,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            top = filt.order_by('-correlation')[:200]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            vals = [o.correlation for o in filt]
            overview = {
                'median': r3(np.median(vals)) if vals else None,
                'q1': r3(np.quantile(vals, 0.25)) if vals else None,
                'q3': r3(np.quantile(vals, 0.75)) if vals else None,
            }
            return J({'results': results, 'total_count': total_count, 'overview': overview})

        return J({'error': 'No recognized AJAX action.'}, status=400)

    # --- Non-AJAX: Build sunbursts and context ---
    def clusters_to_df(data):
        rows = []
        for i, sublist in enumerate(data, start=1):
            cluster_name = f"Cluster {i}"
            for species in sublist:
                rows.append({"Cluster": cluster_name, "Species": species.replace("s__", ""), "Value": 1})
        return pd.DataFrame(rows)

    cluster_data_0_5 = [
                ['s__Ligilactobacillus salivarius', 's__Brachyspira innocens', 's__Limicola phocaeensis_A',
                 's__Bifidobacterium pullorum_B', 's__Phocaeicola intestinalis', 's__Succinatimonas hippei',
                 's__Lachnoclostridium_A stercorigallinarum', 's__Megamonas hypermegale_A'],
                ['s__Enterocloster sp944383785', 's__Mediterraneibacter sp020687545',
                 's__Parachristensenella avicola', 's__Acutalibacter sp900755895',
                 's__Bariatricus faecipullorum', 's__Mediterraneibacter quadrami',
                 's__Blautia_A faecigallinarum'],
                ['s__Mediterranea ndongoniae', 's__Scatomorpha stercorigallinarum',
                 's__Faecalibacterium intestinigallinarum', 's__Faecousia intestinavium',
                 's__UBA1405 sp002305685', 's__Anaerotruncus sp944387965'],
                ['s__Lachnoclostridium_A avicola', 's__Gemmiger stercoravium', 's__RGIG4074 sp944376455',
                 's__Mediterraneibacter faecipullorum', 's__Aveggerthella excrementigallinarum',
                 's__Mediterraneibacter merdigallinarum'],
                ['s__Gallimonas caecicola', 's__Anaerostipes avistercoris', 's__Coprocola pullicola',
                 's__QANA01 sp900554725', 's__Angelakisella sp904420255', 's__Borkfalkia faecipullorum'],
                ['s__Gemmiger faecavium', 's__Barnesiella merdipullorum', 's__Mediterraneibacter sp944383745',
                 's__Bradyrhizobium sp002831585', 's__Dysosmobacter faecalis', 's__Enterococcus_B hirae'],
                ['s__Anaerotruncus excrementipullorum', 's__Mediterraneibacter stercorigallinarum',
                 's__Mediterraneibacter excrementavium', 's__Alloclostridium intestinigallinarum',
                 's__Faecivivens stercoripullorum'],
                ['s__Ventrenecus sp944355355', 's__Borkfalkia excrementavium', 's__Flavonifractor sp002159455',
                 's__Gallimonas intestinigallinarum', 's__Avoscillospira stercorigallinarum'],
                ['s__Lachnoclostridium_B sp000765215', 's__Enorma phocaeensis',
                 's__Dysosmobacter excrementavium', 's__Aphodousia secunda_A', 's__Caccocola sp002159945']]
    cluster_data_0_4 = [
                ['s__CALXCQ01 sp944386835', 's__Flemingibacterium merdigallinarum', 's__UMGS1264 sp944384815',
                 's__Faecenecus gallistercoris', 's__Limosilactobacillus sp012843675',
                 's__JAGTTR01 sp944381745', 's__Metalachnospira gallinarum', 's__Fimimorpha sp904420225',
                 's__Faecousia faecigallinarum', 's__CAJFUR01 sp904420215', 's__CAJFPI01 sp904398675',
                 's__RGIG7193 sp944383835'], ['s__Heteroclostridium caecigallinarum', 's__Gallimonas caecicola',
                                              's__Anaerostipes avistercoris', 's__QANA01 sp900554725',
                                              's__Coprocola pullicola', 's__Angelakisella sp904420255',
                                              's__Thermophilibacter stercoravium',
                                              's__Borkfalkia faecipullorum', 's__Scatosoma pullicola',
                                              's__Borkfalkia faecigallinarum',
                                              's__Scatomorpha merdigallinarum'],
                ['s__QAMM01 sp900762715', 's__Butyricimonas paravirosa', 's__Lawsonibacter sp944385075',
                 's__CALWWS01 sp944385305', 's__Caccousia avistercoris', 's__Pseudobutyricicoccus sp016901775',
                 's__Lawsonibacter sp944385645', 's__Ruthenibacterium merdigallinarum',
                 's__Holdemania sp904395815'],
                ['s__Phocaeicola sp900546355', 's__Parabacteroides sp002159645', 's__Prevotella lascolaii',
                 's__Paraprevotella stercoravium', 's__Phocaeicola barnesiae', 's__Mediterranea sp900553815',
                 's__Desulfovibrio sp944327285', 's__Phocaeicola_A sp900291465',
                 's__Mediterranea massiliensis'],
                ['s__Borkfalkia excrementavium', 's__Eisenbergiella pullicola', 's__Ruthenibacterium avium',
                 's__Avoscillospira stercorigallinarum', 's__Ventrenecus sp944355355',
                 's__Flavonifractor sp002159455', 's__Pseudoscilispira falkowii',
                 's__Gallimonas intestinigallinarum'],
                ['s__Eubacterium_R faecale', 's__Mediterraneibacter tabaqchaliae',
                 's__Pseudoflavonifractor capillosus', 's__Pygmaiobacter sp944386485',
                 's__Egerieimonas_A faecigallinarum', 's__Dysosmobacter sp904393855',
                 's__Scatomonas merdigallinarum', 's__Neoanaerotignum_B sp944378105'],
                ['s__Ligilactobacillus salivarius', 's__Brachyspira innocens', 's__Limicola phocaeensis_A',
                 's__Bifidobacterium pullorum_B', 's__Phocaeicola intestinalis', 's__Succinatimonas hippei',
                 's__Lachnoclostridium_A stercorigallinarum', 's__Megamonas hypermegale_A'],
                ['s__Acutalibacter pullicola', 's__Faecalibacterium gallinarum', 's__SIG471 sp905199135',
                 's__Avoscillospira_A avistercoris', 's__CAJFPI01 sp904420435', 's__Borkfalkia sp904419945',
                 's__Gallimonas sp944367465', 's__Avoscillospira stercoripullorum'],
                ['s__Caccosoma faecigallinarum', 's__Borkfalkia stercoripullorum', 's__UMGS1623 sp900553525',
                 's__Anaerobutyricum stercoris', 's__CALWPC01 sp944383325', 's__Acutalibacter ornithocaccae',
                 's__Coproplasma stercorigallinarum', 's__CAG-273 sp944392105'],
                ['s__CALXSR01 sp944391215', 's__Caccocola faecigallinarum', 's__Merdivicinus faecavium',
                 's__Desulfovibrio faecigallinarum', 's__UBA3402 sp944380605', 's__Bacteroides xylanisolvens',
                 's__Aveggerthella stercoripullorum'],
                ['s__Enterocloster sp944383785', 's__Mediterraneibacter sp020687545',
                 's__Parachristensenella avicola', 's__Acutalibacter sp900755895',
                 's__Bariatricus faecipullorum', 's__Mediterraneibacter quadrami',
                 's__Blautia_A faecigallinarum'],
                ['s__Lachnoclostridium_A avicola', 's__Gemmiger stercoravium', 's__RGIG4074 sp944376455',
                 's__Mediterraneibacter faecipullorum', 's__Aveggerthella excrementigallinarum',
                 's__Mediterraneibacter glycyrrhizinilyticus_A', 's__Mediterraneibacter merdigallinarum'],
                ['s__Mediterraneibacter norwichensis', 's__CALXCT01 sp944386055',
                 's__Ruthenibacterium sp944386555', 's__Limosilactobacillus coleohominis',
                 's__Alectryocaccomicrobium excrementavium', 's__Faecimonas intestinavium'],
                ['s__Eisenbergiella sp900555195', 's__Limosilactobacillus gallistercoris',
                 's__Borkfalkia excrementipullorum', 's__Scatomonas merdavium',
                 's__Ruthenibacterium merdipullorum', 's__Scatomorpha pullicola'],
                ['s__Blautia merdavium', 's__Copromonas faecavium', 's__Anaeromassilibacillus stercoravium',
                 's__Neoanaerotignum_B galli', 's__Ornithomonoglobus sp904420525',
                 's__Gordonibacter urolithinfaciens'],
                ['s__Mediterranea ndongoniae', 's__Scatomorpha stercorigallinarum',
                 's__Faecalibacterium intestinigallinarum', 's__Faecousia intestinavium',
                 's__UBA1405 sp002305685', 's__Anaerotruncus sp944387965'],
                ['s__Gemmiger faecavium', 's__Barnesiella merdipullorum', 's__Mediterraneibacter sp944383745',
                 's__Bradyrhizobium sp002831585', 's__Dysosmobacter faecalis', 's__Enterococcus_B hirae'],
                ['s__Anaerotruncus excrementipullorum', 's__Mediterraneibacter stercorigallinarum',
                 's__Mediterraneibacter excrementavium', 's__Alloclostridium intestinigallinarum',
                 's__Faecivivens stercoripullorum'],
                ['s__Blautia_A gallistercoris', 's__Evtepia excrementipullorum', 's__UMGS1591 sp900553255',
                 's__Paralachnospira caecorum', 's__Avispirillum faecium'],
                ['s__Agathobaculum intestinigallinarum', 's__Avimicrobium caecorum',
                 's__Scybalocola faecipullorum', 's__Pullilachnospira stercoravium',
                 's__Thermophilibacter provencensis'],
                ['s__Flavonifractor plautii', 's__Clostridium_Q saccharolyticum_A',
                 's__Onthovicinus excrementipullorum', 's__Gordonibacter pamelaeae',
                 's__Eubacterium_R faecavium'], ['s__Lachnoclostridium_B sp000765215', 's__Enorma phocaeensis',
                                                 's__Dysosmobacter excrementavium', 's__Aphodousia secunda_A',
                                                 's__Caccocola sp002159945'],
                ['s__CAJFPI01 sp904419145', 's__Faecalicoccus acidiformans',
                 's__Merdiplasma excrementigallinarum', 's__Collinsella tanakaei_B',
                 's__Ruminococcus_G avistercoris'],
                ['s__Alloscillospira gallinarum', 's__Lawsonibacter sp019424865',
                 's__Avoscillospira_A sp904395905', 's__Avimonas merdigallinarum',
                 's__Limosilactobacillus intestinipullorum'],
                ['s__Eisenbergiella merdavium', 's__Choladousia intestinigallinarum', 's__Merdimonas faecis',
                 's__Ventricola intestinavium', 's__Blautia_A intestinavium']]

    cluster_data_0_6 = [
                ['s__Ligilactobacillus salivarius', 's__Brachyspira innocens', 's__Limicola phocaeensis_A',
                 's__Bifidobacterium pullorum_B', 's__Phocaeicola intestinalis', 's__Succinatimonas hippei',
                 's__Lachnoclostridium_A stercorigallinarum', 's__Megamonas hypermegale_A'],
                ['s__Gemmiger faecavium', 's__Barnesiella merdipullorum', 's__Mediterraneibacter sp944383745',
                 's__Bradyrhizobium sp002831585', 's__Dysosmobacter faecalis', 's__Enterococcus_B hirae'],
                ['s__Anaerotruncus excrementipullorum', 's__Mediterraneibacter stercorigallinarum',
                 's__Mediterraneibacter excrementavium', 's__Alloclostridium intestinigallinarum',
                 's__Faecivivens stercoripullorum'],
                ['s__Lachnoclostridium_B sp000765215', 's__Enorma phocaeensis',
                 's__Dysosmobacter excrementavium', 's__Aphodousia secunda_A', 's__Caccocola sp002159945']]

    df_0_4 = clusters_to_df(cluster_data_0_4)
    df_0_5 = clusters_to_df(cluster_data_0_5)
    df_0_6 = clusters_to_df(cluster_data_0_6)
    # Also prepare explore versions (using same data)
    df_0_4_explore = df_0_4.copy()
    df_0_5_explore = df_0_5.copy()
    df_0_6_explore = df_0_6.copy()

    try:
        fig_0_4 = px.sunburst(df_0_4, path=["Cluster", "Species"], values="Value", title="Threshold 0.4")
        fig_0_4.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_4 = pio.to_html(fig_0_4, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_04")
    except Exception as e:
        sunburst_html_0_4 = ""
    try:
        fig_0_5 = px.sunburst(df_0_5, path=["Cluster", "Species"], values="Value", title="Threshold 0.5")
        fig_0_5.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_5 = pio.to_html(fig_0_5, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_03")
    except Exception as e:
        sunburst_html_0_5 = ""
    try:
        fig_0_6 = px.sunburst(df_0_6, path=["Cluster", "Species"], values="Value", title="Threshold 0.6")
        fig_0_6.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_6 = pio.to_html(fig_0_6, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_02")
    except Exception as e:
        sunburst_html_0_6 = ""
    try:
        explore_fig_0_5 = px.sunburst(df_0_5_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.5")
        explore_fig_0_5.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_5 = pio.to_html(explore_fig_0_5, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_03")
    except Exception as e:
        explore_sunburst_html_0_5 = ""
    try:
        explore_fig_0_4 = px.sunburst(df_0_4_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.4")
        explore_fig_0_4.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_4 = pio.to_html(explore_fig_0_4, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_04")
    except Exception as e:
        explore_sunburst_html_0_4 = ""
    try:
        explore_fig_0_6 = px.sunburst(df_0_6_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.6")
        explore_fig_0_6.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_6 = pio.to_html(explore_fig_0_6, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_02")
    except Exception as e:
        explore_sunburst_html_0_6 = ""

    # ileum suggestions from DB to do fot otu
    # otu_list = OtuCorrelation.objects.values_list('var2', flat=True).distinct().order_by('var2')
    # Check from file csv the ileum
    # otu_list = []  # default if anything goes wrong
    try:
        otu_csv_path = os.path.join(settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                                    "otu_to_otu.csv")
        df_otu = pd.read_csv(otu_csv_path, )
        otu_list = df_otu.iloc[:, 0].dropna().unique().tolist()
    except Exception as e:
        otu_list = []
        print(f"Error loading otu_to_muscle.csv: {e}")

    return render(request, f"{host_type}/bacterien2.html", {
        "host_type": host_type.title(),
        "data_type": "Otu",
        "description": "Top 200 displayed only. Gene info from Ensembl REST.",
        # "tissue_types": list(tissue_files_muscle.keys()),
        "sunburst_html_0_4": sunburst_html_0_4,
        "sunburst_html_0_5": sunburst_html_0_5,
        "sunburst_html_0_6": sunburst_html_0_6,
        "explore_sunburst_html_0_4": explore_sunburst_html_0_4,
        "explore_sunburst_html_0_5": explore_sunburst_html_0_5,
        "explore_sunburst_html_0_6": explore_sunburst_html_0_6,
        "otu_list": otu_list,
    })

def bacterien_data_analysisv2_ross(request, host_type='rossv2'):
    """
    1) Creates three sunbursts (thresholds 0.4, 0.3 & 0.2).

    """
    import os, pandas as pd, plotly.express as px, plotly.io as pio
    from django.http import JsonResponse
    from django.shortcuts import render
    from django.conf import settings
    from Avapp.models import OtuCorrelationRoss

    # --- AJAX Handling ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # (A) Load tissue: list distinct var2 (variables)
        if 'load_tissue' in request.GET:
            tissue = request.GET.get('tissue')
            vars_qs = OtuCorrelationRoss.objects.filter(
                Q(from_tissue=tissue) | Q(to_tissue=tissue)
            ).values_list('var2', flat=True).distinct().order_by('var2')
            return J({'variables': list(vars_qs)})

        # (D) Cluster Lookup branch remains unchanged
        if  "cluster_lookup" in request.GET:
            selected_bacteria = request.GET.get("bacteria", "").strip()
            if not selected_bacteria:
                return JsonResponse({"found": False})

            found = False
            cluster_found = None
            threshold = None
            cluster_data_0_6 = [
                ['s__Ligilactobacillus salivarius', 's__Brachyspira innocens', 's__Limicola phocaeensis_A',
                 's__Bifidobacterium pullorum_B', 's__Phocaeicola intestinalis', 's__Succinatimonas hippei',
                 's__Lachnoclostridium_A stercorigallinarum', 's__Megamonas hypermegale_A'],
                ['s__Gemmiger faecavium', 's__Barnesiella merdipullorum', 's__Mediterraneibacter sp944383745',
                 's__Bradyrhizobium sp002831585', 's__Dysosmobacter faecalis', 's__Enterococcus_B hirae'],
                ['s__Anaerotruncus excrementipullorum', 's__Mediterraneibacter stercorigallinarum',
                 's__Mediterraneibacter excrementavium', 's__Alloclostridium intestinigallinarum',
                 's__Faecivivens stercoripullorum'],
                ['s__Lachnoclostridium_B sp000765215', 's__Enorma phocaeensis',
                 's__Dysosmobacter excrementavium', 's__Aphodousia secunda_A', 's__Caccocola sp002159945']]
            cluster_data_0_5 = [
                ['s__Ligilactobacillus salivarius', 's__Brachyspira innocens', 's__Limicola phocaeensis_A',
                 's__Bifidobacterium pullorum_B', 's__Phocaeicola intestinalis', 's__Succinatimonas hippei',
                 's__Lachnoclostridium_A stercorigallinarum', 's__Megamonas hypermegale_A'],
                ['s__Enterocloster sp944383785', 's__Mediterraneibacter sp020687545',
                 's__Parachristensenella avicola', 's__Acutalibacter sp900755895',
                 's__Bariatricus faecipullorum', 's__Mediterraneibacter quadrami',
                 's__Blautia_A faecigallinarum'],
                ['s__Mediterranea ndongoniae', 's__Scatomorpha stercorigallinarum',
                 's__Faecalibacterium intestinigallinarum', 's__Faecousia intestinavium',
                 's__UBA1405 sp002305685', 's__Anaerotruncus sp944387965'],
                ['s__Lachnoclostridium_A avicola', 's__Gemmiger stercoravium', 's__RGIG4074 sp944376455',
                 's__Mediterraneibacter faecipullorum', 's__Aveggerthella excrementigallinarum',
                 's__Mediterraneibacter merdigallinarum'],
                ['s__Gallimonas caecicola', 's__Anaerostipes avistercoris', 's__Coprocola pullicola',
                 's__QANA01 sp900554725', 's__Angelakisella sp904420255', 's__Borkfalkia faecipullorum'],
                ['s__Gemmiger faecavium', 's__Barnesiella merdipullorum', 's__Mediterraneibacter sp944383745',
                 's__Bradyrhizobium sp002831585', 's__Dysosmobacter faecalis', 's__Enterococcus_B hirae'],
                ['s__Anaerotruncus excrementipullorum', 's__Mediterraneibacter stercorigallinarum',
                 's__Mediterraneibacter excrementavium', 's__Alloclostridium intestinigallinarum',
                 's__Faecivivens stercoripullorum'],
                ['s__Ventrenecus sp944355355', 's__Borkfalkia excrementavium', 's__Flavonifractor sp002159455',
                 's__Gallimonas intestinigallinarum', 's__Avoscillospira stercorigallinarum'],
                ['s__Lachnoclostridium_B sp000765215', 's__Enorma phocaeensis',
                 's__Dysosmobacter excrementavium', 's__Aphodousia secunda_A', 's__Caccocola sp002159945']]

            cluster_data_0_4 = [
                ['s__CALXCQ01 sp944386835', 's__Flemingibacterium merdigallinarum', 's__UMGS1264 sp944384815',
                 's__Faecenecus gallistercoris', 's__Limosilactobacillus sp012843675',
                 's__JAGTTR01 sp944381745', 's__Metalachnospira gallinarum', 's__Fimimorpha sp904420225',
                 's__Faecousia faecigallinarum', 's__CAJFUR01 sp904420215', 's__CAJFPI01 sp904398675',
                 's__RGIG7193 sp944383835'], ['s__Heteroclostridium caecigallinarum', 's__Gallimonas caecicola',
                                              's__Anaerostipes avistercoris', 's__QANA01 sp900554725',
                                              's__Coprocola pullicola', 's__Angelakisella sp904420255',
                                              's__Thermophilibacter stercoravium',
                                              's__Borkfalkia faecipullorum', 's__Scatosoma pullicola',
                                              's__Borkfalkia faecigallinarum',
                                              's__Scatomorpha merdigallinarum'],
                ['s__QAMM01 sp900762715', 's__Butyricimonas paravirosa', 's__Lawsonibacter sp944385075',
                 's__CALWWS01 sp944385305', 's__Caccousia avistercoris', 's__Pseudobutyricicoccus sp016901775',
                 's__Lawsonibacter sp944385645', 's__Ruthenibacterium merdigallinarum',
                 's__Holdemania sp904395815'],
                ['s__Phocaeicola sp900546355', 's__Parabacteroides sp002159645', 's__Prevotella lascolaii',
                 's__Paraprevotella stercoravium', 's__Phocaeicola barnesiae', 's__Mediterranea sp900553815',
                 's__Desulfovibrio sp944327285', 's__Phocaeicola_A sp900291465',
                 's__Mediterranea massiliensis'],
                ['s__Borkfalkia excrementavium', 's__Eisenbergiella pullicola', 's__Ruthenibacterium avium',
                 's__Avoscillospira stercorigallinarum', 's__Ventrenecus sp944355355',
                 's__Flavonifractor sp002159455', 's__Pseudoscilispira falkowii',
                 's__Gallimonas intestinigallinarum'],
                ['s__Eubacterium_R faecale', 's__Mediterraneibacter tabaqchaliae',
                 's__Pseudoflavonifractor capillosus', 's__Pygmaiobacter sp944386485',
                 's__Egerieimonas_A faecigallinarum', 's__Dysosmobacter sp904393855',
                 's__Scatomonas merdigallinarum', 's__Neoanaerotignum_B sp944378105'],
                ['s__Ligilactobacillus salivarius', 's__Brachyspira innocens', 's__Limicola phocaeensis_A',
                 's__Bifidobacterium pullorum_B', 's__Phocaeicola intestinalis', 's__Succinatimonas hippei',
                 's__Lachnoclostridium_A stercorigallinarum', 's__Megamonas hypermegale_A'],
                ['s__Acutalibacter pullicola', 's__Faecalibacterium gallinarum', 's__SIG471 sp905199135',
                 's__Avoscillospira_A avistercoris', 's__CAJFPI01 sp904420435', 's__Borkfalkia sp904419945',
                 's__Gallimonas sp944367465', 's__Avoscillospira stercoripullorum'],
                ['s__Caccosoma faecigallinarum', 's__Borkfalkia stercoripullorum', 's__UMGS1623 sp900553525',
                 's__Anaerobutyricum stercoris', 's__CALWPC01 sp944383325', 's__Acutalibacter ornithocaccae',
                 's__Coproplasma stercorigallinarum', 's__CAG-273 sp944392105'],
                ['s__CALXSR01 sp944391215', 's__Caccocola faecigallinarum', 's__Merdivicinus faecavium',
                 's__Desulfovibrio faecigallinarum', 's__UBA3402 sp944380605', 's__Bacteroides xylanisolvens',
                 's__Aveggerthella stercoripullorum'],
                ['s__Enterocloster sp944383785', 's__Mediterraneibacter sp020687545',
                 's__Parachristensenella avicola', 's__Acutalibacter sp900755895',
                 's__Bariatricus faecipullorum', 's__Mediterraneibacter quadrami',
                 's__Blautia_A faecigallinarum'],
                ['s__Lachnoclostridium_A avicola', 's__Gemmiger stercoravium', 's__RGIG4074 sp944376455',
                 's__Mediterraneibacter faecipullorum', 's__Aveggerthella excrementigallinarum',
                 's__Mediterraneibacter glycyrrhizinilyticus_A', 's__Mediterraneibacter merdigallinarum'],
                ['s__Mediterraneibacter norwichensis', 's__CALXCT01 sp944386055',
                 's__Ruthenibacterium sp944386555', 's__Limosilactobacillus coleohominis',
                 's__Alectryocaccomicrobium excrementavium', 's__Faecimonas intestinavium'],
                ['s__Eisenbergiella sp900555195', 's__Limosilactobacillus gallistercoris',
                 's__Borkfalkia excrementipullorum', 's__Scatomonas merdavium',
                 's__Ruthenibacterium merdipullorum', 's__Scatomorpha pullicola'],
                ['s__Blautia merdavium', 's__Copromonas faecavium', 's__Anaeromassilibacillus stercoravium',
                 's__Neoanaerotignum_B galli', 's__Ornithomonoglobus sp904420525',
                 's__Gordonibacter urolithinfaciens'],
                ['s__Mediterranea ndongoniae', 's__Scatomorpha stercorigallinarum',
                 's__Faecalibacterium intestinigallinarum', 's__Faecousia intestinavium',
                 's__UBA1405 sp002305685', 's__Anaerotruncus sp944387965'],
                ['s__Gemmiger faecavium', 's__Barnesiella merdipullorum', 's__Mediterraneibacter sp944383745',
                 's__Bradyrhizobium sp002831585', 's__Dysosmobacter faecalis', 's__Enterococcus_B hirae'],
                ['s__Anaerotruncus excrementipullorum', 's__Mediterraneibacter stercorigallinarum',
                 's__Mediterraneibacter excrementavium', 's__Alloclostridium intestinigallinarum',
                 's__Faecivivens stercoripullorum'],
                ['s__Blautia_A gallistercoris', 's__Evtepia excrementipullorum', 's__UMGS1591 sp900553255',
                 's__Paralachnospira caecorum', 's__Avispirillum faecium'],
                ['s__Agathobaculum intestinigallinarum', 's__Avimicrobium caecorum',
                 's__Scybalocola faecipullorum', 's__Pullilachnospira stercoravium',
                 's__Thermophilibacter provencensis'],
                ['s__Flavonifractor plautii', 's__Clostridium_Q saccharolyticum_A',
                 's__Onthovicinus excrementipullorum', 's__Gordonibacter pamelaeae',
                 's__Eubacterium_R faecavium'], ['s__Lachnoclostridium_B sp000765215', 's__Enorma phocaeensis',
                                                 's__Dysosmobacter excrementavium', 's__Aphodousia secunda_A',
                                                 's__Caccocola sp002159945'],
                ['s__CAJFPI01 sp904419145', 's__Faecalicoccus acidiformans',
                 's__Merdiplasma excrementigallinarum', 's__Collinsella tanakaei_B',
                 's__Ruminococcus_G avistercoris'],
                ['s__Alloscillospira gallinarum', 's__Lawsonibacter sp019424865',
                 's__Avoscillospira_A sp904395905', 's__Avimonas merdigallinarum',
                 's__Limosilactobacillus intestinipullorum'],
                ['s__Eisenbergiella merdavium', 's__Choladousia intestinigallinarum', 's__Merdimonas faecis',
                 's__Ventricola intestinavium', 's__Blautia_A intestinavium']]

            cluster_data_0_3 = [
                ['s__Bifidobacterium pullorum_B', 's__Thermophilibacter avistercoris', 's__Coprousia sp002159765',
                 's__Lactobacillus johnsonii', 's__Ligilactobacillus saerimneri', 's__Ligilactobacillus salivarius'],
                ['s__Thermophilibacter provencensis', 's__Collinsella ihumii', 's__Collinsella sp002305035',
                 's__Pseudobutyricicoccus sp016901775', 's__Alistipes_A ihumii'],
                ['s__Thermophilibacter sp002159495', 's__Copromonas faecavium', 's__Enterocloster aldenensis',
                 's__Enterocloster bolteae', 's__Mediterraneibacter gallistercoris', 's__DXTB01 sp019410105',
                 's__Anaerotruncus colihominis'],
                ['s__Collinsella tanakaei_B', 's__Enorma massiliensis', 's__Mediterraneibacter excrementipullorum',
                 's__Mediterraneibacter faecigallinarum', 's__Gemmiger avistercoris'],
                ['s__Enorma phocaeensis', 's__Enorma sp900751795', 's__Aphodovivens avicola',
                 's__Heteroscilispira lomanii',
                 's__Neoruminococcus faecicola'],
                ['s__Limicola stercorigallinarum', 's__QALR01 sp944381075', 's__Gemmiger sp944388105',
                 's__CAG-273 sp900752335',
                 's__Ornithomonoglobus_A intestinigallinarum'],
                ['s__Aveggerthella stercoripullorum', 's__Alectryocaccomicrobium excrementavium',
                 's__CALWPV01 sp944383515',
                 's__Blautia_A faecigallinarum', 's__Merdiplasma excrementigallinarum', 's__CALXSR01 sp944391215'],
                ['s__CAJFUR01 sp904420215', 's__Eisenbergiella sp900555195', 's__Gallacutalibacter sp944380825',
                 's__UMGS1264 sp944384815', 's__Pseudoscilispira falkowii'],
                ['s__CAJFUR01 sp904420575', 's__Enterocloster sp944383785', 's__Fusicatenibacter intestinigallinarum',
                 's__Merdisoma sp002160825', 's__RGIG7193 sp944381515', 's__Ruthenibacterium merdipullorum'],
                ['s__Gordonibacter avicola', 's__Amedibacterium sp904395785', 's__Onthousia sp944331715',
                 's__Borkfalkia sp944359385', 's__Heritagella sp905215105', 's__Faecalibacterium avium'],
                ['s__Gordonibacter pamelaeae', 's__Onthousia sp944331805', 's__Ventrenecus stercoripullorum',
                 's__QAMM01 sp900552945', 's__CAG-269 sp944386175', 's__Sutterella massiliensis',
                 's__Pelomonas sp003963075'],
                ['s__Gordonibacter urolithinfaciens', 's__Rubneribacter avistercoris', 's__Blautia_A intestinavium',
                 's__Egerieimonas intestinavium', 's__Fimimorpha excrementavium'],
                ['s__Rubneribacter badeniensis', 's__Clostridium_Q saccharolyticum_A',
                 's__Enterocloster excrementigallinarum',
                 's__Flavonifractor plautii', 's__Intestinimonas pullistercoris'],
                ['s__Pelethenecus faecipullorum', 's__Limosilactobacillus timonensis',
                 's__Caccopulliclostridium gallistercoris', 's__Caccovivens sp930990975', 's__Ventrisoma faecale'],
                ['s__Harrysmithimonas galli', 's__Protoclostridium stercorigallinarum', 's__Anaerotignum sp944384295',
                 's__Massilistercora gallistercoris', 's__Flavonifractor sp944385615', 's__Intestinimonas merdavium',
                 's__CAG-269 sp944390535'],
                ['s__Coprobacillus cateniformis', 's__Enterococcus_A avium', 's__Enterococcus_D gallinarum',
                 's__An181 sp002160325', 's__DXYV01 sp019415645'],
                ['s__Fimiplasma intestinipullorum', 's__Blautia_A gallistercoris', 's__Eubacterium_I sp944380065',
                 's__Limivivens intestinipullorum', 's__Ruminococcus_G avistercoris',
                 's__Agathobaculum intestinigallinarum',
                 's__Avoscillospira_A sp904395865'],
                ['s__Massilimicrobiota merdigallinarum', 's__Thomasclavelia spiroformis', 's__Megamonas funiformis',
                 's__Megamonas hypermegale', 's__Helicobacter_D pullorum'],
                ['s__Massilimicrobiota sp002160865', 's__Pullichristensenella stercorigallinarum',
                 's__Mediterraneibacter sp019418195', 's__Pararuminococcus gallinarum', 's__Zhenpiania hominis'],
                ['s__Thomasclavelia merdavium', 's__Mediterraneibacter guildfordensis', 's__Merdimonas massiliensis_A',
                 's__Faeciplasma gallinarum', 's__CAG-793 sp930980675'],
                ['s__Thomasclavelia ramosa', 's__Enterococcus_E cecorum', 's__DXWE01 sp019417045',
                 's__Anaerofilum faecale',
                 's__Fournierella sp002160145', 's__Veillonella_A magna'],
                ['s__Thomasclavelia sp017889095', 's__Paenibacillus_A macerans', 's__Eisenbergiella pullistercoris',
                 's__RGIG7067 sp944384895', 's__Pseudoruminococcus_B merdavium'],
                ['s__Clostridium_AQ innocuum', 's__Neoanaerotignum_B galli', 's__Eisenbergiella merdavium',
                 's__Eisenbergiella merdigallinarum', 's__JAGZMM01 sp904420015'],
                ['s__Faecalicoccus acidiformans', 's__Faecalitalea cylindroides', 's__Sellimonas avistercoris',
                 's__UMGS1591 sp900553255', 's__Dysosmobacter avistercoris', 's__Gallibacter intestinalis'],
                ['s__Faecalicoccus pleomorphus', 's__Mediterraneibacter tabaqchaliae',
                 's__Phocaeicola excrementipullorum',
                 's__Phocaeicola faecium', 's__Phocaeicola plebeius_A'],
                ['s__Holdemania sp904395815', 's__Alloruminococcus vanvlietii', 's__Fournierella massiliensis',
                 's__Fournierella sp002161595', 's__Gemmiger sp905214345', 's__Gemmiger stercoripullorum'],
                ['s__Merdibacter massiliensis', 's__Aphodocola sp944329425', 's__Gallimonas sp944363395',
                 's__Protoclostridium gallicola', 's__Caccovivens sp930990515', 's__CAG-269 sp944388745',
                 's__CAG-269 sp944392675', 's__CALXJJ01 sp944388605'],
                ['s__Merdibacter merdavium', 's__Enterococcus_B hirae', 's__Anaerobutyricum stercoripullorum',
                 's__Fusicatenibacter sp900543115', 's__Mediterraneibacter caccogallinarum'],
                ['s__Merdibacter merdigallinarum', 's__Parachristensenella avicola', 's__Anaerobutyricum stercoris',
                 's__Mediterraneibacter sp900761655', 's__Merdimonas faecis', 's__Scatomonas merdavium'],
                ['s__Merdibacter sp900759455', 's__Fimihabitans intestinipullorum', 's__Ventrenecus sp944332105',
                 's__Scatavimonas merdipullorum', 's__Butyricimonas paravirosa', 's__Akkermansia muciniphila'],
                ['s__Enterococcus faecalis', 's__Blautia_A avistercoris', 's__Zhenpiania sp019420305',
                 's__Alistipes excrementigallinarum', 's__Alistipes faecigallinarum',
                 's__Parabacteroides intestinigallinarum'],
                ['s__Enterococcus_E cecorum_A', 's__Clostridium paraputrificum', 's__Fimicola merdigallinarum',
                 's__Ruminococcus_B intestinipullorum', 's__RGIG7265 sp944384905'],
                ['s__Lactobacillus crispatus', 's__Limosilactobacillus reuteri_E', 's__Limosilactobacillus vaginalis',
                 's__Anaerofustis stercorihominis_A', 's__Anaeromassilibacillus stercoravium'],
                ['s__Lactobacillus gallinarum', 's__Lactobacillus sp930989465', 's__Limosilactobacillus coleohominis',
                 's__Limosilactobacillus gallistercoris', 's__Limosilactobacillus intestinipullorum'],
                ['s__Ligilactobacillus aviarius_B', 's__Roslinia caecavium', 's__Solibaculum mannosilyticum',
                 's__HGM12998 sp900756495', 's__Lawsonibacter sp944385065', 's__Escherichia sp002965065'],
                ['s__Ligilactobacillus faecavium', 's__Faecisoma sp017887425', 's__Evtepia faecigallinarum',
                 's__Ruminococcus_D sp944388405', 's__CAG-273 sp944388985'],
                ['s__Limosilactobacillus excrementigallinarum', 's__CALVVX01 sp944368815', 's__Choladousia sp944382085',
                 's__Mediterraneibacter sp944375765', 's__Egerieicola faecale', 's__CALWZU01 sp944386095'],
                ['s__Limosilactobacillus ingluviei', 's__Limosilactobacillus sp012843675',
                 's__Streptococcus alactolyticus',
                 's__UMGS1623 sp934647945', 's__Pseudoflavonifractor_A sp944386885',
                 's__Faecalibacterium faecigallinarum'],
                ['s__Limosilactobacillus sp902834055', 's__Tyzzerella sp944383305', 's__Mediterraneibacter pullicola',
                 's__Agathobaculum sp900291975', 's__Butyricicoccus sp900604335'],
                ['s__Streptococcus pluranimalium', 's__Blautia_A excrementipullorum',
                 's__Mediterraneibacter surreyensis',
                 's__Pseudoflavonifractor_A merdipullorum', 's__JAGHEK01 sp017889265'],
                ['s__CAG-582 sp944358235', 's__Coproplasma sp944354125', 's__UBA737 sp944376655',
                 's__CALWZA01 sp944385905',
                 's__CAG-273 sp944393025', 's__UMGS1663 sp944386315'],
                ['s__CALVQX01 sp944358405', 's__Massilistercora sp902406105', 's__Mediterraneibacter stercoripullorum',
                 's__CAG-269 sp944387495', 's__UMGS1994 sp944386155'],
                ['s__CALVRE01 sp944358455', 's__Flavonifractor sp944387215', 's__Pelethomonas sp017887695',
                 's__Pelethomonas sp944387775', 's__UBA1405 sp002305685'],
                ['s__CALVUN01 sp944358875', 's__Onthousia sp944333305', 's__CALWDW01 sp944376795',
                 's__Dwaynesavagella gallinarum', 's__Mediterraneibacter sp900541505',
                 's__Mediterraneibacter sp944376685'],
                ['s__CALVVX01 sp944351765', 's__CALVVX01 sp944371525', 's__CAG-465 sp944388565',
                 's__CAG-269 sp944390615',
                 's__CAG-269 sp944393125'],
                ['s__CALVVX01 sp944358825', 's__Roseburia sp944380515', 's__Butyricicoccus sp017886875',
                 's__Flavonifractor merdavium', 's__CAG-269 sp944390625'],
                ['s__CALVXC01 sp944368805', 's__Onthocola_B sp944363805', 's__CAJJPW01 sp905193725',
                 's__Negativibacillus sp944388365', 's__Egerieisoma faecipullorum'],
                ['s__Caccenecus avistercoris', 's__Onthocola_B sp900546715', 's__Scatosoma pullistercoris',
                 's__Caccopulliclostridium sp944350095', 's__Enterenecus stercoripullorum'],
                ['s__Caccenecus sp017888105', 's__UBA10677 sp900543755', 's__Intestinimonas sp944385655',
                 's__Scatomorpha intestinigallinarum', 's__Pygmaiobacter sp944386485'],
                ['s__Caccenecus sp900758895', 's__Alloclostridium sp944380395', 's__Avimonas intestinalis',
                 's__CAJFPI01 sp944386965', 's__CAG-269 sp944393365'],
                ['s__Caccenecus sp944358125', 's__Guopingia tenuis', 's__Merdivicinus excrementipullorum',
                 's__CAG-273 sp904378095', 's__JAAWPK01 sp944388635'],
                ['s__Caccenecus sp944358135', 's__Mediterraneibacter merdavium', 's__Agathobaculum merdigallinarum',
                 's__Flavonifractor intestinigallinarum', 's__Fournierella sp002159185'],
                ['s__Caccenecus sp944358145', 's__Mediterraneibacter sp944377775', 's__CAG-269 sp944386205',
                 's__CAG-269 sp944391785', 's__Merdicola sp001915925'],
                ['s__Coprosoma sp944358495', 's__Ventrenecus sp944350285', 's__Heritagella sp905200265',
                 's__CAG-448 sp944381085', 's__CALWZE01 sp944385925'],
                ['s__Faecenecus gallistercoris', 's__Mediterraneibacter pullistercoris', 's__Acutalibacter pullicola',
                 's__CAG-273 sp944392105', 's__Phocaeicola coprophilus'],
                ['s__Faecimonas intestinavium', 's__Lachnoclostridium_B faecipullorum',
                 's__Mediterraneibacter sp944376695',
                 's__Mediterraneibacter stercoravium', 's__Ruthenibacterium merdavium'],
                ['s__Faecimonas sp017886705', 's__RGIG4074 sp944376455', 's__Lachnoclostridium_B monacensis',
                 's__Avimonas merdigallinarum', 's__Gallacutalibacter pullicola',
                 's__Lentihominibacter excrementipullorum'],
                ['s__Faecimonas sp944332295', 's__Onthousia faecipullorum', 's__Onthousia sp944363705',
                 's__Gallimonas intestinavium', 's__QAKW01 sp944387895'],
                ['s__Faecimonas sp944333345', 's__Onthousia sp944363685', 's__Ventricola gallistercoris',
                 's__Fournierella merdipullorum', 's__Fournierella pullicola'],
                ['s__Faecimonas sp944358705', 's__Gallimonas sp944367185', 's__Merdisoma sp944375885',
                 's__CAG-269 sp944388685',
                 's__UMGS1663 sp944386655'],
                ['s__Faecimonas sp944358945', 's__RGIG3091 sp944372315', 's__Eubacterium_I avistercoris',
                 's__Gemmiger formicilis_A', 's__CAG-269 sp944386685', 's__CAG-793 sp944392425'],
                ['s__Faecimonas sp944359885', 's__Alloclostridium sp944381275', 's__Massilistercora timonensis',
                 's__Limivicinus faecipullorum', 's__CAG-465 sp944383035'],
                ['s__MGBC162581 sp944332535', 's__Onthousia sp944331915', 's__Onthousia sp944363695',
                 's__Emergencia sp944388465', 's__CAG-269 sp944386715'],
                ['s__Onthocola_B sp944331835', 's__UMGS2016 sp944355255', 's__UBA1685 sp944366945',
                 's__CALWRB01 sp944383855',
                 's__RGIG3155 sp934427095'],
                ['s__Onthocola_B sp944332715', 's__Onthousia sp944363755', 's__Anaerotignum lactatifermentans',
                 's__Caccousia avicola', 's__Heteroscilispira sp944385595', 's__UMGS1663 sp944386335'],
                ['s__Onthocola_B sp944363835', 's__Caccovivens sp930979925', 's__Gemmiger sp944388175',
                 's__CAG-269 sp944387545', 's__RGIG8482 sp904381285'],
                ['s__Onthocola_B stercoravium', 's__Caccosoma sp900762575', 's__Faeciplasma pullistercoris',
                 's__UMGS1781 sp944390405', 's__Phocaeicola caecigallinarum_A'],
                ['s__Onthousia faecavium', 's__Hungatella_B pullicola', 's__CAG-269 sp944386165',
                 's__CAG-273 sp930990645',
                 's__CALXJL01 sp944388615', 's__QAKL01 sp944391285'],
                ['s__Onthousia sp944331955', 's__Ventrenecus sp944371545', 's__UMGS1264 sp944380875',
                 's__Faecivivens sp944388825', 's__CAG-273 sp904420285', 's__CAG-793 sp944393305',
                 's__Rikenella faecigallinarum'],
                ['s__Onthousia sp944351375', 's__RGIG4074 sp017886575', 's__Scatosoma pullicola',
                 's__Neoanaerotignum_A sp944377425', 's__Anaerostipes avistercoris'],
                ['s__Onthousia sp944358355', 's__Acetatifactor stercoripullorum', 's__Agathobaculum pullicola',
                 's__Dysosmobacter sp018228705', 's__Intestinimonas sp944387725', 's__Egerieisoma sp900543695'],
                ['s__Onthousia sp944359735', 's__CALWPT01 sp944383495', 's__Agathobaculum sp944384765',
                 's__Enterenecus sp944385485', 's__Barnesiella viscericola'],
                ['s__Onthousia sp944363735', 's__Coproplasma avicola', 's__Clostridium_Q sp944381615',
                 's__Negativibacillus massiliensis', 's__CAG-273 sp944393505'],
                ['s__Onthousia sp944373065', 's__RUG12867 sp944364705', 's__Coproplasma stercoripullorum',
                 's__Faecimorpha sp944376225', 's__CAG-269 sp944391795', 's__CAKNOI01 sp930990125'],
                ['s__Pelethosoma merdigallinarum', 's__Avoscillospira avicola', 's__Avoscillospira stercorigallinarum',
                 's__Scatomorpha gallistercoris', 's__Ruthenibacterium sp944386555'],
                ['s__Pelethosoma sp944332155', 's__Borkfalkia faecavium', 's__Gallimonas sp900548845',
                 's__Scatosoma sp944375795', 's__Howiella intestinavium', 's__CAG-269 sp930989765',
                 's__CAG-269 sp944388775'],
                ['s__Pelethosoma sp944363775', 's__Gallimonas gallistercoris', 's__Enterenecus sp905210385',
                 's__Ruminococcus_D sp900752625', 's__JAAWPK01 sp944386135'],
                ['s__RUG591 sp944350445', 's__Fimimorpha sp904395845', 's__Scybalomonas excrementigallinarum',
                 's__Fournierella pullistercoris', 's__Fusobacterium_A sp900549465'],
                ['s__Scybalousia sp900543675', 's__Faecousia excrementipullorum', 's__CAG-269 sp944388715',
                 's__CAG-273 sp944392435', 's__Scatovivens faecipullorum'],
                ['s__Scybalousia sp944359075', 's__QAKD01 sp003343965', 's__CAG-269 sp944392635',
                 's__CAG-273 sp944392505',
                 's__CAG-793 sp930980855'],
                ['s__UMGS2016 sp944332375', 's__Gallimonas sp944362555', 's__Limadaptatus stercorigallinarum',
                 's__Caccopulliclostridium sp944372325', 's__CAKRRK01 sp934395135', 's__HGM12669 sp900761935'],
                ['s__Ventrenecus avicola', 's__Caccovivens sp904397185', 's__Avoscillospira stercoripullorum',
                 's__Faecalibacterium gallinarum', 's__Fournierella excrementavium', 's__CAG-269 sp944388705'],
                ['s__Ventrenecus sp944350145', 's__Scatosoma sp904419075', 's__HGM11808 sp944380405',
                 's__Caccomorpha excrementavium', 's__Timburyella sp900554165',
                 's__Pseudoflavonifractor_A intestinipullorum',
                 's__Faecivivens sp944387515'],
                ['s__Ventrenecus sp944351315', 's__Blautia_A sp944380045', 's__Fimenecus sp944384995',
                 's__CALXIC01 sp944388265', 's__Gemmiger sp944382785', 's__Gemmiger_A avium', 's__CAG-269 sp944388795'],
                ['s__Ventrenecus sp944355355', 's__Borkfalkia sp904419945', 's__Mediterraneibacter sp944383745',
                 's__CAG-273 sp944390395', 's__UMGS1663 sp944388655'],
                ['s__Caccosoma faecigallinarum', 's__QANA01 sp900554725', 's__Protoclostridium sp944372345',
                 's__Flemingibacterium merdigallinarum', 's__Scatomorpha stercorigallinarum'],
                ['s__Borkfalkia avicola', 's__Borkfalkia excrementigallinarum', 's__Borkfalkia excrementipullorum',
                 's__Borkfalkia sp017886545', 's__Gallimonas merdae'],
                ['s__Borkfalkia avistercoris', 's__Limiplasma pullistercoris', 's__Protoclostridium sp019113265',
                 's__Caccalectryoclostridium excrementigallinarum', 's__Mediterraneibacter colneyensis'],
                ['s__Borkfalkia excrementavium', 's__Borkfalkia sp904373255', 's__Borkfalkia stercoripullorum',
                 's__Coproplasma stercoravium', 's__Eisenbergiella pullicola'],
                ['s__Borkfalkia faecigallinarum', 's__Borkfalkia sp017886895', 's__Borkfalkia sp944328445',
                 's__Coproplasma stercorigallinarum', 's__Heteroclostridium caecigallinarum'],
                ['s__Borkfalkia faecipullorum', 's__Coproplasma excrementipullorum',
                 's__Ornithoclostridium sp944380285',
                 's__Woodwardibium gallinarum', 's__CALWOS01 sp944383185'],
                ['s__Borkfalkia sp003343765', 's__Eisenbergiella sp904392525', 's__HGM12545 sp900761925',
                 's__Avoscillospira_A sp904395905', 's__Gemmiger excrementipullorum'],
                ['s__Borkfalkia sp904374385', 's__Egerieenecus merdigallinarum', 's__Faecivicinus sp944353735',
                 's__Butyrivibrio_A sp944382105', 's__HGM14224 sp900761905'],
                ['s__Borkfalkia sp944328405', 's__Gallimonas faecium', 's__Gallimonas sp944367465',
                 's__Anaerobutyricum avicola', 's__Intestinimonas stercorigallinarum'],
                ['s__Borkfalkia sp944328905', 's__Mediterraneibacter faecavium', 's__CAJFPI01 sp944385425',
                 's__Avimonoglobus intestinipullorum', 's__Escherichia fergusonii'],
                ['s__Borkfalkia sp944342025', 's__UMGS1264 sp904399395', 's__Flavonifractor avistercoris',
                 's__Lawsonibacter pullicola', 's__UBA866 sp904384225'],
                ['s__Coproplasma avistercoris', 's__Gallimonas merdigallinarum', 's__Onthocola_A gallistercoris',
                 's__Heteroruminococcus faecigallinarum', 's__Cryptoclostridium obscurum'],
                ['s__Coproplasma sp944327465', 's__Gallimonas caecicola', 's__Limadaptatus stercoravium',
                 's__HGM11386 sp900761915', 's__UMGS1795 sp900553555'],
                ['s__Coproplasma sp944341075', 's__CAKTXU01 sp934615635', 's__RUG626 sp944386185',
                 's__Scatomorpha sp944387825',
                 's__CAG-793 sp930986425'],
                ['s__Gallimonas intestinalis', 's__UMGS856 sp900760305', 's__Agathobaculum sp944380945',
                 's__Butyricicoccus_A sp944384655', 's__Scatomorpha intestinavium', 's__CAG-269 sp944386755'],
                ['s__Gallimonas intestinigallinarum', 's__Faecousia faecigallinarum',
                 's__Faecalibacterium faecipullorum',
                 's__Faecalibacterium gallistercoris', 's__Faecalibacterium intestinigallinarum',
                 's__Faecivivens stercorigallinarum'],
                ['s__Gallimonas sp017887095', 's__Pullichristensenella avicola', 's__RACS-045 sp944380355',
                 's__JAGTTR01 sp944384015', 's__RUG14109 sp944384865', 's__CAG-245 sp944388645'],
                ['s__Gallimonas sp944340905', 's__CAJFPI01 sp944386985', 's__CAG-273 sp944390505',
                 's__CAG-273 sp944391825',
                 's__Scatovivens sp944393295'],
                ['s__Scatosoma sp900555925', 's__Ventricola sp944363005', 's__CALXGT01 sp944385915',
                 's__JAAZZIT01 sp944382845',
                 's__CAG-269 sp944388735', 's__Merdicola sp944390295'],
                ['s__Heteroclostridium sp944336125', 's__Acetatifactor sp944384205', 's__CALXEN01 sp944387885',
                 's__Fournierella merdigallinarum', 's__CAG-269 sp944388765'],
                ['s__Alectryocaccomicrobium faecavium', 's__UMGS1975 sp900546685', 's__Ventrousia excrementavium',
                 's__Alloscillospira gallinarum', 's__CALXCT01 sp944386055'],
                ['s__Faecaligallichristensenella faecipullorum', 's__Catenibacillus faecigallinarum',
                 's__Lachnoclostridium_A stercoravium', 's__Merdisoma merdipullorum', 's__Paralachnospira_A sangeri',
                 's__Scybalocola faecipullorum', 's__Faecivivens stercoravium'],
                ['s__Faecivicinus avistercoris', 's__Pullichristensenella stercoripullorum', 's__QALW01 sp900552055',
                 's__Tabaqchalia intestinavium', 's__Pelethomonas intestinigallinarum'],
                ['s__Limiplasma merdipullorum', 's__Flavonifractor sp944385575', 's__Merdivicinus sp944386445',
                 's__Pygmaiobacter sp944388335', 's__UBA866 sp016901855'],
                ['s__Onthenecus intestinigallinarum', 's__Monoglobus merdigallinarum', 's__Enterenecus sp944385465',
                 's__Faecousia faecavium', 's__Scatomorpha sp944385765'],
                ['s__Pullichristensenella excrementipullorum', 's__HGM11327 sp900759935', 's__Roslinia sp019419865',
                 's__Avispirillum faecium', 's__Lentihominibacter excrementavium'],
                ['s__Pullichristensenella sp904420265', 's__UMGS882 sp003343885', 's__Enterenecus avicola',
                 's__Aphodoplasma excrementigallinarum', 's__Mailhella merdigallinarum'],
                ['s__Ventricola intestinavium', 's__CALWPC01 sp944383325', 's__Acutalibacter pullistercoris',
                 's__Merdivicinus intestinigallinarum', 's__Bacteroides xylanisolvens'],
                ['s__CALWSW01 sp944384305', 's__Ornithoclostridium excrementipullorum',
                 's__Ornithoclostridium faecigallinarum',
                 's__Faecousia intestinavium', 's__Scatomorpha merdigallinarum'],
                ['s__RGIG9107 sp019420085', 's__QAKD01 sp944386585', 's__CAG-269 sp944393385', 's__CAG-273 sp944391015',
                 's__HGM13862 sp944393575'],
                ['s__Allochristensenella sp019415425', 's__Acutalibacter stercorigallinarum',
                 's__Gallacutalibacter_A stercoravium', 's__RUG626 sp944385785', 's__Merdivicinus faecavium'],
                ['s__QAND01 sp003150225', 's__Bariatricus faecipullorum', 's__JAGTTR01 sp944381745',
                 's__CALXCQ01 sp944386835',
                 's__Anaerotruncus sp944387965'],
                ['s__Caccovivens sp944348085', 's__Avoscillospira_A sp944385365', 's__Enterenecus capillosus_A',
                 's__Faeciplasma avium', 's__Fournierella merdavium', 's__CAG-273 sp930991035',
                 's__CAG-793 sp944388895'],
                ['s__Spyradocola merdavium', 's__Choladousia intestinipullorum', 's__UBA1417 sp900552925',
                 's__Evtepia excrementipullorum', 's__UBA3818 sp904397845'],
                ['s__Alloclostridium intestinigallinarum', 's__Metalachnospira gallinarum',
                 's__Acutalibacter sp900755895',
                 's__Faecivivens stercoripullorum', 's__Bradyrhizobium sp002831585'],
                ['s__Anaerotignum merdipullorum', 's__Mediterraneibacter sp944381495', 's__CALWKP01 sp944380775',
                 's__Faecousia excrementigallinarum', 's__CAG-269 sp904419095'],
                ['s__CALWRB01 sp944381395', 's__CAJFPI01 sp904419145', 's__Avimicrobium caecorum',
                 's__Fimisoma avicola',
                 's__Fimisoma sp900540145'],
                ['s__CALWSX01 sp944384285', 's__Limousia pullorum', 's__Agathobaculum merdavium',
                 's__Pseudobutyricicoccus sp003477405', 's__Fimisoma sp900754795'],
                ['s__Coprocola pullicola', 's__Scatomonas pullistercoris', 's__Acutalibacter sp904419785',
                 's__Butyricicoccus pullicaecorum', 's__Avoscillospira_A avistercoris'],
                ['s__Coprocola sp017888185', 's__Lachnoclostridium_A sp944383765', 's__UMGS1071 sp944384835',
                 's__Agathobaculum merdipullorum', 's__CAG-269 sp930987745'],
                ['s__Neoanaerotignum_A tabaqchaliae', 's__Mediterraneibacter intestinigallinarum',
                 's__Gemmiger avicola',
                 's__Gemmiger stercorigallinarum', 's__Negativibacillus faecipullorum'],
                ['s__Neoanaerotignum_B sp944378105', 's__Enterocloster sp944382045', 's__Enterocloster sp944384065',
                 's__Dysosmobacter excrementigallinarum', 's__CAG-269 sp944386675'],
                ['s__Faecimorpha stercoravium', 's__Lachnospira sp944381165', 's__Mediterraneibacter sp904418845',
                 's__UMGS1071 sp904397205', 's__Flavonifractor sp002159455', 's__Ruthenibacterium avium'],
                ['s__Gallispira edinburgensis', 's__Mediterraneibacter sp019420405', 's__Fimenecus sp900545625',
                 's__Dysosmobacter sp944385405', 's__Ornithomonoglobus merdipullorum'],
                ['s__Acetatifactor sp944383825', 's__Eisenbergiella stercorigallinarum',
                 's__Mediterraneibacter merdipullinarum', 's__UMGS1384 sp900551265', 's__CAG-269 sp944387425'],
                ['s__Anaerostipes butyraticus', 's__Sellimonas caecigallum', 's__Ventrimonas merdavium',
                 's__Lawsonibacter sp944387755', 's__Gemmiger sp944382805', 's__CAG-273 sp944393165',
                 's__Klebsiella pneumoniae', 's__Proteus mirabilis'],
                ['s__Anaerostipes excrementavium', 's__Sellimonas intestinalis', 's__CAJFTX01 sp904420075',
                 's__Metaruminococcus caecorum', 's__Escherichia coli'],
                ['s__Blautia merdavium', 's__Mediterraneibacter norwichensis', 's__Scatomonas merdigallinarum',
                 's__Pseudoflavonifractor capillosus', 's__Avimicrobium faecavium'],
                ['s__Blautia merdigallinarum', 's__Blautia_A faecavium', 's__Eisenbergiella intestinigallinarum',
                 's__Mediterraneibacter merdigallinarum', 's__UBA644 sp014872655'],
                ['s__Blautia ornithocaccae', 's__Blautia pullistercoris', 's__Caccovicinus merdipullorum',
                 's__Fimimorpha sp904420225', 's__JAGZHZ01 sp944376425', 's__Mediterraneibacter catenae',
                 's__Eubacterium_R sp017886765'],
                ['s__Blautia pullicola', 's__Choladousia intestinigallinarum', 's__Mediterraneibacter intestinavium',
                 's__Pseudobutyricicoccus lothianensis', 's__Dysosmobacter excrementavium'],
                ['s__Blautia sp944380235', 's__Blautia_A excrementigallinarum', 's__Fimimorpha faecalis',
                 's__RGIG7193 sp944383835', 's__QAMM01 sp900762715'],
                ['s__Blautia stercorigallinarum', 's__Lachnoclostridium_A stercoripullorum', 's__UBA3402 sp944380605',
                 's__Acutalibacter sp905215055', 's__Acutalibacter stercoravium', 's__Flavonifractor avicola',
                 's__Fumia sp904396495'],
                ['s__Blautia_A intestinigallinarum', 's__Choladocola avistercoris', 's__Copromonas avistercoris',
                 's__Enterocloster excrementipullorum', 's__UMGS1370 sp904395885', 's__Acutalibacter ornithocaccae',
                 's__Pseudoscilispira faecavium', 's__Bilophila wadsworthia'],
                ['s__CAG-303 sp944384155', 's__Dysosmobacter sp944387055', 's__Onthomonas avicola',
                 's__Clostridioides difficile', 's__Acinetobacter wanghuae'],
                ['s__Choladocola sp944381625', 's__Mediterraneibacter cottocaccae', 's__Scatomonas hejianensis',
                 's__CALXGH01 sp944387845', 's__CAG-273 sp944389655'],
                ['s__Choladousia intestinavium', 's__CAJFPI01 sp904398675', 's__CAJFPI01 sp904420435',
                 's__Pelethomonas sp900549475', 's__Ruthenibacterium sp944388395'],
                ['s__Egerieimonas_A faecigallinarum', 's__Merdisoma faecalis', 's__Paralachnospira avium',
                 's__Agathobaculum pullistercoris', 's__Anaerofilum excrementigallinarum'],
                ['s__Eisenbergiella sp944380095', 's__Merdisoma sp944383645', 's__Lawsonibacter sp904420465',
                 's__Anaerotruncus excrementipullorum', 's__Ruthenibacterium sp944386565'],
                ['s__Eubacterium_G sp904420085', 's__Mediterraneibacter excrementavium',
                 's__Mediterraneibacter quadrami',
                 's__Paralachnospira sp944375845', 's__Enterenecus faecium', 's__CAG-269 sp904387305'],
                ['s__Fimousia stercorigallinarum', 's__Mediterraneibacter intestinavium',
                 's__Eubacterium_R faecigallinarum',
                 's__Eubacterium_R faecipullorum', 's__Fimenecus excrementavium', 's__Flavonifractor sp944385585'],
                ['s__Fusicatenibacter sp017887445', 's__Dysosmobacter sp944385455', 's__CAG-269 sp904384245',
                 's__CAG-269 sp944388695', 's__Prevotella massiliensis'],
                ['s__Lachnoclostridium_A avicola', 's__Limivivens merdigallinarum',
                 's__Mediterraneibacter glycyrrhizinilyticus_A', 's__Mediterraneibacter vanvlietii',
                 's__Dysosmobacter faecalis', 's__Brachyspira innocens'],
                ['s__Lachnoclostridium_B massiliensis_A', 's__Mediterranea ndongoniae', 's__Mediterranea pullorum',
                 's__Phocaeicola sp002161765', 's__Barnesiella merdipullorum', 's__Merdimorpha stercoravium'],
                ['s__Lachnoclostridium_B sp000765215', 's__Mediterranea sp900553815', 's__Phocaeicola intestinalis',
                 's__Caccocola faecigallinarum', 's__Caccocola sp002159945'],
                ['s__Mediterraneibacter avicola', 's__Mediterraneibacter caccavium',
                 's__Mediterraneibacter stercorigallinarum',
                 's__CAJFUH01 sp904420155', 's__Fimenecus stercoravium'],
                ['s__Mediterraneibacter sp900120155', 's__Paralachnospira caecorum', 's__Pseudolachnospira avium',
                 's__Pseudolachnospira sp944376945', 's__Emergencia sp904420065'],
                ['s__Pullilachnospira stercoravium', 's__CAJFPI01 sp944386995', 's__Gemmiger faecavium',
                 's__Gemmiger stercoravium', 's__Massiliimalia sp944382885'],
                ['s__Acutalibacter sp904391645', 's__SIG471 sp905199135', 's__Intestinimonas stercoravium',
                 's__Metaruminococcus sp944386475', 's__Ruthenibacterium merdigallinarum'],
                ['s__Caccousia sp900752115', 's__Eubacterium_R sp900539425', 's__Avoscillospira sp944386905',
                 's__Galloscillospira_A stercoripullorum', 's__Pseudoflavonifractor_A gallinarum',
                 's__CALXEM01 sp944387335'],
                ['s__Heritagella intestinalis', 's__Lawsonibacter sp019424865', 's__Lawsonibacter sp900545895',
                 's__Aristotella avistercoris', 's__Schneewindia gallinarum'],
                ['s__Solibaculum sp904397895', 's__Bacteroides fragilis', 's__Phocaeicola dorei',
                 's__Odoribacter splanchnicus',
                 's__Alistipes onderdonkii', 's__Parabacteroides distasonis'],
                ['s__UMGS1071 sp900541905', 's__Ornithomonoglobus sp904420525', 's__CAG-266 sp000436095',
                 's__Megasphaera stantonii', 's__Desulfovibrio sp900556755'],
                ['s__UMGS1623 sp900553525', 's__CAJFPI01 sp904420145', 's__Dysosmobacter sp904393855',
                 's__Scatomorpha sp900759385', 's__Angelakisella sp904420255'],
                ['s__Agathobaculum sp900557315', 's__Dysosmobacter sp944382995', 's__HGM12957 sp900760695',
                 's__Gemmiger formicilis_B', 's__Merdicola sp900553015'],
                ['s__Butyricicoccus avistercoris', 's__Woodwardibium sp900754535', 's__Lawsonibacter sp002161175',
                 's__Limivicinus sp944387735', 's__Scatomorpha merdavium'],
                ['s__Butyricicoccus sp904420185', 's__Butyricicoccus sp944381005', 's__CALXDZ01 sp944387205',
                 's__Pygmaiobacter gallistercoris', 's__CAG-273 sp944392085'],
                ['s__CALWWS01 sp944385305', 's__Lawsonibacter sp944385075', 's__Lawsonibacter sp944385645',
                 's__Pseudoflavonifractor sp904419835', 's__Scatomorpha pullicola'],
                ['s__Dysosmobacter pullicola', 's__Faecousia gallistercoris', 's__Galloscillospira_A excrementavium',
                 's__CALYAO01 sp944393605', 's__HGM11507 sp900761005'],
                ['s__Bacteroides uniformis', 's__Mediterranea massiliensis', 's__Phocaeicola barnesiae',
                 's__Phocaeicola coprocola', 's__Phocaeicola sp900551065', 's__Phocaeicola_A sp900291465'],
                ['s__Paraprevotella stercoravium', 's__Phocaeicola faecipullorum', 's__Prevotella lascolaii',
                 's__Parabacteroides sp002159645', 's__Desulfovibrio faecigallinarum'],
                ['s__Phocaeicola sp900546355', 's__Phocaeicola_A sp003489705', 's__Desulfovibrio sp944327285',
                 's__Aphodousia secunda_A', 's__Duodenibacillus intestinavium', 's__Succinatimonas hippei']
            ]
            # some entry can be appearing in more than one clustter so  ...
            if selected_bacteria.endswith("_otu"):
                selected_bacteria = selected_bacteria[:-4]
            for cluster in cluster_data_0_6:
                if selected_bacteria in cluster:
                    found = True
                    cluster_found = cluster
                    threshold = "0.6"
                    break
            if not found:
                for cluster in cluster_data_0_5:
                    if selected_bacteria in cluster:
                        found = True
                        cluster_found = cluster
                        threshold = "0.5"
                        break
            if not found:
                for cluster in cluster_data_0_4:
                    if selected_bacteria in cluster:
                        found = True
                        cluster_found = cluster
                        threshold = "0.4"
                        break
            if found:
                cleaned_cluster = [s.replace("s__", "") for s in cluster_found]
                return JsonResponse({
                    "found": True,
                    "threshold": threshold,
                    "cluster_members": cleaned_cluster,
                })
            else:
                return JsonResponse({"found": False})


        # ----- Common filters (only for branches that need tissue) -----
        # Common filters
        tissue = request.GET.get('tissue')
        if tissue is None:
            return J({'error': 'Missing tissue.'}, status=400)
        # base_tissue_q = Q(from_tissue=tissue) | Q(to_tissue=tissue)
        # here tissue is otu to adapat for each case
        base_tissue_q = Q(from_tissue='otu') & Q(to_tissue=tissue)

        # (B) Single-var filtering
        if ('multi_variable' not in request.GET
                and 'table_filter' not in request.GET
                and 'cluster_lookup' not in request.GET
                and 'explore_table_filter' not in request.GET
                and 'explore_distribution' not in request.GET):
            var = request.GET.get('variable')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = OtuCorrelationRoss.objects.filter(
                base_tissue_q,
                var2=var,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({'results': [], 'total_count': 0})
            top = filt.order_by('-correlation')[:100]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count})

        # (C) Multi-var filtering
        if 'multi_variable' in request.GET:
            variables = request.GET.getlist('variables[]')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = OtuCorrelationRoss.objects.filter(
                base_tissue_q,
                var2__in=variables,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({'results': [], 'total_count': 0})
            top = filt.order_by('-correlation')[:100]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count})



        # (E) Table Filtering
        if 'table_filter' in request.GET:
            var = request.GET.get('variable')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = OtuCorrelationRoss.objects.filter(
                base_tissue_q,
                var2=var,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({
                    'results': [],
                    'total_count': 0,
                    'overview': {'median': None, 'q1': None, 'q3': None}
                })
            top = filt.order_by('-correlation')[:200]

            results = []
            vals = [o.correlation for o in filt]
            overview = {
                'median': r3(np.median(vals)),
                'q1': r3(np.quantile(vals, 0.25)),
                'q3': r3(np.quantile(vals, 0.75)),
            }
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'Coefficient': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count, 'overview': overview})

        # (F) Explore distribution
        if 'explore_distribution' in request.GET:
            # qs = MuscleCorrelation.objects.filter(base_tissue_q).values_list('correlation', flat=True)
            qs = (OtuCorrelationRoss.objects
                 .filter(base_tissue_q, correlation__isnull=False)
                 .values_list('correlation', flat=True)
                )
            series = list(qs)
            if not series:
                return J({'error': 'No data found.'}, status=400)
            stats = {
                'min': r3(min(series)),
                'q1': r3(np.quantile(series, 0.25)),
                'median': r3(np.median(series)),
                'q3': r3(np.quantile(series, 0.75)),
                'max': r3(max(series)),
            }
            return J({'distribution': {'correlation_values': series, 'stats': stats}})

        # (G) Explore table filter
        if 'explore_table_filter' in request.GET:
            try:
                corr_min = float(request.GET.get('corrMin', -1))
                corr_max = float(request.GET.get('corrMax', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = OtuCorrelationRoss.objects.filter(
                base_tissue_q,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            top = filt.order_by('-correlation')[:200]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            vals = [o.correlation for o in filt]
            overview = {
                'median': r3(np.median(vals)) if vals else None,
                'q1': r3(np.quantile(vals, 0.25)) if vals else None,
                'q3': r3(np.quantile(vals, 0.75)) if vals else None,
            }
            return J({'results': results, 'total_count': total_count, 'overview': overview})

        return J({'error': 'No recognized AJAX action.'}, status=400)

    # --- Non-AJAX: Build sunbursts and context ---
    def clusters_to_df(data):
        rows = []
        for i, sublist in enumerate(data, start=1):
            cluster_name = f"Cluster {i}"
            for species in sublist:
                rows.append({"Cluster": cluster_name, "Species": species.replace("s__", ""), "Value": 1})
        return pd.DataFrame(rows)

    cluster_data_0_6 = [
        ['s__Ligilactobacillus salivarius', 's__Brachyspira innocens', 's__Limicola phocaeensis_A',
         's__Bifidobacterium pullorum_B', 's__Phocaeicola intestinalis', 's__Succinatimonas hippei',
         's__Lachnoclostridium_A stercorigallinarum', 's__Megamonas hypermegale_A'],
        ['s__Gemmiger faecavium', 's__Barnesiella merdipullorum', 's__Mediterraneibacter sp944383745',
         's__Bradyrhizobium sp002831585', 's__Dysosmobacter faecalis', 's__Enterococcus_B hirae'],
        ['s__Anaerotruncus excrementipullorum', 's__Mediterraneibacter stercorigallinarum',
         's__Mediterraneibacter excrementavium', 's__Alloclostridium intestinigallinarum',
         's__Faecivivens stercoripullorum'],
        ['s__Lachnoclostridium_B sp000765215', 's__Enorma phocaeensis',
         's__Dysosmobacter excrementavium', 's__Aphodousia secunda_A', 's__Caccocola sp002159945']]
    cluster_data_0_5 = [
        ['s__Ligilactobacillus salivarius', 's__Brachyspira innocens', 's__Limicola phocaeensis_A',
         's__Bifidobacterium pullorum_B', 's__Phocaeicola intestinalis', 's__Succinatimonas hippei',
         's__Lachnoclostridium_A stercorigallinarum', 's__Megamonas hypermegale_A'],
        ['s__Enterocloster sp944383785', 's__Mediterraneibacter sp020687545',
         's__Parachristensenella avicola', 's__Acutalibacter sp900755895',
         's__Bariatricus faecipullorum', 's__Mediterraneibacter quadrami',
         's__Blautia_A faecigallinarum'],
        ['s__Mediterranea ndongoniae', 's__Scatomorpha stercorigallinarum',
         's__Faecalibacterium intestinigallinarum', 's__Faecousia intestinavium',
         's__UBA1405 sp002305685', 's__Anaerotruncus sp944387965'],
        ['s__Lachnoclostridium_A avicola', 's__Gemmiger stercoravium', 's__RGIG4074 sp944376455',
         's__Mediterraneibacter faecipullorum', 's__Aveggerthella excrementigallinarum',
         's__Mediterraneibacter merdigallinarum'],
        ['s__Gallimonas caecicola', 's__Anaerostipes avistercoris', 's__Coprocola pullicola',
         's__QANA01 sp900554725', 's__Angelakisella sp904420255', 's__Borkfalkia faecipullorum'],
        ['s__Gemmiger faecavium', 's__Barnesiella merdipullorum', 's__Mediterraneibacter sp944383745',
         's__Bradyrhizobium sp002831585', 's__Dysosmobacter faecalis', 's__Enterococcus_B hirae'],
        ['s__Anaerotruncus excrementipullorum', 's__Mediterraneibacter stercorigallinarum',
         's__Mediterraneibacter excrementavium', 's__Alloclostridium intestinigallinarum',
         's__Faecivivens stercoripullorum'],
        ['s__Ventrenecus sp944355355', 's__Borkfalkia excrementavium', 's__Flavonifractor sp002159455',
         's__Gallimonas intestinigallinarum', 's__Avoscillospira stercorigallinarum'],
        ['s__Lachnoclostridium_B sp000765215', 's__Enorma phocaeensis',
         's__Dysosmobacter excrementavium', 's__Aphodousia secunda_A', 's__Caccocola sp002159945']]

    cluster_data_0_4 = [
        ['s__CALXCQ01 sp944386835', 's__Flemingibacterium merdigallinarum', 's__UMGS1264 sp944384815',
         's__Faecenecus gallistercoris', 's__Limosilactobacillus sp012843675',
         's__JAGTTR01 sp944381745', 's__Metalachnospira gallinarum', 's__Fimimorpha sp904420225',
         's__Faecousia faecigallinarum', 's__CAJFUR01 sp904420215', 's__CAJFPI01 sp904398675',
         's__RGIG7193 sp944383835'], ['s__Heteroclostridium caecigallinarum', 's__Gallimonas caecicola',
                                      's__Anaerostipes avistercoris', 's__QANA01 sp900554725',
                                      's__Coprocola pullicola', 's__Angelakisella sp904420255',
                                      's__Thermophilibacter stercoravium',
                                      's__Borkfalkia faecipullorum', 's__Scatosoma pullicola',
                                      's__Borkfalkia faecigallinarum',
                                      's__Scatomorpha merdigallinarum'],
        ['s__QAMM01 sp900762715', 's__Butyricimonas paravirosa', 's__Lawsonibacter sp944385075',
         's__CALWWS01 sp944385305', 's__Caccousia avistercoris', 's__Pseudobutyricicoccus sp016901775',
         's__Lawsonibacter sp944385645', 's__Ruthenibacterium merdigallinarum',
         's__Holdemania sp904395815'],
        ['s__Phocaeicola sp900546355', 's__Parabacteroides sp002159645', 's__Prevotella lascolaii',
         's__Paraprevotella stercoravium', 's__Phocaeicola barnesiae', 's__Mediterranea sp900553815',
         's__Desulfovibrio sp944327285', 's__Phocaeicola_A sp900291465',
         's__Mediterranea massiliensis'],
        ['s__Borkfalkia excrementavium', 's__Eisenbergiella pullicola', 's__Ruthenibacterium avium',
         's__Avoscillospira stercorigallinarum', 's__Ventrenecus sp944355355',
         's__Flavonifractor sp002159455', 's__Pseudoscilispira falkowii',
         's__Gallimonas intestinigallinarum'],
        ['s__Eubacterium_R faecale', 's__Mediterraneibacter tabaqchaliae',
         's__Pseudoflavonifractor capillosus', 's__Pygmaiobacter sp944386485',
         's__Egerieimonas_A faecigallinarum', 's__Dysosmobacter sp904393855',
         's__Scatomonas merdigallinarum', 's__Neoanaerotignum_B sp944378105'],
        ['s__Ligilactobacillus salivarius', 's__Brachyspira innocens', 's__Limicola phocaeensis_A',
         's__Bifidobacterium pullorum_B', 's__Phocaeicola intestinalis', 's__Succinatimonas hippei',
         's__Lachnoclostridium_A stercorigallinarum', 's__Megamonas hypermegale_A'],
        ['s__Acutalibacter pullicola', 's__Faecalibacterium gallinarum', 's__SIG471 sp905199135',
         's__Avoscillospira_A avistercoris', 's__CAJFPI01 sp904420435', 's__Borkfalkia sp904419945',
         's__Gallimonas sp944367465', 's__Avoscillospira stercoripullorum'],
        ['s__Caccosoma faecigallinarum', 's__Borkfalkia stercoripullorum', 's__UMGS1623 sp900553525',
         's__Anaerobutyricum stercoris', 's__CALWPC01 sp944383325', 's__Acutalibacter ornithocaccae',
         's__Coproplasma stercorigallinarum', 's__CAG-273 sp944392105'],
        ['s__CALXSR01 sp944391215', 's__Caccocola faecigallinarum', 's__Merdivicinus faecavium',
         's__Desulfovibrio faecigallinarum', 's__UBA3402 sp944380605', 's__Bacteroides xylanisolvens',
         's__Aveggerthella stercoripullorum'],
        ['s__Enterocloster sp944383785', 's__Mediterraneibacter sp020687545',
         's__Parachristensenella avicola', 's__Acutalibacter sp900755895',
         's__Bariatricus faecipullorum', 's__Mediterraneibacter quadrami',
         's__Blautia_A faecigallinarum'],
        ['s__Lachnoclostridium_A avicola', 's__Gemmiger stercoravium', 's__RGIG4074 sp944376455',
         's__Mediterraneibacter faecipullorum', 's__Aveggerthella excrementigallinarum',
         's__Mediterraneibacter glycyrrhizinilyticus_A', 's__Mediterraneibacter merdigallinarum'],
        ['s__Mediterraneibacter norwichensis', 's__CALXCT01 sp944386055',
         's__Ruthenibacterium sp944386555', 's__Limosilactobacillus coleohominis',
         's__Alectryocaccomicrobium excrementavium', 's__Faecimonas intestinavium'],
        ['s__Eisenbergiella sp900555195', 's__Limosilactobacillus gallistercoris',
         's__Borkfalkia excrementipullorum', 's__Scatomonas merdavium',
         's__Ruthenibacterium merdipullorum', 's__Scatomorpha pullicola'],
        ['s__Blautia merdavium', 's__Copromonas faecavium', 's__Anaeromassilibacillus stercoravium',
         's__Neoanaerotignum_B galli', 's__Ornithomonoglobus sp904420525',
         's__Gordonibacter urolithinfaciens'],
        ['s__Mediterranea ndongoniae', 's__Scatomorpha stercorigallinarum',
         's__Faecalibacterium intestinigallinarum', 's__Faecousia intestinavium',
         's__UBA1405 sp002305685', 's__Anaerotruncus sp944387965'],
        ['s__Gemmiger faecavium', 's__Barnesiella merdipullorum', 's__Mediterraneibacter sp944383745',
         's__Bradyrhizobium sp002831585', 's__Dysosmobacter faecalis', 's__Enterococcus_B hirae'],
        ['s__Anaerotruncus excrementipullorum', 's__Mediterraneibacter stercorigallinarum',
         's__Mediterraneibacter excrementavium', 's__Alloclostridium intestinigallinarum',
         's__Faecivivens stercoripullorum'],
        ['s__Blautia_A gallistercoris', 's__Evtepia excrementipullorum', 's__UMGS1591 sp900553255',
         's__Paralachnospira caecorum', 's__Avispirillum faecium'],
        ['s__Agathobaculum intestinigallinarum', 's__Avimicrobium caecorum',
         's__Scybalocola faecipullorum', 's__Pullilachnospira stercoravium',
         's__Thermophilibacter provencensis'],
        ['s__Flavonifractor plautii', 's__Clostridium_Q saccharolyticum_A',
         's__Onthovicinus excrementipullorum', 's__Gordonibacter pamelaeae',
         's__Eubacterium_R faecavium'], ['s__Lachnoclostridium_B sp000765215', 's__Enorma phocaeensis',
                                         's__Dysosmobacter excrementavium', 's__Aphodousia secunda_A',
                                         's__Caccocola sp002159945'],
        ['s__CAJFPI01 sp904419145', 's__Faecalicoccus acidiformans',
         's__Merdiplasma excrementigallinarum', 's__Collinsella tanakaei_B',
         's__Ruminococcus_G avistercoris'],
        ['s__Alloscillospira gallinarum', 's__Lawsonibacter sp019424865',
         's__Avoscillospira_A sp904395905', 's__Avimonas merdigallinarum',
         's__Limosilactobacillus intestinipullorum'],
        ['s__Eisenbergiella merdavium', 's__Choladousia intestinigallinarum', 's__Merdimonas faecis',
         's__Ventricola intestinavium', 's__Blautia_A intestinavium']]

    cluster_data_0_3 = [
        ['s__Bifidobacterium pullorum_B', 's__Thermophilibacter avistercoris', 's__Coprousia sp002159765',
         's__Lactobacillus johnsonii', 's__Ligilactobacillus saerimneri', 's__Ligilactobacillus salivarius'],
        ['s__Thermophilibacter provencensis', 's__Collinsella ihumii', 's__Collinsella sp002305035',
         's__Pseudobutyricicoccus sp016901775', 's__Alistipes_A ihumii'],
        ['s__Thermophilibacter sp002159495', 's__Copromonas faecavium', 's__Enterocloster aldenensis',
         's__Enterocloster bolteae', 's__Mediterraneibacter gallistercoris', 's__DXTB01 sp019410105',
         's__Anaerotruncus colihominis'],
        ['s__Collinsella tanakaei_B', 's__Enorma massiliensis', 's__Mediterraneibacter excrementipullorum',
         's__Mediterraneibacter faecigallinarum', 's__Gemmiger avistercoris'],
        ['s__Enorma phocaeensis', 's__Enorma sp900751795', 's__Aphodovivens avicola',
         's__Heteroscilispira lomanii',
         's__Neoruminococcus faecicola'],
        ['s__Limicola stercorigallinarum', 's__QALR01 sp944381075', 's__Gemmiger sp944388105',
         's__CAG-273 sp900752335',
         's__Ornithomonoglobus_A intestinigallinarum'],
        ['s__Aveggerthella stercoripullorum', 's__Alectryocaccomicrobium excrementavium',
         's__CALWPV01 sp944383515',
         's__Blautia_A faecigallinarum', 's__Merdiplasma excrementigallinarum', 's__CALXSR01 sp944391215'],
        ['s__CAJFUR01 sp904420215', 's__Eisenbergiella sp900555195', 's__Gallacutalibacter sp944380825',
         's__UMGS1264 sp944384815', 's__Pseudoscilispira falkowii'],
        ['s__CAJFUR01 sp904420575', 's__Enterocloster sp944383785', 's__Fusicatenibacter intestinigallinarum',
         's__Merdisoma sp002160825', 's__RGIG7193 sp944381515', 's__Ruthenibacterium merdipullorum'],
        ['s__Gordonibacter avicola', 's__Amedibacterium sp904395785', 's__Onthousia sp944331715',
         's__Borkfalkia sp944359385', 's__Heritagella sp905215105', 's__Faecalibacterium avium'],
        ['s__Gordonibacter pamelaeae', 's__Onthousia sp944331805', 's__Ventrenecus stercoripullorum',
         's__QAMM01 sp900552945', 's__CAG-269 sp944386175', 's__Sutterella massiliensis',
         's__Pelomonas sp003963075'],
        ['s__Gordonibacter urolithinfaciens', 's__Rubneribacter avistercoris', 's__Blautia_A intestinavium',
         's__Egerieimonas intestinavium', 's__Fimimorpha excrementavium'],
        ['s__Rubneribacter badeniensis', 's__Clostridium_Q saccharolyticum_A',
         's__Enterocloster excrementigallinarum',
         's__Flavonifractor plautii', 's__Intestinimonas pullistercoris'],
        ['s__Pelethenecus faecipullorum', 's__Limosilactobacillus timonensis',
         's__Caccopulliclostridium gallistercoris', 's__Caccovivens sp930990975', 's__Ventrisoma faecale'],
        ['s__Harrysmithimonas galli', 's__Protoclostridium stercorigallinarum', 's__Anaerotignum sp944384295',
         's__Massilistercora gallistercoris', 's__Flavonifractor sp944385615', 's__Intestinimonas merdavium',
         's__CAG-269 sp944390535'],
        ['s__Coprobacillus cateniformis', 's__Enterococcus_A avium', 's__Enterococcus_D gallinarum',
         's__An181 sp002160325', 's__DXYV01 sp019415645'],
        ['s__Fimiplasma intestinipullorum', 's__Blautia_A gallistercoris', 's__Eubacterium_I sp944380065',
         's__Limivivens intestinipullorum', 's__Ruminococcus_G avistercoris',
         's__Agathobaculum intestinigallinarum',
         's__Avoscillospira_A sp904395865'],
        ['s__Massilimicrobiota merdigallinarum', 's__Thomasclavelia spiroformis', 's__Megamonas funiformis',
         's__Megamonas hypermegale', 's__Helicobacter_D pullorum'],
        ['s__Massilimicrobiota sp002160865', 's__Pullichristensenella stercorigallinarum',
         's__Mediterraneibacter sp019418195', 's__Pararuminococcus gallinarum', 's__Zhenpiania hominis'],
        ['s__Thomasclavelia merdavium', 's__Mediterraneibacter guildfordensis', 's__Merdimonas massiliensis_A',
         's__Faeciplasma gallinarum', 's__CAG-793 sp930980675'],
        ['s__Thomasclavelia ramosa', 's__Enterococcus_E cecorum', 's__DXWE01 sp019417045',
         's__Anaerofilum faecale',
         's__Fournierella sp002160145', 's__Veillonella_A magna'],
        ['s__Thomasclavelia sp017889095', 's__Paenibacillus_A macerans', 's__Eisenbergiella pullistercoris',
         's__RGIG7067 sp944384895', 's__Pseudoruminococcus_B merdavium'],
        ['s__Clostridium_AQ innocuum', 's__Neoanaerotignum_B galli', 's__Eisenbergiella merdavium',
         's__Eisenbergiella merdigallinarum', 's__JAGZMM01 sp904420015'],
        ['s__Faecalicoccus acidiformans', 's__Faecalitalea cylindroides', 's__Sellimonas avistercoris',
         's__UMGS1591 sp900553255', 's__Dysosmobacter avistercoris', 's__Gallibacter intestinalis'],
        ['s__Faecalicoccus pleomorphus', 's__Mediterraneibacter tabaqchaliae',
         's__Phocaeicola excrementipullorum',
         's__Phocaeicola faecium', 's__Phocaeicola plebeius_A'],
        ['s__Holdemania sp904395815', 's__Alloruminococcus vanvlietii', 's__Fournierella massiliensis',
         's__Fournierella sp002161595', 's__Gemmiger sp905214345', 's__Gemmiger stercoripullorum'],
        ['s__Merdibacter massiliensis', 's__Aphodocola sp944329425', 's__Gallimonas sp944363395',
         's__Protoclostridium gallicola', 's__Caccovivens sp930990515', 's__CAG-269 sp944388745',
         's__CAG-269 sp944392675', 's__CALXJJ01 sp944388605'],
        ['s__Merdibacter merdavium', 's__Enterococcus_B hirae', 's__Anaerobutyricum stercoripullorum',
         's__Fusicatenibacter sp900543115', 's__Mediterraneibacter caccogallinarum'],
        ['s__Merdibacter merdigallinarum', 's__Parachristensenella avicola', 's__Anaerobutyricum stercoris',
         's__Mediterraneibacter sp900761655', 's__Merdimonas faecis', 's__Scatomonas merdavium'],
        ['s__Merdibacter sp900759455', 's__Fimihabitans intestinipullorum', 's__Ventrenecus sp944332105',
         's__Scatavimonas merdipullorum', 's__Butyricimonas paravirosa', 's__Akkermansia muciniphila'],
        ['s__Enterococcus faecalis', 's__Blautia_A avistercoris', 's__Zhenpiania sp019420305',
         's__Alistipes excrementigallinarum', 's__Alistipes faecigallinarum',
         's__Parabacteroides intestinigallinarum'],
        ['s__Enterococcus_E cecorum_A', 's__Clostridium paraputrificum', 's__Fimicola merdigallinarum',
         's__Ruminococcus_B intestinipullorum', 's__RGIG7265 sp944384905'],
        ['s__Lactobacillus crispatus', 's__Limosilactobacillus reuteri_E', 's__Limosilactobacillus vaginalis',
         's__Anaerofustis stercorihominis_A', 's__Anaeromassilibacillus stercoravium'],
        ['s__Lactobacillus gallinarum', 's__Lactobacillus sp930989465', 's__Limosilactobacillus coleohominis',
         's__Limosilactobacillus gallistercoris', 's__Limosilactobacillus intestinipullorum'],
        ['s__Ligilactobacillus aviarius_B', 's__Roslinia caecavium', 's__Solibaculum mannosilyticum',
         's__HGM12998 sp900756495', 's__Lawsonibacter sp944385065', 's__Escherichia sp002965065'],
        ['s__Ligilactobacillus faecavium', 's__Faecisoma sp017887425', 's__Evtepia faecigallinarum',
         's__Ruminococcus_D sp944388405', 's__CAG-273 sp944388985'],
        ['s__Limosilactobacillus excrementigallinarum', 's__CALVVX01 sp944368815', 's__Choladousia sp944382085',
         's__Mediterraneibacter sp944375765', 's__Egerieicola faecale', 's__CALWZU01 sp944386095'],
        ['s__Limosilactobacillus ingluviei', 's__Limosilactobacillus sp012843675',
         's__Streptococcus alactolyticus',
         's__UMGS1623 sp934647945', 's__Pseudoflavonifractor_A sp944386885',
         's__Faecalibacterium faecigallinarum'],
        ['s__Limosilactobacillus sp902834055', 's__Tyzzerella sp944383305', 's__Mediterraneibacter pullicola',
         's__Agathobaculum sp900291975', 's__Butyricicoccus sp900604335'],
        ['s__Streptococcus pluranimalium', 's__Blautia_A excrementipullorum',
         's__Mediterraneibacter surreyensis',
         's__Pseudoflavonifractor_A merdipullorum', 's__JAGHEK01 sp017889265'],
        ['s__CAG-582 sp944358235', 's__Coproplasma sp944354125', 's__UBA737 sp944376655',
         's__CALWZA01 sp944385905',
         's__CAG-273 sp944393025', 's__UMGS1663 sp944386315'],
        ['s__CALVQX01 sp944358405', 's__Massilistercora sp902406105', 's__Mediterraneibacter stercoripullorum',
         's__CAG-269 sp944387495', 's__UMGS1994 sp944386155'],
        ['s__CALVRE01 sp944358455', 's__Flavonifractor sp944387215', 's__Pelethomonas sp017887695',
         's__Pelethomonas sp944387775', 's__UBA1405 sp002305685'],
        ['s__CALVUN01 sp944358875', 's__Onthousia sp944333305', 's__CALWDW01 sp944376795',
         's__Dwaynesavagella gallinarum', 's__Mediterraneibacter sp900541505',
         's__Mediterraneibacter sp944376685'],
        ['s__CALVVX01 sp944351765', 's__CALVVX01 sp944371525', 's__CAG-465 sp944388565',
         's__CAG-269 sp944390615',
         's__CAG-269 sp944393125'],
        ['s__CALVVX01 sp944358825', 's__Roseburia sp944380515', 's__Butyricicoccus sp017886875',
         's__Flavonifractor merdavium', 's__CAG-269 sp944390625'],
        ['s__CALVXC01 sp944368805', 's__Onthocola_B sp944363805', 's__CAJJPW01 sp905193725',
         's__Negativibacillus sp944388365', 's__Egerieisoma faecipullorum'],
        ['s__Caccenecus avistercoris', 's__Onthocola_B sp900546715', 's__Scatosoma pullistercoris',
         's__Caccopulliclostridium sp944350095', 's__Enterenecus stercoripullorum'],
        ['s__Caccenecus sp017888105', 's__UBA10677 sp900543755', 's__Intestinimonas sp944385655',
         's__Scatomorpha intestinigallinarum', 's__Pygmaiobacter sp944386485'],
        ['s__Caccenecus sp900758895', 's__Alloclostridium sp944380395', 's__Avimonas intestinalis',
         's__CAJFPI01 sp944386965', 's__CAG-269 sp944393365'],
        ['s__Caccenecus sp944358125', 's__Guopingia tenuis', 's__Merdivicinus excrementipullorum',
         's__CAG-273 sp904378095', 's__JAAWPK01 sp944388635'],
        ['s__Caccenecus sp944358135', 's__Mediterraneibacter merdavium', 's__Agathobaculum merdigallinarum',
         's__Flavonifractor intestinigallinarum', 's__Fournierella sp002159185'],
        ['s__Caccenecus sp944358145', 's__Mediterraneibacter sp944377775', 's__CAG-269 sp944386205',
         's__CAG-269 sp944391785', 's__Merdicola sp001915925'],
        ['s__Coprosoma sp944358495', 's__Ventrenecus sp944350285', 's__Heritagella sp905200265',
         's__CAG-448 sp944381085', 's__CALWZE01 sp944385925'],
        ['s__Faecenecus gallistercoris', 's__Mediterraneibacter pullistercoris', 's__Acutalibacter pullicola',
         's__CAG-273 sp944392105', 's__Phocaeicola coprophilus'],
        ['s__Faecimonas intestinavium', 's__Lachnoclostridium_B faecipullorum',
         's__Mediterraneibacter sp944376695',
         's__Mediterraneibacter stercoravium', 's__Ruthenibacterium merdavium'],
        ['s__Faecimonas sp017886705', 's__RGIG4074 sp944376455', 's__Lachnoclostridium_B monacensis',
         's__Avimonas merdigallinarum', 's__Gallacutalibacter pullicola',
         's__Lentihominibacter excrementipullorum'],
        ['s__Faecimonas sp944332295', 's__Onthousia faecipullorum', 's__Onthousia sp944363705',
         's__Gallimonas intestinavium', 's__QAKW01 sp944387895'],
        ['s__Faecimonas sp944333345', 's__Onthousia sp944363685', 's__Ventricola gallistercoris',
         's__Fournierella merdipullorum', 's__Fournierella pullicola'],
        ['s__Faecimonas sp944358705', 's__Gallimonas sp944367185', 's__Merdisoma sp944375885',
         's__CAG-269 sp944388685',
         's__UMGS1663 sp944386655'],
        ['s__Faecimonas sp944358945', 's__RGIG3091 sp944372315', 's__Eubacterium_I avistercoris',
         's__Gemmiger formicilis_A', 's__CAG-269 sp944386685', 's__CAG-793 sp944392425'],
        ['s__Faecimonas sp944359885', 's__Alloclostridium sp944381275', 's__Massilistercora timonensis',
         's__Limivicinus faecipullorum', 's__CAG-465 sp944383035'],
        ['s__MGBC162581 sp944332535', 's__Onthousia sp944331915', 's__Onthousia sp944363695',
         's__Emergencia sp944388465', 's__CAG-269 sp944386715'],
        ['s__Onthocola_B sp944331835', 's__UMGS2016 sp944355255', 's__UBA1685 sp944366945',
         's__CALWRB01 sp944383855',
         's__RGIG3155 sp934427095'],
        ['s__Onthocola_B sp944332715', 's__Onthousia sp944363755', 's__Anaerotignum lactatifermentans',
         's__Caccousia avicola', 's__Heteroscilispira sp944385595', 's__UMGS1663 sp944386335'],
        ['s__Onthocola_B sp944363835', 's__Caccovivens sp930979925', 's__Gemmiger sp944388175',
         's__CAG-269 sp944387545', 's__RGIG8482 sp904381285'],
        ['s__Onthocola_B stercoravium', 's__Caccosoma sp900762575', 's__Faeciplasma pullistercoris',
         's__UMGS1781 sp944390405', 's__Phocaeicola caecigallinarum_A'],
        ['s__Onthousia faecavium', 's__Hungatella_B pullicola', 's__CAG-269 sp944386165',
         's__CAG-273 sp930990645',
         's__CALXJL01 sp944388615', 's__QAKL01 sp944391285'],
        ['s__Onthousia sp944331955', 's__Ventrenecus sp944371545', 's__UMGS1264 sp944380875',
         's__Faecivivens sp944388825', 's__CAG-273 sp904420285', 's__CAG-793 sp944393305',
         's__Rikenella faecigallinarum'],
        ['s__Onthousia sp944351375', 's__RGIG4074 sp017886575', 's__Scatosoma pullicola',
         's__Neoanaerotignum_A sp944377425', 's__Anaerostipes avistercoris'],
        ['s__Onthousia sp944358355', 's__Acetatifactor stercoripullorum', 's__Agathobaculum pullicola',
         's__Dysosmobacter sp018228705', 's__Intestinimonas sp944387725', 's__Egerieisoma sp900543695'],
        ['s__Onthousia sp944359735', 's__CALWPT01 sp944383495', 's__Agathobaculum sp944384765',
         's__Enterenecus sp944385485', 's__Barnesiella viscericola'],
        ['s__Onthousia sp944363735', 's__Coproplasma avicola', 's__Clostridium_Q sp944381615',
         's__Negativibacillus massiliensis', 's__CAG-273 sp944393505'],
        ['s__Onthousia sp944373065', 's__RUG12867 sp944364705', 's__Coproplasma stercoripullorum',
         's__Faecimorpha sp944376225', 's__CAG-269 sp944391795', 's__CAKNOI01 sp930990125'],
        ['s__Pelethosoma merdigallinarum', 's__Avoscillospira avicola', 's__Avoscillospira stercorigallinarum',
         's__Scatomorpha gallistercoris', 's__Ruthenibacterium sp944386555'],
        ['s__Pelethosoma sp944332155', 's__Borkfalkia faecavium', 's__Gallimonas sp900548845',
         's__Scatosoma sp944375795', 's__Howiella intestinavium', 's__CAG-269 sp930989765',
         's__CAG-269 sp944388775'],
        ['s__Pelethosoma sp944363775', 's__Gallimonas gallistercoris', 's__Enterenecus sp905210385',
         's__Ruminococcus_D sp900752625', 's__JAAWPK01 sp944386135'],
        ['s__RUG591 sp944350445', 's__Fimimorpha sp904395845', 's__Scybalomonas excrementigallinarum',
         's__Fournierella pullistercoris', 's__Fusobacterium_A sp900549465'],
        ['s__Scybalousia sp900543675', 's__Faecousia excrementipullorum', 's__CAG-269 sp944388715',
         's__CAG-273 sp944392435', 's__Scatovivens faecipullorum'],
        ['s__Scybalousia sp944359075', 's__QAKD01 sp003343965', 's__CAG-269 sp944392635',
         's__CAG-273 sp944392505',
         's__CAG-793 sp930980855'],
        ['s__UMGS2016 sp944332375', 's__Gallimonas sp944362555', 's__Limadaptatus stercorigallinarum',
         's__Caccopulliclostridium sp944372325', 's__CAKRRK01 sp934395135', 's__HGM12669 sp900761935'],
        ['s__Ventrenecus avicola', 's__Caccovivens sp904397185', 's__Avoscillospira stercoripullorum',
         's__Faecalibacterium gallinarum', 's__Fournierella excrementavium', 's__CAG-269 sp944388705'],
        ['s__Ventrenecus sp944350145', 's__Scatosoma sp904419075', 's__HGM11808 sp944380405',
         's__Caccomorpha excrementavium', 's__Timburyella sp900554165',
         's__Pseudoflavonifractor_A intestinipullorum',
         's__Faecivivens sp944387515'],
        ['s__Ventrenecus sp944351315', 's__Blautia_A sp944380045', 's__Fimenecus sp944384995',
         's__CALXIC01 sp944388265', 's__Gemmiger sp944382785', 's__Gemmiger_A avium', 's__CAG-269 sp944388795'],
        ['s__Ventrenecus sp944355355', 's__Borkfalkia sp904419945', 's__Mediterraneibacter sp944383745',
         's__CAG-273 sp944390395', 's__UMGS1663 sp944388655'],
        ['s__Caccosoma faecigallinarum', 's__QANA01 sp900554725', 's__Protoclostridium sp944372345',
         's__Flemingibacterium merdigallinarum', 's__Scatomorpha stercorigallinarum'],
        ['s__Borkfalkia avicola', 's__Borkfalkia excrementigallinarum', 's__Borkfalkia excrementipullorum',
         's__Borkfalkia sp017886545', 's__Gallimonas merdae'],
        ['s__Borkfalkia avistercoris', 's__Limiplasma pullistercoris', 's__Protoclostridium sp019113265',
         's__Caccalectryoclostridium excrementigallinarum', 's__Mediterraneibacter colneyensis'],
        ['s__Borkfalkia excrementavium', 's__Borkfalkia sp904373255', 's__Borkfalkia stercoripullorum',
         's__Coproplasma stercoravium', 's__Eisenbergiella pullicola'],
        ['s__Borkfalkia faecigallinarum', 's__Borkfalkia sp017886895', 's__Borkfalkia sp944328445',
         's__Coproplasma stercorigallinarum', 's__Heteroclostridium caecigallinarum'],
        ['s__Borkfalkia faecipullorum', 's__Coproplasma excrementipullorum',
         's__Ornithoclostridium sp944380285',
         's__Woodwardibium gallinarum', 's__CALWOS01 sp944383185'],
        ['s__Borkfalkia sp003343765', 's__Eisenbergiella sp904392525', 's__HGM12545 sp900761925',
         's__Avoscillospira_A sp904395905', 's__Gemmiger excrementipullorum'],
        ['s__Borkfalkia sp904374385', 's__Egerieenecus merdigallinarum', 's__Faecivicinus sp944353735',
         's__Butyrivibrio_A sp944382105', 's__HGM14224 sp900761905'],
        ['s__Borkfalkia sp944328405', 's__Gallimonas faecium', 's__Gallimonas sp944367465',
         's__Anaerobutyricum avicola', 's__Intestinimonas stercorigallinarum'],
        ['s__Borkfalkia sp944328905', 's__Mediterraneibacter faecavium', 's__CAJFPI01 sp944385425',
         's__Avimonoglobus intestinipullorum', 's__Escherichia fergusonii'],
        ['s__Borkfalkia sp944342025', 's__UMGS1264 sp904399395', 's__Flavonifractor avistercoris',
         's__Lawsonibacter pullicola', 's__UBA866 sp904384225'],
        ['s__Coproplasma avistercoris', 's__Gallimonas merdigallinarum', 's__Onthocola_A gallistercoris',
         's__Heteroruminococcus faecigallinarum', 's__Cryptoclostridium obscurum'],
        ['s__Coproplasma sp944327465', 's__Gallimonas caecicola', 's__Limadaptatus stercoravium',
         's__HGM11386 sp900761915', 's__UMGS1795 sp900553555'],
        ['s__Coproplasma sp944341075', 's__CAKTXU01 sp934615635', 's__RUG626 sp944386185',
         's__Scatomorpha sp944387825',
         's__CAG-793 sp930986425'],
        ['s__Gallimonas intestinalis', 's__UMGS856 sp900760305', 's__Agathobaculum sp944380945',
         's__Butyricicoccus_A sp944384655', 's__Scatomorpha intestinavium', 's__CAG-269 sp944386755'],
        ['s__Gallimonas intestinigallinarum', 's__Faecousia faecigallinarum',
         's__Faecalibacterium faecipullorum',
         's__Faecalibacterium gallistercoris', 's__Faecalibacterium intestinigallinarum',
         's__Faecivivens stercorigallinarum'],
        ['s__Gallimonas sp017887095', 's__Pullichristensenella avicola', 's__RACS-045 sp944380355',
         's__JAGTTR01 sp944384015', 's__RUG14109 sp944384865', 's__CAG-245 sp944388645'],
        ['s__Gallimonas sp944340905', 's__CAJFPI01 sp944386985', 's__CAG-273 sp944390505',
         's__CAG-273 sp944391825',
         's__Scatovivens sp944393295'],
        ['s__Scatosoma sp900555925', 's__Ventricola sp944363005', 's__CALXGT01 sp944385915',
         's__JAAZZIT01 sp944382845',
         's__CAG-269 sp944388735', 's__Merdicola sp944390295'],
        ['s__Heteroclostridium sp944336125', 's__Acetatifactor sp944384205', 's__CALXEN01 sp944387885',
         's__Fournierella merdigallinarum', 's__CAG-269 sp944388765'],
        ['s__Alectryocaccomicrobium faecavium', 's__UMGS1975 sp900546685', 's__Ventrousia excrementavium',
         's__Alloscillospira gallinarum', 's__CALXCT01 sp944386055'],
        ['s__Faecaligallichristensenella faecipullorum', 's__Catenibacillus faecigallinarum',
         's__Lachnoclostridium_A stercoravium', 's__Merdisoma merdipullorum', 's__Paralachnospira_A sangeri',
         's__Scybalocola faecipullorum', 's__Faecivivens stercoravium'],
        ['s__Faecivicinus avistercoris', 's__Pullichristensenella stercoripullorum', 's__QALW01 sp900552055',
         's__Tabaqchalia intestinavium', 's__Pelethomonas intestinigallinarum'],
        ['s__Limiplasma merdipullorum', 's__Flavonifractor sp944385575', 's__Merdivicinus sp944386445',
         's__Pygmaiobacter sp944388335', 's__UBA866 sp016901855'],
        ['s__Onthenecus intestinigallinarum', 's__Monoglobus merdigallinarum', 's__Enterenecus sp944385465',
         's__Faecousia faecavium', 's__Scatomorpha sp944385765'],
        ['s__Pullichristensenella excrementipullorum', 's__HGM11327 sp900759935', 's__Roslinia sp019419865',
         's__Avispirillum faecium', 's__Lentihominibacter excrementavium'],
        ['s__Pullichristensenella sp904420265', 's__UMGS882 sp003343885', 's__Enterenecus avicola',
         's__Aphodoplasma excrementigallinarum', 's__Mailhella merdigallinarum'],
        ['s__Ventricola intestinavium', 's__CALWPC01 sp944383325', 's__Acutalibacter pullistercoris',
         's__Merdivicinus intestinigallinarum', 's__Bacteroides xylanisolvens'],
        ['s__CALWSW01 sp944384305', 's__Ornithoclostridium excrementipullorum',
         's__Ornithoclostridium faecigallinarum',
         's__Faecousia intestinavium', 's__Scatomorpha merdigallinarum'],
        ['s__RGIG9107 sp019420085', 's__QAKD01 sp944386585', 's__CAG-269 sp944393385', 's__CAG-273 sp944391015',
         's__HGM13862 sp944393575'],
        ['s__Allochristensenella sp019415425', 's__Acutalibacter stercorigallinarum',
         's__Gallacutalibacter_A stercoravium', 's__RUG626 sp944385785', 's__Merdivicinus faecavium'],
        ['s__QAND01 sp003150225', 's__Bariatricus faecipullorum', 's__JAGTTR01 sp944381745',
         's__CALXCQ01 sp944386835',
         's__Anaerotruncus sp944387965'],
        ['s__Caccovivens sp944348085', 's__Avoscillospira_A sp944385365', 's__Enterenecus capillosus_A',
         's__Faeciplasma avium', 's__Fournierella merdavium', 's__CAG-273 sp930991035',
         's__CAG-793 sp944388895'],
        ['s__Spyradocola merdavium', 's__Choladousia intestinipullorum', 's__UBA1417 sp900552925',
         's__Evtepia excrementipullorum', 's__UBA3818 sp904397845'],
        ['s__Alloclostridium intestinigallinarum', 's__Metalachnospira gallinarum',
         's__Acutalibacter sp900755895',
         's__Faecivivens stercoripullorum', 's__Bradyrhizobium sp002831585'],
        ['s__Anaerotignum merdipullorum', 's__Mediterraneibacter sp944381495', 's__CALWKP01 sp944380775',
         's__Faecousia excrementigallinarum', 's__CAG-269 sp904419095'],
        ['s__CALWRB01 sp944381395', 's__CAJFPI01 sp904419145', 's__Avimicrobium caecorum',
         's__Fimisoma avicola',
         's__Fimisoma sp900540145'],
        ['s__CALWSX01 sp944384285', 's__Limousia pullorum', 's__Agathobaculum merdavium',
         's__Pseudobutyricicoccus sp003477405', 's__Fimisoma sp900754795'],
        ['s__Coprocola pullicola', 's__Scatomonas pullistercoris', 's__Acutalibacter sp904419785',
         's__Butyricicoccus pullicaecorum', 's__Avoscillospira_A avistercoris'],
        ['s__Coprocola sp017888185', 's__Lachnoclostridium_A sp944383765', 's__UMGS1071 sp944384835',
         's__Agathobaculum merdipullorum', 's__CAG-269 sp930987745'],
        ['s__Neoanaerotignum_A tabaqchaliae', 's__Mediterraneibacter intestinigallinarum',
         's__Gemmiger avicola',
         's__Gemmiger stercorigallinarum', 's__Negativibacillus faecipullorum'],
        ['s__Neoanaerotignum_B sp944378105', 's__Enterocloster sp944382045', 's__Enterocloster sp944384065',
         's__Dysosmobacter excrementigallinarum', 's__CAG-269 sp944386675'],
        ['s__Faecimorpha stercoravium', 's__Lachnospira sp944381165', 's__Mediterraneibacter sp904418845',
         's__UMGS1071 sp904397205', 's__Flavonifractor sp002159455', 's__Ruthenibacterium avium'],
        ['s__Gallispira edinburgensis', 's__Mediterraneibacter sp019420405', 's__Fimenecus sp900545625',
         's__Dysosmobacter sp944385405', 's__Ornithomonoglobus merdipullorum'],
        ['s__Acetatifactor sp944383825', 's__Eisenbergiella stercorigallinarum',
         's__Mediterraneibacter merdipullinarum', 's__UMGS1384 sp900551265', 's__CAG-269 sp944387425'],
        ['s__Anaerostipes butyraticus', 's__Sellimonas caecigallum', 's__Ventrimonas merdavium',
         's__Lawsonibacter sp944387755', 's__Gemmiger sp944382805', 's__CAG-273 sp944393165',
         's__Klebsiella pneumoniae', 's__Proteus mirabilis'],
        ['s__Anaerostipes excrementavium', 's__Sellimonas intestinalis', 's__CAJFTX01 sp904420075',
         's__Metaruminococcus caecorum', 's__Escherichia coli'],
        ['s__Blautia merdavium', 's__Mediterraneibacter norwichensis', 's__Scatomonas merdigallinarum',
         's__Pseudoflavonifractor capillosus', 's__Avimicrobium faecavium'],
        ['s__Blautia merdigallinarum', 's__Blautia_A faecavium', 's__Eisenbergiella intestinigallinarum',
         's__Mediterraneibacter merdigallinarum', 's__UBA644 sp014872655'],
        ['s__Blautia ornithocaccae', 's__Blautia pullistercoris', 's__Caccovicinus merdipullorum',
         's__Fimimorpha sp904420225', 's__JAGZHZ01 sp944376425', 's__Mediterraneibacter catenae',
         's__Eubacterium_R sp017886765'],
        ['s__Blautia pullicola', 's__Choladousia intestinigallinarum', 's__Mediterraneibacter intestinavium',
         's__Pseudobutyricicoccus lothianensis', 's__Dysosmobacter excrementavium'],
        ['s__Blautia sp944380235', 's__Blautia_A excrementigallinarum', 's__Fimimorpha faecalis',
         's__RGIG7193 sp944383835', 's__QAMM01 sp900762715'],
        ['s__Blautia stercorigallinarum', 's__Lachnoclostridium_A stercoripullorum', 's__UBA3402 sp944380605',
         's__Acutalibacter sp905215055', 's__Acutalibacter stercoravium', 's__Flavonifractor avicola',
         's__Fumia sp904396495'],
        ['s__Blautia_A intestinigallinarum', 's__Choladocola avistercoris', 's__Copromonas avistercoris',
         's__Enterocloster excrementipullorum', 's__UMGS1370 sp904395885', 's__Acutalibacter ornithocaccae',
         's__Pseudoscilispira faecavium', 's__Bilophila wadsworthia'],
        ['s__CAG-303 sp944384155', 's__Dysosmobacter sp944387055', 's__Onthomonas avicola',
         's__Clostridioides difficile', 's__Acinetobacter wanghuae'],
        ['s__Choladocola sp944381625', 's__Mediterraneibacter cottocaccae', 's__Scatomonas hejianensis',
         's__CALXGH01 sp944387845', 's__CAG-273 sp944389655'],
        ['s__Choladousia intestinavium', 's__CAJFPI01 sp904398675', 's__CAJFPI01 sp904420435',
         's__Pelethomonas sp900549475', 's__Ruthenibacterium sp944388395'],
        ['s__Egerieimonas_A faecigallinarum', 's__Merdisoma faecalis', 's__Paralachnospira avium',
         's__Agathobaculum pullistercoris', 's__Anaerofilum excrementigallinarum'],
        ['s__Eisenbergiella sp944380095', 's__Merdisoma sp944383645', 's__Lawsonibacter sp904420465',
         's__Anaerotruncus excrementipullorum', 's__Ruthenibacterium sp944386565'],
        ['s__Eubacterium_G sp904420085', 's__Mediterraneibacter excrementavium',
         's__Mediterraneibacter quadrami',
         's__Paralachnospira sp944375845', 's__Enterenecus faecium', 's__CAG-269 sp904387305'],
        ['s__Fimousia stercorigallinarum', 's__Mediterraneibacter intestinavium',
         's__Eubacterium_R faecigallinarum',
         's__Eubacterium_R faecipullorum', 's__Fimenecus excrementavium', 's__Flavonifractor sp944385585'],
        ['s__Fusicatenibacter sp017887445', 's__Dysosmobacter sp944385455', 's__CAG-269 sp904384245',
         's__CAG-269 sp944388695', 's__Prevotella massiliensis'],
        ['s__Lachnoclostridium_A avicola', 's__Limivivens merdigallinarum',
         's__Mediterraneibacter glycyrrhizinilyticus_A', 's__Mediterraneibacter vanvlietii',
         's__Dysosmobacter faecalis', 's__Brachyspira innocens'],
        ['s__Lachnoclostridium_B massiliensis_A', 's__Mediterranea ndongoniae', 's__Mediterranea pullorum',
         's__Phocaeicola sp002161765', 's__Barnesiella merdipullorum', 's__Merdimorpha stercoravium'],
        ['s__Lachnoclostridium_B sp000765215', 's__Mediterranea sp900553815', 's__Phocaeicola intestinalis',
         's__Caccocola faecigallinarum', 's__Caccocola sp002159945'],
        ['s__Mediterraneibacter avicola', 's__Mediterraneibacter caccavium',
         's__Mediterraneibacter stercorigallinarum',
         's__CAJFUH01 sp904420155', 's__Fimenecus stercoravium'],
        ['s__Mediterraneibacter sp900120155', 's__Paralachnospira caecorum', 's__Pseudolachnospira avium',
         's__Pseudolachnospira sp944376945', 's__Emergencia sp904420065'],
        ['s__Pullilachnospira stercoravium', 's__CAJFPI01 sp944386995', 's__Gemmiger faecavium',
         's__Gemmiger stercoravium', 's__Massiliimalia sp944382885'],
        ['s__Acutalibacter sp904391645', 's__SIG471 sp905199135', 's__Intestinimonas stercoravium',
         's__Metaruminococcus sp944386475', 's__Ruthenibacterium merdigallinarum'],
        ['s__Caccousia sp900752115', 's__Eubacterium_R sp900539425', 's__Avoscillospira sp944386905',
         's__Galloscillospira_A stercoripullorum', 's__Pseudoflavonifractor_A gallinarum',
         's__CALXEM01 sp944387335'],
        ['s__Heritagella intestinalis', 's__Lawsonibacter sp019424865', 's__Lawsonibacter sp900545895',
         's__Aristotella avistercoris', 's__Schneewindia gallinarum'],
        ['s__Solibaculum sp904397895', 's__Bacteroides fragilis', 's__Phocaeicola dorei',
         's__Odoribacter splanchnicus',
         's__Alistipes onderdonkii', 's__Parabacteroides distasonis'],
        ['s__UMGS1071 sp900541905', 's__Ornithomonoglobus sp904420525', 's__CAG-266 sp000436095',
         's__Megasphaera stantonii', 's__Desulfovibrio sp900556755'],
        ['s__UMGS1623 sp900553525', 's__CAJFPI01 sp904420145', 's__Dysosmobacter sp904393855',
         's__Scatomorpha sp900759385', 's__Angelakisella sp904420255'],
        ['s__Agathobaculum sp900557315', 's__Dysosmobacter sp944382995', 's__HGM12957 sp900760695',
         's__Gemmiger formicilis_B', 's__Merdicola sp900553015'],
        ['s__Butyricicoccus avistercoris', 's__Woodwardibium sp900754535', 's__Lawsonibacter sp002161175',
         's__Limivicinus sp944387735', 's__Scatomorpha merdavium'],
        ['s__Butyricicoccus sp904420185', 's__Butyricicoccus sp944381005', 's__CALXDZ01 sp944387205',
         's__Pygmaiobacter gallistercoris', 's__CAG-273 sp944392085'],
        ['s__CALWWS01 sp944385305', 's__Lawsonibacter sp944385075', 's__Lawsonibacter sp944385645',
         's__Pseudoflavonifractor sp904419835', 's__Scatomorpha pullicola'],
        ['s__Dysosmobacter pullicola', 's__Faecousia gallistercoris', 's__Galloscillospira_A excrementavium',
         's__CALYAO01 sp944393605', 's__HGM11507 sp900761005'],
        ['s__Bacteroides uniformis', 's__Mediterranea massiliensis', 's__Phocaeicola barnesiae',
         's__Phocaeicola coprocola', 's__Phocaeicola sp900551065', 's__Phocaeicola_A sp900291465'],
        ['s__Paraprevotella stercoravium', 's__Phocaeicola faecipullorum', 's__Prevotella lascolaii',
         's__Parabacteroides sp002159645', 's__Desulfovibrio faecigallinarum'],
        ['s__Phocaeicola sp900546355', 's__Phocaeicola_A sp003489705', 's__Desulfovibrio sp944327285',
         's__Aphodousia secunda_A', 's__Duodenibacillus intestinavium', 's__Succinatimonas hippei']
    ]

    df_0_4 = clusters_to_df(cluster_data_0_4)
    df_0_5 = clusters_to_df(cluster_data_0_5)
    df_0_6 = clusters_to_df(cluster_data_0_6)
    # Also prepare explore versions (using same data)
    df_0_4_explore = df_0_4.copy()
    df_0_5_explore = df_0_5.copy()
    df_0_6_explore = df_0_6.copy()

    try:
        fig_0_4 = px.sunburst(df_0_4, path=["Cluster", "Species"], values="Value", title="Threshold 0.4")
        fig_0_4.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_4 = pio.to_html(fig_0_4, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_04")
    except Exception as e:
        sunburst_html_0_4 = ""
    try:
        fig_0_5 = px.sunburst(df_0_5, path=["Cluster", "Species"], values="Value", title="Threshold 0.5")
        fig_0_5.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_5 = pio.to_html(fig_0_5, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_03")
    except Exception as e:
        sunburst_html_0_5 = ""
    try:
        fig_0_6 = px.sunburst(df_0_6, path=["Cluster", "Species"], values="Value", title="Threshold 0.6")
        fig_0_6.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_6 = pio.to_html(fig_0_6, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_02")
    except Exception as e:
        sunburst_html_0_6 = ""
    try:
        explore_fig_0_5 = px.sunburst(df_0_5_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.5")
        explore_fig_0_5.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_5 = pio.to_html(explore_fig_0_5, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_03")
    except Exception as e:
        explore_sunburst_html_0_5 = ""
    try:
        explore_fig_0_4 = px.sunburst(df_0_4_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.4")
        explore_fig_0_4.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_4 = pio.to_html(explore_fig_0_4, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_04")
    except Exception as e:
        explore_sunburst_html_0_4 = ""
    try:
        explore_fig_0_6 = px.sunburst(df_0_6_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.6")
        explore_fig_0_6.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_6 = pio.to_html(explore_fig_0_6, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_02")
    except Exception as e:
        explore_sunburst_html_0_6 = ""

    # ileum suggestions from DB to do fot otu
    # otu_list = OtuCorrelation.objects.values_list('var2', flat=True).distinct().order_by('var2')
    # Check from file csv the ileum
    # otu_list = []  # default if anything goes wrong
    try:
        otu_csv_path = os.path.join(settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "res_massive_lr_ross",
                                    "otu_to_otu.csv")
        df_otu = pd.read_csv(otu_csv_path, )
        otu_list = df_otu.iloc[:, 0].dropna().unique().tolist()
    except Exception as e:
        otu_list = []
        print(f"Error loading otu_to_muscle.csv: {e}")

    return render(request, f"{host_type}/bacterien.html", {
        "host_type": host_type.title(),
        "data_type": "Otu",
        "description": "Top 200 displayed only. Gene info from Ensembl REST.",
        # "tissue_types": list(tissue_files_muscle.keys()),
        "sunburst_html_0_4": sunburst_html_0_4,
        "sunburst_html_0_5": sunburst_html_0_5,
        "sunburst_html_0_6": sunburst_html_0_6,
        "explore_sunburst_html_0_4": explore_sunburst_html_0_4,
        "explore_sunburst_html_0_5": explore_sunburst_html_0_5,
        "explore_sunburst_html_0_6": explore_sunburst_html_0_6,
        "otu_list": otu_list,
    })



####################################


####################################
# Version of databse pg functionnal
#####################################
@csrf_exempt
def process_data_functionnal2(request, host_type='isabrownv2'):
    """
    1) Creates three sunbursts (thresholds 0.4, 0.3 & 0.2).

    """
    import os, pandas as pd, plotly.express as px, plotly.io as pio
    from django.http import JsonResponse
    from django.shortcuts import render
    from django.conf import settings
    from Avapp.models import FunctionnalCorrelation
    import numpy as np

    # --- AJAX Handling ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # (A) Load tissue: list distinct var2 (variables)
        if 'load_tissue' in request.GET:
            tissue = request.GET.get('tissue')
            vars_qs = FunctionnalCorrelation.objects.filter(
                Q(from_tissue=tissue) | Q(to_tissue=tissue)
            ).values_list('var2', flat=True).distinct().order_by('var2')
            return J({'variables': list(vars_qs)})

        # (D) Cluster Lookup branch remains unchanged
        if  "cluster_lookup" in request.GET:
            selected_bacteria = request.GET.get("bacteria", "").strip()
            if not selected_bacteria:
                return JsonResponse({"found": False})

            found = False
            cluster_found = None
            threshold = None
            cluster_data_0_6 = [
                ['menaquinol-13 biosynthesis', 'menaquinol-12 biosynthesis', 'demethylmenaquinol-8 biosynthesis I',
                 'demethylmenaquinol-9 biosynthesis', 'demethylmenaquinol-6 biosynthesis I',
                 'menaquinol-11 biosynthesis', 'demethylmenaquinol-4 biosynthesis', 'menaquinol-10 biosynthesis',
                 '&beta;-alanine biosynthesis II', 'menaquinol-7 biosynthesis', 'assimilatory sulfate reduction II',
                 'assimilatory sulfate reduction III'],
                ['Bifidobacterium shunt', 'L-serine biosynthesis I', 'protein Pupylation and dePupylation',
                 'Bifidobacterium shunt II', 'polyphosphate metabolism', 'isoniazid activation',
                 'NAD phosphorylation and dephosphorylation',
                 'felinine and 3-methyl-3-sulfanylbutan-1-ol biosynthesis'],
                ['fructose 2,6-bisphosphate biosynthesis', 'formate oxidation to CO2', 'glycerol degradation I',
                 '3-dehydroquinate biosynthesis II (archaea)', 'nitrate reduction V (assimilatory)',
                 'pyrimidine deoxyribonucleotide phosphorylation', 'L-alanine biosynthesis I',
                 'D-myo-inositol (1,4,5)-trisphosphate biosynthesis'],
                ['CDP-diacylglycerol biosynthesis III', 'tRNA splicing I', 'isoprene biosynthesis II (engineered)',
                 'adenine and adenosine salvage II', 'nitric oxide biosynthesis I (plants)',
                 'mevalonate pathway I (eukaryotes and bacteria)', 'acyl carrier protein activation',
                 'mevalonate pathway IV (archaea)'],
                ['2-aminoethylphosphonate biosynthesis', 'nitrate reduction IV (dissimilatory)',
                 'GDP-6-deoxy-D-altro-heptose biosynthesis', 'Oxidase test', 'hexaprenyl diphosphate biosynthesis',
                 'D-sorbitol degradation I', 'glycerol-3-phosphate shuttle'],
                ['trehalose degradation VI (periplasmic)', 'Extracellular starch(27n) degradation',
                 '(S)-lactate fermentation to propanoate', 'L-threonine degradation V',
                 'trehalose degradation II (cytosolic)', 'C4 photosynthetic carbon assimilation cycle, NAD-ME type',
                 '2-aminoethylphosphonate degradation II'],
                ['putrescine degradation V', "S-methyl-5'-thioadenosine degradation III",
                 '&beta;-alanine degradation I', 'Electron bifurcating LDH/Etf complex', 'acrylonitrile degradation II',
                 'indole-3-acetate biosynthesis V (bacteria and fungi)'],
                ['trehalose degradation V', 'acetate and ATP formation from acetyl-CoA II',
                 '8-amino-7-oxononanoate biosynthesis III', 'trehalose degradation IV',
                 'UDP-N-acetyl-&alpha;-D-mannosaminouronate biosynthesis',
                 'L-tryptophan degradation II (via pyruvate)'],
                ['phytol degradation', 'lactose and galactose degradation I',
                 'poly(glycerol phosphate) wall teichoic acid biosynthesis', 'NADH:menaquinone6 oxidoreductase',
                 '2-carboxy-1,4-naphthoquinol biosynthesis', 'terminal olefins biosynthesis I'],
                ['L-phenylalanine degradation III', 'trehalose degradation III', 'phosphatidylcholine biosynthesis I',
                 'acetaldehyde biosynthesis II', 'maltose degradation', 'oxalate degradation II'],
                ['UDP-N-acetylmuramoyl-pentapeptide biosynthesis II (lysine-containing)',
                 'UDP-N-acetylmuramoyl-pentapeptide biosynthesis I (meso-diaminopimelate containing)',
                 'arginine deiminase test', 'peptidoglycan biosynthesis I (meso-diaminopimelate containing)',
                 'flavin salvage', 'peptidoglycan cross-bridge biosynthesis II (E. faecium)'],
                ['cyclobis-(1&rarr;6)-&alpha;-nigerosyl degradation',
                 'ABH and Lewis epitopes biosynthesis from type 2 precursor disaccharide',
                 'biosynthesis of Lewis epitopes (H. pylori)',
                 'ABH and Lewis epitopes biosynthesis from type 1 precursor disaccharide', 'glycolipid desaturation'],
                ['oleate biosynthesis IV (anaerobic)', 'thiamine diphosphate biosynthesis I (E. coli)',
                 'octaprenyl diphosphate biosynthesis', 'thiamine diphosphate biosynthesis II (Bacillus)',
                 'nonaprenyl diphosphate biosynthesis I'],
                ['flavonol acylglucoside biosynthesis II - isorhamnetin derivatives',
                 'flavonol acylglucoside biosynthesis I - kaempferol derivatives', 'phytochromobilin biosynthesis',
                 'flavonol acylglucoside biosynthesis III - quercetin derivatives',
                 'kaempferide triglycoside biosynthesis'],
                ['trigonelline biosynthesis', 'polymyxin A biosynthesis', 'glycerophosphodiester degradation',
                 'putrescine degradation III', 'serotonin degradation'],
                ['tetradecanoate biosynthesis (mitochondria)', 'anteiso-branched-chain fatty acid biosynthesis',
                 'even iso-branched-chain fatty acid biosynthesis',
                 'octanoyl-[acyl-carrier protein] biosynthesis (mitochondria, yeast)',
                 'odd iso-branched-chain fatty acid biosynthesis'],
                ['D-erythronate degradation I', 'phosphatidylserine and phosphatidylethanolamine biosynthesis I',
                 'thiazole component of thiamine diphosphate biosynthesis I', 'adenosine nucleotides degradation III',
                 'L-tryptophan degradation IV (via indole-3-lactate)'],
                ['triclosan resistance', 'CMP phosphorylation', 'ppGpp metabolism',
                 'guanosine ribonucleotides de novo biosynthesis', 'UTP and CTP de novo biosynthesis'],
                ['archaeosine biosynthesis I', 'L-rhamnose degradation II',
                 'ubiquinol-8 biosynthesis (early decarboxylation)', 'L-rhamnose degradation III',
                 'poly-hydroxy fatty acids biosynthesis'],
                ['Bile acid 7alpha-dehydroxylation', 'Inulin degradation(11xFru,1xGlc) (extracellular)',
                 'iso-bile acids biosynthesis (NADH or NADPH dependent)',
                 'L-Tyrosine degradation to 4-hydroxyphenylacetate via tyramine', 'Ljungdahl-Wood pathway (gapseq)'],
                ['folate transformations III (E. coli)', 'D-galactose detoxification', 'L-histidine degradation VI',
                 'L-histidine degradation III', 'L-alanine degradation II (to D-lactate)'],
                ['purine deoxyribonucleosides degradation I', '4-deoxy-L-threo-hex-4-enopyranuronate degradation',
                 'L-homocysteine biosynthesis', 'adenine and adenosine salvage III',
                 'purine deoxyribonucleosides degradation II']]

            cluster_data_0_5 = [
                ['menaquinol-13 biosynthesis', 'menaquinol-12 biosynthesis', 'demethylmenaquinol-8 biosynthesis I',
                 'demethylmenaquinol-9 biosynthesis', 'demethylmenaquinol-6 biosynthesis I',
                 'menaquinol-11 biosynthesis', 'demethylmenaquinol-4 biosynthesis', 'menaquinol-10 biosynthesis',
                 '&beta;-alanine biosynthesis II', 'menaquinol-7 biosynthesis', 'assimilatory sulfate reduction II',
                 'assimilatory sulfate reduction III'],
                ['CDP-diacylglycerol biosynthesis III', 'tRNA splicing I', 'isoprene biosynthesis II (engineered)',
                 'vancomycin resistance I', 'adenine and adenosine salvage II', 'nitric oxide biosynthesis I (plants)',
                 'mevalonate pathway I (eukaryotes and bacteria)', 'L-lysine biosynthesis II', 'citrate degradation',
                 'acyl carrier protein activation', 'mevalonate pathway IV (archaea)'],
                ['D-erythronate degradation I', 'octaprenyl diphosphate biosynthesis',
                 'thiamine diphosphate biosynthesis II (Bacillus)',
                 'L-tryptophan degradation IV (via indole-3-lactate)',
                 'phosphatidylserine and phosphatidylethanolamine biosynthesis I', 'oleate biosynthesis IV (anaerobic)',
                 'thiazole component of thiamine diphosphate biosynthesis I',
                 'thiamine diphosphate biosynthesis I (E. coli)', 'adenosine nucleotides degradation III',
                 'nonaprenyl diphosphate biosynthesis I'],
                ['hydrogen to dimethyl sulfoxide electron transfer', 'carbon tetrachloride degradation II',
                 'L-isoleucine biosynthesis III', 'CDP-D-arabitol biosynthesis',
                 'L-arginine degradation XIII (reductive Stickland reaction)', 'acetylene degradation (anaerobic)',
                 'reductive acetyl coenzyme A pathway I (homoacetogenic bacteria)',
                 'L-asparagine degradation III (mammalian)', 'methanogenesis from acetate',
                 '&beta;-1,4-D-mannosyl-N-acetyl-D-glucosamine degradation'],
                ['heme b biosynthesis IV (Gram-positive bacteria)',
                 'benzimidazolyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP',
                 '2-carboxy-1,4-naphthoquinol biosynthesis', 'NADH:menaquinone6 oxidoreductase',
                 'terminal olefins biosynthesis I', 'lactose and galactose degradation I', 'cinnamoyl-CoA biosynthesis',
                 'L-Fucose degradation (non-phosphorylating)',
                 'poly(glycerol phosphate) wall teichoic acid biosynthesis', 'phytol degradation'],
                ['fructose 2,6-bisphosphate biosynthesis', 'formate oxidation to CO2', 'glycerol degradation I',
                 '3-dehydroquinate biosynthesis II (archaea)', 'nitrate reduction V (assimilatory)',
                 'pyrimidine deoxyribonucleotide phosphorylation', 'ulvan degradation',
                 'phosphatidylinositol biosynthesis I (bacteria)', 'L-alanine biosynthesis I',
                 'D-myo-inositol (1,4,5)-trisphosphate biosynthesis'],
                ['L-arginine degradation IV (arginine decarboxylase/agmatine deiminase pathway)',
                 'Agmatine extracellular biosynthesis', 'NADH to cytochrome bd oxidase electron transfer I',
                 'adenine and adenosine salvage I', 'NADH to cytochrome bo oxidase electron transfer II',
                 'NADH to cytochrome bd oxidase electron transfer II', 'sulfate activation for sulfonation',
                 'folate transformations II (plants)', 'NADH to cytochrome bo oxidase electron transfer I',
                 'putrescine biosynthesis II'],
                ['4-hydroxyphenylacetate degradation', 'anthranilate degradation III (anaerobic)',
                 'phenylethylamine degradation I', '1,4-dichlorobenzene degradation', '4-hydroxymandelate degradation',
                 'orthanilate degradation', '1,2-dichloroethane degradation', '4-toluenecarboxylate degradation',
                 '2-oxobutanoate degradation II'], ['trehalose biosynthesis III', 'toluene degradation to benzoate',
                                                    'diacylglycerol and triacylglycerol biosynthesis',
                                                    'toluene degradation to 2-hydroxypentadienoate (via 4-methylcatechol)',
                                                    'toluene degradation to 4-methylphenol',
                                                    'toluene degradation to 2-hydroxypentadienoate I (via o-cresol)',
                                                    'trehalose biosynthesis I',
                                                    'toluene degradation to 2-hydroxypentadienoate (via toluene-cis-diol)'],
                ['Bifidobacterium shunt', 'L-serine biosynthesis I', 'protein Pupylation and dePupylation',
                 'Bifidobacterium shunt II', 'polyphosphate metabolism', 'isoniazid activation',
                 'NAD phosphorylation and dephosphorylation',
                 'felinine and 3-methyl-3-sulfanylbutan-1-ol biosynthesis'],
                ['roseoflavin biosynthesis', 'nitric oxide biosynthesis III (bacteria)',
                 'coenzyme B/coenzyme M regeneration III (coenzyme F420-dependent)',
                 'coenzyme B/coenzyme M regeneration II (ferredoxin-dependent)', 'jasmonoyl-L-isoleucine inactivation',
                 'D-altritol and galactitol degradation', 'N-hydroxy-L-pipecolate biosynthesis',
                 'coenzyme B/coenzyme M regeneration IV (H2-dependent)'],
                ['bacteriochlorophyll e biosynthesis', '3-hydroxy-4-methyl-anthranilate biosynthesis II',
                 'bacteriochlorophyll c biosynthesis', 'phosalacine biosynthesis',
                 'NAD salvage pathway II (PNC IV cycle)', 'L-leucine degradation IV (reductive Stickland reaction)',
                 'chlorophyll a biosynthesis III', 'bacteriochlorophyll b biosynthesis'],
                ['N-cyclopropylmelamine degradation', 'lactucaxanthin biosynthesis',
                 'capsanthin and capsorubin biosynthesis', 'coumarin biosynthesis (via 2-coumarate)',
                 'factor 430 biosynthesis', 'artemisinin and arteannuin B biosynthesis',
                 'factor 420 biosynthesis II (mycobacteria)', 'lactate biosynthesis (archaea)'],
                ['L-phenylalanine degradation III', 'trehalose degradation III', 'phosphatidylcholine biosynthesis I',
                 "inosine-5'-phosphate biosynthesis I", 'acetaldehyde biosynthesis II', 'maltose degradation',
                 'NAD phosphorylation and transhydrogenation', 'oxalate degradation II'],
                ['thymine degradation', 'sulfoacetate degradation', 'L-lysine degradation VI',
                 'uracil degradation I (reductive)', 'homotaurine degradation',
                 "cytidine-5'-diphosphate-glycerol biosynthesis", 'yersiniabactin biosynthesis'],
                ['4-hydroxy-2-nonenal detoxification', 'furcatin degradation',
                 'ceramide and sphingolipid recycling and degradation (yeast)', 'chitin deacetylation',
                 'megalomicin A biosynthesis', 'erythromycin A biosynthesis',
                 'tea aroma glycosidic precursor bioactivation'],
                ['saframycin A biosynthesis', 'aureobasidin A biosynthesis', 'fusaridione A biosynthesis',
                 'apicidin biosynthesis', 'apicidin F biosynthesis', 'galactolipid biosynthesis II',
                 'equisetin biosynthesis'],
                ['CDP-6-deoxy-D-gulose biosynthesis', 'cell-surface glycoconjugate-linked phosphonate biosynthesis',
                 'chlorophyll b2 biosynthesis', 'biotin biosynthesis from 8-amino-7-oxononanoate III',
                 'bile acid 7&beta;-dehydroxylation', "5'-deoxyadenosine degradation II", 'NADPH repair (eukaryotes)'],
                ['bassianin and desmethylbassianin biosynthesis', '3,6-anhydro-&alpha;-L-galactopyranose degradation',
                 'arginomycin biosynthesis', 'aspyridone A biosynthesis', 'ferrichrome A biosynthesis',
                 'blasticidin S biosynthesis', 'bacimethrin and bacimethrin pyrophosphate biosynthesis'],
                ['L-arginine degradation II (AST pathway)', 'Calvin-Benson-Bassham cycle',
                 'glycine betaine biosynthesis I (Gram-negative bacteria)',
                 'L-phenylalanine degradation II (anaerobic)', 'L-arginine degradation VIII (arginine oxidase pathway)',
                 'ammonia oxidation I (aerobic)', 'L-arginine degradation VII (arginase 3 pathway)'],
                ['yatein biosynthesis I', 'p-HBAD biosynthesis', 'diphenyl ethers degradation',
                 "(-)-4'-demethyl-epipodophyllotoxin biosynthesis", 'mycobacterial sulfolipid biosynthesis',
                 'carbon monoxide oxidation to CO2', 'dimycocerosyl phthiocerol biosynthesis'],
                ['mevalonate degradation', 'glycogen biosynthesis II (from UDP-D-Glucose)', 'L-leucine degradation II',
                 'gibberellin biosynthesis I (non C-3, non C-13 hydroxylation)', 'L-isoleucine degradation II',
                 'chlorophyll cycle', 'L-leucine degradation III'],
                ['abscisic acid biosynthesis', 'L-ascorbate degradation V', 'methanol oxidation to formaldehyde I',
                 'methylamine degradation II', 'methylamine degradation I', 'L-ascorbate degradation III',
                 'L-ascorbate degradation II (bacterial, aerobic)'],
                ["2,2'-dihydroxyketocarotenoids biosynthesis", "abscisic acid degradation to 7'-hydroxyabscisate",
                 'abscisic acid degradation to neophaseic acid', '5-hexynoate biosynthesis',
                 'echinenone and zeaxanthin biosynthesis (Synechocystis)',
                 'bis(guanylyl molybdenum cofactor) biosynthesis', 'astaxanthin biosynthesis (flowering plants)'],
                ['calonectrin biosynthesis', 'penicillin G and penicillin V biosynthesis',
                 '3-hydroxy-4-methyl-anthranilate biosynthesis I', 'nivalenol biosynthesis',
                 'FeMo cofactor biosynthesis', 'deoxynivalenol biosynthesis',
                 'harzianum A and trichodermin biosynthesis'],
                ['D-apiose degradation I', 'D-apionate degradation II (RLP decarboxylase)',
                 '(S)-lactate fermentation to propanoate, acetate and hydrogen', 'indole-3-acetate degradation II',
                 'D-apionate degradation III (RLP transcarboxylase/hydrolase)', 'dipicolinate biosynthesis',
                 'D-apionate degradation I (xylose isomerase family decarboxylase)'],
                ['2-aminoethylphosphonate biosynthesis', 'nitrate reduction IV (dissimilatory)',
                 'GDP-6-deoxy-D-altro-heptose biosynthesis', 'Oxidase test', 'hexaprenyl diphosphate biosynthesis',
                 'D-sorbitol degradation I', 'glycerol-3-phosphate shuttle'],
                ['heme degradation V', 'heme degradation VII',
                 '6-hydroxymethyl-dihydropterin diphosphate biosynthesis V (Pyrococcus)',
                 '6-hydroxymethyl-dihydropterin diphosphate biosynthesis IV (Plasmodium)', 'heme degradation VI',
                 'urate conversion to allantoin III', 'taurine biosynthesis II'],
                ['hyoscyamine and scopolamine biosynthesis', 'gentiodelphin biosynthesis', 'calystegine biosynthesis',
                 'N-methyl-&Delta;1-pyrrolinium cation biosynthesis', 'L-lysine degradation VII',
                 'nicotine biosynthesis', 'L-lysine degradation VIII'],
                ['&alpha;-cyclopiazonate biosynthesis', 'heme d1 biosynthesis', '(-)-microperfuranone biosynthesis',
                 'prodigiosin biosynthesis', 'ergothioneine biosynthesis II (fungi)',
                 'heme b biosynthesis III (from siroheme)', 'asperlicin E biosynthesis'],
                ['D-sorbitol degradation II', '6-hydroxymethyl-dihydropterin diphosphate biosynthesis I',
                 '4-methylphenyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP',
                 'allantoin degradation to ureidoglycolate II (ammonia producing)',
                 '6-hydroxymethyl-dihydropterin diphosphate biosynthesis III (Chlamydia)',
                 'glycolate and glyoxylate degradation I',
                 'phenyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP'],
                ['staphyloferrin B biosynthesis', 'plant arabinogalactan type II degradation',
                 'L-cysteine biosynthesis IX (Trichomonas vaginalis)',
                 'L-cysteine biosynthesis VIII (Thermococcus kodakarensis)', 'staphylopine biosynthesis',
                 '4-coumarate degradation (aerobic)', 'trans-caffeate degradation (aerobic)'],
                ['Ferredoxin:NAD+ oxidoreductase', 'D-fructuronate degradation', '(S)-propane-1,2-diol degradation',
                 'glycerol degradation III', 'S-methyl-L-methionine cycle', 'Entner-Doudoroff shunt',
                 'xylitol degradation'],
                ['trehalose degradation VI (periplasmic)', 'Extracellular starch(27n) degradation',
                 '(S)-lactate fermentation to propanoate', 'L-threonine degradation V',
                 'trehalose degradation II (cytosolic)', 'C4 photosynthetic carbon assimilation cycle, NAD-ME type',
                 '2-aminoethylphosphonate degradation II'],
                ['anandamide degradation', '2-heptyl-3-hydroxy-4(1H)-quinolone biosynthesis', 'dopamine degradation',
                 'pyocyanin biosynthesis', 'pterostilbene biosynthesis', 'di-myo-inositol phosphate biosynthesis'],
                ['L-lysine degradation V', 'sulfite oxidation III', 'sulfite oxidation II', 'L-lysine degradation IV',
                 'sulfide oxidation III (to sulfite)', 'shisonin biosynthesis'],
                ['protein O-glycosylation (Neisseria)', 'alkane biosynthesis II', 'alkane biosynthesis I',
                 'protein N-glycosylation (bacterial)', '(9Z)-tricosene biosynthesis',
                 'very long chain fatty acid biosynthesis II'],
                ['nerol biosynthesis', 'geraniol biosynthesis (cytosol)', 'acrylate degradation II',
                 'platensimycin biosynthesis', '2-methyl-branched fatty acid &beta;-oxidation',
                 '10-methylstearate biosynthesis'],
                ['methanogenesis from glycine betaine', 'glycine betaine degradation III',
                 'proline betaine degradation II', 'L-dopa degradation II (bacterial)', 'kavain biosynthesis',
                 'yangonin biosynthesis'],
                ['2-deoxy-D-glucose 6-phosphate degradation', '&beta;-alanine degradation III',
                 'mycofactocin biosynthesis', 'microcin B17 biosynthesis',
                 '(2-trimethylamino)ethylphosphonate degradation', 'chlorophyll a2 biosynthesis'],
                ['brassinosteroid biosynthesis II', 'benzoate degradation I (aerobic)', '(+)-pisatin biosynthesis',
                 'fatty acid &alpha;-oxidation I (plants)', 'phytosterol biosynthesis (plants)',
                 'medicarpin conjugates interconversion'],
                ['hinokiresinol biosynthesis', 'kievitone detoxification', 'vernolate biosynthesis II',
                 'hinokinin biosynthesis', 'arctigenin and isoarctigenin biosynthesis',
                 'calycosin 7-O-glucoside biosynthesis'],
                ['&beta; myrcene degradation', 'sesaminol glucoside biosynthesis',
                 'myricetin gentiobioside biosynthesis', 'quercetin gentiotetraside biosynthesis',
                 'emetine biosynthesis', 'noscapine biosynthesis'],
                ['zealexin biosynthesis', 'thiamine diphosphate salvage III', 'thiamine diphosphate salvage I',
                 'thiazole component of thiamine diphosphate biosynthesis II', 'isopropanol biosynthesis (engineered)',
                 'retinoate biosynthesis II'], ['(R)- and (S)-3-hydroxybutanoate biosynthesis (engineered)',
                                                'ubiquinol-6 biosynthesis from 4-aminobenzoate (yeast)',
                                                'nicotinate degradation I',
                                                'baicalein degradation (hydrogen peroxide detoxification)',
                                                'gibberellin biosynthesis V', 'purine deoxyribonucleosides salvage'],
                ['sapienate biosynthesis', 'tetrathionate reduction I (to thiosulfate)', 'chrysin biosynthesis',
                 '(5Z)-icosenoate biosynthesis', 'tetrathionate reductiuon II (to trithionate)',
                 'linear furanocoumarin biosynthesis'],
                ['leucodelphinidin biosynthesis', 'trans-4-hydroxy-L-proline degradation II',
                 "6'-deoxychalcone metabolism", 'anthocyanin biosynthesis (delphinidin 3-O-glucoside)',
                 'L-tyrosine degradation II', 'rose anthocyanin biosynthesis I (via cyanidin 5-O-&beta;-D-glucoside)'],
                ['arsenate reduction (respiratory)',
                 '1D-myo-inositol hexakisphosphate biosynthesis III (Spirodela polyrrhiza)',
                 'arsenite oxidation I (respiratory)', 'wighteone and luteone biosynthesis',
                 'arsenate detoxification II (glutaredoxin)', 'kievitone biosynthesis'],
                ['pyruvate fermentation to opines', 'daunorubicin biosynthesis', 'sucrose biosynthesis III',
                 'thiamine phosphate formation from pyrithiamine and oxythiamine (yeast)', 'aclacinomycin biosynthesis',
                 'doxorubicin biosynthesis'],
                ['IM-2 type &gamma;-butyrolactones biosynthesis', 'D-erythronate degradation II',
                 'D-threonate degradation', 'virginiae butanolide type &gamma;-butyrolactones biosynthesis',
                 'coelimycin P1 biosynthesis', 'A-factor &gamma;-butyrolactone biosynthesis'],
                ['lupanine biosynthesis', 'bisbenzylisoquinoline alkaloid biosynthesis',
                 'hydroxycinnamic acid serotonin amides biosynthesis', 'palmatine biosynthesis',
                 'hydroxycinnamic acid tyramine amides biosynthesis', 'sesamin biosynthesis'],
                ['nepetalactone biosynthesis', '(Kdo)2-lipid A biosynthesis II (P. putida)',
                 'methylphosphonate biosynthesis', 'methylphosphonate degradation III',
                 'N-3-oxalyl-L-2,3-diaminopropanoate biosynthesis',
                 '8-O-methylated benzoxazinoid glucoside biosynthesis'],
                ['willardiine and isowillardiine biosynthesis', 'tetrahydroxyxanthone biosynthesis (from benzoate)',
                 'UDP-&alpha;-D-galacturonate biosynthesis II (from D-galacturonate)',
                 'indole-3-acetate biosynthesis IV (bacteria)', 'L-arginine degradation XI',
                 'tetrahydroxyxanthone biosynthesis (from 3-hydroxybenzoate)'],
                ['cob(II)yrinate a,c-diamide biosynthesis II (late cobalt incorporation)',
                 'urate conversion to allantoin II', 'aminopropanol phosphate biosynthesis II',
                 'lipoate biosynthesis and incorporation IV (yeast)', 'mRNA capping I',
                 'cob(II)yrinate a,c-diamide biosynthesis I (early cobalt insertion)'],
                ['group E Salmonella O antigen biosynthesis', 'group D2 Salmonella O antigen biosynthesis',
                 'group A Salmonella O antigen biosynthesis', 'group D1 Salmonella O antigen biosynthesis',
                 'group C2 Salmonella O antigen biosynthesis', 'toluene degradation to benzoyl-CoA (anaerobic)'],
                ['starch degradation II', 'candicidin biosynthesis', 'methylhalides biosynthesis (plants)',
                 'methylaspartate cycle', 'sangivamycin biosynthesis', 'toyocamycin biosynthesis'],
                ['plasmalogen degradation', 'butane degradation', 'methyl tert-butyl ether degradation',
                 '&omega;-sulfo-II-dihydromenaquinone-9 biosynthesis', 'plasmalogen biosynthesis',
                 '2-methylpropene degradation'],
                ['o-diquinones biosynthesis', 'methane oxidation to methanol II', 'pinitol biosynthesis I',
                 'pinitol biosynthesis II', "S-methyl-5'-thioadenosine degradation I",
                 'nitrate reduction VII (denitrification)'],
                ['thiocoraline biosynthesis', 'echinomycin and triostin A biosynthesis',
                 'quinoxaline-2-carboxylate biosynthesis', 'stellatic acid biosynthesis',
                 '3-hydroxyquinaldate biosynthesis', 'T-2 toxin biosynthesis'],
                ['putrescine biosynthesis III', 'creatinine degradation II', 'phytate degradation I',
                 'creatinine degradation III', 'phytate degradation II', 'aloesone biosynthesis I'],
                ['&beta;-D-mannosyl phosphomycoketide biosynthesis', 'aucuparin biosynthesis',
                 'phthiocerol biosynthesis', 'polyacyltrehalose biosynthesis', 'phenolphthiocerol biosynthesis',
                 'dimycocerosyl triglycosyl phenolphthiocerol biosynthesis'],
                ['5-(methoxycarbonylmethoxy)uridine biosynthesis', 'methylphosphonate degradation I',
                 'proline to cytochrome bo oxidase electron transfer',
                 'D-lactate to cytochrome bo oxidase electron transfer', 'cardiolipin biosynthesis III',
                 'muropeptide degradation'], ['methanogenesis from methylamine', 'soybean saponin I biosynthesis',
                                              'coenzyme B/coenzyme M regeneration I (methanophenazine-dependent)',
                                              'methanogenesis from dimethylamine', 'methyl-coenzyme M oxidation to CO2',
                                              'factor 420 polyglutamylation'],
                ['flavin-N5-oxide biosynthesis', '2-deoxy-D-ribose degradation II', '8-oxo-(d)GTP detoxification II',
                 'chlorpyrifos degradation', 'pyruvoyl group formation from L-serine', 'sodorifen biosynthesis'],
                ['p-cumate degradation to 2-hydroxypentadienoate', 'melamine degradation',
                 'ferulate and sinapate biosynthesis', '4-toluenesulfonate degradation II',
                 'cyanuric acid degradation II', '2-hydroxypenta-2,4-dienoate degradation'],
                ['adenosylcobinamide-GDP salvage from cobinamide II', 'N-methylpyrrolidone degradation',
                 'adenosylcobalamin biosynthesis from adenosylcobinamide-GDP II',
                 'protein O-mannosylation III (mammals, core M3)', 'cobalamin salvage (eukaryotic)',
                 'adenosylcobinamide-GDP salvage from cobinamide I'],
                ['putrescine degradation V', "S-methyl-5'-thioadenosine degradation III",
                 '&beta;-alanine degradation I', 'Electron bifurcating LDH/Etf complex', 'acrylonitrile degradation II',
                 'indole-3-acetate biosynthesis V (bacteria and fungi)'],
                ['caffeine biosynthesis II (via paraxanthine)', 'theobromine biosynthesis I', 'GA12 biosynthesis',
                 'gibberellin biosynthesis II (early C-3 hydroxylation)', 'caffeine biosynthesis I',
                 'gibberellin biosynthesis III (early C-13 hydroxylation)'],
                ["6'-dechloromelleolide F biosynthesis", 'pheomelanin biosynthesis', 'firefly bioluminescence',
                 'coral bioluminescence', 'dinoflagellate bioluminescence', 'jellyfish bioluminescence'],
                ['resolvin D biosynthesis', 'homocarnosine biosynthesis', 'aspirin triggered resolvin E biosynthesis',
                 'carnosine biosynthesis', 'aspirin triggered resolvin D biosynthesis', 'salicylate degradation IV'],
                ['trehalose degradation V', 'acetate and ATP formation from acetyl-CoA II',
                 '8-amino-7-oxononanoate biosynthesis III', 'trehalose degradation IV',
                 'UDP-N-acetyl-&alpha;-D-mannosaminouronate biosynthesis',
                 'L-tryptophan degradation II (via pyruvate)'],
                ['cephamycin C biosynthesis', '2-nitrophenol degradation', '2,4-dinitrotoluene degradation',
                 'nitrobenzene degradation II', '2-nitrotoluene degradation', 'nitrobenzene degradation I'],
                ['thiamine diphosphate biosynthesis III (Staphylococcus)',
                 'thiazole component of thiamne diphosphate biosynthesis III', '(Z)-butanethial-S-oxide biosynthesis',
                 'chitin derivatives degradation', 'thiamine diphosphate biosynthesis IV (eukaryotes)',
                 'base-degraded thiamine salvage'],
                ['sitosterol degradation to androstenedione', 'lincomycin A biosynthesis',
                 'DIBOA-glucoside biosynthesis', 'DIMBOA-glucoside biosynthesis',
                 'dTDP-3-acetamido-&alpha;-D-fucose biosynthesis',
                 'icosapentaenoate biosynthesis I (lower eukaryotes)'],
                ['procollagen hydroxylation and glycosylation', 'protein SAMPylation and SAMP-mediated thiolation',
                 'tRNA-uridine 2-thiolation (yeast mitochondria)', 'tRNA-uridine 2-thiolation (cytoplasmic)',
                 'tRNA-uridine 2-thiolation (mammalian mitochondria)',
                 'tRNA-uridine 2-thiolation and selenation (bacteria)'],
                ['nocardicin A biosynthesis', 'pentose phosphate pathway (oxidative branch) II',
                 'dimethyl sulfide biosynthesis from methionine', 'terephthalate degradation',
                 'protein S-nitrosylation and denitrosylation', 'Arg/N-end rule pathway (eukaryotic)'],
                ['2-fucosyllactose degradation', 'sulfate reduction I (assimilatory)', 'viscosin biosynthesis',
                 'massetolide A biosynthesis', 'Lacto-N-tetraose degradation', 'L-valine degradation I'],
                ['D-sorbitol biosynthesis I', 'L-valine degradation II', 'luteolin biosynthesis',
                 'pinobanksin biosynthesis', 'rosmarinic acid biosynthesis I', 'rosmarinic acid biosynthesis II'],
                ['sophorolipid biosynthesis', 'shikimate degradation I', 'thioredoxin pathway',
                 'sophorosyloxydocosanoate deacetylation', 'sucrose degradation VII (sucrose 3-dehydrogenase)',
                 'sphingolipid biosynthesis (yeast)'],
                ["pyridoxal 5'-phosphate salvage II (plants)", 'pyrimidine deoxyribonucleosides salvage',
                 'quercetin diglycoside biosynthesis (pollen-specific)', 'pinocembrin C-glucosylation',
                 'kaempferol diglycoside biosynthesis (pollen-specific)', 'UTP and CTP dephosphorylation I'],
                ['atromentin biosynthesis', '3-(4-sulfophenyl)butanoate degradation', 'terrequinone A biosynthesis',
                 '(R)-canadine biosynthesis', 'brassicicene C biosynthesis', 'mevalonate pathway III (Thermoplasma)'],
                ['cutin biosynthesis', 'sinapate ester biosynthesis', 'canavanine degradation',
                 'L-tryptophan degradation VI (via tryptamine)', 'UDP-&beta;-L-rhamnose biosynthesis',
                 'choline biosynthesis I'],
                ['oleoresin monoterpene volatiles biosynthesis', 'naphthalene degradation (aerobic)',
                 'betaxanthin biosynthesis', '1,3-dimethylbenzene degradation to 3-methylbenzoate',
                 'isopimaric acid biosynthesis', 'oleoresin sesquiterpene volatiles biosynthesis'],
                ['UDP-N-acetylmuramoyl-pentapeptide biosynthesis II (lysine-containing)',
                 'UDP-N-acetylmuramoyl-pentapeptide biosynthesis I (meso-diaminopimelate containing)',
                 'arginine deiminase test', 'peptidoglycan biosynthesis I (meso-diaminopimelate containing)',
                 'flavin salvage', 'peptidoglycan cross-bridge biosynthesis II (E. faecium)'],
                ['kanosamine biosynthesis II', 'CO2 fixation into oxaloacetate (anaplerotic)',
                 'indole-3-acetate biosynthesis I', 'salicylate biosynthesis II', 'mycolate biosynthesis',
                 'sulfoquinovosyl diacylglycerol biosynthesis'],
                ['pentaketide chromone biosynthesis', 'L-homomethionine biosynthesis', 'taurine degradation II',
                 'phenylacetate degradation II (anaerobic)', 'benzoyl-CoA degradation I (aerobic)',
                 'fluorene degradation II'],
                ['iso-bile acids biosynthesis II', 'gadusol biosynthesis', 'bacteriochlorophyll d biosynthesis',
                 'shinorine biosynthesis', 'bile acid 7&alpha;-dehydroxylation', 'bisphenol A degradation'],
                ['biphenyl degradation', 'linoleate biosynthesis II (animals)', 'phthalate degradation (aerobic)',
                 'gramicidin S biosynthesis', '&gamma;-linolenate biosynthesis II (animals)',
                 'lotaustralin degradation'],
                ['phenylethanol glycoconjugate biosynthesis', 'N-acetyl-D-galactosamine degradation',
                 '3,5-dimethoxytoluene biosynthesis', 'phenylethyl acetate biosynthesis', 'asterrate biosynthesis',
                 'hopanoid biosynthesis (bacteria)'],
                ['tetramethylpyrazine degradation', 'aurachin A, B, C and D biosynthesis', 'aurachin RE biosynthesis',
                 'phospholipid remodeling (phosphatidylethanolamine, yeast)',
                 'ceramide phosphoethanolamine biosynthesis', 'methylphosphonate degradation II'],
                ['cycloartenol biosynthesis', 'epiberberine biosynthesis', 'coptisine biosynthesis',
                 'sterol biosynthesis (methylotrophs)', 'limonene degradation IV (anaerobic)', 'parkeol biosynthesis'],
                ['N-glucosylnicotinate metabolism', 'methylglyoxal degradation VIII', 'NAD salvage (plants)',
                 'rutin biosynthesis', 'methylglyoxal degradation I', '3-methylthiopropanoate biosynthesis'],
                ['divinyl ether biosynthesis II', 'traumatin and (Z)-3-hexen-1-yl acetate biosynthesis',
                 '9-lipoxygenase and 9-allene oxide synthase pathway', 'abietic acid biosynthesis',
                 'levopimaric acid biosynthesis', '9-lipoxygenase and 9-hydroperoxide lyase pathway'],
                ['erythromycin D biosynthesis', 'dTDP-&beta;-L-megosamine biosynthesis', '5-deoxystrigol biosynthesis',
                 'bisabolene biosynthesis (engineered)', 'olivetol biosynthesis'],
                ['menaquinol-4 biosynthesis II', 'dolabralexins biosynthesis', 'tricin biosynthesis',
                 'vitamin K degradation', 'vitamin K-epoxide cycle'],
                ['L-cysteine degradation I', 'cyclohexanol degradation', 'cyanate degradation',
                 'nitrate reduction I (denitrification)', 'D-arabinose degradation II'],
                ['bacteriochlorophyll a biosynthesis', 'D-arabinose degradation III', 'D-glucuronate degradation I',
                 'L-ascorbate biosynthesis III (D-sorbitol pathway)',
                 '5,6-dimethylbenzimidazole biosynthesis I (aerobic)'],
                ['docosahexaenoate biosynthesis I (lower eukaryotes)',
                 'icosapentaenoate biosynthesis II (6-desaturase, mammals)', '4-coumarate degradation (anaerobic)',
                 'icosapentaenoate biosynthesis IV (bacteria)', 'cyanophycin metabolism'],
                ['(1,3)-&beta;-D-xylan degradation', 'xyloglucan degradation I (endoglucanase)',
                 'cellulose degradation II (fungi)', 'flavonoid biosynthesis (in equisetum)', 'L-arabinan degradation'],
                ['3-(imidazol-5-yl)lactate salvage', 'L-histidine degradation V', 'nicotinate degradation II',
                 'L-histidine degradation II', 'ent-kaurene biosynthesis I'],
                ['4-sulfocatechol degradation', 'ethanedisulfonate degradation', 'chlorogenic acid biosynthesis II',
                 'methanesulfonate degradation', 'chlorogenic acid biosynthesis I'],
                ['homospermidine biosynthesis II', 'cholesterol degradation to androstenedione III (anaerobic)',
                 'cytochrome c biogenesis (system I type)', 'cytochrome c biogenesis (system II type)',
                 'androsrtendione degradation II (anaerobic)'],
                ['aliphatic glucosinolate biosynthesis, side chain elongation cycle',
                 'glucosinolate biosynthesis from pentahomomethionine',
                 'glucosinolate biosynthesis from trihomomethionine',
                 'glucosinolate biosynthesis from dihomomethionine',
                 'glucosinolate biosynthesis from tetrahomomethionine'],
                ['4-chloronitrobenzene degradation', '2-nitrobenzoate degradation II',
                 'L-tryptophan degradation to 2-amino-3-carboxymuconate semialdehyde', '4-nitrotoluene degradation II',
                 '2,6-dinitrotoluene degradation'],
                ['3,8-divinyl-chlorophyllide a biosynthesis III (aerobic, light independent)',
                 'L-phenylalanine degradation V', 'polymethylated quercetin biosynthesis',
                 'polymethylated myricetin biosynthesis (tomato)', '7-dehydroporiferasterol biosynthesis'],
                ['triclosan resistance', 'CMP phosphorylation', 'ppGpp metabolism',
                 'guanosine ribonucleotides de novo biosynthesis', 'UTP and CTP de novo biosynthesis'],
                ['Spodoptera littoralis pheromone biosynthesis', 'dechlorogriseofulvin biosynthesis',
                 '(8E,10E)-dodeca-8,10-dienol biosynthesis', 'dTDP-&beta;-L-digitoxose biosynthesis',
                 'griseofulvin biosynthesis'],
                ['i antigen and I antigen biosynthesis', 'globo-series glycosphingolipids biosynthesis',
                 'gala-series glycosphingolipids biosynthesis', 'lacto-series glycosphingolipids biosynthesis',
                 'ganglio-series glycosphingolipids biosynthesis'],
                ['superoxide radicals degradation', 'chitin degradation II (Vibrio)', 'Catalase test',
                 'ethanol degradation IV', 'L-arabinose degradation I'],
                ['dimethylsulfoniopropanoate biosynthesis III (algae and phytoplankton)',
                 'dimethylsulfoniopropanoate biosynthesis II (Spartina)',
                 'dimethylsulfoniopropanoate biosynthesis I (Wollastonia)',
                 'dimethylsulfoniopropanoate degradation II (cleavage)',
                 'dimethylsulfide to cytochrome c2 electron transfer'],
                ['branched-chain polyamines biosynthesis', 'carbaryl degradation',
                 'factor 420 biosynthesis I (archaea)', '3PG-factor 420 biosynthesis',
                 'long-chain polyamine biosynthesis'],
                ['indole-3-acetate inactivation IV', 'free phenylpropanoid acid biosynthesis',
                 'glutamate removal from folates', 'isoflavonoid biosynthesis I', 'isoflavonoid biosynthesis II'],
                ["adenosine 5'-phosphoramidate biosynthesis", 'fatty acid biosynthesis initiation (plant mitochondria)',
                 'diacylglyceryl-N,N,N-trimethylhomoserine biosynthesis', 'scopoletin biosynthesis',
                 '6-hydroxymethyl-dihydropterin diphosphate biosynthesis II (Methanocaldococcus)'],
                ['galloylated catechin biosynthesis', 'anthocyanidin modification (Arabidopsis)',
                 '2-aminoethylphosphonate degradation III', 'cyanidin dimalonylglucoside biosynthesis',
                 'acylated cyanidin galactoside biosynthesis'], ['indole glucosinolate activation (intact plant cell)',
                                                                 'glucosinolate biosynthesis from hexahomomethionine',
                                                                 'NAD salvage pathway I (PNC VI cycle)',
                                                                 'indole glucosinolate activation (herbivore attack)',
                                                                 'quinate degradation I'],
                ['autoinducer CAI-1 biosynthesis', 'nystatin biosynthesis', 'naphthalene degradation (anaerobic)',
                 'astaxanthin dirhamnoside biosynthesis', 'rhizobactin 1021 biosynthesis'],
                ['2-methyladeninyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP',
                 '5-methoxy-6-methylbenzimidazolyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP',
                 'rhabduscin biosynthesis', 'adeninyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP',
                 '12-epi-fischerindole biosynthesis'],
                ['nitroethane degradation', 'ajugose biosynthesis II (galactinol-independent)',
                 'arachidonate biosynthesis I (6-desaturase, lower eukaryotes)', 'kaempferol triglucoside biosynthesis',
                 'esculetin biosynthesis'],
                ['&gamma;-resorcylate degradation I', 'propane degradation I', 'butachlor degradation',
                 '&gamma;-resorcylate degradation II', 'indolmycin biosynthesis'],
                ['paspaline biosynthesis', '3&beta;-hydroxysesquiterpene lactone biosynthesis', 'gossypetin metabolism',
                 'linuron degradation', 'paxilline and diprenylpaxilline biosynthesis'],
                ['dTDP-&beta;-L-olivose biosynthesis', 'umbelliferone biosynthesis', 'plastoquinol-9 biosynthesis II',
                 'dTDP-&beta;-L-mycarose biosynthesis', 'threo-tetrahydrobiopterin biosynthesis'],
                ['gliotoxin biosynthesis', 'lovastatin biosynthesis', 'aflatrem biosynthesis',
                 'fumiquinazoline D biosynthesis', '1,2-propanediol biosynthesis from lactate (engineered)'],
                ['flavonol acylglucoside biosynthesis II - isorhamnetin derivatives',
                 'flavonol acylglucoside biosynthesis I - kaempferol derivatives', 'phytochromobilin biosynthesis',
                 'flavonol acylglucoside biosynthesis III - quercetin derivatives',
                 'kaempferide triglycoside biosynthesis'],
                ['methyl phomopsenoate biosynthesis', 'ophiobolin F biosynthesis', 'bacterial bioluminescence',
                 'sulfoquinovose degradation II', 'icosapentaenoate biosynthesis III (8-desaturase, mammals)'],
                ['pelargonidin diglucoside biosynthesis (acyl-glucose dependent)',
                 'cyanidin diglucoside biosynthesis (acyl-glucose dependent)',
                 'ergothioneine biosynthesis I (bacteria)', 'apigeninidin 5-O-glucoside biosynthesis',
                 'luteolinidin 5-O-glucoside biosynthesis'],
                ['methylglyoxal degradation VII', 'matairesinol biosynthesis',
                 'acetone degradation I (to methylglyoxal)', 'gramine biosynthesis', 'methylglyoxal degradation II'],
                ['anthocyanidin acylglucoside and acylsambubioside biosynthesis', '1-chloro-2-nitrobenzene degradation',
                 'carnosate bioynthesis', 'arabidopyrone biosynthesis', 'nitrite reduction (hemoglobin)'],
                ['adamantanone degradation', 'phosphonoacetate degradation', 'arsonoacetate degradation',
                 'incomplete reductive TCA cycle', '4-nitrotoluene degradation I'],
                ['&alpha;-carotene biosynthesis', '&beta;-carotene biosynthesis',
                 'violaxanthin, antheraxanthin and zeaxanthin interconversion', 'zeaxanthin biosynthesis',
                 'streptomycin biosynthesis'],
                ['palmitoleate biosynthesis III (cyanobacteria)', '(7Z,10Z,13Z)-hexadecatrienoate biosynthesis',
                 'okenone biosynthesis', 'ursodeoxycholate biosynthesis (bacteria)',
                 'linoleate biosynthesis III (cyanobacteria)'],
                ['archaeosine biosynthesis I', 'L-rhamnose degradation II',
                 'ubiquinol-8 biosynthesis (early decarboxylation)', 'L-rhamnose degradation III',
                 'poly-hydroxy fatty acids biosynthesis'],
                ['chaxamycin biosynthesis', 'spectinabilin biosynthesis', 'streptovaricin biosynthesis',
                 'chloramphenicol biosynthesis', 'aureothin biosynthesis'],
                ['Bile acid 7alpha-dehydroxylation', 'Inulin degradation(11xFru,1xGlc) (extracellular)',
                 'iso-bile acids biosynthesis (NADH or NADPH dependent)',
                 'L-Tyrosine degradation to 4-hydroxyphenylacetate via tyramine', 'Ljungdahl-Wood pathway (gapseq)'],
                ['(3R)-linalool biosynthesis', 'viridicatin biosynthesis', 'lyngbyatoxin biosynthesis',
                 "4'-methoxyviridicatin biosynthesis", 'dapdiamides biosynthesis'],
                ['purine deoxyribonucleosides degradation I', '4-deoxy-L-threo-hex-4-enopyranuronate degradation',
                 'L-homocysteine biosynthesis', 'adenine and adenosine salvage III',
                 'purine deoxyribonucleosides degradation II'],
                ['guanosine nucleotides degradation II', 'laminaribiose degradation',
                 'adenosine nucleotides degradation I', 'guanosine nucleotides degradation III',
                 'anhydromuropeptides recycling I'],
                ['betacyanin biosynthesis (via dopamine)', 'aminopropanol phosphate biosynthesis I',
                 'benzene degradation', '1,4-dimethylbenzene degradation to 4-methylbenzoate',
                 '(3E)-4,8-dimethylnona-1,3,7-triene biosynthesis I'],
                ['isorenieratene biosynthesis I (actinobacteria)', 'spongiadioxin C biosynthesis',
                 'polybrominated dihydroxylated diphenyl ethers biosynthesis', 'fungal bioluminescence',
                 'psilocybin biosynthesis'],
                ['L-valine degradation III (oxidative Stickland reaction)', 'valproate &beta;-oxidation',
                 'L-isoleucine degradation III (oxidative Stickland reaction)',
                 'L-alanine degradation VI (reductive Stickland reaction)',
                 'L-leucine degradation V (oxidative Stickland reaction)'],
                ['spermine biosynthesis', 'L-arginine degradation III (arginine decarboxylase/agmatinase pathway)',
                 'L-arginine degradation X (arginine monooxygenase pathway)', 'linezolid resistance',
                 'putrescine biosynthesis I'],
                ['methyl ketone biosynthesis (engineered)', '4-amino-3-hydroxybenzoate degradation',
                 '4-hydroxyacetophenone degradation', 'GDP-L-fucose biosynthesis II (from L-fucose)',
                 'brassinosteroid biosynthesis I'], ['1,5-anhydrofructose degradation', '(-)-camphor biosynthesis',
                                                     'nicotine degradation II (pyrrolidine pathway)',
                                                     'L-pyrrolysine biosynthesis', '(+)-camphor biosynthesis'],
                ['naringenin glycoside biosynthesis', 'chlorophyll a degradation I',
                 'L-glutamate degradation VI (to pyruvate)', 'L-methionine degradation III',
                 'chlorophyll a biosynthesis I'],
                ['baumannoferrin biosynthesis', 'acinetobactin biosynthesis', 'anguibactin biosynthesis',
                 'oxalate degradation VI', 'vanchrobactin biosynthesis'],
                ['rhizobitoxine biosynthesis', 'Escherichia coli serotype O9a O-antigen biosynthesis',
                 'formaldehyde oxidation V (bacillithiol-dependent)', 'homofuraneol biosynthesis',
                 '(2S,3E)-2-amino-4-methoxy-but-3-enoate biosynthesis'],
                ['apigenin glycosides biosynthesis', 'acyl carrier protein metabolism', 'baruol biosynthesis',
                 '(3E)-4,8-dimethylnona-1,3,7-triene biosynthesis II', 'amygdalin and prunasin degradation'],
                ['glycolysis V (Pyrococcus)', 'benzoyl-CoA degradation III (anaerobic)', 'aldoxime degradation',
                 'orcinol degradation', 'resorcinol degradation'],
                ['N6-L-threonylcarbamoyladenosine37-modified tRNA biosynthesis',
                 'cyclopropane fatty acid (CFA) biosynthesis', 'D-gluconate degradation', 'fructose degradation',
                 'L-threonine biosynthesis'],
                ['A series fagopyritols biosynthesis', '&alpha;-amyrin biosynthesis', 'punicate biosynthesis',
                 'B series fagopyritols biosynthesis', '&alpha;-eleostearate biosynthesis'],
                ['sucrose biosynthesis II', 'myo-inositol degradation II', 'mycocyclosin biosynthesis',
                 "inosine-5'-phosphate biosynthesis III", 'alkylnitronates degradation'],
                ['methanogenesis from tetramethylammonium', 'methanogenesis from methanethiol',
                 'salvianin biosynthesis', 'methanogenesis from methylthiopropanoate', 'glucosinolate activation'],
                ['complex N-linked glycan biosynthesis (plants)', 'archaeosine biosynthesis II',
                 'protein O-mannosylation II (mammals, core M1 and core M2)', 'rubber degradation I',
                 'protein O-mannosylation I (yeast)'],
                ['hentriaconta-3,6,9,12,15,19,22,25,28-nonaene biosynthesis', 'paromamine biosynthesis II',
                 'terminal olefins biosynthesis II', "UDP-N,N'-diacetylbacillosamine biosynthesis",
                 'gentamicin biosynthesis'], ['cyclobis-(1&rarr;6)-&alpha;-nigerosyl degradation',
                                              'ABH and Lewis epitopes biosynthesis from type 2 precursor disaccharide',
                                              'biosynthesis of Lewis epitopes (H. pylori)',
                                              'ABH and Lewis epitopes biosynthesis from type 1 precursor disaccharide',
                                              'glycolipid desaturation'],
                ['nitrate reduction III (dissimilatory)', 'pyrimidine ribonucleosides degradation',
                 'putrescine degradation II', 'protocatechuate degradation II (ortho-cleavage pathway)',
                 'L-proline degradation I'],
                ["3,3'-thiodipropanoate degradation", 'cyanidin 3,7-diglucoside polyacylation biosynthesis',
                 'N-methylanthraniloyl-&beta;-D-glucopyranose biosynthesis',
                 "3,3'-disulfanediyldipropannoate degradation", '2-O-acetyl-3-O-trans-coutarate biosynthesis'],
                ['trigonelline biosynthesis', 'polymyxin A biosynthesis', 'glycerophosphodiester degradation',
                 'putrescine degradation III', 'serotonin degradation'],
                ['hydrogen production VI', 'salicin biosynthesis', 'rhamnogalacturonan type I degradation I',
                 "4,4'-diapolycopenedioate biosynthesis", 'hydrogen production V'],
                ['quercetin glucoside biosynthesis (Allium)', 'rutin degradation (plants)',
                 'quercetin glucoside degradation (Allium)', 'L-glucose degradation',
                 'CMP-legionaminate biosynthesis II'],
                ['4-hydroxy-4-methyl-L-glutamate biosynthesis', '4-methylphenol degradation to protocatechuate',
                 '2,5-xylenol and 3,5-xylenol degradation', '2,4-xylenol degradation to protocatechuate',
                 'sch210971 and sch210972 biosynthesis'],
                ['dTDP-4-O-demethyl-&beta;-L-noviose biosynthesis', '3-amino-4,7-dihydroxy-coumarin biosynthesis',
                 'oleate &beta;-oxidation (reductase-dependent, yeast)',
                 '3-dimethylallyl-4-hydroxybenzoate biosynthesis', 'estradiol biosynthesis II'],
                ['UDP-N-acetyl-D-glucosamine biosynthesis I', 'L-asparagine biosynthesis III (tRNA-dependent)',
                 'S-adenosyl-L-methionine salvage II', 'CMP-3-deoxy-D-manno-octulosonate biosynthesis',
                 'cadaverine biosynthesis'], ['oleanolate biosynthesis', '2&alpha;,7&beta;-dihydroxylation of taxusin',
                                              'glycyrrhetinate biosynthesis', 'fumigaclavine biosynthesis',
                                              'esculetin modification'],
                ['CDP-4-dehydro-3,6-dideoxy-D-glucose biosynthesis', 'fluoroacetate degradation',
                 'volatile esters biosynthesis (during fruit ripening)', 'heme b biosynthesis V (aerobic)',
                 'heme b biosynthesis II (oxygen-independent)'],
                ['phosphatidylcholine resynthesis via glycerophosphocholine',
                 '1,4-dihydroxy-6-naphthoate biosynthesis II', 'thiamine triphosphate metabolism',
                 'demethylmenaquinol-6 biosynthesis II', '1,4-dihydroxy-6-naphthoate biosynthesis I'],
                ['pyruvate fermentation to ethanol II', 'pentagalloylglucose biosynthesis', 'cornusiin E biosynthesis',
                 '6-methoxypodophyllotoxin biosynthesis', 'gallotannin biosynthesis'],
                ['L-lysine degradation IX', 'sulfite oxidation IV (sulfite oxidase)', 'taurine biosynthesis I',
                 'carbon disulfide oxidation II (aerobic)', 'L-cysteine degradation III'],
                ['catechol degradation to &beta;-ketoadipate', 'benzoyl-CoA degradation II (anaerobic)',
                 'camalexin biosynthesis', '3,8-divinyl-chlorophyllide a biosynthesis I (aerobic, light-dependent)',
                 'L-carnitine degradation I'],
                ['folate transformations III (E. coli)', 'D-galactose detoxification', 'L-histidine degradation VI',
                 'L-histidine degradation III', 'L-alanine degradation II (to D-lactate)'],
                ['pulcherrimin biosynthesis', 'trehalose biosynthesis II', 'fructan degradation',
                 'bacillithiol biosynthesis', 'L-ascorbate biosynthesis I (plants, L-galactose pathway)'],
                ['pelargonidin conjugates biosynthesis', 'cannabinoid biosynthesis',
                 'acyl-[acyl-carrier protein] thioesterase pathway',
                 'fatty acid &beta;-oxidation III (unsaturated, odd number)',
                 'fatty acid &beta;-oxidation IV (unsaturated, even number)'],
                ['yatein biosynthesis II', '2,4-dinitroanisole degradation',
                 '2,4,6-trinitrophenol and 2,4-dinitrophenol degradation', 'phospholipid desaturation',
                 'bacilysin biosynthesis'], ['methylsalicylate degradation', "pyridoxal 5'-phosphate biosynthesis II",
                                             'glycine betaine degradation I',
                                             'benzoate degradation II (aerobic and anaerobic)',
                                             'NAD(P)/NADPH interconversion'],
                ['calendate biosynthesis', 'petroselinate biosynthesis',
                 'palmitoleate biosynthesis II (plants and bacteria)', 'carbon tetrachloride degradation I',
                 'dimorphecolate biosynthesis'],
                ['thiazole biosynthesis I (facultative anaerobic bacteria) with tautomerase',
                 'menaquinol oxidase (cytochrom aa3-600)', 'Extracellular galactan(2n) degradation',
                 'F420 Biosynthesis until 3 glutamine residues', 'H4SPT-SYN'],
                ['isovitexin glycosides biosynthesis', '2,3-trans-flavanols biosynthesis',
                 'nitrilotriacetate degradation', 'glucosinolate biosynthesis from tryptophan',
                 'capsiconiate biosynthesis'],
                ['tetrahydromonapterin biosynthesis', 'curcumin degradation', 'nitrate reduction VIII (dissimilatory)',
                 'uracil degradation III', 'tRNA processing'],
                ['sphingomyelin metabolism', 'phosphopantothenate biosynthesis II', '&beta;-alanine biosynthesis I',
                 'sphingosine and sphingosine-1-phosphate metabolism', 'berberine biosynthesis'],
                ['glucosylglycerol biosynthesis', 'glycogen biosynthesis III (from &alpha;-maltose 1-phosphate)',
                 'glucosinolate biosynthesis from tyrosine', 'protein NEDDylation',
                 'tRNA-uridine 2-thiolation (thermophilic bacteria)'],
                ['3-methyl-branched fatty acid &alpha;-oxidation', 'ceramide degradation by &alpha;-oxidation',
                 'sulfolactate degradation III', '15-epi-lipoxin biosynthesis', 'lipoxin biosynthesis'],
                ['heme degradation IV', 'heme degradation III', 'neolacto-series glycosphingolipids biosynthesis',
                 'UDP-yelosamine biosynthesis', 'heme degradation II'],
                ['fluoroacetate and fluorothreonine biosynthesis', 'labdane-type diterpenes biosynthesis',
                 'glycolate and glyoxylate degradation III', 'rhamnolipid biosynthesis',
                 'juvenile hormone III biosynthesis II'],
                ['D-carnitine degradation I', 'acetone degradation III (to propane-1,2-diol)',
                 'phosphatidylcholine biosynthesis VII', 'gentisate degradation II',
                 'benzoyl-&beta;-D-glucopyranose biosynthesis'],
                ['sterculate biosynthesis', '6-methoxymellein biosynthesis', 'nitrate reduction VI (assimilatory)',
                 'ethylbenzene degradation (anaerobic)', 'UDP-&alpha;-D-glucuronate biosynthesis (from myo-inositol)'],
                ['tetradecanoate biosynthesis (mitochondria)', 'anteiso-branched-chain fatty acid biosynthesis',
                 'even iso-branched-chain fatty acid biosynthesis',
                 'octanoyl-[acyl-carrier protein] biosynthesis (mitochondria, yeast)',
                 'odd iso-branched-chain fatty acid biosynthesis'],
                ['chlorzoxazone degradation', 'prunasin and amygdalin biosynthesis',
                 'Amaryllidacea alkaloids biosynthesis', 'juglone degradation', 'tunicamycin biosynthesis'],
                ['oxalate degradation III', 'Fe(II) oxidation', 'D-galactose degradation IV', 'oxalate degradation V',
                 'plaunotol biosynthesis'],
                ['androgen biosynthesis', 'mineralocorticoid biosynthesis', 'sulfolactate degradation II',
                 'glucocorticoid biosynthesis', 'estradiol biosynthesis I (via estrone)'],
                ['methanol oxidation to formaldehyde IV', 'vitamin B6 degradation',
                 'reductive monocarboxylic acid cycle', 'paraoxon degradation', 'L-arabinose degradation III'],
                ['4-aminophenol degradation', 'taxiphyllin biosynthesis', 'triethylamine degradation',
                 '2-methylisoborneol biosynthesis', 'geodin biosynthesis'],
                ['viridicatumtoxin biosynthesis', 'glycogen degradation III (via anhydrofructose)',
                 'protein N-glycosylation (Haloferax volcanii)', 'protein N-glycosylation (Methanococcus voltae)',
                 'tryptoquialanine biosynthesis'],
                ['(4Z,7Z,10Z,13Z,16Z)-docosa-4,7,10,13,16-pentaenoate biosynthesis II (4-desaturase)',
                 'arachidonate biosynthesis V (8-detaturase, mammals)',
                 '5,6-dimethylbenzimidazole biosynthesis II (anaerobic)',
                 '(4Z,7Z,10Z,13Z,16Z)-docosapentaenoate biosynthesis (6-desaturase)',
                 'docosahexaenoate biosynthesis IV (4-desaturase, mammals)'],
                ['elloramycin biosynthesis', 'cyclooctatin biosynthesis', 'tetracenomycin C biosynthesis',
                 'oryzalide A biosynthesis', 'phytocassanes biosynthesis, shared reactions'],
                ['holomycin biosynthesis', '10,13-epoxy-11-methyl-octadecadienoate biosynthesis',
                 'zwittermicin A biosynthesis', 'bikaverin biosynthesis', '8-O-methylfusarubin biosynthesis'],
                ['dTDP-L-daunosamine biosynthesis', '6-methylpretetramide biosynthesis',
                 'tetracycline and oxytetracycline biosynthesis', 'thiosulfate disproportionation III (quinone)',
                 'chlorotetracycline biosynthesis'],
                ['phycoviolobilin biosynthesis', 'phycourobilin biosynthesis', 'nitrogen fixation II (flavodoxin)',
                 'phycoerythrobilin biosynthesis II', 'mercaptosuccinate degradation']]
            # some entry can be appearing in more than one clustter so  ...
            if selected_bacteria.endswith("_otu"):
                selected_bacteria = selected_bacteria[:-4]
            for cluster in cluster_data_0_6:
                if selected_bacteria in cluster:
                    found = True
                    cluster_found = cluster
                    threshold = "0.6"
                    break
            if not found:
                for cluster in cluster_data_0_5:
                    if selected_bacteria in cluster:
                        found = True
                        cluster_found = cluster
                        threshold = "0.5"
                        break

            if found:
                cleaned_cluster = [s.replace("s__", "") for s in cluster_found]
                return JsonResponse({
                    "found": True,
                    "threshold": threshold,
                    "cluster_members": cleaned_cluster,
                })
            else:
                return JsonResponse({"found": False})


        # ----- Common filters (only for branches that need tissue) -----
        # Common filters
        tissue = request.GET.get('tissue')
        if tissue is None:
            return J({'error': 'Missing tissue.'}, status=400)
        # base_tissue_q = Q(from_tissue=tissue) | Q(to_tissue=tissue)
        # here tissue is otu to adapat for each case
        base_tissue_q = Q(from_tissue='functionnal') & Q(to_tissue=tissue)

        # (B) Single-var filtering
        if ('multi_variable' not in request.GET
                and 'table_filter' not in request.GET
                and 'cluster_lookup' not in request.GET
                and 'explore_table_filter' not in request.GET
                and 'explore_distribution' not in request.GET):
            var = request.GET.get('variable')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = FunctionnalCorrelation.objects.filter(
                base_tissue_q,
                var2=var,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({'results': [], 'total_count': 0})
            top = filt.order_by('-correlation')[:100]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count})

        # (C) Multi-var filtering
        if 'multi_variable' in request.GET:
            variables = request.GET.getlist('variables[]')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = FunctionnalCorrelation.objects.filter(
                base_tissue_q,
                var2__in=variables,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({'results': [], 'total_count': 0})
            top = filt.order_by('-correlation')[:100]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count})



        # (E) Table Filtering
        if 'table_filter' in request.GET:
            var = request.GET.get('variable')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = FunctionnalCorrelation.objects.filter(
                base_tissue_q,
                var2=var,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({
                    'results': [],
                    'total_count': 0,
                    'overview': {'median': None, 'q1': None, 'q3': None}
                })
            top = filt.order_by('-correlation')[:200]

            results = []
            vals = [o.correlation for o in filt]
            overview = {
                'median': r3(np.median(vals)),
                'q1': r3(np.quantile(vals, 0.25)),
                'q3': r3(np.quantile(vals, 0.75)),
            }
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'Coefficient': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count, 'overview': overview})

        # (F) Explore distribution
        if 'explore_distribution' in request.GET:
            # qs = MuscleCorrelation.objects.filter(base_tissue_q).values_list('correlation', flat=True)
            qs = (FunctionnalCorrelation.objects
                 .filter(base_tissue_q, correlation__isnull=False)
                 .values_list('correlation', flat=True)
                )
            series = list(qs)
            if not series:
                return J({'error': 'No data found.'}, status=400)
            stats = {
                'min': r3(min(series)),
                'q1': r3(np.quantile(series, 0.25)),
                'median': r3(np.median(series)),
                'q3': r3(np.quantile(series, 0.75)),
                'max': r3(max(series)),
            }
            return J({'distribution': {'correlation_values': series, 'stats': stats}})

        # (G) Explore table filter
        if 'explore_table_filter' in request.GET:
            try:
                corr_min = float(request.GET.get('corrMin', -1))
                corr_max = float(request.GET.get('corrMax', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = FunctionnalCorrelation.objects.filter(
                base_tissue_q,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            top = filt.order_by('-correlation')[:200]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            vals = [o.correlation for o in filt]
            overview = {
                'median': r3(np.median(vals)) if vals else None,
                'q1': r3(np.quantile(vals, 0.25)) if vals else None,
                'q3': r3(np.quantile(vals, 0.75)) if vals else None,
            }
            return J({'results': results, 'total_count': total_count, 'overview': overview})

        return J({'error': 'No recognized AJAX action.'}, status=400)

    # --- Non-AJAX: Build sunbursts and context ---
    def clusters_to_df(data):
        rows = []
        for i, sublist in enumerate(data, start=1):
            cluster_name = f"Cluster {i}"
            for species in sublist:
                rows.append({"Cluster": cluster_name, "Species": species.replace("s__", ""), "Value": 1})
        return pd.DataFrame(rows)

    cluster_data_0_6 = [
        ['menaquinol-13 biosynthesis', 'menaquinol-12 biosynthesis', 'demethylmenaquinol-8 biosynthesis I',
         'demethylmenaquinol-9 biosynthesis', 'demethylmenaquinol-6 biosynthesis I',
         'menaquinol-11 biosynthesis', 'demethylmenaquinol-4 biosynthesis', 'menaquinol-10 biosynthesis',
         '&beta;-alanine biosynthesis II', 'menaquinol-7 biosynthesis', 'assimilatory sulfate reduction II',
         'assimilatory sulfate reduction III'],
        ['Bifidobacterium shunt', 'L-serine biosynthesis I', 'protein Pupylation and dePupylation',
         'Bifidobacterium shunt II', 'polyphosphate metabolism', 'isoniazid activation',
         'NAD phosphorylation and dephosphorylation',
         'felinine and 3-methyl-3-sulfanylbutan-1-ol biosynthesis'],
        ['fructose 2,6-bisphosphate biosynthesis', 'formate oxidation to CO2', 'glycerol degradation I',
         '3-dehydroquinate biosynthesis II (archaea)', 'nitrate reduction V (assimilatory)',
         'pyrimidine deoxyribonucleotide phosphorylation', 'L-alanine biosynthesis I',
         'D-myo-inositol (1,4,5)-trisphosphate biosynthesis'],
        ['CDP-diacylglycerol biosynthesis III', 'tRNA splicing I', 'isoprene biosynthesis II (engineered)',
         'adenine and adenosine salvage II', 'nitric oxide biosynthesis I (plants)',
         'mevalonate pathway I (eukaryotes and bacteria)', 'acyl carrier protein activation',
         'mevalonate pathway IV (archaea)'],
        ['2-aminoethylphosphonate biosynthesis', 'nitrate reduction IV (dissimilatory)',
         'GDP-6-deoxy-D-altro-heptose biosynthesis', 'Oxidase test', 'hexaprenyl diphosphate biosynthesis',
         'D-sorbitol degradation I', 'glycerol-3-phosphate shuttle'],
        ['trehalose degradation VI (periplasmic)', 'Extracellular starch(27n) degradation',
         '(S)-lactate fermentation to propanoate', 'L-threonine degradation V',
         'trehalose degradation II (cytosolic)', 'C4 photosynthetic carbon assimilation cycle, NAD-ME type',
         '2-aminoethylphosphonate degradation II'],
        ['putrescine degradation V', "S-methyl-5'-thioadenosine degradation III",
         '&beta;-alanine degradation I', 'Electron bifurcating LDH/Etf complex', 'acrylonitrile degradation II',
         'indole-3-acetate biosynthesis V (bacteria and fungi)'],
        ['trehalose degradation V', 'acetate and ATP formation from acetyl-CoA II',
         '8-amino-7-oxononanoate biosynthesis III', 'trehalose degradation IV',
         'UDP-N-acetyl-&alpha;-D-mannosaminouronate biosynthesis',
         'L-tryptophan degradation II (via pyruvate)'],
        ['phytol degradation', 'lactose and galactose degradation I',
         'poly(glycerol phosphate) wall teichoic acid biosynthesis', 'NADH:menaquinone6 oxidoreductase',
         '2-carboxy-1,4-naphthoquinol biosynthesis', 'terminal olefins biosynthesis I'],
        ['L-phenylalanine degradation III', 'trehalose degradation III', 'phosphatidylcholine biosynthesis I',
         'acetaldehyde biosynthesis II', 'maltose degradation', 'oxalate degradation II'],
        ['UDP-N-acetylmuramoyl-pentapeptide biosynthesis II (lysine-containing)',
         'UDP-N-acetylmuramoyl-pentapeptide biosynthesis I (meso-diaminopimelate containing)',
         'arginine deiminase test', 'peptidoglycan biosynthesis I (meso-diaminopimelate containing)',
         'flavin salvage', 'peptidoglycan cross-bridge biosynthesis II (E. faecium)'],
        ['cyclobis-(1&rarr;6)-&alpha;-nigerosyl degradation',
         'ABH and Lewis epitopes biosynthesis from type 2 precursor disaccharide',
         'biosynthesis of Lewis epitopes (H. pylori)',
         'ABH and Lewis epitopes biosynthesis from type 1 precursor disaccharide', 'glycolipid desaturation'],
        ['oleate biosynthesis IV (anaerobic)', 'thiamine diphosphate biosynthesis I (E. coli)',
         'octaprenyl diphosphate biosynthesis', 'thiamine diphosphate biosynthesis II (Bacillus)',
         'nonaprenyl diphosphate biosynthesis I'],
        ['flavonol acylglucoside biosynthesis II - isorhamnetin derivatives',
         'flavonol acylglucoside biosynthesis I - kaempferol derivatives', 'phytochromobilin biosynthesis',
         'flavonol acylglucoside biosynthesis III - quercetin derivatives',
         'kaempferide triglycoside biosynthesis'],
        ['trigonelline biosynthesis', 'polymyxin A biosynthesis', 'glycerophosphodiester degradation',
         'putrescine degradation III', 'serotonin degradation'],
        ['tetradecanoate biosynthesis (mitochondria)', 'anteiso-branched-chain fatty acid biosynthesis',
         'even iso-branched-chain fatty acid biosynthesis',
         'octanoyl-[acyl-carrier protein] biosynthesis (mitochondria, yeast)',
         'odd iso-branched-chain fatty acid biosynthesis'],
        ['D-erythronate degradation I', 'phosphatidylserine and phosphatidylethanolamine biosynthesis I',
         'thiazole component of thiamine diphosphate biosynthesis I', 'adenosine nucleotides degradation III',
         'L-tryptophan degradation IV (via indole-3-lactate)'],
        ['triclosan resistance', 'CMP phosphorylation', 'ppGpp metabolism',
         'guanosine ribonucleotides de novo biosynthesis', 'UTP and CTP de novo biosynthesis'],
        ['archaeosine biosynthesis I', 'L-rhamnose degradation II',
         'ubiquinol-8 biosynthesis (early decarboxylation)', 'L-rhamnose degradation III',
         'poly-hydroxy fatty acids biosynthesis'],
        ['Bile acid 7alpha-dehydroxylation', 'Inulin degradation(11xFru,1xGlc) (extracellular)',
         'iso-bile acids biosynthesis (NADH or NADPH dependent)',
         'L-Tyrosine degradation to 4-hydroxyphenylacetate via tyramine', 'Ljungdahl-Wood pathway (gapseq)'],
        ['folate transformations III (E. coli)', 'D-galactose detoxification', 'L-histidine degradation VI',
         'L-histidine degradation III', 'L-alanine degradation II (to D-lactate)'],
        ['purine deoxyribonucleosides degradation I', '4-deoxy-L-threo-hex-4-enopyranuronate degradation',
         'L-homocysteine biosynthesis', 'adenine and adenosine salvage III',
         'purine deoxyribonucleosides degradation II']]

    cluster_data_0_5 = [
        ['menaquinol-13 biosynthesis', 'menaquinol-12 biosynthesis', 'demethylmenaquinol-8 biosynthesis I',
         'demethylmenaquinol-9 biosynthesis', 'demethylmenaquinol-6 biosynthesis I',
         'menaquinol-11 biosynthesis', 'demethylmenaquinol-4 biosynthesis', 'menaquinol-10 biosynthesis',
         '&beta;-alanine biosynthesis II', 'menaquinol-7 biosynthesis', 'assimilatory sulfate reduction II',
         'assimilatory sulfate reduction III'],
        ['CDP-diacylglycerol biosynthesis III', 'tRNA splicing I', 'isoprene biosynthesis II (engineered)',
         'vancomycin resistance I', 'adenine and adenosine salvage II', 'nitric oxide biosynthesis I (plants)',
         'mevalonate pathway I (eukaryotes and bacteria)', 'L-lysine biosynthesis II', 'citrate degradation',
         'acyl carrier protein activation', 'mevalonate pathway IV (archaea)'],
        ['D-erythronate degradation I', 'octaprenyl diphosphate biosynthesis',
         'thiamine diphosphate biosynthesis II (Bacillus)',
         'L-tryptophan degradation IV (via indole-3-lactate)',
         'phosphatidylserine and phosphatidylethanolamine biosynthesis I', 'oleate biosynthesis IV (anaerobic)',
         'thiazole component of thiamine diphosphate biosynthesis I',
         'thiamine diphosphate biosynthesis I (E. coli)', 'adenosine nucleotides degradation III',
         'nonaprenyl diphosphate biosynthesis I'],
        ['hydrogen to dimethyl sulfoxide electron transfer', 'carbon tetrachloride degradation II',
         'L-isoleucine biosynthesis III', 'CDP-D-arabitol biosynthesis',
         'L-arginine degradation XIII (reductive Stickland reaction)', 'acetylene degradation (anaerobic)',
         'reductive acetyl coenzyme A pathway I (homoacetogenic bacteria)',
         'L-asparagine degradation III (mammalian)', 'methanogenesis from acetate',
         '&beta;-1,4-D-mannosyl-N-acetyl-D-glucosamine degradation'],
        ['heme b biosynthesis IV (Gram-positive bacteria)',
         'benzimidazolyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP',
         '2-carboxy-1,4-naphthoquinol biosynthesis', 'NADH:menaquinone6 oxidoreductase',
         'terminal olefins biosynthesis I', 'lactose and galactose degradation I', 'cinnamoyl-CoA biosynthesis',
         'L-Fucose degradation (non-phosphorylating)',
         'poly(glycerol phosphate) wall teichoic acid biosynthesis', 'phytol degradation'],
        ['fructose 2,6-bisphosphate biosynthesis', 'formate oxidation to CO2', 'glycerol degradation I',
         '3-dehydroquinate biosynthesis II (archaea)', 'nitrate reduction V (assimilatory)',
         'pyrimidine deoxyribonucleotide phosphorylation', 'ulvan degradation',
         'phosphatidylinositol biosynthesis I (bacteria)', 'L-alanine biosynthesis I',
         'D-myo-inositol (1,4,5)-trisphosphate biosynthesis'],
        ['L-arginine degradation IV (arginine decarboxylase/agmatine deiminase pathway)',
         'Agmatine extracellular biosynthesis', 'NADH to cytochrome bd oxidase electron transfer I',
         'adenine and adenosine salvage I', 'NADH to cytochrome bo oxidase electron transfer II',
         'NADH to cytochrome bd oxidase electron transfer II', 'sulfate activation for sulfonation',
         'folate transformations II (plants)', 'NADH to cytochrome bo oxidase electron transfer I',
         'putrescine biosynthesis II'],
        ['4-hydroxyphenylacetate degradation', 'anthranilate degradation III (anaerobic)',
         'phenylethylamine degradation I', '1,4-dichlorobenzene degradation', '4-hydroxymandelate degradation',
         'orthanilate degradation', '1,2-dichloroethane degradation', '4-toluenecarboxylate degradation',
         '2-oxobutanoate degradation II'], ['trehalose biosynthesis III', 'toluene degradation to benzoate',
                                            'diacylglycerol and triacylglycerol biosynthesis',
                                            'toluene degradation to 2-hydroxypentadienoate (via 4-methylcatechol)',
                                            'toluene degradation to 4-methylphenol',
                                            'toluene degradation to 2-hydroxypentadienoate I (via o-cresol)',
                                            'trehalose biosynthesis I',
                                            'toluene degradation to 2-hydroxypentadienoate (via toluene-cis-diol)'],
        ['Bifidobacterium shunt', 'L-serine biosynthesis I', 'protein Pupylation and dePupylation',
         'Bifidobacterium shunt II', 'polyphosphate metabolism', 'isoniazid activation',
         'NAD phosphorylation and dephosphorylation',
         'felinine and 3-methyl-3-sulfanylbutan-1-ol biosynthesis'],
        ['roseoflavin biosynthesis', 'nitric oxide biosynthesis III (bacteria)',
         'coenzyme B/coenzyme M regeneration III (coenzyme F420-dependent)',
         'coenzyme B/coenzyme M regeneration II (ferredoxin-dependent)', 'jasmonoyl-L-isoleucine inactivation',
         'D-altritol and galactitol degradation', 'N-hydroxy-L-pipecolate biosynthesis',
         'coenzyme B/coenzyme M regeneration IV (H2-dependent)'],
        ['bacteriochlorophyll e biosynthesis', '3-hydroxy-4-methyl-anthranilate biosynthesis II',
         'bacteriochlorophyll c biosynthesis', 'phosalacine biosynthesis',
         'NAD salvage pathway II (PNC IV cycle)', 'L-leucine degradation IV (reductive Stickland reaction)',
         'chlorophyll a biosynthesis III', 'bacteriochlorophyll b biosynthesis'],
        ['N-cyclopropylmelamine degradation', 'lactucaxanthin biosynthesis',
         'capsanthin and capsorubin biosynthesis', 'coumarin biosynthesis (via 2-coumarate)',
         'factor 430 biosynthesis', 'artemisinin and arteannuin B biosynthesis',
         'factor 420 biosynthesis II (mycobacteria)', 'lactate biosynthesis (archaea)'],
        ['L-phenylalanine degradation III', 'trehalose degradation III', 'phosphatidylcholine biosynthesis I',
         "inosine-5'-phosphate biosynthesis I", 'acetaldehyde biosynthesis II', 'maltose degradation',
         'NAD phosphorylation and transhydrogenation', 'oxalate degradation II'],
        ['thymine degradation', 'sulfoacetate degradation', 'L-lysine degradation VI',
         'uracil degradation I (reductive)', 'homotaurine degradation',
         "cytidine-5'-diphosphate-glycerol biosynthesis", 'yersiniabactin biosynthesis'],
        ['4-hydroxy-2-nonenal detoxification', 'furcatin degradation',
         'ceramide and sphingolipid recycling and degradation (yeast)', 'chitin deacetylation',
         'megalomicin A biosynthesis', 'erythromycin A biosynthesis',
         'tea aroma glycosidic precursor bioactivation'],
        ['saframycin A biosynthesis', 'aureobasidin A biosynthesis', 'fusaridione A biosynthesis',
         'apicidin biosynthesis', 'apicidin F biosynthesis', 'galactolipid biosynthesis II',
         'equisetin biosynthesis'],
        ['CDP-6-deoxy-D-gulose biosynthesis', 'cell-surface glycoconjugate-linked phosphonate biosynthesis',
         'chlorophyll b2 biosynthesis', 'biotin biosynthesis from 8-amino-7-oxononanoate III',
         'bile acid 7&beta;-dehydroxylation', "5'-deoxyadenosine degradation II", 'NADPH repair (eukaryotes)'],
        ['bassianin and desmethylbassianin biosynthesis', '3,6-anhydro-&alpha;-L-galactopyranose degradation',
         'arginomycin biosynthesis', 'aspyridone A biosynthesis', 'ferrichrome A biosynthesis',
         'blasticidin S biosynthesis', 'bacimethrin and bacimethrin pyrophosphate biosynthesis'],
        ['L-arginine degradation II (AST pathway)', 'Calvin-Benson-Bassham cycle',
         'glycine betaine biosynthesis I (Gram-negative bacteria)',
         'L-phenylalanine degradation II (anaerobic)', 'L-arginine degradation VIII (arginine oxidase pathway)',
         'ammonia oxidation I (aerobic)', 'L-arginine degradation VII (arginase 3 pathway)'],
        ['yatein biosynthesis I', 'p-HBAD biosynthesis', 'diphenyl ethers degradation',
         "(-)-4'-demethyl-epipodophyllotoxin biosynthesis", 'mycobacterial sulfolipid biosynthesis',
         'carbon monoxide oxidation to CO2', 'dimycocerosyl phthiocerol biosynthesis'],
        ['mevalonate degradation', 'glycogen biosynthesis II (from UDP-D-Glucose)', 'L-leucine degradation II',
         'gibberellin biosynthesis I (non C-3, non C-13 hydroxylation)', 'L-isoleucine degradation II',
         'chlorophyll cycle', 'L-leucine degradation III'],
        ['abscisic acid biosynthesis', 'L-ascorbate degradation V', 'methanol oxidation to formaldehyde I',
         'methylamine degradation II', 'methylamine degradation I', 'L-ascorbate degradation III',
         'L-ascorbate degradation II (bacterial, aerobic)'],
        ["2,2'-dihydroxyketocarotenoids biosynthesis", "abscisic acid degradation to 7'-hydroxyabscisate",
         'abscisic acid degradation to neophaseic acid', '5-hexynoate biosynthesis',
         'echinenone and zeaxanthin biosynthesis (Synechocystis)',
         'bis(guanylyl molybdenum cofactor) biosynthesis', 'astaxanthin biosynthesis (flowering plants)'],
        ['calonectrin biosynthesis', 'penicillin G and penicillin V biosynthesis',
         '3-hydroxy-4-methyl-anthranilate biosynthesis I', 'nivalenol biosynthesis',
         'FeMo cofactor biosynthesis', 'deoxynivalenol biosynthesis',
         'harzianum A and trichodermin biosynthesis'],
        ['D-apiose degradation I', 'D-apionate degradation II (RLP decarboxylase)',
         '(S)-lactate fermentation to propanoate, acetate and hydrogen', 'indole-3-acetate degradation II',
         'D-apionate degradation III (RLP transcarboxylase/hydrolase)', 'dipicolinate biosynthesis',
         'D-apionate degradation I (xylose isomerase family decarboxylase)'],
        ['2-aminoethylphosphonate biosynthesis', 'nitrate reduction IV (dissimilatory)',
         'GDP-6-deoxy-D-altro-heptose biosynthesis', 'Oxidase test', 'hexaprenyl diphosphate biosynthesis',
         'D-sorbitol degradation I', 'glycerol-3-phosphate shuttle'],
        ['heme degradation V', 'heme degradation VII',
         '6-hydroxymethyl-dihydropterin diphosphate biosynthesis V (Pyrococcus)',
         '6-hydroxymethyl-dihydropterin diphosphate biosynthesis IV (Plasmodium)', 'heme degradation VI',
         'urate conversion to allantoin III', 'taurine biosynthesis II'],
        ['hyoscyamine and scopolamine biosynthesis', 'gentiodelphin biosynthesis', 'calystegine biosynthesis',
         'N-methyl-&Delta;1-pyrrolinium cation biosynthesis', 'L-lysine degradation VII',
         'nicotine biosynthesis', 'L-lysine degradation VIII'],
        ['&alpha;-cyclopiazonate biosynthesis', 'heme d1 biosynthesis', '(-)-microperfuranone biosynthesis',
         'prodigiosin biosynthesis', 'ergothioneine biosynthesis II (fungi)',
         'heme b biosynthesis III (from siroheme)', 'asperlicin E biosynthesis'],
        ['D-sorbitol degradation II', '6-hydroxymethyl-dihydropterin diphosphate biosynthesis I',
         '4-methylphenyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP',
         'allantoin degradation to ureidoglycolate II (ammonia producing)',
         '6-hydroxymethyl-dihydropterin diphosphate biosynthesis III (Chlamydia)',
         'glycolate and glyoxylate degradation I',
         'phenyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP'],
        ['staphyloferrin B biosynthesis', 'plant arabinogalactan type II degradation',
         'L-cysteine biosynthesis IX (Trichomonas vaginalis)',
         'L-cysteine biosynthesis VIII (Thermococcus kodakarensis)', 'staphylopine biosynthesis',
         '4-coumarate degradation (aerobic)', 'trans-caffeate degradation (aerobic)'],
        ['Ferredoxin:NAD+ oxidoreductase', 'D-fructuronate degradation', '(S)-propane-1,2-diol degradation',
         'glycerol degradation III', 'S-methyl-L-methionine cycle', 'Entner-Doudoroff shunt',
         'xylitol degradation'],
        ['trehalose degradation VI (periplasmic)', 'Extracellular starch(27n) degradation',
         '(S)-lactate fermentation to propanoate', 'L-threonine degradation V',
         'trehalose degradation II (cytosolic)', 'C4 photosynthetic carbon assimilation cycle, NAD-ME type',
         '2-aminoethylphosphonate degradation II'],
        ['anandamide degradation', '2-heptyl-3-hydroxy-4(1H)-quinolone biosynthesis', 'dopamine degradation',
         'pyocyanin biosynthesis', 'pterostilbene biosynthesis', 'di-myo-inositol phosphate biosynthesis'],
        ['L-lysine degradation V', 'sulfite oxidation III', 'sulfite oxidation II', 'L-lysine degradation IV',
         'sulfide oxidation III (to sulfite)', 'shisonin biosynthesis'],
        ['protein O-glycosylation (Neisseria)', 'alkane biosynthesis II', 'alkane biosynthesis I',
         'protein N-glycosylation (bacterial)', '(9Z)-tricosene biosynthesis',
         'very long chain fatty acid biosynthesis II'],
        ['nerol biosynthesis', 'geraniol biosynthesis (cytosol)', 'acrylate degradation II',
         'platensimycin biosynthesis', '2-methyl-branched fatty acid &beta;-oxidation',
         '10-methylstearate biosynthesis'],
        ['methanogenesis from glycine betaine', 'glycine betaine degradation III',
         'proline betaine degradation II', 'L-dopa degradation II (bacterial)', 'kavain biosynthesis',
         'yangonin biosynthesis'],
        ['2-deoxy-D-glucose 6-phosphate degradation', '&beta;-alanine degradation III',
         'mycofactocin biosynthesis', 'microcin B17 biosynthesis',
         '(2-trimethylamino)ethylphosphonate degradation', 'chlorophyll a2 biosynthesis'],
        ['brassinosteroid biosynthesis II', 'benzoate degradation I (aerobic)', '(+)-pisatin biosynthesis',
         'fatty acid &alpha;-oxidation I (plants)', 'phytosterol biosynthesis (plants)',
         'medicarpin conjugates interconversion'],
        ['hinokiresinol biosynthesis', 'kievitone detoxification', 'vernolate biosynthesis II',
         'hinokinin biosynthesis', 'arctigenin and isoarctigenin biosynthesis',
         'calycosin 7-O-glucoside biosynthesis'],
        ['&beta; myrcene degradation', 'sesaminol glucoside biosynthesis',
         'myricetin gentiobioside biosynthesis', 'quercetin gentiotetraside biosynthesis',
         'emetine biosynthesis', 'noscapine biosynthesis'],
        ['zealexin biosynthesis', 'thiamine diphosphate salvage III', 'thiamine diphosphate salvage I',
         'thiazole component of thiamine diphosphate biosynthesis II', 'isopropanol biosynthesis (engineered)',
         'retinoate biosynthesis II'], ['(R)- and (S)-3-hydroxybutanoate biosynthesis (engineered)',
                                        'ubiquinol-6 biosynthesis from 4-aminobenzoate (yeast)',
                                        'nicotinate degradation I',
                                        'baicalein degradation (hydrogen peroxide detoxification)',
                                        'gibberellin biosynthesis V', 'purine deoxyribonucleosides salvage'],
        ['sapienate biosynthesis', 'tetrathionate reduction I (to thiosulfate)', 'chrysin biosynthesis',
         '(5Z)-icosenoate biosynthesis', 'tetrathionate reductiuon II (to trithionate)',
         'linear furanocoumarin biosynthesis'],
        ['leucodelphinidin biosynthesis', 'trans-4-hydroxy-L-proline degradation II',
         "6'-deoxychalcone metabolism", 'anthocyanin biosynthesis (delphinidin 3-O-glucoside)',
         'L-tyrosine degradation II', 'rose anthocyanin biosynthesis I (via cyanidin 5-O-&beta;-D-glucoside)'],
        ['arsenate reduction (respiratory)',
         '1D-myo-inositol hexakisphosphate biosynthesis III (Spirodela polyrrhiza)',
         'arsenite oxidation I (respiratory)', 'wighteone and luteone biosynthesis',
         'arsenate detoxification II (glutaredoxin)', 'kievitone biosynthesis'],
        ['pyruvate fermentation to opines', 'daunorubicin biosynthesis', 'sucrose biosynthesis III',
         'thiamine phosphate formation from pyrithiamine and oxythiamine (yeast)', 'aclacinomycin biosynthesis',
         'doxorubicin biosynthesis'],
        ['IM-2 type &gamma;-butyrolactones biosynthesis', 'D-erythronate degradation II',
         'D-threonate degradation', 'virginiae butanolide type &gamma;-butyrolactones biosynthesis',
         'coelimycin P1 biosynthesis', 'A-factor &gamma;-butyrolactone biosynthesis'],
        ['lupanine biosynthesis', 'bisbenzylisoquinoline alkaloid biosynthesis',
         'hydroxycinnamic acid serotonin amides biosynthesis', 'palmatine biosynthesis',
         'hydroxycinnamic acid tyramine amides biosynthesis', 'sesamin biosynthesis'],
        ['nepetalactone biosynthesis', '(Kdo)2-lipid A biosynthesis II (P. putida)',
         'methylphosphonate biosynthesis', 'methylphosphonate degradation III',
         'N-3-oxalyl-L-2,3-diaminopropanoate biosynthesis',
         '8-O-methylated benzoxazinoid glucoside biosynthesis'],
        ['willardiine and isowillardiine biosynthesis', 'tetrahydroxyxanthone biosynthesis (from benzoate)',
         'UDP-&alpha;-D-galacturonate biosynthesis II (from D-galacturonate)',
         'indole-3-acetate biosynthesis IV (bacteria)', 'L-arginine degradation XI',
         'tetrahydroxyxanthone biosynthesis (from 3-hydroxybenzoate)'],
        ['cob(II)yrinate a,c-diamide biosynthesis II (late cobalt incorporation)',
         'urate conversion to allantoin II', 'aminopropanol phosphate biosynthesis II',
         'lipoate biosynthesis and incorporation IV (yeast)', 'mRNA capping I',
         'cob(II)yrinate a,c-diamide biosynthesis I (early cobalt insertion)'],
        ['group E Salmonella O antigen biosynthesis', 'group D2 Salmonella O antigen biosynthesis',
         'group A Salmonella O antigen biosynthesis', 'group D1 Salmonella O antigen biosynthesis',
         'group C2 Salmonella O antigen biosynthesis', 'toluene degradation to benzoyl-CoA (anaerobic)'],
        ['starch degradation II', 'candicidin biosynthesis', 'methylhalides biosynthesis (plants)',
         'methylaspartate cycle', 'sangivamycin biosynthesis', 'toyocamycin biosynthesis'],
        ['plasmalogen degradation', 'butane degradation', 'methyl tert-butyl ether degradation',
         '&omega;-sulfo-II-dihydromenaquinone-9 biosynthesis', 'plasmalogen biosynthesis',
         '2-methylpropene degradation'],
        ['o-diquinones biosynthesis', 'methane oxidation to methanol II', 'pinitol biosynthesis I',
         'pinitol biosynthesis II', "S-methyl-5'-thioadenosine degradation I",
         'nitrate reduction VII (denitrification)'],
        ['thiocoraline biosynthesis', 'echinomycin and triostin A biosynthesis',
         'quinoxaline-2-carboxylate biosynthesis', 'stellatic acid biosynthesis',
         '3-hydroxyquinaldate biosynthesis', 'T-2 toxin biosynthesis'],
        ['putrescine biosynthesis III', 'creatinine degradation II', 'phytate degradation I',
         'creatinine degradation III', 'phytate degradation II', 'aloesone biosynthesis I'],
        ['&beta;-D-mannosyl phosphomycoketide biosynthesis', 'aucuparin biosynthesis',
         'phthiocerol biosynthesis', 'polyacyltrehalose biosynthesis', 'phenolphthiocerol biosynthesis',
         'dimycocerosyl triglycosyl phenolphthiocerol biosynthesis'],
        ['5-(methoxycarbonylmethoxy)uridine biosynthesis', 'methylphosphonate degradation I',
         'proline to cytochrome bo oxidase electron transfer',
         'D-lactate to cytochrome bo oxidase electron transfer', 'cardiolipin biosynthesis III',
         'muropeptide degradation'], ['methanogenesis from methylamine', 'soybean saponin I biosynthesis',
                                      'coenzyme B/coenzyme M regeneration I (methanophenazine-dependent)',
                                      'methanogenesis from dimethylamine', 'methyl-coenzyme M oxidation to CO2',
                                      'factor 420 polyglutamylation'],
        ['flavin-N5-oxide biosynthesis', '2-deoxy-D-ribose degradation II', '8-oxo-(d)GTP detoxification II',
         'chlorpyrifos degradation', 'pyruvoyl group formation from L-serine', 'sodorifen biosynthesis'],
        ['p-cumate degradation to 2-hydroxypentadienoate', 'melamine degradation',
         'ferulate and sinapate biosynthesis', '4-toluenesulfonate degradation II',
         'cyanuric acid degradation II', '2-hydroxypenta-2,4-dienoate degradation'],
        ['adenosylcobinamide-GDP salvage from cobinamide II', 'N-methylpyrrolidone degradation',
         'adenosylcobalamin biosynthesis from adenosylcobinamide-GDP II',
         'protein O-mannosylation III (mammals, core M3)', 'cobalamin salvage (eukaryotic)',
         'adenosylcobinamide-GDP salvage from cobinamide I'],
        ['putrescine degradation V', "S-methyl-5'-thioadenosine degradation III",
         '&beta;-alanine degradation I', 'Electron bifurcating LDH/Etf complex', 'acrylonitrile degradation II',
         'indole-3-acetate biosynthesis V (bacteria and fungi)'],
        ['caffeine biosynthesis II (via paraxanthine)', 'theobromine biosynthesis I', 'GA12 biosynthesis',
         'gibberellin biosynthesis II (early C-3 hydroxylation)', 'caffeine biosynthesis I',
         'gibberellin biosynthesis III (early C-13 hydroxylation)'],
        ["6'-dechloromelleolide F biosynthesis", 'pheomelanin biosynthesis', 'firefly bioluminescence',
         'coral bioluminescence', 'dinoflagellate bioluminescence', 'jellyfish bioluminescence'],
        ['resolvin D biosynthesis', 'homocarnosine biosynthesis', 'aspirin triggered resolvin E biosynthesis',
         'carnosine biosynthesis', 'aspirin triggered resolvin D biosynthesis', 'salicylate degradation IV'],
        ['trehalose degradation V', 'acetate and ATP formation from acetyl-CoA II',
         '8-amino-7-oxononanoate biosynthesis III', 'trehalose degradation IV',
         'UDP-N-acetyl-&alpha;-D-mannosaminouronate biosynthesis',
         'L-tryptophan degradation II (via pyruvate)'],
        ['cephamycin C biosynthesis', '2-nitrophenol degradation', '2,4-dinitrotoluene degradation',
         'nitrobenzene degradation II', '2-nitrotoluene degradation', 'nitrobenzene degradation I'],
        ['thiamine diphosphate biosynthesis III (Staphylococcus)',
         'thiazole component of thiamne diphosphate biosynthesis III', '(Z)-butanethial-S-oxide biosynthesis',
         'chitin derivatives degradation', 'thiamine diphosphate biosynthesis IV (eukaryotes)',
         'base-degraded thiamine salvage'],
        ['sitosterol degradation to androstenedione', 'lincomycin A biosynthesis',
         'DIBOA-glucoside biosynthesis', 'DIMBOA-glucoside biosynthesis',
         'dTDP-3-acetamido-&alpha;-D-fucose biosynthesis',
         'icosapentaenoate biosynthesis I (lower eukaryotes)'],
        ['procollagen hydroxylation and glycosylation', 'protein SAMPylation and SAMP-mediated thiolation',
         'tRNA-uridine 2-thiolation (yeast mitochondria)', 'tRNA-uridine 2-thiolation (cytoplasmic)',
         'tRNA-uridine 2-thiolation (mammalian mitochondria)',
         'tRNA-uridine 2-thiolation and selenation (bacteria)'],
        ['nocardicin A biosynthesis', 'pentose phosphate pathway (oxidative branch) II',
         'dimethyl sulfide biosynthesis from methionine', 'terephthalate degradation',
         'protein S-nitrosylation and denitrosylation', 'Arg/N-end rule pathway (eukaryotic)'],
        ['2-fucosyllactose degradation', 'sulfate reduction I (assimilatory)', 'viscosin biosynthesis',
         'massetolide A biosynthesis', 'Lacto-N-tetraose degradation', 'L-valine degradation I'],
        ['D-sorbitol biosynthesis I', 'L-valine degradation II', 'luteolin biosynthesis',
         'pinobanksin biosynthesis', 'rosmarinic acid biosynthesis I', 'rosmarinic acid biosynthesis II'],
        ['sophorolipid biosynthesis', 'shikimate degradation I', 'thioredoxin pathway',
         'sophorosyloxydocosanoate deacetylation', 'sucrose degradation VII (sucrose 3-dehydrogenase)',
         'sphingolipid biosynthesis (yeast)'],
        ["pyridoxal 5'-phosphate salvage II (plants)", 'pyrimidine deoxyribonucleosides salvage',
         'quercetin diglycoside biosynthesis (pollen-specific)', 'pinocembrin C-glucosylation',
         'kaempferol diglycoside biosynthesis (pollen-specific)', 'UTP and CTP dephosphorylation I'],
        ['atromentin biosynthesis', '3-(4-sulfophenyl)butanoate degradation', 'terrequinone A biosynthesis',
         '(R)-canadine biosynthesis', 'brassicicene C biosynthesis', 'mevalonate pathway III (Thermoplasma)'],
        ['cutin biosynthesis', 'sinapate ester biosynthesis', 'canavanine degradation',
         'L-tryptophan degradation VI (via tryptamine)', 'UDP-&beta;-L-rhamnose biosynthesis',
         'choline biosynthesis I'],
        ['oleoresin monoterpene volatiles biosynthesis', 'naphthalene degradation (aerobic)',
         'betaxanthin biosynthesis', '1,3-dimethylbenzene degradation to 3-methylbenzoate',
         'isopimaric acid biosynthesis', 'oleoresin sesquiterpene volatiles biosynthesis'],
        ['UDP-N-acetylmuramoyl-pentapeptide biosynthesis II (lysine-containing)',
         'UDP-N-acetylmuramoyl-pentapeptide biosynthesis I (meso-diaminopimelate containing)',
         'arginine deiminase test', 'peptidoglycan biosynthesis I (meso-diaminopimelate containing)',
         'flavin salvage', 'peptidoglycan cross-bridge biosynthesis II (E. faecium)'],
        ['kanosamine biosynthesis II', 'CO2 fixation into oxaloacetate (anaplerotic)',
         'indole-3-acetate biosynthesis I', 'salicylate biosynthesis II', 'mycolate biosynthesis',
         'sulfoquinovosyl diacylglycerol biosynthesis'],
        ['pentaketide chromone biosynthesis', 'L-homomethionine biosynthesis', 'taurine degradation II',
         'phenylacetate degradation II (anaerobic)', 'benzoyl-CoA degradation I (aerobic)',
         'fluorene degradation II'],
        ['iso-bile acids biosynthesis II', 'gadusol biosynthesis', 'bacteriochlorophyll d biosynthesis',
         'shinorine biosynthesis', 'bile acid 7&alpha;-dehydroxylation', 'bisphenol A degradation'],
        ['biphenyl degradation', 'linoleate biosynthesis II (animals)', 'phthalate degradation (aerobic)',
         'gramicidin S biosynthesis', '&gamma;-linolenate biosynthesis II (animals)',
         'lotaustralin degradation'],
        ['phenylethanol glycoconjugate biosynthesis', 'N-acetyl-D-galactosamine degradation',
         '3,5-dimethoxytoluene biosynthesis', 'phenylethyl acetate biosynthesis', 'asterrate biosynthesis',
         'hopanoid biosynthesis (bacteria)'],
        ['tetramethylpyrazine degradation', 'aurachin A, B, C and D biosynthesis', 'aurachin RE biosynthesis',
         'phospholipid remodeling (phosphatidylethanolamine, yeast)',
         'ceramide phosphoethanolamine biosynthesis', 'methylphosphonate degradation II'],
        ['cycloartenol biosynthesis', 'epiberberine biosynthesis', 'coptisine biosynthesis',
         'sterol biosynthesis (methylotrophs)', 'limonene degradation IV (anaerobic)', 'parkeol biosynthesis'],
        ['N-glucosylnicotinate metabolism', 'methylglyoxal degradation VIII', 'NAD salvage (plants)',
         'rutin biosynthesis', 'methylglyoxal degradation I', '3-methylthiopropanoate biosynthesis'],
        ['divinyl ether biosynthesis II', 'traumatin and (Z)-3-hexen-1-yl acetate biosynthesis',
         '9-lipoxygenase and 9-allene oxide synthase pathway', 'abietic acid biosynthesis',
         'levopimaric acid biosynthesis', '9-lipoxygenase and 9-hydroperoxide lyase pathway'],
        ['erythromycin D biosynthesis', 'dTDP-&beta;-L-megosamine biosynthesis', '5-deoxystrigol biosynthesis',
         'bisabolene biosynthesis (engineered)', 'olivetol biosynthesis'],
        ['menaquinol-4 biosynthesis II', 'dolabralexins biosynthesis', 'tricin biosynthesis',
         'vitamin K degradation', 'vitamin K-epoxide cycle'],
        ['L-cysteine degradation I', 'cyclohexanol degradation', 'cyanate degradation',
         'nitrate reduction I (denitrification)', 'D-arabinose degradation II'],
        ['bacteriochlorophyll a biosynthesis', 'D-arabinose degradation III', 'D-glucuronate degradation I',
         'L-ascorbate biosynthesis III (D-sorbitol pathway)',
         '5,6-dimethylbenzimidazole biosynthesis I (aerobic)'],
        ['docosahexaenoate biosynthesis I (lower eukaryotes)',
         'icosapentaenoate biosynthesis II (6-desaturase, mammals)', '4-coumarate degradation (anaerobic)',
         'icosapentaenoate biosynthesis IV (bacteria)', 'cyanophycin metabolism'],
        ['(1,3)-&beta;-D-xylan degradation', 'xyloglucan degradation I (endoglucanase)',
         'cellulose degradation II (fungi)', 'flavonoid biosynthesis (in equisetum)', 'L-arabinan degradation'],
        ['3-(imidazol-5-yl)lactate salvage', 'L-histidine degradation V', 'nicotinate degradation II',
         'L-histidine degradation II', 'ent-kaurene biosynthesis I'],
        ['4-sulfocatechol degradation', 'ethanedisulfonate degradation', 'chlorogenic acid biosynthesis II',
         'methanesulfonate degradation', 'chlorogenic acid biosynthesis I'],
        ['homospermidine biosynthesis II', 'cholesterol degradation to androstenedione III (anaerobic)',
         'cytochrome c biogenesis (system I type)', 'cytochrome c biogenesis (system II type)',
         'androsrtendione degradation II (anaerobic)'],
        ['aliphatic glucosinolate biosynthesis, side chain elongation cycle',
         'glucosinolate biosynthesis from pentahomomethionine',
         'glucosinolate biosynthesis from trihomomethionine',
         'glucosinolate biosynthesis from dihomomethionine',
         'glucosinolate biosynthesis from tetrahomomethionine'],
        ['4-chloronitrobenzene degradation', '2-nitrobenzoate degradation II',
         'L-tryptophan degradation to 2-amino-3-carboxymuconate semialdehyde', '4-nitrotoluene degradation II',
         '2,6-dinitrotoluene degradation'],
        ['3,8-divinyl-chlorophyllide a biosynthesis III (aerobic, light independent)',
         'L-phenylalanine degradation V', 'polymethylated quercetin biosynthesis',
         'polymethylated myricetin biosynthesis (tomato)', '7-dehydroporiferasterol biosynthesis'],
        ['triclosan resistance', 'CMP phosphorylation', 'ppGpp metabolism',
         'guanosine ribonucleotides de novo biosynthesis', 'UTP and CTP de novo biosynthesis'],
        ['Spodoptera littoralis pheromone biosynthesis', 'dechlorogriseofulvin biosynthesis',
         '(8E,10E)-dodeca-8,10-dienol biosynthesis', 'dTDP-&beta;-L-digitoxose biosynthesis',
         'griseofulvin biosynthesis'],
        ['i antigen and I antigen biosynthesis', 'globo-series glycosphingolipids biosynthesis',
         'gala-series glycosphingolipids biosynthesis', 'lacto-series glycosphingolipids biosynthesis',
         'ganglio-series glycosphingolipids biosynthesis'],
        ['superoxide radicals degradation', 'chitin degradation II (Vibrio)', 'Catalase test',
         'ethanol degradation IV', 'L-arabinose degradation I'],
        ['dimethylsulfoniopropanoate biosynthesis III (algae and phytoplankton)',
         'dimethylsulfoniopropanoate biosynthesis II (Spartina)',
         'dimethylsulfoniopropanoate biosynthesis I (Wollastonia)',
         'dimethylsulfoniopropanoate degradation II (cleavage)',
         'dimethylsulfide to cytochrome c2 electron transfer'],
        ['branched-chain polyamines biosynthesis', 'carbaryl degradation',
         'factor 420 biosynthesis I (archaea)', '3PG-factor 420 biosynthesis',
         'long-chain polyamine biosynthesis'],
        ['indole-3-acetate inactivation IV', 'free phenylpropanoid acid biosynthesis',
         'glutamate removal from folates', 'isoflavonoid biosynthesis I', 'isoflavonoid biosynthesis II'],
        ["adenosine 5'-phosphoramidate biosynthesis", 'fatty acid biosynthesis initiation (plant mitochondria)',
         'diacylglyceryl-N,N,N-trimethylhomoserine biosynthesis', 'scopoletin biosynthesis',
         '6-hydroxymethyl-dihydropterin diphosphate biosynthesis II (Methanocaldococcus)'],
        ['galloylated catechin biosynthesis', 'anthocyanidin modification (Arabidopsis)',
         '2-aminoethylphosphonate degradation III', 'cyanidin dimalonylglucoside biosynthesis',
         'acylated cyanidin galactoside biosynthesis'], ['indole glucosinolate activation (intact plant cell)',
                                                         'glucosinolate biosynthesis from hexahomomethionine',
                                                         'NAD salvage pathway I (PNC VI cycle)',
                                                         'indole glucosinolate activation (herbivore attack)',
                                                         'quinate degradation I'],
        ['autoinducer CAI-1 biosynthesis', 'nystatin biosynthesis', 'naphthalene degradation (anaerobic)',
         'astaxanthin dirhamnoside biosynthesis', 'rhizobactin 1021 biosynthesis'],
        ['2-methyladeninyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP',
         '5-methoxy-6-methylbenzimidazolyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP',
         'rhabduscin biosynthesis', 'adeninyl adenosylcobamide biosynthesis from adenosylcobinamide-GDP',
         '12-epi-fischerindole biosynthesis'],
        ['nitroethane degradation', 'ajugose biosynthesis II (galactinol-independent)',
         'arachidonate biosynthesis I (6-desaturase, lower eukaryotes)', 'kaempferol triglucoside biosynthesis',
         'esculetin biosynthesis'],
        ['&gamma;-resorcylate degradation I', 'propane degradation I', 'butachlor degradation',
         '&gamma;-resorcylate degradation II', 'indolmycin biosynthesis'],
        ['paspaline biosynthesis', '3&beta;-hydroxysesquiterpene lactone biosynthesis', 'gossypetin metabolism',
         'linuron degradation', 'paxilline and diprenylpaxilline biosynthesis'],
        ['dTDP-&beta;-L-olivose biosynthesis', 'umbelliferone biosynthesis', 'plastoquinol-9 biosynthesis II',
         'dTDP-&beta;-L-mycarose biosynthesis', 'threo-tetrahydrobiopterin biosynthesis'],
        ['gliotoxin biosynthesis', 'lovastatin biosynthesis', 'aflatrem biosynthesis',
         'fumiquinazoline D biosynthesis', '1,2-propanediol biosynthesis from lactate (engineered)'],
        ['flavonol acylglucoside biosynthesis II - isorhamnetin derivatives',
         'flavonol acylglucoside biosynthesis I - kaempferol derivatives', 'phytochromobilin biosynthesis',
         'flavonol acylglucoside biosynthesis III - quercetin derivatives',
         'kaempferide triglycoside biosynthesis'],
        ['methyl phomopsenoate biosynthesis', 'ophiobolin F biosynthesis', 'bacterial bioluminescence',
         'sulfoquinovose degradation II', 'icosapentaenoate biosynthesis III (8-desaturase, mammals)'],
        ['pelargonidin diglucoside biosynthesis (acyl-glucose dependent)',
         'cyanidin diglucoside biosynthesis (acyl-glucose dependent)',
         'ergothioneine biosynthesis I (bacteria)', 'apigeninidin 5-O-glucoside biosynthesis',
         'luteolinidin 5-O-glucoside biosynthesis'],
        ['methylglyoxal degradation VII', 'matairesinol biosynthesis',
         'acetone degradation I (to methylglyoxal)', 'gramine biosynthesis', 'methylglyoxal degradation II'],
        ['anthocyanidin acylglucoside and acylsambubioside biosynthesis', '1-chloro-2-nitrobenzene degradation',
         'carnosate bioynthesis', 'arabidopyrone biosynthesis', 'nitrite reduction (hemoglobin)'],
        ['adamantanone degradation', 'phosphonoacetate degradation', 'arsonoacetate degradation',
         'incomplete reductive TCA cycle', '4-nitrotoluene degradation I'],
        ['&alpha;-carotene biosynthesis', '&beta;-carotene biosynthesis',
         'violaxanthin, antheraxanthin and zeaxanthin interconversion', 'zeaxanthin biosynthesis',
         'streptomycin biosynthesis'],
        ['palmitoleate biosynthesis III (cyanobacteria)', '(7Z,10Z,13Z)-hexadecatrienoate biosynthesis',
         'okenone biosynthesis', 'ursodeoxycholate biosynthesis (bacteria)',
         'linoleate biosynthesis III (cyanobacteria)'],
        ['archaeosine biosynthesis I', 'L-rhamnose degradation II',
         'ubiquinol-8 biosynthesis (early decarboxylation)', 'L-rhamnose degradation III',
         'poly-hydroxy fatty acids biosynthesis'],
        ['chaxamycin biosynthesis', 'spectinabilin biosynthesis', 'streptovaricin biosynthesis',
         'chloramphenicol biosynthesis', 'aureothin biosynthesis'],
        ['Bile acid 7alpha-dehydroxylation', 'Inulin degradation(11xFru,1xGlc) (extracellular)',
         'iso-bile acids biosynthesis (NADH or NADPH dependent)',
         'L-Tyrosine degradation to 4-hydroxyphenylacetate via tyramine', 'Ljungdahl-Wood pathway (gapseq)'],
        ['(3R)-linalool biosynthesis', 'viridicatin biosynthesis', 'lyngbyatoxin biosynthesis',
         "4'-methoxyviridicatin biosynthesis", 'dapdiamides biosynthesis'],
        ['purine deoxyribonucleosides degradation I', '4-deoxy-L-threo-hex-4-enopyranuronate degradation',
         'L-homocysteine biosynthesis', 'adenine and adenosine salvage III',
         'purine deoxyribonucleosides degradation II'],
        ['guanosine nucleotides degradation II', 'laminaribiose degradation',
         'adenosine nucleotides degradation I', 'guanosine nucleotides degradation III',
         'anhydromuropeptides recycling I'],
        ['betacyanin biosynthesis (via dopamine)', 'aminopropanol phosphate biosynthesis I',
         'benzene degradation', '1,4-dimethylbenzene degradation to 4-methylbenzoate',
         '(3E)-4,8-dimethylnona-1,3,7-triene biosynthesis I'],
        ['isorenieratene biosynthesis I (actinobacteria)', 'spongiadioxin C biosynthesis',
         'polybrominated dihydroxylated diphenyl ethers biosynthesis', 'fungal bioluminescence',
         'psilocybin biosynthesis'],
        ['L-valine degradation III (oxidative Stickland reaction)', 'valproate &beta;-oxidation',
         'L-isoleucine degradation III (oxidative Stickland reaction)',
         'L-alanine degradation VI (reductive Stickland reaction)',
         'L-leucine degradation V (oxidative Stickland reaction)'],
        ['spermine biosynthesis', 'L-arginine degradation III (arginine decarboxylase/agmatinase pathway)',
         'L-arginine degradation X (arginine monooxygenase pathway)', 'linezolid resistance',
         'putrescine biosynthesis I'],
        ['methyl ketone biosynthesis (engineered)', '4-amino-3-hydroxybenzoate degradation',
         '4-hydroxyacetophenone degradation', 'GDP-L-fucose biosynthesis II (from L-fucose)',
         'brassinosteroid biosynthesis I'], ['1,5-anhydrofructose degradation', '(-)-camphor biosynthesis',
                                             'nicotine degradation II (pyrrolidine pathway)',
                                             'L-pyrrolysine biosynthesis', '(+)-camphor biosynthesis'],
        ['naringenin glycoside biosynthesis', 'chlorophyll a degradation I',
         'L-glutamate degradation VI (to pyruvate)', 'L-methionine degradation III',
         'chlorophyll a biosynthesis I'],
        ['baumannoferrin biosynthesis', 'acinetobactin biosynthesis', 'anguibactin biosynthesis',
         'oxalate degradation VI', 'vanchrobactin biosynthesis'],
        ['rhizobitoxine biosynthesis', 'Escherichia coli serotype O9a O-antigen biosynthesis',
         'formaldehyde oxidation V (bacillithiol-dependent)', 'homofuraneol biosynthesis',
         '(2S,3E)-2-amino-4-methoxy-but-3-enoate biosynthesis'],
        ['apigenin glycosides biosynthesis', 'acyl carrier protein metabolism', 'baruol biosynthesis',
         '(3E)-4,8-dimethylnona-1,3,7-triene biosynthesis II', 'amygdalin and prunasin degradation'],
        ['glycolysis V (Pyrococcus)', 'benzoyl-CoA degradation III (anaerobic)', 'aldoxime degradation',
         'orcinol degradation', 'resorcinol degradation'],
        ['N6-L-threonylcarbamoyladenosine37-modified tRNA biosynthesis',
         'cyclopropane fatty acid (CFA) biosynthesis', 'D-gluconate degradation', 'fructose degradation',
         'L-threonine biosynthesis'],
        ['A series fagopyritols biosynthesis', '&alpha;-amyrin biosynthesis', 'punicate biosynthesis',
         'B series fagopyritols biosynthesis', '&alpha;-eleostearate biosynthesis'],
        ['sucrose biosynthesis II', 'myo-inositol degradation II', 'mycocyclosin biosynthesis',
         "inosine-5'-phosphate biosynthesis III", 'alkylnitronates degradation'],
        ['methanogenesis from tetramethylammonium', 'methanogenesis from methanethiol',
         'salvianin biosynthesis', 'methanogenesis from methylthiopropanoate', 'glucosinolate activation'],
        ['complex N-linked glycan biosynthesis (plants)', 'archaeosine biosynthesis II',
         'protein O-mannosylation II (mammals, core M1 and core M2)', 'rubber degradation I',
         'protein O-mannosylation I (yeast)'],
        ['hentriaconta-3,6,9,12,15,19,22,25,28-nonaene biosynthesis', 'paromamine biosynthesis II',
         'terminal olefins biosynthesis II', "UDP-N,N'-diacetylbacillosamine biosynthesis",
         'gentamicin biosynthesis'], ['cyclobis-(1&rarr;6)-&alpha;-nigerosyl degradation',
                                      'ABH and Lewis epitopes biosynthesis from type 2 precursor disaccharide',
                                      'biosynthesis of Lewis epitopes (H. pylori)',
                                      'ABH and Lewis epitopes biosynthesis from type 1 precursor disaccharide',
                                      'glycolipid desaturation'],
        ['nitrate reduction III (dissimilatory)', 'pyrimidine ribonucleosides degradation',
         'putrescine degradation II', 'protocatechuate degradation II (ortho-cleavage pathway)',
         'L-proline degradation I'],
        ["3,3'-thiodipropanoate degradation", 'cyanidin 3,7-diglucoside polyacylation biosynthesis',
         'N-methylanthraniloyl-&beta;-D-glucopyranose biosynthesis',
         "3,3'-disulfanediyldipropannoate degradation", '2-O-acetyl-3-O-trans-coutarate biosynthesis'],
        ['trigonelline biosynthesis', 'polymyxin A biosynthesis', 'glycerophosphodiester degradation',
         'putrescine degradation III', 'serotonin degradation'],
        ['hydrogen production VI', 'salicin biosynthesis', 'rhamnogalacturonan type I degradation I',
         "4,4'-diapolycopenedioate biosynthesis", 'hydrogen production V'],
        ['quercetin glucoside biosynthesis (Allium)', 'rutin degradation (plants)',
         'quercetin glucoside degradation (Allium)', 'L-glucose degradation',
         'CMP-legionaminate biosynthesis II'],
        ['4-hydroxy-4-methyl-L-glutamate biosynthesis', '4-methylphenol degradation to protocatechuate',
         '2,5-xylenol and 3,5-xylenol degradation', '2,4-xylenol degradation to protocatechuate',
         'sch210971 and sch210972 biosynthesis'],
        ['dTDP-4-O-demethyl-&beta;-L-noviose biosynthesis', '3-amino-4,7-dihydroxy-coumarin biosynthesis',
         'oleate &beta;-oxidation (reductase-dependent, yeast)',
         '3-dimethylallyl-4-hydroxybenzoate biosynthesis', 'estradiol biosynthesis II'],
        ['UDP-N-acetyl-D-glucosamine biosynthesis I', 'L-asparagine biosynthesis III (tRNA-dependent)',
         'S-adenosyl-L-methionine salvage II', 'CMP-3-deoxy-D-manno-octulosonate biosynthesis',
         'cadaverine biosynthesis'], ['oleanolate biosynthesis', '2&alpha;,7&beta;-dihydroxylation of taxusin',
                                      'glycyrrhetinate biosynthesis', 'fumigaclavine biosynthesis',
                                      'esculetin modification'],
        ['CDP-4-dehydro-3,6-dideoxy-D-glucose biosynthesis', 'fluoroacetate degradation',
         'volatile esters biosynthesis (during fruit ripening)', 'heme b biosynthesis V (aerobic)',
         'heme b biosynthesis II (oxygen-independent)'],
        ['phosphatidylcholine resynthesis via glycerophosphocholine',
         '1,4-dihydroxy-6-naphthoate biosynthesis II', 'thiamine triphosphate metabolism',
         'demethylmenaquinol-6 biosynthesis II', '1,4-dihydroxy-6-naphthoate biosynthesis I'],
        ['pyruvate fermentation to ethanol II', 'pentagalloylglucose biosynthesis', 'cornusiin E biosynthesis',
         '6-methoxypodophyllotoxin biosynthesis', 'gallotannin biosynthesis'],
        ['L-lysine degradation IX', 'sulfite oxidation IV (sulfite oxidase)', 'taurine biosynthesis I',
         'carbon disulfide oxidation II (aerobic)', 'L-cysteine degradation III'],
        ['catechol degradation to &beta;-ketoadipate', 'benzoyl-CoA degradation II (anaerobic)',
         'camalexin biosynthesis', '3,8-divinyl-chlorophyllide a biosynthesis I (aerobic, light-dependent)',
         'L-carnitine degradation I'],
        ['folate transformations III (E. coli)', 'D-galactose detoxification', 'L-histidine degradation VI',
         'L-histidine degradation III', 'L-alanine degradation II (to D-lactate)'],
        ['pulcherrimin biosynthesis', 'trehalose biosynthesis II', 'fructan degradation',
         'bacillithiol biosynthesis', 'L-ascorbate biosynthesis I (plants, L-galactose pathway)'],
        ['pelargonidin conjugates biosynthesis', 'cannabinoid biosynthesis',
         'acyl-[acyl-carrier protein] thioesterase pathway',
         'fatty acid &beta;-oxidation III (unsaturated, odd number)',
         'fatty acid &beta;-oxidation IV (unsaturated, even number)'],
        ['yatein biosynthesis II', '2,4-dinitroanisole degradation',
         '2,4,6-trinitrophenol and 2,4-dinitrophenol degradation', 'phospholipid desaturation',
         'bacilysin biosynthesis'], ['methylsalicylate degradation', "pyridoxal 5'-phosphate biosynthesis II",
                                     'glycine betaine degradation I',
                                     'benzoate degradation II (aerobic and anaerobic)',
                                     'NAD(P)/NADPH interconversion'],
        ['calendate biosynthesis', 'petroselinate biosynthesis',
         'palmitoleate biosynthesis II (plants and bacteria)', 'carbon tetrachloride degradation I',
         'dimorphecolate biosynthesis'],
        ['thiazole biosynthesis I (facultative anaerobic bacteria) with tautomerase',
         'menaquinol oxidase (cytochrom aa3-600)', 'Extracellular galactan(2n) degradation',
         'F420 Biosynthesis until 3 glutamine residues', 'H4SPT-SYN'],
        ['isovitexin glycosides biosynthesis', '2,3-trans-flavanols biosynthesis',
         'nitrilotriacetate degradation', 'glucosinolate biosynthesis from tryptophan',
         'capsiconiate biosynthesis'],
        ['tetrahydromonapterin biosynthesis', 'curcumin degradation', 'nitrate reduction VIII (dissimilatory)',
         'uracil degradation III', 'tRNA processing'],
        ['sphingomyelin metabolism', 'phosphopantothenate biosynthesis II', '&beta;-alanine biosynthesis I',
         'sphingosine and sphingosine-1-phosphate metabolism', 'berberine biosynthesis'],
        ['glucosylglycerol biosynthesis', 'glycogen biosynthesis III (from &alpha;-maltose 1-phosphate)',
         'glucosinolate biosynthesis from tyrosine', 'protein NEDDylation',
         'tRNA-uridine 2-thiolation (thermophilic bacteria)'],
        ['3-methyl-branched fatty acid &alpha;-oxidation', 'ceramide degradation by &alpha;-oxidation',
         'sulfolactate degradation III', '15-epi-lipoxin biosynthesis', 'lipoxin biosynthesis'],
        ['heme degradation IV', 'heme degradation III', 'neolacto-series glycosphingolipids biosynthesis',
         'UDP-yelosamine biosynthesis', 'heme degradation II'],
        ['fluoroacetate and fluorothreonine biosynthesis', 'labdane-type diterpenes biosynthesis',
         'glycolate and glyoxylate degradation III', 'rhamnolipid biosynthesis',
         'juvenile hormone III biosynthesis II'],
        ['D-carnitine degradation I', 'acetone degradation III (to propane-1,2-diol)',
         'phosphatidylcholine biosynthesis VII', 'gentisate degradation II',
         'benzoyl-&beta;-D-glucopyranose biosynthesis'],
        ['sterculate biosynthesis', '6-methoxymellein biosynthesis', 'nitrate reduction VI (assimilatory)',
         'ethylbenzene degradation (anaerobic)', 'UDP-&alpha;-D-glucuronate biosynthesis (from myo-inositol)'],
        ['tetradecanoate biosynthesis (mitochondria)', 'anteiso-branched-chain fatty acid biosynthesis',
         'even iso-branched-chain fatty acid biosynthesis',
         'octanoyl-[acyl-carrier protein] biosynthesis (mitochondria, yeast)',
         'odd iso-branched-chain fatty acid biosynthesis'],
        ['chlorzoxazone degradation', 'prunasin and amygdalin biosynthesis',
         'Amaryllidacea alkaloids biosynthesis', 'juglone degradation', 'tunicamycin biosynthesis'],
        ['oxalate degradation III', 'Fe(II) oxidation', 'D-galactose degradation IV', 'oxalate degradation V',
         'plaunotol biosynthesis'],
        ['androgen biosynthesis', 'mineralocorticoid biosynthesis', 'sulfolactate degradation II',
         'glucocorticoid biosynthesis', 'estradiol biosynthesis I (via estrone)'],
        ['methanol oxidation to formaldehyde IV', 'vitamin B6 degradation',
         'reductive monocarboxylic acid cycle', 'paraoxon degradation', 'L-arabinose degradation III'],
        ['4-aminophenol degradation', 'taxiphyllin biosynthesis', 'triethylamine degradation',
         '2-methylisoborneol biosynthesis', 'geodin biosynthesis'],
        ['viridicatumtoxin biosynthesis', 'glycogen degradation III (via anhydrofructose)',
         'protein N-glycosylation (Haloferax volcanii)', 'protein N-glycosylation (Methanococcus voltae)',
         'tryptoquialanine biosynthesis'],
        ['(4Z,7Z,10Z,13Z,16Z)-docosa-4,7,10,13,16-pentaenoate biosynthesis II (4-desaturase)',
         'arachidonate biosynthesis V (8-detaturase, mammals)',
         '5,6-dimethylbenzimidazole biosynthesis II (anaerobic)',
         '(4Z,7Z,10Z,13Z,16Z)-docosapentaenoate biosynthesis (6-desaturase)',
         'docosahexaenoate biosynthesis IV (4-desaturase, mammals)'],
        ['elloramycin biosynthesis', 'cyclooctatin biosynthesis', 'tetracenomycin C biosynthesis',
         'oryzalide A biosynthesis', 'phytocassanes biosynthesis, shared reactions'],
        ['holomycin biosynthesis', '10,13-epoxy-11-methyl-octadecadienoate biosynthesis',
         'zwittermicin A biosynthesis', 'bikaverin biosynthesis', '8-O-methylfusarubin biosynthesis'],
        ['dTDP-L-daunosamine biosynthesis', '6-methylpretetramide biosynthesis',
         'tetracycline and oxytetracycline biosynthesis', 'thiosulfate disproportionation III (quinone)',
         'chlorotetracycline biosynthesis'],
        ['phycoviolobilin biosynthesis', 'phycourobilin biosynthesis', 'nitrogen fixation II (flavodoxin)',
         'phycoerythrobilin biosynthesis II', 'mercaptosuccinate degradation']]

    df_0_5 = clusters_to_df(cluster_data_0_5)
    df_0_6 = clusters_to_df(cluster_data_0_6)
    # Also prepare explore versions (using same data)
    df_0_5_explore = df_0_5.copy()
    df_0_6_explore = df_0_6.copy()


    try:
        fig_0_5 = px.sunburst(df_0_5, path=["Cluster", "Species"], values="Value", title="Threshold 0.5")
        fig_0_5.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_5 = pio.to_html(fig_0_5, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_03")
    except Exception as e:
        sunburst_html_0_5 = ""
    try:
        fig_0_6 = px.sunburst(df_0_6, path=["Cluster", "Species"], values="Value", title="Threshold 0.6")
        fig_0_6.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_6 = pio.to_html(fig_0_6, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_02")
    except Exception as e:
        sunburst_html_0_6 = ""
    try:
        explore_fig_0_5 = px.sunburst(df_0_5_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.5")
        explore_fig_0_5.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_5 = pio.to_html(explore_fig_0_5, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_03")
    except Exception as e:
        explore_sunburst_html_0_5 = ""

    try:
        explore_fig_0_6 = px.sunburst(df_0_6_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.6")
        explore_fig_0_6.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_6 = pio.to_html(explore_fig_0_6, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_02")
    except Exception as e:
        explore_sunburst_html_0_6 = ""

    # ileum suggestions from DB to do fot otu
    # otu_list = OtuCorrelation.objects.values_list('var2', flat=True).distinct().order_by('var2')
    # Check from file csv the ileum
    # otu_list = []  # default if anything goes wrong
    try:
        otu_csv_path = os.path.join(settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                                    "otu_to_functionnal.csv")
        df_otu = pd.read_csv(otu_csv_path, )
        otu_list = df_otu.iloc[:, 0].dropna().unique().tolist()
    except Exception as e:
        otu_list = []
        print(f"Error loading otu_to_functionnal.csv: {e}")

    return render(request, f"{host_type}/functionnal.html", {
        "host_type": host_type.title(),
        "data_type": "Functionnal",
        "description": "Top 200 displayed only. Gene info from Ensembl REST.",
        # "tissue_types": list(tissue_files_muscle.keys()),
        "sunburst_html_0_5": sunburst_html_0_5,
        "sunburst_html_0_6": sunburst_html_0_6,
        "explore_sunburst_html_0_5": explore_sunburst_html_0_5,
        "explore_sunburst_html_0_6": explore_sunburst_html_0_6,
        "otu_list": otu_list,
    })
#####################################


####################################
# Version of databse pg molecule
#####################################

def molecule_data_analysisv2(request, host_type='isabrownv2'):
    """
    1) Builds three sunbursts from TSVs (unchanged).
    2) AJAX branches now query IleumCorrelation instead of reading CSVs.
    """
    # --- AJAX Handling ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # (A) Load tissue: list distinct var2 (variables)
        if 'load_tissue' in request.GET:
            tissue = request.GET.get('tissue')
            vars_qs = MetabCorrelation.objects.filter(
                Q(from_tissue=tissue) | Q(to_tissue=tissue)
            ).values_list('var2', flat=True).distinct().order_by('var2')
            return J({'variables': list(vars_qs)})

        # (D) Cluster Lookup branch remains unchanged
        if "cluster_lookup" in request.GET:
            selected_bacteria = request.GET.get("bacteria", "").strip()
            if selected_bacteria.endswith("_otu"):
                selected_bacteria = selected_bacteria[:-4]
            if selected_bacteria.startswith("s__"):
                prefix = "s__"
                core = selected_bacteria[3:].replace("_metab", " ")
                selected_bacteria = prefix + core
            else:
                selected_bacteria = selected_bacteria.replace("_metab", "")
            selected_bacteria = selected_bacteria.replace(" B", "_B").replace(" A", "_A")
            found = False
            cluster_found = None
            threshold = None
            cluster_data_0_5 = [['Proline', 'Indoline_479', 'Piperidine_556', 'Deoxyguanosine', 'Thymidine', 'H01040'],
                                ['X00736', 'X00394', 'H00524', 'H00277', 'X00151', 'H00079'],
                                ['META-ETHYLPHENOL', 'Propyl gallate', '4-Vinylphenol', 'H00768',
                                 '3-Phenyllactic acid'],
                                ['H00180', 'Urobilin', 'X01002', 'X00220', 'H00860'],
                                ['Malic acid', 'Xanthine', 'Uracil', 'Thiamine', 'Pyruvic acid']]

            cluster_data_0_4 = [
                ['Urobilin', 'Propyl gallate', '3-Phenyllactic acid', 'H00180', 'META-ETHYLPHENOL', 'X01002', 'X00220',
                 'H00860',
                 '4-Vinylphenol', 'H00768'],
                ['Tetradecanedioic acid', 'X00087', 'Indole-3-carboxyaldehyde', '1-Aminocyclohexanecarboxylic acid',
                 'X00846',
                 'H00434', 'H02578', 'H02435'],
                ['H02583', '(+)-Costunolide_257', 'N8-Acetylspermidine', 'H00798', 'X00107', 'X00309',
                 '4-Hydroxyhygric acid'],
                ['Stachyose', 'X02359', 'X03645', 'Creatinine', 'Hexose trimer', 'Pinitol', 'H03399'],
                ['Lactic acid', 'Ornithine', 'Arginine', 'Betaine', 'Creatine', 'Lysine', 'Carnosine'],
                ['X00842', 'Norepinephrine', 'DOPA', 'X10785', 'H03047', 'X03140'],
                ['H00890', 'X01182', '3-Hydroxybenzoic acid', 'X00637', 'H01305', '3-Hydroxycinnamic acid'],
                ['Proline', 'Indoline_479', 'Piperidine_556', 'Deoxyguanosine', 'Thymidine', 'H01040'],
                ['X00736', 'X00394', 'H00524', 'H00277', 'X00151', 'H00079'],
                ['Isoliquiritigenin', 'X04317', 'H00181', 'Verrucarol', 'X00590'],
                ['5-Hydroxyindole', 'Indole-3-glyoxylic acid', 'N-Acetylmethionine', 'X00146', 'Puerarin'],
                ['X06269', 'H00096', 'Glycylleucine', 'H00253', 'H02415'],
                ['Malic acid', 'Xanthine', 'Uracil', 'Thiamine', 'Pyruvic acid'],
                ['Acetylcarnitine', 'H00346', 'X00757', 'X00246', 'H01009']]

            cluster_data_0_3 = [
                ['Xanthine', 'Allopurinol_421', '2-Picolinic acid', '3-Methyl-2-oxovaleric acid', 'Acetylmuramic acid',
                 'Uracil',
                 'Pyruvic acid', 'Hypoxanthine', 'Malic acid', 'Urocanic acid', 'Nicotinic acid ribonucleoside',
                 'Thiamine',
                 'N-(5-Aminopentyl)acetamide_184'],
                ['H00890', 'X01182', 'H00417', '3-Hydroxycinnamic acid', '3-Hydroxybenzoic acid', 'X00637', 'H00743',
                 'H01305',
                 'gamma-Aminobutyric acid', 'X00639'],
                ['Urobilin', 'Propyl gallate', '3-Phenyllactic acid', 'H00180', 'META-ETHYLPHENOL', 'X01002', 'X00220',
                 'H00860',
                 '4-Vinylphenol', 'H00768'],
                ['X04860', 'H03558', 'gamma-Caprolactone', 'Vanillin', 'X04183', 'X05705', 'X08701', 'X06691',
                 'X05456'],
                ['X00043', '3-Methylglutaconic acid', 'H00346', 'X00455', 'Acetylcarnitine', 'X00246', 'X00757',
                 'H01009',
                 'beta-Muricholic acid'],
                ['5-Hydroxyindole', 'Indole-3-lactic acid', 'N-Acetylmethionine', 'X00225', 'Indole-3-glyoxylic acid',
                 'Puerarin',
                 '5,6-Dihydrothymine', 'H00544', 'X00146'],
                ['X04317', 'H00181', 'Isoliquiritigenin', 'Verrucarol', 'Prostaglandin E2', 'scyllo-Inositol', 'Butein',
                 '2-Oxo-3-phenylpropanoic acid', 'X00590'],
                ['Catechin', 'X00980', 'X09476', 'Gomisin J', 'X00382', 'Oridonin', '7beta-Hydroxylathyrol', 'H03845',
                 'X00100'],
                ['Tetradecanedioic acid', 'X00087', 'Indole-3-carboxyaldehyde', '1-Aminocyclohexanecarboxylic acid',
                 'X00846',
                 'H00434', 'H02578', 'H02435'],
                ['X06269', 'Leucylalanine', 'H00096', 'X00599', 'Glycylleucine', 'H00253', 'H02415', 'H01934'],
                ['Kirenol', 'Hexahydrocurcumin', 'X04156', 'H02615', 'N-Acetylhistidine', 'X05146', 'X08351', 'X00731'],
                ['Lactic acid', 'Ornithine', 'Arginine', 'Betaine', 'Creatine', 'Lysine', 'Carnosine'],
                ['X00508', 'X05149', 'H00162', 'H12871', 'H00117', 'H02755', 'Indole-3-carbinol'],
                ['N-Acetyl-5-hydroxytryptamine', 'Tryptamine', 'X08212', 'Inulicin', '2-Methylbutyrylglycine', 'H00207',
                 'Salicylic acid'],
                ['Leucine', 'Phosphocholine', 'Gulonic acid gamma-lactone', 'X00269', 'Piperidine_557', 'X03698',
                 'Isoleucine'],
                ['Stachyose', 'X02359', 'X03645', 'Creatinine', 'Hexose trimer', 'Pinitol', 'H03399'],
                ['H02583', '(+)-Costunolide_257', 'N8-Acetylspermidine', 'H00798', 'X00107', 'X00309',
                 '4-Hydroxyhygric acid'],
                ['X00138', '5-Hydroxytryptamine creatinine sulfate monohydrate', 'Patulin_548', 'H00171', 'X04612',
                 'Pipecolinic acid', 'H00553'], ['H01685', 'H02971', 'H00025', 'H00265', 'H02475', 'Fucose', 'H00762'],
                ['2-Hydroxyphenylacetic acid', 'X07085', 'X01114', 'H01154', 'Vanillyl alcohol', 'X01498'],
                ['X00842', 'Norepinephrine', 'DOPA', 'X10785', 'H03047', 'X03140'],
                ['Proline', 'Indoline_479', 'Piperidine_556', 'Deoxyguanosine', 'Thymidine', 'H01040'],
                ['SL00115', 'X14123', 'X01733', 'X05003', 'H02794', 'X02808'],
                ['Anserine/Homocarnosine', '7-Methylguanine', 'Caffeic acid', 'Ribulose 5-phosphate', 'H03322',
                 'D-arabinose'],
                ['X00200', 'X01850', 'Imidazoleacetic acid', 'X01454', 'H00722', 'Citraconic acid'],
                ['Daurisoline', 'N-Acetylputrescine', 'X00018', 'X01275', 'Sulfuretin', 'Quinic acid'],
                ['Allopurinol_118', 'Phenylalanine', 'Inosine', 'Propionylcarnitine', 'Butyrylcarnitine',
                 'Indoline_480'],
                ['X00736', 'X00394', 'H00524', 'H00277', 'X00151', 'H00079'],
                ['X00905', 'Veratridine', 'H02163', 'H04645', 'X04102'],
                ['X06478', 'X14611', 'X04952', 'X00568', 'X06276'],
                ['Cyclo(L-Phe-L-Pro)', 'X02378', 'X01038', 'X01185', 'X05178'],
                ['1-Aminocyclopropanecarboxylic acid', 'N-Methylaspartic acid', '3-Hydroxybutyric acid', 'X01703',
                 'Valerylcarnitine'], ['O-Desmethylangolensin_545', 'X01578', 'H00035', 'Ononetin', 'Pantothenic acid'],
                ['X01099', 'Dimethylmalonic acid', 'H02108', 'H01407', 'X10202'],
                ['H03435', 'Argininosuccinic acid', 'H07398', 'X07540', 'H01019'],
                ['a Zearalenol', 'Blinin', 'X13463', 'X04161', 'Ingenol'],
                ['X03335', 'Transtorine', 'X00672', 'H01727', '3-Hydroxy-2-methyl-4-pyrone'],
                ['X01909', 'H10665', 'Isofraxidin', 'H02257', '5-Methyluridine']]

            cluster_data_0_2 = [
                ['Tetradecanedioic acid', 'Hypaconitine', 'H02755', 'H02200', 'N1-Methyl-2-pyridone-5-carboxamide',
                 'X00508',
                 'X00059', 'H02233', 'H00434', 'H02578', 'X03124', 'X05149', 'Succinic acid', 'X00087',
                 'Indole-3-carboxyaldehyde',
                 '1-Aminocyclohexanecarboxylic acid', 'Indole-3-carbinol', 'X00846', 'X00409', 'H00162', 'H12871',
                 'H00117',
                 'H02435'],
                ['Leucine', 'Phosphocholine', 'X00269', 'Betaine', 'Inosine', 'X03698', 'Propionylcarnitine',
                 'Carnosine',
                 'Allopurinol_118', 'Phenylalanine', 'Gulonic acid gamma-lactone', 'Isoleucine', 'Creatine',
                 'Butyrylcarnitine',
                 'Indoline_480', 'Lactic acid', 'Ornithine', 'Arginine', 'Piperidine_557', 'Lysine'],
                ['Caffeic acid', 'X00018', '4-Hydroxyhygric acid', 'X01275', 'D-arabinose', '(+)-Costunolide_257',
                 'N8-Acetylspermidine', 'H00798', 'N-Acetylputrescine', 'H03322', 'X00309', 'Daurisoline',
                 'Quinic acid',
                 'H02583',
                 'Anserine/Homocarnosine', '7-Methylguanine', 'X00107', 'Ribulose 5-phosphate', 'Sulfuretin'],
                ['2-Picolinic acid', '3-Methyl-2-oxovaleric acid', 'Uracil', 'Acetylmuramic acid', 'Hypoxanthine',
                 'Nicotinic acid ribonucleoside', 'Urocanic acid', 'X00394', 'X00151', 'Xanthine', 'H00524',
                 'Allopurinol_421',
                 'Pyruvic acid', 'H00079', 'Malic acid', 'X00736', 'Thiamine', 'H00277',
                 'N-(5-Aminopentyl)acetamide_184'],
                ['X00138', 'N-Acetyl-5-hydroxytryptamine', 'Tryptamine', '2-Methylbutyrylglycine', 'Patulin_548',
                 'H00171',
                 'H00207', 'Diethanolamine', '5-Hydroxytryptamine creatinine sulfate monohydrate', 'X00509', 'ectoine',
                 'X04612',
                 'Pipecolinic acid', 'Salicylic acid', 'H00553', 'Inulicin', 'Nordihydroguaiaretic acid', 'X08212'],
                ['H00890', 'X01182', 'H00417', '3-Hydroxycinnamic acid', '3-Hydroxybenzoic acid', 'X00637', 'H00579',
                 'X00514',
                 'H01305', 'gamma-Aminobutyric acid', 'X00639', 'Lotaustralin', 'beta-Hydroxyisovaleric acid', 'H00743',
                 'H00198',
                 'X03337', 'H00287'],
                ['X00462', 'Piperidine_556', '2-Aminoadipic acid', 'Deoxyuridine', '5-Aminovaleric acid', 'Proline',
                 'Cytosine',
                 'H00595', 'Thymidine', 'Lauramidopropyl betaine', 'Indoline_479', 'H00520', 'H01040',
                 'N-Acetylarginine',
                 'Deoxyguanosine', 'H00630'],
                ['Methyl gallate', 'Genipin', 'H03399', 'X00587', 'X02359', 'Hexose trimer', 'Stachyose',
                 'Proline/(R)-pyrrolidine-2-carboxylic acid', 'N-Acetylneuraminic acid', 'H00202', 'X03645',
                 'Creatinine',
                 'Pinitol', 'SL00418', 'L-Quebrachitol', 'H01387'],
                ['Catechin', 'X01738', 'X00980', 'X00708', 'X09476', 'Dihydrocucurbitacin B', 'Deoxyelephantopin',
                 'Enterolactone_458', 'Gomisin J', 'X00382', 'Oridonin', 'Enterolactone_459', '7beta-Hydroxylathyrol',
                 'H03845',
                 'X00100'],
                ['X02114', '2-Hydroxy-3-methylbutyric acid', 'Prolylhydroxyproline', 'H00823', 'Glucuronic acid',
                 'Pyroglutamic acid', '2-Hydroxy-2-methylbutanoic acid', 'N-Acetylgalactosamine',
                 'N-Acetylmannosamine',
                 'Adenosine', 'Galactosamine', 'Diaminopimelic acid', '2-Hydroxyisocaproic acid',
                 'N-Acetylornithine'],
                ['X07545', 'X03140', 'H03047', 'X00061', 'X00842', 'Norepinephrine', 'DOPA', 'X14186', 'X10785',
                 'Castanospermine',
                 'H00423', 'Bufotalin', 'X06638'],
                ['DL-Glutamine', 'Taurine', 'Alanine', 'Choline', 'Serine', 'H00270', 'Threonine', 'Asparagine',
                 'Histidine',
                 'Glutamine', 'X01010', 'Tryptophan'],
                ['H02971', 'H00025', 'H01685', 'H00265', 'Carnitine', 'H00572', 'H02475', 'Fucose',
                 'N-Acetylaspartic acid',
                 'H00762', '1-Methyladenosine', 'N-Acetylglutamic acid'],
                ['Pimelic acid', 'X03659', 'X01155', '4-Hydroxy-2,5-dimethyl-3(2H)-furanone', 'X00844', 'SL00035',
                 'Bicine',
                 'X06380', 'Hippuric acid', '3-hydroxy-4,5-dimethyl-3(5H)-furanone', 'X01565'],
                ['Rhodojaponin III', 'X01347', 'X01033', 'Pentoxifylline', 'X02741', 'Quinine', 'X00336', 'X05089',
                 'X05359',
                 'X12625', 'X00583'],
                ['H05669', 'H01450', 'X05466', 'X00927', 'H08607', 'X01605', 'X04291', 'H02554', 'H11880', 'X00775'],
                ['X05178', 'X06276', 'X00568', 'Cyclo(L-Phe-L-Pro)', 'X02378', 'X06478', 'X01038', 'X01185', 'X04952',
                 'X14611'],
                ['Shikimic acid', 'H05210', 'X02748', 'H03536', 'H00332', 'H01061', 'H05721', 'H02505', 'H02245',
                 'H03548'],
                ['H03505', '3,3-Dimethylglutaric acid', 'H00266', 'X05711', 'H04800', 'X01331', 'X02482', 'H00956',
                 'X02025',
                 'H03949'],
                ['X06643', 'X05760', 'H03349', 'X04161', 'H02768', 'a Zearalenol', 'Blinin', 'H02237', 'X13463',
                 'Ingenol'],
                ['Urobilin', 'Propyl gallate', '3-Phenyllactic acid', 'H00180', 'META-ETHYLPHENOL', 'X01002', 'X00220',
                 'H00860',
                 '4-Vinylphenol', 'H00768'],
                ['X04860', 'H03558', 'gamma-Caprolactone', 'Vanillin', 'X04183', 'X05705', 'X08701', 'X06691',
                 'X05456'],
                ['X00022', 'H00534', 'Stachydrine', 'H07398', 'H01019', 'H03435', 'Argininosuccinic acid', 'H00646',
                 'X07540'],
                ['X00043', '3-Methylglutaconic acid', 'H00346', 'X00455', 'Acetylcarnitine', 'X00246', 'X00757',
                 'H01009',
                 'beta-Muricholic acid'],
                ['5-Hydroxyindole', 'Indole-3-lactic acid', 'N-Acetylmethionine', 'X00225', 'Indole-3-glyoxylic acid',
                 'Puerarin',
                 '5,6-Dihydrothymine', 'H00544', 'X00146'],
                ['X00097', 'Pyridoxine', 'H03896', 'X00224', 'X01099', 'Dimethylmalonic acid', 'H02108', 'H01407',
                 'X10202'],
                ['X08198', 'X00041', 'H00930', 'Pinocembrin', 'X01242', 'Asymmetric dimethylarginine', 'X00660',
                 'SL00194',
                 'H00488'], ['N-Methylaspartic acid', '3-Hydroxybutyric acid', 'X01703', 'Valerylcarnitine',
                             '1-Aminocyclopropanecarboxylic acid', 'Pyridoxamine', "Pyridoxal 5'-phosphate",
                             'Methionine',
                             'Aspartic acid'],
                ['X04317', 'H00181', 'Isoliquiritigenin', 'Verrucarol', 'Prostaglandin E2', 'scyllo-Inositol', 'Butein',
                 '2-Oxo-3-phenylpropanoic acid', 'X00590'],
                ['X01909', 'Isofraxidin', 'H00447', 'X03744', 'H06253', 'H10665', 'H02257', '5-Methyluridine',
                 'H09307'],
                ['X06269', 'Leucylalanine', 'H00096', 'X00599', 'Glycylleucine', 'H00253', 'H02415', 'H01934'],
                ['Kirenol', 'Hexahydrocurcumin', 'X04156', 'H02615', 'N-Acetylhistidine', 'X05146', 'X08351', 'X00731'],
                ['2-Hydroxyphenylacetic acid', 'H01154', 'Vanillyl alcohol', 'X03155', 'X01498', 'X07085', 'X01114',
                 'Gibberellin A3'],
                ['X00443', 'X02611', 'H02424', '4-Guanidinobutyric acid', 'X00543', 'X05119', 'SL00091', 'X06373'],
                ['3-Methylhistidine/ 1-Methylhistidine', 'H00353', 'X01923', 'Acetylagmatine', 'X03182',
                 '3-Indoxylsulfuric acid',
                 'Trigonelline', 'H00284'],
                ['delta-Gluconolactone/ delta-Gluconic acid delta-lactone', 'Decursinol', 'Kynurenine', 'X00834',
                 'N-Methyl-2-pyrrolidone', "4'-O-Methylpyridoxine", 'beta-Alanine'],
                ['X06608', '4-pyridoxic acid', 'H00543', 'X01683', 'O-Desmethylangolensin_94', 'Indole-3-acetic acid',
                 '4-Hydroxybenzoic acid'],
                ['H01987', 'Guvacine hydrochloride', 'X01253', 'X00537', 'X02889', 'X00726', 'Traumatic acid'],
                ['Daidzein', 'Naringenin/Pinobanksin', '4-Hydroxyproline', 'Uridine', 'Glucose', 'Nicotinic acid',
                 'Pyridoxal'],
                ['SL00115', 'X14123', 'X01733', 'X05003', 'H02794', 'X02808'],
                ['X00528', 'Guanosine', 'X04006', 'Valine', 'H00547', 'HY-30220_(S)-2-Hydroxy-3-phenylpropanoic acid'],
                ['Dopamine', 'Tyrosine', 'H02734', '(+)-Costunolide_258', 'X03614', 'SL00069'],
                ['X00200', 'X01850', 'Imidazoleacetic acid', 'X01454', 'H00722', 'Citraconic acid'],
                ['H00517', 'X05938', 'Glaucocalyxin A', 'X01446', '4-Hydroxybenzaldehyde', 'H00451'],
                ['X00905', 'Veratridine', 'H02163', 'H04645', 'X04102'],
                ['H00276', 'H03656', 'Hexose dimer', 'Agmatine', 'Guanine'],
                ['O-Desmethylangolensin_545', 'X01578', 'H00035', 'Ononetin', 'Pantothenic acid'],
                ['X12234', 'X02147', 'Sebacic acid', 'X09130', 'H01633'],
                ['X03335', 'Transtorine', 'X00672', 'H01727', '3-Hydroxy-2-methyl-4-pyrone']]
            for cluster in cluster_data_0_5:
                if selected_bacteria in cluster:
                    found = True
                    cluster_found = cluster
                    threshold = "0.5"
                    break
            if not found:
                for cluster in cluster_data_0_4:
                    if selected_bacteria in cluster:
                        found = True
                        cluster_found = cluster
                        threshold = "0.4"
                        break
            if not found:
                for cluster in cluster_data_0_3:
                    if selected_bacteria in cluster:
                        found = True
                        cluster_found = cluster
                        threshold = "0.3"
                        break
            if not found:
                for cluster in cluster_data_0_2:
                    if selected_bacteria in cluster:
                        found = True
                        cluster_found = cluster
                        threshold = "0.2"
                        break
            if found:
                cleaned_cluster = [s.replace("s__", "") for s in cluster_found]
                return J({
                    "found": True,
                    "threshold": threshold,
                    "cluster_members": cleaned_cluster,
                })
            else:
                return J({"found": False})

        # Common filters
        tissue = request.GET.get('tissue')
        if tissue is None:
            return J({'error': 'Missing tissue.'}, status=400)
        # base_tissue_q = Q(from_tissue=tissue) | Q(to_tissue=tissue)
        # here tissue is metab to adapat for each case
        base_tissue_q = Q(from_tissue='metab') & Q(to_tissue=tissue)

        # (B) Single-var filtering
        if ('multi_variable' not in request.GET
            and 'table_filter' not in request.GET
            and 'cluster_lookup' not in request.GET
            and 'explore_table_filter' not in request.GET
            and 'explore_distribution' not in request.GET):
            var = request.GET.get('variable')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min  = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = MetabCorrelation.objects.filter(
                base_tissue_q,
                var2=var,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({'results': [], 'total_count': 0})
            top = filt.order_by('-correlation')[:100]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count})

        # (C) Multi-var filtering
        if 'multi_variable' in request.GET:
            variables = request.GET.getlist('variables[]')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min  = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = MetabCorrelation.objects.filter(
                base_tissue_q,
                var2__in=variables,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({'results': [], 'total_count': 0})
            top = filt.order_by('-correlation')[:100]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count})

        # (E) Table Filtering
        if 'table_filter' in request.GET:
            var = request.GET.get('variable')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min  = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = MetabCorrelation.objects.filter(
                base_tissue_q,
                var2=var,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({
                    'results': [],
                    'total_count': 0,
                    'overview': {'median': None, 'q1': None, 'q3': None}
                })
            top = filt.order_by('-correlation')[:200]

            results = []
            vals = [o.correlation for o in filt]
            overview = {
                'median': r3(np.median(vals)),
                'q1': r3(np.quantile(vals, 0.25)),
                'q3': r3(np.quantile(vals, 0.75)),
            }
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'Coefficient': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count, 'overview': overview})

        # (F) Explore distribution
        if 'explore_distribution' in request.GET:
            # qs = IleumCorrelation.objects.filter(base_tissue_q).values_list('correlation', flat=True)
            qs = (MetabCorrelation.objects
                  .filter(base_tissue_q, correlation__isnull=False)
                  .values_list('correlation', flat=True)
                  )
            series = list(qs)
            if not series:
                return J({'error': 'No data found.'}, status=400)
            stats = {
                'min': r3(min(series)),
                'q1': r3(np.quantile(series, 0.25)),
                'median': r3(np.median(series)),
                'q3': r3(np.quantile(series, 0.75)),
                'max': r3(max(series)),
            }
            return J({'distribution': {'correlation_values': series, 'stats': stats}})

        # (G) Explore table filter
        if 'explore_table_filter' in request.GET:
            try:
                corr_min = float(request.GET.get('corrMin', -1))
                corr_max = float(request.GET.get('corrMax', 1))
                acc_min  = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = MetabCorrelation.objects.filter(
                base_tissue_q,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            top = filt.order_by('-correlation')[:200]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            vals = [o.correlation for o in filt]
            overview = {
                'median': r3(np.median(vals)) if vals else None,
                'q1': r3(np.quantile(vals, 0.25)) if vals else None,
                'q3': r3(np.quantile(vals, 0.75)) if vals else None,
            }
            return J({'results': results, 'total_count': total_count, 'overview': overview})

        return J({'error': 'No recognized AJAX action.'}, status=400)

    # --- Non-AJAX: build sunbursts + context ---
    def clusters_to_df(data):
        rows = []
        for i, sublist in enumerate(data, start=1):
            cluster_name = f"Cluster {i}"
            for species in sublist:
                rows.append({"Cluster": cluster_name, "Species": species.replace("s__", ""), "Value": 1})
        return pd.DataFrame(rows)

    cluster_data_0_5 = [['Proline', 'Indoline_479', 'Piperidine_556', 'Deoxyguanosine', 'Thymidine', 'H01040'],
                        ['X00736', 'X00394', 'H00524', 'H00277', 'X00151', 'H00079'],
                        ['META-ETHYLPHENOL', 'Propyl gallate', '4-Vinylphenol', 'H00768', '3-Phenyllactic acid'],
                        ['H00180', 'Urobilin', 'X01002', 'X00220', 'H00860'],
                        ['Malic acid', 'Xanthine', 'Uracil', 'Thiamine', 'Pyruvic acid']]

    cluster_data_0_4 = [
        ['Urobilin', 'Propyl gallate', '3-Phenyllactic acid', 'H00180', 'META-ETHYLPHENOL', 'X01002', 'X00220',
         'H00860',
         '4-Vinylphenol', 'H00768'],
        ['Tetradecanedioic acid', 'X00087', 'Indole-3-carboxyaldehyde', '1-Aminocyclohexanecarboxylic acid', 'X00846',
         'H00434', 'H02578', 'H02435'],
        ['H02583', '(+)-Costunolide_257', 'N8-Acetylspermidine', 'H00798', 'X00107', 'X00309', '4-Hydroxyhygric acid'],
        ['Stachyose', 'X02359', 'X03645', 'Creatinine', 'Hexose trimer', 'Pinitol', 'H03399'],
        ['Lactic acid', 'Ornithine', 'Arginine', 'Betaine', 'Creatine', 'Lysine', 'Carnosine'],
        ['X00842', 'Norepinephrine', 'DOPA', 'X10785', 'H03047', 'X03140'],
        ['H00890', 'X01182', '3-Hydroxybenzoic acid', 'X00637', 'H01305', '3-Hydroxycinnamic acid'],
        ['Proline', 'Indoline_479', 'Piperidine_556', 'Deoxyguanosine', 'Thymidine', 'H01040'],
        ['X00736', 'X00394', 'H00524', 'H00277', 'X00151', 'H00079'],
        ['Isoliquiritigenin', 'X04317', 'H00181', 'Verrucarol', 'X00590'],
        ['5-Hydroxyindole', 'Indole-3-glyoxylic acid', 'N-Acetylmethionine', 'X00146', 'Puerarin'],
        ['X06269', 'H00096', 'Glycylleucine', 'H00253', 'H02415'],
        ['Malic acid', 'Xanthine', 'Uracil', 'Thiamine', 'Pyruvic acid'],
        ['Acetylcarnitine', 'H00346', 'X00757', 'X00246', 'H01009']]

    cluster_data_0_3 = [
        ['Xanthine', 'Allopurinol_421', '2-Picolinic acid', '3-Methyl-2-oxovaleric acid', 'Acetylmuramic acid',
         'Uracil',
         'Pyruvic acid', 'Hypoxanthine', 'Malic acid', 'Urocanic acid', 'Nicotinic acid ribonucleoside', 'Thiamine',
         'N-(5-Aminopentyl)acetamide_184'],
        ['H00890', 'X01182', 'H00417', '3-Hydroxycinnamic acid', '3-Hydroxybenzoic acid', 'X00637', 'H00743', 'H01305',
         'gamma-Aminobutyric acid', 'X00639'],
        ['Urobilin', 'Propyl gallate', '3-Phenyllactic acid', 'H00180', 'META-ETHYLPHENOL', 'X01002', 'X00220',
         'H00860',
         '4-Vinylphenol', 'H00768'],
        ['X04860', 'H03558', 'gamma-Caprolactone', 'Vanillin', 'X04183', 'X05705', 'X08701', 'X06691', 'X05456'],
        ['X00043', '3-Methylglutaconic acid', 'H00346', 'X00455', 'Acetylcarnitine', 'X00246', 'X00757', 'H01009',
         'beta-Muricholic acid'],
        ['5-Hydroxyindole', 'Indole-3-lactic acid', 'N-Acetylmethionine', 'X00225', 'Indole-3-glyoxylic acid',
         'Puerarin',
         '5,6-Dihydrothymine', 'H00544', 'X00146'],
        ['X04317', 'H00181', 'Isoliquiritigenin', 'Verrucarol', 'Prostaglandin E2', 'scyllo-Inositol', 'Butein',
         '2-Oxo-3-phenylpropanoic acid', 'X00590'],
        ['Catechin', 'X00980', 'X09476', 'Gomisin J', 'X00382', 'Oridonin', '7beta-Hydroxylathyrol', 'H03845',
         'X00100'],
        ['Tetradecanedioic acid', 'X00087', 'Indole-3-carboxyaldehyde', '1-Aminocyclohexanecarboxylic acid', 'X00846',
         'H00434', 'H02578', 'H02435'],
        ['X06269', 'Leucylalanine', 'H00096', 'X00599', 'Glycylleucine', 'H00253', 'H02415', 'H01934'],
        ['Kirenol', 'Hexahydrocurcumin', 'X04156', 'H02615', 'N-Acetylhistidine', 'X05146', 'X08351', 'X00731'],
        ['Lactic acid', 'Ornithine', 'Arginine', 'Betaine', 'Creatine', 'Lysine', 'Carnosine'],
        ['X00508', 'X05149', 'H00162', 'H12871', 'H00117', 'H02755', 'Indole-3-carbinol'],
        ['N-Acetyl-5-hydroxytryptamine', 'Tryptamine', 'X08212', 'Inulicin', '2-Methylbutyrylglycine', 'H00207',
         'Salicylic acid'],
        ['Leucine', 'Phosphocholine', 'Gulonic acid gamma-lactone', 'X00269', 'Piperidine_557', 'X03698', 'Isoleucine'],
        ['Stachyose', 'X02359', 'X03645', 'Creatinine', 'Hexose trimer', 'Pinitol', 'H03399'],
        ['H02583', '(+)-Costunolide_257', 'N8-Acetylspermidine', 'H00798', 'X00107', 'X00309', '4-Hydroxyhygric acid'],
        ['X00138', '5-Hydroxytryptamine creatinine sulfate monohydrate', 'Patulin_548', 'H00171', 'X04612',
         'Pipecolinic acid', 'H00553'], ['H01685', 'H02971', 'H00025', 'H00265', 'H02475', 'Fucose', 'H00762'],
        ['2-Hydroxyphenylacetic acid', 'X07085', 'X01114', 'H01154', 'Vanillyl alcohol', 'X01498'],
        ['X00842', 'Norepinephrine', 'DOPA', 'X10785', 'H03047', 'X03140'],
        ['Proline', 'Indoline_479', 'Piperidine_556', 'Deoxyguanosine', 'Thymidine', 'H01040'],
        ['SL00115', 'X14123', 'X01733', 'X05003', 'H02794', 'X02808'],
        ['Anserine/Homocarnosine', '7-Methylguanine', 'Caffeic acid', 'Ribulose 5-phosphate', 'H03322', 'D-arabinose'],
        ['X00200', 'X01850', 'Imidazoleacetic acid', 'X01454', 'H00722', 'Citraconic acid'],
        ['Daurisoline', 'N-Acetylputrescine', 'X00018', 'X01275', 'Sulfuretin', 'Quinic acid'],
        ['Allopurinol_118', 'Phenylalanine', 'Inosine', 'Propionylcarnitine', 'Butyrylcarnitine', 'Indoline_480'],
        ['X00736', 'X00394', 'H00524', 'H00277', 'X00151', 'H00079'],
        ['X00905', 'Veratridine', 'H02163', 'H04645', 'X04102'], ['X06478', 'X14611', 'X04952', 'X00568', 'X06276'],
        ['Cyclo(L-Phe-L-Pro)', 'X02378', 'X01038', 'X01185', 'X05178'],
        ['1-Aminocyclopropanecarboxylic acid', 'N-Methylaspartic acid', '3-Hydroxybutyric acid', 'X01703',
         'Valerylcarnitine'], ['O-Desmethylangolensin_545', 'X01578', 'H00035', 'Ononetin', 'Pantothenic acid'],
        ['X01099', 'Dimethylmalonic acid', 'H02108', 'H01407', 'X10202'],
        ['H03435', 'Argininosuccinic acid', 'H07398', 'X07540', 'H01019'],
        ['a Zearalenol', 'Blinin', 'X13463', 'X04161', 'Ingenol'],
        ['X03335', 'Transtorine', 'X00672', 'H01727', '3-Hydroxy-2-methyl-4-pyrone'],
        ['X01909', 'H10665', 'Isofraxidin', 'H02257', '5-Methyluridine']]

    cluster_data_0_2 = [
        ['Tetradecanedioic acid', 'Hypaconitine', 'H02755', 'H02200', 'N1-Methyl-2-pyridone-5-carboxamide', 'X00508',
         'X00059', 'H02233', 'H00434', 'H02578', 'X03124', 'X05149', 'Succinic acid', 'X00087',
         'Indole-3-carboxyaldehyde',
         '1-Aminocyclohexanecarboxylic acid', 'Indole-3-carbinol', 'X00846', 'X00409', 'H00162', 'H12871', 'H00117',
         'H02435'],
        ['Leucine', 'Phosphocholine', 'X00269', 'Betaine', 'Inosine', 'X03698', 'Propionylcarnitine', 'Carnosine',
         'Allopurinol_118', 'Phenylalanine', 'Gulonic acid gamma-lactone', 'Isoleucine', 'Creatine', 'Butyrylcarnitine',
         'Indoline_480', 'Lactic acid', 'Ornithine', 'Arginine', 'Piperidine_557', 'Lysine'],
        ['Caffeic acid', 'X00018', '4-Hydroxyhygric acid', 'X01275', 'D-arabinose', '(+)-Costunolide_257',
         'N8-Acetylspermidine', 'H00798', 'N-Acetylputrescine', 'H03322', 'X00309', 'Daurisoline', 'Quinic acid',
         'H02583',
         'Anserine/Homocarnosine', '7-Methylguanine', 'X00107', 'Ribulose 5-phosphate', 'Sulfuretin'],
        ['2-Picolinic acid', '3-Methyl-2-oxovaleric acid', 'Uracil', 'Acetylmuramic acid', 'Hypoxanthine',
         'Nicotinic acid ribonucleoside', 'Urocanic acid', 'X00394', 'X00151', 'Xanthine', 'H00524', 'Allopurinol_421',
         'Pyruvic acid', 'H00079', 'Malic acid', 'X00736', 'Thiamine', 'H00277', 'N-(5-Aminopentyl)acetamide_184'],
        ['X00138', 'N-Acetyl-5-hydroxytryptamine', 'Tryptamine', '2-Methylbutyrylglycine', 'Patulin_548', 'H00171',
         'H00207', 'Diethanolamine', '5-Hydroxytryptamine creatinine sulfate monohydrate', 'X00509', 'ectoine',
         'X04612',
         'Pipecolinic acid', 'Salicylic acid', 'H00553', 'Inulicin', 'Nordihydroguaiaretic acid', 'X08212'],
        ['H00890', 'X01182', 'H00417', '3-Hydroxycinnamic acid', '3-Hydroxybenzoic acid', 'X00637', 'H00579', 'X00514',
         'H01305', 'gamma-Aminobutyric acid', 'X00639', 'Lotaustralin', 'beta-Hydroxyisovaleric acid', 'H00743',
         'H00198',
         'X03337', 'H00287'],
        ['X00462', 'Piperidine_556', '2-Aminoadipic acid', 'Deoxyuridine', '5-Aminovaleric acid', 'Proline', 'Cytosine',
         'H00595', 'Thymidine', 'Lauramidopropyl betaine', 'Indoline_479', 'H00520', 'H01040', 'N-Acetylarginine',
         'Deoxyguanosine', 'H00630'],
        ['Methyl gallate', 'Genipin', 'H03399', 'X00587', 'X02359', 'Hexose trimer', 'Stachyose',
         'Proline/(R)-pyrrolidine-2-carboxylic acid', 'N-Acetylneuraminic acid', 'H00202', 'X03645', 'Creatinine',
         'Pinitol', 'SL00418', 'L-Quebrachitol', 'H01387'],
        ['Catechin', 'X01738', 'X00980', 'X00708', 'X09476', 'Dihydrocucurbitacin B', 'Deoxyelephantopin',
         'Enterolactone_458', 'Gomisin J', 'X00382', 'Oridonin', 'Enterolactone_459', '7beta-Hydroxylathyrol', 'H03845',
         'X00100'], ['X02114', '2-Hydroxy-3-methylbutyric acid', 'Prolylhydroxyproline', 'H00823', 'Glucuronic acid',
                     'Pyroglutamic acid', '2-Hydroxy-2-methylbutanoic acid', 'N-Acetylgalactosamine',
                     'N-Acetylmannosamine',
                     'Adenosine', 'Galactosamine', 'Diaminopimelic acid', '2-Hydroxyisocaproic acid',
                     'N-Acetylornithine'],
        ['X07545', 'X03140', 'H03047', 'X00061', 'X00842', 'Norepinephrine', 'DOPA', 'X14186', 'X10785',
         'Castanospermine',
         'H00423', 'Bufotalin', 'X06638'],
        ['DL-Glutamine', 'Taurine', 'Alanine', 'Choline', 'Serine', 'H00270', 'Threonine', 'Asparagine', 'Histidine',
         'Glutamine', 'X01010', 'Tryptophan'],
        ['H02971', 'H00025', 'H01685', 'H00265', 'Carnitine', 'H00572', 'H02475', 'Fucose', 'N-Acetylaspartic acid',
         'H00762', '1-Methyladenosine', 'N-Acetylglutamic acid'],
        ['Pimelic acid', 'X03659', 'X01155', '4-Hydroxy-2,5-dimethyl-3(2H)-furanone', 'X00844', 'SL00035', 'Bicine',
         'X06380', 'Hippuric acid', '3-hydroxy-4,5-dimethyl-3(5H)-furanone', 'X01565'],
        ['Rhodojaponin III', 'X01347', 'X01033', 'Pentoxifylline', 'X02741', 'Quinine', 'X00336', 'X05089', 'X05359',
         'X12625', 'X00583'],
        ['H05669', 'H01450', 'X05466', 'X00927', 'H08607', 'X01605', 'X04291', 'H02554', 'H11880', 'X00775'],
        ['X05178', 'X06276', 'X00568', 'Cyclo(L-Phe-L-Pro)', 'X02378', 'X06478', 'X01038', 'X01185', 'X04952',
         'X14611'],
        ['Shikimic acid', 'H05210', 'X02748', 'H03536', 'H00332', 'H01061', 'H05721', 'H02505', 'H02245', 'H03548'],
        ['H03505', '3,3-Dimethylglutaric acid', 'H00266', 'X05711', 'H04800', 'X01331', 'X02482', 'H00956', 'X02025',
         'H03949'],
        ['X06643', 'X05760', 'H03349', 'X04161', 'H02768', 'a Zearalenol', 'Blinin', 'H02237', 'X13463', 'Ingenol'],
        ['Urobilin', 'Propyl gallate', '3-Phenyllactic acid', 'H00180', 'META-ETHYLPHENOL', 'X01002', 'X00220',
         'H00860',
         '4-Vinylphenol', 'H00768'],
        ['X04860', 'H03558', 'gamma-Caprolactone', 'Vanillin', 'X04183', 'X05705', 'X08701', 'X06691', 'X05456'],
        ['X00022', 'H00534', 'Stachydrine', 'H07398', 'H01019', 'H03435', 'Argininosuccinic acid', 'H00646', 'X07540'],
        ['X00043', '3-Methylglutaconic acid', 'H00346', 'X00455', 'Acetylcarnitine', 'X00246', 'X00757', 'H01009',
         'beta-Muricholic acid'],
        ['5-Hydroxyindole', 'Indole-3-lactic acid', 'N-Acetylmethionine', 'X00225', 'Indole-3-glyoxylic acid',
         'Puerarin',
         '5,6-Dihydrothymine', 'H00544', 'X00146'],
        ['X00097', 'Pyridoxine', 'H03896', 'X00224', 'X01099', 'Dimethylmalonic acid', 'H02108', 'H01407', 'X10202'],
        ['X08198', 'X00041', 'H00930', 'Pinocembrin', 'X01242', 'Asymmetric dimethylarginine', 'X00660', 'SL00194',
         'H00488'], ['N-Methylaspartic acid', '3-Hydroxybutyric acid', 'X01703', 'Valerylcarnitine',
                     '1-Aminocyclopropanecarboxylic acid', 'Pyridoxamine', "Pyridoxal 5'-phosphate", 'Methionine',
                     'Aspartic acid'],
        ['X04317', 'H00181', 'Isoliquiritigenin', 'Verrucarol', 'Prostaglandin E2', 'scyllo-Inositol', 'Butein',
         '2-Oxo-3-phenylpropanoic acid', 'X00590'],
        ['X01909', 'Isofraxidin', 'H00447', 'X03744', 'H06253', 'H10665', 'H02257', '5-Methyluridine', 'H09307'],
        ['X06269', 'Leucylalanine', 'H00096', 'X00599', 'Glycylleucine', 'H00253', 'H02415', 'H01934'],
        ['Kirenol', 'Hexahydrocurcumin', 'X04156', 'H02615', 'N-Acetylhistidine', 'X05146', 'X08351', 'X00731'],
        ['2-Hydroxyphenylacetic acid', 'H01154', 'Vanillyl alcohol', 'X03155', 'X01498', 'X07085', 'X01114',
         'Gibberellin A3'],
        ['X00443', 'X02611', 'H02424', '4-Guanidinobutyric acid', 'X00543', 'X05119', 'SL00091', 'X06373'],
        ['3-Methylhistidine/ 1-Methylhistidine', 'H00353', 'X01923', 'Acetylagmatine', 'X03182',
         '3-Indoxylsulfuric acid',
         'Trigonelline', 'H00284'],
        ['delta-Gluconolactone/ delta-Gluconic acid delta-lactone', 'Decursinol', 'Kynurenine', 'X00834',
         'N-Methyl-2-pyrrolidone', "4'-O-Methylpyridoxine", 'beta-Alanine'],
        ['X06608', '4-pyridoxic acid', 'H00543', 'X01683', 'O-Desmethylangolensin_94', 'Indole-3-acetic acid',
         '4-Hydroxybenzoic acid'],
        ['H01987', 'Guvacine hydrochloride', 'X01253', 'X00537', 'X02889', 'X00726', 'Traumatic acid'],
        ['Daidzein', 'Naringenin/Pinobanksin', '4-Hydroxyproline', 'Uridine', 'Glucose', 'Nicotinic acid', 'Pyridoxal'],
        ['SL00115', 'X14123', 'X01733', 'X05003', 'H02794', 'X02808'],
        ['X00528', 'Guanosine', 'X04006', 'Valine', 'H00547', 'HY-30220_(S)-2-Hydroxy-3-phenylpropanoic acid'],
        ['Dopamine', 'Tyrosine', 'H02734', '(+)-Costunolide_258', 'X03614', 'SL00069'],
        ['X00200', 'X01850', 'Imidazoleacetic acid', 'X01454', 'H00722', 'Citraconic acid'],
        ['H00517', 'X05938', 'Glaucocalyxin A', 'X01446', '4-Hydroxybenzaldehyde', 'H00451'],
        ['X00905', 'Veratridine', 'H02163', 'H04645', 'X04102'],
        ['H00276', 'H03656', 'Hexose dimer', 'Agmatine', 'Guanine'],
        ['O-Desmethylangolensin_545', 'X01578', 'H00035', 'Ononetin', 'Pantothenic acid'],
        ['X12234', 'X02147', 'Sebacic acid', 'X09130', 'H01633'],
        ['X03335', 'Transtorine', 'X00672', 'H01727', '3-Hydroxy-2-methyl-4-pyrone']]

    df_0_5 = clusters_to_df(cluster_data_0_5)
    df_0_4 = clusters_to_df(cluster_data_0_4)
    df_0_3 = clusters_to_df(cluster_data_0_3)
    df_0_2 = clusters_to_df(cluster_data_0_2)
    # Also prepare explore versions (using same data)
    df_0_5_explore = df_0_5.copy()
    df_0_4_explore = df_0_4.copy()
    df_0_3_explore = df_0_3.copy()
    df_0_2_explore = df_0_2.copy()

    try:
        fig_0_5 = px.sunburst(df_0_5, path=["Cluster", "Species"], values="Value", title="Threshold 0.5")
        fig_0_5.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_5 = pio.to_html(fig_0_5, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_05")
    except Exception as e:
        sunburst_html_0_5 = ""
    try:
        fig_0_4 = px.sunburst(df_0_4, path=["Cluster", "Species"], values="Value", title="Threshold 0.4")
        fig_0_4.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_4 = pio.to_html(fig_0_4, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_04")
    except Exception as e:
        sunburst_html_0_4 = ""
    try:
        fig_0_3 = px.sunburst(df_0_3, path=["Cluster", "Species"], values="Value", title="Threshold 0.3")
        fig_0_3.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_3 = pio.to_html(fig_0_3, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_03")
    except Exception as e:
        sunburst_html_0_3 = ""
    try:
        fig_0_2 = px.sunburst(df_0_2, path=["Cluster", "Species"], values="Value", title="Threshold 0.2")
        fig_0_2.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_2 = pio.to_html(fig_0_2, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_02")
    except Exception as e:
        sunburst_html_0_2 = ""

    try:
        explore_fig_0_5 = px.sunburst(df_0_5_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.5")
        explore_fig_0_5.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_5 = pio.to_html(explore_fig_0_5, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_05")
    except Exception as e:
        explore_sunburst_html_0_5 = ""
    try:
        explore_fig_0_3 = px.sunburst(df_0_3_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.3")
        explore_fig_0_3.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_3 = pio.to_html(explore_fig_0_3, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_03")
    except Exception as e:
        explore_sunburst_html_0_3 = ""
    try:
        explore_fig_0_4 = px.sunburst(df_0_4_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.4")
        explore_fig_0_4.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_4 = pio.to_html(explore_fig_0_4, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_04")
    except Exception as e:
        explore_sunburst_html_0_4 = ""
    try:
        explore_fig_0_2 = px.sunburst(df_0_2_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.2")
        explore_fig_0_2.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_2 = pio.to_html(explore_fig_0_2, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_02")
    except Exception as e:
        explore_sunburst_html_0_2 = ""

    # ileum suggestions from DB
    # otu_list = IleumCorrelation.objects.values_list('var2', flat=True).distinct().order_by('var2')
    # Check from file csv the ileum
    try:
        otu_csv_path = os.path.join(settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                                    "otu_to_metab.csv")
        df_otu = pd.read_csv(otu_csv_path , )
        otu_list = df_otu.iloc[:, 0].dropna().unique().tolist()
    except Exception as e:
        otu_list = []
        print(f"Error loading otu_to_metab.csv: {e}")

    return render(request, f"{host_type}/molecule.html", {
        'host_type': host_type.title(),
        'data_type': 'Metab',
        'description': 'Top 200 displayed only. Gene info from Ensembl REST.',
        # 'tissue_types': list(
        #     IleumCorrelation.objects.values_list('from_tissue', flat=True).distinct()
        # ),
        # Include your sunburst_html_* variables in context as before
        "sunburst_html_0_5": sunburst_html_0_5,
        "sunburst_html_0_4": sunburst_html_0_4,
        "sunburst_html_0_3": sunburst_html_0_3,
        "sunburst_html_0_2": sunburst_html_0_2,
        "explore_sunburst_html_0_5": explore_sunburst_html_0_5,
        "explore_sunburst_html_0_4": explore_sunburst_html_0_4,
        "explore_sunburst_html_0_3": explore_sunburst_html_0_3,
        "explore_sunburst_html_0_2": explore_sunburst_html_0_2,
        'otu_list': list(otu_list),
    })
#####################################


####################################
# Version of databse pg scfa
#####################################
def process_data_scfa2(request, host_type='isabrownv2'):
    """
    1) Builds three sunbursts from TSVs (unchanged).
    2) AJAX branches now query IleumCorrelation instead of reading CSVs.
    """
    # --- AJAX Handling ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # (A) Load tissue: list distinct var2 (variables)
        if 'load_tissue' in request.GET:
            tissue = request.GET.get('tissue')
            vars_qs = AcidCorrelation.objects.filter(
                Q(from_tissue=tissue) | Q(to_tissue=tissue)
            ).values_list('var2', flat=True).distinct().order_by('var2')
            return J({'variables': list(vars_qs)})

        # (D) Cluster Lookup branch remains unchanged
        if "cluster_lookup" in request.GET:
            selected_bacteria = request.GET.get("bacteria", "").strip()
            if selected_bacteria.endswith("_otu"):
                selected_bacteria = selected_bacteria[:-4]
            if selected_bacteria.startswith("s__"):
                prefix = "s__"
                core = selected_bacteria[3:].replace("_", " ")
                selected_bacteria = prefix + core
            else:
                selected_bacteria = selected_bacteria.replace("_", "")
            selected_bacteria = selected_bacteria.replace(" B", "_B").replace(" A", "_A")
            found = False
            cluster_found = None
            threshold = None

        # Common filters
        tissue = request.GET.get('tissue')
        if tissue is None:
            return J({'error': 'Missing tissue.'}, status=400)
        # base_tissue_q = Q(from_tissue=tissue) | Q(to_tissue=tissue)
        # here tissue is ileum to adapat for each case
        base_tissue_q = Q(from_tissue='acid') & Q(to_tissue=tissue)

        # (B) Single-var filtering
        if ('multi_variable' not in request.GET
            and 'table_filter' not in request.GET
            and 'cluster_lookup' not in request.GET
            and 'explore_table_filter' not in request.GET
            and 'explore_distribution' not in request.GET):
            var = request.GET.get('variable')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min  = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = AcidCorrelation.objects.filter(
                base_tissue_q,
                var2=var,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({'results': [], 'total_count': 0})
            top = filt.order_by('-correlation')[:100]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count})

        # (C) Multi-var filtering
        if 'multi_variable' in request.GET:
            variables = request.GET.getlist('variables[]')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min  = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = AcidCorrelation.objects.filter(
                base_tissue_q,
                var2__in=variables,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({'results': [], 'total_count': 0})
            top = filt.order_by('-correlation')[:100]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count})

        # (E) Table Filtering
        if 'table_filter' in request.GET:
            var = request.GET.get('variable')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min  = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = AcidCorrelation.objects.filter(
                base_tissue_q,
                var2=var,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({
                    'results': [],
                    'total_count': 0,
                    'overview': {'median': None, 'q1': None, 'q3': None}
                })
            top = filt.order_by('-correlation')[:200]

            results = []
            vals = [o.correlation for o in filt]
            overview = {
                'median': r3(np.median(vals)),
                'q1': r3(np.quantile(vals, 0.25)),
                'q3': r3(np.quantile(vals, 0.75)),
            }
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'Coefficient': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count, 'overview': overview})

        # (F) Explore distribution
        if 'explore_distribution' in request.GET:
            # qs = IleumCorrelation.objects.filter(base_tissue_q).values_list('correlation', flat=True)
            qs = (AcidCorrelation.objects
                  .filter(base_tissue_q, correlation__isnull=False)
                  .values_list('correlation', flat=True)
                  )
            series = list(qs)
            if not series:
                return J({'error': 'No data found.'}, status=400)
            stats = {
                'min': r3(min(series)),
                'q1': r3(np.quantile(series, 0.25)),
                'median': r3(np.median(series)),
                'q3': r3(np.quantile(series, 0.75)),
                'max': r3(max(series)),
            }
            return J({'distribution': {'correlation_values': series, 'stats': stats}})

        # (G) Explore table filter
        if 'explore_table_filter' in request.GET:
            try:
                corr_min = float(request.GET.get('corrMin', -1))
                corr_max = float(request.GET.get('corrMax', 1))
                acc_min  = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = AcidCorrelation.objects.filter(
                base_tissue_q,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            top = filt.order_by('-correlation')[:200]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            vals = [o.correlation for o in filt]
            overview = {
                'median': r3(np.median(vals)) if vals else None,
                'q1': r3(np.quantile(vals, 0.25)) if vals else None,
                'q3': r3(np.quantile(vals, 0.75)) if vals else None,
            }
            return J({'results': results, 'total_count': total_count, 'overview': overview})

        return J({'error': 'No recognized AJAX action.'}, status=400)

    # --- Non-AJAX: build sunbursts + context ---
    def clusters_to_df(data):
        rows = []
        for i, sublist in enumerate(data, start=1):
            cluster_name = f"Cluster {i}"
            for species in sublist:
                rows.append({"Cluster": cluster_name, "Species": species.replace("s__", ""), "Value": 1})
        return pd.DataFrame(rows)

    # ileum suggestions from DB
    # otu_list = IleumCorrelation.objects.values_list('var2', flat=True).distinct().order_by('var2')
    # Check from file csv the ileum
    try:
        otu_csv_path = os.path.join(settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                                    "otu_to_acid.csv")
        df_otu = pd.read_csv(otu_csv_path , )
        otu_list = df_otu.iloc[:, 0].dropna().unique().tolist()
    except Exception as e:
        otu_list = []
        print(f"Error loading otu_to_acid.csv: {e}")

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
    explore_top_samples_plot_html = pio.to_html(top_samples_plot, full_html=False)

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

    return render(request, f"{host_type}/scfa2.html", {
        'host_type': host_type.title(),
        'data_type': 'Acid',
        'description': 'Top 200 displayed only. Gene info from Ensembl REST.',
        'sunburst_plot': sunburst_plot_html,
        "top_samples_plot": top_samples_plot_html,
        # 'tissue_types': list(
        #     IleumCorrelation.objects.values_list('from_tissue', flat=True).distinct()
        # ),
        # Include your sunburst_html_* variables in context as before
        'otu_list': list(otu_list),
    })


#####################################

#####################################
# Version of databse pg Ileum
#####################################
import os
import json
import math
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio

from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render

# Adjust the import below to your actual model name and app

from Avapp.models import IleumCorrelation
# JSON-cleaning helper to strip NaN/Inf and convert numpy types

def _json_clean(x):
    if isinstance(x, dict):
        return {k: _json_clean(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_json_clean(v) for v in x]
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        x = float(x)
    try:
        f = float(x)
        if not math.isfinite(f):
            return None
        return f
    except Exception:
        return x

# JsonResponse wrapper enforcing no NaN/Inf

def J(payload, status=200):
    clean = _json_clean(payload)
    # will raise if any NaN/Inf slipped through
    test = json.dumps(clean, allow_nan=False, ensure_ascii=False)
    return JsonResponse(json.loads(test), status=status,
                        json_dumps_params={'allow_nan': False, 'ensure_ascii': False})

# Round to 3 decimals, drop non-finite

def r3(x):
    try:
        if x is None:
            return None
        v = float(x)
        if not math.isfinite(v):
            return None
        return round(v, 3)
    except Exception:
        return None

@csrf_exempt
def ileum_data_analysisv2(request, host_type='isabrownv2'):
    """
    1) Builds three sunbursts from TSVs (unchanged).
    2) AJAX branches now query IleumCorrelation instead of reading CSVs.
    """
    # --- AJAX Handling ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # (A) Load tissue: list distinct var2 (variables)
        if 'load_tissue' in request.GET:
            tissue = request.GET.get('tissue')
            vars_qs = IleumCorrelation.objects.filter(
                Q(from_tissue=tissue) | Q(to_tissue=tissue)
            ).values_list('var2', flat=True).distinct().order_by('var2')
            return J({'variables': list(vars_qs)})

        # (D) Cluster Lookup branch remains unchanged
        if "cluster_lookup" in request.GET:
            selected_bacteria = request.GET.get("bacteria", "").strip()
            if selected_bacteria.endswith("_otu"):
                selected_bacteria = selected_bacteria[:-4]
            if selected_bacteria.startswith("s__"):
                prefix = "s__"
                core = selected_bacteria[3:].replace("_", " ")
                selected_bacteria = prefix + core
            else:
                selected_bacteria = selected_bacteria.replace("_", "")
            selected_bacteria = selected_bacteria.replace(" B", "_B").replace(" A", "_A")
            found = False
            cluster_found = None
            threshold = None
            cluster_data_0_4 = [
                ["ENSGALG00010000369", "ENSGALG00010000239", "ENSGALG00010000358", "ENSGALG00010000246",
                 "ENSGALG00010000326", "ENSGALG00010012336", "ENSGALG00010000249", "ENSGALG00010013702",
                 "ENSGALG00010011857", "ENSGALG00010011555", "ENSGALG00010000309"],
                ["ENSGALG00010005481", "ENSGALG00010000318", "ENSGALG00010012927", "ENSGALG00010000354",
                 "SPIN1L", "ENSGALG00010000313", "ENSGALG00010000282", "ENSGALG00010013706",
                 "ENSGALG00010011467"],
                ["ENSGALG00010003614", "ENSGALG00010003644", "ENSGALG00010003646", "ENSGALG00010003635",
                 "ENSGALG00010003643", "ENSGALG00010003623", "ENSGALG00010003613", "ENSGALG00010003625",
                 "ENSGALG00010003640"],
                ["ENSGALG00010003565", "ENSGALG00010003584", "ENSGALG00010003563", "ENSGALG00010003575",
                 "ENSGALG00010003537", "ENSGALG00010003598", "ENSGALG00010003529",
                 "ENSGALG00010003576"], ["RAD54B", "SMC2", "TERF1", "BORA", "TTK", "CENPU"],
                ["ENSGALG00010013950", "ENSGALG00010023025", "ENSGALG00010019862", "ENSGALG00010018778",
                 "ENSGALG00010007736", "ENSGALG00010004169"],
                ["ENSGALG00010004938", "ENSGALG00010015531", "ENSGALG00010006725", "ENSGALG00010018789",
                 "ENSGALG00010007061"],
                ["ENSGALG00010006935", "ENSGALG00010007268", "ENSGALG00010013049", "ENSGALG00010003188",
                 "ENSGALG00010000968"],
                ["ENSGALG00010013151", "ENSGALG00010009922", "ENSGALG00010012494", "ENSGALG00010006950",
                 "ENSGALG00010015775"],
                ["ENSGALG00010013567", "ENSGALG00010015575", "ENSGALG00010004208", "ENSGALG00010012840",
                 "ENSGALG00010002797"]]

            cluster_data_0_3 = [
                ["ENSGALG00010003644", "ENSGALG00010003584", "ENSGALG00010003646", "ENSGALG00010003635",
                 "ENSGALG00010003643", "ENSGALG00010003537", "ENSGALG00010003598", "ENSGALG00010003640",
                 "ENSGALG00010003576", "ENSGALG00010003565", "ENSGALG00010003614", "ENSGALG00010003563",
                 "ENSGALG00010003575", "ENSGALG00010003613", "ENSGALG00010003623", "ENSGALG00010003625",
                 "ENSGALG00010003529"],
                ["ENSGALG00010000369", "ENSGALG00010000239", "ENSGALG00010000358", "ENSGALG00010000246",
                 "ENSGALG00010000326", "ENSGALG00010012336", "ENSGALG00010000249", "ENSGALG00010013702",
                 "ENSGALG00010011857", "ENSGALG00010011555", "ENSGALG00010000309"],
                ["ENSGALG00010007147", "ENSGALG00010020566", "ENSGALG00010005005", "ENSGALG00010013879",
                 "ENSGALG00010016272", "ENSGALG00010004331", "ENSGALG00010020188", "ENSGALG00010014786",
                 "ENSGALG00010020349"],
                ["MCPH1", "RAD54B", "SMC2", "TERF1", "TTK", "SFR1", "BORA", "CENPU", "CDC7"],
                ["ENSGALG00010005481", "ENSGALG00010000318", "ENSGALG00010012927", "ENSGALG00010000354",
                 "SPIN1L", "ENSGALG00010000313", "ENSGALG00010000282", "ENSGALG00010013706",
                 "ENSGALG00010011467"],
                ["ENSGALG00010018845", "ENSGALG00010004435", "ENSGALG00010029472", "ENSGALG00010010739",
                 "ENSGALG00010017298", "ENSGALG00010027000", "ENSGALG00010010563"],
                ["ENSGALG00010011821", "ENSGALG00010014495", "ENSGALG00010019286", "ENSGALG00010013571",
                 "ENSGALG00010006303", "MGAT4C", "ENSGALG00010011219"],
                ["ENSGALG00010019749", "ENSGALG00010008845", "ENSGALG00010010249", "IFNG",
                 "ENSGALG00010015609", "ENSGALG00010009075", "ENSGALG00010028505"],
                ["ENSGALG00010027048", "ENSGALG00010021910", "RNF17", "ENSGALG00010004565",
                 "ENSGALG00010017014", "ENSGALG00010019849"],
                ["ENSGALG00010013950", "ENSGALG00010023025", "ENSGALG00010019862", "ENSGALG00010018778",
                 "ENSGALG00010007736", "ENSGALG00010004169"],
                ["SLC5A12", "ENSGALG00010025255", "ENSGALG00010028699", "SPIA1", "DFNA5", "ABCA13"],
                ["ENSGALG00010012604", "ENSGALG00010011339", "ENSGALG00010013778", "ENSGALG00010003609",
                 "Metazoa_SRP", "ENSGALG00010005593"],
                ["ENSGALG00010019133", "ENSGALG00010021921", "CYP27C1", "ENSGALG00010004694",
                 "ENSGALG00010019251", "ENSGALG00010019729"],
                ["ENSGALG00010014044", "ENSGALG00010003482", "ENSGALG00010005192", "ENSGALG00010003556",
                 "ENSGALG00010009165", "ENSGALG00010004945"],
                ["S1PR4", "FAM65B", "TMEM132E", "ITGB7", "ENSGALG00010028467", "ENSGALG00010005585"],
                ["CAD", "TIMELESS", "CHEK1", "CDC6", "METTL13", "ESPL1"],
                ["ENSGALG00010003587", "HBE1", "ENSGALG00010008539", "ENSGALG00010005816",
                 "ENSGALG00010012306", "ENSGALG00010018888"],
                ["ENSGALG00010021256", "NT5C3B", "ENSGALG00010006172", "DHX58", "TAPBP",
                 "ENSGALG00010026316"],
                ["ENSGALG00010004692", "ENSGALG00010019809", "ENSGALG00010001039", "ENSGALG00010013730",
                 "ENSGALG00010002731", "ENSGALG00010006511"],
                ["ENSGALG00010013151", "ENSGALG00010009293", "ENSGALG00010009922", "ENSGALG00010012494",
                 "ENSGALG00010006950", "ENSGALG00010015775"],
                ["ENSGALG00010019528", "ENSGALG00010016717", "ENSGALG00010008868", "ENSGALG00010016196",
                 "ENSGALG00010027456", "ENSGALG00010014616"],
                ["RBP4A", "PRPS2", "TDO2", "FGB", "ALB", "TTR"],
                ["ENSGALG00010009046", "TRIM29", "ENSGALG00010010540", "ENSGALG00010006733",
                 "ENSGALG00010008611", "ENSGALG00010006990"],
                ["FMO4", "BPIFB3", "ANO5", "FETUB", "ADH1C", "ENSGALG00010021522"],
                ["ENSGALG00010008908", "ENSGALG00010016084", "ENSGALG00010007291", "ENSGALG00010007015",
                 "ENSGALG00010013738"], ["IL17REL", "CCL21", "IL20RA", "RLN3", "CTLA4"],
                ["BCL11A", "PIGQ", "ERICH3", "CARD10", "RAP1GAP2"],
                ["ENSGALG00010010328", "ENSGALG00010015394", "GJD2", "KCNA10", "ENSGALG00010013496"],
                ["ENSGALG00010013718", "ENSGALG00010023899", "ENSGALG00010009845", "ENSGALG00010023323",
                 "ENSGALG00010003093"],
                ["ENSGALG00010022369", "ENSGALG00010004742", "ENSGALG00010013059", "ENSGALG00010002563",
                 "ENSGALG00010019044"],
                ["ENSGALG00010006695", "ENSGALG00010019241", "ENSGALG00010011083", "ENSGALG00010022156",
                 "ENSGALG00010003421"],
                ["ENSGALG00010004938", "ENSGALG00010015531", "ENSGALG00010006725", "ENSGALG00010018789",
                 "ENSGALG00010007061"],
                ["NRG4", "ENSGALG00010025839", "ENSGALG00010016164", "ENSGALG00010014013",
                 "ENSGALG00010001538"],
                ["ENSGALG00010022350", "ENSGALG00010011194", "ENSGALG00010020372", "ENSGALG00010013540",
                 "ENSGALG00010023619"],
                ["ENSGALG00010000956", "ENSGALG00010013819", "ENSGALG00010005781", "ENSGALG00010006662",
                 "ENSGALG00010009729"], ["CDK5R1", "KIRREL3", "ACTG2", "GM2A", "RAB40C"],
                ["ENSGALG00010021499", "ENSGALG00010009865", "ENSGALG00010017370", "ENSGALG00010015757",
                 "CRISP2"], ["ENSGALG00010022963", "ENSGALG00010008367", "ENSGALG00010011411", "PARD6A",
                             "ENSGALG00010027708"],
                ["NUDT2", "ENSGALG00010009595", "CMC2", "TMEM167A", "NUDT7"],
                ["ENSGALG00010004563", "ENSGALG00010010656", "ENSGALG00010018798", "ENSGALG00010013279",
                 "ENSGALG00010016226"],
                ["ENSGALG00010013567", "ENSGALG00010015575", "ENSGALG00010004208", "ENSGALG00010012840",
                 "ENSGALG00010002797"], ["CISD3", "DNLZ", "NDUFAF8", "C12orf57", "C22orf39"],
                ["CPA6", "ENSGALG00010007958", "CYP24A1", "ENSGALG00010009096", "ENSGALG00010008676"],
                ["ENSGALG00010003520", "ENSGALG00010026158", "ENSGALG00010000094", "ENSGALG00010006722",
                 "ENSGALG00010023006"],
                ["ENSGALG00010025478", "ENSGALG00010005640", "ENSGALG00010011877", "NEK10",
                 "ENSGALG00010017474"],
                ["ENSGALG00010006729", "ENSGALG00010007722", "ENSGALG00010007652", "ENSGALG00010014422",
                 "ENSGALG00010010583"],
                ["ENSGALG00010029113", "ENSGALG00010019754", "ENSGALG00010011771", "ENSGALG00010020508",
                 "ENSGALG00010006938"],
                ["ENSGALG00010006935", "ENSGALG00010007268", "ENSGALG00010013049", "ENSGALG00010003188",
                 "ENSGALG00010000968"], ["CCDC186", "OVOA", "UGT8", "PLEKHA7", "ITPRID2"],
                ["ENSGALG00010007790", "ENSGALG00010025973", "ENSGALG00010012789", "ENSGALG00010004448",
                 "ENSGALG00010007119"], ["C21orf91", "TNFRSF4", "IGSF6", "ENSGALG00010002921", "AQP1"],
                ["ENSGALG00010010598", "ENSGALG00010001331", "ENSGALG00010009751", "ENSGALG00010003369",
                 "CRB1"],
                ["ENSGALG00010004915", "ENSGALG00010004490", "ENSGALG00010012319", "ENSGALG00010001063",
                 "ENSGALG00010006114"], ["LANCL1", "INTS8", "RABL6", "MORC1", "VPS26B"],
                ["MRPS14", "PSMC5", "PTRH2", "YRDC", "SNRPC"]]

            cluster_data_0_2 = [
                ["ENSGALG00010003644", "ENSGALG00010003584", "ENSGALG00010003646", "ENSGALG00010003635",
                 "ENSGALG00010003643", "ENSGALG00010003537", "ENSGALG00010003598", "ENSGALG00010003640",
                 "ENSGALG00010003576", "ENSGALG00010003565", "ENSGALG00010003614", "ENSGALG00010003563",
                 "ENSGALG00010003575", "ENSGALG00010003613", "ENSGALG00010003623", "ENSGALG00010003625",
                 "ENSGALG00010003529"],
                ["ENSGALG00010011339", "ENSGALG00010003287", "DCT", "ENSGALG00010012860",
                 "ENSGALG00010020937", "ENSGALG00010005593", "ENSGALG00010012604", "5_8S_rRNA", "PROZ",
                 "ENSGALG00010013134", "ENSGALG00010013778", "ENSGALG00010003609", "ENSGALG00010011473",
                 "Metazoa_SRP"],
                ["ENSGALG00010023640", "ENSGALG00010003932", "IYD", "ENSGALG00010029155",
                 "ENSGALG00010028831", "ENSGALG00010020326", "ENSGALG00010001357", "ENSGALG00010009944",
                 "ENSGALG00010022940", "ENSGALG00010023467", "ENSGALG00010023370"],
                ["ENSGALG00010000369", "ENSGALG00010000239", "ENSGALG00010000358", "ENSGALG00010000246",
                 "ENSGALG00010000326", "ENSGALG00010012336", "ENSGALG00010000249", "ENSGALG00010013702",
                 "ENSGALG00010011857", "ENSGALG00010011555", "ENSGALG00010000309"],
                ["ENSGALG00010019528", "ENSGALG00010016717", "ENSGALG00010029981", "ENSGALG00010006734",
                 "ENSGALG00010016196", "ENSGALG00010012385", "ENSGALG00010008868", "ENSGALG00010023608",
                 "ENSGALG00010018065", "ENSGALG00010027456", "ENSGALG00010014616"],
                ["ENSGALG00010027765", "ENSGALG00010026961", "ZIC1", "EN2", "ENSGALG00010027472",
                 "ENSGALG00010014498", "ENSGALG00010025332", "ENSGALG00010012478", "TFAP2B",
                 "ENSGALG00010014177", "ENSGALG00010003359"],
                ["ZNF804B", "ENSGALG00010023647", "ENSGALG00010009189", "ENSGALG00010012545",
                 "ENSGALG00010013188", "KCNQ2", "ENSGALG00010006555", "ENSGALG00010002898", "CHIR-AB1",
                 "C17H9ORF172", "ENSGALG00010024684"],
                ["ENSGALG00010004938", "ENSGALG00010006725", "ENSGALG00010008601", "ENSGALG00010007061",
                 "ENSGALG00010018789", "ENSGALG00010021808", "ENSGALG00010015531", "ENSGALG00010026383",
                 "ENSGALG00010023988", "ENSGALG00010002607"],
                ["ENSGALG00010000646", "CUX2", "NPS", "VSX1", "ENSGALG00010005419",
                 "ENSGALG00010009978", "ENSGALG00010003297", "EGR4", "CELF5", "ENSGALG00010020591"],
                ["ABHD17B", "SMIM5", "ENSGALG00010003215", "CTBS", "ENSGALG00010009619",
                 "ENSGALG00010007089", "ENSGALG00010006119", "ENSGALG00010014619", "ENSGALG00010006726",
                 "GUCA2B"],
                ["ENSGALG00010000497", "ENSGALG00010012448", "ENSGALG00010000892", "TSPAN19",
                 "ENSGALG00010014598", "VTCN1", "ENSGALG00010007293", "ENSGALG00010020347",
                 "ENSGALG00010011727", "ENSGALG00010018850"],
                ["RBP4A", "SPIA4", "PRPS2", "CYP2R1", "TDO2", "AQP9", "TTR", "ITIH3", "ALB", "FGB"],
                ["CD74", "KLHL18", "ENSGALG00010016511", "UBXN11", "MECR", "KIAA0040",
                 "ENSGALG00010023183", "ENSGALG00010024892", "DMB2", "ENSGALG00010022322"],
                ["CNDP1", "SLC38A2", "NADK2", "SMC5", "ENSGALG00010020106", "EEIG2", "PDP1", "IFT74",
                 "PLA2G4F", "USP16"],
                ["ENSGALG00010002950", "ENSGALG00010008597", "ENSGALG00010013683", "ENSGALG00010006925",
                 "ENSGALG00010015396", "ENSGALG00010000896", "ENSGALG00010015011", "ENSGALG00010015223",
                 "RNF2", "HSD17B3"],
                ["TGIF1", "SMAD7", "CBR3", "ENSGALG00010026534", "CXCL14", "MAP1LC3B", "SESN1", "BIK",
                 "PIK3IP1"],
                ["ENSGALG00010005813", "ENSGALG00010025177", "ENSGALG00010014845", "SLITRK5",
                 "ENSGALG00010020600", "ENSGALG00010025859", "ENSGALG00010004084", "ENSGALG00010005865",
                 "CADM2"],
                ["ENSGALG00010005481", "ENSGALG00010000318", "ENSGALG00010012927", "ENSGALG00010000354",
                 "SPIN1L", "ENSGALG00010000313", "ENSGALG00010000282", "ENSGALG00010013706",
                 "ENSGALG00010011467"],
                ["ENSGALG00010011486", "EGLN3", "ENSGALG00010021536", "CYP4V2", "ETNPPL",
                 "ENSGALG00010016771", "KBTBD11", "GYS2", "RD3"],
                ["ENSGALG00010014207", "ENSGALG00010025804", "ENSGALG00010003538", "CSDC2",
                 "ENSGALG00010004815", "ENSGALG00010008751", "ENSGALG00010006984", "NEUROD2",
                 "ENSGALG00010000192"],
                ["ENSGALG00010004321", "ENSGALG00010022785", "ENSGALG00010006565", "ENSGALG00010023745",
                 "ENSGALG00010014524", "GPM6A", "ENSGALG00010019562", "ENSGALG00010027042",
                 "ENSGALG00010012374"],
                ["ENSGALG00010004915", "ENSGALG00010023753", "ENSGALG00010023302", "ENSGALG00010004490",
                 "ENSGALG00010006114", "ENSGALG00010019075", "ENSGALG00010016162", "ENSGALG00010012319",
                 "ENSGALG00010001063"],
                ["ENSGALG00010007147", "ENSGALG00010020566", "ENSGALG00010005005", "ENSGALG00010013879",
                 "ENSGALG00010016272", "ENSGALG00010004331", "ENSGALG00010020188", "ENSGALG00010014786",
                 "ENSGALG00010020349"],
                ["CISD3", "DNLZ", "NDUFAF8", "C22orf39", "ENSGALG00010010051", "ENSGALG00010011443",
                 "APOC3", "C12orf57", "URM1"],
                ["MCPH1", "RAD54B", "SMC2", "TERF1", "TTK", "SFR1", "BORA", "CENPU", "CDC7"],
                ["ENSGALG00010023667", "ENSGALG00010004634", "ENSGALG00010008463", "NKX2-5", "MARCH4",
                 "ENSGALG00010020251", "FGF4", "ENSGALG00010009285", "ENSGALG00010010114"],
                ["ENSGALG00010007794", "ENSGALG00010012065", "ENSGALG00010007219", "ENSGALG00010023691",
                 "ENSGALG00010000847", "ENSGALG00010003514", "ENSGALG00010003284", "ENSGALG00010004517",
                 "ENSGALG00010008851"],
                ["ENSGALG00010022963", "ENSGALG00010011411", "ENSGALG00010013701", "PARD6A",
                 "ENSGALG00010027708", "ENSGALG00010008367", "KLHL35", "ENSGALG00010022882",
                 "ENSGALG00010018178"],
                ["ENSGALG00010007857", "ENSGALG00010016386", "IFNL3A", "IL4I1", "ENSGALG00010012743",
                 "ACOD1", "CD86", "ENSGALG00010013573", "SLC2A6"],
                ["ENSGALG00010022007", "ENSGALG00010025478", "ENSGALG00010005640", "ENSGALG00010011877",
                 "NEK10", "ENSGALG00010011206", "ENSGALG00010007205", "ENSGALG00010002230",
                 "ENSGALG00010017474"],
                ["ENSGALG00010003587", "ENSGALG00010018962", "HBE1", "ENSGALG00010008539",
                 "ENSGALG00010005816", "ENSGALG00010023072", "ENSGALG00010012306", "ENSGALG00010018888",
                 "ENSGALG00010009599"],
                ["ENSGALG00010010731", "ENSGALG00010008545", "ENSGALG00010025124", "ENSGALG00010012584",
                 "ENSGALG00010007738", "ENSGALG00010003151", "ENSGALG00010002695", "ENSGALG00010014627",
                 "ENSGALG00010006605"],
                ["ENSGALG00010000956", "SIM2", "ENSGALG00010006662", "ENSGALG00010009729",
                 "ENSGALG00010005781", "ENSGALG00010011032", "ENSGALG00010019338", "ENSGALG00010013819",
                 "ENSGALG00010008591"],
                ["ENSGALG00010013567", "ENSGALG00010004647", "ENSGALG00010006385", "ENSGALG00010002797",
                 "ENSGALG00010002021", "ENSGALG00010015575", "ENSGALG00010004208", "ENSGALG00010009893",
                 "ENSGALG00010012840"],
                ["MYD88", "B3GNT7", "TMEM248", "NT5C1B", "OTUD4", "SH2D6", "B4GALT1", "PFKP", "SUCO"],
                ["ENSGALG00010002861", "ENSGALG00010027655", "ENSGALG00010028331", "ENSGALG00010002945",
                 "ENSGALG00010001005", "ENSGALG00010025261", "ENSGALG00010002297", "ENSGALG00010023535",
                 "ENSGALG00010020647"],
                ["ENSGALG00010006879", "CACNG5", "ENSGALG00010015120", "ENSGALG00010027544",
                 "ENSGALG00010025675", "ENSGALG00010014113", "ENSGALG00010019651", "ENSGALG00010008566",
                 "SHOX"],
                ["ENSGALG00010026158", "ENSGALG00010006722", "ENSGALG00010013957", "ENSGALG00010000293",
                 "PDZRN4", "ENSGALG00010003520", "ENSGALG00010000094", "ENSGALG00010023006"],
                ["ENSGALG00010006981", "SYCE3", "OVAL", "ENSGALG00010007269", "ENSGALG00010010194",
                 "ENSGALG00010024455", "ENSGALG00010012465", "ENSGALG00010019877"],
                ["LGR4", "KIAA0319L", "ADAM28", "KALRN", "RNF19A", "PDLIM5", "BEND7", "PTK2"],
                ["ADRB1", "ENSGALG00010001779", "ATP13A2", "C1QL4", "ENSGALG00010027630",
                 "ENSGALG00010014048", "NRN1L", "ENSGALG00010011274"],
                ["CHEK1", "INSM1", "METTL13", "CAD", "ESPL1", "TIMELESS", "CDC6", "ENSGALG00010000338"],
                ["STARD4", "ENSGALG00010012919", "LRRC8B", "BST1", "GID8", "ENSGALG00010004684",
                 "PDLIM3", "ENSGALG00010026350"],
                ["ENSGALG00010006695", "ENSGALG00010007583", "ENSGALG00010016032", "ENSGALG00010022156",
                 "ENSGALG00010003421", "ENSGALG00010019241", "ENSGALG00010011083",
                 "ENSGALG00010005896"],
                ["ENSGALG00010004854", "PDK4", "ENSGALG00010029265", "ENSGALG00010026627",
                 "ENSGALG00010002740", "FTCD", "PCK1", "CYP2AC1"],
                ["FRS2", "ENSGALG00010019116", "ENSGALG00010024668", "PTPN21", "NHLRC2", "RO60",
                 "NBEAL1", "N4BP2"],
                ["ENSGALG00010019841", "ENSGALG00010027817", "ENSGALG00010003445", "ENSGALG00010006115",
                 "ENSGALG00010004783", "CNP1", "CCDC166", "ENSGALG00010013978"],
                ["ENSGALG00010009595", "ENSGALG00010001629", "CMC2", "ENSGALG00010011203", "TMEM167A",
                 "NUDT2", "ENSGALG00010029279", "NUDT7"],
                ["ZMYM4", "NPAT", "KIAA1549", "PLAGL2", "NR4A3", "SLC1A4", "NUP153", "SLC38A1"],
                ["ENSGALG00010005028", "ENSGALG00010018953", "ENSGALG00010005928", "ENSGALG00010011701",
                 "ENSGALG00010005754", "ENSGALG00010026450", "ENSGALG00010009134",
                 "ENSGALG00010029873"],
                ["CHST6", "NRBF2", "NMRK1", "ENSGALG00010009874", "RBM11", "ENSGALG00010011795",
                 "ENSGALG00010024764", "ARSK"],
                ["MFSD2B", "ENSGALG00010005673", "ENSGALG00010003890", "ENSGALG00010013647", "ART4",
                 "CACNB4", "ENSGALG00010011200", "NISCH"],
                ["ENSGALG00010030013", "RFX6", "SLC24A2", "ENSGALG00010006393", "RNPC3",
                 "ENSGALG00010019561", "ENSGALG00010020698", "ENSGALG00010026749"],
                ["ENSGALG00010023088", "ENSGALG00010006807", "ENSGALG00010011542", "ENSGALG00010020731",
                 "ENSGALG00010011199", "ENSGALG00010006003", "ENSGALG00010006258",
                 "ENSGALG00010019685"],
                ["U1", "ENSGALG00010014036", "ENSGALG00010011197", "ENSGALG00010015586",
                 "ENSGALG00010015996", "ENSGALG00010014271", "ENSGALG00010015387",
                 "ENSGALG00010003493"],
                ["ENSGALG00010010225", "ENSGALG00010001103", "ENSGALG00010016318", "ENSGALG00010001387",
                 "ENSGALG00010006656", "ENSGALG00010003492", "ENSGALG00010026728",
                 "ENSGALG00010008962"],
                ["ENSGALG00010020919", "ENSGALG00010015794", "ENSGALG00010024273", "ENSGALG00010013507",
                 "ENSGALG00010008643", "ENSGALG00010023735", "ENSGALG00010020639",
                 "ENSGALG00010019765"],
                ["ENSGALG00010014702", "GDF3", "ENSGALG00010000302", "IL10RA", "ENSGALG00010000427",
                 "ACAP1", "DOK2", "SASH3"],
                ["HTT", "BTBD7", "NF1", "HCFC2", "CEP97", "AKAP11", "MRTFB", "ATG2A"],
                ["ZFYVE26", "MBTD1", "ABCA5", "IFFO2", "MFSD4B", "CACNA1B", "ENSGALG00010012670",
                 "FOXO4"],
                ["ENSGALG00010021256", "OASL", "ENSGALG00010006172", "DEDD", "NT5C3B", "DHX58", "TAPBP",
                 "ENSGALG00010026316"],
                ["AKNA", "DGKZ", "LIMK1", "MAP4K1", "PPP1R9B", "CHST13", "ENSGALG00010017349", "EML3"],
                ["ENSGALG00010012764", "ENSGALG00010001565", "ENSGALG00010016467", "ENSGALG00010029083",
                 "ENSGALG00010026503", "ENSGALG00010018169", "ENSGALG00010019851",
                 "ENSGALG00010009014"],
                ["ENSGALG00010007778", "ENSGALG00010026238", "ENSGALG00010011624", "ENSGALG00010000925",
                 "ENSGALG00010006703", "ENSGALG00010011684", "ENSGALG00010006349",
                 "ENSGALG00010001472"],
                ["CCT3", "EWSR1", "RBM14", "RAVER1", "ENSGALG00010003882", "ENSGALG00010000398",
                 "DCAF15", "ENSGALG00010000581"],
                ["ENSGALG00010026555", "ENSGALG00010006213", "ENSGALG00010029096", "ENSGALG00010009438",
                 "ENSGALG00010021547", "ENSGALG00010026408", "ENSGALG00010009604",
                 "ENSGALG00010014623"],
                ["RBP2", "ENSGALG00010015262", "ENSGALG00010015519", "ENSGALG00010014652", "CCDC112",
                 "ENSGALG00010023463", "FSTL5", "CTXN2"],
                ["DYNLT3", "FHL5", "AP4S1", "FAM105A", "CPNE3", "TBC1D15", "ENSGALG00010011294",
                 "ENSGALG00010011457"],
                ["ENSGALG00010027613", "ENSGALG00010014239", "ENSGALG00010004566", "ENSGALG00010014978",
                 "ENSGALG00010024411", "ENSGALG00010029819", "ENSGALG00010019917",
                 "ENSGALG00010004909"],
                ["ENSGALG00010004692", "ENSGALG00010019809", "ENSGALG00010006511", "ENSGALG00010002731",
                 "ENSGALG00010013730", "ENSGALG00010001039", "5_8S_rRNA", "ENSGALG00010018151"],
                ["ENSGALG00010027354", "ENSGALG00010000273", "ASTN1", "ENSGALG00010000418",
                 "ENSGALG00010029818", "ENSGALG00010000692", "MDGA1", "ENSGALG00010004090"],
                ["TMPRSS2", "GPT2", "ENSGALG00010010110", "CDS1", "F2RL1", "CHMP4C", "GPR85", "STYK1"],
                ["ENSGALG00010019522", "ENSGALG00010015273", "ENSGALG00010029113", "ENSGALG00010019672",
                 "ENSGALG00010019754", "ENSGALG00010011771", "ENSGALG00010020508",
                 "ENSGALG00010006938"],
                ["ENSGALG00010017719", "ENSGALG00010025561", "USP53", "ENSGALG00010017731", "SYTL5",
                 "ENSGALG00010026526", "FAM83B", "ENSGALG00010017736"],
                ["ENSGALG00010021991", "ENSGALG00010021499", "ENSGALG00010000909", "ENSGALG00010017370",
                 "ENSGALG00010015757", "ENSGALG00010014322", "CRISP2", "ENSGALG00010009865"],
                ["SMYD3", "NSA2", "RFXAP", "ENSGALG00010004979", "EIF3M", "MSANTD4",
                 "ENSGALG00010011757"],
                ["ENSGALG00010010526", "ENSGALG00010015568", "ENSGALG00010007062", "ENSGALG00010013088",
                 "ENSGALG00010024248", "ENSGALG00010004840", "ENSGALG00010004998"],
                ["APRT", "BSPRY", "DCTN6", "BRINP1", "TIMM23B", "FKBP1A", "ENSGALG00010028966"],
                ["GADD45G", "FAM26F", "SOCS1", "CD274", "K123", "ENSGALG00010029641",
                 "ENSGALG00010008831"], ["H2AFZ", "TUBB6", "APTX", "EBNA1BP2", "RPA2", "ALG8", "PSMD7"],
                ["ENSGALG00010009446", "RPS27L", "COX6C", "LGALS2", "IL15", "TXN", "GLRX"],
                ["ENSGALG00010001094", "IL22", "IL26", "IL17F", "MMP7", "ENSGALG00010001359", "WHRN"],
                ["HTR1D", "ENSGALG00010003099", "ENSGALG00010015526", "TFAP2C", "ENSGALG00010001533",
                 "ENSGALG00010003231", "ENSGALG00010012392"],
                ["ENSGALG00010002963", "ENSGALG00010001631", "ENSGALG00010001609", "ENSGALG00010025146",
                 "RAG2", "ENSGALG00010002862", "ENSGALG00010005693"],
                ["POLL", "TMEM8B", "SLC6A20", "ENSGALG00010015376", "FHOD1", "CAPN14", "NKX6-2"],
                ["ENSGALG00010011089", "ENSGALG00010004873", "ENSGALG00010025166", "ENSGALG00010007769",
                 "ENSGALG00010010181", "ENSGALG00010025636", "ENSGALG00010013243"],
                ["ENSGALG00010029167", "RASGRF2", "MALRD1", "CCSER2", "ENSGALG00010010832",
                 "ENSGALG00010018857", "DLG5"],
                ["FAM168A", "MAB21L1", "FZD1", "NUP93", "ENSGALG00010012456", "ENSGALG00010024132",
                 "ENSGALG00010003152"],
                ["ENSGALG00010013569", "ENSGALG00010012258", "ENSGALG00010022106", "CNTNAP5",
                 "ENSGALG00010006275", "ENSGALG00010008692", "ENSGALG00010018918"],
                ["ACMSD", "CALM2", "MCUR1", "ENSGALG00010013167", "SAR1B", "PPIL6",
                 "ENSGALG00010019793"],
                ["TRADD", "ACACA", "ARHGEF12", "SETD1A", "UNK", "ASH1L", "GNA13"],
                ["CAPN3", "GPR155", "E4F1", "MTR", "CCND2", "TMEM68", "ENSGALG00010008298"],
                ["TMCC1", "ENSGALG00010012096", "DSG2", "ENSGALG00010018079", "EZR", "FOXJ3", "NRDE2"],
                ["BIN2", "CYTIP", "RAC2", "TRAF3IP3", "ENSGALG00010028649", "CD247", "CD48"],
                ["TRABD", "WDR3", "UHRF1", "RAD54L", "MCM4", "SMC4", "RPA1"],
                ["COPE", "DRG1", "SSR3", "DFFA", "MRPL19", "SSBP1", "SNRPD3"],
                ["ENSGALG00010011102", "TMEM60", "C8orf76", "GTPBP8", "ENSGALG00010016620", "EIF3H",
                 "LECT2"], ["ENSGALG00010029541", "TNFRSF9", "TMSB4X", "ENSGALG00010023671", "SYTL1",
                            "ENSGALG00010015272", "SLC31A2"],
                ["MXI1", "RHPN1", "RNF103", "GPR83L", "CDHR5", "GCH1", "ENSGALG00010011814"],
                ["HOXC10", "ENSGALG00010017321", "ENSGALG00010010464", "ENSGALG00010006882",
                 "ENSGALG00010015385", "ENSGALG00010015599", "ENSGALG00010010673"],
                ["ENSGALG00010011821", "ENSGALG00010014495", "ENSGALG00010019286", "ENSGALG00010013571",
                 "ENSGALG00010006303", "MGAT4C", "ENSGALG00010011219"],
                ["ENSGALG00010026829", "ENSGALG00010023577", "ENSGALG00010010229", "ENSGALG00010004259",
                 "ENSGALG00010014879", "ENSGALG00010004573", "ENSGALG00010014782"],
                ["ENSGALG00010022369", "ENSGALG00010009869", "ENSGALG00010004742", "ENSGALG00010013059",
                 "ENSGALG00010002563", "ENSGALG00010019044", "ENSGALG00010026863"],
                ["ENSGALG00010020466", "ENSGALG00010028077", "ENSGALG00010019347", "GPR153", "DEFB4A",
                 "ENSGALG00010006767", "GHSR"],
                ["SYAP1", "ST7", "ENSGALG00010016582", "PTGR3", "UEVLD", "TSPAN13", "RAB2A"],
                ["DGLUCY", "TRAK1", "MCF2", "ENSGALG00010015935", "DAB1", "SGPL1", "NF2L"],
                ["OVALY", "ENSGALG00010023901", "ENSGALG00010003548", "ENSGALG00010022543", "CYP7A1",
                 "ENSGALG00010006122", "ENSGALG00010023599"],
                ["ENSGALG00010001049", "ENSGALG00010015216", "LIN28A", "DDX25", "ATP6AP1L",
                 "ENSGALG00010029794", "ENSGALG00010017853"],
                ["ENSGALG00010026359", "ENSGALG00010010772", "ENSGALG00010010660", "ENSGALG00010014998",
                 "ENSGALG00010019465", "ENSGALG00010010757", "VSTM2A"],
                ["ENSGALG00010019909", "5_8S_rRNA", "ENSGALG00010000500", "ENSGALG00010012211",
                 "ENSGALG00010026622", "HINTW", "ENSGALG00010006326"],
                ["ENSGALG00010020028", "ENSGALG00010018325", "ENSGALG00010003076", "SACS",
                 "ENSGALG00010005012", "ENSGALG00010011707", "RAB3C"],
                ["ENSGALG00010004023", "ENSGALG00010011279", "EFCAB10", "ENSGALG00010010264",
                 "ENSGALG00010016813", "KCNG4", "ENSGALG00010028236"],
                ["DLGAP2", "ENSGALG00010028035", "ENSGALG00010022740", "ENSGALG00010027418",
                 "ENSGALG00010027452", "ENSGALG00010000769", "FAM124B"],
                ["ENSGALG00010020645", "ENSGALG00010011656", "ENSGALG00010030078", "ENSGALG00010000895",
                 "LRRTM1", "ENSGALG00010030080", "LRRC6"],
                ["ENSGALG00010019749", "ENSGALG00010008845", "ENSGALG00010010249", "IFNG",
                 "ENSGALG00010015609", "ENSGALG00010009075", "ENSGALG00010028505"],
                ["CDCP1", "MAP7D2", "FNBP1L", "RAB11FIP1", "DPP8", "ACSL5", "NECTIN3"],
                ["RAB11FIP2", "CCDC102B", "ENSGALG00010014419", "FBXO30", "FEM1C", "ENSGALG00010026407",
                 "ENSGALG00010028358"],
                ["UBE2J2", "RAB19", "KIF5B", "YTHDF3", "TMF1", "PDZD8", "ITFG1"],
                ["ENSGALG00010025076", "ENSGALG00010012609", "ENSGALG00010020322", "ENSGALG00010030018",
                 "ENSGALG00010025567", "ENSGALG00010017461", "ENSGALG00010007498"],
                ["ENSGALG00010026415", "ENSGALG00010026853", "LRRC7", "ENSGALG00010011237",
                 "ENSGALG00010026487", "ENSGALG00010010469", "ENSGALG00010001662"],
                ["ENSGALG00010014044", "ENSGALG00010003482", "ENSGALG00010005192", "ENSGALG00010003556",
                 "ENSGALG00010009165", "ENSGALG00010004945", "GDAP1L1"],
                ["ENSGALG00010028261", "ENSGALG00010000076", "ENSGALG00010008018", "YJU2B",
                 "ENSGALG00010025159", "ENSGALG00010010708", "ENSGALG00010004957"],
                ["ENSGALG00010018845", "ENSGALG00010004435", "ENSGALG00010029472", "ENSGALG00010010739",
                 "ENSGALG00010017298", "ENSGALG00010027000", "ENSGALG00010010563"],
                ["HMGN5", "PSMA2", "ALKBH8", "CRCP", "EIF2S1", "MOXD1", "RSL24D1"],
                ["STON2", "ENSGALG00010025731", "ENSGALG00010001625", "MYZAP", "SH3TC1", "LCORL",
                 "RGS12"], ["PPP1R36", "ENSGALG00010028446", "ENSGALG00010018884", "ENSGALG00010009877",
                            "ENSGALG00010008744", "ENSGALG00010017073", "ENSGALG00010005239"],
                ["ENSGALG00010027048", "ENSGALG00010021910", "RNF17", "ENSGALG00010004565",
                 "ENSGALG00010017014", "ENSGALG00010019849"],
                ["MBIP", "BRD9", "TRMT10C", "TBPL1", "RTF1", "PKDCC"],
                ["ENSGALG00010016326", "TMEM168", "NLRC5", "UBAP1", "ARHGAP22", "ENSGALG00010019699"],
                ["ENSGALG00010007768", "ENSGALG00010013216", "ENSGALG00010026996", "ENSGALG00010002618",
                 "ENSGALG00010026752", "ENSGALG00010003853"],
                ["TMTC4", "YES1", "SUPT20H", "OVOL2", "PEX1", "OPA1"],
                ["SREBF2", "PHACTR4", "MXD1", "KBTBD4", "CTNND1", "MFSD13A"],
                ["PPP1R14D", "AP1S3", "FAS", "SELENOF", "ODF2L", "FAM18B1"],
                ["NDUFB6", "MRPL2", "ENSGALG00010024944", "ENSGALG00010010869", "PLP2",
                 "ENSGALG00010027713"],
                ["ENSGALG00010019696", "FBXO32", "MAN1A1", "CYBRD1", "NGEF", "CD36"],
                ["NUAK2", "MGAT4C", "FEV", "SLC36A1", "PLEKHJ1", "ENSGALG00010018401"],
                ["N4BP3", "WNT1", "NEIL1", "ENSGALG00010000771", "TUSC1", "MCAT"],
                ["GATA3", "ENSGALG00010028834", "CDC20B", "ENSGALG00010015868", "ENSGALG00010017197",
                 "ENSGALG00010018934"],
                ["WDR34", "JMJD6", "ENSGALG00010029207", "NES", "PRR11", "PRC1"],
                ["TPBG", "MRE11", "WDHD1", "SCML2", "SLITRK2", "DHTKD1"],
                ["IFNGR1", "ENSGALG00010012194", "ENSGALG00010010788", "CPT1A", "LYN", "KCTD20"],
                ["LRRC38", "FAM179A", "KCTD15", "ZC4H2", "ENSGALG00010026753", "ENSGALG00010020003"],
                ["ENSGALG00010012541", "ENSGALG00010027153", "RBMS1", "CPQ", "PARVB", "GPR52"],
                ["ENSGALG00010003953", "ENSGALG00010010696", "ENSGALG00010004336", "DIRAS2", "C4orf54",
                 "CD163L"], ["PHF19", "SPTBN2", "DNMT1", "NOTCH1", "ENSGALG00010005263", "ARHGEF2"],
                ["ENSGALG00010013115", "KCNE2", "ENSGALG00010013097", "ENSGALG00010005050", "GINM1",
                 "ENSGALG00010008994"],
                ["ENSGALG00010017668", "SH2D1A", "CD8BP", "NLRC3", "GLIPR1", "CD38"],
                ["SEL1L", "ATP11B", "PDP2", "PARP4", "SMAD5", "TRAPPC10"],
                ["INPP5D", "NCKAP1L", "RASSF2", "SLC43A3", "ADAM33", "PDE4B"],
                ["POLR3A", "OMD", "MSMP", "TNFRSF19", "PITRM1", "CEP152"],
                ["MAML1", "PHC3", "RC3H1", "HIPK3", "KIF13B", "TET2"],
                ["ENSGALG00010007766", "SP4", "ENSGALG00010025883", "LRCH2", "ENSGALG00010017156",
                 "DNAH3"], ["RBM7", "TAF11", "ANXA2", "CKB", "ENSGALG00010025126", "H3F3B"],
                ["INTS7", "URB1", "HEATR1", "SFPQ", "ENSGALG00010025369", "ADAMTS14"],
                ["ENSGALG00010013151", "ENSGALG00010009293", "ENSGALG00010009922", "ENSGALG00010012494",
                 "ENSGALG00010006950", "ENSGALG00010015775"],
                ["PLEKHM2", "CHPF", "KIAA1522", "VPS51", "UBL7", "RNF25"],
                ["ENSGALG00010019681", "ENSGALG00010004911", "SCN5A", "GJA3", "ENSGALG00010025254",
                 "ENSGALG00010012827"], ["NCOR1", "WAPL", "MED13L", "MED13", "KAT6A", "RNF111"],
                ["ENSGALG00010014187", "ENSGALG00010010123", "HOXA11", "ENSGALG00010001077",
                 "ENSGALG00010006610", "ENSGALG00010008944"],
                ["ENSGALG00010020557", "NAMPTP1", "ENSGALG00010020087", "IFNAR1", "CHPT1", "SLC37A1"],
                ["ANXA1", "ZC3HAV1L", "GCG", "RCAN1", "PDPN", "RAD51AP1"],
                ["IGDCC3", "ENSGALG00010002633", "ENSGALG00010019645", "ITIH6", "CORO7", "ZBTB25"],
                ["ENSGALG00010017238", "ENSGALG00010022011", "ENSGALG00010004213", "ENSGALG00010005378",
                 "ENSGALG00010009789", "ENSGALG00010025035"],
                ["PHF3", "TRAF6", "CEP120", "DCUN1D3", "ZBTB21", "ENSGALG00010014649"],
                ["CD5", "HCK", "IL21R", "RASAL3", "CARMIL2", "IRF4"],
                ["ENSGALG00010019853", "ENSGALG00010006870", "STC1", "ENSGALG00010010241",
                 "ENSGALG00010007103", "ENSGALG00010018610"],
                ["CKMT2", "ENSGALG00010016992", "PRR35", "ENSGALG00010016595", "ENSGALG00010000230",
                 "ENSGALG00010002279"],
                ["FAM136A", "ENSGALG00010010059", "GRHPR", "HYLS1", "ENSGALG00010000303", "PSMC3IP"],
                ["RPL11", "RPS13", "IFT43", "RPS23", "RPS3A", "RPL24"],
                ["NRG3", "ENSGALG00010014462", "ENSGALG00010004376", "ENSGALG00010019276",
                 "ENSGALG00010011646", "ENSGALG00010003549"],
                ["ENSGALG00010003797", "MPZL1", "RRM2B", "SGK3", "DUSP3", "CRBN"],
                ["ENSGALG00010002602", "ENSGALG00010008665", "ENSGALG00010004551", "ENSGALG00010025352",
                 "ENSGALG00010013211", "ENSGALG00010019678"],
                ["AMPH", "JAM3", "COLEC12", "CDH11", "ROBO1", "SLIT2"],
                ["RELN", "DPP6", "ZNF536", "RASGRF1", "STAB2", "LRRN2"],
                ["ENSGALG00010018402", "ENSGALG00010021773", "ENSGALG00010017501", "ENSGALG00010011328",
                 "ENSGALG00010008626", "ENSGALG00010007782"],
                ["ENSGALG00010007570", "ENSGALG00010021899", "IL2", "ENSGALG00010001648", "ST18",
                 "ENSGALG00010005200"], ["ND4", "COX1", "COX2", "ND5", "CYTB", "COX3"],
                ["ENSGALG00010016194", "ENSGALG00010020380", "ENSGALG00010017527", "ENSGALG00010004637",
                 "ENSGALG00010006960", "ENSGALG00010009405"],
                ["ENSGALG00010026320", "TCERG1", "COL6A3", "FOCAD", "NEMP2", "BRD3"],
                ["TASOR2", "ENSGALG00010000081", "RUBCN", "ENTPD3", "CCDC92B", "RNF216"],
                ["HMGN2P46", "ATG10", "BBS5", "RBFA", "TEN1", "IL7"],
                ["CHMP3", "SEC22B", "ENSGALG00010005171", "NAXD", "ENSGALG00010018371", "LYSMD3"],
                ["ENSGALG00010011191", "ENSGALG00010016371", "ENSGALG00010004349", "ENSGALG00010022510",
                 "ENSGALG00010016608", "ENSGALG00010009110"],
                ["POU3F4", "SSTR4", "ENSGALG00010014548", "ENSGALG00010012776", "ENSGALG00010015527",
                 "ENSGALG00010009248"], ["RPF1", "DYL1", "SNRPB2", "MRPS10", "SNRNP48", "BCCIP"],
                ["DCLK3", "CASS4", "CELF2", "STK38", "CAVIN4", "RASGEF1A"],
                ["DNAH5", "ENSGALG00010014771", "ENSGALG00010008957", "ENSGALG00010012794",
                 "ENSGALG00010019365", "ENSGALG00010011914"],
                ["AICDA", "ENSGALG00010019117", "GPR132", "ENSGALG00010019270", "ENSGALG00010015192",
                 "TRAF5"],
                ["PAIP2B", "CTNS", "ENSGALG00010026726", "ENSGALG00010018771", "CWF19L2", "PPP1CC"],
                ["ENSGALG00010022621", "ENSGALG00010008531", "ENSGALG00010022447", "ENSGALG00010015559",
                 "ENSGALG00010025366", "ENSGALG00010014202"],
                ["NAA15", "HAUS6", "CHORDC1", "NCBP1", "NEDD1", "SKIV2L2"],
                ["ENSGALG00010008869", "ENSGALG00010008922", "ZIC3", "ENSGALG00010005876",
                 "ENSGALG00010002258", "ENSGALG00010004064"],
                ["EDAR", "CYP1B1", "NUCKS1", "NDNF", "ENSGALG00010025740", "NFIA"],
                ["REC114", "ENSGALG00010003524", "ENSGALG00010021828", "EMILIN3", "ENSGALG00010014826",
                 "ENSGALG00010016166"],
                ["ENSGALG00010008872", "RBM43", "ENSGALG00010028489", "PMAIP1", "GPR137B",
                 "ENSGALG00010015820"],
                ["ENSGALG00010019405", "ENSGALG00010026640", "ENSGALG00010014723", "ENSGALG00010017863",
                 "LEPR", "ENSGALG00010021150"], ["PTCH2", "KCNN3", "SNED1", "IGSF3", "LRP1", "RPRD2"],
                ["TNIP2", "CXCR1", "IL1R2", "TCEANC2", "PDXP", "MOB1A"],
                ["ETS2", "ENSGALG00010012060", "EIF6", "FOXK2", "PTPRE", "BRAP"],
                ["ENSGALG00010014374", "ENSGALG00010006786", "ZPAX", "ENSGALG00010009630",
                 "ENSGALG00010002117", "ENSGALG00010004816"],
                ["ENSGALG00010027645", "ENSGALG00010027164", "TCF7", "POU2AF1", "C15orf39",
                 "ENSGALG00010028246"],
                ["ENSGALG00010006556", "ANKRD33B", "ENSGALG00010003475", "ENSGALG00010003683",
                 "ENSGALG00010002320", "ENSGALG00010024066"],
                ["SAT1", "SLC1A1", "FBXO48", "ENSGALG00010029878", "AMN1", "ENSGALG00010018243"],
                ["NPY1R", "ENSGALG00010016363", "ENSGALG00010010233", "ENSGALG00010009023",
                 "ENSGALG00010001366", "ENSGALG00010010235"],
                ["ENSGALG00010006973", "ENSGALG00010014195", "ENSGALG00010019880", "ENSGALG00010008833",
                 "ENSGALG00010007008", "ENSGALG00010015480"],
                ["MED7", "ZRSR2", "RNF146", "SPTY2D1", "TAF8", "SDCBP"],
                ["ENC1", "ZHX2", "ARHGEF6", "ENSGALG00010015643", "RFTN1", "NUAK1"],
                ["ENSGALG00010011290", "GLRA2", "ENSGALG00010019229", "ENSGALG00010024390",
                 "ENSGALG00010025838", "ENSGALG00010010294"],
                ["KIAA0232", "PTAR1", "ENSGALG00010014039", "CCNT2", "PLPPR4", "TAB3"],
                ["SLC5A12", "ENSGALG00010025255", "ENSGALG00010028699", "SPIA1", "DFNA5", "ABCA13"],
                ["ENSGALG00010019133", "ENSGALG00010021921", "CYP27C1", "ENSGALG00010004694",
                 "ENSGALG00010019251", "ENSGALG00010019729"],
                ["ENSGALG00010002242", "ENSGALG00010000987", "ENSGALG00010012652", "ENSGALG00010019665",
                 "ENSGALG00010014558", "GABRQ"],
                ["MTTPL", "KLHL17", "FOXD1", "ENSGALG00010025560", "SIAH3", "ENSGALG00010027559"],
                ["GPR55", "ENSGALG00010017378", "ENSGALG00010028553", "CD8A", "TBXT",
                 "ENSGALG00010012145"],
                ["IL21", "ENSGALG00010008911", "ENSGALG00010007124", "ENSGALG00010004164",
                 "ENSGALG00010008953", "ENSGALG00010015307"],
                ["USP6NL", "CYTH3", "MKRN2", "GRAMD4", "HMBOX1", "ENSGALG00010023063"],
                ["SLC43A2", "TMEM117", "KRT80", "BRPF3", "ACVR2A", "MAPK1IP1L"],
                ["AMPD1", "HOXB13", "ENSGALG00010000181", "ENSGALG00010006117", "ENSGALG00010005455",
                 "ENSGALG00010000601"],
                ["ENSGALG00010012461", "ENSGALG00010016389", "ENSGALG00010027647", "EMX1",
                 "ENSGALG00010023475", "ENSGALG00010022914"],
                ["ROPN1L", "SRRM4", "ENSGALG00010018763", "ENSGALG00010011285", "ENSGALG00010028307",
                 "ENSGALG00010028890"],
                ["CTAGE1", "ENSGALG00010026840", "ENSGALG00010006295", "AFP", "ENSGALG00010009589",
                 "ENSGALG00010018392"],
                ["PPP1R26", "TECPR2", "KATNIP", "MAN1A2", "ENSGALG00010014954", "BROX"],
                ["RAB20", "RAP1GDS1", "VSIG4", "ENSGALG00010023963", "CYTL1", "FBXO33"],
                ["AIFM3", "NDUFAF6", "PRKN", "HGSNAT", "MTERF2", "PKP2"],
                ["SNAP29", "USP12", "ZBTB34", "COPS2", "ZNF644", "PEX2"],
                ["PTPN5", "SCNN1B", "DENND1A", "MYT1", "DISP2", "BTAF1"],
                ["ENSGALG00010006356", "ENSGALG00010002328", "ENSGALG00010023747", "ENSGALG00010018940",
                 "SMIM18", "ENSGALG00010013920"],
                ["ENSGALG00010013752", "ENSGALG00010012700", "LARP6L", "TDRD15", "ENSGALG00010005842",
                 "ENSGALG00010022658"],
                ["PWP1", "ENSGALG00010010771", "RAE1", "TRMT61A", "CENPH", "DCK2"],
                ["ENSGALG00010009046", "TRIM29", "ENSGALG00010010540", "ENSGALG00010006733",
                 "ENSGALG00010008611", "ENSGALG00010006990"],
                ["ENSGALG00010006089", "DSCAM", "ENSGALG00010026631", "SGCZ", "ENSGALG00010014196",
                 "MSX2"],
                ["AIF1L", "SUN2", "ENSGALG00010025600", "HRH2", "ENSGALG00010017323", "SH3BP1"],
                ["ENSGALG00010015082", "ENSGALG00010019626", "BMX", "ENSGALG00010024367",
                 "ENSGALG00010008826", "ENSGALG00010003569"],
                ["RUNX1", "CDK14", "PREX1", "PAG1", "CYFIP2", "TNRC6C"],
                ["ENSGALG00010026615", "ENSGALG00010024355", "ZBTB43", "VWA3A", "CCDC141", "IRAG1"],
                ["ENSGALG00010008041", "ENSGALG00010015639", "ENSGALG00010015058", "ENSGALG00010029885",
                 "ENSGALG00010016641", "ENSGALG00010016713"],
                ["ENSGALG00010013950", "ENSGALG00010023025", "ENSGALG00010019862", "ENSGALG00010018778",
                 "ENSGALG00010007736", "ENSGALG00010004169"],
                ["ANKRD9", "PACRG", "ENSGALG00010023594", "TIRAP", "C1orf43", "KXD1"],
                ["NATD1", "MYLIP", "MBP", "ENSGALG00010000078", "SH3GLB2", "TNIP1"],
                ["ALDH2", "RALY", "SLC2A11", "NUDT19", "HID1", "NBR1"],
                ["ENSGALG00010005639", "ENSGALG00010015672", "ENSGALG00010008778", "ENSGALG00010018954",
                 "USH1G", "ENSGALG00010003723"],
                ["GABRA1", "ENSGALG00010023920", "ENSGALG00010010342", "ENSGALG00010008818",
                 "ENSGALG00010024067", "ENSGALG00010025122"],
                ["NIPA2", "DECR1", "CA12", "ENSGALG00010008541", "ESCO1", "ANXA11"],
                ["ENSGALG00010015138", "PACSIN2", "INSIG2", "ENSGALG00010014394", "BCAR3", "CDC14B"],
                ["CXCR5", "P2RY6", "DOK5", "ENSGALG00010021391", "ENSGALG00010015199", "LRRC61"],
                ["NOP58", "PCNA", "RAN", "UTP18", "ENSGALG00010029439", "EDEM2"],
                ["REEP5", "ENSGALG00010020176", "CDC14A", "ISCA1", "MCFD2", "ZFYVE21"],
                ["ENSGALG00010023396", "ENSGALG00010022829", "ENSGALG00010026711", "ENSGALG00010008721",
                 "ENSGALG00010029103", "KLHL31"],
                ["ENSGALG00010007653", "CXCL13L2", "ENSGALG00010020795", "ENSGALG00010015873",
                 "ENSGALG00010006586", "ENSGALG00010019775"],
                ["ENSGALG00010008587", "ENSGALG00010014008", "ENSGALG00010022542", "ENSGALG00010007424",
                 "ENSGALG00010014071", "ENSGALG00010009723"],
                ["S1PR4", "FAM65B", "TMEM132E", "ITGB7", "ENSGALG00010028467", "ENSGALG00010005585"],
                ["TMIGD1", "SH3BP2", "MEP1B", "KCNJ16", "PIK3CB", "DPP4"],
                ["ENSGALG00010025843", "ENSGALG00010023085", "SLC45A2", "ZIC2", "ENSGALG00010002204",
                 "ENSGALG00010000911"],
                ["SPOCK3", "ENSGALG00010002485", "ENSGALG00010017254", "ENSGALG00010007390",
                 "ENSGALG00010010801", "ENSGALG00010017302"],
                ["ENSGALG00010028427", "ENSGALG00010000696", "ENSGALG00010023758", "TRIM45", "CETP",
                 "C1QA"],
                ["ENSGALG00010000344", "FAM210B", "ENSGALG00010011314", "ENSGALG00010017875", "MAB21L3",
                 "C3orf18"],
                ["ENSGALG00010003355", "ENSGALG00010018272", "ENSGALG00010025356", "ENSGALG00010018321",
                 "ENSGALG00010029460", "ENSGALG00010026343"],
                ["DDX20", "DUSP7", "NUFIP1", "ENSGALG00010019226", "ODC", "OR51E2"],
                ["WDR33", "ABL1", "ADAM11", "CDK12", "NUP98", "AGRN"],
                ["ENSGALG00010010239", "ENSGALG00010011766", "ENSGALG00010006419", "NELL1", "ASIP",
                 "ENSGALG00010007216"],
                ["ENSGALG00010011985", "CD200R1B", "ENSGALG00010027633", "ENSGALG00010015784", "CPO",
                 "ENSGALG00010010794"],
                ["ENSGALG00010003629", "ENSGALG00010013489", "TMEM215", "ENSGALG00010019304",
                 "ENSGALG00010016014", "ENSGALG00010014932"],
                ["ENSGALG00010021312", "ADSS1", "PPP1R19L", "LMTK2", "ENSGALG00010013079", "KDM4C"],
                ["OXLD1", "MTMR11", "ENSGALG00010027295", "ENSGALG00010026240", "FCSK", "CYB561D2"],
                ["ENSGALG00010008097", "ENSGALG00010003545", "ENSGALG00010026607", "ENSGALG00010014449",
                 "ENSGALG00010029100", "ENSGALG00010026254"],
                ["AMPD2", "CDON", "ENSGALG00010001780", "KIAA1324", "ZBTB7A", "FZD8"],
                ["CCNG2", "FBXL3", "SELENOP1", "TINAG", "PLEKHS1", "YPEL5"],
                ["EEF1E1", "GLRX2", "ENSGALG00010015356", "C9orf85", "SRSF10", "KRR1"],
                ["FAM3D", "FAM76A", "ENSGALG00010028298", "TMED10", "SDCBP2", "PUF60"],
                ["GALNT7", "MFN1", "DLD", "MICU2", "HMG20A", "PLS3"],
                ["METTL23", "DNAJA4", "ENSGALG00010026672", "ENSGALG00010024603", "TK1", "TOR1B"],
                ["ENSGALG00010016599", "ADRA2A", "ABCG5", "SLC22A16", "DAO", "USP2"],
                ["FMO4", "BPIFB3", "ANO5", "FETUB", "ADH1C", "ENSGALG00010021522"],
                ["IL1B", "CCL4", "IL13RA2", "ADM", "ENSGALG00010022313"],
                ["CACNA1S", "CCLI5", "ENSGALG00010028678", "ENSGALG00010004198", "ENSGALG00010025776"],
                ["RFX4", "ENSGALG00010011944", "AKAP7", "SUSD1", "MBLAC2"],
                ["ENSGALG00010007371", "ENSGALG00010006629", "TMEM181", "SPATA17", "PLCB1"],
                ["ENSGALG00010007776", "ENSGALG00010010704", "METTL4", "ANKRD26", "UBA2"],
                ["NSMCE2", "BAG1", "EIF3E", "ENSGALG00010002582", "ENSGALG00010024324"],
                ["ENSGALG00010006153", "U6", "ENSGALG00010005923", "ENSGALG00010027656",
                 "ENSGALG00010022331"],
                ["TBX21", "ENSGALG00010003777", "MPL", "ENSGALG00010027582", "RGS19"],
                ["PATL1", "ENSGALG00010019621", "KIAA1755", "HNRNPL", "GDF6"],
                ["ENSGALG00010006086", "ENSGALG00010015603", "ENSGALG00010024293", "ERC2", "CCDC66"],
                ["NBEA", "CLVS2", "CACNB2", "GDNF", "SEMA3A"],
                ["ENSGALG00010018908", "ENSGALG00010014951", "ENSGALG00010021524", "ENSGALG00010016009",
                 "DNM3"],
                ["ENSGALG00010013718", "ENSGALG00010023899", "ENSGALG00010009845", "ENSGALG00010023323",
                 "ENSGALG00010003093"], ["UBE2U", "C10orf2", "ENSGALG00010026195", "FARSA", "STIP1"],
                ["ENSGALG00010003826", "PURG", "ENSGALG00010028319", "LRRC34", "MAP3K15"],
                ["CASP8AP2", "ZNF148", "ENSGALG00010025836", "ABCB7", "ATM"],
                ["KCNJ15", "LRRC39", "ENSGALG00010029176", "ENSGALG00010001839", "ENSGALG00010006904"],
                ["UBQLN4", "STT3A", "PSMD2", "GUSB", "NUP62"],
                ["ANKRD28", "PRICKLE1", "CHRNB4", "ENSGALG00010026770", "ENSGALG00010027809"],
                ["ASH2L", "SH3GL2", "WNT16", "PBX1", "TSC22D2"],
                ["IFRD1", "CAMK2D", "ANGEL2", "ZBTB26", "ZFAND5"],
                ["SLC4A10", "ENSGALG00010017165", "ENSGALG00010002900", "ENSGALG00010023878",
                 "ENSGALG00010026848"],
                ["ENSGALG00010015707", "ENSGALG00010013090", "CRISP2", "IL12B", "SEPT14"],
                ["IMMP1L", "LSM5", "GNG13", "HAUS2", "THOC7"],
                ["ENSGALG00010024069", "GCK", "ENSGALG00010013509", "FCHSD1", "ALKBH4"],
                ["ENSGALG00010018445", "ENSGALG00010015781", "ENSGALG00010007587", "ENSGALG00010008854",
                 "ENSGALG00010028376"], ["ERI1", "ZNFY2", "GTF2F2", "NARS", "PCNP"],
                ["CTBP2", "ENSGALG00010012071", "DDRGK1", "TCEA1", "ZCRB1"],
                ["SFN", "ENSGALG00010025570", "ENSGALG00010006920", "ENSGALG00010008048",
                 "ENSGALG00010025792"], ["CTNNA1", "PEX14", "TAF5L", "RAB10", "CHUK"],
                ["ENSGALG00010008732", "ENSGALG00010007704", "ENSGALG00010018545", "ENSGALG00010026442",
                 "ENSGALG00010005308"], ["INAFM2", "ENSGALG00010006038", "ANAPC11", "MED29", "PIGBOS1"],
                ["ENSGALG00010023757", "ENSGALG00010009810", "CWC22", "JAK2", "VRK2"],
                ["ENSGALG00010014337", "ENSGALG00010014420", "ENSGALG00010023092", "CALN1",
                 "RNase_MRP"],
                ["ENSGALG00010019784", "ENSGALG00010004035", "ENSGALG00010019107", "ENSGALG00010018659",
                 "ENSGALG00010002286"], ["CMTR1", "RSAD2", "ENSGALG00010008221", "EPSTI1", "USP18"],
                ["FAM175A", "LIMS1", "SYCE2", "ENSGALG00010002540", "B3GALNT1"],
                ["SLC4A4", "MEI1", "HEATR5A", "TRAPPC9", "AREL1"],
                ["ENSGALG00010004532", "CENPW", "CENPQ", "PDIA4", "EIF1AX"],
                ["POMT2", "RBM33", "GPATCH2L", "GZF1", "FAM219A"],
                ["SSH2", "SH2B2", "APBA3", "ENSGALG00010025449", "ZDHHC18"],
                ["ENSGALG00010001519", "ENSGALG00010012012", "ENSGALG00010009687", "ENSGALG00010002221",
                 "ENSGALG00010010639"],
                ["ENSGALG00010020066", "MOB3C", "ENSGALG00010019700", "CXCL13L3", "TPD52L2"],
                ["ENSGALG00010018400", "DDX4", "SNX20", "LIX1", "GPR65"],
                ["ENSGALG00010015937", "SYNDIG1L", "SLC6A12", "ENSGALG00010028033", "AMDHD1"],
                ["ENSGALG00010006729", "ENSGALG00010007722", "ENSGALG00010007652", "ENSGALG00010014422",
                 "ENSGALG00010010583"], ["SIRT4", "MORN4", "PRKAG1", "BAAT", "FDXR"],
                ["AATF", "KIF15", "NOLC1", "DNA2", "MCM10"],
                ["ENSGALG00010023789", "ENSGALG00010026750", "DHRS9", "PHF21B", "ENSGALG00010006814"],
                ["RASL11A", "P4HA3", "NECAB3", "NPTXR", "GAL3ST1"],
                ["ENSGALG00010006147", "SLC6A1", "WASF3", "GPER1", "NTNG1"],
                ["ENSGALG00010026620", "ENSGALG00010025704", "SOX11", "ENSGALG00010022048", "OLFM1"],
                ["KDM7A", "MYO1E", "ADGRA3", "C2CD5", "ENSGALG00010016231"],
                ["GATAD2B", "NFIC", "UPF1", "CACNA2D2", "UBAP2L"],
                ["ENSGALG00010007790", "ENSGALG00010025973", "ENSGALG00010012789", "ENSGALG00010004448",
                 "ENSGALG00010007119"], ["PPP1R2", "MTDH", "SNX32", "MFSD8", "SDF4"],
                ["GPR20", "STK31", "RASGEF1B", "ENSGALG00010014345", "OPN3"],
                ["ENSGALG00010022501", "ENSGALG00010022570", "ENSGALG00010018637", "ENSGALG00010024348",
                 "ENSGALG00010014591"], ["LMO2", "ENSGALG00010005303", "BHLHA15", "PPAT", "SAA"],
                ["ENSGALG00010008837", "CNTN3", "OPNVA", "WDR27", "ITGA2"],
                ["C1orf232", "IL17RC", "DNAJC22", "C1orf74", "ENSGALG00010022968"],
                ["ENSGALG00010006587", "DTHD1", "ENSGALG00010019774", "GABRB2", "ENSGALG00010020042"],
                ["COA7", "AKR1D1", "ENSGALG00010016490", "ENSGALG00010021889", "ENSGALG00010009425"],
                ["LANCL1", "INTS8", "RABL6", "MORC1", "VPS26B"],
                ["DOCK2", "ENSGALG00010006445", "ABCG1", "WDFY4", "ANKRD44"],
                ["HNF4A", "VIPR1", "ENSGALG00010002866", "RAVER2", "AXL"],
                ["BCL11A", "PIGQ", "ERICH3", "CARD10", "RAP1GAP2"],
                ["SEL1L3", "ACTN2", "BMPR1A", "PANK3", "MAN2A1"],
                ["ENSGALG00010016176", "TTC36", "ENSGALG00010017412", "ENSGALG00010029078",
                 "ENSGALG00010007170"], ["ENSGALG00010019547", "USPL1", "SPICE1", "C5orf49", "ADAT1"],
                ["DPH2", "DSN1", "NCBP2", "THOC3", "ELOF1"],
                ["ENSGALG00010027989", "ZNF511", "TBL2", "ENSGALG00010029498", "AFMID"],
                ["ENSGALG00010014888", "ENSGALG00010003534", "ENSGALG00010013807", "ENSGALG00010021392",
                 "ENSGALG00010012585"], ["ATG101", "KLF8", "SPRYD3", "ENSGALG00010025572", "BCL7B"],
                ["ENSGALG00010013999", "ENSGALG00010016217", "ENSGALG00010014569", "ENSGALG00010010795",
                 "ENSGALG00010014660"], ["OGFOD3", "GABARAPL1", "PAPD5", "KCTD2", "MAPKAPK5"],
                ["EIF4EBP1", "MEAF6", "ZNF593", "HIST1H3H", "CCDC27"],
                ["ENSGALG00010006094", "ENSGALG00010028356", "ENSGALG00010007239", "ENSGALG00010012589",
                 "ENSGALG00010001095"],
                ["SLC12A3", "ENSGALG00010026778", "ENSGALG00010011265", "ENSGALG00010025681", "DCX"],
                ["RAB39B", "PFKFB2", "ARHGAP29", "ENSGALG00010030073", "PPP1R1C"],
                ["HMGCR", "PPP4R1", "SLC12A7", "TSPAN14", "MED17"],
                ["CDK5R1", "KIRREL3", "ACTG2", "GM2A", "RAB40C"],
                ["FTH1", "MED9", "HNRNPKL", "CDKN2A", "GPX1"],
                ["EZH2", "CCT8", "SDAD1", "FST", "METTL18"],
                ["ENSGALG00010023505", "RPUSD2", "PUS1", "ENSGALG00010023171", "KNSTRN"],
                ["FOXK1", "GBF1", "NPRL3", "INTS1", "EIF4G3"],
                ["ENSGALG00010005120", "MIXL1", "ENSGALG00010023659", "ENSGALG00010027514",
                 "ENSGALG00010023554"],
                ["ENSGALG00010013865", "LAMB4", "ENSGALG00010004570", "ENSGALG00010005196",
                 "ENSGALG00010023010"],
                ["ENSGALG00010009109", "ENSGALG00010010215", "CLDND1", "H2AFY", "ENSGALG00010012015"],
                ["ENSGALG00010012549", "ENSGALG00010007012", "ENSGALG00010009815", "ENSGALG00010014110",
                 "ENSGALG00010015818"],
                ["ENSGALG00010027625", "ENSGALG00010016645", "ENSGALG00010011442", "ENSGALG00010025284",
                 "ENSGALG00010026585"], ["HSPA13", "HMGCS1", "TXNRD1", "ICE2", "SLC30A7"],
                ["HOXB8", "ENSGALG00010012676", "ENSGALG00010005374", "MORN3", "ENSGALG00010016229"],
                ["ENSGALG00010020652", "NYX", "RUNX2", "ENSGALG00010018433", "GRIN2B"],
                ["ENSGALG00010004844", "AKAP6", "ENSGALG00010007058", "ENSGALG00010007190",
                 "ENSGALG00010005216"],
                ["BDKRB1", "ENSGALG00010026211", "ENSGALG00010007739", "SERPINA10", "MSANTD1"],
                ["SALL1", "MAP7D3", "CHRNA9", "ENSGALG00010005203", "CEP85L"],
                ["KSR2", "ENSGALG00010005361", "ENSGALG00010000310", "ENSGALG00010000316", "LACTBL1"],
                ["DIAPH3", "CDCA2", "CENPE", "BRIP1", "FBXO39"],
                ["LY6E", "DEDD", "PLACL2", "MAFF", "ENSGALG00010008187"],
                ["CHSY1", "ACTR8", "GPR39", "STX17", "UBE2D2"],
                ["ENSGALG00010020780", "ENSGALG00010015106", "IMPG2", "ENSGALG00010013764", "GNB3"],
                ["ENSGALG00010021551", "TET1", "ENSGALG00010020072", "ENSGALG00010023327", "LRP2"],
                ["TOMT", "ENSGALG00010004106", "ENSGALG00010023502", "ENSGALG00010000560",
                 "ENSGALG00010029856"],
                ["ENSGALG00010003839", "ART7B", "SMYD4", "ENSGALG00010004962", "SLC7A4"],
                ["CPA6", "ENSGALG00010007958", "CYP24A1", "ENSGALG00010009096", "ENSGALG00010008676"],
                ["SIPA1L2", "PDCD1LG2", "ENSGALG00010005295", "ZPLD1", "TC2N"],
                ["LINS1", "LIG4", "MIER3", "FGL2", "ENSGALG00010009811"],
                ["ANO3", "ZNF507", "RIMBP2", "RFX3", "DGKQ"],
                ["IL7R", "HDGFL3", "TREM2", "MMP27", "SATB1"],
                ["HPGD", "C7orf73", "FABP2", "ENSGALG00010029684", "ENSGALG00010020610"],
                ["HN1", "ENSGALG00010022500", "TTC19", "WDR53", "COX5A"],
                ["TRMT1L", "ENSGALG00010007232", "ARHGAP40", "PCDH11X", "TRPV1"],
                ["ACTR10", "ARMC6", "CARS2", "TMEM11", "PRKRIP1"],
                ["ARHGAP15", "FAM49A", "SYK", "TLR7", "IL18RAP"],
                ["ENSGALG00010024292", "ENSGALG00010003221", "ENSGALG00010003182", "ENSGALG00010004498",
                 "ENSGALG00010003196"], ["CHD9", "MBOAT2", "SMG1", "HDX", "PAK3"],
                ["CCDC186", "OVOA", "UGT8", "PLEKHA7", "ITPRID2"],
                ["LRRC49", "BICC1", "ENSGALG00010025162", "FIGN", "C12H3orf14"],
                ["PCYT2", "GHRH", "TMEM9", "DHDDS", "PIGW"],
                ["PRCP", "ENSGALG00010027790", "NMRAL1", "DRD5", "ENSGALG00010006163"],
                ["MRPS14", "PSMC5", "PTRH2", "YRDC", "SNRPC"],
                ["ENSGALG00010009037", "CACNA1F", "GRIN2C", "CBX4", "SIRPA"],
                ["DSCAML1", "MAL", "ENSGALG00010023876", "ENSGALG00010016441", "ENSGALG00010013058"],
                ["GPN2", "ENSGALG00010018536", "NHP2", "ENHO", "B4GALT7"],
                ["ENSGALG00010024359", "ENSGALG00010006669", "ENSGALG00010005665", "ENSGALG00010012294",
                 "ENSGALG00010027666"],
                ["ENSGALG00010010328", "ENSGALG00010015394", "GJD2", "KCNA10", "ENSGALG00010013496"],
                ["PREP", "ENSGALG00010007472", "PRR16", "ENSGALG00010008348", "PPP2R2C"],
                ["MTAP", "C9orf72", "CDC42SE2", "KLHL5", "RNASET2"],
                ["ENSGALG00010026498", "CEP170B", "DOCK5", "ENSGALG00010023346", "TAOK1"],
                ["STX2", "GIPC2", "KRAS", "LCORL", "TMTC3"],
                ["RPL32", "RPL26L1", "RPL36", "RPS2", "RPL7A"],
                ["ENSGALG00010009718", "ENSGALG00010006596", "ENSGALG00010026605", "C6orf120",
                 "ENSGALG00010027620"], ["ARSA", "SOWAHA", "RUNDC1", "RIC8A", "TAP2"],
                ["NRG4", "ENSGALG00010025839", "ENSGALG00010016164", "ENSGALG00010014013",
                 "ENSGALG00010001538"],
                ["TBC1D32", "CERKL", "ENSGALG00010011739", "CNTNAP2", "ENSGALG00010006617"],
                ["ENSGALG00010022350", "ENSGALG00010011194", "ENSGALG00010020372", "ENSGALG00010013540",
                 "ENSGALG00010023619"],
                ["ENSGALG00010005059", "ENSGALG00010009938", "ENSGALG00010011270", "ENSGALG00010010787",
                 "ENSGALG00010015506"], ["SMAD6", "ARHGDIG", "NT5DC4", "FAM219B", "TMEM45BL"],
                ["ENSGALG00010013864", "KCNK16", "PDE6B", "ENSGALG00010001996", "ENSGALG00010014401"],
                ["ENSGALG00010000256", "ENSGALG00010005822", "ENSGALG00010019151", "ENSGALG00010016401",
                 "ENSGALG00010003213"], ["BECN1", "TMX4", "ENSGALG00010024800", "CHN1", "PMS2"],
                ["EIF4EBP3", "EPS15", "ENSGALG00010005315", "TMEM131", "GIT2"],
                ["ENSGALG00010012136", "ENSGALG00010007434", "DUSP19", "MYL12B", "HPCAL1"],
                ["ENSGALG00010009849", "CYP2C23a", "ENSGALG00010002708", "NDRG1", "PELI3"],
                ["CAPRIN2", "DLGAP5", "RPGRIP1L", "NCAPG2", "KIF20B"],
                ["ENSGALG00010004563", "ENSGALG00010010656", "ENSGALG00010018798", "ENSGALG00010013279",
                 "ENSGALG00010016226"],
                ["ENSGALG00010017525", "ENSGALG00010025955", "ENSGALG00010019353", "ENSGALG00010008898",
                 "ENSGALG00010007049"], ["ZFP91", "EBF2", "PGR", "ENSGALG00010006250", "ANKRD2"],
                ["DSEL", "CYP3A5", "CDKL2", "FAM114A1", "ENSGALG00010029109"],
                ["NEK8", "FBXL18", "TTI1", "RXRA", "FAM78B"],
                ["ENSGALG00010025648", "ADAP2", "FKBP5", "ENSGALG00010025861", "HOMER3"],
                ["CCR2", "HACD4", "VCAM1", "SLC10A2", "GPR183"],
                ["NIPAL4", "ENSGALG00010018417", "ENSGALG00010025966", "ENSGALG00010002274",
                 "ENSGALG00010018346"], ["GJB2", "FOLH1", "C1orf101", "PIK3C2G", "SOAT1"],
                ["B3GNT9", "ENSGALG00010028072", "ABCC3", "ENSGALG00010024070", "DDX51"],
                ["EEPD1", "ENSGALG00010007238", "MMP17", "ENSGALG00010019299", "GUCA1A"],
                ["NUP214", "KDM5A", "MED12", "GTF3C1", "MED1"],
                ["ENSGALG00010025641", "ENSGALG00010027509", "ENSGALG00010012530", "ENSGALG00010018744",
                 "AGXT"], ["GASK1B", "GEN1", "CEP128", "GALNT3", "CP"],
                ["PGAP1", "ENSGALG00010021711", "DGKH", "ENSGALG00010004375", "ENSGALG00010004994"],
                ["ENSGALG00010010859", "NCAPH", "TRIP13", "CENPO", "CCNA2"],
                ["DEPTOR", "ZNF319", "ENSGALG00010024266", "LRRC3C", "TRIM65"],
                ["CCND3", "LIMD2", "GRAPL", "DOK3", "GNG2"],
                ["MN1", "TMEM201", "GRAMD1B", "STK35", "DYSF"],
                ["ENSGALG00010017135", "HELQ", "GTDC1", "SCARNA7", "ANKMY1"],
                ["GOLT1B", "THAP12", "TTC8", "IL1RL1", "CHRNA5"],
                ["RAI14", "RPS6KA5", "ENSGALG00010019818", "DOP1B", "ENSGALG00010018360"],
                ["DHX57", "EP300", "ENSGALG00010002919", "NCOA5", "CREBBP"],
                ["NPY7R", "ZNF704", "MBD3", "SERINC5", "UBE2QL1"],
                ["SLBP", "ENSGALG00010011905", "5_8S_rRNA", "ANGPT1", "MINDY3"],
                ["C21orf91", "TNFRSF4", "IGSF6", "ENSGALG00010002921", "AQP1"],
                ["RABIF", "MIEN1", "GTF3C2", "EXOSC5", "COQ4"],
                ["ENSGALG00010010582", "ENSGALG00010009095", "ENSGALG00010001384", "ENSGALG00010002833",
                 "ENSGALG00010020418"],
                ["ENSGALG00010002871", "TLK1", "HACD2", "SRBD1", "ENSGALG00010003106"],
                ["ENSGALG00010010598", "ENSGALG00010001331", "ENSGALG00010009751", "ENSGALG00010003369",
                 "CRB1"], ["ARSH", "ASNSD1", "LEPROTL1", "ENSGALG00010004012", "KCTD6"],
                ["SUSD2", "ITGB6", "ENSGALG00010019281", "NRIP1", "ENSGALG00010015518"],
                ["ENSGALG00010008908", "ENSGALG00010016084", "ENSGALG00010007291", "ENSGALG00010007015",
                 "ENSGALG00010013738"],
                ["ENSGALG00010025088", "ENSGALG00010012874", "TSPEAR", "KCNK12", "ENSGALG00010000117"],
                ["DAPK3", "ASPHD1", "SMTN", "CD34", "FLII"],
                ["IL17REL", "CCL21", "IL20RA", "RLN3", "CTLA4"],
                ["HOXD9", "ENSGALG00010029048", "ENSGALG00010001532", "PAQR9", "ENSGALG00010018783"],
                ["MSGN1", "ENSGALG00010003401", "ENSGALG00010001492", "ENSGALG00010006829",
                 "ENSGALG00010029465"], ["RPL3", "RPL13", "ENSGALG00010029218", "TOMM5", "RPL18A"],
                ["ZDHHC2", "WASHC5", "LSM11", "FAM149B1", "AGO1"],
                ["RPL14", "RPL27A", "RPS8", "LYPLAL1", "ENY2"],
                ["FRMD7", "TECTA", "ENSGALG00010016710", "ENSGALG00010025077", "ENSGALG00010025180"],
                ["CELF4", "SNCA", "SNAP25", "CBLN3", "ENSGALG00010002556"],
                ["ENSGALG00010006308", "ENSGALG00010005096", "ENSGALG00010013166", "ITGBL1",
                 "ENSGALG00010004037"], ["RAB11FIP5", "APBB1IP", "MYO18B", "ETS1", "DOCK8"],
                ["METTL21A", "ZSWIM7", "SERF2", "FADS6", "LUC7L"],
                ["NECAP2", "TCIRG1", "PIM1", "ENSGALG00010005254", "ADAM8"],
                ["ENSGALG00010020720", "TBCCD1", "PYCR1", "ADRM1", "LRRC59"],
                ["C12orf4", "C9ORF152", "CAPZA2", "LYVE1", "SERPINI1"],
                ["ENSGALG00010002750", "B9D1", "PDCD11", "NUP155", "KNTC1"],
                ["ENSGALG00010001707", "ENSGALG00010007069", "FGFBP1", "GRP", "EREG"],
                ["RPL15", "RPS11", "DCPS", "RACK1", "EFHD2"],
                ["VAC14", "CEP131", "CCM2L", "AP3B2", "CHST3"],
                ["ENSGALG00010014433", "ENSGALG00010015593", "ENSGALG00010009863", "ENSGALG00010014021",
                 "ENSGALG00010014215"], ["RAD52", "GFM1", "FRZB", "TRAP1", "SOX9"],
                ["ENSGALG00010023683", "ENSGALG00010016770", "ENSGALG00010022982", "ENSGALG00010016596",
                 "ENSGALG00010000565"],
                ["ENSGALG00010026837", "CCKAR", "ENSGALG00010015860", "CSMD1", "ENSGALG00010010718"],
                ["FAM83F", "MTSS1", "ENSGALG00010029850", "GDPD4", "PARP8"],
                ["RDH5", "ENSGALG00010024113", "ENSGALG00010027955", "AIP", "ENSGALG00010026806"],
                ["ARL11", "SIAH2", "OAT", "ADM2", "CTSD"], ["RPL4", "RPS27A", "RPS10", "RPL8", "RPS20"],
                ["GANC", "UBAC1", "SLC44A1", "TPCN2", "ANKS6"],
                ["GAMT", "HAND2", "NR2F1", "GFRA2", "SNCB"],
                ["ASF1A", "ARPC5L", "FOPNL", "UXS1", "ENSGALG00010012473"],
                ["ENSGALG00010015762", "ENSGALG00010004719", "ENSGALG00010025258", "ENSGALG00010027606",
                 "ENSGALG00010023858"],
                ["ENSGALG00010015232", "ENSGALG00010016243", "ENSGALG00010016188", "ENSGALG00010007387",
                 "ENSGALG00010015968"],
                ["MS4A4A", "PHYHD1", "ENSGALG00010005450", "EVA1CL", "ENSGALG00010004071"],
                ["ENSGALG00010008892", "ENSGALG00010004196", "TMEM61", "ENSGALG00010001729", "PCGF1"],
                ["ENSGALG00010014802", "ENSGALG00010007976", "ENSGALG00010000405", "ENSGALG00010008475",
                 "ENSGALG00010000752"], ["ENSGALG00010005330", "GSTA2", "NGF", "INHBB", "C8B"],
                ["ENSGALG00010006935", "ENSGALG00010007268", "ENSGALG00010013049", "ENSGALG00010003188",
                 "ENSGALG00010000968"], ["TASOR", "LHX6", "USP49", "CDK5RAP2", "ENSGALG00010026108"],
                ["RBM46", "ENSGALG00010018634", "SLC26A8", "ENPP3", "SLC7A6"],
                ["SAMM50", "FAM32A", "CYB5D2", "ENSGALG00010005922", "ENSGALG00010027020"],
                ["FMNL1", "LPXN", "MYO1G", "ARHGAP45", "KIF21B"],
                ["ENSGALG00010000934", "REG4", "ENSGALG00010027839", "KCNJ12", "ENSGALG00010010170"],
                ["ENSGALG00010005801", "ENSGALG00010026773", "ENSGALG00010020763", "ENSGALG00010001936",
                 "ENSGALG00010025008"]]
            for cluster in cluster_data_0_4:
                if selected_bacteria in cluster:
                    found = True
                    cluster_found = cluster
                    threshold = "0.4"
                    break
            if not found:
                for cluster in cluster_data_0_3:
                    if selected_bacteria in cluster:
                        found = True
                        cluster_found = cluster
                        threshold = "0.3"
                        break
            if not found:
                for cluster in cluster_data_0_2:
                    if selected_bacteria in cluster:
                        found = True
                        cluster_found = cluster
                        threshold = "0.2"
                        break
            if found:
                cleaned_cluster = [s.replace("s__", "") for s in cluster_found]
                return J({
                    "found": True,
                    "threshold": threshold,
                    "cluster_members": cleaned_cluster,
                })
            else:
                return J({"found": False})

        # Common filters
        tissue = request.GET.get('tissue')
        if tissue is None:
            return J({'error': 'Missing tissue.'}, status=400)
        # base_tissue_q = Q(from_tissue=tissue) | Q(to_tissue=tissue)
        # here tissue is ileum to adapat for each case
        base_tissue_q = Q(from_tissue='ileum') & Q(to_tissue=tissue)

        # (B) Single-var filtering
        if ('multi_variable' not in request.GET
            and 'table_filter' not in request.GET
            and 'cluster_lookup' not in request.GET
            and 'explore_table_filter' not in request.GET
            and 'explore_distribution' not in request.GET):
            var = request.GET.get('variable')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min  = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = IleumCorrelation.objects.filter(
                base_tissue_q,
                var2=var,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({'results': [], 'total_count': 0})
            top = filt.order_by('-correlation')[:100]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count})

        # (C) Multi-var filtering
        if 'multi_variable' in request.GET:
            variables = request.GET.getlist('variables[]')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min  = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = IleumCorrelation.objects.filter(
                base_tissue_q,
                var2__in=variables,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({'results': [], 'total_count': 0})
            top = filt.order_by('-correlation')[:100]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count})

        # (E) Table Filtering
        if 'table_filter' in request.GET:
            var = request.GET.get('variable')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min  = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = IleumCorrelation.objects.filter(
                base_tissue_q,
                var2=var,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({
                    'results': [],
                    'total_count': 0,
                    'overview': {'median': None, 'q1': None, 'q3': None}
                })
            top = filt.order_by('-correlation')[:200]

            results = []
            vals = [o.correlation for o in filt]
            overview = {
                'median': r3(np.median(vals)),
                'q1': r3(np.quantile(vals, 0.25)),
                'q3': r3(np.quantile(vals, 0.75)),
            }
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'Coefficient': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count, 'overview': overview})

        # (F) Explore distribution
        if 'explore_distribution' in request.GET:
            # qs = IleumCorrelation.objects.filter(base_tissue_q).values_list('correlation', flat=True)
            qs = (IleumCorrelation.objects
                  .filter(base_tissue_q, correlation__isnull=False)
                  .values_list('correlation', flat=True)
                  )
            series = list(qs)
            if not series:
                return J({'error': 'No data found.'}, status=400)
            stats = {
                'min': r3(min(series)),
                'q1': r3(np.quantile(series, 0.25)),
                'median': r3(np.median(series)),
                'q3': r3(np.quantile(series, 0.75)),
                'max': r3(max(series)),
            }
            return J({'distribution': {'correlation_values': series, 'stats': stats}})

        # (G) Explore table filter
        if 'explore_table_filter' in request.GET:
            try:
                corr_min = float(request.GET.get('corrMin', -1))
                corr_max = float(request.GET.get('corrMax', 1))
                acc_min  = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = IleumCorrelation.objects.filter(
                base_tissue_q,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            top = filt.order_by('-correlation')[:200]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            vals = [o.correlation for o in filt]
            overview = {
                'median': r3(np.median(vals)) if vals else None,
                'q1': r3(np.quantile(vals, 0.25)) if vals else None,
                'q3': r3(np.quantile(vals, 0.75)) if vals else None,
            }
            return J({'results': results, 'total_count': total_count, 'overview': overview})

        return J({'error': 'No recognized AJAX action.'}, status=400)

    # --- Non-AJAX: build sunbursts + context ---
    def clusters_to_df(data):
        rows = []
        for i, sublist in enumerate(data, start=1):
            cluster_name = f"Cluster {i}"
            for species in sublist:
                rows.append({"Cluster": cluster_name, "Species": species.replace("s__", ""), "Value": 1})
        return pd.DataFrame(rows)

    cluster_data_0_4 = [["ENSGALG00010000369", "ENSGALG00010000239", "ENSGALG00010000358", "ENSGALG00010000246",
                         "ENSGALG00010000326", "ENSGALG00010012336", "ENSGALG00010000249", "ENSGALG00010013702",
                         "ENSGALG00010011857", "ENSGALG00010011555", "ENSGALG00010000309"],
                        ["ENSGALG00010005481", "ENSGALG00010000318", "ENSGALG00010012927", "ENSGALG00010000354",
                         "SPIN1L", "ENSGALG00010000313", "ENSGALG00010000282", "ENSGALG00010013706",
                         "ENSGALG00010011467"],
                        ["ENSGALG00010003614", "ENSGALG00010003644", "ENSGALG00010003646", "ENSGALG00010003635",
                         "ENSGALG00010003643", "ENSGALG00010003623", "ENSGALG00010003613", "ENSGALG00010003625",
                         "ENSGALG00010003640"],
                        ["ENSGALG00010003565", "ENSGALG00010003584", "ENSGALG00010003563", "ENSGALG00010003575",
                         "ENSGALG00010003537", "ENSGALG00010003598", "ENSGALG00010003529",
                         "ENSGALG00010003576"], ["RAD54B", "SMC2", "TERF1", "BORA", "TTK", "CENPU"],
                        ["ENSGALG00010013950", "ENSGALG00010023025", "ENSGALG00010019862", "ENSGALG00010018778",
                         "ENSGALG00010007736", "ENSGALG00010004169"],
                        ["ENSGALG00010004938", "ENSGALG00010015531", "ENSGALG00010006725", "ENSGALG00010018789",
                         "ENSGALG00010007061"],
                        ["ENSGALG00010006935", "ENSGALG00010007268", "ENSGALG00010013049", "ENSGALG00010003188",
                         "ENSGALG00010000968"],
                        ["ENSGALG00010013151", "ENSGALG00010009922", "ENSGALG00010012494", "ENSGALG00010006950",
                         "ENSGALG00010015775"],
                        ["ENSGALG00010013567", "ENSGALG00010015575", "ENSGALG00010004208", "ENSGALG00010012840",
                         "ENSGALG00010002797"]]

    cluster_data_0_3 = [["ENSGALG00010003644", "ENSGALG00010003584", "ENSGALG00010003646", "ENSGALG00010003635",
                         "ENSGALG00010003643", "ENSGALG00010003537", "ENSGALG00010003598", "ENSGALG00010003640",
                         "ENSGALG00010003576", "ENSGALG00010003565", "ENSGALG00010003614", "ENSGALG00010003563",
                         "ENSGALG00010003575", "ENSGALG00010003613", "ENSGALG00010003623", "ENSGALG00010003625",
                         "ENSGALG00010003529"],
                        ["ENSGALG00010000369", "ENSGALG00010000239", "ENSGALG00010000358", "ENSGALG00010000246",
                         "ENSGALG00010000326", "ENSGALG00010012336", "ENSGALG00010000249", "ENSGALG00010013702",
                         "ENSGALG00010011857", "ENSGALG00010011555", "ENSGALG00010000309"],
                        ["ENSGALG00010007147", "ENSGALG00010020566", "ENSGALG00010005005", "ENSGALG00010013879",
                         "ENSGALG00010016272", "ENSGALG00010004331", "ENSGALG00010020188", "ENSGALG00010014786",
                         "ENSGALG00010020349"],
                        ["MCPH1", "RAD54B", "SMC2", "TERF1", "TTK", "SFR1", "BORA", "CENPU", "CDC7"],
                        ["ENSGALG00010005481", "ENSGALG00010000318", "ENSGALG00010012927", "ENSGALG00010000354",
                         "SPIN1L", "ENSGALG00010000313", "ENSGALG00010000282", "ENSGALG00010013706",
                         "ENSGALG00010011467"],
                        ["ENSGALG00010018845", "ENSGALG00010004435", "ENSGALG00010029472", "ENSGALG00010010739",
                         "ENSGALG00010017298", "ENSGALG00010027000", "ENSGALG00010010563"],
                        ["ENSGALG00010011821", "ENSGALG00010014495", "ENSGALG00010019286", "ENSGALG00010013571",
                         "ENSGALG00010006303", "MGAT4C", "ENSGALG00010011219"],
                        ["ENSGALG00010019749", "ENSGALG00010008845", "ENSGALG00010010249", "IFNG",
                         "ENSGALG00010015609", "ENSGALG00010009075", "ENSGALG00010028505"],
                        ["ENSGALG00010027048", "ENSGALG00010021910", "RNF17", "ENSGALG00010004565",
                         "ENSGALG00010017014", "ENSGALG00010019849"],
                        ["ENSGALG00010013950", "ENSGALG00010023025", "ENSGALG00010019862", "ENSGALG00010018778",
                         "ENSGALG00010007736", "ENSGALG00010004169"],
                        ["SLC5A12", "ENSGALG00010025255", "ENSGALG00010028699", "SPIA1", "DFNA5", "ABCA13"],
                        ["ENSGALG00010012604", "ENSGALG00010011339", "ENSGALG00010013778", "ENSGALG00010003609",
                         "Metazoa_SRP", "ENSGALG00010005593"],
                        ["ENSGALG00010019133", "ENSGALG00010021921", "CYP27C1", "ENSGALG00010004694",
                         "ENSGALG00010019251", "ENSGALG00010019729"],
                        ["ENSGALG00010014044", "ENSGALG00010003482", "ENSGALG00010005192", "ENSGALG00010003556",
                         "ENSGALG00010009165", "ENSGALG00010004945"],
                        ["S1PR4", "FAM65B", "TMEM132E", "ITGB7", "ENSGALG00010028467", "ENSGALG00010005585"],
                        ["CAD", "TIMELESS", "CHEK1", "CDC6", "METTL13", "ESPL1"],
                        ["ENSGALG00010003587", "HBE1", "ENSGALG00010008539", "ENSGALG00010005816",
                         "ENSGALG00010012306", "ENSGALG00010018888"],
                        ["ENSGALG00010021256", "NT5C3B", "ENSGALG00010006172", "DHX58", "TAPBP",
                         "ENSGALG00010026316"],
                        ["ENSGALG00010004692", "ENSGALG00010019809", "ENSGALG00010001039", "ENSGALG00010013730",
                         "ENSGALG00010002731", "ENSGALG00010006511"],
                        ["ENSGALG00010013151", "ENSGALG00010009293", "ENSGALG00010009922", "ENSGALG00010012494",
                         "ENSGALG00010006950", "ENSGALG00010015775"],
                        ["ENSGALG00010019528", "ENSGALG00010016717", "ENSGALG00010008868", "ENSGALG00010016196",
                         "ENSGALG00010027456", "ENSGALG00010014616"],
                        ["RBP4A", "PRPS2", "TDO2", "FGB", "ALB", "TTR"],
                        ["ENSGALG00010009046", "TRIM29", "ENSGALG00010010540", "ENSGALG00010006733",
                         "ENSGALG00010008611", "ENSGALG00010006990"],
                        ["FMO4", "BPIFB3", "ANO5", "FETUB", "ADH1C", "ENSGALG00010021522"],
                        ["ENSGALG00010008908", "ENSGALG00010016084", "ENSGALG00010007291", "ENSGALG00010007015",
                         "ENSGALG00010013738"], ["IL17REL", "CCL21", "IL20RA", "RLN3", "CTLA4"],
                        ["BCL11A", "PIGQ", "ERICH3", "CARD10", "RAP1GAP2"],
                        ["ENSGALG00010010328", "ENSGALG00010015394", "GJD2", "KCNA10", "ENSGALG00010013496"],
                        ["ENSGALG00010013718", "ENSGALG00010023899", "ENSGALG00010009845", "ENSGALG00010023323",
                         "ENSGALG00010003093"],
                        ["ENSGALG00010022369", "ENSGALG00010004742", "ENSGALG00010013059", "ENSGALG00010002563",
                         "ENSGALG00010019044"],
                        ["ENSGALG00010006695", "ENSGALG00010019241", "ENSGALG00010011083", "ENSGALG00010022156",
                         "ENSGALG00010003421"],
                        ["ENSGALG00010004938", "ENSGALG00010015531", "ENSGALG00010006725", "ENSGALG00010018789",
                         "ENSGALG00010007061"],
                        ["NRG4", "ENSGALG00010025839", "ENSGALG00010016164", "ENSGALG00010014013",
                         "ENSGALG00010001538"],
                        ["ENSGALG00010022350", "ENSGALG00010011194", "ENSGALG00010020372", "ENSGALG00010013540",
                         "ENSGALG00010023619"],
                        ["ENSGALG00010000956", "ENSGALG00010013819", "ENSGALG00010005781", "ENSGALG00010006662",
                         "ENSGALG00010009729"], ["CDK5R1", "KIRREL3", "ACTG2", "GM2A", "RAB40C"],
                        ["ENSGALG00010021499", "ENSGALG00010009865", "ENSGALG00010017370", "ENSGALG00010015757",
                         "CRISP2"], ["ENSGALG00010022963", "ENSGALG00010008367", "ENSGALG00010011411", "PARD6A",
                                     "ENSGALG00010027708"],
                        ["NUDT2", "ENSGALG00010009595", "CMC2", "TMEM167A", "NUDT7"],
                        ["ENSGALG00010004563", "ENSGALG00010010656", "ENSGALG00010018798", "ENSGALG00010013279",
                         "ENSGALG00010016226"],
                        ["ENSGALG00010013567", "ENSGALG00010015575", "ENSGALG00010004208", "ENSGALG00010012840",
                         "ENSGALG00010002797"], ["CISD3", "DNLZ", "NDUFAF8", "C12orf57", "C22orf39"],
                        ["CPA6", "ENSGALG00010007958", "CYP24A1", "ENSGALG00010009096", "ENSGALG00010008676"],
                        ["ENSGALG00010003520", "ENSGALG00010026158", "ENSGALG00010000094", "ENSGALG00010006722",
                         "ENSGALG00010023006"],
                        ["ENSGALG00010025478", "ENSGALG00010005640", "ENSGALG00010011877", "NEK10",
                         "ENSGALG00010017474"],
                        ["ENSGALG00010006729", "ENSGALG00010007722", "ENSGALG00010007652", "ENSGALG00010014422",
                         "ENSGALG00010010583"],
                        ["ENSGALG00010029113", "ENSGALG00010019754", "ENSGALG00010011771", "ENSGALG00010020508",
                         "ENSGALG00010006938"],
                        ["ENSGALG00010006935", "ENSGALG00010007268", "ENSGALG00010013049", "ENSGALG00010003188",
                         "ENSGALG00010000968"], ["CCDC186", "OVOA", "UGT8", "PLEKHA7", "ITPRID2"],
                        ["ENSGALG00010007790", "ENSGALG00010025973", "ENSGALG00010012789", "ENSGALG00010004448",
                         "ENSGALG00010007119"], ["C21orf91", "TNFRSF4", "IGSF6", "ENSGALG00010002921", "AQP1"],
                        ["ENSGALG00010010598", "ENSGALG00010001331", "ENSGALG00010009751", "ENSGALG00010003369",
                         "CRB1"],
                        ["ENSGALG00010004915", "ENSGALG00010004490", "ENSGALG00010012319", "ENSGALG00010001063",
                         "ENSGALG00010006114"], ["LANCL1", "INTS8", "RABL6", "MORC1", "VPS26B"],
                        ["MRPS14", "PSMC5", "PTRH2", "YRDC", "SNRPC"]]

    cluster_data_0_2 = [["ENSGALG00010003644", "ENSGALG00010003584", "ENSGALG00010003646", "ENSGALG00010003635",
                         "ENSGALG00010003643", "ENSGALG00010003537", "ENSGALG00010003598", "ENSGALG00010003640",
                         "ENSGALG00010003576", "ENSGALG00010003565", "ENSGALG00010003614", "ENSGALG00010003563",
                         "ENSGALG00010003575", "ENSGALG00010003613", "ENSGALG00010003623", "ENSGALG00010003625",
                         "ENSGALG00010003529"],
                        ["ENSGALG00010011339", "ENSGALG00010003287", "DCT", "ENSGALG00010012860",
                         "ENSGALG00010020937", "ENSGALG00010005593", "ENSGALG00010012604", "5_8S_rRNA", "PROZ",
                         "ENSGALG00010013134", "ENSGALG00010013778", "ENSGALG00010003609", "ENSGALG00010011473",
                         "Metazoa_SRP"],
                        ["ENSGALG00010023640", "ENSGALG00010003932", "IYD", "ENSGALG00010029155",
                         "ENSGALG00010028831", "ENSGALG00010020326", "ENSGALG00010001357", "ENSGALG00010009944",
                         "ENSGALG00010022940", "ENSGALG00010023467", "ENSGALG00010023370"],
                        ["ENSGALG00010000369", "ENSGALG00010000239", "ENSGALG00010000358", "ENSGALG00010000246",
                         "ENSGALG00010000326", "ENSGALG00010012336", "ENSGALG00010000249", "ENSGALG00010013702",
                         "ENSGALG00010011857", "ENSGALG00010011555", "ENSGALG00010000309"],
                        ["ENSGALG00010019528", "ENSGALG00010016717", "ENSGALG00010029981", "ENSGALG00010006734",
                         "ENSGALG00010016196", "ENSGALG00010012385", "ENSGALG00010008868", "ENSGALG00010023608",
                         "ENSGALG00010018065", "ENSGALG00010027456", "ENSGALG00010014616"],
                        ["ENSGALG00010027765", "ENSGALG00010026961", "ZIC1", "EN2", "ENSGALG00010027472",
                         "ENSGALG00010014498", "ENSGALG00010025332", "ENSGALG00010012478", "TFAP2B",
                         "ENSGALG00010014177", "ENSGALG00010003359"],
                        ["ZNF804B", "ENSGALG00010023647", "ENSGALG00010009189", "ENSGALG00010012545",
                         "ENSGALG00010013188", "KCNQ2", "ENSGALG00010006555", "ENSGALG00010002898", "CHIR-AB1",
                         "C17H9ORF172", "ENSGALG00010024684"],
                        ["ENSGALG00010004938", "ENSGALG00010006725", "ENSGALG00010008601", "ENSGALG00010007061",
                         "ENSGALG00010018789", "ENSGALG00010021808", "ENSGALG00010015531", "ENSGALG00010026383",
                         "ENSGALG00010023988", "ENSGALG00010002607"],
                        ["ENSGALG00010000646", "CUX2", "NPS", "VSX1", "ENSGALG00010005419",
                         "ENSGALG00010009978", "ENSGALG00010003297", "EGR4", "CELF5", "ENSGALG00010020591"],
                        ["ABHD17B", "SMIM5", "ENSGALG00010003215", "CTBS", "ENSGALG00010009619",
                         "ENSGALG00010007089", "ENSGALG00010006119", "ENSGALG00010014619", "ENSGALG00010006726",
                         "GUCA2B"],
                        ["ENSGALG00010000497", "ENSGALG00010012448", "ENSGALG00010000892", "TSPAN19",
                         "ENSGALG00010014598", "VTCN1", "ENSGALG00010007293", "ENSGALG00010020347",
                         "ENSGALG00010011727", "ENSGALG00010018850"],
                        ["RBP4A", "SPIA4", "PRPS2", "CYP2R1", "TDO2", "AQP9", "TTR", "ITIH3", "ALB", "FGB"],
                        ["CD74", "KLHL18", "ENSGALG00010016511", "UBXN11", "MECR", "KIAA0040",
                         "ENSGALG00010023183", "ENSGALG00010024892", "DMB2", "ENSGALG00010022322"],
                        ["CNDP1", "SLC38A2", "NADK2", "SMC5", "ENSGALG00010020106", "EEIG2", "PDP1", "IFT74",
                         "PLA2G4F", "USP16"],
                        ["ENSGALG00010002950", "ENSGALG00010008597", "ENSGALG00010013683", "ENSGALG00010006925",
                         "ENSGALG00010015396", "ENSGALG00010000896", "ENSGALG00010015011", "ENSGALG00010015223",
                         "RNF2", "HSD17B3"],
                        ["TGIF1", "SMAD7", "CBR3", "ENSGALG00010026534", "CXCL14", "MAP1LC3B", "SESN1", "BIK",
                         "PIK3IP1"],
                        ["ENSGALG00010005813", "ENSGALG00010025177", "ENSGALG00010014845", "SLITRK5",
                         "ENSGALG00010020600", "ENSGALG00010025859", "ENSGALG00010004084", "ENSGALG00010005865",
                         "CADM2"],
                        ["ENSGALG00010005481", "ENSGALG00010000318", "ENSGALG00010012927", "ENSGALG00010000354",
                         "SPIN1L", "ENSGALG00010000313", "ENSGALG00010000282", "ENSGALG00010013706",
                         "ENSGALG00010011467"],
                        ["ENSGALG00010011486", "EGLN3", "ENSGALG00010021536", "CYP4V2", "ETNPPL",
                         "ENSGALG00010016771", "KBTBD11", "GYS2", "RD3"],
                        ["ENSGALG00010014207", "ENSGALG00010025804", "ENSGALG00010003538", "CSDC2",
                         "ENSGALG00010004815", "ENSGALG00010008751", "ENSGALG00010006984", "NEUROD2",
                         "ENSGALG00010000192"],
                        ["ENSGALG00010004321", "ENSGALG00010022785", "ENSGALG00010006565", "ENSGALG00010023745",
                         "ENSGALG00010014524", "GPM6A", "ENSGALG00010019562", "ENSGALG00010027042",
                         "ENSGALG00010012374"],
                        ["ENSGALG00010004915", "ENSGALG00010023753", "ENSGALG00010023302", "ENSGALG00010004490",
                         "ENSGALG00010006114", "ENSGALG00010019075", "ENSGALG00010016162", "ENSGALG00010012319",
                         "ENSGALG00010001063"],
                        ["ENSGALG00010007147", "ENSGALG00010020566", "ENSGALG00010005005", "ENSGALG00010013879",
                         "ENSGALG00010016272", "ENSGALG00010004331", "ENSGALG00010020188", "ENSGALG00010014786",
                         "ENSGALG00010020349"],
                        ["CISD3", "DNLZ", "NDUFAF8", "C22orf39", "ENSGALG00010010051", "ENSGALG00010011443",
                         "APOC3", "C12orf57", "URM1"],
                        ["MCPH1", "RAD54B", "SMC2", "TERF1", "TTK", "SFR1", "BORA", "CENPU", "CDC7"],
                        ["ENSGALG00010023667", "ENSGALG00010004634", "ENSGALG00010008463", "NKX2-5", "MARCH4",
                         "ENSGALG00010020251", "FGF4", "ENSGALG00010009285", "ENSGALG00010010114"],
                        ["ENSGALG00010007794", "ENSGALG00010012065", "ENSGALG00010007219", "ENSGALG00010023691",
                         "ENSGALG00010000847", "ENSGALG00010003514", "ENSGALG00010003284", "ENSGALG00010004517",
                         "ENSGALG00010008851"],
                        ["ENSGALG00010022963", "ENSGALG00010011411", "ENSGALG00010013701", "PARD6A",
                         "ENSGALG00010027708", "ENSGALG00010008367", "KLHL35", "ENSGALG00010022882",
                         "ENSGALG00010018178"],
                        ["ENSGALG00010007857", "ENSGALG00010016386", "IFNL3A", "IL4I1", "ENSGALG00010012743",
                         "ACOD1", "CD86", "ENSGALG00010013573", "SLC2A6"],
                        ["ENSGALG00010022007", "ENSGALG00010025478", "ENSGALG00010005640", "ENSGALG00010011877",
                         "NEK10", "ENSGALG00010011206", "ENSGALG00010007205", "ENSGALG00010002230",
                         "ENSGALG00010017474"],
                        ["ENSGALG00010003587", "ENSGALG00010018962", "HBE1", "ENSGALG00010008539",
                         "ENSGALG00010005816", "ENSGALG00010023072", "ENSGALG00010012306", "ENSGALG00010018888",
                         "ENSGALG00010009599"],
                        ["ENSGALG00010010731", "ENSGALG00010008545", "ENSGALG00010025124", "ENSGALG00010012584",
                         "ENSGALG00010007738", "ENSGALG00010003151", "ENSGALG00010002695", "ENSGALG00010014627",
                         "ENSGALG00010006605"],
                        ["ENSGALG00010000956", "SIM2", "ENSGALG00010006662", "ENSGALG00010009729",
                         "ENSGALG00010005781", "ENSGALG00010011032", "ENSGALG00010019338", "ENSGALG00010013819",
                         "ENSGALG00010008591"],
                        ["ENSGALG00010013567", "ENSGALG00010004647", "ENSGALG00010006385", "ENSGALG00010002797",
                         "ENSGALG00010002021", "ENSGALG00010015575", "ENSGALG00010004208", "ENSGALG00010009893",
                         "ENSGALG00010012840"],
                        ["MYD88", "B3GNT7", "TMEM248", "NT5C1B", "OTUD4", "SH2D6", "B4GALT1", "PFKP", "SUCO"],
                        ["ENSGALG00010002861", "ENSGALG00010027655", "ENSGALG00010028331", "ENSGALG00010002945",
                         "ENSGALG00010001005", "ENSGALG00010025261", "ENSGALG00010002297", "ENSGALG00010023535",
                         "ENSGALG00010020647"],
                        ["ENSGALG00010006879", "CACNG5", "ENSGALG00010015120", "ENSGALG00010027544",
                         "ENSGALG00010025675", "ENSGALG00010014113", "ENSGALG00010019651", "ENSGALG00010008566",
                         "SHOX"],
                        ["ENSGALG00010026158", "ENSGALG00010006722", "ENSGALG00010013957", "ENSGALG00010000293",
                         "PDZRN4", "ENSGALG00010003520", "ENSGALG00010000094", "ENSGALG00010023006"],
                        ["ENSGALG00010006981", "SYCE3", "OVAL", "ENSGALG00010007269", "ENSGALG00010010194",
                         "ENSGALG00010024455", "ENSGALG00010012465", "ENSGALG00010019877"],
                        ["LGR4", "KIAA0319L", "ADAM28", "KALRN", "RNF19A", "PDLIM5", "BEND7", "PTK2"],
                        ["ADRB1", "ENSGALG00010001779", "ATP13A2", "C1QL4", "ENSGALG00010027630",
                         "ENSGALG00010014048", "NRN1L", "ENSGALG00010011274"],
                        ["CHEK1", "INSM1", "METTL13", "CAD", "ESPL1", "TIMELESS", "CDC6", "ENSGALG00010000338"],
                        ["STARD4", "ENSGALG00010012919", "LRRC8B", "BST1", "GID8", "ENSGALG00010004684",
                         "PDLIM3", "ENSGALG00010026350"],
                        ["ENSGALG00010006695", "ENSGALG00010007583", "ENSGALG00010016032", "ENSGALG00010022156",
                         "ENSGALG00010003421", "ENSGALG00010019241", "ENSGALG00010011083",
                         "ENSGALG00010005896"],
                        ["ENSGALG00010004854", "PDK4", "ENSGALG00010029265", "ENSGALG00010026627",
                         "ENSGALG00010002740", "FTCD", "PCK1", "CYP2AC1"],
                        ["FRS2", "ENSGALG00010019116", "ENSGALG00010024668", "PTPN21", "NHLRC2", "RO60",
                         "NBEAL1", "N4BP2"],
                        ["ENSGALG00010019841", "ENSGALG00010027817", "ENSGALG00010003445", "ENSGALG00010006115",
                         "ENSGALG00010004783", "CNP1", "CCDC166", "ENSGALG00010013978"],
                        ["ENSGALG00010009595", "ENSGALG00010001629", "CMC2", "ENSGALG00010011203", "TMEM167A",
                         "NUDT2", "ENSGALG00010029279", "NUDT7"],
                        ["ZMYM4", "NPAT", "KIAA1549", "PLAGL2", "NR4A3", "SLC1A4", "NUP153", "SLC38A1"],
                        ["ENSGALG00010005028", "ENSGALG00010018953", "ENSGALG00010005928", "ENSGALG00010011701",
                         "ENSGALG00010005754", "ENSGALG00010026450", "ENSGALG00010009134",
                         "ENSGALG00010029873"],
                        ["CHST6", "NRBF2", "NMRK1", "ENSGALG00010009874", "RBM11", "ENSGALG00010011795",
                         "ENSGALG00010024764", "ARSK"],
                        ["MFSD2B", "ENSGALG00010005673", "ENSGALG00010003890", "ENSGALG00010013647", "ART4",
                         "CACNB4", "ENSGALG00010011200", "NISCH"],
                        ["ENSGALG00010030013", "RFX6", "SLC24A2", "ENSGALG00010006393", "RNPC3",
                         "ENSGALG00010019561", "ENSGALG00010020698", "ENSGALG00010026749"],
                        ["ENSGALG00010023088", "ENSGALG00010006807", "ENSGALG00010011542", "ENSGALG00010020731",
                         "ENSGALG00010011199", "ENSGALG00010006003", "ENSGALG00010006258",
                         "ENSGALG00010019685"],
                        ["U1", "ENSGALG00010014036", "ENSGALG00010011197", "ENSGALG00010015586",
                         "ENSGALG00010015996", "ENSGALG00010014271", "ENSGALG00010015387",
                         "ENSGALG00010003493"],
                        ["ENSGALG00010010225", "ENSGALG00010001103", "ENSGALG00010016318", "ENSGALG00010001387",
                         "ENSGALG00010006656", "ENSGALG00010003492", "ENSGALG00010026728",
                         "ENSGALG00010008962"],
                        ["ENSGALG00010020919", "ENSGALG00010015794", "ENSGALG00010024273", "ENSGALG00010013507",
                         "ENSGALG00010008643", "ENSGALG00010023735", "ENSGALG00010020639",
                         "ENSGALG00010019765"],
                        ["ENSGALG00010014702", "GDF3", "ENSGALG00010000302", "IL10RA", "ENSGALG00010000427",
                         "ACAP1", "DOK2", "SASH3"],
                        ["HTT", "BTBD7", "NF1", "HCFC2", "CEP97", "AKAP11", "MRTFB", "ATG2A"],
                        ["ZFYVE26", "MBTD1", "ABCA5", "IFFO2", "MFSD4B", "CACNA1B", "ENSGALG00010012670",
                         "FOXO4"],
                        ["ENSGALG00010021256", "OASL", "ENSGALG00010006172", "DEDD", "NT5C3B", "DHX58", "TAPBP",
                         "ENSGALG00010026316"],
                        ["AKNA", "DGKZ", "LIMK1", "MAP4K1", "PPP1R9B", "CHST13", "ENSGALG00010017349", "EML3"],
                        ["ENSGALG00010012764", "ENSGALG00010001565", "ENSGALG00010016467", "ENSGALG00010029083",
                         "ENSGALG00010026503", "ENSGALG00010018169", "ENSGALG00010019851",
                         "ENSGALG00010009014"],
                        ["ENSGALG00010007778", "ENSGALG00010026238", "ENSGALG00010011624", "ENSGALG00010000925",
                         "ENSGALG00010006703", "ENSGALG00010011684", "ENSGALG00010006349",
                         "ENSGALG00010001472"],
                        ["CCT3", "EWSR1", "RBM14", "RAVER1", "ENSGALG00010003882", "ENSGALG00010000398",
                         "DCAF15", "ENSGALG00010000581"],
                        ["ENSGALG00010026555", "ENSGALG00010006213", "ENSGALG00010029096", "ENSGALG00010009438",
                         "ENSGALG00010021547", "ENSGALG00010026408", "ENSGALG00010009604",
                         "ENSGALG00010014623"],
                        ["RBP2", "ENSGALG00010015262", "ENSGALG00010015519", "ENSGALG00010014652", "CCDC112",
                         "ENSGALG00010023463", "FSTL5", "CTXN2"],
                        ["DYNLT3", "FHL5", "AP4S1", "FAM105A", "CPNE3", "TBC1D15", "ENSGALG00010011294",
                         "ENSGALG00010011457"],
                        ["ENSGALG00010027613", "ENSGALG00010014239", "ENSGALG00010004566", "ENSGALG00010014978",
                         "ENSGALG00010024411", "ENSGALG00010029819", "ENSGALG00010019917",
                         "ENSGALG00010004909"],
                        ["ENSGALG00010004692", "ENSGALG00010019809", "ENSGALG00010006511", "ENSGALG00010002731",
                         "ENSGALG00010013730", "ENSGALG00010001039", "5_8S_rRNA", "ENSGALG00010018151"],
                        ["ENSGALG00010027354", "ENSGALG00010000273", "ASTN1", "ENSGALG00010000418",
                         "ENSGALG00010029818", "ENSGALG00010000692", "MDGA1", "ENSGALG00010004090"],
                        ["TMPRSS2", "GPT2", "ENSGALG00010010110", "CDS1", "F2RL1", "CHMP4C", "GPR85", "STYK1"],
                        ["ENSGALG00010019522", "ENSGALG00010015273", "ENSGALG00010029113", "ENSGALG00010019672",
                         "ENSGALG00010019754", "ENSGALG00010011771", "ENSGALG00010020508",
                         "ENSGALG00010006938"],
                        ["ENSGALG00010017719", "ENSGALG00010025561", "USP53", "ENSGALG00010017731", "SYTL5",
                         "ENSGALG00010026526", "FAM83B", "ENSGALG00010017736"],
                        ["ENSGALG00010021991", "ENSGALG00010021499", "ENSGALG00010000909", "ENSGALG00010017370",
                         "ENSGALG00010015757", "ENSGALG00010014322", "CRISP2", "ENSGALG00010009865"],
                        ["SMYD3", "NSA2", "RFXAP", "ENSGALG00010004979", "EIF3M", "MSANTD4",
                         "ENSGALG00010011757"],
                        ["ENSGALG00010010526", "ENSGALG00010015568", "ENSGALG00010007062", "ENSGALG00010013088",
                         "ENSGALG00010024248", "ENSGALG00010004840", "ENSGALG00010004998"],
                        ["APRT", "BSPRY", "DCTN6", "BRINP1", "TIMM23B", "FKBP1A", "ENSGALG00010028966"],
                        ["GADD45G", "FAM26F", "SOCS1", "CD274", "K123", "ENSGALG00010029641",
                         "ENSGALG00010008831"], ["H2AFZ", "TUBB6", "APTX", "EBNA1BP2", "RPA2", "ALG8", "PSMD7"],
                        ["ENSGALG00010009446", "RPS27L", "COX6C", "LGALS2", "IL15", "TXN", "GLRX"],
                        ["ENSGALG00010001094", "IL22", "IL26", "IL17F", "MMP7", "ENSGALG00010001359", "WHRN"],
                        ["HTR1D", "ENSGALG00010003099", "ENSGALG00010015526", "TFAP2C", "ENSGALG00010001533",
                         "ENSGALG00010003231", "ENSGALG00010012392"],
                        ["ENSGALG00010002963", "ENSGALG00010001631", "ENSGALG00010001609", "ENSGALG00010025146",
                         "RAG2", "ENSGALG00010002862", "ENSGALG00010005693"],
                        ["POLL", "TMEM8B", "SLC6A20", "ENSGALG00010015376", "FHOD1", "CAPN14", "NKX6-2"],
                        ["ENSGALG00010011089", "ENSGALG00010004873", "ENSGALG00010025166", "ENSGALG00010007769",
                         "ENSGALG00010010181", "ENSGALG00010025636", "ENSGALG00010013243"],
                        ["ENSGALG00010029167", "RASGRF2", "MALRD1", "CCSER2", "ENSGALG00010010832",
                         "ENSGALG00010018857", "DLG5"],
                        ["FAM168A", "MAB21L1", "FZD1", "NUP93", "ENSGALG00010012456", "ENSGALG00010024132",
                         "ENSGALG00010003152"],
                        ["ENSGALG00010013569", "ENSGALG00010012258", "ENSGALG00010022106", "CNTNAP5",
                         "ENSGALG00010006275", "ENSGALG00010008692", "ENSGALG00010018918"],
                        ["ACMSD", "CALM2", "MCUR1", "ENSGALG00010013167", "SAR1B", "PPIL6",
                         "ENSGALG00010019793"],
                        ["TRADD", "ACACA", "ARHGEF12", "SETD1A", "UNK", "ASH1L", "GNA13"],
                        ["CAPN3", "GPR155", "E4F1", "MTR", "CCND2", "TMEM68", "ENSGALG00010008298"],
                        ["TMCC1", "ENSGALG00010012096", "DSG2", "ENSGALG00010018079", "EZR", "FOXJ3", "NRDE2"],
                        ["BIN2", "CYTIP", "RAC2", "TRAF3IP3", "ENSGALG00010028649", "CD247", "CD48"],
                        ["TRABD", "WDR3", "UHRF1", "RAD54L", "MCM4", "SMC4", "RPA1"],
                        ["COPE", "DRG1", "SSR3", "DFFA", "MRPL19", "SSBP1", "SNRPD3"],
                        ["ENSGALG00010011102", "TMEM60", "C8orf76", "GTPBP8", "ENSGALG00010016620", "EIF3H",
                         "LECT2"], ["ENSGALG00010029541", "TNFRSF9", "TMSB4X", "ENSGALG00010023671", "SYTL1",
                                    "ENSGALG00010015272", "SLC31A2"],
                        ["MXI1", "RHPN1", "RNF103", "GPR83L", "CDHR5", "GCH1", "ENSGALG00010011814"],
                        ["HOXC10", "ENSGALG00010017321", "ENSGALG00010010464", "ENSGALG00010006882",
                         "ENSGALG00010015385", "ENSGALG00010015599", "ENSGALG00010010673"],
                        ["ENSGALG00010011821", "ENSGALG00010014495", "ENSGALG00010019286", "ENSGALG00010013571",
                         "ENSGALG00010006303", "MGAT4C", "ENSGALG00010011219"],
                        ["ENSGALG00010026829", "ENSGALG00010023577", "ENSGALG00010010229", "ENSGALG00010004259",
                         "ENSGALG00010014879", "ENSGALG00010004573", "ENSGALG00010014782"],
                        ["ENSGALG00010022369", "ENSGALG00010009869", "ENSGALG00010004742", "ENSGALG00010013059",
                         "ENSGALG00010002563", "ENSGALG00010019044", "ENSGALG00010026863"],
                        ["ENSGALG00010020466", "ENSGALG00010028077", "ENSGALG00010019347", "GPR153", "DEFB4A",
                         "ENSGALG00010006767", "GHSR"],
                        ["SYAP1", "ST7", "ENSGALG00010016582", "PTGR3", "UEVLD", "TSPAN13", "RAB2A"],
                        ["DGLUCY", "TRAK1", "MCF2", "ENSGALG00010015935", "DAB1", "SGPL1", "NF2L"],
                        ["OVALY", "ENSGALG00010023901", "ENSGALG00010003548", "ENSGALG00010022543", "CYP7A1",
                         "ENSGALG00010006122", "ENSGALG00010023599"],
                        ["ENSGALG00010001049", "ENSGALG00010015216", "LIN28A", "DDX25", "ATP6AP1L",
                         "ENSGALG00010029794", "ENSGALG00010017853"],
                        ["ENSGALG00010026359", "ENSGALG00010010772", "ENSGALG00010010660", "ENSGALG00010014998",
                         "ENSGALG00010019465", "ENSGALG00010010757", "VSTM2A"],
                        ["ENSGALG00010019909", "5_8S_rRNA", "ENSGALG00010000500", "ENSGALG00010012211",
                         "ENSGALG00010026622", "HINTW", "ENSGALG00010006326"],
                        ["ENSGALG00010020028", "ENSGALG00010018325", "ENSGALG00010003076", "SACS",
                         "ENSGALG00010005012", "ENSGALG00010011707", "RAB3C"],
                        ["ENSGALG00010004023", "ENSGALG00010011279", "EFCAB10", "ENSGALG00010010264",
                         "ENSGALG00010016813", "KCNG4", "ENSGALG00010028236"],
                        ["DLGAP2", "ENSGALG00010028035", "ENSGALG00010022740", "ENSGALG00010027418",
                         "ENSGALG00010027452", "ENSGALG00010000769", "FAM124B"],
                        ["ENSGALG00010020645", "ENSGALG00010011656", "ENSGALG00010030078", "ENSGALG00010000895",
                         "LRRTM1", "ENSGALG00010030080", "LRRC6"],
                        ["ENSGALG00010019749", "ENSGALG00010008845", "ENSGALG00010010249", "IFNG",
                         "ENSGALG00010015609", "ENSGALG00010009075", "ENSGALG00010028505"],
                        ["CDCP1", "MAP7D2", "FNBP1L", "RAB11FIP1", "DPP8", "ACSL5", "NECTIN3"],
                        ["RAB11FIP2", "CCDC102B", "ENSGALG00010014419", "FBXO30", "FEM1C", "ENSGALG00010026407",
                         "ENSGALG00010028358"],
                        ["UBE2J2", "RAB19", "KIF5B", "YTHDF3", "TMF1", "PDZD8", "ITFG1"],
                        ["ENSGALG00010025076", "ENSGALG00010012609", "ENSGALG00010020322", "ENSGALG00010030018",
                         "ENSGALG00010025567", "ENSGALG00010017461", "ENSGALG00010007498"],
                        ["ENSGALG00010026415", "ENSGALG00010026853", "LRRC7", "ENSGALG00010011237",
                         "ENSGALG00010026487", "ENSGALG00010010469", "ENSGALG00010001662"],
                        ["ENSGALG00010014044", "ENSGALG00010003482", "ENSGALG00010005192", "ENSGALG00010003556",
                         "ENSGALG00010009165", "ENSGALG00010004945", "GDAP1L1"],
                        ["ENSGALG00010028261", "ENSGALG00010000076", "ENSGALG00010008018", "YJU2B",
                         "ENSGALG00010025159", "ENSGALG00010010708", "ENSGALG00010004957"],
                        ["ENSGALG00010018845", "ENSGALG00010004435", "ENSGALG00010029472", "ENSGALG00010010739",
                         "ENSGALG00010017298", "ENSGALG00010027000", "ENSGALG00010010563"],
                        ["HMGN5", "PSMA2", "ALKBH8", "CRCP", "EIF2S1", "MOXD1", "RSL24D1"],
                        ["STON2", "ENSGALG00010025731", "ENSGALG00010001625", "MYZAP", "SH3TC1", "LCORL",
                         "RGS12"], ["PPP1R36", "ENSGALG00010028446", "ENSGALG00010018884", "ENSGALG00010009877",
                                    "ENSGALG00010008744", "ENSGALG00010017073", "ENSGALG00010005239"],
                        ["ENSGALG00010027048", "ENSGALG00010021910", "RNF17", "ENSGALG00010004565",
                         "ENSGALG00010017014", "ENSGALG00010019849"],
                        ["MBIP", "BRD9", "TRMT10C", "TBPL1", "RTF1", "PKDCC"],
                        ["ENSGALG00010016326", "TMEM168", "NLRC5", "UBAP1", "ARHGAP22", "ENSGALG00010019699"],
                        ["ENSGALG00010007768", "ENSGALG00010013216", "ENSGALG00010026996", "ENSGALG00010002618",
                         "ENSGALG00010026752", "ENSGALG00010003853"],
                        ["TMTC4", "YES1", "SUPT20H", "OVOL2", "PEX1", "OPA1"],
                        ["SREBF2", "PHACTR4", "MXD1", "KBTBD4", "CTNND1", "MFSD13A"],
                        ["PPP1R14D", "AP1S3", "FAS", "SELENOF", "ODF2L", "FAM18B1"],
                        ["NDUFB6", "MRPL2", "ENSGALG00010024944", "ENSGALG00010010869", "PLP2",
                         "ENSGALG00010027713"],
                        ["ENSGALG00010019696", "FBXO32", "MAN1A1", "CYBRD1", "NGEF", "CD36"],
                        ["NUAK2", "MGAT4C", "FEV", "SLC36A1", "PLEKHJ1", "ENSGALG00010018401"],
                        ["N4BP3", "WNT1", "NEIL1", "ENSGALG00010000771", "TUSC1", "MCAT"],
                        ["GATA3", "ENSGALG00010028834", "CDC20B", "ENSGALG00010015868", "ENSGALG00010017197",
                         "ENSGALG00010018934"],
                        ["WDR34", "JMJD6", "ENSGALG00010029207", "NES", "PRR11", "PRC1"],
                        ["TPBG", "MRE11", "WDHD1", "SCML2", "SLITRK2", "DHTKD1"],
                        ["IFNGR1", "ENSGALG00010012194", "ENSGALG00010010788", "CPT1A", "LYN", "KCTD20"],
                        ["LRRC38", "FAM179A", "KCTD15", "ZC4H2", "ENSGALG00010026753", "ENSGALG00010020003"],
                        ["ENSGALG00010012541", "ENSGALG00010027153", "RBMS1", "CPQ", "PARVB", "GPR52"],
                        ["ENSGALG00010003953", "ENSGALG00010010696", "ENSGALG00010004336", "DIRAS2", "C4orf54",
                         "CD163L"], ["PHF19", "SPTBN2", "DNMT1", "NOTCH1", "ENSGALG00010005263", "ARHGEF2"],
                        ["ENSGALG00010013115", "KCNE2", "ENSGALG00010013097", "ENSGALG00010005050", "GINM1",
                         "ENSGALG00010008994"],
                        ["ENSGALG00010017668", "SH2D1A", "CD8BP", "NLRC3", "GLIPR1", "CD38"],
                        ["SEL1L", "ATP11B", "PDP2", "PARP4", "SMAD5", "TRAPPC10"],
                        ["INPP5D", "NCKAP1L", "RASSF2", "SLC43A3", "ADAM33", "PDE4B"],
                        ["POLR3A", "OMD", "MSMP", "TNFRSF19", "PITRM1", "CEP152"],
                        ["MAML1", "PHC3", "RC3H1", "HIPK3", "KIF13B", "TET2"],
                        ["ENSGALG00010007766", "SP4", "ENSGALG00010025883", "LRCH2", "ENSGALG00010017156",
                         "DNAH3"], ["RBM7", "TAF11", "ANXA2", "CKB", "ENSGALG00010025126", "H3F3B"],
                        ["INTS7", "URB1", "HEATR1", "SFPQ", "ENSGALG00010025369", "ADAMTS14"],
                        ["ENSGALG00010013151", "ENSGALG00010009293", "ENSGALG00010009922", "ENSGALG00010012494",
                         "ENSGALG00010006950", "ENSGALG00010015775"],
                        ["PLEKHM2", "CHPF", "KIAA1522", "VPS51", "UBL7", "RNF25"],
                        ["ENSGALG00010019681", "ENSGALG00010004911", "SCN5A", "GJA3", "ENSGALG00010025254",
                         "ENSGALG00010012827"], ["NCOR1", "WAPL", "MED13L", "MED13", "KAT6A", "RNF111"],
                        ["ENSGALG00010014187", "ENSGALG00010010123", "HOXA11", "ENSGALG00010001077",
                         "ENSGALG00010006610", "ENSGALG00010008944"],
                        ["ENSGALG00010020557", "NAMPTP1", "ENSGALG00010020087", "IFNAR1", "CHPT1", "SLC37A1"],
                        ["ANXA1", "ZC3HAV1L", "GCG", "RCAN1", "PDPN", "RAD51AP1"],
                        ["IGDCC3", "ENSGALG00010002633", "ENSGALG00010019645", "ITIH6", "CORO7", "ZBTB25"],
                        ["ENSGALG00010017238", "ENSGALG00010022011", "ENSGALG00010004213", "ENSGALG00010005378",
                         "ENSGALG00010009789", "ENSGALG00010025035"],
                        ["PHF3", "TRAF6", "CEP120", "DCUN1D3", "ZBTB21", "ENSGALG00010014649"],
                        ["CD5", "HCK", "IL21R", "RASAL3", "CARMIL2", "IRF4"],
                        ["ENSGALG00010019853", "ENSGALG00010006870", "STC1", "ENSGALG00010010241",
                         "ENSGALG00010007103", "ENSGALG00010018610"],
                        ["CKMT2", "ENSGALG00010016992", "PRR35", "ENSGALG00010016595", "ENSGALG00010000230",
                         "ENSGALG00010002279"],
                        ["FAM136A", "ENSGALG00010010059", "GRHPR", "HYLS1", "ENSGALG00010000303", "PSMC3IP"],
                        ["RPL11", "RPS13", "IFT43", "RPS23", "RPS3A", "RPL24"],
                        ["NRG3", "ENSGALG00010014462", "ENSGALG00010004376", "ENSGALG00010019276",
                         "ENSGALG00010011646", "ENSGALG00010003549"],
                        ["ENSGALG00010003797", "MPZL1", "RRM2B", "SGK3", "DUSP3", "CRBN"],
                        ["ENSGALG00010002602", "ENSGALG00010008665", "ENSGALG00010004551", "ENSGALG00010025352",
                         "ENSGALG00010013211", "ENSGALG00010019678"],
                        ["AMPH", "JAM3", "COLEC12", "CDH11", "ROBO1", "SLIT2"],
                        ["RELN", "DPP6", "ZNF536", "RASGRF1", "STAB2", "LRRN2"],
                        ["ENSGALG00010018402", "ENSGALG00010021773", "ENSGALG00010017501", "ENSGALG00010011328",
                         "ENSGALG00010008626", "ENSGALG00010007782"],
                        ["ENSGALG00010007570", "ENSGALG00010021899", "IL2", "ENSGALG00010001648", "ST18",
                         "ENSGALG00010005200"], ["ND4", "COX1", "COX2", "ND5", "CYTB", "COX3"],
                        ["ENSGALG00010016194", "ENSGALG00010020380", "ENSGALG00010017527", "ENSGALG00010004637",
                         "ENSGALG00010006960", "ENSGALG00010009405"],
                        ["ENSGALG00010026320", "TCERG1", "COL6A3", "FOCAD", "NEMP2", "BRD3"],
                        ["TASOR2", "ENSGALG00010000081", "RUBCN", "ENTPD3", "CCDC92B", "RNF216"],
                        ["HMGN2P46", "ATG10", "BBS5", "RBFA", "TEN1", "IL7"],
                        ["CHMP3", "SEC22B", "ENSGALG00010005171", "NAXD", "ENSGALG00010018371", "LYSMD3"],
                        ["ENSGALG00010011191", "ENSGALG00010016371", "ENSGALG00010004349", "ENSGALG00010022510",
                         "ENSGALG00010016608", "ENSGALG00010009110"],
                        ["POU3F4", "SSTR4", "ENSGALG00010014548", "ENSGALG00010012776", "ENSGALG00010015527",
                         "ENSGALG00010009248"], ["RPF1", "DYL1", "SNRPB2", "MRPS10", "SNRNP48", "BCCIP"],
                        ["DCLK3", "CASS4", "CELF2", "STK38", "CAVIN4", "RASGEF1A"],
                        ["DNAH5", "ENSGALG00010014771", "ENSGALG00010008957", "ENSGALG00010012794",
                         "ENSGALG00010019365", "ENSGALG00010011914"],
                        ["AICDA", "ENSGALG00010019117", "GPR132", "ENSGALG00010019270", "ENSGALG00010015192",
                         "TRAF5"],
                        ["PAIP2B", "CTNS", "ENSGALG00010026726", "ENSGALG00010018771", "CWF19L2", "PPP1CC"],
                        ["ENSGALG00010022621", "ENSGALG00010008531", "ENSGALG00010022447", "ENSGALG00010015559",
                         "ENSGALG00010025366", "ENSGALG00010014202"],
                        ["NAA15", "HAUS6", "CHORDC1", "NCBP1", "NEDD1", "SKIV2L2"],
                        ["ENSGALG00010008869", "ENSGALG00010008922", "ZIC3", "ENSGALG00010005876",
                         "ENSGALG00010002258", "ENSGALG00010004064"],
                        ["EDAR", "CYP1B1", "NUCKS1", "NDNF", "ENSGALG00010025740", "NFIA"],
                        ["REC114", "ENSGALG00010003524", "ENSGALG00010021828", "EMILIN3", "ENSGALG00010014826",
                         "ENSGALG00010016166"],
                        ["ENSGALG00010008872", "RBM43", "ENSGALG00010028489", "PMAIP1", "GPR137B",
                         "ENSGALG00010015820"],
                        ["ENSGALG00010019405", "ENSGALG00010026640", "ENSGALG00010014723", "ENSGALG00010017863",
                         "LEPR", "ENSGALG00010021150"], ["PTCH2", "KCNN3", "SNED1", "IGSF3", "LRP1", "RPRD2"],
                        ["TNIP2", "CXCR1", "IL1R2", "TCEANC2", "PDXP", "MOB1A"],
                        ["ETS2", "ENSGALG00010012060", "EIF6", "FOXK2", "PTPRE", "BRAP"],
                        ["ENSGALG00010014374", "ENSGALG00010006786", "ZPAX", "ENSGALG00010009630",
                         "ENSGALG00010002117", "ENSGALG00010004816"],
                        ["ENSGALG00010027645", "ENSGALG00010027164", "TCF7", "POU2AF1", "C15orf39",
                         "ENSGALG00010028246"],
                        ["ENSGALG00010006556", "ANKRD33B", "ENSGALG00010003475", "ENSGALG00010003683",
                         "ENSGALG00010002320", "ENSGALG00010024066"],
                        ["SAT1", "SLC1A1", "FBXO48", "ENSGALG00010029878", "AMN1", "ENSGALG00010018243"],
                        ["NPY1R", "ENSGALG00010016363", "ENSGALG00010010233", "ENSGALG00010009023",
                         "ENSGALG00010001366", "ENSGALG00010010235"],
                        ["ENSGALG00010006973", "ENSGALG00010014195", "ENSGALG00010019880", "ENSGALG00010008833",
                         "ENSGALG00010007008", "ENSGALG00010015480"],
                        ["MED7", "ZRSR2", "RNF146", "SPTY2D1", "TAF8", "SDCBP"],
                        ["ENC1", "ZHX2", "ARHGEF6", "ENSGALG00010015643", "RFTN1", "NUAK1"],
                        ["ENSGALG00010011290", "GLRA2", "ENSGALG00010019229", "ENSGALG00010024390",
                         "ENSGALG00010025838", "ENSGALG00010010294"],
                        ["KIAA0232", "PTAR1", "ENSGALG00010014039", "CCNT2", "PLPPR4", "TAB3"],
                        ["SLC5A12", "ENSGALG00010025255", "ENSGALG00010028699", "SPIA1", "DFNA5", "ABCA13"],
                        ["ENSGALG00010019133", "ENSGALG00010021921", "CYP27C1", "ENSGALG00010004694",
                         "ENSGALG00010019251", "ENSGALG00010019729"],
                        ["ENSGALG00010002242", "ENSGALG00010000987", "ENSGALG00010012652", "ENSGALG00010019665",
                         "ENSGALG00010014558", "GABRQ"],
                        ["MTTPL", "KLHL17", "FOXD1", "ENSGALG00010025560", "SIAH3", "ENSGALG00010027559"],
                        ["GPR55", "ENSGALG00010017378", "ENSGALG00010028553", "CD8A", "TBXT",
                         "ENSGALG00010012145"],
                        ["IL21", "ENSGALG00010008911", "ENSGALG00010007124", "ENSGALG00010004164",
                         "ENSGALG00010008953", "ENSGALG00010015307"],
                        ["USP6NL", "CYTH3", "MKRN2", "GRAMD4", "HMBOX1", "ENSGALG00010023063"],
                        ["SLC43A2", "TMEM117", "KRT80", "BRPF3", "ACVR2A", "MAPK1IP1L"],
                        ["AMPD1", "HOXB13", "ENSGALG00010000181", "ENSGALG00010006117", "ENSGALG00010005455",
                         "ENSGALG00010000601"],
                        ["ENSGALG00010012461", "ENSGALG00010016389", "ENSGALG00010027647", "EMX1",
                         "ENSGALG00010023475", "ENSGALG00010022914"],
                        ["ROPN1L", "SRRM4", "ENSGALG00010018763", "ENSGALG00010011285", "ENSGALG00010028307",
                         "ENSGALG00010028890"],
                        ["CTAGE1", "ENSGALG00010026840", "ENSGALG00010006295", "AFP", "ENSGALG00010009589",
                         "ENSGALG00010018392"],
                        ["PPP1R26", "TECPR2", "KATNIP", "MAN1A2", "ENSGALG00010014954", "BROX"],
                        ["RAB20", "RAP1GDS1", "VSIG4", "ENSGALG00010023963", "CYTL1", "FBXO33"],
                        ["AIFM3", "NDUFAF6", "PRKN", "HGSNAT", "MTERF2", "PKP2"],
                        ["SNAP29", "USP12", "ZBTB34", "COPS2", "ZNF644", "PEX2"],
                        ["PTPN5", "SCNN1B", "DENND1A", "MYT1", "DISP2", "BTAF1"],
                        ["ENSGALG00010006356", "ENSGALG00010002328", "ENSGALG00010023747", "ENSGALG00010018940",
                         "SMIM18", "ENSGALG00010013920"],
                        ["ENSGALG00010013752", "ENSGALG00010012700", "LARP6L", "TDRD15", "ENSGALG00010005842",
                         "ENSGALG00010022658"],
                        ["PWP1", "ENSGALG00010010771", "RAE1", "TRMT61A", "CENPH", "DCK2"],
                        ["ENSGALG00010009046", "TRIM29", "ENSGALG00010010540", "ENSGALG00010006733",
                         "ENSGALG00010008611", "ENSGALG00010006990"],
                        ["ENSGALG00010006089", "DSCAM", "ENSGALG00010026631", "SGCZ", "ENSGALG00010014196",
                         "MSX2"],
                        ["AIF1L", "SUN2", "ENSGALG00010025600", "HRH2", "ENSGALG00010017323", "SH3BP1"],
                        ["ENSGALG00010015082", "ENSGALG00010019626", "BMX", "ENSGALG00010024367",
                         "ENSGALG00010008826", "ENSGALG00010003569"],
                        ["RUNX1", "CDK14", "PREX1", "PAG1", "CYFIP2", "TNRC6C"],
                        ["ENSGALG00010026615", "ENSGALG00010024355", "ZBTB43", "VWA3A", "CCDC141", "IRAG1"],
                        ["ENSGALG00010008041", "ENSGALG00010015639", "ENSGALG00010015058", "ENSGALG00010029885",
                         "ENSGALG00010016641", "ENSGALG00010016713"],
                        ["ENSGALG00010013950", "ENSGALG00010023025", "ENSGALG00010019862", "ENSGALG00010018778",
                         "ENSGALG00010007736", "ENSGALG00010004169"],
                        ["ANKRD9", "PACRG", "ENSGALG00010023594", "TIRAP", "C1orf43", "KXD1"],
                        ["NATD1", "MYLIP", "MBP", "ENSGALG00010000078", "SH3GLB2", "TNIP1"],
                        ["ALDH2", "RALY", "SLC2A11", "NUDT19", "HID1", "NBR1"],
                        ["ENSGALG00010005639", "ENSGALG00010015672", "ENSGALG00010008778", "ENSGALG00010018954",
                         "USH1G", "ENSGALG00010003723"],
                        ["GABRA1", "ENSGALG00010023920", "ENSGALG00010010342", "ENSGALG00010008818",
                         "ENSGALG00010024067", "ENSGALG00010025122"],
                        ["NIPA2", "DECR1", "CA12", "ENSGALG00010008541", "ESCO1", "ANXA11"],
                        ["ENSGALG00010015138", "PACSIN2", "INSIG2", "ENSGALG00010014394", "BCAR3", "CDC14B"],
                        ["CXCR5", "P2RY6", "DOK5", "ENSGALG00010021391", "ENSGALG00010015199", "LRRC61"],
                        ["NOP58", "PCNA", "RAN", "UTP18", "ENSGALG00010029439", "EDEM2"],
                        ["REEP5", "ENSGALG00010020176", "CDC14A", "ISCA1", "MCFD2", "ZFYVE21"],
                        ["ENSGALG00010023396", "ENSGALG00010022829", "ENSGALG00010026711", "ENSGALG00010008721",
                         "ENSGALG00010029103", "KLHL31"],
                        ["ENSGALG00010007653", "CXCL13L2", "ENSGALG00010020795", "ENSGALG00010015873",
                         "ENSGALG00010006586", "ENSGALG00010019775"],
                        ["ENSGALG00010008587", "ENSGALG00010014008", "ENSGALG00010022542", "ENSGALG00010007424",
                         "ENSGALG00010014071", "ENSGALG00010009723"],
                        ["S1PR4", "FAM65B", "TMEM132E", "ITGB7", "ENSGALG00010028467", "ENSGALG00010005585"],
                        ["TMIGD1", "SH3BP2", "MEP1B", "KCNJ16", "PIK3CB", "DPP4"],
                        ["ENSGALG00010025843", "ENSGALG00010023085", "SLC45A2", "ZIC2", "ENSGALG00010002204",
                         "ENSGALG00010000911"],
                        ["SPOCK3", "ENSGALG00010002485", "ENSGALG00010017254", "ENSGALG00010007390",
                         "ENSGALG00010010801", "ENSGALG00010017302"],
                        ["ENSGALG00010028427", "ENSGALG00010000696", "ENSGALG00010023758", "TRIM45", "CETP",
                         "C1QA"],
                        ["ENSGALG00010000344", "FAM210B", "ENSGALG00010011314", "ENSGALG00010017875", "MAB21L3",
                         "C3orf18"],
                        ["ENSGALG00010003355", "ENSGALG00010018272", "ENSGALG00010025356", "ENSGALG00010018321",
                         "ENSGALG00010029460", "ENSGALG00010026343"],
                        ["DDX20", "DUSP7", "NUFIP1", "ENSGALG00010019226", "ODC", "OR51E2"],
                        ["WDR33", "ABL1", "ADAM11", "CDK12", "NUP98", "AGRN"],
                        ["ENSGALG00010010239", "ENSGALG00010011766", "ENSGALG00010006419", "NELL1", "ASIP",
                         "ENSGALG00010007216"],
                        ["ENSGALG00010011985", "CD200R1B", "ENSGALG00010027633", "ENSGALG00010015784", "CPO",
                         "ENSGALG00010010794"],
                        ["ENSGALG00010003629", "ENSGALG00010013489", "TMEM215", "ENSGALG00010019304",
                         "ENSGALG00010016014", "ENSGALG00010014932"],
                        ["ENSGALG00010021312", "ADSS1", "PPP1R19L", "LMTK2", "ENSGALG00010013079", "KDM4C"],
                        ["OXLD1", "MTMR11", "ENSGALG00010027295", "ENSGALG00010026240", "FCSK", "CYB561D2"],
                        ["ENSGALG00010008097", "ENSGALG00010003545", "ENSGALG00010026607", "ENSGALG00010014449",
                         "ENSGALG00010029100", "ENSGALG00010026254"],
                        ["AMPD2", "CDON", "ENSGALG00010001780", "KIAA1324", "ZBTB7A", "FZD8"],
                        ["CCNG2", "FBXL3", "SELENOP1", "TINAG", "PLEKHS1", "YPEL5"],
                        ["EEF1E1", "GLRX2", "ENSGALG00010015356", "C9orf85", "SRSF10", "KRR1"],
                        ["FAM3D", "FAM76A", "ENSGALG00010028298", "TMED10", "SDCBP2", "PUF60"],
                        ["GALNT7", "MFN1", "DLD", "MICU2", "HMG20A", "PLS3"],
                        ["METTL23", "DNAJA4", "ENSGALG00010026672", "ENSGALG00010024603", "TK1", "TOR1B"],
                        ["ENSGALG00010016599", "ADRA2A", "ABCG5", "SLC22A16", "DAO", "USP2"],
                        ["FMO4", "BPIFB3", "ANO5", "FETUB", "ADH1C", "ENSGALG00010021522"],
                        ["IL1B", "CCL4", "IL13RA2", "ADM", "ENSGALG00010022313"],
                        ["CACNA1S", "CCLI5", "ENSGALG00010028678", "ENSGALG00010004198", "ENSGALG00010025776"],
                        ["RFX4", "ENSGALG00010011944", "AKAP7", "SUSD1", "MBLAC2"],
                        ["ENSGALG00010007371", "ENSGALG00010006629", "TMEM181", "SPATA17", "PLCB1"],
                        ["ENSGALG00010007776", "ENSGALG00010010704", "METTL4", "ANKRD26", "UBA2"],
                        ["NSMCE2", "BAG1", "EIF3E", "ENSGALG00010002582", "ENSGALG00010024324"],
                        ["ENSGALG00010006153", "U6", "ENSGALG00010005923", "ENSGALG00010027656",
                         "ENSGALG00010022331"],
                        ["TBX21", "ENSGALG00010003777", "MPL", "ENSGALG00010027582", "RGS19"],
                        ["PATL1", "ENSGALG00010019621", "KIAA1755", "HNRNPL", "GDF6"],
                        ["ENSGALG00010006086", "ENSGALG00010015603", "ENSGALG00010024293", "ERC2", "CCDC66"],
                        ["NBEA", "CLVS2", "CACNB2", "GDNF", "SEMA3A"],
                        ["ENSGALG00010018908", "ENSGALG00010014951", "ENSGALG00010021524", "ENSGALG00010016009",
                         "DNM3"],
                        ["ENSGALG00010013718", "ENSGALG00010023899", "ENSGALG00010009845", "ENSGALG00010023323",
                         "ENSGALG00010003093"], ["UBE2U", "C10orf2", "ENSGALG00010026195", "FARSA", "STIP1"],
                        ["ENSGALG00010003826", "PURG", "ENSGALG00010028319", "LRRC34", "MAP3K15"],
                        ["CASP8AP2", "ZNF148", "ENSGALG00010025836", "ABCB7", "ATM"],
                        ["KCNJ15", "LRRC39", "ENSGALG00010029176", "ENSGALG00010001839", "ENSGALG00010006904"],
                        ["UBQLN4", "STT3A", "PSMD2", "GUSB", "NUP62"],
                        ["ANKRD28", "PRICKLE1", "CHRNB4", "ENSGALG00010026770", "ENSGALG00010027809"],
                        ["ASH2L", "SH3GL2", "WNT16", "PBX1", "TSC22D2"],
                        ["IFRD1", "CAMK2D", "ANGEL2", "ZBTB26", "ZFAND5"],
                        ["SLC4A10", "ENSGALG00010017165", "ENSGALG00010002900", "ENSGALG00010023878",
                         "ENSGALG00010026848"],
                        ["ENSGALG00010015707", "ENSGALG00010013090", "CRISP2", "IL12B", "SEPT14"],
                        ["IMMP1L", "LSM5", "GNG13", "HAUS2", "THOC7"],
                        ["ENSGALG00010024069", "GCK", "ENSGALG00010013509", "FCHSD1", "ALKBH4"],
                        ["ENSGALG00010018445", "ENSGALG00010015781", "ENSGALG00010007587", "ENSGALG00010008854",
                         "ENSGALG00010028376"], ["ERI1", "ZNFY2", "GTF2F2", "NARS", "PCNP"],
                        ["CTBP2", "ENSGALG00010012071", "DDRGK1", "TCEA1", "ZCRB1"],
                        ["SFN", "ENSGALG00010025570", "ENSGALG00010006920", "ENSGALG00010008048",
                         "ENSGALG00010025792"], ["CTNNA1", "PEX14", "TAF5L", "RAB10", "CHUK"],
                        ["ENSGALG00010008732", "ENSGALG00010007704", "ENSGALG00010018545", "ENSGALG00010026442",
                         "ENSGALG00010005308"], ["INAFM2", "ENSGALG00010006038", "ANAPC11", "MED29", "PIGBOS1"],
                        ["ENSGALG00010023757", "ENSGALG00010009810", "CWC22", "JAK2", "VRK2"],
                        ["ENSGALG00010014337", "ENSGALG00010014420", "ENSGALG00010023092", "CALN1",
                         "RNase_MRP"],
                        ["ENSGALG00010019784", "ENSGALG00010004035", "ENSGALG00010019107", "ENSGALG00010018659",
                         "ENSGALG00010002286"], ["CMTR1", "RSAD2", "ENSGALG00010008221", "EPSTI1", "USP18"],
                        ["FAM175A", "LIMS1", "SYCE2", "ENSGALG00010002540", "B3GALNT1"],
                        ["SLC4A4", "MEI1", "HEATR5A", "TRAPPC9", "AREL1"],
                        ["ENSGALG00010004532", "CENPW", "CENPQ", "PDIA4", "EIF1AX"],
                        ["POMT2", "RBM33", "GPATCH2L", "GZF1", "FAM219A"],
                        ["SSH2", "SH2B2", "APBA3", "ENSGALG00010025449", "ZDHHC18"],
                        ["ENSGALG00010001519", "ENSGALG00010012012", "ENSGALG00010009687", "ENSGALG00010002221",
                         "ENSGALG00010010639"],
                        ["ENSGALG00010020066", "MOB3C", "ENSGALG00010019700", "CXCL13L3", "TPD52L2"],
                        ["ENSGALG00010018400", "DDX4", "SNX20", "LIX1", "GPR65"],
                        ["ENSGALG00010015937", "SYNDIG1L", "SLC6A12", "ENSGALG00010028033", "AMDHD1"],
                        ["ENSGALG00010006729", "ENSGALG00010007722", "ENSGALG00010007652", "ENSGALG00010014422",
                         "ENSGALG00010010583"], ["SIRT4", "MORN4", "PRKAG1", "BAAT", "FDXR"],
                        ["AATF", "KIF15", "NOLC1", "DNA2", "MCM10"],
                        ["ENSGALG00010023789", "ENSGALG00010026750", "DHRS9", "PHF21B", "ENSGALG00010006814"],
                        ["RASL11A", "P4HA3", "NECAB3", "NPTXR", "GAL3ST1"],
                        ["ENSGALG00010006147", "SLC6A1", "WASF3", "GPER1", "NTNG1"],
                        ["ENSGALG00010026620", "ENSGALG00010025704", "SOX11", "ENSGALG00010022048", "OLFM1"],
                        ["KDM7A", "MYO1E", "ADGRA3", "C2CD5", "ENSGALG00010016231"],
                        ["GATAD2B", "NFIC", "UPF1", "CACNA2D2", "UBAP2L"],
                        ["ENSGALG00010007790", "ENSGALG00010025973", "ENSGALG00010012789", "ENSGALG00010004448",
                         "ENSGALG00010007119"], ["PPP1R2", "MTDH", "SNX32", "MFSD8", "SDF4"],
                        ["GPR20", "STK31", "RASGEF1B", "ENSGALG00010014345", "OPN3"],
                        ["ENSGALG00010022501", "ENSGALG00010022570", "ENSGALG00010018637", "ENSGALG00010024348",
                         "ENSGALG00010014591"], ["LMO2", "ENSGALG00010005303", "BHLHA15", "PPAT", "SAA"],
                        ["ENSGALG00010008837", "CNTN3", "OPNVA", "WDR27", "ITGA2"],
                        ["C1orf232", "IL17RC", "DNAJC22", "C1orf74", "ENSGALG00010022968"],
                        ["ENSGALG00010006587", "DTHD1", "ENSGALG00010019774", "GABRB2", "ENSGALG00010020042"],
                        ["COA7", "AKR1D1", "ENSGALG00010016490", "ENSGALG00010021889", "ENSGALG00010009425"],
                        ["LANCL1", "INTS8", "RABL6", "MORC1", "VPS26B"],
                        ["DOCK2", "ENSGALG00010006445", "ABCG1", "WDFY4", "ANKRD44"],
                        ["HNF4A", "VIPR1", "ENSGALG00010002866", "RAVER2", "AXL"],
                        ["BCL11A", "PIGQ", "ERICH3", "CARD10", "RAP1GAP2"],
                        ["SEL1L3", "ACTN2", "BMPR1A", "PANK3", "MAN2A1"],
                        ["ENSGALG00010016176", "TTC36", "ENSGALG00010017412", "ENSGALG00010029078",
                         "ENSGALG00010007170"], ["ENSGALG00010019547", "USPL1", "SPICE1", "C5orf49", "ADAT1"],
                        ["DPH2", "DSN1", "NCBP2", "THOC3", "ELOF1"],
                        ["ENSGALG00010027989", "ZNF511", "TBL2", "ENSGALG00010029498", "AFMID"],
                        ["ENSGALG00010014888", "ENSGALG00010003534", "ENSGALG00010013807", "ENSGALG00010021392",
                         "ENSGALG00010012585"], ["ATG101", "KLF8", "SPRYD3", "ENSGALG00010025572", "BCL7B"],
                        ["ENSGALG00010013999", "ENSGALG00010016217", "ENSGALG00010014569", "ENSGALG00010010795",
                         "ENSGALG00010014660"], ["OGFOD3", "GABARAPL1", "PAPD5", "KCTD2", "MAPKAPK5"],
                        ["EIF4EBP1", "MEAF6", "ZNF593", "HIST1H3H", "CCDC27"],
                        ["ENSGALG00010006094", "ENSGALG00010028356", "ENSGALG00010007239", "ENSGALG00010012589",
                         "ENSGALG00010001095"],
                        ["SLC12A3", "ENSGALG00010026778", "ENSGALG00010011265", "ENSGALG00010025681", "DCX"],
                        ["RAB39B", "PFKFB2", "ARHGAP29", "ENSGALG00010030073", "PPP1R1C"],
                        ["HMGCR", "PPP4R1", "SLC12A7", "TSPAN14", "MED17"],
                        ["CDK5R1", "KIRREL3", "ACTG2", "GM2A", "RAB40C"],
                        ["FTH1", "MED9", "HNRNPKL", "CDKN2A", "GPX1"],
                        ["EZH2", "CCT8", "SDAD1", "FST", "METTL18"],
                        ["ENSGALG00010023505", "RPUSD2", "PUS1", "ENSGALG00010023171", "KNSTRN"],
                        ["FOXK1", "GBF1", "NPRL3", "INTS1", "EIF4G3"],
                        ["ENSGALG00010005120", "MIXL1", "ENSGALG00010023659", "ENSGALG00010027514",
                         "ENSGALG00010023554"],
                        ["ENSGALG00010013865", "LAMB4", "ENSGALG00010004570", "ENSGALG00010005196",
                         "ENSGALG00010023010"],
                        ["ENSGALG00010009109", "ENSGALG00010010215", "CLDND1", "H2AFY", "ENSGALG00010012015"],
                        ["ENSGALG00010012549", "ENSGALG00010007012", "ENSGALG00010009815", "ENSGALG00010014110",
                         "ENSGALG00010015818"],
                        ["ENSGALG00010027625", "ENSGALG00010016645", "ENSGALG00010011442", "ENSGALG00010025284",
                         "ENSGALG00010026585"], ["HSPA13", "HMGCS1", "TXNRD1", "ICE2", "SLC30A7"],
                        ["HOXB8", "ENSGALG00010012676", "ENSGALG00010005374", "MORN3", "ENSGALG00010016229"],
                        ["ENSGALG00010020652", "NYX", "RUNX2", "ENSGALG00010018433", "GRIN2B"],
                        ["ENSGALG00010004844", "AKAP6", "ENSGALG00010007058", "ENSGALG00010007190",
                         "ENSGALG00010005216"],
                        ["BDKRB1", "ENSGALG00010026211", "ENSGALG00010007739", "SERPINA10", "MSANTD1"],
                        ["SALL1", "MAP7D3", "CHRNA9", "ENSGALG00010005203", "CEP85L"],
                        ["KSR2", "ENSGALG00010005361", "ENSGALG00010000310", "ENSGALG00010000316", "LACTBL1"],
                        ["DIAPH3", "CDCA2", "CENPE", "BRIP1", "FBXO39"],
                        ["LY6E", "DEDD", "PLACL2", "MAFF", "ENSGALG00010008187"],
                        ["CHSY1", "ACTR8", "GPR39", "STX17", "UBE2D2"],
                        ["ENSGALG00010020780", "ENSGALG00010015106", "IMPG2", "ENSGALG00010013764", "GNB3"],
                        ["ENSGALG00010021551", "TET1", "ENSGALG00010020072", "ENSGALG00010023327", "LRP2"],
                        ["TOMT", "ENSGALG00010004106", "ENSGALG00010023502", "ENSGALG00010000560",
                         "ENSGALG00010029856"],
                        ["ENSGALG00010003839", "ART7B", "SMYD4", "ENSGALG00010004962", "SLC7A4"],
                        ["CPA6", "ENSGALG00010007958", "CYP24A1", "ENSGALG00010009096", "ENSGALG00010008676"],
                        ["SIPA1L2", "PDCD1LG2", "ENSGALG00010005295", "ZPLD1", "TC2N"],
                        ["LINS1", "LIG4", "MIER3", "FGL2", "ENSGALG00010009811"],
                        ["ANO3", "ZNF507", "RIMBP2", "RFX3", "DGKQ"],
                        ["IL7R", "HDGFL3", "TREM2", "MMP27", "SATB1"],
                        ["HPGD", "C7orf73", "FABP2", "ENSGALG00010029684", "ENSGALG00010020610"],
                        ["HN1", "ENSGALG00010022500", "TTC19", "WDR53", "COX5A"],
                        ["TRMT1L", "ENSGALG00010007232", "ARHGAP40", "PCDH11X", "TRPV1"],
                        ["ACTR10", "ARMC6", "CARS2", "TMEM11", "PRKRIP1"],
                        ["ARHGAP15", "FAM49A", "SYK", "TLR7", "IL18RAP"],
                        ["ENSGALG00010024292", "ENSGALG00010003221", "ENSGALG00010003182", "ENSGALG00010004498",
                         "ENSGALG00010003196"], ["CHD9", "MBOAT2", "SMG1", "HDX", "PAK3"],
                        ["CCDC186", "OVOA", "UGT8", "PLEKHA7", "ITPRID2"],
                        ["LRRC49", "BICC1", "ENSGALG00010025162", "FIGN", "C12H3orf14"],
                        ["PCYT2", "GHRH", "TMEM9", "DHDDS", "PIGW"],
                        ["PRCP", "ENSGALG00010027790", "NMRAL1", "DRD5", "ENSGALG00010006163"],
                        ["MRPS14", "PSMC5", "PTRH2", "YRDC", "SNRPC"],
                        ["ENSGALG00010009037", "CACNA1F", "GRIN2C", "CBX4", "SIRPA"],
                        ["DSCAML1", "MAL", "ENSGALG00010023876", "ENSGALG00010016441", "ENSGALG00010013058"],
                        ["GPN2", "ENSGALG00010018536", "NHP2", "ENHO", "B4GALT7"],
                        ["ENSGALG00010024359", "ENSGALG00010006669", "ENSGALG00010005665", "ENSGALG00010012294",
                         "ENSGALG00010027666"],
                        ["ENSGALG00010010328", "ENSGALG00010015394", "GJD2", "KCNA10", "ENSGALG00010013496"],
                        ["PREP", "ENSGALG00010007472", "PRR16", "ENSGALG00010008348", "PPP2R2C"],
                        ["MTAP", "C9orf72", "CDC42SE2", "KLHL5", "RNASET2"],
                        ["ENSGALG00010026498", "CEP170B", "DOCK5", "ENSGALG00010023346", "TAOK1"],
                        ["STX2", "GIPC2", "KRAS", "LCORL", "TMTC3"],
                        ["RPL32", "RPL26L1", "RPL36", "RPS2", "RPL7A"],
                        ["ENSGALG00010009718", "ENSGALG00010006596", "ENSGALG00010026605", "C6orf120",
                         "ENSGALG00010027620"], ["ARSA", "SOWAHA", "RUNDC1", "RIC8A", "TAP2"],
                        ["NRG4", "ENSGALG00010025839", "ENSGALG00010016164", "ENSGALG00010014013",
                         "ENSGALG00010001538"],
                        ["TBC1D32", "CERKL", "ENSGALG00010011739", "CNTNAP2", "ENSGALG00010006617"],
                        ["ENSGALG00010022350", "ENSGALG00010011194", "ENSGALG00010020372", "ENSGALG00010013540",
                         "ENSGALG00010023619"],
                        ["ENSGALG00010005059", "ENSGALG00010009938", "ENSGALG00010011270", "ENSGALG00010010787",
                         "ENSGALG00010015506"], ["SMAD6", "ARHGDIG", "NT5DC4", "FAM219B", "TMEM45BL"],
                        ["ENSGALG00010013864", "KCNK16", "PDE6B", "ENSGALG00010001996", "ENSGALG00010014401"],
                        ["ENSGALG00010000256", "ENSGALG00010005822", "ENSGALG00010019151", "ENSGALG00010016401",
                         "ENSGALG00010003213"], ["BECN1", "TMX4", "ENSGALG00010024800", "CHN1", "PMS2"],
                        ["EIF4EBP3", "EPS15", "ENSGALG00010005315", "TMEM131", "GIT2"],
                        ["ENSGALG00010012136", "ENSGALG00010007434", "DUSP19", "MYL12B", "HPCAL1"],
                        ["ENSGALG00010009849", "CYP2C23a", "ENSGALG00010002708", "NDRG1", "PELI3"],
                        ["CAPRIN2", "DLGAP5", "RPGRIP1L", "NCAPG2", "KIF20B"],
                        ["ENSGALG00010004563", "ENSGALG00010010656", "ENSGALG00010018798", "ENSGALG00010013279",
                         "ENSGALG00010016226"],
                        ["ENSGALG00010017525", "ENSGALG00010025955", "ENSGALG00010019353", "ENSGALG00010008898",
                         "ENSGALG00010007049"], ["ZFP91", "EBF2", "PGR", "ENSGALG00010006250", "ANKRD2"],
                        ["DSEL", "CYP3A5", "CDKL2", "FAM114A1", "ENSGALG00010029109"],
                        ["NEK8", "FBXL18", "TTI1", "RXRA", "FAM78B"],
                        ["ENSGALG00010025648", "ADAP2", "FKBP5", "ENSGALG00010025861", "HOMER3"],
                        ["CCR2", "HACD4", "VCAM1", "SLC10A2", "GPR183"],
                        ["NIPAL4", "ENSGALG00010018417", "ENSGALG00010025966", "ENSGALG00010002274",
                         "ENSGALG00010018346"], ["GJB2", "FOLH1", "C1orf101", "PIK3C2G", "SOAT1"],
                        ["B3GNT9", "ENSGALG00010028072", "ABCC3", "ENSGALG00010024070", "DDX51"],
                        ["EEPD1", "ENSGALG00010007238", "MMP17", "ENSGALG00010019299", "GUCA1A"],
                        ["NUP214", "KDM5A", "MED12", "GTF3C1", "MED1"],
                        ["ENSGALG00010025641", "ENSGALG00010027509", "ENSGALG00010012530", "ENSGALG00010018744",
                         "AGXT"], ["GASK1B", "GEN1", "CEP128", "GALNT3", "CP"],
                        ["PGAP1", "ENSGALG00010021711", "DGKH", "ENSGALG00010004375", "ENSGALG00010004994"],
                        ["ENSGALG00010010859", "NCAPH", "TRIP13", "CENPO", "CCNA2"],
                        ["DEPTOR", "ZNF319", "ENSGALG00010024266", "LRRC3C", "TRIM65"],
                        ["CCND3", "LIMD2", "GRAPL", "DOK3", "GNG2"],
                        ["MN1", "TMEM201", "GRAMD1B", "STK35", "DYSF"],
                        ["ENSGALG00010017135", "HELQ", "GTDC1", "SCARNA7", "ANKMY1"],
                        ["GOLT1B", "THAP12", "TTC8", "IL1RL1", "CHRNA5"],
                        ["RAI14", "RPS6KA5", "ENSGALG00010019818", "DOP1B", "ENSGALG00010018360"],
                        ["DHX57", "EP300", "ENSGALG00010002919", "NCOA5", "CREBBP"],
                        ["NPY7R", "ZNF704", "MBD3", "SERINC5", "UBE2QL1"],
                        ["SLBP", "ENSGALG00010011905", "5_8S_rRNA", "ANGPT1", "MINDY3"],
                        ["C21orf91", "TNFRSF4", "IGSF6", "ENSGALG00010002921", "AQP1"],
                        ["RABIF", "MIEN1", "GTF3C2", "EXOSC5", "COQ4"],
                        ["ENSGALG00010010582", "ENSGALG00010009095", "ENSGALG00010001384", "ENSGALG00010002833",
                         "ENSGALG00010020418"],
                        ["ENSGALG00010002871", "TLK1", "HACD2", "SRBD1", "ENSGALG00010003106"],
                        ["ENSGALG00010010598", "ENSGALG00010001331", "ENSGALG00010009751", "ENSGALG00010003369",
                         "CRB1"], ["ARSH", "ASNSD1", "LEPROTL1", "ENSGALG00010004012", "KCTD6"],
                        ["SUSD2", "ITGB6", "ENSGALG00010019281", "NRIP1", "ENSGALG00010015518"],
                        ["ENSGALG00010008908", "ENSGALG00010016084", "ENSGALG00010007291", "ENSGALG00010007015",
                         "ENSGALG00010013738"],
                        ["ENSGALG00010025088", "ENSGALG00010012874", "TSPEAR", "KCNK12", "ENSGALG00010000117"],
                        ["DAPK3", "ASPHD1", "SMTN", "CD34", "FLII"],
                        ["IL17REL", "CCL21", "IL20RA", "RLN3", "CTLA4"],
                        ["HOXD9", "ENSGALG00010029048", "ENSGALG00010001532", "PAQR9", "ENSGALG00010018783"],
                        ["MSGN1", "ENSGALG00010003401", "ENSGALG00010001492", "ENSGALG00010006829",
                         "ENSGALG00010029465"], ["RPL3", "RPL13", "ENSGALG00010029218", "TOMM5", "RPL18A"],
                        ["ZDHHC2", "WASHC5", "LSM11", "FAM149B1", "AGO1"],
                        ["RPL14", "RPL27A", "RPS8", "LYPLAL1", "ENY2"],
                        ["FRMD7", "TECTA", "ENSGALG00010016710", "ENSGALG00010025077", "ENSGALG00010025180"],
                        ["CELF4", "SNCA", "SNAP25", "CBLN3", "ENSGALG00010002556"],
                        ["ENSGALG00010006308", "ENSGALG00010005096", "ENSGALG00010013166", "ITGBL1",
                         "ENSGALG00010004037"], ["RAB11FIP5", "APBB1IP", "MYO18B", "ETS1", "DOCK8"],
                        ["METTL21A", "ZSWIM7", "SERF2", "FADS6", "LUC7L"],
                        ["NECAP2", "TCIRG1", "PIM1", "ENSGALG00010005254", "ADAM8"],
                        ["ENSGALG00010020720", "TBCCD1", "PYCR1", "ADRM1", "LRRC59"],
                        ["C12orf4", "C9ORF152", "CAPZA2", "LYVE1", "SERPINI1"],
                        ["ENSGALG00010002750", "B9D1", "PDCD11", "NUP155", "KNTC1"],
                        ["ENSGALG00010001707", "ENSGALG00010007069", "FGFBP1", "GRP", "EREG"],
                        ["RPL15", "RPS11", "DCPS", "RACK1", "EFHD2"],
                        ["VAC14", "CEP131", "CCM2L", "AP3B2", "CHST3"],
                        ["ENSGALG00010014433", "ENSGALG00010015593", "ENSGALG00010009863", "ENSGALG00010014021",
                         "ENSGALG00010014215"], ["RAD52", "GFM1", "FRZB", "TRAP1", "SOX9"],
                        ["ENSGALG00010023683", "ENSGALG00010016770", "ENSGALG00010022982", "ENSGALG00010016596",
                         "ENSGALG00010000565"],
                        ["ENSGALG00010026837", "CCKAR", "ENSGALG00010015860", "CSMD1", "ENSGALG00010010718"],
                        ["FAM83F", "MTSS1", "ENSGALG00010029850", "GDPD4", "PARP8"],
                        ["RDH5", "ENSGALG00010024113", "ENSGALG00010027955", "AIP", "ENSGALG00010026806"],
                        ["ARL11", "SIAH2", "OAT", "ADM2", "CTSD"], ["RPL4", "RPS27A", "RPS10", "RPL8", "RPS20"],
                        ["GANC", "UBAC1", "SLC44A1", "TPCN2", "ANKS6"],
                        ["GAMT", "HAND2", "NR2F1", "GFRA2", "SNCB"],
                        ["ASF1A", "ARPC5L", "FOPNL", "UXS1", "ENSGALG00010012473"],
                        ["ENSGALG00010015762", "ENSGALG00010004719", "ENSGALG00010025258", "ENSGALG00010027606",
                         "ENSGALG00010023858"],
                        ["ENSGALG00010015232", "ENSGALG00010016243", "ENSGALG00010016188", "ENSGALG00010007387",
                         "ENSGALG00010015968"],
                        ["MS4A4A", "PHYHD1", "ENSGALG00010005450", "EVA1CL", "ENSGALG00010004071"],
                        ["ENSGALG00010008892", "ENSGALG00010004196", "TMEM61", "ENSGALG00010001729", "PCGF1"],
                        ["ENSGALG00010014802", "ENSGALG00010007976", "ENSGALG00010000405", "ENSGALG00010008475",
                         "ENSGALG00010000752"], ["ENSGALG00010005330", "GSTA2", "NGF", "INHBB", "C8B"],
                        ["ENSGALG00010006935", "ENSGALG00010007268", "ENSGALG00010013049", "ENSGALG00010003188",
                         "ENSGALG00010000968"], ["TASOR", "LHX6", "USP49", "CDK5RAP2", "ENSGALG00010026108"],
                        ["RBM46", "ENSGALG00010018634", "SLC26A8", "ENPP3", "SLC7A6"],
                        ["SAMM50", "FAM32A", "CYB5D2", "ENSGALG00010005922", "ENSGALG00010027020"],
                        ["FMNL1", "LPXN", "MYO1G", "ARHGAP45", "KIF21B"],
                        ["ENSGALG00010000934", "REG4", "ENSGALG00010027839", "KCNJ12", "ENSGALG00010010170"],
                        ["ENSGALG00010005801", "ENSGALG00010026773", "ENSGALG00010020763", "ENSGALG00010001936",
                         "ENSGALG00010025008"]]

    df_0_4 = clusters_to_df(cluster_data_0_4)
    df_0_3 = clusters_to_df(cluster_data_0_3)
    df_0_2 = clusters_to_df(cluster_data_0_2)
    # Also prepare explore versions (using same data)
    df_0_4_explore = df_0_4.copy()
    df_0_3_explore = df_0_3.copy()
    df_0_2_explore = df_0_2.copy()

    try:
        fig_0_4 = px.sunburst(df_0_4, path=["Cluster", "Species"], values="Value", title="Threshold 0.4")
        fig_0_4.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_4 = pio.to_html(fig_0_4, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_04")
    except Exception as e:
        sunburst_html_0_4 = ""
    try:
        fig_0_3 = px.sunburst(df_0_3, path=["Cluster", "Species"], values="Value", title="Threshold 0.3")
        fig_0_3.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_3 = pio.to_html(fig_0_3, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_03")
    except Exception as e:
        sunburst_html_0_3 = ""
    try:
        fig_0_2 = px.sunburst(df_0_2, path=["Cluster", "Species"], values="Value", title="Threshold 0.2")
        fig_0_2.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_2 = pio.to_html(fig_0_2, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_02")
    except Exception as e:
        sunburst_html_0_2 = ""
    try:
        explore_fig_0_3 = px.sunburst(df_0_3_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.3")
        explore_fig_0_3.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_3 = pio.to_html(explore_fig_0_3, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_03")
    except Exception as e:
        explore_sunburst_html_0_3 = ""
    try:
        explore_fig_0_4 = px.sunburst(df_0_4_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.4")
        explore_fig_0_4.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_4 = pio.to_html(explore_fig_0_4, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_04")
    except Exception as e:
        explore_sunburst_html_0_4 = ""
    try:
        explore_fig_0_2 = px.sunburst(df_0_2_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.2")
        explore_fig_0_2.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_2 = pio.to_html(explore_fig_0_2, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_02")
    except Exception as e:
        explore_sunburst_html_0_2 = ""

    # ... your existing sunburst code here ...

    # ileum suggestions from DB
    # otu_list = IleumCorrelation.objects.values_list('var2', flat=True).distinct().order_by('var2')
    # Check from file csv the ileum
    try:
        otu_csv_path = os.path.join(settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                                    "otu_to_ileum.csv")
        df_otu = pd.read_csv(otu_csv_path , )
        otu_list = df_otu.iloc[:, 0].dropna().unique().tolist()
    except Exception as e:
        otu_list = []
        print(f"Error loading otu_to_ileum.csv: {e}")

    return render(request, f"{host_type}/ileum.html", {
        'host_type': host_type.title(),
        'data_type': 'Ileum',
        'description': 'Top 200 displayed only. Gene info from Ensembl REST.',
        # 'tissue_types': list(
        #     IleumCorrelation.objects.values_list('from_tissue', flat=True).distinct()
        # ),
        # Include your sunburst_html_* variables in context as before
        "sunburst_html_0_4": sunburst_html_0_4,
        "sunburst_html_0_3": sunburst_html_0_3,
        "sunburst_html_0_2": sunburst_html_0_2,
        "explore_sunburst_html_0_4": explore_sunburst_html_0_4,
        "explore_sunburst_html_0_3": explore_sunburst_html_0_3,
        "explore_sunburst_html_0_2": explore_sunburst_html_0_2,
        'otu_list': list(otu_list),
    })


#################################
#### Muscle access from database
#################################
from .models import MuscleCorrelation
from .models import MuscleCorrelationRoss


def muscle_data_analysisv2_ross(request, host_type='rossv2'):
    """
    1) Creates three sunbursts (thresholds 0.4, 0.3 & 0.2).

    """
    # --- AJAX Handling ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # (A) Load tissue: list distinct var2 (variables)
        if 'load_tissue' in request.GET:
            tissue = request.GET.get('tissue')
            vars_qs = MuscleCorrelationRoss.objects.filter(
                Q(from_tissue=tissue) | Q(to_tissue=tissue)
            ).values_list('var2', flat=True).distinct().order_by('var2')
            return J({'variables': list(vars_qs)})

        # (D) Cluster Lookup branch remains unchanged
        if  "cluster_lookup" in request.GET:
            selected_bacteria = request.GET.get("bacteria", "").strip()
            if not selected_bacteria:
                return JsonResponse({"found": False})

            found = False
            cluster_found = None
            threshold = None
            cluster_data_0_3 = [
                ["ENSGALG00010003598", "ENSGALG00010003613", "ENSGALG00010003635", "ENSGALG00010003537",
                 "ENSGALG00010003623", "ENSGALG00010003644", "ENSGALG00010003640", "ENSGALG00010003643",
                 "ENSGALG00010003575", "ENSGALG00010003584", "ENSGALG00010003563", "ENSGALG00010003614",
                 "ENSGALG00010003529", "ENSGALG00010003576", "ENSGALG00010003565"],
                ["TNMD", "COL1A1", "COL1A2", "COL12A1", "LTBP1", "COL11A1", "FNDC1",
                 "ENSGALG00010026410", "ABI3BP", "CREB3L1", "LOX", "COMP", "FMOD", "TGFBI"],
                ["ENSGALG00010002289", "ENSGALG00010003557", "ENSGALG00010003549", "ENSGALG00010002366",
                 "ENSGALG00010003626", "ENSGALG00010002378", "ENSGALG00010003625", "ENSGALG00010003633",
                 "ENSGALG00010003646", "ENSGALG00010003542", "ENSGALG00010002050"],
                ["IL17RC", "ENSGALG00010027359", "ENSGALG00010016500", "ENSGALG00010000353", "C12orf57",
                 "ENSGALG00010017207", "NDUFB6", "RPS28", "ENSGALG00010028201", "CHURC1"],
                ["NCOR1", "SYNE2", "RYR3", "MYPN", "HIPK3", "FRY", "AKAP9", "DST", "BIRC6", "HERC2"],
                ["COL5A1", "COL16A1", "COL6A2", "COL6A1", "COL6A3", "OBSL1", "MRC2", "ELN"],
                ["SHFM1", "UQCR10", "HINT2", "COX6C", "ATP5E", "USMG5", "ATP5PF", "NDUFA4"],
                ["FGG", "ENSGALG00010021130", "FGB", "FGA", "SPINK5", "ALB", "SPP2"],
                ["PIT54", "TTR", "ALDOB", "TF", "C3", "HPX", "AHSG"],
                ["DNAJC3", "PAFAH1B1", "ITSN1", "LAMP2", "MEF2C", "ENSGALG00010007137", "PHF3"],
                ["SLC43A2", "FOXK2", "PFKFB3", "GLUL", "SESN1", "KLHL24", "SEMA7A"],
                ["CLASP1", "SPAG9", "TLN2", "ENSGALG00010012055", "HERC1", "RERE", "KMT2C"],
                ["UCP3", "GPR157", "CDKN1B", "ENSGALG00010026046", "HIST1H101", "CEBPD", "KLF10"],
                ["HSPA8", "SAMD4A", "RSRP1", "JMJD6", "HSP90AA1", "PPP1R3C", "HSPA2"],
                ["SLN", "MLST8", "MCRS1", "PPP1CA", "COPS7A", "ENSGALG00010027927"],
                ["MARK3", "FAM120A", "STAU1", "PLCL2", "UBE4A", "QKI"],
                ["NMRK2", "ATP6V1D", "CARHSP1", "VDAC1", "ATP5PO", "ATP6V1E1"],
                ["RPS15", "RPL29", "RPS21", "RPL36", "UBA52", "RPL38"],
                ["DCUN1D5", "VPS37C", "CD63", "STUB1", "ENSGALG00010027282", "DNAJB2"],
                ["MPHOSPH6", "NDUFV3", "PFDN4", "RPS24", "MRPS31", "HSPE1"],
                ["RTRAF", "FUNDC1", "DNAJC2", "UBE2F", "UEVLD", "RSL24D1"],
                ["NID1", "MED13", "MYH9", "LAMA4", "MCAM", "CILP"],
                ["SNX21", "PRKAG3", "MYBPC2", "MRI1", "ENSGALG00010019255", "ENSGALG00010000588"],
                ["RPS11", "RACK1", "RPSAP58", "RPL4", "RPS26", "RPL15"],
                ["POLR2A", "LRP1", "TLN1", "FN1", "LAMB2", "ENSGALG00010003205"],
                ["USP47", "FOXJ3", "NFATC3", "AGL", "ENSGALG00010012102", "MYOM1"],
                ["DCN", "FAP", "MMP2", "MFAP5", "POSTN", "ANXA1"],
                ["RCN1", "TFRC", "CKAP4", "HSPA5", "HMGCR"],
                ["EIF4EBP2", "CAV3", "MMP15", "WSB2", "HRAS"],
                ["NISCH", "SPPL2A", "IPO7", "ARRDC4", "SGCB"],
                ["TMEM255A", "OPTN", "FAR1", "HIF1AN", "ENSGALG00010000003"],
                ["UPF3B", "SOD1", "HBBA", "HBA1", "HBAD"],
                ["RPL23", "RPS23", "RPL37", "EEF1B2", "RPL37A"],
                ["HSPA4", "ENSGALG00010011196", "NCOA4", "BAG3", "DDX46"],
                ["CACNA1S", "OGT", "SCN4A", "PLA2R1", "EPRS"],
                ["MXRA5", "SVEP1", "PKD1", "ENSGALG00010012436", "SPTBN1"],
                ["RNF114", "LDHA", "CRIPT", "GLO1", "PHAX"],
                ["STX18", "SNAP29", "CAPZA2", "LRRC2", "COPS2"],
                ["RPS15A", "RPL18A", "RPL27A", "ENSGALG00010029218", "RPL35A"],
                ["ITM2B", "BTF3", "PSMD7", "PDCL3", "FKBP3"],
                ["DNAJA2", "PSMD6", "ALDH7A1", "FH", "OLA1"],
                ["RPLP2", "RPL22", "RPS10", "RPL19", "RPL35"],
                ["ENSGALG00010000476", "ENSGALG00010010115", "UBR4", "OBSCN", "TTN"],
                ["CD81", "GDI1", "HNRNPH1", "PSMD2", "HNRNPR"],
                ["SMTNL2", "ENC1", "ATP2A2", "GPD2", "ENSGALG00010015603"],
                ["HSD17B10", "SGCA", "TOMM5", "ATP5D", "NDUFS7"],
                ["RETREG1", "PLA2G15", "CPT1A", "PDK4", "ELOVL1"],
                ["LETM1", "UBE2N", "ARPP19", "ATE1", "CUL2"],
                ["FLII", "GCN1", "RNF123", "PRRC2C", "DDB1"],
                ["RAB10", "KIF5B", "CTSD", "HBS1L", "MAT2B"],
                ["PNPLA2", "CLPX", "KIDINS220", "NAMPTP1", "UGP2"],
                ["ASB12", "STUM", "ATIC", "SREBF2", "AHCY"],
                ["TIMM17B", "TOMM6", "NDUFB2", "PFDN5", "NDUFB9"],
                ["NID2", "COL4A1", "COL4A2", "LAMB1", "EIF4G1"],
                ["RPS6KA3", "SLK", "AKAP6", "USP13", "PTPN21"],
                ["TTLL7", "SMCR8", "RILPL1", "GOLGA3", "NCEH1"],
                ["MICU2", "FBXW11", "ATL2", "ABRA", "IBTK"]]
            cluster_data_0_4 = [
                ["ENSGALG00010003598", "ENSGALG00010003613", "ENSGALG00010003635", "ENSGALG00010003537",
                 "ENSGALG00010003623", "ENSGALG00010003644", "ENSGALG00010003640", "ENSGALG00010003643",
                 "ENSGALG00010003575", "ENSGALG00010003584", "ENSGALG00010003563", "ENSGALG00010003614",
                 "ENSGALG00010003529", "ENSGALG00010003576", "ENSGALG00010003565"],
                ["TNMD", "COL1A1", "COL1A2", "COL12A1", "LTBP1", "COL11A1", "FNDC1",
                 "ENSGALG00010026410", "ABI3BP", "CREB3L1", "LOX", "COMP", "FMOD", "TGFBI"],
                ["ENSGALG00010002289", "ENSGALG00010003557", "ENSGALG00010003549", "ENSGALG00010002366",
                 "ENSGALG00010003626", "ENSGALG00010002378", "ENSGALG00010003625", "ENSGALG00010003633",
                 "ENSGALG00010003646", "ENSGALG00010003542", "ENSGALG00010002050"],
                ["HSPA8", "SAMD4A", "RSRP1", "JMJD6", "HSP90AA1", "PPP1R3C", "HSPA2"],
                ["FGG", "ENSGALG00010021130", "FGB", "FGA", "SPINK5", "ALB", "SPP2"],
                ["NID1", "MED13", "MYH9", "LAMA4", "MCAM", "CILP"],
                ["COL5A1", "MRC2", "COL6A2", "COL6A1", "COL6A3"],
                ["ENSGALG00010000353", "C12orf57", "NDUFB6", "RPS28", "ENSGALG00010016500"],
                ["TIMM17B", "TOMM6", "NDUFB2", "PFDN5", "NDUFB9"],
                ["ENSGALG00010000476", "ENSGALG00010010115", "UBR4", "OBSCN", "TTN"],
                ["RPS11", "RACK1", "RPSAP58", "RPS26", "RPL15"],
                ["NID2", "COL4A1", "COL4A2", "LAMB1", "EIF4G1"],
                ["HSPA4", "ENSGALG00010011196", "NCOA4", "BAG3", "DDX46"],
                ["FLII", "GCN1", "RNF123", "PRRC2C", "DDB1"]]

            cluster_data_0_5 = [
                ["ENSGALG00010003598", "ENSGALG00010003613", "ENSGALG00010003635", "ENSGALG00010003537",
                 "ENSGALG00010003623", "ENSGALG00010003644", "ENSGALG00010003640", "ENSGALG00010003643",
                 "ENSGALG00010003575", "ENSGALG00010003584", "ENSGALG00010003563", "ENSGALG00010003614",
                 "ENSGALG00010003529", "ENSGALG00010003576", "ENSGALG00010003565"],
                ["TNMD", "COL1A1", "COL1A2", "COL12A1", "LTBP1", "COL11A1", "FNDC1", "COMP", "FMOD",
                 "TGFBI"],
                ["ENSGALG00010003557", "ENSGALG00010003625", "ENSGALG00010003549", "ENSGALG00010003646",
                 "ENSGALG00010003633", "ENSGALG00010003542"],
                ["COL5A1", "MRC2", "COL6A2", "COL6A1", "COL6A3"],
                ["FLII", "GCN1", "RNF123", "PRRC2C", "DDB1"],
                ["ENSGALG00010002378", "ENSGALG00010002289", "ENSGALG00010002366", "ENSGALG00010003626",
                 "ENSGALG00010002050"]]

            for cluster in cluster_data_0_4:
                if selected_bacteria in cluster:
                    found = True
                    cluster_found = cluster
                    threshold = "0.4"
                    break
            if not found:
                for cluster in cluster_data_0_3:
                    if selected_bacteria in cluster:
                        found = True
                        cluster_found = cluster
                        threshold = "0.3"
                        break
            if not found:
                for cluster in cluster_data_0_5:
                    if selected_bacteria in cluster:
                        found = True
                        cluster_found = cluster
                        threshold = "0.5"
                        break
            if found:
                cleaned_cluster = [s.replace("s__", "") for s in cluster_found]
                return JsonResponse({
                    "found": True,
                    "threshold": threshold,
                    "cluster_members": cleaned_cluster,
                })
            else:
                return JsonResponse({"found": False})


        # ----- Common filters (only for branches that need tissue) -----
        # Common filters
        tissue = request.GET.get('tissue')
        if tissue is None:
            return J({'error': 'Missing tissue.'}, status=400)
        # base_tissue_q = Q(from_tissue=tissue) | Q(to_tissue=tissue)
        # here tissue is muscle to adapat for each case
        base_tissue_q = Q(from_tissue='muscle') & Q(to_tissue=tissue)

        # (B) Single-var filtering
        if ('multi_variable' not in request.GET
                and 'table_filter' not in request.GET
                and 'cluster_lookup' not in request.GET
                and 'explore_table_filter' not in request.GET
                and 'explore_distribution' not in request.GET):
            var = request.GET.get('variable')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = MuscleCorrelationRoss.objects.filter(
                base_tissue_q,
                var2=var,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({'results': [], 'total_count': 0})
            top = filt.order_by('-correlation')[:100]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count})

        # (C) Multi-var filtering
        if 'multi_variable' in request.GET:
            variables = request.GET.getlist('variables[]')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = MuscleCorrelationRoss.objects.filter(
                base_tissue_q,
                var2__in=variables,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({'results': [], 'total_count': 0})
            top = filt.order_by('-correlation')[:100]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count})



        # (E) Table Filtering
        if 'table_filter' in request.GET:
            var = request.GET.get('variable')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = MuscleCorrelationRoss.objects.filter(
                base_tissue_q,
                var2=var,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({
                    'results': [],
                    'total_count': 0,
                    'overview': {'median': None, 'q1': None, 'q3': None}
                })
            top = filt.order_by('-correlation')[:200]

            results = []
            vals = [o.correlation for o in filt]
            overview = {
                'median': r3(np.median(vals)),
                'q1': r3(np.quantile(vals, 0.25)),
                'q3': r3(np.quantile(vals, 0.75)),
            }
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'Coefficient': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count, 'overview': overview})

        # (F) Explore distribution
        if 'explore_distribution' in request.GET:
            # qs = MuscleCorrelation.objects.filter(base_tissue_q).values_list('correlation', flat=True)
            qs = (MuscleCorrelationRoss.objects
                 .filter(base_tissue_q, correlation__isnull=False)
                 .values_list('correlation', flat=True)
                )
            series = list(qs)
            if not series:
                return J({'error': 'No data found.'}, status=400)
            stats = {
                'min': r3(min(series)),
                'q1': r3(np.quantile(series, 0.25)),
                'median': r3(np.median(series)),
                'q3': r3(np.quantile(series, 0.75)),
                'max': r3(max(series)),
            }
            return J({'distribution': {'correlation_values': series, 'stats': stats}})

        # (G) Explore table filter
        if 'explore_table_filter' in request.GET:
            try:
                corr_min = float(request.GET.get('corrMin', -1))
                corr_max = float(request.GET.get('corrMax', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = MuscleCorrelationRoss.objects.filter(
                base_tissue_q,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            top = filt.order_by('-correlation')[:200]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            vals = [o.correlation for o in filt]
            overview = {
                'median': r3(np.median(vals)) if vals else None,
                'q1': r3(np.quantile(vals, 0.25)) if vals else None,
                'q3': r3(np.quantile(vals, 0.75)) if vals else None,
            }
            return J({'results': results, 'total_count': total_count, 'overview': overview})

        return J({'error': 'No recognized AJAX action.'}, status=400)

    # --- Non-AJAX: Build sunbursts and context ---
    def clusters_to_df(data):
        rows = []
        for i, sublist in enumerate(data, start=1):
            cluster_name = f"Cluster {i}"
            for species in sublist:
                rows.append({"Cluster": cluster_name, "Species": species.replace("s__", ""), "Value": 1})
        return pd.DataFrame(rows)

    cluster_data_0_3 = [
        ["ENSGALG00010003598", "ENSGALG00010003613", "ENSGALG00010003635", "ENSGALG00010003537",
         "ENSGALG00010003623", "ENSGALG00010003644", "ENSGALG00010003640", "ENSGALG00010003643",
         "ENSGALG00010003575", "ENSGALG00010003584", "ENSGALG00010003563", "ENSGALG00010003614",
         "ENSGALG00010003529", "ENSGALG00010003576", "ENSGALG00010003565"],
        ["TNMD", "COL1A1", "COL1A2", "COL12A1", "LTBP1", "COL11A1", "FNDC1",
         "ENSGALG00010026410", "ABI3BP", "CREB3L1", "LOX", "COMP", "FMOD", "TGFBI"],
        ["ENSGALG00010002289", "ENSGALG00010003557", "ENSGALG00010003549", "ENSGALG00010002366",
         "ENSGALG00010003626", "ENSGALG00010002378", "ENSGALG00010003625", "ENSGALG00010003633",
         "ENSGALG00010003646", "ENSGALG00010003542", "ENSGALG00010002050"],
        ["IL17RC", "ENSGALG00010027359", "ENSGALG00010016500", "ENSGALG00010000353", "C12orf57",
         "ENSGALG00010017207", "NDUFB6", "RPS28", "ENSGALG00010028201", "CHURC1"],
        ["NCOR1", "SYNE2", "RYR3", "MYPN", "HIPK3", "FRY", "AKAP9", "DST", "BIRC6", "HERC2"],
        ["COL5A1", "COL16A1", "COL6A2", "COL6A1", "COL6A3", "OBSL1", "MRC2", "ELN"],
        ["SHFM1", "UQCR10", "HINT2", "COX6C", "ATP5E", "USMG5", "ATP5PF", "NDUFA4"],
        ["FGG", "ENSGALG00010021130", "FGB", "FGA", "SPINK5", "ALB", "SPP2"],
        ["PIT54", "TTR", "ALDOB", "TF", "C3", "HPX", "AHSG"],
        ["DNAJC3", "PAFAH1B1", "ITSN1", "LAMP2", "MEF2C", "ENSGALG00010007137", "PHF3"],
        ["SLC43A2", "FOXK2", "PFKFB3", "GLUL", "SESN1", "KLHL24", "SEMA7A"],
        ["CLASP1", "SPAG9", "TLN2", "ENSGALG00010012055", "HERC1", "RERE", "KMT2C"],
        ["UCP3", "GPR157", "CDKN1B", "ENSGALG00010026046", "HIST1H101", "CEBPD", "KLF10"],
        ["HSPA8", "SAMD4A", "RSRP1", "JMJD6", "HSP90AA1", "PPP1R3C", "HSPA2"],
        ["SLN", "MLST8", "MCRS1", "PPP1CA", "COPS7A", "ENSGALG00010027927"],
        ["MARK3", "FAM120A", "STAU1", "PLCL2", "UBE4A", "QKI"],
        ["NMRK2", "ATP6V1D", "CARHSP1", "VDAC1", "ATP5PO", "ATP6V1E1"],
        ["RPS15", "RPL29", "RPS21", "RPL36", "UBA52", "RPL38"],
        ["DCUN1D5", "VPS37C", "CD63", "STUB1", "ENSGALG00010027282", "DNAJB2"],
        ["MPHOSPH6", "NDUFV3", "PFDN4", "RPS24", "MRPS31", "HSPE1"],
        ["RTRAF", "FUNDC1", "DNAJC2", "UBE2F", "UEVLD", "RSL24D1"],
        ["NID1", "MED13", "MYH9", "LAMA4", "MCAM", "CILP"],
        ["SNX21", "PRKAG3", "MYBPC2", "MRI1", "ENSGALG00010019255", "ENSGALG00010000588"],
        ["RPS11", "RACK1", "RPSAP58", "RPL4", "RPS26", "RPL15"],
        ["POLR2A", "LRP1", "TLN1", "FN1", "LAMB2", "ENSGALG00010003205"],
        ["USP47", "FOXJ3", "NFATC3", "AGL", "ENSGALG00010012102", "MYOM1"],
        ["DCN", "FAP", "MMP2", "MFAP5", "POSTN", "ANXA1"],
        ["RCN1", "TFRC", "CKAP4", "HSPA5", "HMGCR"],
        ["EIF4EBP2", "CAV3", "MMP15", "WSB2", "HRAS"],
        ["NISCH", "SPPL2A", "IPO7", "ARRDC4", "SGCB"],
        ["TMEM255A", "OPTN", "FAR1", "HIF1AN", "ENSGALG00010000003"],
        ["UPF3B", "SOD1", "HBBA", "HBA1", "HBAD"],
        ["RPL23", "RPS23", "RPL37", "EEF1B2", "RPL37A"],
        ["HSPA4", "ENSGALG00010011196", "NCOA4", "BAG3", "DDX46"],
        ["CACNA1S", "OGT", "SCN4A", "PLA2R1", "EPRS"],
        ["MXRA5", "SVEP1", "PKD1", "ENSGALG00010012436", "SPTBN1"],
        ["RNF114", "LDHA", "CRIPT", "GLO1", "PHAX"],
        ["STX18", "SNAP29", "CAPZA2", "LRRC2", "COPS2"],
        ["RPS15A", "RPL18A", "RPL27A", "ENSGALG00010029218", "RPL35A"],
        ["ITM2B", "BTF3", "PSMD7", "PDCL3", "FKBP3"],
        ["DNAJA2", "PSMD6", "ALDH7A1", "FH", "OLA1"],
        ["RPLP2", "RPL22", "RPS10", "RPL19", "RPL35"],
        ["ENSGALG00010000476", "ENSGALG00010010115", "UBR4", "OBSCN", "TTN"],
        ["CD81", "GDI1", "HNRNPH1", "PSMD2", "HNRNPR"],
        ["SMTNL2", "ENC1", "ATP2A2", "GPD2", "ENSGALG00010015603"],
        ["HSD17B10", "SGCA", "TOMM5", "ATP5D", "NDUFS7"],
        ["RETREG1", "PLA2G15", "CPT1A", "PDK4", "ELOVL1"],
        ["LETM1", "UBE2N", "ARPP19", "ATE1", "CUL2"],
        ["FLII", "GCN1", "RNF123", "PRRC2C", "DDB1"],
        ["RAB10", "KIF5B", "CTSD", "HBS1L", "MAT2B"],
        ["PNPLA2", "CLPX", "KIDINS220", "NAMPTP1", "UGP2"],
        ["ASB12", "STUM", "ATIC", "SREBF2", "AHCY"],
        ["TIMM17B", "TOMM6", "NDUFB2", "PFDN5", "NDUFB9"],
        ["NID2", "COL4A1", "COL4A2", "LAMB1", "EIF4G1"],
        ["RPS6KA3", "SLK", "AKAP6", "USP13", "PTPN21"],
        ["TTLL7", "SMCR8", "RILPL1", "GOLGA3", "NCEH1"],
        ["MICU2", "FBXW11", "ATL2", "ABRA", "IBTK"]]
    cluster_data_0_4 = [
        ["ENSGALG00010003598", "ENSGALG00010003613", "ENSGALG00010003635", "ENSGALG00010003537",
         "ENSGALG00010003623", "ENSGALG00010003644", "ENSGALG00010003640", "ENSGALG00010003643",
         "ENSGALG00010003575", "ENSGALG00010003584", "ENSGALG00010003563", "ENSGALG00010003614",
         "ENSGALG00010003529", "ENSGALG00010003576", "ENSGALG00010003565"],
        ["TNMD", "COL1A1", "COL1A2", "COL12A1", "LTBP1", "COL11A1", "FNDC1",
         "ENSGALG00010026410", "ABI3BP", "CREB3L1", "LOX", "COMP", "FMOD", "TGFBI"],
        ["ENSGALG00010002289", "ENSGALG00010003557", "ENSGALG00010003549", "ENSGALG00010002366",
         "ENSGALG00010003626", "ENSGALG00010002378", "ENSGALG00010003625", "ENSGALG00010003633",
         "ENSGALG00010003646", "ENSGALG00010003542", "ENSGALG00010002050"],
        ["HSPA8", "SAMD4A", "RSRP1", "JMJD6", "HSP90AA1", "PPP1R3C", "HSPA2"],
        ["FGG", "ENSGALG00010021130", "FGB", "FGA", "SPINK5", "ALB", "SPP2"],
        ["NID1", "MED13", "MYH9", "LAMA4", "MCAM", "CILP"],
        ["COL5A1", "MRC2", "COL6A2", "COL6A1", "COL6A3"],
        ["ENSGALG00010000353", "C12orf57", "NDUFB6", "RPS28", "ENSGALG00010016500"],
        ["TIMM17B", "TOMM6", "NDUFB2", "PFDN5", "NDUFB9"],
        ["ENSGALG00010000476", "ENSGALG00010010115", "UBR4", "OBSCN", "TTN"],
        ["RPS11", "RACK1", "RPSAP58", "RPS26", "RPL15"],
        ["NID2", "COL4A1", "COL4A2", "LAMB1", "EIF4G1"],
        ["HSPA4", "ENSGALG00010011196", "NCOA4", "BAG3", "DDX46"],
        ["FLII", "GCN1", "RNF123", "PRRC2C", "DDB1"]]

    cluster_data_0_5 = [
        ["ENSGALG00010003598", "ENSGALG00010003613", "ENSGALG00010003635", "ENSGALG00010003537",
         "ENSGALG00010003623", "ENSGALG00010003644", "ENSGALG00010003640", "ENSGALG00010003643",
         "ENSGALG00010003575", "ENSGALG00010003584", "ENSGALG00010003563", "ENSGALG00010003614",
         "ENSGALG00010003529", "ENSGALG00010003576", "ENSGALG00010003565"],
        ["TNMD", "COL1A1", "COL1A2", "COL12A1", "LTBP1", "COL11A1", "FNDC1", "COMP", "FMOD",
         "TGFBI"],
        ["ENSGALG00010003557", "ENSGALG00010003625", "ENSGALG00010003549", "ENSGALG00010003646",
         "ENSGALG00010003633", "ENSGALG00010003542"],
        ["COL5A1", "MRC2", "COL6A2", "COL6A1", "COL6A3"],
        ["FLII", "GCN1", "RNF123", "PRRC2C", "DDB1"],
        ["ENSGALG00010002378", "ENSGALG00010002289", "ENSGALG00010002366", "ENSGALG00010003626",
         "ENSGALG00010002050"]]

    df_0_4 = clusters_to_df(cluster_data_0_4)
    df_0_3 = clusters_to_df(cluster_data_0_3)
    df_0_5 = clusters_to_df(cluster_data_0_5)
    # Also prepare explore versions (using same data)
    df_0_4_explore = df_0_4.copy()
    df_0_3_explore = df_0_3.copy()
    df_0_5_explore = df_0_5.copy()

    try:
        fig_0_4 = px.sunburst(df_0_4, path=["Cluster", "Species"], values="Value", title="Threshold 0.4")
        fig_0_4.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_4 = pio.to_html(fig_0_4, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_04")
    except Exception as e:
        sunburst_html_0_4 = ""
    try:
        fig_0_3 = px.sunburst(df_0_3, path=["Cluster", "Species"], values="Value", title="Threshold 0.3")
        fig_0_3.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_3 = pio.to_html(fig_0_3, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_03")
    except Exception as e:
        sunburst_html_0_3 = ""
    try:
        fig_0_5 = px.sunburst(df_0_5, path=["Cluster", "Species"], values="Value", title="Threshold 0.5")
        fig_0_5.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_5 = pio.to_html(fig_0_5, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_02")
    except Exception as e:
        sunburst_html_0_5 = ""
    try:
        explore_fig_0_3 = px.sunburst(df_0_3_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.3")
        explore_fig_0_3.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_3 = pio.to_html(explore_fig_0_3, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_03")
    except Exception as e:
        explore_sunburst_html_0_3 = ""
    try:
        explore_fig_0_4 = px.sunburst(df_0_4_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.4")
        explore_fig_0_4.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_4 = pio.to_html(explore_fig_0_4, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_04")
    except Exception as e:
        explore_sunburst_html_0_4 = ""
    try:
        explore_fig_0_5 = px.sunburst(df_0_5_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.5")
        explore_fig_0_5.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_5 = pio.to_html(explore_fig_0_5, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_02")
    except Exception as e:
        explore_sunburst_html_0_5 = ""

    # ileum suggestions from DB
    # otu_list = IleumCorrelation.objects.values_list('var2', flat=True).distinct().order_by('var2')
    # Check from file csv the ileum
    # otu_list = []  # default if anything goes wrong
    try:
        otu_csv_path = os.path.join(settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "res_massive_lr_ross",
                                    "otu_to_muscle.csv")
        df_otu = pd.read_csv(otu_csv_path, )
        otu_list = df_otu.iloc[:, 0].dropna().unique().tolist()
    except Exception as e:
        otu_list = []
        print(f"Error loading otu_to_muscle.csv: {e}")

    return render(request, f"{host_type}/muscle.html", {
        "host_type": host_type.title(),
        "data_type": "Muscle",
        "description": "Top 200 displayed only. Gene info from Ensembl REST.",
        # "tissue_types": list(tissue_files_muscle.keys()),
        "sunburst_html_0_4": sunburst_html_0_4,
        "sunburst_html_0_3": sunburst_html_0_3,
        "sunburst_html_0_5": sunburst_html_0_5,
        "explore_sunburst_html_0_4": explore_sunburst_html_0_4,
        "explore_sunburst_html_0_3": explore_sunburst_html_0_3,
        "explore_sunburst_html_0_5": explore_sunburst_html_0_5,
        "otu_list": otu_list,
    })


def muscle_data_analysisv2(request, host_type='isabrownv2'):
    """
    1) Creates three sunbursts (thresholds 0.4, 0.3 & 0.2).

    """
    # --- AJAX Handling ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # (A) Load tissue: list distinct var2 (variables)
        if 'load_tissue' in request.GET:
            tissue = request.GET.get('tissue')
            vars_qs = MuscleCorrelation.objects.filter(
                Q(from_tissue=tissue) | Q(to_tissue=tissue)
            ).values_list('var2', flat=True).distinct().order_by('var2')
            return J({'variables': list(vars_qs)})

        # (D) Cluster Lookup branch remains unchanged
        if  "cluster_lookup" in request.GET:
            selected_bacteria = request.GET.get("bacteria", "").strip()
            if not selected_bacteria:
                return JsonResponse({"found": False})

            found = False
            cluster_found = None
            threshold = None
            cluster_data_0_3 = [["ENSGALG00010003598", "ENSGALG00010003613", "ENSGALG00010003635", "ENSGALG00010003537",
                                                         "ENSGALG00010003623", "ENSGALG00010003644", "ENSGALG00010003640", "ENSGALG00010003643",
                                                         "ENSGALG00010003575", "ENSGALG00010003584", "ENSGALG00010003563", "ENSGALG00010003614",
                                                         "ENSGALG00010003529", "ENSGALG00010003576", "ENSGALG00010003565"],
                                                        ["TNMD", "COL1A1", "COL1A2", "COL12A1", "LTBP1", "COL11A1", "FNDC1",
                                                         "ENSGALG00010026410", "ABI3BP", "CREB3L1", "LOX", "COMP", "FMOD", "TGFBI"],
                                                        ["ENSGALG00010002289", "ENSGALG00010003557", "ENSGALG00010003549", "ENSGALG00010002366",
                                                         "ENSGALG00010003626", "ENSGALG00010002378", "ENSGALG00010003625", "ENSGALG00010003633",
                                                         "ENSGALG00010003646", "ENSGALG00010003542", "ENSGALG00010002050"],
                                                        ["IL17RC", "ENSGALG00010027359", "ENSGALG00010016500", "ENSGALG00010000353", "C12orf57",
                                                         "ENSGALG00010017207", "NDUFB6", "RPS28", "ENSGALG00010028201", "CHURC1"],
                                                        ["NCOR1", "SYNE2", "RYR3", "MYPN", "HIPK3", "FRY", "AKAP9", "DST", "BIRC6", "HERC2"],
                                                        ["COL5A1", "COL16A1", "COL6A2", "COL6A1", "COL6A3", "OBSL1", "MRC2", "ELN"],
                                                        ["SHFM1", "UQCR10", "HINT2", "COX6C", "ATP5E", "USMG5", "ATP5PF", "NDUFA4"],
                                                        ["FGG", "ENSGALG00010021130", "FGB", "FGA", "SPINK5", "ALB", "SPP2"],
                                                        ["PIT54", "TTR", "ALDOB", "TF", "C3", "HPX", "AHSG"],
                                                        ["DNAJC3", "PAFAH1B1", "ITSN1", "LAMP2", "MEF2C", "ENSGALG00010007137", "PHF3"],
                                                        ["SLC43A2", "FOXK2", "PFKFB3", "GLUL", "SESN1", "KLHL24", "SEMA7A"],
                                                        ["CLASP1", "SPAG9", "TLN2", "ENSGALG00010012055", "HERC1", "RERE", "KMT2C"],
                                                        ["UCP3", "GPR157", "CDKN1B", "ENSGALG00010026046", "HIST1H101", "CEBPD", "KLF10"],
                                                        ["HSPA8", "SAMD4A", "RSRP1", "JMJD6", "HSP90AA1", "PPP1R3C", "HSPA2"],
                                                        ["SLN", "MLST8", "MCRS1", "PPP1CA", "COPS7A", "ENSGALG00010027927"],
                                                        ["MARK3", "FAM120A", "STAU1", "PLCL2", "UBE4A", "QKI"],
                                                        ["NMRK2", "ATP6V1D", "CARHSP1", "VDAC1", "ATP5PO", "ATP6V1E1"],
                                                        ["RPS15", "RPL29", "RPS21", "RPL36", "UBA52", "RPL38"],
                                                        ["DCUN1D5", "VPS37C", "CD63", "STUB1", "ENSGALG00010027282", "DNAJB2"],
                                                        ["MPHOSPH6", "NDUFV3", "PFDN4", "RPS24", "MRPS31", "HSPE1"],
                                                        ["RTRAF", "FUNDC1", "DNAJC2", "UBE2F", "UEVLD", "RSL24D1"],
                                                        ["NID1", "MED13", "MYH9", "LAMA4", "MCAM", "CILP"],
                                                        ["SNX21", "PRKAG3", "MYBPC2", "MRI1", "ENSGALG00010019255", "ENSGALG00010000588"],
                                                        ["RPS11", "RACK1", "RPSAP58", "RPL4", "RPS26", "RPL15"],
                                                        ["POLR2A", "LRP1", "TLN1", "FN1", "LAMB2", "ENSGALG00010003205"],
                                                        ["USP47", "FOXJ3", "NFATC3", "AGL", "ENSGALG00010012102", "MYOM1"],
                                                        ["DCN", "FAP", "MMP2", "MFAP5", "POSTN", "ANXA1"],
                                                        ["RCN1", "TFRC", "CKAP4", "HSPA5", "HMGCR"],
                                                        ["EIF4EBP2", "CAV3", "MMP15", "WSB2", "HRAS"],
                                                        ["NISCH", "SPPL2A", "IPO7", "ARRDC4", "SGCB"],
                                                        ["TMEM255A", "OPTN", "FAR1", "HIF1AN", "ENSGALG00010000003"],
                                                        ["UPF3B", "SOD1", "HBBA", "HBA1", "HBAD"],
                                                        ["RPL23", "RPS23", "RPL37", "EEF1B2", "RPL37A"],
                                                        ["HSPA4", "ENSGALG00010011196", "NCOA4", "BAG3", "DDX46"],
                                                        ["CACNA1S", "OGT", "SCN4A", "PLA2R1", "EPRS"],
                                                        ["MXRA5", "SVEP1", "PKD1", "ENSGALG00010012436", "SPTBN1"],
                                                        ["RNF114", "LDHA", "CRIPT", "GLO1", "PHAX"],
                                                        ["STX18", "SNAP29", "CAPZA2", "LRRC2", "COPS2"],
                                                        ["RPS15A", "RPL18A", "RPL27A", "ENSGALG00010029218", "RPL35A"],
                                                        ["ITM2B", "BTF3", "PSMD7", "PDCL3", "FKBP3"],
                                                        ["DNAJA2", "PSMD6", "ALDH7A1", "FH", "OLA1"],
                                                        ["RPLP2", "RPL22", "RPS10", "RPL19", "RPL35"],
                                                        ["ENSGALG00010000476", "ENSGALG00010010115", "UBR4", "OBSCN", "TTN"],
                                                        ["CD81", "GDI1", "HNRNPH1", "PSMD2", "HNRNPR"],
                                                        ["SMTNL2", "ENC1", "ATP2A2", "GPD2", "ENSGALG00010015603"],
                                                        ["HSD17B10", "SGCA", "TOMM5", "ATP5D", "NDUFS7"],
                                                        ["RETREG1", "PLA2G15", "CPT1A", "PDK4", "ELOVL1"],
                                                        ["LETM1", "UBE2N", "ARPP19", "ATE1", "CUL2"],
                                                        ["FLII", "GCN1", "RNF123", "PRRC2C", "DDB1"],
                                                        ["RAB10", "KIF5B", "CTSD", "HBS1L", "MAT2B"],
                                                        ["PNPLA2", "CLPX", "KIDINS220", "NAMPTP1", "UGP2"],
                                                        ["ASB12", "STUM", "ATIC", "SREBF2", "AHCY"],
                                                        ["TIMM17B", "TOMM6", "NDUFB2", "PFDN5", "NDUFB9"],
                                                        ["NID2", "COL4A1", "COL4A2", "LAMB1", "EIF4G1"],
                                                        ["RPS6KA3", "SLK", "AKAP6", "USP13", "PTPN21"],
                                                        ["TTLL7", "SMCR8", "RILPL1", "GOLGA3", "NCEH1"],
                                                        ["MICU2", "FBXW11", "ATL2", "ABRA", "IBTK"]]
            cluster_data_0_4 = [["ENSGALG00010003598", "ENSGALG00010003613", "ENSGALG00010003635", "ENSGALG00010003537",
                                 "ENSGALG00010003623", "ENSGALG00010003644", "ENSGALG00010003640", "ENSGALG00010003643",
                                 "ENSGALG00010003575", "ENSGALG00010003584", "ENSGALG00010003563", "ENSGALG00010003614",
                                 "ENSGALG00010003529", "ENSGALG00010003576", "ENSGALG00010003565"],
                                ["TNMD", "COL1A1", "COL1A2", "COL12A1", "LTBP1", "COL11A1", "FNDC1",
                                 "ENSGALG00010026410", "ABI3BP", "CREB3L1", "LOX", "COMP", "FMOD", "TGFBI"],
                                ["ENSGALG00010002289", "ENSGALG00010003557", "ENSGALG00010003549", "ENSGALG00010002366",
                                 "ENSGALG00010003626", "ENSGALG00010002378", "ENSGALG00010003625", "ENSGALG00010003633",
                                 "ENSGALG00010003646", "ENSGALG00010003542", "ENSGALG00010002050"],
                                ["HSPA8", "SAMD4A", "RSRP1", "JMJD6", "HSP90AA1", "PPP1R3C", "HSPA2"],
                                ["FGG", "ENSGALG00010021130", "FGB", "FGA", "SPINK5", "ALB", "SPP2"],
                                ["NID1", "MED13", "MYH9", "LAMA4", "MCAM", "CILP"],
                                ["COL5A1", "MRC2", "COL6A2", "COL6A1", "COL6A3"],
                                ["ENSGALG00010000353", "C12orf57", "NDUFB6", "RPS28", "ENSGALG00010016500"],
                                ["TIMM17B", "TOMM6", "NDUFB2", "PFDN5", "NDUFB9"],
                                ["ENSGALG00010000476", "ENSGALG00010010115", "UBR4", "OBSCN", "TTN"],
                                ["RPS11", "RACK1", "RPSAP58", "RPS26", "RPL15"],
                                ["NID2", "COL4A1", "COL4A2", "LAMB1", "EIF4G1"],
                                ["HSPA4", "ENSGALG00010011196", "NCOA4", "BAG3", "DDX46"],
                                ["FLII", "GCN1", "RNF123", "PRRC2C", "DDB1"]]

            cluster_data_0_2 = [["ENSGALG00010003598", "ENSGALG00010003613", "ENSGALG00010003635", "ENSGALG00010003537",
                                 "ENSGALG00010003623", "ENSGALG00010003644", "ENSGALG00010003640", "ENSGALG00010003643",
                                 "ENSGALG00010003575", "ENSGALG00010003584", "ENSGALG00010003563", "ENSGALG00010003614",
                                 "ENSGALG00010003529", "ENSGALG00010003576", "ENSGALG00010003565"],
                                ["TNMD", "COL1A1", "COL1A2", "COL12A1", "LTBP1", "COL11A1", "FNDC1", "COMP", "FMOD",
                                 "TGFBI"],
                                ["ENSGALG00010003557", "ENSGALG00010003625", "ENSGALG00010003549", "ENSGALG00010003646",
                                 "ENSGALG00010003633", "ENSGALG00010003542"],
                                ["COL5A1", "MRC2", "COL6A2", "COL6A1", "COL6A3"],
                                ["FLII", "GCN1", "RNF123", "PRRC2C", "DDB1"],
                                ["ENSGALG00010002378", "ENSGALG00010002289", "ENSGALG00010002366", "ENSGALG00010003626",
                                 "ENSGALG00010002050"]]

            for cluster in cluster_data_0_4:
                if selected_bacteria in cluster:
                    found = True
                    cluster_found = cluster
                    threshold = "0.4"
                    break
            if not found:
                for cluster in cluster_data_0_3:
                    if selected_bacteria in cluster:
                        found = True
                        cluster_found = cluster
                        threshold = "0.3"
                        break
            if not found:
                for cluster in cluster_data_0_2:
                    if selected_bacteria in cluster:
                        found = True
                        cluster_found = cluster
                        threshold = "0.2"
                        break
            if found:
                cleaned_cluster = [s.replace("s__", "") for s in cluster_found]
                return JsonResponse({
                    "found": True,
                    "threshold": threshold,
                    "cluster_members": cleaned_cluster,
                })
            else:
                return JsonResponse({"found": False})


        # ----- Common filters (only for branches that need tissue) -----
        # Common filters
        tissue = request.GET.get('tissue')
        if tissue is None:
            return J({'error': 'Missing tissue.'}, status=400)
        # base_tissue_q = Q(from_tissue=tissue) | Q(to_tissue=tissue)
        # here tissue is muscle to adapat for each case
        base_tissue_q = Q(from_tissue='muscle') & Q(to_tissue=tissue)

        # (B) Single-var filtering
        if ('multi_variable' not in request.GET
                and 'table_filter' not in request.GET
                and 'cluster_lookup' not in request.GET
                and 'explore_table_filter' not in request.GET
                and 'explore_distribution' not in request.GET):
            var = request.GET.get('variable')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = MuscleCorrelation.objects.filter(
                base_tissue_q,
                var2=var,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({'results': [], 'total_count': 0})
            top = filt.order_by('-correlation')[:100]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count})

        # (C) Multi-var filtering
        if 'multi_variable' in request.GET:
            variables = request.GET.getlist('variables[]')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = MuscleCorrelation.objects.filter(
                base_tissue_q,
                var2__in=variables,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({'results': [], 'total_count': 0})
            top = filt.order_by('-correlation')[:100]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count})



        # (E) Table Filtering
        if 'table_filter' in request.GET:
            var = request.GET.get('variable')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = MuscleCorrelation.objects.filter(
                base_tissue_q,
                var2=var,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({
                    'results': [],
                    'total_count': 0,
                    'overview': {'median': None, 'q1': None, 'q3': None}
                })
            top = filt.order_by('-correlation')[:200]

            results = []
            vals = [o.correlation for o in filt]
            overview = {
                'median': r3(np.median(vals)),
                'q1': r3(np.quantile(vals, 0.25)),
                'q3': r3(np.quantile(vals, 0.75)),
            }
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'Coefficient': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count, 'overview': overview})

        # (F) Explore distribution
        if 'explore_distribution' in request.GET:
            # qs = MuscleCorrelation.objects.filter(base_tissue_q).values_list('correlation', flat=True)
            qs = (MuscleCorrelation.objects
                 .filter(base_tissue_q, correlation__isnull=False)
                 .values_list('correlation', flat=True)
                )
            series = list(qs)
            if not series:
                return J({'error': 'No data found.'}, status=400)
            stats = {
                'min': r3(min(series)),
                'q1': r3(np.quantile(series, 0.25)),
                'median': r3(np.median(series)),
                'q3': r3(np.quantile(series, 0.75)),
                'max': r3(max(series)),
            }
            return J({'distribution': {'correlation_values': series, 'stats': stats}})

        # (G) Explore table filter
        if 'explore_table_filter' in request.GET:
            try:
                corr_min = float(request.GET.get('corrMin', -1))
                corr_max = float(request.GET.get('corrMax', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = MuscleCorrelation.objects.filter(
                base_tissue_q,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            top = filt.order_by('-correlation')[:200]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            vals = [o.correlation for o in filt]
            overview = {
                'median': r3(np.median(vals)) if vals else None,
                'q1': r3(np.quantile(vals, 0.25)) if vals else None,
                'q3': r3(np.quantile(vals, 0.75)) if vals else None,
            }
            return J({'results': results, 'total_count': total_count, 'overview': overview})

        return J({'error': 'No recognized AJAX action.'}, status=400)

    # --- Non-AJAX: Build sunbursts and context ---
    def clusters_to_df(data):
        rows = []
        for i, sublist in enumerate(data, start=1):
            cluster_name = f"Cluster {i}"
            for species in sublist:
                rows.append({"Cluster": cluster_name, "Species": species.replace("s__", ""), "Value": 1})
        return pd.DataFrame(rows)

    cluster_data_0_3 = [["ENSGALG00010003598", "ENSGALG00010003613", "ENSGALG00010003635", "ENSGALG00010003537",
                         "ENSGALG00010003623", "ENSGALG00010003644", "ENSGALG00010003640", "ENSGALG00010003643",
                         "ENSGALG00010003575", "ENSGALG00010003584", "ENSGALG00010003563", "ENSGALG00010003614",
                         "ENSGALG00010003529", "ENSGALG00010003576", "ENSGALG00010003565"],
                        ["TNMD", "COL1A1", "COL1A2", "COL12A1", "LTBP1", "COL11A1", "FNDC1",
                         "ENSGALG00010026410", "ABI3BP", "CREB3L1", "LOX", "COMP", "FMOD", "TGFBI"],
                        ["ENSGALG00010002289", "ENSGALG00010003557", "ENSGALG00010003549", "ENSGALG00010002366",
                         "ENSGALG00010003626", "ENSGALG00010002378", "ENSGALG00010003625", "ENSGALG00010003633",
                         "ENSGALG00010003646", "ENSGALG00010003542", "ENSGALG00010002050"],
                        ["IL17RC", "ENSGALG00010027359", "ENSGALG00010016500", "ENSGALG00010000353", "C12orf57",
                         "ENSGALG00010017207", "NDUFB6", "RPS28", "ENSGALG00010028201", "CHURC1"],
                        ["NCOR1", "SYNE2", "RYR3", "MYPN", "HIPK3", "FRY", "AKAP9", "DST", "BIRC6", "HERC2"],
                        ["COL5A1", "COL16A1", "COL6A2", "COL6A1", "COL6A3", "OBSL1", "MRC2", "ELN"],
                        ["SHFM1", "UQCR10", "HINT2", "COX6C", "ATP5E", "USMG5", "ATP5PF", "NDUFA4"],
                        ["FGG", "ENSGALG00010021130", "FGB", "FGA", "SPINK5", "ALB", "SPP2"],
                        ["PIT54", "TTR", "ALDOB", "TF", "C3", "HPX", "AHSG"],
                        ["DNAJC3", "PAFAH1B1", "ITSN1", "LAMP2", "MEF2C", "ENSGALG00010007137", "PHF3"],
                        ["SLC43A2", "FOXK2", "PFKFB3", "GLUL", "SESN1", "KLHL24", "SEMA7A"],
                        ["CLASP1", "SPAG9", "TLN2", "ENSGALG00010012055", "HERC1", "RERE", "KMT2C"],
                        ["UCP3", "GPR157", "CDKN1B", "ENSGALG00010026046", "HIST1H101", "CEBPD", "KLF10"],
                        ["HSPA8", "SAMD4A", "RSRP1", "JMJD6", "HSP90AA1", "PPP1R3C", "HSPA2"],
                        ["SLN", "MLST8", "MCRS1", "PPP1CA", "COPS7A", "ENSGALG00010027927"],
                        ["MARK3", "FAM120A", "STAU1", "PLCL2", "UBE4A", "QKI"],
                        ["NMRK2", "ATP6V1D", "CARHSP1", "VDAC1", "ATP5PO", "ATP6V1E1"],
                        ["RPS15", "RPL29", "RPS21", "RPL36", "UBA52", "RPL38"],
                        ["DCUN1D5", "VPS37C", "CD63", "STUB1", "ENSGALG00010027282", "DNAJB2"],
                        ["MPHOSPH6", "NDUFV3", "PFDN4", "RPS24", "MRPS31", "HSPE1"],
                        ["RTRAF", "FUNDC1", "DNAJC2", "UBE2F", "UEVLD", "RSL24D1"],
                        ["NID1", "MED13", "MYH9", "LAMA4", "MCAM", "CILP"],
                        ["SNX21", "PRKAG3", "MYBPC2", "MRI1", "ENSGALG00010019255", "ENSGALG00010000588"],
                        ["RPS11", "RACK1", "RPSAP58", "RPL4", "RPS26", "RPL15"],
                        ["POLR2A", "LRP1", "TLN1", "FN1", "LAMB2", "ENSGALG00010003205"],
                        ["USP47", "FOXJ3", "NFATC3", "AGL", "ENSGALG00010012102", "MYOM1"],
                        ["DCN", "FAP", "MMP2", "MFAP5", "POSTN", "ANXA1"],
                        ["RCN1", "TFRC", "CKAP4", "HSPA5", "HMGCR"],
                        ["EIF4EBP2", "CAV3", "MMP15", "WSB2", "HRAS"],
                        ["NISCH", "SPPL2A", "IPO7", "ARRDC4", "SGCB"],
                        ["TMEM255A", "OPTN", "FAR1", "HIF1AN", "ENSGALG00010000003"],
                        ["UPF3B", "SOD1", "HBBA", "HBA1", "HBAD"],
                        ["RPL23", "RPS23", "RPL37", "EEF1B2", "RPL37A"],
                        ["HSPA4", "ENSGALG00010011196", "NCOA4", "BAG3", "DDX46"],
                        ["CACNA1S", "OGT", "SCN4A", "PLA2R1", "EPRS"],
                        ["MXRA5", "SVEP1", "PKD1", "ENSGALG00010012436", "SPTBN1"],
                        ["RNF114", "LDHA", "CRIPT", "GLO1", "PHAX"],
                        ["STX18", "SNAP29", "CAPZA2", "LRRC2", "COPS2"],
                        ["RPS15A", "RPL18A", "RPL27A", "ENSGALG00010029218", "RPL35A"],
                        ["ITM2B", "BTF3", "PSMD7", "PDCL3", "FKBP3"],
                        ["DNAJA2", "PSMD6", "ALDH7A1", "FH", "OLA1"],
                        ["RPLP2", "RPL22", "RPS10", "RPL19", "RPL35"],
                        ["ENSGALG00010000476", "ENSGALG00010010115", "UBR4", "OBSCN", "TTN"],
                        ["CD81", "GDI1", "HNRNPH1", "PSMD2", "HNRNPR"],
                        ["SMTNL2", "ENC1", "ATP2A2", "GPD2", "ENSGALG00010015603"],
                        ["HSD17B10", "SGCA", "TOMM5", "ATP5D", "NDUFS7"],
                        ["RETREG1", "PLA2G15", "CPT1A", "PDK4", "ELOVL1"],
                        ["LETM1", "UBE2N", "ARPP19", "ATE1", "CUL2"],
                        ["FLII", "GCN1", "RNF123", "PRRC2C", "DDB1"],
                        ["RAB10", "KIF5B", "CTSD", "HBS1L", "MAT2B"],
                        ["PNPLA2", "CLPX", "KIDINS220", "NAMPTP1", "UGP2"],
                        ["ASB12", "STUM", "ATIC", "SREBF2", "AHCY"],
                        ["TIMM17B", "TOMM6", "NDUFB2", "PFDN5", "NDUFB9"],
                        ["NID2", "COL4A1", "COL4A2", "LAMB1", "EIF4G1"],
                        ["RPS6KA3", "SLK", "AKAP6", "USP13", "PTPN21"],
                        ["TTLL7", "SMCR8", "RILPL1", "GOLGA3", "NCEH1"],
                        ["MICU2", "FBXW11", "ATL2", "ABRA", "IBTK"]]
    cluster_data_0_4 = [["ENSGALG00010003598", "ENSGALG00010003613", "ENSGALG00010003635", "ENSGALG00010003537",
                         "ENSGALG00010003623", "ENSGALG00010003644", "ENSGALG00010003640", "ENSGALG00010003643",
                         "ENSGALG00010003575", "ENSGALG00010003584", "ENSGALG00010003563", "ENSGALG00010003614",
                         "ENSGALG00010003529", "ENSGALG00010003576", "ENSGALG00010003565"],
                        ["TNMD", "COL1A1", "COL1A2", "COL12A1", "LTBP1", "COL11A1", "FNDC1",
                         "ENSGALG00010026410", "ABI3BP", "CREB3L1", "LOX", "COMP", "FMOD", "TGFBI"],
                        ["ENSGALG00010002289", "ENSGALG00010003557", "ENSGALG00010003549", "ENSGALG00010002366",
                         "ENSGALG00010003626", "ENSGALG00010002378", "ENSGALG00010003625", "ENSGALG00010003633",
                         "ENSGALG00010003646", "ENSGALG00010003542", "ENSGALG00010002050"],
                        ["HSPA8", "SAMD4A", "RSRP1", "JMJD6", "HSP90AA1", "PPP1R3C", "HSPA2"],
                        ["FGG", "ENSGALG00010021130", "FGB", "FGA", "SPINK5", "ALB", "SPP2"],
                        ["NID1", "MED13", "MYH9", "LAMA4", "MCAM", "CILP"],
                        ["COL5A1", "MRC2", "COL6A2", "COL6A1", "COL6A3"],
                        ["ENSGALG00010000353", "C12orf57", "NDUFB6", "RPS28", "ENSGALG00010016500"],
                        ["TIMM17B", "TOMM6", "NDUFB2", "PFDN5", "NDUFB9"],
                        ["ENSGALG00010000476", "ENSGALG00010010115", "UBR4", "OBSCN", "TTN"],
                        ["RPS11", "RACK1", "RPSAP58", "RPS26", "RPL15"],
                        ["NID2", "COL4A1", "COL4A2", "LAMB1", "EIF4G1"],
                        ["HSPA4", "ENSGALG00010011196", "NCOA4", "BAG3", "DDX46"],
                        ["FLII", "GCN1", "RNF123", "PRRC2C", "DDB1"]]

    cluster_data_0_2 = [["ENSGALG00010003598", "ENSGALG00010003613", "ENSGALG00010003635", "ENSGALG00010003537",
                         "ENSGALG00010003623", "ENSGALG00010003644", "ENSGALG00010003640", "ENSGALG00010003643",
                         "ENSGALG00010003575", "ENSGALG00010003584", "ENSGALG00010003563", "ENSGALG00010003614",
                         "ENSGALG00010003529", "ENSGALG00010003576", "ENSGALG00010003565"],
                        ["TNMD", "COL1A1", "COL1A2", "COL12A1", "LTBP1", "COL11A1", "FNDC1", "COMP", "FMOD",
                         "TGFBI"],
                        ["ENSGALG00010003557", "ENSGALG00010003625", "ENSGALG00010003549", "ENSGALG00010003646",
                         "ENSGALG00010003633", "ENSGALG00010003542"],
                        ["COL5A1", "MRC2", "COL6A2", "COL6A1", "COL6A3"],
                        ["FLII", "GCN1", "RNF123", "PRRC2C", "DDB1"],
                        ["ENSGALG00010002378", "ENSGALG00010002289", "ENSGALG00010002366", "ENSGALG00010003626",
                         "ENSGALG00010002050"]]

    df_0_4 = clusters_to_df(cluster_data_0_4)
    df_0_3 = clusters_to_df(cluster_data_0_3)
    df_0_2 = clusters_to_df(cluster_data_0_2)
    # Also prepare explore versions (using same data)
    df_0_4_explore = df_0_4.copy()
    df_0_3_explore = df_0_3.copy()
    df_0_2_explore = df_0_2.copy()

    try:
        fig_0_4 = px.sunburst(df_0_4, path=["Cluster", "Species"], values="Value", title="Threshold 0.4")
        fig_0_4.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_4 = pio.to_html(fig_0_4, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_04")
    except Exception as e:
        sunburst_html_0_4 = ""
    try:
        fig_0_3 = px.sunburst(df_0_3, path=["Cluster", "Species"], values="Value", title="Threshold 0.3")
        fig_0_3.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_3 = pio.to_html(fig_0_3, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_03")
    except Exception as e:
        sunburst_html_0_3 = ""
    try:
        fig_0_2 = px.sunburst(df_0_2, path=["Cluster", "Species"], values="Value", title="Threshold 0.2")
        fig_0_2.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_2 = pio.to_html(fig_0_2, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_02")
    except Exception as e:
        sunburst_html_0_2 = ""
    try:
        explore_fig_0_3 = px.sunburst(df_0_3_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.3")
        explore_fig_0_3.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_3 = pio.to_html(explore_fig_0_3, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_03")
    except Exception as e:
        explore_sunburst_html_0_3 = ""
    try:
        explore_fig_0_4 = px.sunburst(df_0_4_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.4")
        explore_fig_0_4.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_4 = pio.to_html(explore_fig_0_4, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_04")
    except Exception as e:
        explore_sunburst_html_0_4 = ""
    try:
        explore_fig_0_2 = px.sunburst(df_0_2_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.2")
        explore_fig_0_2.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_2 = pio.to_html(explore_fig_0_2, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_02")
    except Exception as e:
        explore_sunburst_html_0_2 = ""

    # ileum suggestions from DB
    # otu_list = IleumCorrelation.objects.values_list('var2', flat=True).distinct().order_by('var2')
    # Check from file csv the ileum
    # otu_list = []  # default if anything goes wrong
    try:
        otu_csv_path = os.path.join(settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                                    "otu_to_muscle.csv")
        df_otu = pd.read_csv(otu_csv_path, )
        otu_list = df_otu.iloc[:, 0].dropna().unique().tolist()
    except Exception as e:
        otu_list = []
        print(f"Error loading otu_to_muscle.csv: {e}")

    return render(request, f"{host_type}/muscle.html", {
        "host_type": host_type.title(),
        "data_type": "Muscle",
        "description": "Top 200 displayed only. Gene info from Ensembl REST.",
        # "tissue_types": list(tissue_files_muscle.keys()),
        "sunburst_html_0_4": sunburst_html_0_4,
        "sunburst_html_0_3": sunburst_html_0_3,
        "sunburst_html_0_2": sunburst_html_0_2,
        "explore_sunburst_html_0_4": explore_sunburst_html_0_4,
        "explore_sunburst_html_0_3": explore_sunburst_html_0_3,
        "explore_sunburst_html_0_2": explore_sunburst_html_0_2,
        "otu_list": otu_list,
    })



#################################
#### Liver access from database
#################################
from .models import LiverCorrelation

def liver_data_analysisv2(request, host_type='isabrownv2'):
    """
    1) Creates three sunbursts (thresholds 0.4, 0.3 & 0.2).

    """
    # --- AJAX Handling ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # (A) Load tissue: list distinct var2 (variables)
        if 'load_tissue' in request.GET:
            tissue = request.GET.get('tissue')
            vars_qs = LiverCorrelation.objects.filter(
                Q(from_tissue=tissue) | Q(to_tissue=tissue)
            ).values_list('var2', flat=True).distinct().order_by('var2')
            return J({'variables': list(vars_qs)})

        # (D) Cluster Lookup branch remains unchanged
        if  "cluster_lookup" in request.GET:
            selected_bacteria = request.GET.get("bacteria", "").strip()
            if not selected_bacteria:
                return JsonResponse({"found": False})

            found = False
            cluster_found = None
            threshold = None
            cluster_data_0_3 = [["ENSGALG00010003557", "ENSGALG00010003644", "ENSGALG00010003584", "ENSGALG00010003635",
                                 "ENSGALG00010003643", "ENSGALG00010003537", "ENSGALG00010003598", "ENSGALG00010003640",
                                 "ENSGALG00010003576", "ENSGALG00010003565", "ENSGALG00010003614", "ENSGALG00010003563",
                                 "ENSGALG00010003575", "ENSGALG00010003613", "ENSGALG00010003623",
                                 "ENSGALG00010003529"], ["KIAA1524", "GEN1", "ATAD2", "CKAP5", "POLA1", "KIAA1328"],
                                ["ND4", "COX3", "ND2", "CYTB", "ATP6", "ND1"],
                                ["RCHY1", "ACBD6", "BLCAP", "LSM12", "MAD2L2", "KXD1"],
                                ["LRP5", "ZER1", "ABTB1", "ENSGALG00010014429", "DDHD1", "SLC22A23"],
                                ["P3H2", "ENSGALG00010022050", "ENSGALG00010017585", "TRMT2B", "AEBP1"],
                                ["AGO4", "NCOA6", "ZW10", "AGO1", "TAB3"],
                                ["WWC3", "SLC2A13", "AFDN", "KLF12", "USP53"],
                                ["HIF1AN", "CYP3A4", "ENSGALG00010003152", "ENSGALG00010025339", "MTFR1"],
                                ["CAPN15", "NOS3", "ENSGALG00010016848", "ENSGALG00010027348", "HIC1"],
                                ["ELAPOR2", "PDE5A", "VIPR2", "GFRA1", "SOX6"],
                                ["MCM5", "MCM3", "CDCA7", "RAD54L", "MCM2"],
                                ["SHE", "ENSGALG00010000571", "ENSGALG00010027227", "RNF215", "AIP"],
                                ["ENSGALG00010018015", "LMCD1", "STK11", "SLC4A1", "IGFBP2"],
                                ["SERPINB6", "ATP6V1C1", "CPE", "ASAH1", "C4BPM"],
                                ["FOXO4", "WDR81", "PDPR", "PGAP6", "UPF1"],
                                ["SPDL1", "ORC4", "COPS8", "GTF2H3", "TMX4"],
                                ["FAM162A", "DNAJC9", "MRPL20", "TMEM126A", "SSR1"],
                                ["MIPEP", "DPH6", "DARS", "K123", "ENSGALG00010006275"],
                                ["ENSGALG00010029171", "KAT2A", "PPRC1", "SMARCC1", "KANK4"],
                                ["ANK3", "PPL", "TNC", "COL6A3", "ENSGALG00010026320"],
                                ["ACTR5", "VWA9", "DDX10", "HEATR3", "POLR3B"],
                                ["TRIM28", "OGDH", "ARHGEF10L", "ATP13A1", "ALDH9A1"],
                                ["CHTF18", "PSMD10", "AIFM1", "SRSF7L", "ENSGALG00010018401"],
                                ["TOR1AIP2", "PATL1", "ENSGALG00010000081", "DYM", "PCBP2"],
                                ["NFS1", "SLC4A1AP", "PCCB", "ASS1", "SLC25A12"],
                                ["NAT8B", "TTC36", "PITHD1", "RNF166", "NAPRT"],
                                ["ENSGALG00010010901", "CCDC71L", "DEDD", "CCND3", "TBC1D22B"],
                                ["HEATR6", "GRB2", "CRKL", "KPNA1", "RBM15"],
                                ["SMYD4", "ING5", "CABLES1", "ENSGALG00010028453", "SERPINF2"]]
            cluster_data_0_2 = [["ENSGALG00010003557", "ENSGALG00010003644", "ENSGALG00010003584", "ENSGALG00010003635",
                                 "ENSGALG00010003643", "ENSGALG00010003537", "ENSGALG00010003598", "ENSGALG00010003640",
                                 "ENSGALG00010003576", "ENSGALG00010003565", "ENSGALG00010003614", "ENSGALG00010003563",
                                 "ENSGALG00010003575", "ENSGALG00010003613", "ENSGALG00010003623",
                                 "ENSGALG00010003529"],
                                ["ENSGALG00010018015", "LMCD1", "MERTK", "VNN2", "IGFBP2", "TOB2", "EHD3", "AARS2",
                                 "COL13A1", "STK11", "IDS", "CDK9", "SLC4A1", "APLP2"],
                                ["PIAS3", "ADGRG1", "ENG", "SGSM3", "STAT5A", "WLS", "HSPG2", "GPR182", "TIE1", "CD34",
                                 "ARSG", "HIP1"],
                                ["CYP4B7", "ACAD11", "ATIC", "HAO2", "ACOX1", "EHHADH", "FAM110B", "AQP11", "KYNU",
                                 "NCALD", "AASS", "FAXDC2"],
                                ["ENSGALG00010001804", "MBP", "NRG2", "SH3GLB2", "ENSGALG00010006728", "SPPL3", "F7",
                                 "PIK3IP1", "AADAT", "ENSGALG00010000853"],
                                ["HSPD1", "ORC6", "RARS", "ZNF622", "TCP1", "ACAD9", "HSPA9", "RCL1", "PSMG1",
                                 "FASTKD2"],
                                ["ENSGALG00010023758", "CTIF", "MTSS2", "CD151", "SSPN", "SUFU", "TEAD3", "DENND6B",
                                 "DNAJB5", "UBE2D2"],
                                ["FAM214A", "TRAK1", "CAPN5", "ENSGALG00010026220", "RAB43", "PAM", "ITIH2", "SORBS1",
                                 "PROS1", "ENSGALG00010004860"],
                                ["KIAA1524", "ATAD2", "CKAP5", "POLA1", "KIAA1328", "MSH6", "GEN1", "MMS22L", "CIT",
                                 "DNA2"],
                                ["ELAPOR2", "OSBPL5", "ABHD17B", "SOX6", "FBLN2", "PDE5A", "VIPR2", "IFT122", "GFRA1"],
                                ["MARK1", "ESRRG", "RCSD1", "NR3C2", "USP44", "KCNK7", "ENSGALG00010026760",
                                 "ENSGALG00010015643", "NAT"],
                                ["CDCA7L", "VASH2", "ENSGALG00010021677", "ACTL6A", "MGME1", "SEC61A2", "CDC37L1",
                                 "FAM60A", "GIPC2"],
                                ["GUCD1", "CHIR-IG1-5", "SOCS4", "DPEP2", "CPXM2", "CEP70", "TCTN1", "MYLK", "TMOD2"],
                                ["UQCRC1", "CCDC25", "GOLGA7", "GLOD4", "SAMM50", "ACTR10", "ENSGALG00010010850",
                                 "ACSS3", "PON1"], ["HIF1AN", "CYP3A4", "SLC16A12", "F2", "ENSGALG00010025339", "MTFR1",
                                                    "ENSGALG00010003152", "APOH", "ZC3H11A"],
                                ["HEATR6", "BAZ1B", "CRKL", "KPNA1", "GTF3C1", "RBM15", "DOT1L", "GRB2", "AP2B1"],
                                ["ENSGALG00010015356", "ENSGALG00010029333", "RFXAP", "DNAJC2", "UPRT", "DRG2", "NUTF2",
                                 "MRPL40", "FAM192A"],
                                ["TOR1AIP2", "ENSGALG00010000081", "SP2", "PATL1", "FBXO42", "SCAMP4", "DYM", "PCBP2",
                                 "SP1"], ["CHMP2A", "FAM222A", "DIS3L2", "FZR1", "NR1D1", "PABPC4", "DENND2B",
                                          "ENSGALG00010017752", "HOMER2"],
                                ["ERH", "THYN1", "MRPL47", "MRPL3", "SNRPE", "METTL5", "KNSTRN", "CNIH1", "BIRC5"],
                                ["TRIM28", "OGDH", "SLC17A9", "CREB3", "ENSGALG00010013472", "VPS45", "ARHGEF10L",
                                 "ATP13A1", "ALDH9A1"],
                                ["NIBAN2", "FHIP1B", "COLGALT1", "ESYT1", "FZD8", "RIPOR1", "SLC4A2", "HYAL2",
                                 "ENSGALG00010004099"],
                                ["EP300", "AGO4", "PLAGL2", "MBD5", "AGO1", "TAB3", "ZW10", "NCOA6", "ANKRD17"],
                                ["AQP3", "GRTP1", "ELK3", "HEXB", "HAVCR1", "TMEM230", "TMEM268", "ATP6V1B2", "COG7"],
                                ["CDCA9", "NOCT", "ENSGALG00010021950", "ENSGALG00010023748", "SESN1", "COQ10B",
                                 "KIAA1191", "FOXP1"],
                                ["ST7", "IBA57", "SEC23B", "ADPRHL2", "OSGEPL1", "LACTB", "THUMPD1", "PBX3"],
                                ["ATXN10", "SH3BGRL", "K123", "IFT52", "ENSGALG00010006275", "DARS", "DPH6", "MIPEP"],
                                ["SDK1", "PTGFRN", "TTL", "EPHB2", "ENSGALG00010025742", "TFCP2L1", "SPRY3", "DIP2C"],
                                ["RAB40B", "SIRT3", "ATP1B1", "NIPSNAP3A", "DERL3", "SOD3", "SUCNR1", "YY2"],
                                ["EEA1", "OSBPL8", "LMBRD2", "SCYL2", "PDPK1", "PIK3CA", "CDYL2", "NBEAL1"],
                                ["MRPL22", "RAD18", "SSR1", "HMGN5", "FAM162A", "DNAJC9", "MRPL20", "TMEM126A"],
                                ["ENSGALG00010028052", "ADAMTSL2", "SEPTIN5", "ATG13", "ATP2B2", "MATCAP2", "TCF3",
                                 "MVB12B"], ["STAB1", "NRP2", "ADORA2B", "KDR", "ARHGEF18", "SH3BP5", "GATA4",
                                             "ENSGALG00010015149"],
                                ["MIB1", "STAM", "HEATR1", "UBR5", "USP9Y", "AQR", "CLASP2", "XPO4"],
                                ["CBFB", "FRRS1L", "PCOLCE2", "ATF3", "RHOQ", "ENSGALG00010024764", "NSMF", "EAF2"],
                                ["PKNOX2", "FZD9", "PGM1", "CUEDC1", "SESN2", "RBFOX2", "NFE2L1", "GPR162"],
                                ["CAV1", "COLEC11", "BMP5", "FAM175A", "SPERT", "UBE2J1", "NCOA7", "RPGR"],
                                ["GLG1", "CDH1", "POMGNT1", "PIP5K1C", "SORL1", "POLDIP2", "CACNA2D2", "D2HGDH"],
                                ["ENDOV", "ENSGALG00010014319", "RPL38", "CLEC3B", "DPH3P1", "TOMM7", "CBX8",
                                 "ENSGALG00010026873"],
                                ["ENSGALG00010029857", "REXO1", "ANKRD11", "ORAI3", "SIRT4", "NUFIP2",
                                 "ENSGALG00010025137", "CLK2"],
                                ["ENSGALG00010022050", "TRMT2B", "FHOD1", "AEBP1", "COL16A1", "P3H2", "CLCN7",
                                 "ENSGALG00010017585"],
                                ["GXYLT1", "MSL3", "LYVE1", "CASP18", "VCAM1", "NSMAF", "RNMT", "ORC3"],
                                ["G6PC1", "ENSGALG00010016599", "KLHL26", "SLC20A1", "PIGQ", "OAT", "SMOX", "BHLHE40"],
                                ["WNK1", "EDEM3", "POMT2", "PIGO", "BCL2L13", "DENND5B", "LEMD3", "MIEF1"],
                                ["RTKN", "ENSGALG00010027348", "ENSGALG00010003882", "CAPN15", "NOS3",
                                 "ENSGALG00010016848", "TPP1", "HIC1"],
                                ["SFT2D2", "HSPA4L", "VKORC1L1", "GK5", "PITRM1", "GPS1", "USP47", "LARS1"],
                                ["SHANK3", "AATK", "MAF1", "ACTN4", "MAN2C1", "USP19", "PLEKHM1", "SLC25A1"],
                                ["JOSD1", "TNRC18", "ENSGALG00010000148", "ENSGALG00010008352", "FOXA1", "DAZAP2",
                                 "ZC3H4", "LCOR"],
                                ["TOGARAM1", "DHX33", "CYP1A1", "DVL3", "PI4KB", "POLR1B", "TRIM9", "GLIS2"],
                                ["WDR3", "GNB1L", "NKRF", "SNX3", "PRPF40A", "TBL3", "DDX51"],
                                ["PRCP", "LMBRD1", "LY86", "ZFAND1", "SLC15A4", "SUGCT", "PFKP"],
                                ["GLRX5", "UTP11", "NDUFAF1", "TMEM14A", "PRDX1", "CACYBP", "NDUFA4"],
                                ["RAPGEF3", "MT4", "ENSGALG00010003777", "BCAR1", "PYURF", "SIDT2", "SLC46A1"],
                                ["SUCLG2", "ERI2", "TRIM24", "MELK", "ECT2", "NUSAP1", "TANGO2"],
                                ["CYP2AC2", "ENSGALG00010018176", "ATL2", "SLC17A5", "FBLN1", "ACADSB", "GART"],
                                ["ENSGALG00010028419", "ENSGALG00010021256", "OASL", "DHX58", "IFITM5",
                                 "ENSGALG00010021272", "ENSGALG00010026316"],
                                ["ENSGALG00010020720", "MRAS", "ENSGALG00010009796", "SLC25A17", "CDKN2A", "SNRPGP15",
                                 "ENSGALG00010028085"],
                                ["TNS3", "WWC3", "TMEM245", "SLC2A13", "AFDN", "KLF12", "USP53"],
                                ["TUSC2", "SLC25A39", "CCT3", "PIP5K1A", "OTUB1", "CPSF1", "NUDCD3"],
                                ["BIN2", "RNF19B", "GBP", "C1QC", "ENSGALG00010028467", "C1QA", "BF1"],
                                ["DAP3", "SELENOK", "MAPRE1", "SPOUT1", "MYL6", "MRPS11", "HTD2"],
                                ["LOX", "ADAMTS12", "PXDN", "UGT8", "ANKRD50", "IQSEC1", "ENSGALG00010013071"],
                                ["ANP32E", "USP34", "C2CD5", "FNBP1L", "EML4", "IPO7", "PRKCZ"],
                                ["PLA2G4A", "MARCH1", "CD44", "CYBB", "TBXAS1", "CYSLTR2", "IKZF1"],
                                ["AHR1A", "MLH3", "MIGA1", "SOCS6", "ZBTB21", "ARHGAP5", "UBE3C"],
                                ["ABCC3", "ENSGALG00010022879", "LPCAT1", "ADA", "VWF", "MMRN2", "TNFRSF1A"],
                                ["CALR", "AXIN1", "ENSGALG00010024051", "CRPL2", "SNX27", "MFAP1", "HM13"],
                                ["PHAX", "FAM122B", "RAE1", "APIP", "TOPORS", "ZNF644", "ENSGALG00010014398"],
                                ["LLGL1", "ATL1", "ZBTB39", "RAVER1", "DCAF15", "MECP2", "TMEM186"],
                                ["SMARCAD1", "EIF4G2", "MSH2", "METTL14", "NUP37", "FGFR1OP", "KIF23"],
                                ["OPTN", "TBP", "RHOG2", "HMGA2", "ZBTB18", "ENSGALG00010005682", "SLC25A30"],
                                ["INTS12", "ENSGALG00010020074", "DUSP14", "CHAMP1", "ATF4", "ZFP36L1", "WIPI2"],
                                ["RAB18", "MOCS2", "TMEM38B", "ENSGALG00010016834", "HDAC11", "MYL12B", "RAB2A"],
                                ["SF3B4", "WIPF2", "ARRDC1", "YTHDF2", "CPSF7", "USF1", "FBXL14"],
                                ["TTC37", "MON2", "SEPTIN6", "NCBP1", "RELCH", "CCP110", "SYNE3"],
                                ["ENSGALG00010002750", "MASTL", "ZNF385D", "EZR", "PLK4", "ENSGALG00010000911",
                                 "PTDSS1"],
                                ["ENSGALG00010004592", "ENSGALG00010027015", "DNM1", "KLB", "NANS", "TOM1L2", "COL3A1"],
                                ["ENSGALG00010029171", "KAT2A", "PPRC1", "PLEKHG3", "SMARCC1", "ENSGALG00010004962",
                                 "KANK4"], ["ASXL2", "DOCK5", "ZC3H3", "ENSGALG00010017349", "LPP", "CYFIP2", "CD248"],
                                ["DNAJA1", "PRPF3", "TPRA1", "ENSGALG00010027306", "CERS5", "B4GALT4", "ATRIP"],
                                ["KIF2A", "UBLCP1", "CWC27", "TMEM192", "DTWD2", "LCORL", "UBE2N"],
                                ["RAC2", "LGALS3", "MAX", "ART7B", "CD48", "FCER1G", "ARHGDIB"],
                                ["EIF2D", "TBL1X", "TPRG1L", "KLHL14", "ADI1", "GPD1L2", "AGFG1"],
                                ["HERPUD2", "BTF3L4", "ENSGALG00010018371", "LGMN", "SDF4", "ADAL", "RCN2"],
                                ["HIKESHI", "AP3S1", "RNF146", "RMDN1", "CLDND1", "RPL34", "IMPACT"],
                                ["ITPKA", "HMGCS1", "CYLD", "PDK4", "GABARAPL1", "LRP12", "DAPK2"],
                                ["PODXL", "NEK8", "DGKD", "NOTCH1", "ATP2B4", "INO80D", "SIN3B"],
                                ["TMEM109", "PSMD4", "PEX11G", "MUL1", "SCAMP2", "TCN2", "IL6R"],
                                ["H2AFZ", "NIFK", "PSMB3", "TPI1", "HP1BP3", "CENPH", "AHSA1"],
                                ["LAPTM4A", "LIPA", "ABHD18", "TNFAIP8", "RTFDC1", "TANK", "ITM2A"],
                                ["LIX1L", "ARID3A", "TMEM184A", "ZSWIM5", "KANK3", "MLXIPL", "CDC42EP1"],
                                ["ADCK2", "VDAC2", "PMPCB", "ORAOV1", "MOCS3", "UCHL5", "ENSGALG00010025161"],
                                ["FOXM1", "SHCBP1", "INCENP", "KNTC1", "MANSC1", "ANLN", "KIF18A"],
                                ["ARPC1B", "IL2RG", "CDK5RAP1", "CNN2", "DMB2", "SLC2A6", "NRROS"],
                                ["DCP1B", "TPPP", "FST", "KCNJ8", "VAV3", "FHL1", "C5orf34"],
                                ["TBC1D13", "SLC25A42", "RNF123", "NDST1", "BLTP2", "ABCA2", "ENSGALG00010013362"],
                                ["ENSGALG00010023776", "PIGR", "PNPLA7", "DOLK", "ACOX2", "GLDC", "KMO"],
                                ["EGLN1", "CDC42EP3", "ENSGALG00010016051", "ELL2", "SREK1", "AHI1", "TRPC1"],
                                ["ASL1", "EXFABP", "TLR1B", "PSTPIP2", "HTR7", "SCPEP1", "LAPTM5"],
                                ["DDX5", "VPS18", "ERCC3", "POLG2", "IKBKB", "LRPPRC", "ARGLU1"],
                                ["ENSGALG00010018598", "PNPLA6", "C3", "EVI5L", "WDR59", "ADAMTS15", "PCASP2"],
                                ["USP54", "SPRED2", "GUCY2C", "ADPGK", "RCOR3", "B3GALT6", "OVCH2"],
                                ["NDUFB3", "ACYP2", "OAZ2", "LAMTOR3", "NDUFB5", "MIF4GD", "COX5A"],
                                ["POLL", "CTNNA1", "ABHD16A", "POGZ", "SARDH", "SLC8B1", "MID2"],
                                ["EPHB1", "IGF2BP1", "YARS", "USP5", "TBCC", "RAI1", "GTF2E1"],
                                ["SLC12A4", "ENSGALG00010024433", "PARG", "ATRNL1", "ABCC4", "BORCS5", "FAM241A"],
                                ["PAXIP1", "ENSGALG00010012244", "KBTBD2", "SART3", "PTBP1", "CAMSAP1"],
                                ["BUB3", "RABL3", "PRIM2", "AGK", "NUP107", "RALB"],
                                ["ENSGALG00010015148", "SOCS1", "RAP1GAP3", "RNF141", "NAP1L1", "SORBS2"],
                                ["KIAA1429", "KDM5A", "FBXL17", "GPATCH2L", "ANKS3", "SUPT7L"],
                                ["PLEKHM3", "DLC1", "IDUA", "ADGRF5", "KIF3A", "TET2"],
                                ["DPYD", "ERICH3", "ENSGALG00010010802", "ENSGALG00010023368", "WRN", "SCN4A"],
                                ["IL2RB", "JARID2", "KLF3", "RBM6", "PTPN6", "PTK2"],
                                ["ENSGALG00010024682", "ENSGALG00010023880", "PHPT1", "TUBA1A", "CDC6", "CDK2"],
                                ["TLR3", "IFIH1", "PARP9", "EIF2AK2", "PARP12", "ENSGALG00010022207"],
                                ["BLM", "TXNDC16", "DDX11", "CLSPN", "GPR75", "TOPBP1"],
                                ["VDHAP", "GOT2", "FMO3", "ENSGALG00010026947", "ACAA1", "GSTK1"],
                                ["DAAM2", "FAM102A", "SLC4A4", "VIPR1", "NR3C1", "ST8SIA5"],
                                ["ENSGALG00010009849", "PLAGL1", "PRRG4", "PLEKHA1", "BIRC8", "USP16"],
                                ["SOX5", "ARRB1", "TTC17", "GIGYF2", "A1CF", "MAGI1"],
                                ["DIP2A", "SNX8", "CPED1", "DENND4A", "FYCO1", "TMPPE"],
                                ["C1orf131", "DNAJC18", "BAMBI", "DHRSX", "ENSGALG00010025126", "SPRY2"],
                                ["PHF3", "USP7", "ENSGALG00010009457", "PDXDC1", "FAM199X", "CSDE1"],
                                ["PIK3R6", "GM2A", "NCF1C", "HPSE", "SMAP2", "SERPING1"],
                                ["UBE2W", "EDNRB", "CASD1", "LTBP1", "NT5E", "SGCE"],
                                ["MAP1LC3A", "UBE2Q2", "PIGH", "ENSGALG00010011742", "HIC2", "BTG1L"],
                                ["ARHGAP10", "SLC7A2", "ENSGALG00010006525", "TACC2", "EEF2K", "HSF3"],
                                ["THOC5", "ASH2L", "MOB3A", "SARNP", "AK2", "NUP62"],
                                ["ERP29", "SPP2", "AvBD9", "SGK2", "ATP5J2", "HIBCH"],
                                ["EXTL2", "UNKL", "PAN3", "WTIP", "SPATA2", "ZNF280D"],
                                ["UBE2H", "CNOT10", "WIPF3", "GPHN", "ACSL5", "NPAS2"],
                                ["ENSGALG00010007873", "ENSGALG00010027409", "ENSGALG00010014994", "RPL36", "CYB5RL",
                                 "P3H3"], ["NDOR1", "MAP2K5", "HYI", "ENSGALG00010013915", "TM2D2", "STK16"],
                                ["NHLRC3", "XPO1", "UGGT2", "EPS15", "RBM12", "ENSGALG00010018857"],
                                ["ZEB1", "CAPSL", "TTN", "ANGPT1", "PLCXD1", "PLEKHF2"],
                                ["CAPZA2", "BZW2", "TMEM70", "CCNB1", "DHFR", "DCTN5"],
                                ["MRPS22", "PCNA", "RAN", "DEPDC7", "ARPC1A", "RFC2"],
                                ["JPH1", "NAA16", "TAF2", "TDG", "TAF5", "MMRN1"],
                                ["ENSGALG00010012742", "PARP1", "GPI", "WDR90", "LONP1", "NOM1"],
                                ["ADAP1", "GALK1", "SFXN2", "SLC29A1", "SCD", "CS"],
                                ["IKZF4", "KANSL1", "ZNF142", "HIP1R", "KMT2D", "ZDHHC5"],
                                ["NUP43", "NUP133", "CHEK2", "POP1", "SUCLA2", "ZDHHC13"],
                                ["GATAD2B", "SENP8", "R3HDM2", "BCL9L", "SEPTIN9", "CHST13"],
                                ["KIF11", "ATAD5", "TRIM59", "TMEM63A", "KIF15", "TTK"],
                                ["UCHL3", "DPM1", "RPF1", "TXNL4A", "BCCIP", "CRELD2"],
                                ["RPS21", "RPL30", "ENSGALG00010029344", "FAM8A1", "TTC30B", "SPINK4"],
                                ["KAZN", "PAQR3", "CUEDC2", "B4GALNT4", "SLC35E3", "GTF3C5"],
                                ["ENSGALG00010014578", "PCYT1A", "OPHN1", "SCMH1", "ENSGALG00010029524", "ASAP3"],
                                ["YOD1", "ECPAS", "ENSGALG00010025477", "TRIM32", "ZZEF1", "DDI2"],
                                ["FBXW7", "MPPED1", "LGALS2", "TRAF3IP1", "ENSGALG00010010309", "RSBN1L"],
                                ["APP", "PHOSPHO1", "WIPI1", "ARMH4", "PLPP3", "ENSGALG00010027617"],
                                ["NUP210", "ARNT2", "CHSY1", "IARS1", "USP40", "GFPT1"],
                                ["CLN5", "FUBP3", "TMPRSS2", "PCYOX1", "MXD1", "ENSGALG00010005585"],
                                ["ND4", "COX3", "ND2", "CYTB", "ATP6", "ND1"],
                                ["MRPS31", "DYL1", "EIF2S1", "COPS4", "FAM89A", "CBR4"],
                                ["BCKDHB", "ACADL", "SDHB", "PGRMC1", "MARC1", "ATP5PO"],
                                ["FGA", "MAPK8IP3", "BACH2", "ENSGALG00010002894", "ENSGALG00010017350", "GCNT4"],
                                ["KIAA0232", "BNIP2", "FGD6", "RIPOR3", "HYCC2", "SF3B1"],
                                ["TESK2", "LAMB2", "ENSGALG00010026241", "SLC7A5", "CERS1", "C8B"],
                                ["MCRIP2", "ACOT8", "PMM1", "SRXN1", "ENSGALG00010018284", "PFKFB1"],
                                ["MTHFD2", "HKDC1", "ANGPTL3", "ENSGALG00010026889", "C4orf54", "HDAC9"],
                                ["RCHY1", "ACBD6", "BLCAP", "LSM12", "MAD2L2", "KXD1"],
                                ["ENSGALG00010009129", "ABHD1", "KHK", "ENSGALG00010006055", "ENSGALG00010004046",
                                 "ENSGALG00010006131"],
                                ["ENSGALG00010026293", "KRIT1", "LRIF1", "ARHGEF3", "SERAC1", "ENSGALG00010026720"],
                                ["POLD1", "WDR76", "ESCO2", "NCBP2", "LIG1", "CTPS1"],
                                ["ENSGALG00010012286", "MYH1B", "ENSGALG00010003287", "ENSGALG00010003609", "5_8S_rRNA",
                                 "ENSGALG00010003258"],
                                ["INF2", "INPP5D", "PIK3R5", "WDFY4", "ENSGALG00010021441", "LRRK1"],
                                ["ENSGALG00010021566", "SWT1", "AQP9", "BRE", "ARL8B", "FBXO11"],
                                ["ENSGALG00010004505", "ATRN", "PLD1", "RECQL5", "FNIP1", "MFSD13A"],
                                ["RPLP1", "RPS17", "RPS3", "CIB1", "CALML4", "RACK1"],
                                ["ASMTL", "BRCA1", "RTTN", "HAUS3", "ZRANB3", "ATR"],
                                ["C2CD3", "FANCA", "CEP85", "ZNF367", "MCM10", "TERF2"],
                                ["PIDD1", "NEDD4L", "ENSGALG00010022678", "CLCN5", "CETP", "TRPC4AP"],
                                ["TTR", "PRXL2A", "TMEM254", "COX4I1", "FBP1", "HADH"],
                                ["ENSGALG00010014249", "FBXO45", "TPST1", "NME3", "ENSGALG00010026607", "TCOF1"],
                                ["GPN3", "HAT1", "MRPL19", "GMNN", "BLOC1S4", "SPC25"],
                                ["CNN3", "ATG4C", "SNAP29", "NUB1", "SVIP", "ITFG1"],
                                ["ENSGALG00010001372", "ENSGALG00010001283", "BCAS3", "ENSGALG00010001244", "WWP2",
                                 "FLII"], ["FPGT", "SH3GLB1", "SYPL1", "ARF1", "TPM1", "LDHA"],
                                ["SNX19", "GLTP", "SRRD", "TLE3", "MOB1A", "ENSGALG00010022034"],
                                ["PODN", "ZNF598", "RAB11FIP1", "USP20", "DPP9", "LARP1"],
                                ["SMARCB1", "WDR5B", "TSSC4", "ENSGALG00010012079", "PA2G4", "CENPT"],
                                ["BORCS8", "ENSGALG00010026046", "PPA2", "RPL8", "KLHL3", "DCTN1"],
                                ["CUL1", "ZNF518A", "LTN1", "XPOT", "ENSGALG00010009117", "SCFD1"],
                                ["ARHGAP35", "SLC38A10", "TMEM259", "ENSGALG00010027276", "PIK3C2B", "SLC16A1"],
                                ["SLC3A1", "ENSGALG00010005008", "PEPD", "MKLN1", "HIBADH", "IDH1"],
                                ["ENSGALG00010028674", "ENSGALG00010026566", "VPS13C", "MDM4", "SERINC3", "UBXN7"],
                                ["SLC22A5", "ACACB", "XDH", "ENSGALG00010026601", "RNF145", "MIB2"],
                                ["BLVRA", "SCAMP1", "TMEM140", "STK17A", "FIG4", "LRRC70"],
                                ["CIDEA", "PABIR3", "CEPT1", "TDRD7", "DTNBP1", "TM2D1"],
                                ["SLC7A6OS", "TRUB1", "REXO2", "OSER1", "CFAP20", "VCL"],
                                ["LRP5", "ZER1", "ABTB1", "ENSGALG00010014429", "DDHD1", "SLC22A23"],
                                ["SPINK5", "ATP6V0A1", "SERHL", "GSTA4", "TADA1", "NIPSNAP1"],
                                ["CMTR1", "ZNFX1", "MYD88", "DTX3L", "SMCHD1", "EPSTI1"],
                                ["ALKBH5", "TMEM184B", "TMEM39A", "STT3A", "ARCN1", "CNNM4"],
                                ["GTDC1", "ATP6AP1", "WARS", "SERPINE2", "TMEM144", "TMED11"],
                                ["UMPS", "LDHB", "ENSGALG00010017814", "ALAS1", "MLYCD", "RGN"],
                                ["RAB3GAP2", "GOLGA4", "GOPC", "ENSGALG00010024800", "TNKS2", "PPP4R1"],
                                ["CAPN1", "ENSGALG00010000346", "ZNF362", "TET3", "ENSGALG00010003937", "DHX34"],
                                ["NABP1", "TICRR", "SAAL1", "KIF24", "LBR", "IPO9"],
                                ["G3BP1", "SEC22B", "IMMT", "EIF2B5", "ABCF2", "PGK2"],
                                ["UBE3A", "ENSGALG00010023547", "VGLL4", "CHDH", "FBXL5", "RPS6KB1"],
                                ["COPB2", "KIF1BP", "MAGT1", "API5", "SKIV2L2", "UBA6"],
                                ["BMP6", "EML1", "CREBRF", "TRIM23", "LRATD2", "ENSGALG00010008298"],
                                ["CHCHD2", "APH1A", "CHCHD10", "AMT", "NDUFA13", "NDUFS2"],
                                ["MRPS33", "MPHOSPH8", "ENSGALG00010018635", "UBE2G2", "BTF3", "MTIF3"],
                                ["ENSGALG00010015325", "ABCD3", "ENSGALG00010026296", "DENND6A", "ABHD4", "RAB9A"],
                                ["RELN", "ENSGALG00010029265", "GTF2I", "ALS2CL", "ENSGALG00010023446",
                                 "ENSGALG00010026223"],
                                ["ENSGALG00010026907", "ACBD4", "SPRYD3", "MFSD5", "SFT2D3", "B4GALT2"],
                                ["TBX2", "NPRL3", "CDHR2", "TBX3", "PCDHGC3", "PGGHG"],
                                ["AAAS", "JUND", "IMP4", "CTU2", "NSUN4", "ULK3"],
                                ["WDR61", "ALDH1A1", "LTA4H", "NDUFA9", "KIFAP3", "SEPTIN2L"],
                                ["TIMP2", "RUSC1", "ENSGALG00010028188", "TIMM13", "LAMTOR2", "PEX19"],
                                ["ENSGALG00010026628", "RFFL", "CYP3A5", "HNRNPD", "SAA", "CYTH4"],
                                ["ITSN1", "CEP120", "ENSGALG00010022810", "CDK5RAP2", "MAP3K1", "FAM126A"],
                                ["SLC43A2", "ENSGALG00010014553", "ENSGALG00010026725", "FAM110C", "HID1", "FNDC3A"],
                                ["SLC25A24", "TUBB6", "LIMS1", "MYEF2", "C21H1orf159", "BBS7"],
                                ["MFSD9", "GID8", "GTF2H1", "OLFM3", "TMEM181", "RAD23B"],
                                ["RFX3", "BCR", "RAPH1", "ENSGALG00010026830", "GARRE1", "TJP1"],
                                ["RALBP1", "TMEM57", "TAF5L", "TAOK3", "NR0B2", "BAG4"],
                                ["KDM4B", "ZFYVE26", "ENSGALG00010018886", "FRMD1", "ENSGALG00010001436",
                                 "ENSGALG00010018696"],
                                ["CD74", "ENSGALG00010028194", "ANXA6", "ENSGALG00010017601", "IGSF1", "HEXA"],
                                ["SLC39A8", "FGFR1OP2", "CUL3", "MKKS", "TMEM19", "STX12"],
                                ["ZSWIM8", "CEP170B", "ZNF618", "ZBTB37", "HEG1", "ENSGALG00010028711"],
                                ["ERLEC1", "HPGDS", "RAB28", "TMEM165", "PNO1"],
                                ["ENSGALG00010027239", "ABR", "PLEKHA6", "VPS53", "RNF25"],
                                ["AOC3", "POFUT1", "MRPL37", "SIL1", "HTRA2"],
                                ["DLGAP5", "SLC7A7", "CENPF", "HNRNPA3", "HJURP"],
                                ["WDR1", "TAF1B", "NOP14", "PUM3", "RIOK2"],
                                ["REV3L", "ZNF608", "KLF13", "ENPP1", "SLC45A1"],
                                ["SPRY1", "GNAS", "ENSGALG00010002803", "TBL1XR1", "EXOC3"],
                                ["TCF20", "CHERP", "CREBBP", "SMG7", "ANKRD52"],
                                ["ITGB3", "GATA5", "C1orf210", "SLC25A22", "SMUG1"],
                                ["CATSPER4", "MYO7A", "BMF", "SIX4", "SLC38A6"],
                                ["RUBCNL", "GPR34", "GCNT1", "FAM45A", "ACKR4"],
                                ["RHOA", "RNF7", "RPS24", "RIDA", "THOC7"],
                                ["VPS72", "NUP88", "PLPP2", "GNAI3", "TBL2"],
                                ["ERAL1", "CDC34", "METTL7A", "ENSGALG00010029480", "PROC"],
                                ["ENSGALG00010023425", "IGF1R", "ADAM28", "ENSGALG00010012707", "TIAM1"],
                                ["SMAD6", "ENSGALG00010029351", "GCGR", "NAXE", "ELOB"],
                                ["MRPS25", "PPP1R7", "MRPL58", "YEATS4", "COMMD8"],
                                ["DGKZ", "FBXW5", "FICD", "DCTN4", "ENSGALG00010022925"],
                                ["DCBLD1", "AvBD10", "CITED4", "ENSGALG00010014558", "C11ORF52"],
                                ["TERF1", "RTEL1", "MRE11", "POLQ", "SLC37A1"],
                                ["AATF", "ENSGALG00010016891", "SFPQ", "TSEN2", "GEMIN5"],
                                ["HMOX1", "ENSGALG00010009573", "FMO4", "CDK5", "ENSGALG00010027295"],
                                ["HEPH", "L2HGDH", "ABCD2", "BPHL", "CYP46A1"],
                                ["HSPA5", "RFWD3", "ENSGALG00010012456", "ENOX2", "MYBBP1A"],
                                ["POLA2", "UCK2", "YARS2", "ENSGALG00010014704", "HSP90AB1"],
                                ["CAMLG", "PGPEP1L", "VPS13D", "OSBPL1A", "AGT"],
                                ["PHLPP1", "KCTD2", "NECAP1", "SAP130", "FOXJ3"],
                                ["G0S2", "HNF4A", "VASN", "ENSGALG00010016651", "TRIM7.1"],
                                ["ENSGALG00010024690", "FASTK", "RPUSD4", "EXOSC6", "IGSF9"],
                                ["ACO1", "ENSGALG00010006269", "PAH", "ENSGALG00010012436", "ALDH6A1"],
                                ["MGMT", "DCAF17", "RAB3IP", "ISOC1", "NXT2"],
                                ["ENSGALG00010004705", "SLC29A3", "MYO1D", "CACNB1", "KDM5B"],
                                ["POR", "DLST", "G3BP2", "ELAC2", "EIF3B"],
                                ["MFSD4B", "RASSF8", "CREB3L2", "VAT1", "ATP9A"],
                                ["PCDH7", "ARFGEF3", "ENSGALG00010009268", "RAPGEF1", "MAGI3"],
                                ["GRAMD1C", "PRPF38B", "TOP1", "PHAF1", "PNN"],
                                ["NDUFA10", "ACAA2", "PSMB7", "MRPS27", "GHITM"],
                                ["ENSGALG00010004990", "CACFD1", "SCFD2", "TOR2A", "ENSGALG00010029775"],
                                ["WHAMM", "ENSGALG00010020033", "RHBDF1", "PIAS1", "ELF1"],
                                ["RPL35", "RPLP2", "RPS13", "RPL27", "RPL12"],
                                ["GANC", "PRPF39", "SLC25A48", "BRWD3", "PI4KA"],
                                ["POLR2H", "DDTL", "UPF3B", "SNRPC", "MRPL18"],
                                ["NUP54", "AMD1", "TMEM69", "SLTM", "ACTR8"],
                                ["C10orf88", "ENSGALG00010009378", "GTPBP4", "UBAC2", "SURF6"],
                                ["SSH2", "ZNF687", "ZNF692", "SMARCC2", "CCNT1"],
                                ["TM9SF3", "GNB1", "ENSGALG00010018298", "LRRC28", "HHAT"],
                                ["STRAP", "FARS2", "PDIA4", "SDHA", "PECR"],
                                ["FAM120B", "C1H3ORF52", "CCDC93", "ENSGALG00010005012", "CCDC18"],
                                ["TFPI2", "ASB9", "CYP7A1", "EIF2S3", "LPAR6"],
                                ["SH3GL1", "ENSGALG00010001756", "MIER2", "SLC38A3", "CTNND1"],
                                ["RHOT1", "SCAF11", "TPCN2", "SEC24A", "CLCC1"],
                                ["TMEM39B", "IHH", "EML3", "PTPN9", "DDIT4"],
                                ["MICALL1", "ENSGALG00010000688", "RHOG", "ENSGALG00010022302", "PSME1"],
                                ["MCM5", "MCM3", "CDCA7", "RAD54L", "MCM2"],
                                ["ITGA2B", "NATD1", "C2orf42", "ADD2", "SAMD11"],
                                ["MOSPD1", "CTSZ", "LYPLA1", "HINT3", "EREG"],
                                ["TRPM1", "B3GNT9", "TCF12", "NAA25", "PLEKHA7"],
                                ["CTSH", "TSC22D4", "SCAMP5", "ATP5E", "PAF1"],
                                ["GNA12", "ENSGALG00010020084", "DENND5A", "HMG20A", "PPM1K"],
                                ["SHE", "ENSGALG00010000571", "ENSGALG00010027227", "RNF215", "AIP"],
                                ["TMCO4", "MT3", "DAO", "ENSGALG00010029938", "HSD11B1b"],
                                ["GFM1", "HADHA", "MRPL38", "PSMD1", "HADHB"],
                                ["RPS6KA5", "ITGA1", "PCGF3", "ZEB2", "ENSGALG00010015239"],
                                ["ENSGALG00010012179", "HIST1H101", "IL13RA2", "DNAL4", "BBS4"],
                                ["MAPKBP1", "TTC28", "FLNB", "PRRC2B", "PEAK1"],
                                ["TMCC1", "CCDC186", "EIF2AK4", "MTMR2", "MADD"],
                                ["THOC1", "FBXO5", "RCAN1", "MTFR2", "MTF2"],
                                ["EIF2B3", "ACTR6", "YWHAH", "HNRNPH3", "TUBA5"],
                                ["UTP6", "GINS3", "SRP19", "RSL1D1", "SDF2L1"],
                                ["VPS35L", "PLEK", "RUFY1", "VSIG4", "VPS41"],
                                ["RASA3", "PLAU", "SLC12A7", "FAR1", "MOSPD2"],
                                ["ARHGAP11B", "LIMA1", "PPP1R8", "CCNF", "TFDP2"],
                                ["MAML1", "ZBTB32", "GPRC5B", "DUSP16", "ZC3H12C"],
                                ["MYH11", "PDIK1L", "DACT1", "RPS6KC1", "MGEA5"],
                                ["FKBP4", "NUDCD2", "DHTKD1", "ELP2", "PRORP"],
                                ["COX7C", "MEAF6", "UQCR10", "ATP5PF", "H1F0"],
                                ["TMEM222", "IER5", "ENSGALG00010023487", "ENSGALG00010026434", "CORO1B"],
                                ["ENSGALG00010015468", "ENSGALG00010015603", "WHSC1L1", "NARF", "NELFA"],
                                ["SULF2", "ENSGALG00010025824", "PTPN21", "CGNL1", "SLC22A15"],
                                ["TRIP11", "MKRN2", "PLS3", "PDZD8", "DLG5"],
                                ["HMG20B", "SYNGR2", "NSUN5", "EXOSC1", "MFSD12"],
                                ["AIF1L", "ARHGAP30", "IFI30", "ZNF710", "CYTH1"],
                                ["TMEM132A", "DES", "LOXL3", "FAM43A", "TKFC"],
                                ["ENSGALG00010000635", "RBM19", "FZD3", "GLCE", "NEK9"],
                                ["TMC6", "MED16", "SCAP", "BRPF1", "XYLT2"],
                                ["SEC24C", "NRDC", "ENSGALG00010020454", "ANKLE2", "RTCB"],
                                ["PIK3CD", "DHX57", "NUP188", "RBM47", "RAPGEF6"],
                                ["TMEM161B", "UBR2", "DCUN1D3", "DMXL1", "SPOPL"],
                                ["CRIPT", "CRNKL1", "ENSGALG00010000812", "ADSS2", "GRK4"],
                                ["GATC", "BORCS7", "MED20", "CUTC", "ARHGEF16"],
                                ["SERPINB6", "ATP6V1C1", "CPE", "ASAH1", "C4BPM"],
                                ["NOLC1", "STAG1", "QSER1", "TPR", "ZFYVE9"],
                                ["SNAP23", "PRMT9", "MIOS", "RBM26", "MSH3"],
                                ["ARHGAP42", "INO80C", "ORC1", "BTAF1", "LEO1"],
                                ["FAM107A", "GIPC1", "ZNF341", "CBLL1", "GMEB1"],
                                ["UFD1L", "UEVLD", "SDHD", "MRPL23", "UBE2E3"],
                                ["PTP4A2", "SERP1", "HAGH", "VAMP4", "WBP1L"],
                                ["PPARA", "CMTR2", "ENSGALG00010023042", "TRIP12", "LRRC8C"],
                                ["FOXO4", "WDR81", "PDPR", "PGAP6", "UPF1"],
                                ["PITPNM2", "ADAMTS9", "UNK", "ZBTB44", "AKAP13"],
                                ["MCUR1", "EIF6", "LAP3", "LIPT1", "RPA3"],
                                ["ENSGALG00010012093", "SREBF2", "TRAF7", "TNFRSF21", "KANSL3"],
                                ["DCAF7", "NR2C2", "PPFIA1", "SLC38A9", "KLHL9"],
                                ["UHMK1", "NEIL1", "UQCRQ", "BRCC3", "NDUFA6"],
                                ["TLE4", "LURAP1L", "RNF5", "ENSGALG00010017980", "PRPSAP1"],
                                ["SAPCD2", "SRSF1", "IQGAP3", "IPP", "PRC1"],
                                ["ENSGALG00010023304", "ACP5", "APLNR", "LRRC3C", "ENSGALG00010008013"],
                                ["MARS2", "SEC16B", "ENSGALG00010028060", "FOXRED1", "FLAD1"],
                                ["TBC1D24", "CDK13", "NF1", "ABCA1", "SNX18"],
                                ["SPDL1", "ORC4", "COPS8", "GTF2H3", "TMX4"],
                                ["PTTG1IP", "SGSH", "ENSGALG00010029491", "UBALD1", "SNX33"],
                                ["FASTKD5", "MTOR", "ELP1", "AP1G1", "PHLPP2"],
                                ["PAM16", "COX5B", "VPS37C", "UBTD1", "ENSGALG00010019690"],
                                ["ENSGALG00010006038", "ENSGALG00010000134", "ELOF1", "RRS1", "PRMT5"],
                                ["TAMM41", "MED31", "SELENOF", "MAP2K4", "LRPAP1"],
                                ["ASB1", "UGP2", "ENSGALG00010026909", "ENSGALG00010016177", "ENSGALG00010001640"],
                                ["PHYH", "ENSGALG00010003551", "DNAJB14", "DDX41", "THOP1"],
                                ["NUDT19", "AKR1A1", "SGTA", "PPP1CC", "VMP1"],
                                ["CALCRL", "SESN3", "IQGAP3", "ASAP1", "TBC1D2B"],
                                ["CEP104", "PPP3R1", "PPP2R5C", "EAF1", "RGS12"],
                                ["FBXO4", "ENSGALG00010012893", "RAD1", "COMMD7", "ENSGALG00010012899"],
                                ["COL4A2", "SDK2", "ENSGALG00010014980", "ADAMTS7", "RGS5"],
                                ["SMIM20", "ENSGALG00010003606", "COX6C", "DNAJC19", "RPL26L1"],
                                ["CHD2", "USP22", "RIT1", "PHF12", "MORC1"],
                                ["SRFBP1", "PRELID3B", "PCID2", "MPHOSPH10", "DYNLT3"],
                                ["AFF2", "STXBP1", "SEC31B", "BCL9", "ENSGALG00010018616"],
                                ["DTD1", "RER1", "MRPL33", "UBXN4", "GNG5"],
                                ["NRXN1", "TTC8", "BMP10", "THBS1", "ALDH1A3"],
                                ["DFFA", "ENSGALG00010016041", "VTI1B", "ENSGALG00010026900", "SMAP1"],
                                ["ALG10", "DNAJC25", "CCDC82", "VTA1", "NUDT7"],
                                ["PTGR3", "DECR1", "TXNDC12", "MRPS6", "GATD3AL1"],
                                ["TMEM201", "ZNF516", "SVEP1", "THBS2", "MTHFD1L"],
                                ["TMCO1", "ACAT1", "RDH10", "SUCLG1", "SULT"],
                                ["BLB1", "HRASLS", "SMIM4", "FAM110D", "GJA4"],
                                ["OSGIN1", "DDX21", "FERMT1", "RBL1", "HSPA8"],
                                ["PTPRK", "LANCL1", "WDR33", "ADAM17", "GMPS"],
                                ["PNPLA2", "RNF19A", "SLC22A4", "MASP2", "PDE8A"],
                                ["TENT2", "CLK4", "RNFT1", "ZCCHC10", "NR2C1"],
                                ["NCOA3", "ENSGALG00010014907", "RBMXL1", "ENSGALG00010023327", "MAPK8"],
                                ["TMEM154", "QPCT", "FAM83H", "NRSN1", "RAB5A"],
                                ["ANK3", "PPL", "TNC", "COL6A3", "ENSGALG00010026320"],
                                ["CRK", "REV1", "U2SURP", "RCAN3", "MAPKAPK5"],
                                ["SSNA1", "DNAJC15", "SHFM1", "CWF19L2", "GTF3A"],
                                ["KLHL22", "PEX13", "SGMS1", "NRAS", "TMEM41B"],
                                ["SYNE2", "ADAM9", "ZBTB5", "ZRANB1", "GPC4"],
                                ["CD14", "MYO1F", "TGM2", "MPEG1", "BEAN1"],
                                ["SPARC", "CPTP", "SQSTM1", "ENSGALG00010026686", "COL5A1"],
                                ["UBE2J2", "ACSM5", "MAPK4", "PARD6B", "CARNMT1"],
                                ["CHCHD3", "SLC18B1", "PSMB2", "GTPBP10", "PSMD14"],
                                ["VMA21", "TMBIM4", "PDCD6", "B3GLCT", "HPRT1"],
                                ["RAB11FIP5", "FOXK1", "RUSC2", "SEMA6D", "ETS1"],
                                ["CHD4", "KIAA1671", "IGF2BP2", "ENSGALG00010023460", "HIPK2"],
                                ["AGMAT", "CIDEC", "PAFAH2", "FAHD1", "RPLP0"],
                                ["ZNF384", "ADGRL2", "ANTXR2", "RANBP10", "ENSGALG00010022715"],
                                ["NXN", "UBTD2", "ENSGALG00010026948", "GSK3A", "SOX9"],
                                ["H3F3C", "NAA20", "ENSGALG00010006785", "RBM34", "ZFYVE21"],
                                ["NENF", "PDCD5", "EIF4E3", "RAP1A", "UBE2I"],
                                ["EIF3K", "COX6A1", "ENSGALG00010010869", "RPL19", "ATP5I"],
                                ["ACTR5", "VWA9", "DDX10", "HEATR3", "POLR3B"],
                                ["CHTF18", "PSMD10", "AIFM1", "SRSF7L", "ENSGALG00010018401"],
                                ["IL1RL1", "SMOC2", "IGFBP3", "GAS6", "KCNK4"],
                                ["ZBTB10", "MYO1E", "INPP5E", "REPS2", "COBL"],
                                ["SEPHS3", "MTMR3", "INPPL1", "ENSGALG00010000306", "SF3A1"],
                                ["DNAJC11", "AMPH", "GLE1", "THAP12", "ROBO1"],
                                ["TOLLIP", "NIPAL3", "ZDHHC17", "USP33", "GPATCH1"],
                                ["NFS1", "SLC4A1AP", "PCCB", "ASS1", "SLC25A12"],
                                ["CBS", "CYP7B1", "SLC16A10", "SH3RF1", "MOCOS"],
                                ["CEBPA", "ENSGALG00010028738", "BMI1", "UBTF", "PBX1"],
                                ["NAT8B", "TTC36", "PITHD1", "RNF166", "NAPRT"],
                                ["VANGL1", "RBM33", "HIPK1", "HECTD4", "DMAP1"],
                                ["SRSF6", "ZC3HAV1L", "MCEE", "GPR1", "PLPPR5"],
                                ["ENSGALG00010010901", "CCDC71L", "DEDD", "CCND3", "TBC1D22B"],
                                ["DAPK3", "RARG", "ENSGALG00010024784", "TNKS1BP1", "BAZ2A"],
                                ["SZT2", "MCM3AP", "DEPDC5", "VPS8", "KDM4A"], ["ERI1", "TFDP1", "SMN", "UXS1", "DCTD"],
                                ["UBR1", "DGCR8", "ZCCHC24", "MRTFB", "MARF1"],
                                ["RPUSD3", "TYSND1", "TAF10", "RNPEP", "ENSGALG00010026195"],
                                ["HIST1H2A4L1", "TIMM10", "ADO", "WDR55", "SMIM19"],
                                ["ENSGALG00010003570", "ENSGALG00010003538", "ENSGALG00010007082", "ENSGALG00010007339",
                                 "SEMA6B"],
                                ["CCL19", "ENSGALG00010023972", "ENSGALG00010027309", "ENSGALG00010023981", "IFI35"],
                                ["NPLOC4", "WDR18", "RNF26", "STRIP1", "PCSK7"],
                                ["UBE3B", "CLASP1", "NTSR1", "GCN1", "RNF216"],
                                ["WBP2NL", "TOR4A", "SLC11A1", "NCKIPSD", "FKBP15"],
                                ["SMYD4", "ING5", "CABLES1", "ENSGALG00010028453", "SERPINF2"],
                                ["FAAP100", "ANAPC2", "ENSGALG00010025899", "CKLF", "NLRP3"],
                                ["UTP18", "ERLIN1", "DNAAF5", "CRMP1", "NUP93"],
                                ["ENSGALG00010029884", "KIF12", "ZNHIT3", "SLC39A11", "RASA4B"]]

            cluster_data_0_4 = [["ENSGALG00010003614", "ENSGALG00010003644", "ENSGALG00010003584", "ENSGALG00010003635",
                                 "ENSGALG00010003575", "ENSGALG00010003643", "ENSGALG00010003613", "ENSGALG00010003623",
                                 "ENSGALG00010003598", "ENSGALG00010003640"],
                                ["ENSGALG00010003557", "ENSGALG00010003565", "ENSGALG00010003537", "ENSGALG00010003563",
                                 "ENSGALG00010003529", "ENSGALG00010003576"],
                                ["ND4", "COX3", "ND2", "CYTB", "ATP6", "ND1"],
                                ["MCM5", "MCM3", "CDCA7", "RAD54L", "MCM2"]]

            for cluster in cluster_data_0_4:
                if selected_bacteria in cluster:
                    found = True
                    cluster_found = cluster
                    threshold = "0.4"
                    break
            if not found:
                for cluster in cluster_data_0_3:
                    if selected_bacteria in cluster:
                        found = True
                        cluster_found = cluster
                        threshold = "0.3"
                        break
            if not found:
                for cluster in cluster_data_0_2:
                    if selected_bacteria in cluster:
                        found = True
                        cluster_found = cluster
                        threshold = "0.2"
                        break
            if found:
                cleaned_cluster = [s.replace("s__", "") for s in cluster_found]
                return JsonResponse({
                    "found": True,
                    "threshold": threshold,
                    "cluster_members": cleaned_cluster,
                })
            else:
                return JsonResponse({"found": False})


        # ----- Common filters (only for branches that need tissue) -----
        # Common filters
        tissue = request.GET.get('tissue')
        if tissue is None:
            return J({'error': 'Missing tissue.'}, status=400)
        # base_tissue_q = Q(from_tissue=tissue) | Q(to_tissue=tissue)
        # here tissue is muscle to adapat for each case
        base_tissue_q = Q(from_tissue='liver') & Q(to_tissue=tissue)

        # (B) Single-var filtering
        if ('multi_variable' not in request.GET
                and 'table_filter' not in request.GET
                and 'cluster_lookup' not in request.GET
                and 'explore_table_filter' not in request.GET
                and 'explore_distribution' not in request.GET):
            var = request.GET.get('variable')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = LiverCorrelation.objects.filter(
                base_tissue_q,
                var2=var,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({'results': [], 'total_count': 0})
            top = filt.order_by('-correlation')[:100]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count})

        # (C) Multi-var filtering
        if 'multi_variable' in request.GET:
            variables = request.GET.getlist('variables[]')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = LiverCorrelation.objects.filter(
                base_tissue_q,
                var2__in=variables,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({'results': [], 'total_count': 0})
            top = filt.order_by('-correlation')[:100]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count})



        # (E) Table Filtering
        if 'table_filter' in request.GET:
            var = request.GET.get('variable')
            try:
                corr_min = float(request.GET.get('correlation_min', -1))
                corr_max = float(request.GET.get('correlation_max', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = LiverCorrelation.objects.filter(
                base_tissue_q,
                var2=var,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            if total_count == 0:
                return J({
                    'results': [],
                    'total_count': 0,
                    'overview': {'median': None, 'q1': None, 'q3': None}
                })
            top = filt.order_by('-correlation')[:200]

            results = []
            vals = [o.correlation for o in filt]
            overview = {
                'median': r3(np.median(vals)),
                'q1': r3(np.quantile(vals, 0.25)),
                'q3': r3(np.quantile(vals, 0.75)),
            }
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'Coefficient': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            return J({'results': results, 'total_count': total_count, 'overview': overview})

        # (F) Explore distribution
        if 'explore_distribution' in request.GET:
            # qs = LiverCorrelation.objects.filter(base_tissue_q).values_list('correlation', flat=True)
            qs = (LiverCorrelation.objects
                  .filter(base_tissue_q, correlation__isnull=False)
                  .values_list('correlation', flat=True)
                  )
            series = list(qs)
            if not series:
                return J({'error': 'No data found.'}, status=400)
            stats = {
                'min': r3(min(series)),
                'q1': r3(np.quantile(series, 0.25)),
                'median': r3(np.median(series)),
                'q3': r3(np.quantile(series, 0.75)),
                'max': r3(max(series)),
            }
            return J({'distribution': {'correlation_values': series, 'stats': stats}})

        # (G) Explore table filter
        if 'explore_table_filter' in request.GET:
            try:
                corr_min = float(request.GET.get('corrMin', -1))
                corr_max = float(request.GET.get('corrMax', 1))
                acc_min = float(request.GET.get('accuracy', 0))
            except:
                return J({'error': 'Invalid numeric parameters.'}, status=400)
            if corr_min > corr_max:
                return J({'error': 'Min correlation cannot exceed max correlation.'}, status=400)

            filt = LiverCorrelation.objects.filter(
                base_tissue_q,
                correlation__gte=corr_min,
                correlation__lte=corr_max,
                accuracy__gte=acc_min
            )
            total_count = filt.count()
            top = filt.order_by('-correlation')[:200]

            results = []
            for obj in top:
                results.append({
                    'var1': obj.var1,
                    'var2': obj.var2,
                    'correlation': r3(obj.correlation),
                    'min_val': r3(obj.min),
                    'max_val': r3(obj.max),
                    'accuracy': r3(obj.accuracy),
                    'pvalue': r3(getattr(obj, 'pvalue', None)),
                })
            vals = [o.correlation for o in filt]
            overview = {
                'median': r3(np.median(vals)) if vals else None,
                'q1': r3(np.quantile(vals, 0.25)) if vals else None,
                'q3': r3(np.quantile(vals, 0.75)) if vals else None,
            }
            return J({'results': results, 'total_count': total_count, 'overview': overview})

        return J({'error': 'No recognized AJAX action.'}, status=400)

    # --- Non-AJAX: Build sunbursts and context ---
    def clusters_to_df(data):
        rows = []
        for i, sublist in enumerate(data, start=1):
            cluster_name = f"Cluster {i}"
            for species in sublist:
                rows.append({"Cluster": cluster_name, "Species": species.replace("s__", ""), "Value": 1})
        return pd.DataFrame(rows)

    cluster_data_0_3 = [["ENSGALG00010003557", "ENSGALG00010003644", "ENSGALG00010003584", "ENSGALG00010003635",
                         "ENSGALG00010003643", "ENSGALG00010003537", "ENSGALG00010003598", "ENSGALG00010003640",
                         "ENSGALG00010003576", "ENSGALG00010003565", "ENSGALG00010003614", "ENSGALG00010003563",
                         "ENSGALG00010003575", "ENSGALG00010003613", "ENSGALG00010003623",
                         "ENSGALG00010003529"], ["KIAA1524", "GEN1", "ATAD2", "CKAP5", "POLA1", "KIAA1328"],
                        ["ND4", "COX3", "ND2", "CYTB", "ATP6", "ND1"],
                        ["RCHY1", "ACBD6", "BLCAP", "LSM12", "MAD2L2", "KXD1"],
                        ["LRP5", "ZER1", "ABTB1", "ENSGALG00010014429", "DDHD1", "SLC22A23"],
                        ["P3H2", "ENSGALG00010022050", "ENSGALG00010017585", "TRMT2B", "AEBP1"],
                        ["AGO4", "NCOA6", "ZW10", "AGO1", "TAB3"],
                        ["WWC3", "SLC2A13", "AFDN", "KLF12", "USP53"],
                        ["HIF1AN", "CYP3A4", "ENSGALG00010003152", "ENSGALG00010025339", "MTFR1"],
                        ["CAPN15", "NOS3", "ENSGALG00010016848", "ENSGALG00010027348", "HIC1"],
                        ["ELAPOR2", "PDE5A", "VIPR2", "GFRA1", "SOX6"],
                        ["MCM5", "MCM3", "CDCA7", "RAD54L", "MCM2"],
                        ["SHE", "ENSGALG00010000571", "ENSGALG00010027227", "RNF215", "AIP"],
                        ["ENSGALG00010018015", "LMCD1", "STK11", "SLC4A1", "IGFBP2"],
                        ["SERPINB6", "ATP6V1C1", "CPE", "ASAH1", "C4BPM"],
                        ["FOXO4", "WDR81", "PDPR", "PGAP6", "UPF1"],
                        ["SPDL1", "ORC4", "COPS8", "GTF2H3", "TMX4"],
                        ["FAM162A", "DNAJC9", "MRPL20", "TMEM126A", "SSR1"],
                        ["MIPEP", "DPH6", "DARS", "K123", "ENSGALG00010006275"],
                        ["ENSGALG00010029171", "KAT2A", "PPRC1", "SMARCC1", "KANK4"],
                        ["ANK3", "PPL", "TNC", "COL6A3", "ENSGALG00010026320"],
                        ["ACTR5", "VWA9", "DDX10", "HEATR3", "POLR3B"],
                        ["TRIM28", "OGDH", "ARHGEF10L", "ATP13A1", "ALDH9A1"],
                        ["CHTF18", "PSMD10", "AIFM1", "SRSF7L", "ENSGALG00010018401"],
                        ["TOR1AIP2", "PATL1", "ENSGALG00010000081", "DYM", "PCBP2"],
                        ["NFS1", "SLC4A1AP", "PCCB", "ASS1", "SLC25A12"],
                        ["NAT8B", "TTC36", "PITHD1", "RNF166", "NAPRT"],
                        ["ENSGALG00010010901", "CCDC71L", "DEDD", "CCND3", "TBC1D22B"],
                        ["HEATR6", "GRB2", "CRKL", "KPNA1", "RBM15"],
                        ["SMYD4", "ING5", "CABLES1", "ENSGALG00010028453", "SERPINF2"]]
    cluster_data_0_2 = [["ENSGALG00010003557", "ENSGALG00010003644", "ENSGALG00010003584", "ENSGALG00010003635",
                         "ENSGALG00010003643", "ENSGALG00010003537", "ENSGALG00010003598", "ENSGALG00010003640",
                         "ENSGALG00010003576", "ENSGALG00010003565", "ENSGALG00010003614", "ENSGALG00010003563",
                         "ENSGALG00010003575", "ENSGALG00010003613", "ENSGALG00010003623",
                         "ENSGALG00010003529"],
                        ["ENSGALG00010018015", "LMCD1", "MERTK", "VNN2", "IGFBP2", "TOB2", "EHD3", "AARS2",
                         "COL13A1", "STK11", "IDS", "CDK9", "SLC4A1", "APLP2"],
                        ["PIAS3", "ADGRG1", "ENG", "SGSM3", "STAT5A", "WLS", "HSPG2", "GPR182", "TIE1", "CD34",
                         "ARSG", "HIP1"],
                        ["CYP4B7", "ACAD11", "ATIC", "HAO2", "ACOX1", "EHHADH", "FAM110B", "AQP11", "KYNU",
                         "NCALD", "AASS", "FAXDC2"],
                        ["ENSGALG00010001804", "MBP", "NRG2", "SH3GLB2", "ENSGALG00010006728", "SPPL3", "F7",
                         "PIK3IP1", "AADAT", "ENSGALG00010000853"],
                        ["HSPD1", "ORC6", "RARS", "ZNF622", "TCP1", "ACAD9", "HSPA9", "RCL1", "PSMG1",
                         "FASTKD2"],
                        ["ENSGALG00010023758", "CTIF", "MTSS2", "CD151", "SSPN", "SUFU", "TEAD3", "DENND6B",
                         "DNAJB5", "UBE2D2"],
                        ["FAM214A", "TRAK1", "CAPN5", "ENSGALG00010026220", "RAB43", "PAM", "ITIH2", "SORBS1",
                         "PROS1", "ENSGALG00010004860"],
                        ["KIAA1524", "ATAD2", "CKAP5", "POLA1", "KIAA1328", "MSH6", "GEN1", "MMS22L", "CIT",
                         "DNA2"],
                        ["ELAPOR2", "OSBPL5", "ABHD17B", "SOX6", "FBLN2", "PDE5A", "VIPR2", "IFT122", "GFRA1"],
                        ["MARK1", "ESRRG", "RCSD1", "NR3C2", "USP44", "KCNK7", "ENSGALG00010026760",
                         "ENSGALG00010015643", "NAT"],
                        ["CDCA7L", "VASH2", "ENSGALG00010021677", "ACTL6A", "MGME1", "SEC61A2", "CDC37L1",
                         "FAM60A", "GIPC2"],
                        ["GUCD1", "CHIR-IG1-5", "SOCS4", "DPEP2", "CPXM2", "CEP70", "TCTN1", "MYLK", "TMOD2"],
                        ["UQCRC1", "CCDC25", "GOLGA7", "GLOD4", "SAMM50", "ACTR10", "ENSGALG00010010850",
                         "ACSS3", "PON1"], ["HIF1AN", "CYP3A4", "SLC16A12", "F2", "ENSGALG00010025339", "MTFR1",
                                            "ENSGALG00010003152", "APOH", "ZC3H11A"],
                        ["HEATR6", "BAZ1B", "CRKL", "KPNA1", "GTF3C1", "RBM15", "DOT1L", "GRB2", "AP2B1"],
                        ["ENSGALG00010015356", "ENSGALG00010029333", "RFXAP", "DNAJC2", "UPRT", "DRG2", "NUTF2",
                         "MRPL40", "FAM192A"],
                        ["TOR1AIP2", "ENSGALG00010000081", "SP2", "PATL1", "FBXO42", "SCAMP4", "DYM", "PCBP2",
                         "SP1"], ["CHMP2A", "FAM222A", "DIS3L2", "FZR1", "NR1D1", "PABPC4", "DENND2B",
                                  "ENSGALG00010017752", "HOMER2"],
                        ["ERH", "THYN1", "MRPL47", "MRPL3", "SNRPE", "METTL5", "KNSTRN", "CNIH1", "BIRC5"],
                        ["TRIM28", "OGDH", "SLC17A9", "CREB3", "ENSGALG00010013472", "VPS45", "ARHGEF10L",
                         "ATP13A1", "ALDH9A1"],
                        ["NIBAN2", "FHIP1B", "COLGALT1", "ESYT1", "FZD8", "RIPOR1", "SLC4A2", "HYAL2",
                         "ENSGALG00010004099"],
                        ["EP300", "AGO4", "PLAGL2", "MBD5", "AGO1", "TAB3", "ZW10", "NCOA6", "ANKRD17"],
                        ["AQP3", "GRTP1", "ELK3", "HEXB", "HAVCR1", "TMEM230", "TMEM268", "ATP6V1B2", "COG7"],
                        ["CDCA9", "NOCT", "ENSGALG00010021950", "ENSGALG00010023748", "SESN1", "COQ10B",
                         "KIAA1191", "FOXP1"],
                        ["ST7", "IBA57", "SEC23B", "ADPRHL2", "OSGEPL1", "LACTB", "THUMPD1", "PBX3"],
                        ["ATXN10", "SH3BGRL", "K123", "IFT52", "ENSGALG00010006275", "DARS", "DPH6", "MIPEP"],
                        ["SDK1", "PTGFRN", "TTL", "EPHB2", "ENSGALG00010025742", "TFCP2L1", "SPRY3", "DIP2C"],
                        ["RAB40B", "SIRT3", "ATP1B1", "NIPSNAP3A", "DERL3", "SOD3", "SUCNR1", "YY2"],
                        ["EEA1", "OSBPL8", "LMBRD2", "SCYL2", "PDPK1", "PIK3CA", "CDYL2", "NBEAL1"],
                        ["MRPL22", "RAD18", "SSR1", "HMGN5", "FAM162A", "DNAJC9", "MRPL20", "TMEM126A"],
                        ["ENSGALG00010028052", "ADAMTSL2", "SEPTIN5", "ATG13", "ATP2B2", "MATCAP2", "TCF3",
                         "MVB12B"], ["STAB1", "NRP2", "ADORA2B", "KDR", "ARHGEF18", "SH3BP5", "GATA4",
                                     "ENSGALG00010015149"],
                        ["MIB1", "STAM", "HEATR1", "UBR5", "USP9Y", "AQR", "CLASP2", "XPO4"],
                        ["CBFB", "FRRS1L", "PCOLCE2", "ATF3", "RHOQ", "ENSGALG00010024764", "NSMF", "EAF2"],
                        ["PKNOX2", "FZD9", "PGM1", "CUEDC1", "SESN2", "RBFOX2", "NFE2L1", "GPR162"],
                        ["CAV1", "COLEC11", "BMP5", "FAM175A", "SPERT", "UBE2J1", "NCOA7", "RPGR"],
                        ["GLG1", "CDH1", "POMGNT1", "PIP5K1C", "SORL1", "POLDIP2", "CACNA2D2", "D2HGDH"],
                        ["ENDOV", "ENSGALG00010014319", "RPL38", "CLEC3B", "DPH3P1", "TOMM7", "CBX8",
                         "ENSGALG00010026873"],
                        ["ENSGALG00010029857", "REXO1", "ANKRD11", "ORAI3", "SIRT4", "NUFIP2",
                         "ENSGALG00010025137", "CLK2"],
                        ["ENSGALG00010022050", "TRMT2B", "FHOD1", "AEBP1", "COL16A1", "P3H2", "CLCN7",
                         "ENSGALG00010017585"],
                        ["GXYLT1", "MSL3", "LYVE1", "CASP18", "VCAM1", "NSMAF", "RNMT", "ORC3"],
                        ["G6PC1", "ENSGALG00010016599", "KLHL26", "SLC20A1", "PIGQ", "OAT", "SMOX", "BHLHE40"],
                        ["WNK1", "EDEM3", "POMT2", "PIGO", "BCL2L13", "DENND5B", "LEMD3", "MIEF1"],
                        ["RTKN", "ENSGALG00010027348", "ENSGALG00010003882", "CAPN15", "NOS3",
                         "ENSGALG00010016848", "TPP1", "HIC1"],
                        ["SFT2D2", "HSPA4L", "VKORC1L1", "GK5", "PITRM1", "GPS1", "USP47", "LARS1"],
                        ["SHANK3", "AATK", "MAF1", "ACTN4", "MAN2C1", "USP19", "PLEKHM1", "SLC25A1"],
                        ["JOSD1", "TNRC18", "ENSGALG00010000148", "ENSGALG00010008352", "FOXA1", "DAZAP2",
                         "ZC3H4", "LCOR"],
                        ["TOGARAM1", "DHX33", "CYP1A1", "DVL3", "PI4KB", "POLR1B", "TRIM9", "GLIS2"],
                        ["WDR3", "GNB1L", "NKRF", "SNX3", "PRPF40A", "TBL3", "DDX51"],
                        ["PRCP", "LMBRD1", "LY86", "ZFAND1", "SLC15A4", "SUGCT", "PFKP"],
                        ["GLRX5", "UTP11", "NDUFAF1", "TMEM14A", "PRDX1", "CACYBP", "NDUFA4"],
                        ["RAPGEF3", "MT4", "ENSGALG00010003777", "BCAR1", "PYURF", "SIDT2", "SLC46A1"],
                        ["SUCLG2", "ERI2", "TRIM24", "MELK", "ECT2", "NUSAP1", "TANGO2"],
                        ["CYP2AC2", "ENSGALG00010018176", "ATL2", "SLC17A5", "FBLN1", "ACADSB", "GART"],
                        ["ENSGALG00010028419", "ENSGALG00010021256", "OASL", "DHX58", "IFITM5",
                         "ENSGALG00010021272", "ENSGALG00010026316"],
                        ["ENSGALG00010020720", "MRAS", "ENSGALG00010009796", "SLC25A17", "CDKN2A", "SNRPGP15",
                         "ENSGALG00010028085"],
                        ["TNS3", "WWC3", "TMEM245", "SLC2A13", "AFDN", "KLF12", "USP53"],
                        ["TUSC2", "SLC25A39", "CCT3", "PIP5K1A", "OTUB1", "CPSF1", "NUDCD3"],
                        ["BIN2", "RNF19B", "GBP", "C1QC", "ENSGALG00010028467", "C1QA", "BF1"],
                        ["DAP3", "SELENOK", "MAPRE1", "SPOUT1", "MYL6", "MRPS11", "HTD2"],
                        ["LOX", "ADAMTS12", "PXDN", "UGT8", "ANKRD50", "IQSEC1", "ENSGALG00010013071"],
                        ["ANP32E", "USP34", "C2CD5", "FNBP1L", "EML4", "IPO7", "PRKCZ"],
                        ["PLA2G4A", "MARCH1", "CD44", "CYBB", "TBXAS1", "CYSLTR2", "IKZF1"],
                        ["AHR1A", "MLH3", "MIGA1", "SOCS6", "ZBTB21", "ARHGAP5", "UBE3C"],
                        ["ABCC3", "ENSGALG00010022879", "LPCAT1", "ADA", "VWF", "MMRN2", "TNFRSF1A"],
                        ["CALR", "AXIN1", "ENSGALG00010024051", "CRPL2", "SNX27", "MFAP1", "HM13"],
                        ["PHAX", "FAM122B", "RAE1", "APIP", "TOPORS", "ZNF644", "ENSGALG00010014398"],
                        ["LLGL1", "ATL1", "ZBTB39", "RAVER1", "DCAF15", "MECP2", "TMEM186"],
                        ["SMARCAD1", "EIF4G2", "MSH2", "METTL14", "NUP37", "FGFR1OP", "KIF23"],
                        ["OPTN", "TBP", "RHOG2", "HMGA2", "ZBTB18", "ENSGALG00010005682", "SLC25A30"],
                        ["INTS12", "ENSGALG00010020074", "DUSP14", "CHAMP1", "ATF4", "ZFP36L1", "WIPI2"],
                        ["RAB18", "MOCS2", "TMEM38B", "ENSGALG00010016834", "HDAC11", "MYL12B", "RAB2A"],
                        ["SF3B4", "WIPF2", "ARRDC1", "YTHDF2", "CPSF7", "USF1", "FBXL14"],
                        ["TTC37", "MON2", "SEPTIN6", "NCBP1", "RELCH", "CCP110", "SYNE3"],
                        ["ENSGALG00010002750", "MASTL", "ZNF385D", "EZR", "PLK4", "ENSGALG00010000911",
                         "PTDSS1"],
                        ["ENSGALG00010004592", "ENSGALG00010027015", "DNM1", "KLB", "NANS", "TOM1L2", "COL3A1"],
                        ["ENSGALG00010029171", "KAT2A", "PPRC1", "PLEKHG3", "SMARCC1", "ENSGALG00010004962",
                         "KANK4"], ["ASXL2", "DOCK5", "ZC3H3", "ENSGALG00010017349", "LPP", "CYFIP2", "CD248"],
                        ["DNAJA1", "PRPF3", "TPRA1", "ENSGALG00010027306", "CERS5", "B4GALT4", "ATRIP"],
                        ["KIF2A", "UBLCP1", "CWC27", "TMEM192", "DTWD2", "LCORL", "UBE2N"],
                        ["RAC2", "LGALS3", "MAX", "ART7B", "CD48", "FCER1G", "ARHGDIB"],
                        ["EIF2D", "TBL1X", "TPRG1L", "KLHL14", "ADI1", "GPD1L2", "AGFG1"],
                        ["HERPUD2", "BTF3L4", "ENSGALG00010018371", "LGMN", "SDF4", "ADAL", "RCN2"],
                        ["HIKESHI", "AP3S1", "RNF146", "RMDN1", "CLDND1", "RPL34", "IMPACT"],
                        ["ITPKA", "HMGCS1", "CYLD", "PDK4", "GABARAPL1", "LRP12", "DAPK2"],
                        ["PODXL", "NEK8", "DGKD", "NOTCH1", "ATP2B4", "INO80D", "SIN3B"],
                        ["TMEM109", "PSMD4", "PEX11G", "MUL1", "SCAMP2", "TCN2", "IL6R"],
                        ["H2AFZ", "NIFK", "PSMB3", "TPI1", "HP1BP3", "CENPH", "AHSA1"],
                        ["LAPTM4A", "LIPA", "ABHD18", "TNFAIP8", "RTFDC1", "TANK", "ITM2A"],
                        ["LIX1L", "ARID3A", "TMEM184A", "ZSWIM5", "KANK3", "MLXIPL", "CDC42EP1"],
                        ["ADCK2", "VDAC2", "PMPCB", "ORAOV1", "MOCS3", "UCHL5", "ENSGALG00010025161"],
                        ["FOXM1", "SHCBP1", "INCENP", "KNTC1", "MANSC1", "ANLN", "KIF18A"],
                        ["ARPC1B", "IL2RG", "CDK5RAP1", "CNN2", "DMB2", "SLC2A6", "NRROS"],
                        ["DCP1B", "TPPP", "FST", "KCNJ8", "VAV3", "FHL1", "C5orf34"],
                        ["TBC1D13", "SLC25A42", "RNF123", "NDST1", "BLTP2", "ABCA2", "ENSGALG00010013362"],
                        ["ENSGALG00010023776", "PIGR", "PNPLA7", "DOLK", "ACOX2", "GLDC", "KMO"],
                        ["EGLN1", "CDC42EP3", "ENSGALG00010016051", "ELL2", "SREK1", "AHI1", "TRPC1"],
                        ["ASL1", "EXFABP", "TLR1B", "PSTPIP2", "HTR7", "SCPEP1", "LAPTM5"],
                        ["DDX5", "VPS18", "ERCC3", "POLG2", "IKBKB", "LRPPRC", "ARGLU1"],
                        ["ENSGALG00010018598", "PNPLA6", "C3", "EVI5L", "WDR59", "ADAMTS15", "PCASP2"],
                        ["USP54", "SPRED2", "GUCY2C", "ADPGK", "RCOR3", "B3GALT6", "OVCH2"],
                        ["NDUFB3", "ACYP2", "OAZ2", "LAMTOR3", "NDUFB5", "MIF4GD", "COX5A"],
                        ["POLL", "CTNNA1", "ABHD16A", "POGZ", "SARDH", "SLC8B1", "MID2"],
                        ["EPHB1", "IGF2BP1", "YARS", "USP5", "TBCC", "RAI1", "GTF2E1"],
                        ["SLC12A4", "ENSGALG00010024433", "PARG", "ATRNL1", "ABCC4", "BORCS5", "FAM241A"],
                        ["PAXIP1", "ENSGALG00010012244", "KBTBD2", "SART3", "PTBP1", "CAMSAP1"],
                        ["BUB3", "RABL3", "PRIM2", "AGK", "NUP107", "RALB"],
                        ["ENSGALG00010015148", "SOCS1", "RAP1GAP3", "RNF141", "NAP1L1", "SORBS2"],
                        ["KIAA1429", "KDM5A", "FBXL17", "GPATCH2L", "ANKS3", "SUPT7L"],
                        ["PLEKHM3", "DLC1", "IDUA", "ADGRF5", "KIF3A", "TET2"],
                        ["DPYD", "ERICH3", "ENSGALG00010010802", "ENSGALG00010023368", "WRN", "SCN4A"],
                        ["IL2RB", "JARID2", "KLF3", "RBM6", "PTPN6", "PTK2"],
                        ["ENSGALG00010024682", "ENSGALG00010023880", "PHPT1", "TUBA1A", "CDC6", "CDK2"],
                        ["TLR3", "IFIH1", "PARP9", "EIF2AK2", "PARP12", "ENSGALG00010022207"],
                        ["BLM", "TXNDC16", "DDX11", "CLSPN", "GPR75", "TOPBP1"],
                        ["VDHAP", "GOT2", "FMO3", "ENSGALG00010026947", "ACAA1", "GSTK1"],
                        ["DAAM2", "FAM102A", "SLC4A4", "VIPR1", "NR3C1", "ST8SIA5"],
                        ["ENSGALG00010009849", "PLAGL1", "PRRG4", "PLEKHA1", "BIRC8", "USP16"],
                        ["SOX5", "ARRB1", "TTC17", "GIGYF2", "A1CF", "MAGI1"],
                        ["DIP2A", "SNX8", "CPED1", "DENND4A", "FYCO1", "TMPPE"],
                        ["C1orf131", "DNAJC18", "BAMBI", "DHRSX", "ENSGALG00010025126", "SPRY2"],
                        ["PHF3", "USP7", "ENSGALG00010009457", "PDXDC1", "FAM199X", "CSDE1"],
                        ["PIK3R6", "GM2A", "NCF1C", "HPSE", "SMAP2", "SERPING1"],
                        ["UBE2W", "EDNRB", "CASD1", "LTBP1", "NT5E", "SGCE"],
                        ["MAP1LC3A", "UBE2Q2", "PIGH", "ENSGALG00010011742", "HIC2", "BTG1L"],
                        ["ARHGAP10", "SLC7A2", "ENSGALG00010006525", "TACC2", "EEF2K", "HSF3"],
                        ["THOC5", "ASH2L", "MOB3A", "SARNP", "AK2", "NUP62"],
                        ["ERP29", "SPP2", "AvBD9", "SGK2", "ATP5J2", "HIBCH"],
                        ["EXTL2", "UNKL", "PAN3", "WTIP", "SPATA2", "ZNF280D"],
                        ["UBE2H", "CNOT10", "WIPF3", "GPHN", "ACSL5", "NPAS2"],
                        ["ENSGALG00010007873", "ENSGALG00010027409", "ENSGALG00010014994", "RPL36", "CYB5RL",
                         "P3H3"], ["NDOR1", "MAP2K5", "HYI", "ENSGALG00010013915", "TM2D2", "STK16"],
                        ["NHLRC3", "XPO1", "UGGT2", "EPS15", "RBM12", "ENSGALG00010018857"],
                        ["ZEB1", "CAPSL", "TTN", "ANGPT1", "PLCXD1", "PLEKHF2"],
                        ["CAPZA2", "BZW2", "TMEM70", "CCNB1", "DHFR", "DCTN5"],
                        ["MRPS22", "PCNA", "RAN", "DEPDC7", "ARPC1A", "RFC2"],
                        ["JPH1", "NAA16", "TAF2", "TDG", "TAF5", "MMRN1"],
                        ["ENSGALG00010012742", "PARP1", "GPI", "WDR90", "LONP1", "NOM1"],
                        ["ADAP1", "GALK1", "SFXN2", "SLC29A1", "SCD", "CS"],
                        ["IKZF4", "KANSL1", "ZNF142", "HIP1R", "KMT2D", "ZDHHC5"],
                        ["NUP43", "NUP133", "CHEK2", "POP1", "SUCLA2", "ZDHHC13"],
                        ["GATAD2B", "SENP8", "R3HDM2", "BCL9L", "SEPTIN9", "CHST13"],
                        ["KIF11", "ATAD5", "TRIM59", "TMEM63A", "KIF15", "TTK"],
                        ["UCHL3", "DPM1", "RPF1", "TXNL4A", "BCCIP", "CRELD2"],
                        ["RPS21", "RPL30", "ENSGALG00010029344", "FAM8A1", "TTC30B", "SPINK4"],
                        ["KAZN", "PAQR3", "CUEDC2", "B4GALNT4", "SLC35E3", "GTF3C5"],
                        ["ENSGALG00010014578", "PCYT1A", "OPHN1", "SCMH1", "ENSGALG00010029524", "ASAP3"],
                        ["YOD1", "ECPAS", "ENSGALG00010025477", "TRIM32", "ZZEF1", "DDI2"],
                        ["FBXW7", "MPPED1", "LGALS2", "TRAF3IP1", "ENSGALG00010010309", "RSBN1L"],
                        ["APP", "PHOSPHO1", "WIPI1", "ARMH4", "PLPP3", "ENSGALG00010027617"],
                        ["NUP210", "ARNT2", "CHSY1", "IARS1", "USP40", "GFPT1"],
                        ["CLN5", "FUBP3", "TMPRSS2", "PCYOX1", "MXD1", "ENSGALG00010005585"],
                        ["ND4", "COX3", "ND2", "CYTB", "ATP6", "ND1"],
                        ["MRPS31", "DYL1", "EIF2S1", "COPS4", "FAM89A", "CBR4"],
                        ["BCKDHB", "ACADL", "SDHB", "PGRMC1", "MARC1", "ATP5PO"],
                        ["FGA", "MAPK8IP3", "BACH2", "ENSGALG00010002894", "ENSGALG00010017350", "GCNT4"],
                        ["KIAA0232", "BNIP2", "FGD6", "RIPOR3", "HYCC2", "SF3B1"],
                        ["TESK2", "LAMB2", "ENSGALG00010026241", "SLC7A5", "CERS1", "C8B"],
                        ["MCRIP2", "ACOT8", "PMM1", "SRXN1", "ENSGALG00010018284", "PFKFB1"],
                        ["MTHFD2", "HKDC1", "ANGPTL3", "ENSGALG00010026889", "C4orf54", "HDAC9"],
                        ["RCHY1", "ACBD6", "BLCAP", "LSM12", "MAD2L2", "KXD1"],
                        ["ENSGALG00010009129", "ABHD1", "KHK", "ENSGALG00010006055", "ENSGALG00010004046",
                         "ENSGALG00010006131"],
                        ["ENSGALG00010026293", "KRIT1", "LRIF1", "ARHGEF3", "SERAC1", "ENSGALG00010026720"],
                        ["POLD1", "WDR76", "ESCO2", "NCBP2", "LIG1", "CTPS1"],
                        ["ENSGALG00010012286", "MYH1B", "ENSGALG00010003287", "ENSGALG00010003609", "5_8S_rRNA",
                         "ENSGALG00010003258"],
                        ["INF2", "INPP5D", "PIK3R5", "WDFY4", "ENSGALG00010021441", "LRRK1"],
                        ["ENSGALG00010021566", "SWT1", "AQP9", "BRE", "ARL8B", "FBXO11"],
                        ["ENSGALG00010004505", "ATRN", "PLD1", "RECQL5", "FNIP1", "MFSD13A"],
                        ["RPLP1", "RPS17", "RPS3", "CIB1", "CALML4", "RACK1"],
                        ["ASMTL", "BRCA1", "RTTN", "HAUS3", "ZRANB3", "ATR"],
                        ["C2CD3", "FANCA", "CEP85", "ZNF367", "MCM10", "TERF2"],
                        ["PIDD1", "NEDD4L", "ENSGALG00010022678", "CLCN5", "CETP", "TRPC4AP"],
                        ["TTR", "PRXL2A", "TMEM254", "COX4I1", "FBP1", "HADH"],
                        ["ENSGALG00010014249", "FBXO45", "TPST1", "NME3", "ENSGALG00010026607", "TCOF1"],
                        ["GPN3", "HAT1", "MRPL19", "GMNN", "BLOC1S4", "SPC25"],
                        ["CNN3", "ATG4C", "SNAP29", "NUB1", "SVIP", "ITFG1"],
                        ["ENSGALG00010001372", "ENSGALG00010001283", "BCAS3", "ENSGALG00010001244", "WWP2",
                         "FLII"], ["FPGT", "SH3GLB1", "SYPL1", "ARF1", "TPM1", "LDHA"],
                        ["SNX19", "GLTP", "SRRD", "TLE3", "MOB1A", "ENSGALG00010022034"],
                        ["PODN", "ZNF598", "RAB11FIP1", "USP20", "DPP9", "LARP1"],
                        ["SMARCB1", "WDR5B", "TSSC4", "ENSGALG00010012079", "PA2G4", "CENPT"],
                        ["BORCS8", "ENSGALG00010026046", "PPA2", "RPL8", "KLHL3", "DCTN1"],
                        ["CUL1", "ZNF518A", "LTN1", "XPOT", "ENSGALG00010009117", "SCFD1"],
                        ["ARHGAP35", "SLC38A10", "TMEM259", "ENSGALG00010027276", "PIK3C2B", "SLC16A1"],
                        ["SLC3A1", "ENSGALG00010005008", "PEPD", "MKLN1", "HIBADH", "IDH1"],
                        ["ENSGALG00010028674", "ENSGALG00010026566", "VPS13C", "MDM4", "SERINC3", "UBXN7"],
                        ["SLC22A5", "ACACB", "XDH", "ENSGALG00010026601", "RNF145", "MIB2"],
                        ["BLVRA", "SCAMP1", "TMEM140", "STK17A", "FIG4", "LRRC70"],
                        ["CIDEA", "PABIR3", "CEPT1", "TDRD7", "DTNBP1", "TM2D1"],
                        ["SLC7A6OS", "TRUB1", "REXO2", "OSER1", "CFAP20", "VCL"],
                        ["LRP5", "ZER1", "ABTB1", "ENSGALG00010014429", "DDHD1", "SLC22A23"],
                        ["SPINK5", "ATP6V0A1", "SERHL", "GSTA4", "TADA1", "NIPSNAP1"],
                        ["CMTR1", "ZNFX1", "MYD88", "DTX3L", "SMCHD1", "EPSTI1"],
                        ["ALKBH5", "TMEM184B", "TMEM39A", "STT3A", "ARCN1", "CNNM4"],
                        ["GTDC1", "ATP6AP1", "WARS", "SERPINE2", "TMEM144", "TMED11"],
                        ["UMPS", "LDHB", "ENSGALG00010017814", "ALAS1", "MLYCD", "RGN"],
                        ["RAB3GAP2", "GOLGA4", "GOPC", "ENSGALG00010024800", "TNKS2", "PPP4R1"],
                        ["CAPN1", "ENSGALG00010000346", "ZNF362", "TET3", "ENSGALG00010003937", "DHX34"],
                        ["NABP1", "TICRR", "SAAL1", "KIF24", "LBR", "IPO9"],
                        ["G3BP1", "SEC22B", "IMMT", "EIF2B5", "ABCF2", "PGK2"],
                        ["UBE3A", "ENSGALG00010023547", "VGLL4", "CHDH", "FBXL5", "RPS6KB1"],
                        ["COPB2", "KIF1BP", "MAGT1", "API5", "SKIV2L2", "UBA6"],
                        ["BMP6", "EML1", "CREBRF", "TRIM23", "LRATD2", "ENSGALG00010008298"],
                        ["CHCHD2", "APH1A", "CHCHD10", "AMT", "NDUFA13", "NDUFS2"],
                        ["MRPS33", "MPHOSPH8", "ENSGALG00010018635", "UBE2G2", "BTF3", "MTIF3"],
                        ["ENSGALG00010015325", "ABCD3", "ENSGALG00010026296", "DENND6A", "ABHD4", "RAB9A"],
                        ["RELN", "ENSGALG00010029265", "GTF2I", "ALS2CL", "ENSGALG00010023446",
                         "ENSGALG00010026223"],
                        ["ENSGALG00010026907", "ACBD4", "SPRYD3", "MFSD5", "SFT2D3", "B4GALT2"],
                        ["TBX2", "NPRL3", "CDHR2", "TBX3", "PCDHGC3", "PGGHG"],
                        ["AAAS", "JUND", "IMP4", "CTU2", "NSUN4", "ULK3"],
                        ["WDR61", "ALDH1A1", "LTA4H", "NDUFA9", "KIFAP3", "SEPTIN2L"],
                        ["TIMP2", "RUSC1", "ENSGALG00010028188", "TIMM13", "LAMTOR2", "PEX19"],
                        ["ENSGALG00010026628", "RFFL", "CYP3A5", "HNRNPD", "SAA", "CYTH4"],
                        ["ITSN1", "CEP120", "ENSGALG00010022810", "CDK5RAP2", "MAP3K1", "FAM126A"],
                        ["SLC43A2", "ENSGALG00010014553", "ENSGALG00010026725", "FAM110C", "HID1", "FNDC3A"],
                        ["SLC25A24", "TUBB6", "LIMS1", "MYEF2", "C21H1orf159", "BBS7"],
                        ["MFSD9", "GID8", "GTF2H1", "OLFM3", "TMEM181", "RAD23B"],
                        ["RFX3", "BCR", "RAPH1", "ENSGALG00010026830", "GARRE1", "TJP1"],
                        ["RALBP1", "TMEM57", "TAF5L", "TAOK3", "NR0B2", "BAG4"],
                        ["KDM4B", "ZFYVE26", "ENSGALG00010018886", "FRMD1", "ENSGALG00010001436",
                         "ENSGALG00010018696"],
                        ["CD74", "ENSGALG00010028194", "ANXA6", "ENSGALG00010017601", "IGSF1", "HEXA"],
                        ["SLC39A8", "FGFR1OP2", "CUL3", "MKKS", "TMEM19", "STX12"],
                        ["ZSWIM8", "CEP170B", "ZNF618", "ZBTB37", "HEG1", "ENSGALG00010028711"],
                        ["ERLEC1", "HPGDS", "RAB28", "TMEM165", "PNO1"],
                        ["ENSGALG00010027239", "ABR", "PLEKHA6", "VPS53", "RNF25"],
                        ["AOC3", "POFUT1", "MRPL37", "SIL1", "HTRA2"],
                        ["DLGAP5", "SLC7A7", "CENPF", "HNRNPA3", "HJURP"],
                        ["WDR1", "TAF1B", "NOP14", "PUM3", "RIOK2"],
                        ["REV3L", "ZNF608", "KLF13", "ENPP1", "SLC45A1"],
                        ["SPRY1", "GNAS", "ENSGALG00010002803", "TBL1XR1", "EXOC3"],
                        ["TCF20", "CHERP", "CREBBP", "SMG7", "ANKRD52"],
                        ["ITGB3", "GATA5", "C1orf210", "SLC25A22", "SMUG1"],
                        ["CATSPER4", "MYO7A", "BMF", "SIX4", "SLC38A6"],
                        ["RUBCNL", "GPR34", "GCNT1", "FAM45A", "ACKR4"],
                        ["RHOA", "RNF7", "RPS24", "RIDA", "THOC7"],
                        ["VPS72", "NUP88", "PLPP2", "GNAI3", "TBL2"],
                        ["ERAL1", "CDC34", "METTL7A", "ENSGALG00010029480", "PROC"],
                        ["ENSGALG00010023425", "IGF1R", "ADAM28", "ENSGALG00010012707", "TIAM1"],
                        ["SMAD6", "ENSGALG00010029351", "GCGR", "NAXE", "ELOB"],
                        ["MRPS25", "PPP1R7", "MRPL58", "YEATS4", "COMMD8"],
                        ["DGKZ", "FBXW5", "FICD", "DCTN4", "ENSGALG00010022925"],
                        ["DCBLD1", "AvBD10", "CITED4", "ENSGALG00010014558", "C11ORF52"],
                        ["TERF1", "RTEL1", "MRE11", "POLQ", "SLC37A1"],
                        ["AATF", "ENSGALG00010016891", "SFPQ", "TSEN2", "GEMIN5"],
                        ["HMOX1", "ENSGALG00010009573", "FMO4", "CDK5", "ENSGALG00010027295"],
                        ["HEPH", "L2HGDH", "ABCD2", "BPHL", "CYP46A1"],
                        ["HSPA5", "RFWD3", "ENSGALG00010012456", "ENOX2", "MYBBP1A"],
                        ["POLA2", "UCK2", "YARS2", "ENSGALG00010014704", "HSP90AB1"],
                        ["CAMLG", "PGPEP1L", "VPS13D", "OSBPL1A", "AGT"],
                        ["PHLPP1", "KCTD2", "NECAP1", "SAP130", "FOXJ3"],
                        ["G0S2", "HNF4A", "VASN", "ENSGALG00010016651", "TRIM7.1"],
                        ["ENSGALG00010024690", "FASTK", "RPUSD4", "EXOSC6", "IGSF9"],
                        ["ACO1", "ENSGALG00010006269", "PAH", "ENSGALG00010012436", "ALDH6A1"],
                        ["MGMT", "DCAF17", "RAB3IP", "ISOC1", "NXT2"],
                        ["ENSGALG00010004705", "SLC29A3", "MYO1D", "CACNB1", "KDM5B"],
                        ["POR", "DLST", "G3BP2", "ELAC2", "EIF3B"],
                        ["MFSD4B", "RASSF8", "CREB3L2", "VAT1", "ATP9A"],
                        ["PCDH7", "ARFGEF3", "ENSGALG00010009268", "RAPGEF1", "MAGI3"],
                        ["GRAMD1C", "PRPF38B", "TOP1", "PHAF1", "PNN"],
                        ["NDUFA10", "ACAA2", "PSMB7", "MRPS27", "GHITM"],
                        ["ENSGALG00010004990", "CACFD1", "SCFD2", "TOR2A", "ENSGALG00010029775"],
                        ["WHAMM", "ENSGALG00010020033", "RHBDF1", "PIAS1", "ELF1"],
                        ["RPL35", "RPLP2", "RPS13", "RPL27", "RPL12"],
                        ["GANC", "PRPF39", "SLC25A48", "BRWD3", "PI4KA"],
                        ["POLR2H", "DDTL", "UPF3B", "SNRPC", "MRPL18"],
                        ["NUP54", "AMD1", "TMEM69", "SLTM", "ACTR8"],
                        ["C10orf88", "ENSGALG00010009378", "GTPBP4", "UBAC2", "SURF6"],
                        ["SSH2", "ZNF687", "ZNF692", "SMARCC2", "CCNT1"],
                        ["TM9SF3", "GNB1", "ENSGALG00010018298", "LRRC28", "HHAT"],
                        ["STRAP", "FARS2", "PDIA4", "SDHA", "PECR"],
                        ["FAM120B", "C1H3ORF52", "CCDC93", "ENSGALG00010005012", "CCDC18"],
                        ["TFPI2", "ASB9", "CYP7A1", "EIF2S3", "LPAR6"],
                        ["SH3GL1", "ENSGALG00010001756", "MIER2", "SLC38A3", "CTNND1"],
                        ["RHOT1", "SCAF11", "TPCN2", "SEC24A", "CLCC1"],
                        ["TMEM39B", "IHH", "EML3", "PTPN9", "DDIT4"],
                        ["MICALL1", "ENSGALG00010000688", "RHOG", "ENSGALG00010022302", "PSME1"],
                        ["MCM5", "MCM3", "CDCA7", "RAD54L", "MCM2"],
                        ["ITGA2B", "NATD1", "C2orf42", "ADD2", "SAMD11"],
                        ["MOSPD1", "CTSZ", "LYPLA1", "HINT3", "EREG"],
                        ["TRPM1", "B3GNT9", "TCF12", "NAA25", "PLEKHA7"],
                        ["CTSH", "TSC22D4", "SCAMP5", "ATP5E", "PAF1"],
                        ["GNA12", "ENSGALG00010020084", "DENND5A", "HMG20A", "PPM1K"],
                        ["SHE", "ENSGALG00010000571", "ENSGALG00010027227", "RNF215", "AIP"],
                        ["TMCO4", "MT3", "DAO", "ENSGALG00010029938", "HSD11B1b"],
                        ["GFM1", "HADHA", "MRPL38", "PSMD1", "HADHB"],
                        ["RPS6KA5", "ITGA1", "PCGF3", "ZEB2", "ENSGALG00010015239"],
                        ["ENSGALG00010012179", "HIST1H101", "IL13RA2", "DNAL4", "BBS4"],
                        ["MAPKBP1", "TTC28", "FLNB", "PRRC2B", "PEAK1"],
                        ["TMCC1", "CCDC186", "EIF2AK4", "MTMR2", "MADD"],
                        ["THOC1", "FBXO5", "RCAN1", "MTFR2", "MTF2"],
                        ["EIF2B3", "ACTR6", "YWHAH", "HNRNPH3", "TUBA5"],
                        ["UTP6", "GINS3", "SRP19", "RSL1D1", "SDF2L1"],
                        ["VPS35L", "PLEK", "RUFY1", "VSIG4", "VPS41"],
                        ["RASA3", "PLAU", "SLC12A7", "FAR1", "MOSPD2"],
                        ["ARHGAP11B", "LIMA1", "PPP1R8", "CCNF", "TFDP2"],
                        ["MAML1", "ZBTB32", "GPRC5B", "DUSP16", "ZC3H12C"],
                        ["MYH11", "PDIK1L", "DACT1", "RPS6KC1", "MGEA5"],
                        ["FKBP4", "NUDCD2", "DHTKD1", "ELP2", "PRORP"],
                        ["COX7C", "MEAF6", "UQCR10", "ATP5PF", "H1F0"],
                        ["TMEM222", "IER5", "ENSGALG00010023487", "ENSGALG00010026434", "CORO1B"],
                        ["ENSGALG00010015468", "ENSGALG00010015603", "WHSC1L1", "NARF", "NELFA"],
                        ["SULF2", "ENSGALG00010025824", "PTPN21", "CGNL1", "SLC22A15"],
                        ["TRIP11", "MKRN2", "PLS3", "PDZD8", "DLG5"],
                        ["HMG20B", "SYNGR2", "NSUN5", "EXOSC1", "MFSD12"],
                        ["AIF1L", "ARHGAP30", "IFI30", "ZNF710", "CYTH1"],
                        ["TMEM132A", "DES", "LOXL3", "FAM43A", "TKFC"],
                        ["ENSGALG00010000635", "RBM19", "FZD3", "GLCE", "NEK9"],
                        ["TMC6", "MED16", "SCAP", "BRPF1", "XYLT2"],
                        ["SEC24C", "NRDC", "ENSGALG00010020454", "ANKLE2", "RTCB"],
                        ["PIK3CD", "DHX57", "NUP188", "RBM47", "RAPGEF6"],
                        ["TMEM161B", "UBR2", "DCUN1D3", "DMXL1", "SPOPL"],
                        ["CRIPT", "CRNKL1", "ENSGALG00010000812", "ADSS2", "GRK4"],
                        ["GATC", "BORCS7", "MED20", "CUTC", "ARHGEF16"],
                        ["SERPINB6", "ATP6V1C1", "CPE", "ASAH1", "C4BPM"],
                        ["NOLC1", "STAG1", "QSER1", "TPR", "ZFYVE9"],
                        ["SNAP23", "PRMT9", "MIOS", "RBM26", "MSH3"],
                        ["ARHGAP42", "INO80C", "ORC1", "BTAF1", "LEO1"],
                        ["FAM107A", "GIPC1", "ZNF341", "CBLL1", "GMEB1"],
                        ["UFD1L", "UEVLD", "SDHD", "MRPL23", "UBE2E3"],
                        ["PTP4A2", "SERP1", "HAGH", "VAMP4", "WBP1L"],
                        ["PPARA", "CMTR2", "ENSGALG00010023042", "TRIP12", "LRRC8C"],
                        ["FOXO4", "WDR81", "PDPR", "PGAP6", "UPF1"],
                        ["PITPNM2", "ADAMTS9", "UNK", "ZBTB44", "AKAP13"],
                        ["MCUR1", "EIF6", "LAP3", "LIPT1", "RPA3"],
                        ["ENSGALG00010012093", "SREBF2", "TRAF7", "TNFRSF21", "KANSL3"],
                        ["DCAF7", "NR2C2", "PPFIA1", "SLC38A9", "KLHL9"],
                        ["UHMK1", "NEIL1", "UQCRQ", "BRCC3", "NDUFA6"],
                        ["TLE4", "LURAP1L", "RNF5", "ENSGALG00010017980", "PRPSAP1"],
                        ["SAPCD2", "SRSF1", "IQGAP3", "IPP", "PRC1"],
                        ["ENSGALG00010023304", "ACP5", "APLNR", "LRRC3C", "ENSGALG00010008013"],
                        ["MARS2", "SEC16B", "ENSGALG00010028060", "FOXRED1", "FLAD1"],
                        ["TBC1D24", "CDK13", "NF1", "ABCA1", "SNX18"],
                        ["SPDL1", "ORC4", "COPS8", "GTF2H3", "TMX4"],
                        ["PTTG1IP", "SGSH", "ENSGALG00010029491", "UBALD1", "SNX33"],
                        ["FASTKD5", "MTOR", "ELP1", "AP1G1", "PHLPP2"],
                        ["PAM16", "COX5B", "VPS37C", "UBTD1", "ENSGALG00010019690"],
                        ["ENSGALG00010006038", "ENSGALG00010000134", "ELOF1", "RRS1", "PRMT5"],
                        ["TAMM41", "MED31", "SELENOF", "MAP2K4", "LRPAP1"],
                        ["ASB1", "UGP2", "ENSGALG00010026909", "ENSGALG00010016177", "ENSGALG00010001640"],
                        ["PHYH", "ENSGALG00010003551", "DNAJB14", "DDX41", "THOP1"],
                        ["NUDT19", "AKR1A1", "SGTA", "PPP1CC", "VMP1"],
                        ["CALCRL", "SESN3", "IQGAP3", "ASAP1", "TBC1D2B"],
                        ["CEP104", "PPP3R1", "PPP2R5C", "EAF1", "RGS12"],
                        ["FBXO4", "ENSGALG00010012893", "RAD1", "COMMD7", "ENSGALG00010012899"],
                        ["COL4A2", "SDK2", "ENSGALG00010014980", "ADAMTS7", "RGS5"],
                        ["SMIM20", "ENSGALG00010003606", "COX6C", "DNAJC19", "RPL26L1"],
                        ["CHD2", "USP22", "RIT1", "PHF12", "MORC1"],
                        ["SRFBP1", "PRELID3B", "PCID2", "MPHOSPH10", "DYNLT3"],
                        ["AFF2", "STXBP1", "SEC31B", "BCL9", "ENSGALG00010018616"],
                        ["DTD1", "RER1", "MRPL33", "UBXN4", "GNG5"],
                        ["NRXN1", "TTC8", "BMP10", "THBS1", "ALDH1A3"],
                        ["DFFA", "ENSGALG00010016041", "VTI1B", "ENSGALG00010026900", "SMAP1"],
                        ["ALG10", "DNAJC25", "CCDC82", "VTA1", "NUDT7"],
                        ["PTGR3", "DECR1", "TXNDC12", "MRPS6", "GATD3AL1"],
                        ["TMEM201", "ZNF516", "SVEP1", "THBS2", "MTHFD1L"],
                        ["TMCO1", "ACAT1", "RDH10", "SUCLG1", "SULT"],
                        ["BLB1", "HRASLS", "SMIM4", "FAM110D", "GJA4"],
                        ["OSGIN1", "DDX21", "FERMT1", "RBL1", "HSPA8"],
                        ["PTPRK", "LANCL1", "WDR33", "ADAM17", "GMPS"],
                        ["PNPLA2", "RNF19A", "SLC22A4", "MASP2", "PDE8A"],
                        ["TENT2", "CLK4", "RNFT1", "ZCCHC10", "NR2C1"],
                        ["NCOA3", "ENSGALG00010014907", "RBMXL1", "ENSGALG00010023327", "MAPK8"],
                        ["TMEM154", "QPCT", "FAM83H", "NRSN1", "RAB5A"],
                        ["ANK3", "PPL", "TNC", "COL6A3", "ENSGALG00010026320"],
                        ["CRK", "REV1", "U2SURP", "RCAN3", "MAPKAPK5"],
                        ["SSNA1", "DNAJC15", "SHFM1", "CWF19L2", "GTF3A"],
                        ["KLHL22", "PEX13", "SGMS1", "NRAS", "TMEM41B"],
                        ["SYNE2", "ADAM9", "ZBTB5", "ZRANB1", "GPC4"],
                        ["CD14", "MYO1F", "TGM2", "MPEG1", "BEAN1"],
                        ["SPARC", "CPTP", "SQSTM1", "ENSGALG00010026686", "COL5A1"],
                        ["UBE2J2", "ACSM5", "MAPK4", "PARD6B", "CARNMT1"],
                        ["CHCHD3", "SLC18B1", "PSMB2", "GTPBP10", "PSMD14"],
                        ["VMA21", "TMBIM4", "PDCD6", "B3GLCT", "HPRT1"],
                        ["RAB11FIP5", "FOXK1", "RUSC2", "SEMA6D", "ETS1"],
                        ["CHD4", "KIAA1671", "IGF2BP2", "ENSGALG00010023460", "HIPK2"],
                        ["AGMAT", "CIDEC", "PAFAH2", "FAHD1", "RPLP0"],
                        ["ZNF384", "ADGRL2", "ANTXR2", "RANBP10", "ENSGALG00010022715"],
                        ["NXN", "UBTD2", "ENSGALG00010026948", "GSK3A", "SOX9"],
                        ["H3F3C", "NAA20", "ENSGALG00010006785", "RBM34", "ZFYVE21"],
                        ["NENF", "PDCD5", "EIF4E3", "RAP1A", "UBE2I"],
                        ["EIF3K", "COX6A1", "ENSGALG00010010869", "RPL19", "ATP5I"],
                        ["ACTR5", "VWA9", "DDX10", "HEATR3", "POLR3B"],
                        ["CHTF18", "PSMD10", "AIFM1", "SRSF7L", "ENSGALG00010018401"],
                        ["IL1RL1", "SMOC2", "IGFBP3", "GAS6", "KCNK4"],
                        ["ZBTB10", "MYO1E", "INPP5E", "REPS2", "COBL"],
                        ["SEPHS3", "MTMR3", "INPPL1", "ENSGALG00010000306", "SF3A1"],
                        ["DNAJC11", "AMPH", "GLE1", "THAP12", "ROBO1"],
                        ["TOLLIP", "NIPAL3", "ZDHHC17", "USP33", "GPATCH1"],
                        ["NFS1", "SLC4A1AP", "PCCB", "ASS1", "SLC25A12"],
                        ["CBS", "CYP7B1", "SLC16A10", "SH3RF1", "MOCOS"],
                        ["CEBPA", "ENSGALG00010028738", "BMI1", "UBTF", "PBX1"],
                        ["NAT8B", "TTC36", "PITHD1", "RNF166", "NAPRT"],
                        ["VANGL1", "RBM33", "HIPK1", "HECTD4", "DMAP1"],
                        ["SRSF6", "ZC3HAV1L", "MCEE", "GPR1", "PLPPR5"],
                        ["ENSGALG00010010901", "CCDC71L", "DEDD", "CCND3", "TBC1D22B"],
                        ["DAPK3", "RARG", "ENSGALG00010024784", "TNKS1BP1", "BAZ2A"],
                        ["SZT2", "MCM3AP", "DEPDC5", "VPS8", "KDM4A"], ["ERI1", "TFDP1", "SMN", "UXS1", "DCTD"],
                        ["UBR1", "DGCR8", "ZCCHC24", "MRTFB", "MARF1"],
                        ["RPUSD3", "TYSND1", "TAF10", "RNPEP", "ENSGALG00010026195"],
                        ["HIST1H2A4L1", "TIMM10", "ADO", "WDR55", "SMIM19"],
                        ["ENSGALG00010003570", "ENSGALG00010003538", "ENSGALG00010007082", "ENSGALG00010007339",
                         "SEMA6B"],
                        ["CCL19", "ENSGALG00010023972", "ENSGALG00010027309", "ENSGALG00010023981", "IFI35"],
                        ["NPLOC4", "WDR18", "RNF26", "STRIP1", "PCSK7"],
                        ["UBE3B", "CLASP1", "NTSR1", "GCN1", "RNF216"],
                        ["WBP2NL", "TOR4A", "SLC11A1", "NCKIPSD", "FKBP15"],
                        ["SMYD4", "ING5", "CABLES1", "ENSGALG00010028453", "SERPINF2"],
                        ["FAAP100", "ANAPC2", "ENSGALG00010025899", "CKLF", "NLRP3"],
                        ["UTP18", "ERLIN1", "DNAAF5", "CRMP1", "NUP93"],
                        ["ENSGALG00010029884", "KIF12", "ZNHIT3", "SLC39A11", "RASA4B"]]

    cluster_data_0_4 = [["ENSGALG00010003614", "ENSGALG00010003644", "ENSGALG00010003584", "ENSGALG00010003635",
                         "ENSGALG00010003575", "ENSGALG00010003643", "ENSGALG00010003613", "ENSGALG00010003623",
                         "ENSGALG00010003598", "ENSGALG00010003640"],
                        ["ENSGALG00010003557", "ENSGALG00010003565", "ENSGALG00010003537", "ENSGALG00010003563",
                         "ENSGALG00010003529", "ENSGALG00010003576"],
                        ["ND4", "COX3", "ND2", "CYTB", "ATP6", "ND1"],
                        ["MCM5", "MCM3", "CDCA7", "RAD54L", "MCM2"]]

    df_0_4 = clusters_to_df(cluster_data_0_4)
    df_0_3 = clusters_to_df(cluster_data_0_3)
    df_0_2 = clusters_to_df(cluster_data_0_2)
    # Also prepare explore versions (using same data)
    df_0_4_explore = df_0_4.copy()
    df_0_3_explore = df_0_3.copy()
    df_0_2_explore = df_0_2.copy()

    try:
        fig_0_4 = px.sunburst(df_0_4, path=["Cluster", "Species"], values="Value", title="Threshold 0.4")
        fig_0_4.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_4 = pio.to_html(fig_0_4, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_04")
    except Exception as e:
        sunburst_html_0_4 = ""
    try:
        fig_0_3 = px.sunburst(df_0_3, path=["Cluster", "Species"], values="Value", title="Threshold 0.3")
        fig_0_3.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_3 = pio.to_html(fig_0_3, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_03")
    except Exception as e:
        sunburst_html_0_3 = ""
    try:
        fig_0_2 = px.sunburst(df_0_2, path=["Cluster", "Species"], values="Value", title="Threshold 0.2")
        fig_0_2.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        sunburst_html_0_2 = pio.to_html(fig_0_2, full_html=False, include_plotlyjs=False,
                                        config={"responsive": True}, div_id="sunburst_02")
    except Exception as e:
        sunburst_html_0_2 = ""
    try:
        explore_fig_0_3 = px.sunburst(df_0_3_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.3")
        explore_fig_0_3.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_3 = pio.to_html(explore_fig_0_3, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_03")
    except Exception as e:
        explore_sunburst_html_0_3 = ""
    try:
        explore_fig_0_4 = px.sunburst(df_0_4_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.4")
        explore_fig_0_4.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_4 = pio.to_html(explore_fig_0_4, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_04")
    except Exception as e:
        explore_sunburst_html_0_4 = ""
    try:
        explore_fig_0_2 = px.sunburst(df_0_2_explore, path=["Cluster", "Species"], values="Value", title="Threshold 0.2")
        explore_fig_0_2.update_layout(width=700, height=700, margin=dict(t=40, l=0, r=0, b=0))
        explore_sunburst_html_0_2 = pio.to_html(explore_fig_0_2, full_html=False, include_plotlyjs=False,
                                                config={"responsive": True}, div_id="explore_sunburst_02")
    except Exception as e:
        explore_sunburst_html_0_2 = ""

    # ileum suggestions from DB
    # otu_list = IleumCorrelation.objects.values_list('var2', flat=True).distinct().order_by('var2')
    # Check from file csv the ileum
    # otu_list = []  # default if anything goes wrong
    try:
        otu_csv_path = os.path.join(settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "csv_massive_lr",
                                    "otu_to_liver.csv")
        df_otu = pd.read_csv(otu_csv_path, )
        otu_list = df_otu.iloc[:, 0].dropna().unique().tolist()
    except Exception as e:
        otu_list = []
        print(f"Error loading otu_to_liver.csv: {e}")

    return render(request, f"{host_type}/liver.html", {
        "host_type": host_type.title(),
        "data_type": "Muscle",
        "description": "Top 200 displayed only. Gene info from Ensembl REST.",
        # "tissue_types": list(tissue_files_muscle.keys()),
        "sunburst_html_0_4": sunburst_html_0_4,
        "sunburst_html_0_3": sunburst_html_0_3,
        "sunburst_html_0_2": sunburst_html_0_2,
        "explore_sunburst_html_0_4": explore_sunburst_html_0_4,
        "explore_sunburst_html_0_3": explore_sunburst_html_0_3,
        "explore_sunburst_html_0_2": explore_sunburst_html_0_2,
        "otu_list": otu_list,
    })

#################################################################
#################################################################
def process_data_scfa22(request, host_type='isabrownv2'):
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
        return JsonResponse({"error": "No recognized AJAX action."}, status=400)

        # File paths
    # peak_area_file = os.path.join("Avapp", "static", "Avapp", "csv", "peak_area_scfa.csv")
    peak_area_file = os.path.join(settings.BASE_DIR, "Avapp", "static", "Avapp", "csv", "peak_area_scfa.csv")
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


#### Muscle Ross
def ross_muscle_data_analysis(request):
    """
    Analyze transcriptomics data (muscle) for a given host type.
    """
    """
       Analyze transcriptomics data (ileum) for a given host type.
       """
    host_type = "ross"

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
    host_type = "isabrown"
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
                pathway_sunburst_data = json.loads(json.dumps(cluster_sunburst.to_dict(),
                                                              default=lambda x: x.tolist() if isinstance(x,
                                                                                                         np.ndarray) else x))
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
                pathway_sunburst_data = json.loads(json.dumps(cluster_sunburst.to_dict(),
                                                              default=lambda x: x.tolist() if isinstance(x,
                                                                                                         np.ndarray) else x))
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


# =============================================================================
# Nk Network Multiomic - Graph Building Logic
# =============================================================================

# Database configuration
def get_nk_network_engine():
    """Get SQLAlchemy engine for Nk Network database connection."""
    db_name = os.environ.get('DB_NAME', 'devdatabase_16_11')
    db_user = os.environ.get('DB_USER', 'reda')
    db_password = os.environ.get('DB_PASSWORD', '1321')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(db_url, pool_pre_ping=True)


# Tissue to table mapping
TISSUE_TABLE_MAP = {
    'otu': 'avapp_tissuecorrelation_otu',
    'ileum': 'avapp_tissuecorrelation',
    'muscle': 'avapp_tissuecorrelation_muscle',
    'liver': 'avapp_tissuecorrelation_liver',
    'metab': 'avapp_tissuecorrelation_metab',
}

# Tissue colors for visualization
TISSUE_COLORS = {
    'otu': '#1f77b4',
    'ileum': '#2ca02c',
    'muscle': '#ff7f0e',
    'liver': '#d62728',
    'metab': '#9467bd',
}


def fetch_seed_candidates_nk(tissue, limit=10000):
    """Fetch seed candidates for a given tissue."""
    engine = get_nk_network_engine()
    table = TISSUE_TABLE_MAP.get(tissue, 'avapp_tissuecorrelation')

    if table == 'avapp_tissuecorrelation':
        mv = 'public.mv_seed_ileum'
    elif table == 'avapp_tissuecorrelation_muscle':
        mv = 'public.mv_seed_muscle'
    elif table == 'avapp_tissuecorrelation_liver':
        mv = 'public.mv_seed_liver'
    else:
        q = text(f"""
            SELECT DISTINCT var2
            FROM {table}
            WHERE var2 IS NOT NULL
            ORDER BY var2
            LIMIT :lim
        """)
        with engine.connect() as conn:
            rows = conn.execute(q, {"lim": limit}).fetchall()
        return [r[0] for r in rows]

    q = text(f"""
        SELECT var2
        FROM {mv}
        ORDER BY var2
        LIMIT :lim
    """)

    with engine.connect() as conn:
        rows = conn.execute(q, {"lim": limit}).fetchall()

    return [r[0] for r in rows]


def fetch_neighbors_nk(seed_id, tissue, allowed_tissues, top_k=5, abs_threshold=0.0,
                        corr_min=-5, corr_max=5, accuracy_min=0.0):
    """Fetch neighbors for a seed variable with monotone constraint."""
    engine = get_nk_network_engine()
    table = TISSUE_TABLE_MAP.get(tissue, 'avapp_tissuecorrelation')

    # Build allowed tissues filter
    if allowed_tissues:
        tissue_filter = f"AND t.to_tissue IN ({','.join([f"'{t}'" for t in allowed_tissues])})"
    else:
        tissue_filter = ""

    q = text(f"""
        SELECT
            t.var1 AS neighbor_id,
            t.correlation,
            t.accuracy,
            t.to_tissue,
            ABS(t.correlation) AS abs_corr
        FROM {table} t
        WHERE t.var2 = :seed_id
            AND ABS(t.correlation) > :abs_thr
            AND t.correlation >= :corr_min
            AND t.correlation <= :corr_max
            AND t.accuracy >= :acc_min
            {tissue_filter}
        ORDER BY abs_corr DESC
        LIMIT :top_k
    """)

    params = {
        "seed_id": seed_id,
        "abs_thr": abs_threshold,
        "corr_min": corr_min,
        "corr_max": corr_max,
        "acc_min": accuracy_min,
        "top_k": top_k
    }

    with engine.connect() as conn:
        rows = conn.execute(q, params).fetchall()

    return [
        {
            'neighbor_id': r[0],
            'correlation': r[1],
            'accuracy': r[2],
            'to_tissue': r[3],
            'abs_corr': r[4]
        }
        for r in rows
    ]


def build_nk_graph(seed_id, tissue, allowed_tissues, top_k=5, max_depth=3,
                   abs_threshold=0.0, corr_min=-5, corr_max=5, accuracy_min=0.0):
    """Build monotone correlation graph."""
    edges = []
    nodes = {}
    visited = set()
    layer = 0

    # Start with seed node
    frontier = [(seed_id, tissue, 0.0)]  # (var_id, from_tissue, parent_abs_corr)

    MAX_FRONTIER = 10000
    MAX_EDGES = 100000

    while frontier and layer < max_depth and len(edges) < MAX_EDGES:
        next_frontier = []

        for current_var, current_tissue, parent_abs in frontier:
            if current_var in visited:
                continue
            visited.add(current_var)

            # Add node if not exists
            if current_var not in nodes:
                nodes[current_var] = {
                    'id': current_var,
                    'label': current_var,
                    'tissue': current_tissue,
                    'layer': layer
                }

            # Fetch neighbors
            neighbors = fetch_neighbors_nk(
                current_var, current_tissue, allowed_tissues,
                top_k, abs_threshold, corr_min, corr_max, accuracy_min
            )

            for n in neighbors:
                neighbor_id = n['neighbor_id']
                abs_corr = n['abs_corr']

                # Monotone constraint: each level must have higher abs correlation
                if abs_corr <= parent_abs and layer > 0:
                    continue

                # Add edge
                edge_key = tuple(sorted([current_var, neighbor_id]))
                if edge_key not in [(e['source'], e['target']) for e in edges]:
                    edges.append({
                        'source': current_var,
                        'target': neighbor_id,
                        'correlation': n['correlation'],
                        'abs_corr': abs_corr,
                        'accuracy': n['accuracy'],
                        'level': layer + 1
                    })

                    # Add neighbor node
                    if neighbor_id not in nodes:
                        nodes[neighbor_id] = {
                            'id': neighbor_id,
                            'label': neighbor_id,
                            'tissue': n['to_tissue'],
                            'layer': layer + 1
                        }

                    if len(next_frontier) < MAX_FRONTIER:
                        next_frontier.append((neighbor_id, n['to_tissue'], abs_corr))

        frontier = next_frontier
        layer += 1

    return {'nodes': list(nodes.values()), 'edges': edges}


def nodes_to_cytoscape(nodes, edges):
    """Convert nodes and edges to Cytoscape.js format."""
    cytoscape_nodes = []
    for node in nodes:
        tissue = node.get('tissue', 'unknown')
        color = TISSUE_COLORS.get(tissue, '#333333')
        cytoscape_nodes.append({
            'data': {
                'id': node['id'],
                'label': node['label'][:30],  # Truncate long labels
                'tissue': tissue,
                'layer': node.get('layer', 0),
                'color': color
            }
        })

    cytoscape_edges = []
    for edge in edges:
        corr = edge['correlation']
        abs_corr = abs(corr)
        edge_color = '#2196F3' if corr > 0 else '#F44336'
        cytoscape_edges.append({
            'data': {
                'source': edge['source'],
                'target': edge['target'],
                'correlation': corr,
                'abs_corr': abs_corr,
                'accuracy': edge.get('accuracy', 0),
                'level': edge.get('level', 0),
                'edge_color': edge_color
            }
        })

    return cytoscape_nodes + cytoscape_edges


@csrf_exempt
def nk_network_api(request):
    """API endpoint for Nk Network Multiomic graph data."""
    if request.method == 'GET':
        # Get parameters
        seed_id = request.GET.get('seed_id', '')
        tissue = request.GET.get('tissue', 'ileum')
        allowed_tissues = request.GET.getlist('allowed_tissues')
        top_k = int(request.GET.get('top_k', 5))
        max_depth = int(request.GET.get('max_depth', 3))
        abs_threshold = float(request.GET.get('abs_threshold', 0.0))
        corr_min = float(request.GET.get('corr_min', -5))
        corr_max = float(request.GET.get('corr_max', 5))
        accuracy_min = float(request.GET.get('accuracy_min', 0.0))

        if not seed_id:
            return JsonResponse({'error': 'seed_id is required'}, status=400)

        # Build graph
        graph_data = build_nk_graph(
            seed_id, tissue, allowed_tissues, top_k, max_depth,
            abs_threshold, corr_min, corr_max, accuracy_min
        )

        # Convert to Cytoscape format
        elements = nodes_to_cytoscape(graph_data['nodes'], graph_data['edges'])

        return JsonResponse({
            'elements': elements,
            'stats': {
                'node_count': len(graph_data['nodes']),
                'edge_count': len(graph_data['edges'])
            }
        })

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def nk_network_seeds(request):
    """API endpoint to get seed candidates for Nk Network."""
    if request.method == 'GET':
        tissue = request.GET.get('tissue', 'ileum')
        limit = int(request.GET.get('limit', 1000))

        seeds = fetch_seed_candidates_nk(tissue, limit)
        return JsonResponse({'seeds': seeds[:limit]})

    return JsonResponse({'error': 'Method not allowed'}, status=405)
