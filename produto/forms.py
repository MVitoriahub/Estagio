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
            'item'     : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Vestido Floral'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'marca'    : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Zara'}),
            'colecao'  : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Verão 2025'}),
            'lucro'    : forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 30'}),
        }

    def clean_lucro(self):
        lucro = self.cleaned_data.get('lucro')
        if lucro is not None and lucro < 0:
            raise forms.ValidationError('O lucro não pode ser negativo.')
        return lucro


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
            'valor_bruto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 50.00'}),
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
    """Usado na edição do produto — quantidade travada."""

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
            'quantidade' : forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_bruto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 50.00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantidade'].disabled = True  # ignora POST, mantém valor original

    def clean_valor_bruto(self):
        valor_bruto = self.cleaned_data.get('valor_bruto')
        if valor_bruto is not None and valor_bruto <= 0:
            raise forms.ValidationError('O valor bruto deve ser maior que zero.')
        return valor_bruto