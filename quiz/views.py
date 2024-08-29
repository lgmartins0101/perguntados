from django.shortcuts import render, redirect, get_object_or_404
from .forms import CriarQuestaoForm, CriarJogoForm, VerificarRespostaForm
from .models import Jogo, Questao
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json



def formatar_questao(questao):
    return {
        'id': questao.id,
        'enunciado': questao.enunciado,
        'respostas': questao.respostas,
        'resposta_correta': questao.resposta_correta
    }

def formatar_jogo(jogo):
    return {
        'id': jogo.id,
        'nome': jogo.nome,
        'data_criacao': jogo.data_criacao,
        'questoes': jogo.questoes,
        'time_a_pontos': jogo.time_a_pontos,
        'time_b_pontos': jogo.time_b_pontos,
        'time_c_pontos': jogo.time_c_pontos,
        'time_d_pontos': jogo.time_d_pontos
    }

def json_response(data, status=200):
    return JsonResponse(data, status=status, safe=False)

def erro_response(message, status=400):
    return JsonResponse({'status': 'error', 'message': message}, status=status)



@csrf_exempt
def verificar_resposta(request):
    if request.method == "POST":
        data=json.loads(request.body)
        form = VerificarRespostaForm(data)
        if form.is_valid():
            jogo_id = form.cleaned_data['jogo_id'].id
            time = form.cleaned_data['time']
            questao_id = form.cleaned_data['questao_id'].id
            resposta_fornecida = form.cleaned_data['resposta_fornecida']            
            
            jogo = get_object_or_404(Jogo, id=jogo_id)
            questao = get_object_or_404(Questao, id=questao_id)
            
            if not jogo or not questao:
                return JsonResponse({'status': 'error', 'message': 'Jogo ou questão não encontrado.'}, status=404)
        
            if resposta_fornecida == questao.resposta_correta:
                # Atualizar a pontuação do time
                if time == 'A':
                    jogo.time_a_pontos += 10
                elif time == 'B':
                    jogo.time_b_pontos += 10
                elif time == 'C':
                    jogo.time_c_pontos += 10
                elif time == 'D':
                    jogo.time_d_pontos += 10                
                
                jogo.save()
                return JsonResponse({'status': 'success', 'message': 'Resposta correta!'})
            else:
                
                if time != 'A':
                    jogo.time_a_pontos += 5
                if time != 'B':
                    jogo.time_b_pontos += 5
                if time != 'C':
                    jogo.time_c_pontos += 5
                if time != 'D':
                    jogo.time_d_pontos += 5
                mensagem = "Resposta incorreta!"
                jogo.save()
                return JsonResponse({'status': 'error', 'message': 'Resposta incorreta!'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

@csrf_exempt
def questao(request):
    if request.method == "POST":
        return criar_questao(request)
    elif request.method == "GET":
        return listar_questao(request)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método não permitido.'}, status=405)


@csrf_exempt
def questao_id(request, id=None):
    if request.method == "GET":
        return listar_questao(request,id)
    elif request.method == "DELETE":
        return deletar_questao(request,id)
    elif request.method == "PATCH":
        return atualizar_questao(request,id)
    elif request.method == "PUT":
        return atualizar_questao(request,id)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método não permitido.'}, status=405)

def criar_questao(request):
    try:
        # Tenta carregar o corpo da requisição como JSON
        data = json.loads(request.body)
        
        # Verifica se o dado é uma lista ou um único dicionário
        if isinstance(data, list):
            questoes = data
        else:
            questoes = [data]  # Envolve o dicionário em uma lista

        erros = []
        for questao_data in questoes:
            form = CriarQuestaoForm(questao_data)
            if form.is_valid():
                form.save()
            else:
                erros.append(form.errors)

        if erros:
            return erro_response('Erros de validação', 400)
        return json_response({'status': 'success', 'message': 'Todas as questões foram criadas com sucesso!'})
    except:
        return erro_response('JSON inválido', 400)

def deletar_questao(request, id=None):
    try:
        if id:
            questao = get_object_or_404(Questao, id=id)
            questao.delete()
            return json_response({'status': 'success', 'message': 'Questão deletada com sucesso!'})
        else:
            return erro_response('ID da questão não fornecido', 400)
    except Exception as e:
        return erro_response(str(e), 400)

def atualizar_questao(request,id):
    try:
        if not id:
            return erro_response('ID da questão não fornecido', 400)
        
        data = json.loads(request.body)
        questao = get_object_or_404(Questao, id=id)
        
        for field in ['enunciado', 'respostas', 'resposta_correta']:
            if field in data:
                setattr(questao, field, data[field])
        questao.save()
        return json_response({'status': 'success', 'message': 'Questão atualizada com sucesso!'})
    
    except Exception as e:
        return erro_response(str(e), 400)

def listar_questao(request, id=None):
    if id:
        questao = get_object_or_404(Questao, id=id)
        return json_response(formatar_questao(questao))
    else:
        questoes = Questao.objects.all()
        return json_response([formatar_questao(questao) for questao in questoes])


@csrf_exempt
def jogo(request):
    if request.method == "POST":
        return criar_jogo(request)
    elif request.method == "GET":
        return listar_jogo(request)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método não permitido.'}, status=405)


@csrf_exempt
def jogo_id(request, id):
    if request.method == "GET":
        return listar_jogo(request,id)
    elif request.method == "PUT":
        return atualizar_jogo(request,id)
    
    elif request.method == "PATCH":
        return atualizar_jogo(request,id)
    
    elif request.method == "DELETE":
        return deletar_jogo(request,id)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método não permitido.'}, status=405)


def criar_jogo(request):
    try:
        data=json.loads(request.body)
        form = CriarJogoForm(data)
        if form.is_valid():
            questoes_ids = data.get('questoes')
            jogo = form.save(commit=False)
            jogo.questoes = questoes_ids
            jogo.save()
            return JsonResponse({'status': 'success', 'message': 'Jogo criado com sucesso!'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    except json.JSONDecodeError:
        return erro_response('JSON inválido', 400)

def deletar_jogo(request, id=None):
    try:
        if id:
            jogo = get_object_or_404(Jogo, id=id)
            jogo.delete()
            return json_response({'status': 'success', 'message': 'Jogo deletado com sucesso!'})
        else:
            return erro_response('ID do jogo não fornecido', 400)
    except Exception as e:
        return erro_response(str(e), 400)

        
def atualizar_jogo(request,id=None):
    try:
        if not id:
            return erro_response('ID do jogo não fornecido', 400)
        
        data = json.loads(request.body)
        jogo = get_object_or_404(Jogo, id=id)
        
        if request.method == "PUT":
            for field in ['nome', 'questoes', 'time_a_pontos', 'time_b_pontos', 'time_c_pontos', 'time_d_pontos']:
                if field in data:
                    setattr(jogo, field, data[field])
                
            jogo.save()
            return json_response({'status': 'success', 'message': 'Jogo atualizado com sucesso!'})
        
        elif request.method == "PATCH":
            for field, value in data.items():
                if hasattr(jogo, field):
                    setattr(jogo, field, value)
            jogo.save()
            return json_response({'status': 'success', 'message': 'Jogo parcialmente atualizado com sucesso!'})
        
        else:
            return erro_response('Método não permitido.', 405)
    
    except Exception as e:
        return erro_response(str(e), 400)

def listar_jogo(request,id=None):
    if id:
        jogo = get_object_or_404(Jogo, id=id)
        return json_response(formatar_jogo(jogo))
    else:
        jogos = Jogo.objects.all()
        return json_response([formatar_jogo(jogo) for jogo in jogos])


