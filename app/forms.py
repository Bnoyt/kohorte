from django import forms
from .models import *

class UtilisateurProfileForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = '__all__'

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('titre', 'contenu')

class BugForm(forms.Form):
    sujet = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)