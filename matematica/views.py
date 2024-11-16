from django.shortcuts import render
from sympy import symbols, sympify, diff, integrate, SympifyError, lambdify
from .models import Calcolo, SteamReformerCalcolo
import time
import matplotlib
matplotlib.use('Agg')  # Utilizza un backend senza interfaccia grafica
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from .serializers import CalcoloSerializer, SteamReformerCalcoloSerializer
from django.contrib import messages
from .utils import calcola_rapporto_vapore_carbonio, calcola_calore_di_reazione
from .forms import SteamReformerForm

def calcolatore_view(request):
    # La tua implementazione attuale
    risultato = ''
    graph = ''
    if request.method == 'POST':
        espressione = request.POST.get('espressione')
        operazione = request.POST.get('operazione')
        start_time = time.time()
        try:
            x = symbols('x')
            funzione = sympify(espressione)
            if operazione == 'derivata':
                risultato_sympy = diff(funzione, x)
                risultato = str(risultato_sympy)

                # Generazione del grafico per la derivata
                try:
                    f_num = lambdify(x, funzione, modules=['numpy'])
                    f_prime_num = lambdify(x, risultato_sympy, modules=['numpy'])
                    x_vals = np.linspace(-10, 10, 400)
                    y_vals = f_num(x_vals)
                    y_prime_vals = f_prime_num(x_vals)

                    fig, ax = plt.subplots()
                    ax.plot(x_vals, y_vals, label='f(x)')
                    ax.plot(x_vals, y_prime_vals, label="f'(x)")
                    ax.set_xlabel('x')
                    ax.set_ylabel('y')
                    ax.set_title("Grafico di f(x) e f'(x)")
                    ax.legend()

                    buffer = BytesIO()
                    plt.savefig(buffer, format='png')
                    buffer.seek(0)
                    image_png = buffer.getvalue()
                    buffer.close()
                    graph = base64.b64encode(image_png).decode('utf-8')
                    plt.close(fig)
                except Exception as e:
                    graph = ''
                    risultato += f" Errore durante la generazione del grafico: {str(e)}"

            elif operazione == 'integrale':
                risultato_sympy = integrate(funzione, x)
                risultato = str(risultato_sympy)

                # Generazione del grafico per l'integrale
                try:
                    f_num = lambdify(x, funzione, modules=['numpy'])
                    F_num = lambdify(x, risultato_sympy, modules=['numpy'])
                    x_vals = np.linspace(-10, 10, 400)
                    y_vals = f_num(x_vals)
                    y_int_vals = F_num(x_vals)

                    fig, ax = plt.subplots()
                    ax.plot(x_vals, y_vals, label='f(x)')
                    ax.plot(x_vals, y_int_vals, label='∫f(x)dx')
                    ax.set_xlabel('x')
                    ax.set_ylabel('y')
                    ax.set_title('Grafico di f(x) e ∫f(x)dx')
                    ax.legend()

                    buffer = BytesIO()
                    plt.savefig(buffer, format='png')
                    buffer.seek(0)
                    image_png = buffer.getvalue()
                    buffer.close()
                    graph = base64.b64encode(image_png).decode('utf-8')
                    plt.close(fig)
                except Exception as e:
                    graph = ''
                    risultato += f" Errore durante la generazione del grafico: {str(e)}"

            else:
                # Per altre operazioni che non prevedono il grafico
                risultato = 'Operazione non valida o non supportata per il grafico.'
                graph = ''

            end_time = time.time()
            tempo_calcolo = end_time - start_time

            # Salva il calcolo nel database
            calcolo = Calcolo.objects.create(
                espressione=espressione,
                operazione=operazione,
                risultato=risultato,
                tempo_calcolo=tempo_calcolo
            )
            calcolo.save()

        except SympifyError:
            risultato = 'Espressione non valida.'
            graph = ''
        except Exception as e:
            risultato = f'Errore durante il calcolo: {str(e)}'
            graph = ''
    else:
        graph = ''

    # Recupera gli ultimi 10 calcoli dal database
    calcoli = Calcolo.objects.order_by('-data')[:10]

    return render(request, 'calcolatore.html', {'risultato': risultato, 'calcoli': calcoli, 'graph': graph})

def steam_reformer_view(request):
    risultato = {}
    graph = ''
    if request.method == 'POST':
        form = SteamReformerForm(request.POST)
        if form.is_valid():
            portata_molare_idrocarburo = form.cleaned_data['portata_molare_idrocarburo']
            portata_molare_vapore = form.cleaned_data['portata_molare_vapore']
            entalpia_prodotti = form.cleaned_data['entalpia_prodotti']
            entalpia_reagenti = form.cleaned_data['entalpia_reagenti']
            quantita_molare = form.cleaned_data['quantita_molare']
            
            start_time = time.time()

            try:
                # Esegui i calcoli
                rapporto = calcola_rapporto_vapore_carbonio(portata_molare_idrocarburo, portata_molare_vapore)
                calore_reazione = calcola_calore_di_reazione(entalpia_prodotti, entalpia_reagenti, quantita_molare)
                
                risultato = {
                    'rapporto_vapore_carbonio': rapporto,
                    'calore_di_reazione': calore_reazione,
                }
                
                # Genera un grafico semplice
                x = [0, 1, 2, 3, 4, 5]
                y = [0, calore_reazione, calore_reazione * 2, calore_reazione * 3, calore_reazione * 4, calore_reazione * 5]
                
                plt.figure()
                plt.plot(x, y, marker='o')
                plt.title('Calore di Reazione nel Tempo')
                plt.xlabel('Tempo (s)')
                plt.ylabel('Calore di Reazione (kJ)')
                
                buffer = BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                image_png = buffer.getvalue()
                graph = base64.b64encode(image_png).decode()
                buffer.close()
                plt.close()
                
                # Salva il calcolo nel database
                calcolo = SteamReformerCalcolo.objects.create(
                    portata_molare_idrocarburo=portata_molare_idrocarburo,
                    portata_molare_vapore=portata_molare_vapore,
                    entalpia_prodotti=entalpia_prodotti,
                    entalpia_reagenti=entalpia_reagenti,
                    quantita_molare=quantita_molare,
                    rapporto_vapore_carbonio=rapporto,
                    calore_di_reazione=calore_reazione,
                    tempo_calcolo=time.time() - start_time
                )
                
                messages.success(request, 'Calcoli eseguiti con successo!')
            except ValueError as ve:
                risultato = {}
                graph = ''
                messages.error(request, str(ve))
            except Exception as e:
                risultato = {}
                graph = ''
                messages.error(request, f'Errore durante il calcolo: {str(e)}')
        else:
            messages.error(request, 'Dati del form non validi.')
    else:
        form = SteamReformerForm()
    
    # Recupera gli ultimi 10 calcoli
    calcoli = SteamReformerCalcolo.objects.all().order_by('-data')[:10]
    
    return render(request, 'steam_reformer.html', {
        'form': form,
        'risultato': risultato,
        'calcoli': calcoli,
        'graph': graph
    })

@csrf_exempt
@api_view(['POST'])
def calcolatore_api(request):
    espressione = request.data.get('espressione')
    operazione = request.data.get('operazione')

    risultato = ''
    try:
        x = symbols('x')
        funzione = sympify(espressione)
        start_time = time.time()

        if operazione == 'derivata':
            risultato_sympy = diff(funzione, x)
            risultato = str(risultato_sympy)
        elif operazione == 'integrale':
            risultato_sympy = integrate(funzione, x)
            risultato = str(risultato_sympy)
        else:
            return Response({'errore': 'Operazione non supportata.'}, status=400)

        end_time = time.time()
        tempo_calcolo = end_time - start_time

        # Salva il calcolo nel database
        calcolo = Calcolo.objects.create(
            espressione=espressione,
            operazione=operazione,
            risultato=risultato,
            tempo_calcolo=tempo_calcolo
        )
        calcolo.save()

        # Serializza e restituisci il risultato
        serializer = CalcoloSerializer(calcolo)
        return Response(serializer.data, status=200)

    except SympifyError:
        return Response({'errore': 'Espressione non valida.'}, status=400)
    except Exception as e:
        return Response({'errore': f'Errore durante il calcolo: {str(e)}'}, status=500)

@csrf_exempt
@api_view(['POST'])
def steam_reformer_api(request):
    data = request.data
    required_fields = [
        'portata_molare_idrocarburo',
        'portata_molare_vapore',
        'entalpia_prodotti',
        'entalpia_reagenti',
        'quantita_molare'
    ]
    
    # Verifica che tutti i campi richiesti siano presenti
    for field in required_fields:
        if field not in data:
            return Response({'error': f'Manca il campo: {field}'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        portata_molare_idrocarburo = float(data['portata_molare_idrocarburo'])
        portata_molare_vapore = float(data['portata_molare_vapore'])
        entalpia_prodotti = float(data['entalpia_prodotti'])
        entalpia_reagenti = float(data['entalpia_reagenti'])
        quantita_molare = float(data['quantita_molare'])
    except ValueError:
        return Response({'error': 'I campi devono essere numerici.'}, status=status.HTTP_400_BAD_REQUEST)
    
    start_time = time.time()
    
    try:
        # Esegui i calcoli
        rapporto = calcola_rapporto_vapore_carbonio(portata_molare_idrocarburo, portata_molare_vapore)
        calore_reazione = calcola_calore_di_reazione(entalpia_prodotti, entalpia_reagenti, quantita_molare)
        
        # Genera un grafico
        x_vals = [0, 1, 2, 3, 4, 5]
        y_vals = [0, float(calore_reazione), float(calore_reazione)*2, float(calore_reazione)*3, float(calore_reazione)*4, float(calore_reazione)*5]
        
        plt.figure()
        plt.plot(x_vals, y_vals, marker='o')
        plt.title('Calore di Reazione nel Tempo')
        plt.xlabel('Tempo (s)')
        plt.ylabel('Calore di Reazione (kJ)')
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        graph = base64.b64encode(image_png).decode()
        buffer.close()
        plt.close()
        
        # Salva il calcolo nel database
        calcolo = SteamReformerCalcolo.objects.create(
            portata_molare_idrocarburo=portata_molare_idrocarburo,
            portata_molare_vapore=portata_molare_vapore,
            entalpia_prodotti=entalpia_prodotti,
            entalpia_reagenti=entalpia_reagenti,
            quantita_molare=quantita_molare,
            rapporto_vapore_carbonio=rapporto,
            calore_di_reazione=calore_reazione,
            tempo_calcolo=time.time() - start_time
        )
        
        serializer = SteamReformerCalcoloSerializer(calcolo)
        response_data = serializer.data
        response_data['graph'] = graph  # Aggiunge il grafico in base64
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def steam_reformer_calcoli_api(request):
    calcoli = SteamReformerCalcolo.objects.all().order_by('-data')[:10]
    serializer = SteamReformerCalcoloSerializer(calcoli, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
