from django.conf.urls import include, url
from django.contrib import admin

from main import views


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', views.Index.as_view(), name='index'),

    url(r'^data/(?P<mdl>[\w-]+)/', views.Data.as_view(), name='data'),
    url(r'^create/(?P<mdl>[\w-]+)/', views.Create.as_view(), name='create'),
    url(r'^update/(?P<mdl>[\w-]+)/(?P<pk>[\w-]+)/',
        views.Update.as_view(), name='update'),
]
