from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):

    class Meta:
        model  = Cliente
        fields = ['nome', 'cpf', 'contato', 'rua', 'numero', 'bairro', 'cidade']
        labels = {
            'nome'   : 'Nome',
            'cpf'    : 'CPF',
            'contato': 'Contato',
            'rua'    : 'Rua',
            'numero' : 'Número',
            'bairro' : 'Bairro',
            'cidade' : 'Cidade',
        }
        widgets = {
            'nome'   : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Maria Silva'}),
            'cpf'    : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 000.000.000-00'}),
            'contato': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: (43) 99999-9999'}),
            'rua'    : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Rua das Flores'}),
            'numero' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 123'}),
            'bairro' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Centro'}),
            'cidade' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Sertanópolis'}),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        # Remove caracteres não numéricos para validar o tamanho
        cpf_numeros = ''.join(filter(str.isdigit, cpf))
        if len(cpf_numeros) != 11:
            raise forms.ValidationError('CPF inválido. Digite 11 dígitos.')
        return cpf