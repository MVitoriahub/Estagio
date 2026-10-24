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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cliente excluído com o mesmo CPF, encontrado em clean_cpf (só no cadastro)
        self._cliente_excluido = None

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf', '')
        cpf_numeros = ''.join(filter(str.isdigit, cpf))

        if len(cpf_numeros) != 11:
            raise forms.ValidationError('CPF inválido. Digite 11 dígitos.')

        outros = Cliente.todos.filter(cpf=cpf_numeros)
        if self.instance.pk:
            outros = outros.exclude(pk=self.instance.pk)

        if outros.filter(deletado=False).exists():
            raise forms.ValidationError('Já existe um cliente cadastrado com esse CPF.')

        excluido = outros.filter(deletado=True).first()
        if excluido:
            if self.instance.pk:
                # Edição: não dá para assumir o CPF de um cliente excluído
                raise forms.ValidationError(
                    'Este CPF pertence a um cliente excluído. '
                    'Para reativá-lo, use a tela de cadastro.'
                )
            # Cadastro: o save() vai reativar o cliente antigo em vez de criar outro
            self._cliente_excluido = excluido

        return cpf_numeros

    def clean_contato(self):
        # Guarda só os números, como já é feito com o CPF
        contato = self.cleaned_data.get('contato', '')
        contato_numeros = ''.join(filter(str.isdigit, contato))

        if not contato_numeros:
            raise forms.ValidationError('Informe um contato válido.')

        return contato_numeros

    def save(self, commit=True):
        """Se o CPF é de um cliente excluído, reativa o registro antigo com os
        dados novos. Assim o histórico de vendas continua ligado à mesma pessoa."""
        antigo = self._cliente_excluido
        if antigo is not None and not self.instance.pk:
            for campo in self.Meta.fields:
                setattr(antigo, campo, self.cleaned_data[campo])
            antigo.deletado    = False
            antigo.deletado_em = None
            self.instance = antigo
            if commit:
                antigo.save()
            return antigo
        return super().save(commit)