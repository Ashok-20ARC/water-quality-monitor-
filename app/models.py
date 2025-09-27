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

class AnalysisResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='water_samples/')
    timestamp = models.DateTimeField(auto_now_add=True)
    wqi_score = models.FloatField()
    clarity_score = models.FloatField()
    avg_color_bgr = models.CharField(max_length=50) # Stored as "b,g,r"
    ph = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    dissolved_oxygen = models.FloatField(null=True, blank=True)
    turbidity = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Analysis for {self.user.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-timestamp']