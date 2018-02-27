# -*- coding: utf-8 -*-
from django.core.management.base import CommandError, BaseCommand

class RecCommand(BaseCommand):

    folder = 'subcommands'
    subcommands = {}

    def __init__(self):
        pass


