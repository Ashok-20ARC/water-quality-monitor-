from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .analysis_logic import perform_full_analysis
import json
from django.db.models import Avg, Count
from django.utils import timezone
from .models import AnalysisResult
from .forms import ImageUploadForm,CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm

@login_required
def home_view(request):
    form = ImageUploadForm()
    latest_result = AnalysisResult.objects.filter(user=request.user).first()
    recent_analyses = AnalysisResult.objects.filter(user=request.user)[:5]

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES['image']
            
            try:
                # Perform the analysis
                analysis_data = perform_full_analysis(image_file)

                # Save the result to the database
                result = AnalysisResult(
                    user=request.user,
                    image=image_file, # Django handles saving the uploaded file
                    wqi_score=analysis_data['wqi_score'],
                    clarity_score=analysis_data['clarity_score'],
                    avg_color_bgr=analysis_data['avg_color_bgr'],
                    ph=analysis_data['ph'],
                    temperature=analysis_data['temperature'],
                    dissolved_oxygen=analysis_data['dissolved_oxygen'],
                    turbidity=analysis_data['turbidity']
                )
                result.save()
                messages.success(request, 'Analysis complete! See the new results below.')
                return redirect('home')

            except Exception as e:
                messages.error(request, f"An error occurred during analysis: {e}")
    
    # Chart Data Preparation
    chart_data = {}
    all_analyses = AnalysisResult.objects.filter(user=request.user).order_by('timestamp')
    if all_analyses.exists():
        # WQI Trend Chart
        wqi_labels = [res.timestamp.strftime('%b %d, %H:%M') for res in all_analyses]
        wqi_values = [round(res.wqi_score, 2) for res in all_analyses]

        # Average Sensor Readings Radar Chart
        avg_stats = all_analyses.aggregate(
            avg_ph=Avg('ph'),
            avg_temp=Avg('temperature'),
            avg_do=Avg('dissolved_oxygen'),
            avg_turbidity=Avg('turbidity')
        )

        chart_data = {
            'wqiLabels': wqi_labels,
            'wqiValues': wqi_values,
            'sensorLabels': ['pH', 'Temperature (°C)', 'Dissolved O2 (mg/L)', 'Turbidity (NTU)'],
            'sensorValues': [
                round(avg_stats['avg_ph'] or 0, 2),
                round(avg_stats['avg_temp'] or 0, 2),
                round(avg_stats['avg_do'] or 0, 2),
                round(avg_stats['avg_turbidity'] or 0, 2),
            ]
        }


    context = {
        'form': form,
        'latest_result': latest_result,
        'recent_analyses': recent_analyses,
        'chart_data_json': json.dumps(chart_data)
    }
    return render(request, 'app/home.html', context)


@login_required
def history_view(request):
    all_analyses = AnalysisResult.objects.filter(user=request.user)
    context = {'analyses': all_analyses}
    return render(request, 'app/history.html', context)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('home')
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"{field.label}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request, 'app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')