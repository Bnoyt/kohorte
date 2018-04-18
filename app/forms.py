from django import forms
from .models import *
from markdownx.widgets import MarkdownxWidget

class UtilisateurProfileForm(forms.Form):
    pseudo = forms.CharField(max_length=100)#quel max ?
    email = forms.EmailField()
    passwordOld = forms.CharField(max_length=32, widget=forms.PasswordInput) 
    passwordNew = forms.CharField(max_length=32, widget=forms.PasswordInput) 
    passwordNewField = forms.CharField(max_length=32, widget=forms.PasswordInput) 
    genre = forms.ChoiceField(choices = Utilisateur.GENRES)
    age = forms.IntegerField(min_value=0 , max_value = 150)

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
