from django import forms
from .models import Produto, ProdutoVariacao


class ProdutoForm(forms.ModelForm):

    class Meta:
        model  = Produto
        fields = ['item', 'categoria', 'marca', 'colecao', 'lucro']
        labels = {
            'item'     : 'Nome do Produto',
            'categoria': 'Categoria',
            'marca'    : 'Marca',
            'colecao'  : 'Coleção',
            'lucro'    : 'Lucro (%)',
        }
        widgets = {
            'item'     : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Vestido Amarelo Floral'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'marca'    : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Hering'}),
            'colecao'  : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Verão 2026'}),
            'lucro'    : forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 30', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].choices = [('', 'Selecione uma categoria')] + list(Produto.CATEGORIA_CHOICES)

    def clean_lucro(self):
        lucro = self.cleaned_data.get('lucro')
        if lucro is not None and lucro < 0:
            raise forms.ValidationError('O lucro não pode ser negativo.')
        return lucro

    def clean_marca(self):
        marca = self.cleaned_data.get('marca', '').strip()
        return marca.title()

    def clean_colecao(self):
        colecao = self.cleaned_data.get('colecao', '').strip()
        return colecao.title()


class ProdutoVariacaoForm(forms.ModelForm):
    """Usado apenas na criação do produto."""

    class Meta:
        model  = ProdutoVariacao
        fields = ['tamanho', 'quantidade', 'valor_bruto']
        labels = {
            'tamanho'    : 'Tamanho',
            'quantidade' : 'Quantidade',
            'valor_bruto': 'Valor Bruto (R$)',
        }
        widgets = {
            'tamanho'    : forms.Select(attrs={'class': 'form-control'}),
            'quantidade' : forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 10'}),
            'valor_bruto': forms.TextInput(attrs={
                'class': 'form-control valor-bruto-mask',
                'placeholder': 'Ex: 50,00',
                'inputmode': 'decimal',
            }),
        }

    def clean_quantidade(self):
        quantidade = self.cleaned_data.get('quantidade')
        if quantidade is not None and quantidade < 0:
            raise forms.ValidationError('A quantidade não pode ser negativa.')
        return quantidade

    def clean_valor_bruto(self):
        valor_bruto = self.cleaned_data.get('valor_bruto')
        if valor_bruto is not None and valor_bruto <= 0:
            raise forms.ValidationError('O valor bruto deve ser maior que zero.')
        return valor_bruto


class ProdutoVariacaoEditForm(forms.ModelForm):
    """Usado na edição do produto — quantidade travada, preço de venda editável."""

    class Meta:
        model  = ProdutoVariacao
        fields = ['tamanho', 'quantidade', 'valor_bruto', 'preco_venda', 'estoque_minimo']
        labels = {
            'tamanho'       : 'Tamanho',
            'quantidade'    : 'Quantidade',
            'valor_bruto'   : 'Custo médio (R$)',
            'preco_venda'   : 'Preço de venda (R$)',
            'estoque_minimo': 'Estoque mínimo',
        }
        widgets = {
            'tamanho'       : forms.Select(attrs={'class': 'form-control'}),
            'quantidade'    : forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_bruto'   : forms.TextInput(attrs={
                'class': 'form-control valor-bruto-mask',
                'placeholder': 'Ex: 50,00',
                'inputmode': 'decimal',
            }),
            'preco_venda'   : forms.TextInput(attrs={
                'class': 'form-control valor-bruto-mask',
                'placeholder': 'Ex: 100,00',
                'inputmode': 'decimal',
            }),
            'estoque_minimo': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantidade'].disabled = True
        self.fields['preco_venda'].required = True

    def clean_valor_bruto(self):
        valor_bruto = self.cleaned_data.get('valor_bruto')
        if valor_bruto is not None and valor_bruto <= 0:
            raise forms.ValidationError('O custo deve ser maior que zero.')
        return valor_bruto

    def clean_preco_venda(self):
        preco = self.cleaned_data.get('preco_venda')
        if preco is not None and preco <= 0:
            raise forms.ValidationError('O preço de venda deve ser maior que zero.')
        return preco