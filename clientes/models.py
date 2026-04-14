from django.db import models

class Cliente(models.Model):
    nome = models.CharField(max_length = 100)
    cpf = models.CharField(max_length = 14)
    contato = models.CharField(max_length = 20)

    rua = models.CharField(max_length = 100)
    numero = models.CharField(max_length = 100)
    bairro = models.CharField(max_length = 100)
    cidade = models.CharField(max_length = 100)

    def __str__(self):
        return self.nome