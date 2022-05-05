from django.contrib import admin
from django.db.models import Count
from django.template.response import TemplateResponse
from .models import User, Post, Comment, Tag
from django.utils.html import mark_safe
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.urls import path



admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Tag)

