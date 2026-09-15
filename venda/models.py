from django.db import models
from django.utils import timezone
from clientes.models import Cliente
from produto.models import ProdutoVariacao


class Venda(models.Model):

    PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('pix',      'PIX'),
        ('credito',  'Cartão de Crédito'),
        ('debito',   'Cartão de Débito'),
    ]

    STATUS_CHOICES = [
        ('aberta',     'Aberta'),
        ('finalizada', 'Finalizada'),
        ('cancelada',  'Cancelada'),
    ]

    cliente         = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='vendas')
    forma_pagamento = models.CharField(max_length=20, choices=PAGAMENTO_CHOICES, blank=True)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta')
    data_venda      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Venda'
        verbose_name_plural = 'Vendas'
        ordering            = ['-data_venda']

    def __str__(self):
        return f'Venda #{self.pk} — {self.get_status_display()}'

    @property
    def valor_total(self):
        return sum(item.valor_total for item in self.itens.all())

    def finalizar(self, cliente, forma_pagamento):
        """Finaliza a venda, vincula cliente/pagamento e baixa o estoque."""
        from estoque.models import Estoque
        self.cliente         = cliente
        self.forma_pagamento = forma_pagamento
        self.status          = 'finalizada'
        self.save()
        for item in self.itens.all():
            Estoque.objects.create(
                variacao   = item.variacao,
                tipo       = 'saida',
                quantidade = item.quantidade,
                observacao = f'Venda #{self.pk}',
            )

    def cancelar(self):
        """Cancela a venda e devolve o estoque se já estava finalizada."""
        from estoque.models import Estoque
        if self.status == 'finalizada':
            for item in self.itens.all():
                Estoque.objects.create(
                    variacao   = item.variacao,
                    tipo       = 'entrada',
                    quantidade = item.quantidade,
                    observacao = f'Cancelamento da Venda #{self.pk}',
                )
        self.status = 'cancelada'
        self.save()


class ItemVenda(models.Model):
    venda          = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens')
    variacao       = models.ForeignKey(ProdutoVariacao, on_delete=models.CASCADE)
    quantidade     = models.IntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name        = 'Item da Venda'
        verbose_name_plural = 'Itens da Venda'

    def __str__(self):
        return f'{self.variacao.produto.item} x{self.quantidade}'

    @property
    def valor_total(self):
        return self.valor_unitario * self.quantidade