from django.db import models

from django.conf import settings


class Client(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)


    class Meta:
        permissions = [('view_all_clients', 'Can view all clients')]


    def str(self): return self.email


class Message(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()


    class Meta:
        permissions = [('view_all_messages', 'Can view all messages')]


    def str(self): return self.subject


class Mailing(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    STATUS_CHOICES = [('CREATED', 'Создана'), ('RUNNING', 'Запущена'), ('COMPLETED', 'Завершена')]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='CREATED')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    clients = models.ManyToManyField(Client)


    class Meta:
        permissions = [('view_all_mailings', 'Can view all mailings')]


    def str(self): return f"Mailing {self.id}"


class MailingAttempt(models.Model):
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='attempts')
    tried_at = models.DateTimeField(auto_now_add=True)
    STATUS = [('SUCCESS', 'Успешно'), ('FAIL', 'Не успешно')]
    status = models.CharField(max_length=7, choices=STATUS)
    server_response = models.TextField(blank=True)

