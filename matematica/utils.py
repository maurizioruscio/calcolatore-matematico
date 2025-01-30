import ast
import math
import json


def calcola_rapporto_vapore_carbonio(portata_molare_idrocarburo, portata_molare_vapore):
    try:
        # Assumiamo che ogni mole di idrocarburo contenga una mole di carbonio
        moles_carbonio = portata_molare_idrocarburo  # Modifica se necessario per idrocarburi diversi dal metano
        rapporto = portata_molare_vapore / moles_carbonio
        return rapporto  # Ritorna un float
    except ZeroDivisionError:
        raise ValueError("La portata molare dell'idrocarburo non può essere zero.")
    except Exception as e:
        raise ValueError(f"Errore nel calcolo del rapporto Vapore/Carbonio: {str(e)}")


def calcola_calore_di_reazione(entalpia_prodotti, entalpia_reagenti, quantita_molare):
    try:
        delta_enthalpy = entalpia_prodotti - entalpia_reagenti
        calore_di_reazione = quantita_molare * delta_enthalpy
        return calore_di_reazione  # Ritorna un float
    except Exception as e:
        raise ValueError(f"Errore nel calcolo del calore di reazione: {str(e)}")

def execute_equation_part(code_snippet, input_data):
    """
    Esegue il code_snippet (test parziale di formula)
    in un ambiente sicuro/limitato, restituendo il risultato
    o sollevando eccezioni.
    """
    
    # ATTENZIONE: In produzione, eval è pericoloso senza sandboxing adeguato.

    # Costruzione di un namespace con le funzioni ammese (es. math, ...)
    allowed_namespace = {
        '__builtins__': {},
        'math': math,
        
    }
    # Aggiungo le variabili di input
    for k, v in input_data.items():
        allowed_namespace[k] = v

    try:
        result = eval(code_snippet, allowed_namespace)
    except Exception as e:
        raise ValueError(str(e))

    return result