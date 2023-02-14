from django.contrib import admin
from django import forms 
from django.template.response import TemplateResponse
from django.urls import path
from django.shortcuts import render

from movie.models import Movie, Seat, Show, Promotion
# Register your models here.


class PromotionAdminForm(forms.ModelForm):
    is_sent = forms.BooleanField(required=False)

    class Meta:
        model = Promotion
        fields = "__all__"
    
    def clean(self):
        if self.cleaned_data.get("is_sent", False):
                raise forms.ValidationError("cant update promotion already sent")
        return self.cleaned_data


class ShowAdminForm(forms.ModelForm):

    class Meta:
        model = Show
        fields="__all__"

    def clean(self):
        data = self.cleaned_data
        end_between_show = Show.objects.filter(
            show_date=data["show_date"], 
            end_time__range=(data["start_time"], data["end_time"])
            ).exists()
        
        start_between_show = Show.objects.filter(
            show_date=data["show_date"], 
            start_time__range=(data["start_time"], data["end_time"])
            ).exists()
         
        if end_between_show or start_between_show:
            raise forms.ValidationError("Other show already exists at these timings")
        return data

class MovieAdmin(admin.ModelAdmin):
    fields = ('title', 'alias', 'category', 'rating', 'cast', 'director', 'trailer', 'synopsis', 'movie_code', 'expire_date', 'poster_image', 'is_playing')
    list_display=['title', 'alias', 'movie_code', 'expire_date', 'poster_image', 'is_playing']

admin.site.register(Movie, MovieAdmin)


class ShowAdmin(admin.ModelAdmin):
    form = ShowAdminForm
    # fields = ('movie', 'show_date','start_time', 'end_time')
    list_display=['get_title', 'movie', 'show_date','start_time', 'end_time']

    @admin.display(ordering='movie__title', description='Movie')
    def get_title(self, obj):
        return obj.movie.title

admin.site.register(Show, ShowAdmin)


class PromotionAdmin(admin.ModelAdmin):
    form = PromotionAdminForm
    # fields = ['movie', 'promo_code', 'off_amount', 'off_percent', 'promo_type', 'min_amount']
    list_display=['promo_code', 'off_amount', 'off_percent', 'promo_type', 'min_amount']

admin.site.register(Promotion, PromotionAdmin)

admin.site.register(Seat)

