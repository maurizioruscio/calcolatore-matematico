from rest_framework import serializers
from .models import Calcolo

class CalcoloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calcolo
        fields = ['id', 'espressione', 'operazione', 'risultato', 'tempo_calcolo', 'data']
