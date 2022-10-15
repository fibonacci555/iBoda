from email.policy import default
from django import forms
from .models import Post, Comment, Feedback
from django.db import models

AGE_CHOICES =(
    ("Todas as idades", "Todas as idades"),
    ("+18", "+18"),
    ("+25", "+25"),
    ("+40", "+40"),
    
)

MUSIC_CHOICES =(
    ("Todos os géneros", "Todos os géneros"),
    ("Techno", "Techno"),
    ("Jazz", "Jazz"),
    ("80's", "80's"),
    ("Hip-Hop", "Hip-Hop"),
    ("Funk", "Funk"),
)

CITIES = (("Alcobaça", "Alcobaça"),
("Almada", "Almada"),
("Amadora", "Amadora"),
("Aveiro", "Aveiro"),
("Barreiro", "Barreiro"),
("Beja", "Beja"),
("Braga", "Braga"),
("Bragança", "Bragança"),
("Cartaxo", "Cartaxo"),
("Chaves", "Chaves"),
("Coimbra", "Coimbra"),
("Elvas", "Elvas"),
("Espinhos", "Espinhos"),
("Évora", "Évora"),
("Faro", "Faro"),
("Fátima", "Fátima"),
("Funchal", "Funchal"),
("Fundão", "Fundão"),
("Gouveia", "Gouveia"),
("Guarda", "Guarda"),
("Leiria", "Leiria"),
("Lisboa", "Lisboa"),
("Loures", "Loures"),
("Maia", "Maia"),
("Mirandela", "Mirandela"),
("Moura", "Moura"),
("Penafiel", "Penafiel"),
("Pinhel", "Pinhel"),
("Portalegre", "Portalegre"),
("Portimão", "Portimão"),
("Porto", "Porto"),
("Praia da Vitória", "Praia da Vitória"),
("Queluz", "Queluz"),
("Ribeira Grande", "Ribeira Grande"),
("Santa Cruz", "Santa Cruz"),
("Santana", "Santana"),
("São Pedro do Sul", "São Pedro do Sul"),
("Seia", "Seia"),
("Setúbal", "Setúbal"),
("Sintra", "Sintra"),
("Tavira", "Tavira"),
("Tomar", "Tomar"),
("Trancoso", "Trancoso"),
("Trofa", "Trofa"),
("Viana do Castelo", "Viana do Castelo"),
("Vila Nova de Gaia", "Vila Nova de Gaia"),
("Vila Real", "Vila Real"),
)






class PostForm(forms.ModelForm):
    body = forms.CharField(
        label='',
        widget=forms.Textarea(
            attrs={'rows': '3',
                   'placeholder': 'Say Something...'}
        ))
    image = forms.ImageField(required=False)
    music = forms.ChoiceField(choices = MUSIC_CHOICES)
    age = forms.ChoiceField(choices = AGE_CHOICES)
    city = forms.ChoiceField(choices=CITIES)
    

    class Meta:
        model = Post
        fields = ['title','city','body','music','date','age','image','url','public']

class CommentForm(forms.ModelForm):
    comment = forms.CharField(
        label='',
        widget=forms.Textarea(
            attrs={'rows': '3',
                   'placeholder': 'Say Something...'}
        ))

    class Meta:
        model = Comment
        fields = ['comment']

class FeedbackForm(forms.ModelForm):
    body = forms.CharField(
        label='',
        widget=forms.Textarea(
            attrs={'rows': '3',
                   'placeholder': 'Say Something...'}
        ))
    
    

    class Meta:
        model = Feedback
        fields = ['name', 'body', 'email']




#class RegisterForm(forms.ModelForm):

#    birth = models.DateField(default="2002-09-03",blank=False,null=False)

#    class Meta:
#        model = UserProfile
#        fields = ['birth','city']




