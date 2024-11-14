from django.shortcuts import render
from sympy import symbols, sympify, diff, integrate, Eq, dsolve, solve, Function, lambdify
from sympy.core.sympify import SympifyError
from .models import Calcolo
import time

import matplotlib
matplotlib.use('Agg')  # Imposta il backend di Matplotlib per l'ambiente senza interfaccia grafica

import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CalcoloSerializer

def calcolatore_view(request):
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

@api_view(['POST'])
def calcolatore_api(request):
    if request.method == 'POST':
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
