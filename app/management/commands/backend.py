# -*- coding: utf-8 -*-

from app.management.subcommander import Subcommander

class Command(Subcommander):
    app_name = 'app'
    folder = 'backend_subcommands'
    subcommands = {
        'start': 'start',
        'stop': 'stop',
    }