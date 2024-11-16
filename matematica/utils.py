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
