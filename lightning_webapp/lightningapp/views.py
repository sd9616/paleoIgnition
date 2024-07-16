import zipfile
import pandas as pd 
from django.shortcuts import render
import netCDF4
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.http import HttpResponse, HttpResponseBadRequest
from django.template import loader
import os
import scipy.io as sio
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def contact(request):
    return render(request, 'contact.html')

def create_plot(request):
    return render(request, 'create_plot.html')

def about(request):
    return render(request, 'about.html')

def home(request):
    return render(request, 'home.html')

def index(request):
    return render(request, 'index.html')

TRACE = "TRACE"
FAMOUS = "FAMOUS"
LOVECLIM = "LOVECLIM"

# REPLACE WITH PATH TO FILE WITH NPY FILES
# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to your file
file_path = os.path.join(current_dir, 'data')
print(file_path)

# [variable, latitude, longitude, time]
dataset_files_loveclm = [
    np.load(file_path + '/lc_rolling_avg_with_latlon.npy'),
    np.load(file_path + '/lc_lat.npy'),
    np.load(file_path + '/lc_lon.npy'),
    np.load(file_path + '/lc_time_rolling.npy')
]
#lightningapp/data/fa_lat.npy

dataset_files_trace = [
    np.load(file_path + '/tr_rolling_avg_with_latlon.npy'),
    np.load(file_path + '/tr_lat.npy'),
    np.load(file_path + '/tr_lon.npy'),
    np.load(file_path + '/tr_time_rolling.npy')
]

dataset_files_famous = [
    np.load(file_path + '/fa_rolling_avg_with_latlon.npy'),
    np.load(file_path + '/fa_lat.npy'),
    np.load(file_path + '/fa_lon.npy'),
    np.load(file_path + '/fa_time_rolling.npy')
]

dataset_files_list = {
    TRACE: dataset_files_trace,
    LOVECLIM: dataset_files_loveclm,
    FAMOUS: dataset_files_famous,
}

def plot_lightning(request):
    if request.method == 'POST':
        lat_point = float(request.POST.get('latitude'))
        print(lat_point)
        lon_point = float(request.POST.get('longitude'))
        print(lat_point)
        dataset = request.POST.get('dataset')
        print(dataset)


        dataset_files = None

        if dataset == "ALL":
            plt.figure(figsize=(10, 6))
            for key, dataset_files in dataset_files_list.items():
                var = dataset_files[0]
                lat = dataset_files[1]
                lon = dataset_files[2]
                time = dataset_files[3]

                print(var.shape)
                lat_idx = np.argmin(np.abs(lat - lat_point))
                lon_idx = np.argmin(np.abs(lon - lon_point))

                if lat_idx < 0 or lat_idx >= lat.shape[0] or lon_idx < 0 or lon_idx >= lon.shape[0]:
                    print(f"Error: Latitude or longitude values are out of bounds for the dataset {key}. Skipping.")
                    continue

                plt.plot(time, var[:, lat_idx, lon_idx].flatten(), label=f'{key}')

            plt.xlabel('Time')
            plt.ylabel('Lightning')
            plt.title(f'All Datasets: Time series of Lightning at Lat: {lat_point}, Lon: {lon_point}')
            plt.grid(True)
            plt.legend()
            plt.tight_layout()
            plt.show()

            # Construct the absolute path to file
            png_file_path = os.path.join(current_dir, 'static','plots')
            plot_file_path = png_file_path + '/plots.png'
            plt.savefig(plot_file_path)

            # Close the plot to prevent memory leaks
            plt.close()

            # Render the template with the plot
            template = loader.get_template('/Users/andrewondara/lightning-webapp/lightning_webapp/lightningapp/templates/index.html')
            context = {'plot_file_path': plot_file_path}
            return HttpResponse(template.render(context, request))
        elif dataset in dataset_files_list:
            dataset_files = dataset_files_list[dataset]

            if -180 <= lat_point < 0:
                lat_point = lat_point + 360
            
            var = dataset_files[0]
            lat = dataset_files[1]
            lon = dataset_files[2]
            time = dataset_files[3]

            lat_idx = np.argmin(np.abs(lat - lat_point))
            lon_idx = np.argmin(np.abs(lon - lon_point))

            if lat_idx < 0 or lat_idx >= lat.shape[0] or lon_idx < 0 or lon_idx >= lon.shape[0]:
                print("Error: Latitude or longitude values are out of bounds for the dataset.")
                return

            plt.figure(figsize=(10, 6))
            plt.plot(time, var[:, lat_idx, lon_idx], marker='o')
            plt.xlabel('Time')
            plt.ylabel('Lightning')
            
            # plt.title(f'{dataset}: Time series of Lightning at Lat: {lat_point}, Lon: {lon_point}')
            plt.title(f'{dataset}: Time series of Lightning at Lat: {lat_point}, Lon: {lon_point}')
            plt.grid(True)
            plt.tight_layout()


            # Save the plot to a file
            png_file_path = os.path.join(current_dir, 'static','plots')
            plot_file_path = png_file_path + '/plots.png'
            plt.savefig(plot_file_path)
            # Save the data to a CSV file
            data = np.column_stack((time, var[:, lat_idx, lon_idx]))
            csv_file_path = os.path.join(current_dir, 'static', 'csv')
            data_file_path = os.path.join(csv_file_path, 'data.csv')
            np.savetxt(data_file_path, data, delimiter=',')

            # Close the plot to prevent memory leaks
            plt.close()

            # Construct the absolute path to your template file
            template_path = os.path.join(current_dir, 'templates', 'create_plot.html')

            # Load the template using the absolute path
            template = loader.get_template(template_path)
            context = {'plot_file_path': plot_file_path}
            return HttpResponse(template.render(context, request))

        else:
            return HttpResponseBadRequest("Invalid dataset name")
        
    return HttpResponseBadRequest()

def export_data(request):
    if request.method == 'POST':
    
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="plot_and_data.zip"'
        plot_file_path = os.path.join(current_dir, 'static', 'plots', 'plots.png')
        data_file_path = os.path.join(current_dir, 'static', 'csv', 'data.csv')

        with zipfile.ZipFile(response, 'w') as zipf:
            zipf.write(plot_file_path, arcname='plots.png')
            zipf.write(data_file_path, arcname='data.csv')

        return response
    else:
        return HttpResponseBadRequest("Invalid request method")