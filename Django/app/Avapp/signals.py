# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ShinyUserToken

@receiver(post_save, sender=User)
def generate_shiny_token(sender, instance, created, **kwargs):
    if created:
        ShinyUserToken.objects.create(user=instance, token="generate_your_token_here")
