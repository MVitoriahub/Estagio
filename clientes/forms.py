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
            'bairro' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Bairro'}),
            'cidade' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Sertanópolis'}),
        }

    def clean_cpf(self):  # ← indentado dentro da classe
        cpf = self.cleaned_data.get('cpf', '')
        cpf_numeros = ''.join(filter(str.isdigit, cpf))

        if len(cpf_numeros) != 11:
            raise forms.ValidationError('CPF inválido. Digite 11 dígitos.')

        qs = Cliente.todos.filter(cpf=cpf_numeros, deletado=False)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Já existe um cliente cadastrado com esse CPF.')

        return cpf_numeros