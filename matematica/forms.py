from django import forms
from django.core.exceptions import ValidationError
from .models import EquationPart

class SteamReformerForm(forms.Form):
    portata_molare_idrocarburo = forms.FloatField(
        label='Portata Molare Idrocarburo (mol/s)',
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Es. 1.0'})
    )
    portata_molare_vapore = forms.FloatField(
        label='Portata Molare Vapore (mol/s)',
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Es. 2.0'})
    )
    entalpia_prodotti = forms.FloatField(
        label='Entalpia dei Prodotti (kJ/mol)',
        widget=forms.NumberInput(attrs={'placeholder': 'Es. 100.0'})
    )
    entalpia_reagenti = forms.FloatField(
        label='Entalpia dei Reagenti (kJ/mol)',
        widget=forms.NumberInput(attrs={'placeholder': 'Es. 50.0'})
    )
    quantita_molare = forms.FloatField(
        label='Quantità Molare (mol)',
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'Es. 2.0'})
    )
    
    def clean_portata_molare_vapore(self):
        portata = self.cleaned_data.get('portata_molare_vapore')
        if portata <= 0:
            raise ValidationError('La portata molare del vapore deve essere maggiore di zero.')
        return portata

class BOBYQAForm(forms.Form):
    x0 = forms.CharField(
        label='Punto di Partenza (x0)',
        help_text='Inserisci il punto di partenza come elenco di numeri separati da virgole. Ad esempio: -1.2, 1.0',
        widget=forms.TextInput(attrs={'placeholder': '-1.2, 1.0'})
    )

class SteamReformerSimulationForm(forms.Form):
    pressione = forms.FloatField(label='Pressione (Pa)', initial=101325)
    temperatura_iniziale = forms.FloatField(label='Temperatura Iniziale (K)', initial=800)
    frazione_molare_CH4 = forms.FloatField(label='Frazione Molare CH4', initial=0.2)
    frazione_molare_H2O = forms.FloatField(label='Frazione Molare H2O', initial=0.8)
    peso_catalizzatore = forms.FloatField(label='Peso del Catalizzatore (kg)', initial=100)
    flusso_molare_totale = forms.FloatField(label='Flusso Molare Totale (mol/s)', initial=10)

class ElectricSteamReformerSimulationForm(forms.Form):
    pressione = forms.FloatField(label='Pressione (Pa)', initial=101325)
    temperatura_iniziale = forms.FloatField(label='Temperatura Iniziale (K)', initial=800)
    frazione_molare_CH4 = forms.FloatField(label='Frazione Molare CH₄', initial=0.2)
    frazione_molare_H2O = forms.FloatField(label='Frazione Molare H₂O', initial=0.8)
    peso_catalizzatore = forms.FloatField(label='Peso del Catalizzatore (kg)', initial=100)
    flusso_molare_totale = forms.FloatField(label='Flusso Molare Totale (mol/s)', initial=10)
    potenza_elettrica = forms.FloatField(label='Potenza Elettrica (W)', initial=10000)

class VesselForm(forms.Form):
    pressione = forms.FloatField(label='Pressione Interna (Pa)', initial=2e6) # es. 2 MPa
    diametro = forms.FloatField(label='Diametro Interno (m)', initial=1.0)
    tensione_ammissibile = forms.FloatField(label='Tensione Ammissibile (Pa)', initial=200e6)
    efficienza_giunto = forms.FloatField(label='Efficienza Giunto (0-1)', initial=0.85)

class EquationPartForm(forms.ModelForm):
    class Meta:
        model = EquationPart
        fields = ['name', 'description', 'code_snippet']

class EquationPartTestForm(forms.Form):
    """
    Usato per testare in modo semplificato un EquationPart
    con un dizionario di variabili di input.
    """
    equation_part_id = forms.IntegerField(widget=forms.HiddenInput())
    input_data_json = forms.CharField(
        label="Variabili in formato JSON",
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text='Esempio: {"temperature": 300, "pressure": 101325}'
    )
