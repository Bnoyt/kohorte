from django import forms
from .models import *
from markdownx.widgets import MarkdownxWidget

class UtilisateurProfileForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = '__all__'

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('titre', 'contenu')
        widgets = {
            'titre': forms.TextInput(attrs={'class': "form-control border-input"}),
            'contenu': MarkdownxWidget(attrs={'class': "form-control border-input"}),
        }

class BugForm(forms.Form):
    sujet = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)