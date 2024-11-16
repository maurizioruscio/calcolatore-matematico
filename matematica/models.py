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
