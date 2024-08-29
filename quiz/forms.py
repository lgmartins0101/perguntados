from django import forms
from .models import Questao, Jogo

class CriarQuestaoForm(forms.ModelForm):
    class Meta:
        model = Questao
        fields = ['enunciado', 'respostas', 'resposta_correta']

class CriarJogoForm(forms.ModelForm):
    questoes= forms.JSONField()  # Campo para capturar IDs das questões em JSON

    class Meta:
        model = Jogo
        fields = ['nome', 'questoes']

class VerificarRespostaForm(forms.Form):
    jogo_id = forms.ModelChoiceField(queryset=Jogo.objects.all())
    time = forms.ChoiceField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    questao_id = forms.ModelChoiceField(queryset=Questao.objects.all())
    resposta_fornecida = forms.IntegerField()
