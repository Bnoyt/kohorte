# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import .models as models #TODO check
# Reference :
# https://docs.djangoproject.com/en/dev/howto/custom-management-commands/#howto-custom-management-commands

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        suivi_simple = models.TypeSuivi(label = "suivi simple", actif = True)
        suivi_auto_post = models.TypeSuivi(label = "auto apres post", actif = True)
        suivi_auto_branch = models.TypeSuivi(label = "auto pendant branch", actif = True)
        suivi_annule = models.TypeSuivi(label = "post puis unfollow", actif = False)
        suivi_simple.save()
        suivi_auto_post.save()
        suivi_auto_branch.save()
        suivi_annule.save()

        upvote = models.TypeVote(label = "upovte", impact = 1)
        signal = models.TypeVote(label = "signal", impact = -1)
        upvote.save()
        signal.save()

        filiation = models.TypeArete(label="filiation")
        filiation.save()
        pass
