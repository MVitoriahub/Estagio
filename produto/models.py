from decimal import Decimal
from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deletado=False)


class Produto(models.Model):

    CATEGORIA_CHOICES = [
        ('blusa', 'Blusa'),
        ('calça', 'Calça'),
        ('shorts', 'Shorts'),
        ('bermuda', 'Bermuda'),
        ('saia', 'Saia'),
        ('meia', 'Meia'),
        ('legging', 'Legging'),
        ('vestido', 'Vestido'),
        ('camisa', 'Camisa'),
        ('camiseta', 'Camiseta'),
        ('conjunto_feminino', 'Conjunto Feminino'),
        ('conjunto_masculino', 'Conjunto Masculino'),
        ('jaqueta', 'Jaqueta'),
        ('moletom', 'Moletom'),
        ('body', 'Body'),
        ('colete', 'Colete'),
        ('calca_jeans', 'Calça Jeans'),
        ('calcado', 'Calçado'),
        ('acessorio', 'Acessório'),
    ]

    id_item     = models.AutoField(primary_key=True)
    item        = models.CharField(max_length=100)
    categoria   = models.CharField(max_length=50, choices=CATEGORIA_CHOICES)
    marca       = models.CharField(max_length=50)
    colecao     = models.CharField(max_length=50)
    lucro       = models.DecimalField(max_digits=5, decimal_places=2)

    deletado    = models.BooleanField(default=False)
    deletado_em = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    todos   = models.Manager()

    class Meta:
        verbose_name        = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering            = ['item']

    def __str__(self):
        return f'{self.item} - {self.marca}'

    def delete(self, using=None, keep_parents=False):  
        self.variacoes.filter(deletado=False).update(
            deletado=True,
            deletado_em=timezone.now()
        )
        self.deletado    = True
        self.deletado_em = timezone.now()
        self.save()


class ProdutoVariacao(models.Model):

    TAMANHO_CHOICES = [
        ('RN', 'RN'), ('PP', 'PP'), ('P', 'P'),  ('M', 'M'),
        ('G', 'G'),   ('GG', 'GG'), ('XGG', 'XGG'),
        ('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
        ('06', '06'), ('08', '08'), ('10', '10'), ('12', '12'),
        ('14', '14'), ('16', '16'), ('18', '18'), ('20', '20'),
    ]

    produto     = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name='variacoes'
    )
    tamanho     = models.CharField(max_length=10, choices=TAMANHO_CHOICES)
    quantidade  = models.IntegerField()
    valor_bruto = models.DecimalField(max_digits=10, decimal_places=2)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    deletado    = models.BooleanField(default=False)
    deletado_em = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    todos   = models.Manager()

    class Meta:
        verbose_name        = 'Variação'
        verbose_name_plural = 'Variações'
        ordering            = ['tamanho']

    def __str__(self):
        return f'{self.produto.item} - Tam: {self.tamanho} | Qtd: {self.quantidade}'

    def calcular_preco_venda(self):
        lucro_percentual = self.produto.lucro / Decimal('100')
        return self.valor_bruto * (Decimal('1') + lucro_percentual)

    def save(self, *args, **kwargs):
        self.preco_venda = self.calcular_preco_venda()
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):  
        self.deletado    = True
        self.deletado_em = timezone.now()
        self.save()