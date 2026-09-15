from django import forms
from clientes.models import Cliente
from produto.models import Produto, ProdutoVariacao
from .models import Venda


class AdicionarItemForm(forms.Form):
    produto    = forms.ModelChoiceField(
        queryset  = Produto.objects.all(),
        label     = 'Item',
        widget    = forms.Select(attrs={'class': 'form-control', 'id': 'id_produto'}),
    )
    variacao   = forms.ModelChoiceField(
        queryset  = ProdutoVariacao.objects.none(),
        label     = 'Tamanho',
        widget    = forms.Select(attrs={'class': 'form-control', 'id': 'id_variacao'}),
    )
    quantidade = forms.IntegerField(
        min_value = 1,
        label     = 'Quantidade',
        widget    = forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'produto' in self.data:
            try:
                produto_id = int(self.data.get('produto'))
                self.fields['variacao'].queryset = ProdutoVariacao.objects.filter(
                    produto_id=produto_id, quantidade__gt=0
                )
            except (ValueError, TypeError):
                pass

    def clean(self):
        cleaned_data = super().clean()
        variacao     = cleaned_data.get('variacao')
        quantidade   = cleaned_data.get('quantidade')
        if variacao and quantidade and quantidade > variacao.quantidade:
            raise forms.ValidationError(
                f'Saldo insuficiente. Disponível: {variacao.quantidade} unidades.'
            )
        return cleaned_data


class FinalizarVendaForm(forms.Form):
    cliente = forms.ModelChoiceField(
        queryset  = Cliente.objects.all(),
        label     = 'Cliente',
        required  = False,
        empty_label = 'Sem cliente',
        widget    = forms.Select(attrs={'class': 'form-control'}),
    )
    forma_pagamento = forms.ChoiceField(
        choices = Venda.PAGAMENTO_CHOICES,
        label   = 'Pagamento',
        widget  = forms.Select(attrs={'class': 'form-control'}),
    )