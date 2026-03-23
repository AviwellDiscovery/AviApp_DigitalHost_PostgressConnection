from django.urls import path
from .views import plot, graph_view, download_csv, custom_login, custom_logout, HostFilterView, SchemaOverview, \
    isabrown_detailv2, \
    DigitalHostFilterViewv2, DigitalHostFilterView, liver_data_analysisv2, muscle_data_analysisv2, \
    process_data_functionnal2, ensembl_id_lookup, process_databacteryv2, process_dataliverv2, molecule_data_analysisv2, \
    ileum_data_analysisv2, bacterien_data_analysisv2, host_detail, get_features_by_study, filter_data_by_feature, \
    filter_data_by_features, muscle_data_analysis, liver_data_analysis, ross_muscle_data_analysis, ileum_data_analysis, \
    process_data_scfa2 , bacterien_data_analysisv2_ross, muscle_data_analysisv2_ross, nk_network_api, nk_network_seeds
from . import views
from django.contrib.auth.views import LoginView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('study', views.showdata_study, name="study"),
    path('analysis', views.showdata_analysis, name="analysis"),
    path('feature', views.showdata_feature, name="feature"),
    path('pen', views.showdata_pen, name="pen"),
    # test numercial host
    path('fetch_sunburst_data/', views.fetch_sunburst_data, name='fetch_sunburst_data'),
    path('fetch_sunburst_data_ross_muscle/', views.fetch_sunburst_data_ross_muscle, name='fetch_sunburst_data_ross_muscle'),

    #ileum isabrown
    # path('<str:host_type>/ileum/', ileum_data_analysis, name='ileum_data_analysis'),

    path('isabrown/ileum/', ileum_data_analysis, name='ileum_data_analysis'),
    path('isabrownv2/ileum/', ileum_data_analysisv2, name='process_data_ileumv2'),
    path('isabrownv2/muscle/',muscle_data_analysisv2, name='msucle_data_analysisv2'),
    path('isabrownv2/molecule/', molecule_data_analysisv2, name='molecule_data_analysisv2'),
    path('isabrownv2/liver/', liver_data_analysisv2, name='process_data_liverv2'),
    path('isabrownv2/bacterien/', bacterien_data_analysisv2, name='process_databacteryv2'),
    path('isabrownv2/fonctionnel/', process_data_functionnal2, name='process_data_functionnal2'),
    path('isabrownv2/scfa/', process_data_scfa2, name='process_data_scfa2'),
    path('rossv2/bacterien/', bacterien_data_analysisv2_ross, name='bacterien_data_analysisv2_ross'),
    path('rossv2/muscle/', muscle_data_analysisv2_ross, name='muscle_data_analysisv2_ross'),

    #ensemble lookup
    path('ensembl-lookup/', views.ensembl_id_lookup, name='ensembl_id_lookup'),
    #liver isabrown
    path('<str:host_type>/liver/', liver_data_analysis, name='liver_data_analysis'),
    #muscle
    path('ross/muscle/', ross_muscle_data_analysis, name='ross_muscle_data_analysis'),
    path('isabrown/muscle/', muscle_data_analysis, name='muscle_data_analysis'),
    # isabrown otuv2
    # path('<str:host_type>/bacterien/', views.bacterien_data_analysisv2, name='bacterien'),
    # path('<str:host_type>/ileum/', ileum_data_analysisv2, name='ileum'),


    #bacterien isabrown
    path('<str:host_type>/bacterien/', views.bacterien_data_analysis, name='bacterien'),
 # molecule isabrown
    path('<str:host_type>/molecule/', views.molecule_data_analysis, name='molecule_data'),
    path('<host_type>/<data_type>/', views.process_data, name='process_data'),
    # path('<host_type>/<data_type>/', views.process_datav2, name='process_data_ileumv2'),
    path('<host_type>/<data_type>/', views.process_datamusclev2, name='process_data_musclev2'),
    path('<host_type>/<data_type>/', views.process_datamoleculev2, name='process_data_moleculev2'),
    # path('<host_type>/<data_type>/', views.process_dataliverv2, name='process_data_liverv2'),
    path('<host_type>/<data_type>/', views.process_databacteryv2, name='process_databacteryv2'),
    path('<host_type>/<data_type>/', views.process_databacteryv2_ross, name='process_databacteryv2_ross'),
    path('<host_type>/<data_type>/', views.muscle_data_analysisv2_ross, name='muscle_data_analysisv2_ross'),

    #path('<host_type>/<data_type>/', views.process_data_functionnal2, name='process_data_functionnal2'),



    path('isabrown/', views.isabrown_detail, name='isabrown_detail'),
    path('isabrownv2/', views.isabrown_detailv2, name='isabrown_detailv2'),
    path('rossv2/', views.ross_detailv2, name='ross_detailv2'),

    path('ross/', views.ross_detail, name='ross_detail'),
    path('DigitalHost', DigitalHostFilterView.as_view(), name="DigitalHost"),
    path('DigitalHostv2', DigitalHostFilterViewv2.as_view(), name="DigitalHostv2"),
    path('host/<str:host_type>/', host_detail, name='host_detail'),  # Make sure this line is here
    path('host/chicken/', host_detail, name='host_detail'),  # same line after selection from first
    path('get_features_by_study/', get_features_by_study, name='get_features_by_study'),
    path('filter_data_by_feature/', filter_data_by_feature, name='filter_data_by_feature'),
    path('filter_data_by_features/', filter_data_by_features, name='filter_data_by_features'),
    path('construct_query/', views.construct_query, name='construct_query'),
    #end test digital host
    path('host', HostFilterView.as_view(), name="host"),
    path('schema', SchemaOverview.as_view(), name="schema"),
    path('pen/<int:entry_id>/', views.showdata_penhasfeature, name='showdata_penhasfeature'),
    path('host/<int:entry_id>/', views.showdata_hosthaspen, name='showdata_hosthaspen'),
    path("<int:question_id>/results/", views.results, name="results"),
    path('plot/', plot, name='plot'),
    path('bokeh/', graph_view, name='graph-view'),
    path('download/', download_csv, name='download_csv'),
    path('form/', views.my_view, name='showdata_hosthaspen'),
    path('visualize/', views.visualize_data, name='visualize_data'),
    path('analysis/', views.analysis_data, name='analysis'),
    path('selected_hosts/', views.analysis_data, name='selected_hosts'),
    #
    path('host_filter/', views.host_filter_view, name='host_filter'),
    # path('login/', custom_login, name='custom_login'),
    path('', LoginView.as_view(), name='login'),  # Set the default URL to login
    path('logout/', custom_logout, name='logout'),
    path('streamlit/', views.streamlit_view, name='streamlit_view'),
    path('shiny_dashboard/', views.shiny_dashboard, name='shiny_dashboard'),
    path('session_key/', views.generate_session_key, name='session_key'),
    path('generate_token/', views.generate_token, name='generate_token'),

    # Nk Network Multiomic API
    path('nk-network/api/', nk_network_api, name='nk_network_api'),
    path('nk-network/seeds/', nk_network_seeds, name='nk_network_seeds'),

]

urlpatterns += staticfiles_urlpatterns()
