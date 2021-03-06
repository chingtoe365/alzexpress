"""ADDB URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from ADDBapp import views, views_csvdownloaders, ajax

summary_patterns = ([
        url(r'^$', views.summary, name='addb_summary'),
        url(r'^(?P<dataset>GSE[\d]+)/$', views.dataset_summary, name='addb_dataset_summary'),
        url(r'^(?P<dataset>GSE[\d]+)/(?P<region>[\w]+)$', views.summary_volcano, name='addb_summary_volcano'),
    ])

csv_downloader_patterns = ([
        # url(r'^$', views.summary, name='addb_summary'),
        # url(r'^(?P<collection_string>.+)/$', views_csvdownloaders.download_cross_study_deg_csv, name="addb_download_cross_study_deg_csv"),
        url(r'^cross-study/(?P<collection_string>.+)/$', views_csvdownloaders.download_cross_study_deg_csv, name="addb_download_cross_study_deg_csv"),
        url(r'^meta/(?P<collection_name>.+)/$', views_csvdownloaders.download_csv_for_all_meta_stat, name="download_csv_for_all_meta_stat"),
        url(r'^meta/(?P<collection_name>.+)/(?P<feature_string>.+)$', views_csvdownloaders.download_csv_for_meta_queried_features, name="download_csv_for_meta_queried_features"),
        url(r'^separate/(?P<dataset>.+)/(?P<region>.+)/$', views_csvdownloaders.download_csv_for_separate_stat, name="download_csv_for_separate_stat"),
    ])  

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name="addb_home"),
    # url(r'^$', views.index, name="addb_index"),
    url(r'^upload/', views.upload, name="addb_upload"),
    url(r'^query/', views.query, name="addb_query"),
    url(r'^summary/', include(summary_patterns)),
    # url(r'^summary/$', views.summary, name="addb_summary"),
    # url(r'^summary/(?P<dataset>GSE[\d]+)', views.dataset_summary, name="addb_dataset_summary"),
    url(r'^detail/', views.detail, name="addb_detail"),
    url(r'^meta/', views.meta, name="addb_meta"),
    url(r'^crossstudy/', views.cross_study, name="addb_cross_studies"),
    url(r'^get_top_tables/', ajax.get_top_tables, name="addb_gettoptable"),
    # url(r'^download_cross_study_deg_csv/', views_csvdownloaders.download_cross_study_deg_csv, name="addb_download_cross_study_deg_csv"),
    # url(r'^download_cross_study_deg_csv/', include(csv_downloader_patterns)),
    url(r'^download/', include(csv_downloader_patterns)),
    # url(r'^featureQuery/', views.featureQuery, name="addb_featureQuery"),
    # url(r'^test/', views.test, name="addb_test"),
    # url(r'^queriedfeatures/', views.queried_feature_stat, name="queried_feature_stat"),
    # url(r'^$', views.index, name='addb_index'),
    # url(r'^upload/', views.upload, name='addb_upload'),
    # url(r'^query/', views.query, name='addb_query'),
    # url(r'^upload_handler/', views.upload_handler),
]

