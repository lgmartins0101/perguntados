from django.db import models
import jsonfield  
class Questao(models.Model):
    enunciado = models.CharField(max_length=500)
    respostas = jsonfield.JSONField() 
    resposta_correta = models.IntegerField()
    nivel= models.CharField(max_length=20)
    categoria= models.CharField(max_length=40)

    
      

class Jogo(models.Model):
    nome = models.CharField(max_length=200)
    data_criacao = models.DateField(auto_now_add=True)
    questoes = jsonfield.JSONField()  
    time_a_pontos = models.IntegerField(default=0)
    time_b_pontos = models.IntegerField(default=0)
    time_c_pontos = models.IntegerField(default=0)
    time_d_pontos = models.IntegerField(default=0)

    