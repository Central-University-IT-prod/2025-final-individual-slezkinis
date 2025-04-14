from django.db import models


class Client(models.Model):
    client_id = models.CharField(max_length=100, primary_key=True)
    login = models.CharField(max_length=100)
    age = models.IntegerField()
    location = models.CharField(max_length=100)
    gender = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"