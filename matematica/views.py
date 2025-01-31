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
import pybobyqa
from .models import BOBYQACalcolo
from .forms import BOBYQAForm
from .forms import SteamReformerSimulationForm
from .forms import ElectricSteamReformerSimulationForm
from .models import ElectricSteamReformerSimulation
from .forms import VesselForm
from .models import VesselSimulation
from scipy.integrate import solve_ivp
import plotly.offline as opy
import plotly.graph_objs as go
from .models import SteamReformerSimulation
import logging
import json
from django.http import JsonResponse
logger = logging.getLogger(__name__)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import EquationPart, EquationTestResult
from .forms import EquationPartForm, EquationPartTestForm
from .utils import execute_equation_part
import json
import time

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

def bobyqa_view(request):
    risultato = ''
    tempo_calcolo = 0
    if request.method == 'POST':
        form = BOBYQAForm(request.POST)
        if form.is_valid():
            x0_input = form.cleaned_data['x0']
            try:
                # Converte la stringa di input in un array numpy
                x0_list = [float(x.strip()) for x in x0_input.split(',')]
                x0 = np.array(x0_list)

                # Definisce la funzione obiettivo (Rosenbrock)
                def rosenbrock(x):
                    return 100.0 * (x[1] - x[0] ** 2) ** 2 + (1.0 - x[0]) ** 2

                # Esegue il calcolo e misura il tempo
                start_time = time.time()
                soln = pybobyqa.solve(rosenbrock, x0)
                end_time = time.time()
                tempo_calcolo = end_time - start_time

                # Salva il calcolo nel database
                calcolo = BOBYQACalcolo.objects.create(
                    x0=str(x0_input),
                    risultato=str(soln),
                    tempo_calcolo=tempo_calcolo
                )
                calcolo.save()

                risultato = soln
                messages.success(request, 'Calcolo eseguito con successo!')
            except Exception as e:
                messages.error(request, f'Errore durante il calcolo: {str(e)}')
                risultato = ''
        else:
            messages.error(request, 'Dati del form non validi.')
    else:
        form = BOBYQAForm()

    # Recupera gli ultimi 10 calcoli
    calcoli = BOBYQACalcolo.objects.all().order_by('-data')[:10]

    return render(request, 'bobyqa.html', {
        'form': form,
        'risultato': risultato,
        'tempo_calcolo': tempo_calcolo,
        'calcoli': calcoli
    })


    risultato = None
    tempo_calcolo = 0
    graph_div = None  # Variabile per il grafico interattivo

    if request.method == 'POST':
        form = SteamReformerSimulationForm(request.POST)
        if form.is_valid():
            # Estrae i dati dal form
            P = form.cleaned_data['pressione']
            T0 = form.cleaned_data['temperatura_iniziale']
            y_CH4_0 = form.cleaned_data['frazione_molare_CH4']
            y_H2O_0 = form.cleaned_data['frazione_molare_H2O']
            W = form.cleaned_data['peso_catalizzatore']
            F_tot = form.cleaned_data['flusso_molare_totale']

            # Assicura che le frazioni molari sommino a 1
            y_sum = y_CH4_0 + y_H2O_0
            y_CH4_0 /= y_sum
            y_H2O_0 /= y_sum

            # Frazioni molari iniziali per gli altri componenti
            y_CO_0 = 0.0
            y_CO2_0 = 0.0
            y_H2_0 = 0.0

            y0 = np.array([y_CH4_0, y_H2O_0, y_CO_0, y_CO2_0, y_H2_0, T0])

            try:
                # Risoluzione delle ODE
                start_time = time.time()
                sol = solve_ivp(
                    lambda z, y_vars: model(z, y_vars, P, T0, W, F_tot),
                    [0, W],
                    y0,
                    method='RK45',
                    t_eval=np.linspace(0, W, 100)
                )
                end_time = time.time()
                tempo_calcolo = end_time - start_time

                # Prepara i risultati per la visualizzazione
                risultato = {
                    'z': sol.t.tolist(),
                    'y': sol.y.tolist()
                }

                # Genera il grafico interattivo con Plotly
                z = sol.t  # Posizione lungo il reattore
                y = sol.y  # Frazioni molari dei componenti

                # Nomi dei componenti
                component_names = ['CH₄', 'H₂O', 'CO', 'CO₂', 'H₂']

                # Crea le tracce per ogni componente
                traces = []
                for i in range(5):
                    trace = go.Scatter(
                        x=z,
                        y=y[i],
                        mode='lines',
                        name=component_names[i]
                    )
                    traces.append(trace)

                layout = go.Layout(
                    title='Profili di Concentrazione lungo il Reattore',
                    xaxis=dict(title='Peso del Catalizzatore (kg)'),
                    yaxis=dict(title='Frazione Molare'),
                    hovermode='closest'
                )

                fig = go.Figure(data=traces, layout=layout)
                graph_div = opy.plot(fig, auto_open=False, output_type='div')

                # Salva la simulazione nel database
                simulazione = SteamReformerSimulation.objects.create(
                    pressione=P,
                    temperatura_iniziale=T0,
                    frazione_molare_CH4=y_CH4_0,
                    frazione_molare_H2O=y_H2O_0,
                    peso_catalizzatore=W,
                    flusso_molare_totale=F_tot,
                    risultato=str(risultato),
                    tempo_calcolo=tempo_calcolo
                )
                simulazione.save()
                messages.success(request, 'Simulazione eseguita con successo!')
            except Exception as e:
                messages.error(request, f'Errore durante la simulazione: {str(e)}')
                risultato = None
        else:
            messages.error(request, 'Dati del form non validi.')
    else:
        form = SteamReformerSimulationForm()

    # Recupera le ultime simulazioni
    simulazioni = SteamReformerSimulation.objects.all().order_by('-data')[:10]

    return render(request, 'steam_reformer_simulation.html', {
        'form': form,
        'risultato': risultato,
        'tempo_calcolo': tempo_calcolo,
        'simulazioni': simulazioni,
        'graph_div': graph_div
    })

# Definisci le costanti di equilibrio
def equilibrium_constants(T):
    # T in Kelvin
    K_SR = np.exp(19088 / T - 19.36)     # Steam Reforming
    K_WGS = np.exp(4400 / T - 4.07)      # Water Gas Shift
    K_Met = np.exp(-11680 / T + 13.65)   # Metanazione
    return np.array([K_SR, K_WGS, K_Met])

# Definisci le velocità di reazione
def reaction_rates(P, T, y):
    # P: pressione totale (Pa)
    # T: temperatura (K)
    # y: frazioni molari (array)

    # Costanti cinetiche (esempio, da adattare con dati reali)
    k_SR = 1e5 * np.exp(-24000 / (8.314 * T))    # Steam Reforming
    k_WGS = 1e3 * np.exp(-20000 / (8.314 * T))   # Water Gas Shift
    k_Met = 1e2 * np.exp(-22000 / (8.314 * T))   # Metanazione

    # Pressioni parziali (Pa)
    p = y * P

    # Velocità di reazione (mol/kg_cat·s)
    r_SR = k_SR * p[0] * p[1]  # CH4 * H2O
    r_WGS = k_WGS * p[2] * p[1]  # CO * H2O
    r_Met = k_Met * p[2] * p[4]**3  # CO * H2^3

    return np.array([r_SR, r_WGS, r_Met])

# Definisci la funzione modello per le ODE
def model(z, y_vars, P, W, F_tot):
    # z: posizione lungo il reattore (kg di catalizzatore)
    # y_vars: array contenente le frazioni molari [y_CH4, y_H2O, y_CO, y_CO2, y_H2, T]
    # P: pressione totale (Pa)
    # W: peso totale del catalizzatore (kg)
    # F_tot: flusso molare totale (mol/s)

    y = y_vars[:5]  # Frazioni molari
    T = y_vars[5]   # Temperatura (K)

    # Matrice stechiometrica (componenti x reazioni)
    nu = np.array([
        [-1,  0,  1],  # CH4
        [-1, -1,  1],  # H2O
        [ 1, -1, -1],  # CO
        [ 0,  1, -1],  # CO2
        [ 3,  1, -3],  # H2
    ])

    # Calcolo delle costanti di equilibrio
    K_eq = equilibrium_constants(T)

    # Calcolo delle velocità di reazione
    rates = reaction_rates(P, T, y)

    # Bilancio molare per ogni componente
    dydz = np.zeros(6)
    for i in range(5):  # Per ogni componente
        dydz[i] = np.dot(nu[i, :], rates) / F_tot

    # Bilancio energetico (semplificato)
    delta_H = np.array([206000, -41000, -206000])  # J/mol
    Q = np.dot(delta_H, rates)  # Calore di reazione totale (J/kg_cat·s)

    Cp_tot = 100  # J/mol·K (approssimato)
    dydz[5] = -Q / (F_tot * Cp_tot)

    return dydz

def electric_model(z, y_vars, P, W, F_tot, P_elettrica):
    y = y_vars[:5]  # Frazioni molari
    T = y_vars[5]   # Temperatura (K)

    # Matrice stechiometrica
    nu = np.array([
        [-1,  0,  1],  # CH₄
        [-1, -1,  1],  # H₂O
        [ 1, -1, -1],  # CO
        [ 0,  1, -1],  # CO₂
        [ 3,  1, -3],  # H₂
    ])

    # Calcolo delle costanti di equilibrio
    K_eq = equilibrium_constants(T)

    # Calcolo delle velocità di reazione
    rates = reaction_rates(P, T, y)

    # Bilancio molare
    dydz = np.zeros(6)
    for i in range(5):
        dydz[i] = np.dot(nu[i, :], rates) / F_tot

    # Bilancio energetico con riscaldamento elettrico
    delta_H = np.array([206000, -41000, -206000])  # J/mol
    Q_reazione = np.dot(delta_H, rates)  # J/kg_cat·s

    # Calore fornito elettricamente per unità di peso del catalizzatore
    Q_elettrico = P_elettrica / W  # W/kg_cat = J/s·kg_cat

    Cp_tot = 100  # J/mol·K (approssimato)
    dydz[5] = (-Q_reazione + Q_elettrico) / (F_tot * Cp_tot)

    return dydz

def steam_reformer_simulation_view(request):
    risultato = None
    tempo_calcolo = 0
    plot_html = ""  # Per il grafico interattivo
    results = []  # Lista per i risultati finali

    if request.method == 'POST':
        form = SteamReformerSimulationForm(request.POST)
        if form.is_valid():
            try:
                # Estrazione dei dati dal form
                P = form.cleaned_data['pressione']
                T0 = form.cleaned_data['temperatura_iniziale']
                y_CH4_0 = form.cleaned_data['frazione_molare_CH4']
                y_H2O_0 = form.cleaned_data['frazione_molare_H2O']
                W = form.cleaned_data['peso_catalizzatore']
                F_tot = form.cleaned_data['flusso_molare_totale']

                # Verifica che le frazioni molari siano valide
                if y_CH4_0 + y_H2O_0 > 1.0:
                    messages.error(request, 'La somma delle frazioni molari non può superare 1.0.')
                    return render(request, 'steam_reformer_simulation.html', {
                        'form': form,
                        'tempo_calcolo': tempo_calcolo,
                        'plot_html': plot_html
                    })

                # Altre frazioni molari iniziali
                y_CO_0 = 0.0
                y_CO2_0 = 0.0
                y_H2_0 = 1.0 - y_CH4_0 - y_H2O_0  # Il resto della frazione molare

                y0 = np.array([y_CH4_0, y_H2O_0, y_CO_0, y_CO2_0, y_H2_0, T0])

                # Risoluzione delle ODE
                start_time = time.time()
                sol = solve_ivp(
                    lambda z, y_vars: model(z, y_vars, P, W, F_tot),
                    [0, W],
                    y0,
                    method='BDF',
                    t_eval=np.linspace(0, W, 50),
                    max_step=1.0
                )
                end_time = time.time()
                tempo_calcolo = end_time - start_time

                if not sol.success:
                    messages.error(request, f'Errore durante l\'integrazione: {sol.message}')
                    return render(request, 'steam_reformer_simulation.html', {
                        'form': form,
                        'tempo_calcolo': tempo_calcolo,
                        'plot_html': plot_html
                    })

                # Prepara i risultati
                risultato = {
                    'z': sol.t.tolist(),
                    'y': sol.y.tolist()
                }

                # Genera il grafico interattivo con Plotly
                fig = go.Figure()

                componenti = ['CH₄', 'H₂O', 'CO', 'CO₂', 'H₂']
                for i, componente in enumerate(componenti):
                    fig.add_trace(go.Scatter(
                        x=sol.t,
                        y=sol.y[i],
                        mode='lines',
                        name=componente
                    ))

                fig.update_layout(
                    title="Concentrazioni lungo il reattore",
                    xaxis_title="Peso del Catalizzatore (kg)",
                    yaxis_title="Frazione Molare",
                    template="plotly_white"
                )

                plot_html = fig.to_html(full_html=False)

                # Prepara i risultati finali per il template
                results = []
                for i, componente in enumerate(componenti):
                    final_value = sol.y[i][-1]
                    results.append({'component': componente, 'value': final_value})

                # Salva i dati nel database
                simulazione = SteamReformerSimulation.objects.create(
                    pressione=P,
                    temperatura_iniziale=T0,
                    frazione_molare_CH4=y_CH4_0,
                    frazione_molare_H2O=y_H2O_0,
                    peso_catalizzatore=W,
                    flusso_molare_totale=F_tot,
                    risultato=str(risultato),
                    tempo_calcolo=tempo_calcolo
                )
                simulazione.save()
            except Exception as e:
                messages.error(request, f'Errore durante la simulazione: {str(e)}')
        else:
            messages.error(request, 'Dati del form non validi.')
    else:
        form = SteamReformerSimulationForm()

    # Recupera le ultime simulazioni
    simulazioni = SteamReformerSimulation.objects.all().order_by('-data')[:10]

    return render(request, 'steam_reformer_simulation.html', {
        'form': form,
        'risultato': risultato,
        'tempo_calcolo': tempo_calcolo,
        'simulazioni': simulazioni,
        'plot_html': plot_html,
        'results': results
    })

    risultato = None
    tempo_calcolo = 0
    plot_html = ""  # Per il grafico interattivo

    if request.method == 'POST':
        form = SteamReformerSimulationForm(request.POST)
        if form.is_valid():
            try:
                # Estrazione dei dati dal form
                P = form.cleaned_data['pressione']
                T0 = form.cleaned_data['temperatura_iniziale']
                y_CH4_0 = form.cleaned_data['frazione_molare_CH4']
                y_H2O_0 = form.cleaned_data['frazione_molare_H2O']
                W = form.cleaned_data['peso_catalizzatore']
                F_tot = form.cleaned_data['flusso_molare_totale']

                # Verifica che le frazioni molari siano valide
                if y_CH4_0 + y_H2O_0 > 1.0:
                    messages.error(request, 'La somma delle frazioni molari non può superare 1.0.')
                    return render(request, 'steam_reformer_simulation.html', {
                        'form': form,
                        'tempo_calcolo': tempo_calcolo,
                        'plot_html': plot_html
                    })

                # Altre frazioni molari iniziali
                y_CO_0 = 0.0
                y_CO2_0 = 0.0
                y_H2_0 = 1.0 - y_CH4_0 - y_H2O_0  # Il resto della frazione molare

                y0 = np.array([y_CH4_0, y_H2O_0, y_CO_0, y_CO2_0, y_H2_0, T0])

                # Risoluzione delle ODE
                start_time = time.time()
                sol = solve_ivp(
                    lambda z, y_vars: model(z, y_vars, P, W, F_tot),
                    [0, W],
                    y0,
                    #method='RK45',
                    method='BDF',
                    t_eval=np.linspace(0, W, 100)
                )
                end_time = time.time()
                tempo_calcolo = end_time - start_time
                
                logger.debug(f"Soluzione integratore: success={sol.success}, message={sol.message}")
                if not sol.success:
                    messages.error(request, f"Errore durante l'integrazione: {sol.message}")
                    # Aggiungi un return qui per interrompere l'esecuzione
                    return render(request, 'steam_reformer_simulation.html', {
                        'form': form,
                        'tempo_calcolo': tempo_calcolo,
                        'simulazioni': simulazioni,
                        # Aggiungi 'messages' al contesto
                    })

                # Prepara i risultati
                risultato = {
                    'z': sol.t.tolist(),
                    'y': sol.y.tolist()
                }

                # Genera il grafico interattivo con Plotly
                fig = go.Figure()

                componenti = ['CH₄', 'H₂O', 'CO', 'CO₂', 'H₂']
                for i, componente in enumerate(componenti):
                    fig.add_trace(go.Scatter(
                        x=sol.t,
                        y=sol.y[i],
                        mode='lines',
                        name=componente
                    ))

                fig.update_layout(
                    title="Concentrazioni lungo il reattore",
                    xaxis_title="Peso del Catalizzatore (kg)",
                    yaxis_title="Frazione Molare",
                    template="plotly_dark"
                )

                plot_html = fig.to_html(full_html=False)

                # Salva i dati nel database
                simulazione = SteamReformerSimulation.objects.create(
                    pressione=P,
                    temperatura_iniziale=T0,
                    frazione_molare_CH4=y_CH4_0,
                    frazione_molare_H2O=y_H2O_0,
                    peso_catalizzatore=W,
                    flusso_molare_totale=F_tot,
                    risultato=str(risultato),
                    tempo_calcolo=tempo_calcolo
                )
                simulazione.save()
            except Exception as e:
                messages.error(request, f'Errore durante la simulazione: {str(e)}')
        else:
            messages.error(request, 'Dati del form non validi.')
    else:
        form = SteamReformerSimulationForm()

    # Recupera le ultime simulazioni
    simulazioni = SteamReformerSimulation.objects.all().order_by('-data')[:10]
    componenti = ['CH₄', 'H₂O', 'CO', 'CO₂', 'H₂']
    range_risultato = range(len(componenti))
    return render(request, 'steam_reformer_simulation.html', {
        'form': form,
        'risultato': risultato,
        'tempo_calcolo': tempo_calcolo,
        'simulazioni': simulazioni,
        'plot_html': plot_html
    })

def electric_steam_reformer_simulation_view(request):
    risultato = None
    tempo_calcolo = 0
    plot_html = ""

    if request.method == 'POST':
        form = ElectricSteamReformerSimulationForm(request.POST)
        if form.is_valid():
            try:
                # Estrazione dei dati dal form
                P = form.cleaned_data['pressione']
                T0 = form.cleaned_data['temperatura_iniziale']
                y_CH4_0 = form.cleaned_data['frazione_molare_CH4']
                y_H2O_0 = form.cleaned_data['frazione_molare_H2O']
                W = form.cleaned_data['peso_catalizzatore']
                F_tot = form.cleaned_data['flusso_molare_totale']
                P_elettrica = form.cleaned_data['potenza_elettrica']

                # Verifica delle frazioni molari
                if y_CH4_0 + y_H2O_0 > 1.0:
                    messages.error(request, 'La somma delle frazioni molari non può superare 1.0.')
                    return render(request, 'electric_steam_reformer_simulation.html', {'form': form})

                # Altre frazioni molari iniziali
                y_CO_0 = 0.0
                y_CO2_0 = 0.0
                y_H2_0 = 1.0 - y_CH4_0 - y_H2O_0

                y0 = np.array([y_CH4_0, y_H2O_0, y_CO_0, y_CO2_0, y_H2_0, T0])

                # Risoluzione delle ODE
                start_time = time.time()
                sol = solve_ivp(
                    lambda z, y_vars: electric_model(z, y_vars, P, W, F_tot, P_elettrica),
                    [0, W],
                    y0,
                    method='BDF',
                    t_eval=np.linspace(0, W, 50),
                    max_step=1.0
                )
                end_time = time.time()
                tempo_calcolo = end_time - start_time

                if not sol.success:
                    messages.error(request, f"Errore durante l'integrazione: {sol.message}")
                    return render(request, 'electric_steam_reformer_simulation.html', {'form': form})

                # Prepara i risultati
                risultato = {
                    'z': sol.t.tolist(),
                    'y': sol.y.tolist()
                }

                # Genera il grafico
                fig = go.Figure()

                componenti = ['CH₄', 'H₂O', 'CO', 'CO₂', 'H₂']
                for i, componente in enumerate(componenti):
                    fig.add_trace(go.Scatter(
                        x=sol.t,
                        y=sol.y[i],
                        mode='lines',
                        name=componente
                    ))

                fig.update_layout(
                    title="Concentrazioni lungo il reattore",
                    xaxis_title="Peso del Catalizzatore (kg)",
                    yaxis_title="Frazione Molare",
                    template="plotly_white"
                )

                plot_html = fig.to_html(full_html=False)

                # Prepara i risultati finali per il template
                results = []
                for i, componente in enumerate(componenti):
                    final_value = sol.y[i][-1]
                    results.append({'component': componente, 'value': final_value})

                # Salva la simulazione nel database
                simulazione = ElectricSteamReformerSimulation.objects.create(
                    pressione=P,
                    temperatura_iniziale=T0,
                    frazione_molare_CH4=y_CH4_0,
                    frazione_molare_H2O=y_H2O_0,
                    peso_catalizzatore=W,
                    flusso_molare_totale=F_tot,
                    potenza_elettrica=P_elettrica,
                    risultato=str(risultato),
                    tempo_calcolo=tempo_calcolo
                )
                simulazione.save()

            except Exception as e:
                messages.error(request, f'Errore durante la simulazione: {str(e)}')
                return render(request, 'electric_steam_reformer_simulation.html', {'form': form})

        else:
            messages.error(request, 'Dati del form non validi.')
            return render(request, 'electric_steam_reformer_simulation.html', {'form': form})

    else:
        form = ElectricSteamReformerSimulationForm()

    # Recupera le ultime simulazioni
    simulazioni = ElectricSteamReformerSimulation.objects.all().order_by('-data')[:10]

    return render(request, 'electric_steam_reformer_simulation.html', {
        'form': form,
        'risultato': risultato,
        'tempo_calcolo': tempo_calcolo,
        'simulazioni': simulazioni,
        'plot_html': plot_html,
        'results': results if 'results' in locals() else None
    })

def vessel_calculation(P, D, S, E):
    R = D / 2.0
    denom = (S * E) - (0.6 * P)
    if denom <= 0:
        raise ValueError("Parametri non validi. Verificare i valori.")
    t = (P * R) / denom
    return t

def vessel_simulation_view(request):
    risultato = None
    tempo_calcolo = 0

    if request.method == 'POST':
        form = VesselForm(request.POST)
        if form.is_valid():
            try:
                P = form.cleaned_data['pressione']
                D = form.cleaned_data['diametro']
                S = form.cleaned_data['tensione_ammissibile']
                E = form.cleaned_data['efficienza_giunto']

                start_time = time.time()
                t = vessel_calculation(P, D, S, E)
                end_time = time.time()
                tempo_calcolo = end_time - start_time

                risultato = {
                    'spessore': t,
                    'input': {
                        'pressione': P,
                        'diametro': D,
                        'tensione_ammissibile': S,
                        'efficienza_giunto': E
                    }
                }

                # Salvataggio nel database
                simulazione = VesselSimulation.objects.create(
                    pressione=P,
                    diametro=D,
                    tensione_ammissibile=S,
                    efficienza_giunto=E,
                    risultato=json.dumps(risultato),
                    tempo_calcolo=tempo_calcolo
                )
                simulazione.save()

            except Exception as e:
                messages.error(request, f'Errore durante il calcolo: {str(e)}')
                form = VesselForm()
        else:
            messages.error(request, 'Dati del form non validi.')
    else:
        form = VesselForm()

    simulazioni = VesselSimulation.objects.all().order_by('-data')[:10]

    return render(request, 'vessel_simulation.html', {
        'form': form,
        'risultato': risultato,
        'tempo_calcolo': tempo_calcolo,
        'simulazioni': simulazioni
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

@csrf_exempt
def vessel_api(request):
    if request.method == 'POST':
        # Leggi i parametri dal body JSON
        import json
        data = json.loads(request.body.decode('utf-8'))
        P = data.get('pressione')
        D = data.get('diametro')
        S = data.get('tensione_ammissibile')
        E = data.get('efficienza_giunto')

        # Esegui il calcolo
        try:
            t = vessel_calculation(P, D, S, E)
            return JsonResponse({
                'spessore': t,
                'input': {
                    'pressione': P,
                    'diametro': D,
                    'tensione_ammissibile': S,
                    'efficienza_giunto': E
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Usa il metodo POST con parametri in JSON'}, status=405)


@api_view(['GET'])
def steam_reformer_calcoli_api(request):
    calcoli = SteamReformerCalcolo.objects.all().order_by('-data')[:10]
    serializer = SteamReformerCalcoloSerializer(calcoli, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

def equation_part_list_view(request):
    """
    Vista per elencare tutti gli EquationPart creati,
    offrendo la possibilità di crearne uno nuovo.
    """
    parts = EquationPart.objects.order_by('-created_at')
    return render(request, 'equation_tester/part_list.html', {'parts': parts})

def equation_part_create_view(request):
    """
    Vista per creare un nuovo EquationPart.
    """
    if request.method == 'POST':
        form = EquationPartForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Nuovo pezzo di formula creato con successo!")
            return redirect('equation_part_list')
    else:
        form = EquationPartForm()
    return render(request, 'equation_tester/part_create.html', {'form': form})

def equation_part_detail_view(request, pk):
    """
    Vista di dettaglio di un EquationPart, con possibilità di testare il codice.
    """
    part = get_object_or_404(EquationPart, pk=pk)
    test_form = EquationPartTestForm(initial={'equation_part_id': part.id})

    # Mostra gli ultimi test eseguiti su questo part
    test_results = EquationTestResult.objects.filter(equation_part=part).order_by('-created_at')[:10]

    return render(request, 'equation_tester/part_detail.html', {
        'part': part,
        'test_form': test_form,
        'test_results': test_results
    })

def equation_part_test_view(request):
    """
    Vista che riceve POST dal form EquationPartTestForm
    e calcola in modo parziale la formula, restituendo
    un risultato (o un errore).
    """
    if request.method == 'POST':
        form = EquationPartTestForm(request.POST)
        if form.is_valid():
            part_id = form.cleaned_data['equation_part_id']
            input_data_json = form.cleaned_data['input_data_json']

            part = get_object_or_404(EquationPart, pk=part_id)

            try:
                input_data = json.loads(input_data_json)
            except json.JSONDecodeError:
                messages.error(request, "Formato JSON non valido.")
                return redirect('equation_part_detail', pk=part_id)

            start_time = time.time()
            try:
                result_value = execute_equation_part(part.code_snippet, input_data)
                error_msg = ""
            except Exception as e:
                result_value = None
                error_msg = f"Errore: {str(e)}"

            end_time = time.time()

            # Salvataggio del test
            EquationTestResult.objects.create(
                equation_part=part,
                input_data=input_data,
                output_value=result_value if result_value is not None else 0.0,
                error_message=error_msg
            )

            if error_msg:
                messages.error(request, f"Test parziale fallito: {error_msg}")
            else:
                messages.success(request, f"Test parziale riuscito, risultato = {result_value}")
            
            return redirect('equation_part_detail', pk=part_id)
    return redirect('equation_part_list')