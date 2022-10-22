from email.policy import default
from django.contrib.auth.models import User
from django.db import models
from django_cryptography.fields import encrypt

class Room(models.Model):
    name = models.CharField(max_length=128, null=True)
    
    def join(self, user):
        self.online.add(user)
        self.save()

    def leave(self, user):
        self.online.remove(user)
        self.save()
    
    def __str__(self):
        return f'{self.name} ({self.get_online_count()})'

class Message(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    message = encrypt(models.CharField(max_length=512, default=None))
    timestamp = models.DateTimeField(auto_now_add=True)
