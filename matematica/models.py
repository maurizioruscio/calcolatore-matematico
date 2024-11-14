from django.db import models

class Calcolo(models.Model):
    espressione = models.CharField(max_length=255)
    operazione = models.CharField(max_length=50)
    risultato = models.TextField()
    tempo_calcolo = models.FloatField()     
    data = models.DateTimeField(auto_now_add=True)
    variabile_dipendente = models.CharField(max_length=50, null=True, blank=True)
    variabili_sistema = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return f"{self.operazione} di {self.espressione}"
