from rest_framework import serializers
from .models import Calcolo
from .models import SteamReformerCalcolo
class CalcoloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calcolo
        fields = ['id', 'espressione', 'operazione', 'risultato', 'tempo_calcolo', 'data']

class SteamReformerCalcoloSerializer(serializers.ModelSerializer):
    class Meta:
        model = SteamReformerCalcolo
        fields = '__all__'
