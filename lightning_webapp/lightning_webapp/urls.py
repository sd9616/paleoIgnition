from django.contrib import admin
from django.urls import path
from lightningapp import views



urlpatterns = [
    path("admin/", admin.site.urls),
    path('index/', views.index, name='index'),
    path('plot-lightning/', views.plot_lightning, name='plot_lightning'),
    path('export-data/', views.export_data, name='export_data'),
    path('contact/', views.contact, name='contact'),
    path('home/', views.home, name='home'),
    path('create-plot/', views.create_plot, name='create_plot'),
    path('about/', views.about, name='about'),
]
