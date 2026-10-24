from django import forms

from produto.models import ProdutoVariacao
from .models import Estoque


class EstoqueForm(forms.ModelForm):

    class Meta:
        model  = Estoque
        fields = ['tipo', 'quantidade', 'observacao']
        labels = {
            'tipo'      : 'Tipo',
            'quantidade': 'Quantidade',
            'observacao': 'Observação',
        }
        widgets = {
            'tipo'      : forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        variacao = kwargs.pop('variacao', None)
        super().__init__(*args, **kwargs)
        # Necessário para a validação de saldo do model funcionar dentro do form
        if variacao is not None:
            self.instance.variacao = variacao


class NovaVariacaoForm(forms.Form):
    tamanho     = forms.ChoiceField(
        choices=ProdutoVariacao.TAMANHO_CHOICES,
        label='Tamanho',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    quantidade  = forms.IntegerField(
        min_value=0,
        label='Quantidade',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 10'}),
    )
    valor_bruto = forms.DecimalField(
        min_value=0.01,
        max_digits=10,
        decimal_places=2,
        label='Custo unitário (R$)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ex: 50.00'}),
    )
    preco_venda = forms.DecimalField(
        required=False,
        min_value=0.01,
        max_digits=10,
        decimal_places=2,
        label='Novo preço de venda (R$) — opcional',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Deixe vazio para manter o atual'}),
    )