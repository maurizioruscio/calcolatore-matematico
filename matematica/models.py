from django.db import models

class Calcolo(models.Model):
    espressione = models.CharField(max_length=500)
    operazione = models.CharField(max_length=100)
    risultato = models.TextField()
    tempo_calcolo = models.FloatField()     
    data = models.DateTimeField(auto_now_add=True)
    variabile_dipendente = models.CharField(max_length=50, null=True, blank=True)
    variabili_sistema = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return f"{self.operazione} di {self.espressione}"

class SteamReformerCalcolo(models.Model):
    portata_molare_idrocarburo = models.FloatField()
    portata_molare_vapore = models.FloatField()
    entalpia_prodotti = models.FloatField()
    entalpia_reagenti = models.FloatField()
    quantita_molare = models.FloatField()
    rapporto_vapore_carbonio = models.FloatField()
    calore_di_reazione = models.FloatField()
    tempo_calcolo = models.FloatField()
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Steam Reformer Calcolo - {self.data.strftime('%d/%m/%Y %H:%M:%S')}"
    
class BOBYQACalcolo(models.Model):
    x0 = models.TextField()  # Punto di partenza (come stringa)
    risultato = models.TextField()  # Risultato della minimizzazione
    tempo_calcolo = models.FloatField()
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"BOBYQA Calcolo ID {self.id} - x0: {self.x0}"

class SteamReformerSimulation(models.Model):
    # Parametri di input
    pressione = models.FloatField()
    temperatura_iniziale = models.FloatField()
    frazione_molare_CH4 = models.FloatField()
    frazione_molare_H2O = models.FloatField()
    peso_catalizzatore = models.FloatField()
    flusso_molare_totale = models.FloatField()

    # Risultati
    risultato = models.TextField()
    tempo_calcolo = models.FloatField()
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Simulazione ID {self.id} - {self.data}"
    
class ElectricSteamReformerSimulation(models.Model):
    data = models.DateTimeField(auto_now_add=True)
    pressione = models.FloatField()
    temperatura_iniziale = models.FloatField()
    frazione_molare_CH4 = models.FloatField()
    frazione_molare_H2O = models.FloatField()
    peso_catalizzatore = models.FloatField()
    flusso_molare_totale = models.FloatField()
    potenza_elettrica = models.FloatField()
    risultato = models.TextField()
    tempo_calcolo = models.FloatField()

    def __str__(self):
        return f"Simulazione del {self.data}"

class VesselSimulation(models.Model):
    data = models.DateTimeField(auto_now_add=True)
    pressione = models.FloatField()  # Pa
    diametro = models.FloatField()   # m
    tensione_ammissibile = models.FloatField() # Pa
    efficienza_giunto = models.FloatField()    # dimensionless
    risultato = models.TextField()   # JSON o stringa con i risultati
    tempo_calcolo = models.FloatField()

    def __str__(self):
        return f"Vessel Simulation ID {self.id} - {self.data}"
    
class EquationPart(models.Model):
    """
    Rappresenta un pezzo di formula (o un sotto-modulo) testabile in modo indipendente.
    Ad esempio: un termine di degrado, un fattore di pressione, ecc.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    code_snippet = models.TextField(
        help_text="Inserisci il codice o la formula Python che calcola questo componente."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class EquationTestResult(models.Model):
    """
    Memorizza i risultati dei test parziali o totali su un determinato EquationPart.
    """
    equation_part = models.ForeignKey(EquationPart, on_delete=models.CASCADE)
    input_data = models.JSONField(help_text="Dizionario con le variabili usate nel test.")
    output_value = models.FloatField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Test result for {self.equation_part.name} - {self.created_at}"