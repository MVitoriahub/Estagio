from django.db import models
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
    data_movimentacao = models.DateTimeField(auto_now_add=True)
    observacao        = models.TextField(blank=True)

    class Meta:
        verbose_name        = 'Movimentação de Estoque'
        verbose_name_plural = 'Movimentações de Estoque'
        ordering            = ['-data_movimentacao']

    def __str__(self):
        return f'{self.tipo} - {self.variacao} - {self.data_movimentacao:%d/%m/%Y}'

    def clean(self):
        if self.tipo == 'saida' and self.quantidade > self.variacao.quantidade:
            raise ValidationError(
                f'Saldo insuficiente. Disponível: {self.variacao.quantidade} unidades.'
            )

    def save(self, *args, **kwargs):
        self.full_clean()  # valida antes de salvar
        super().save(*args, **kwargs)
        # Atualiza o quantidade na variação
        if self.tipo == 'entrada':
            self.variacao.quantidade += self.quantidade
        else:
            self.variacao.quantidade -= self.quantidade
        self.variacao.save()