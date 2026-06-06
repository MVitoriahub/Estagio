from django.db import models
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deletado=False)


class Cliente(models.Model):
    nome    = models.CharField(max_length=100)
    cpf     = models.CharField(max_length=14, unique=True)
    contato = models.CharField(max_length=20)
    rua     = models.CharField(max_length=100)
    numero  = models.CharField(max_length=10)
    bairro  = models.CharField(max_length=100)
    cidade  = models.CharField(max_length=100)

    # Soft delete
    deletado    = models.BooleanField(default=False)
    deletado_em = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    todos   = models.Manager()

    class Meta:
        verbose_name        = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering            = ['nome']

    def __str__(self):
        return self.nome

    def delete(self, using=None, keep_parents=False):
        self.deletado    = True
        self.deletado_em = timezone.now()
        self.save()