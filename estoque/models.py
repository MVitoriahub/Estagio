from decimal import Decimal

from django.db import models, transaction
from django.core.exceptions import ValidationError
from produto.models import ProdutoVariacao


class Estoque(models.Model):

    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida',   'Saída'),
    ]

    variacao          = models.ForeignKey(ProdutoVariacao, on_delete=models.CASCADE, related_name='movimentacoes')
    tipo              = models.CharField(max_length=10, choices=TIPO_CHOICES)
    quantidade        = models.IntegerField()
    custo_unitario    = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    saldo_apos        = models.IntegerField(null=True, blank=True, editable=False)
    data_movimentacao = models.DateTimeField(auto_now_add=True)
    observacao        = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'
        ordering            = ['-data_movimentacao', '-id']

    def __str__(self):
        return f'{self.tipo} - {self.variacao} - {self.data_movimentacao:%d/%m/%Y}'

    def clean(self):
        if self.pk or not self.variacao_id:
            return
        if self.quantidade is None or self.quantidade <= 0:
            raise ValidationError('A quantidade deve ser maior que zero.')
        if self.tipo == 'entrada' and self.custo_unitario is not None and self.custo_unitario <= 0:
            raise ValidationError('O custo unitário deve ser maior que zero.')
        if self.tipo == 'saida' and self.quantidade > self.variacao.quantidade:
            raise ValidationError(
                f'Saldo insuficiente. Disponível: {self.variacao.quantidade} unidades.'
            )

    def save(self, *args, **kwargs):
        # Alterar um registro já existente nunca mexe no saldo.
        if self.pk:
            return super().save(*args, **kwargs)

        with transaction.atomic():
            # Trava a linha da variação para evitar duas movimentações simultâneas
            variacao = ProdutoVariacao.todos.select_for_update().get(pk=self.variacao_id)
            self.variacao = variacao

            # Entrada sem custo informado usa o custo médio atual (o custo médio não muda)
            if self.tipo == 'entrada' and self.custo_unitario is None:
                self.custo_unitario = variacao.valor_bruto

            self.full_clean()

            if self.tipo == 'entrada':
                qtd_antiga = variacao.quantidade
                if qtd_antiga > 0:
                    custo_medio = (
                        qtd_antiga * variacao.valor_bruto + self.quantidade * self.custo_unitario
                    ) / (qtd_antiga + self.quantidade)
                else:
                    custo_medio = self.custo_unitario
                variacao.valor_bruto = Decimal(custo_medio).quantize(Decimal('0.01'))
                variacao.quantidade  = qtd_antiga + self.quantidade
            else:
                variacao.quantidade -= self.quantidade

            self.saldo_apos = variacao.quantidade
            super().save(*args, **kwargs)
            # update_fields garante que o preco_venda nunca é tocado
            variacao.save(update_fields=['quantidade', 'valor_bruto'])