from django import forms
from produto.models import ProdutoVariacao
from .models import Estoque


class EstoqueForm(forms.ModelForm):
    class Meta:
        model  = Estoque
        fields = ['tipo', 'quantidade', 'observacao']


class NovaVariacaoForm(forms.Form):
    tamanho     = forms.ChoiceField(
        choices  = ProdutoVariacao.TAMANHO_CHOICES,
        label    = 'Tamanho',
        widget   = forms.Select(attrs={'class': 'form-control'}),
    )
    quantidade  = forms.IntegerField(
        min_value = 0,
        label     = 'Quantidade inicial',
        widget    = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 5'}),
    )
    valor_bruto = forms.DecimalField(
        min_value    = 0.01,
        decimal_places = 2,
        label        = 'Valor Bruto (R$)',
        widget       = forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ex: 50.00'}),
    )