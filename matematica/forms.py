from django import forms
from django.core.exceptions import ValidationError

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
