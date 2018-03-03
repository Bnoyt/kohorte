# -*- coding: utf-8 -*-
from importlib import import_module
import sys
from glob import glob

from django.core.management.base import (CommandError, SystemCheckError,
                                         BaseCommand, handle_default_options,
                                         no_style, OutputWrapper)
from django.db import connections
from django.core.exceptions import ImproperlyConfigured

class RecCommand(BaseCommand):

    folder = 'subcommands'
    import_format = '..{folder}.{command}'

    def get_subcommands(self):
        subcommands = []
        path = __file__.split('\\')[:-3] + self.__module__.split('.')[:-1] + [self.folder]
        path = '\\'.join(path)
        pkg = self.__module__
        for filename in glob(path + '\\*.py'):
            subcommand = filename.split('\\')[-1].replace('.py', '')
            if not subcommand.startswith('_'):
                try:
                    module = import_module(
                            self.import_format.format(folder = self.folder,
                                                      command = subcommand),
                            package=pkg)
                    if issubclass(module.Command, BaseCommand):
                        subcommands.append(subcommand)
                except (ModuleNotFoundError, AttributeError) as e:
                    pass
        return subcommands

    def print_subcommands(self):
        usage = ['', 'Available subcommands:']
        for name in self.get_subcommands():
            usage.append('  {0}'.format(name))
        return '\n'.join(usage)

    def print_help(self, prog_name, subcommand):
        super(RecCommand, self).print_help(prog_name, subcommand)
        self.stdout.write('{0}\n\n'.format(self.print_subcommands(prog_name)))

    def get_subcommand(self, subcommand):
        try:
            pkg = self.__module__
            module = import_module(
                    self.import_format.format(folder = self.folder,
                                              command = subcommand),
                    package=pkg)
            return module.Command()
        except (ModuleNotFoundError, AttributeError):
            path = '.'.join(pkg.split('.')[:-1])
            raise CommandError(
                    'Undefined subcommand {0}.{1}.{2}{3}'.format(
                            path, self.folder, subcommand,
                            self.print_subcommands()))

    def add_arguments(self, parser):
        parser.add_argument('subcommand',
                             choices=self.get_subcommands(),
                             help='The subcommand to be executed')

    def run_from_argv(self, argv):
        """
        Set up any environment changes requested (e.g., Python path
        and Django settings), then run this command. If the
        command raises a ``CommandError``, intercept it and print it sensibly
        to stderr. If the ``--traceback`` option is present or the raised
        ``Exception`` is not ``CommandError``, raise it.
        """
        self._called_from_command_line = True
        index = 2
        options = type('', (), {'traceback': False})()
        try:
            while index < len(argv) and argv[index].startswith('-'):
                index += 1
            if index < len(argv):
            #subcommand = self.get_subcommand(argv[index])
                subargv = argv[:2] + argv[index+1:]
                subargv[1] = subargv[1] + '.' + argv[index]
                argv = argv[:index+1]
            else:
                subargv = argv[:2]

            parser = self.create_parser(argv[0], argv[1])
            options = parser.parse_args(argv[2:])
            cmd_options = vars(options)
            args = cmd_options.pop('args', ())
            handle_default_options(options)

            #cmd_options['__command'] = subcommand
            cmd_options['__argv'] = subargv

            self.execute(*args, **cmd_options)
            #subcommand.run_from_argv(subargv)
        except Exception as e:
            if options.traceback or not isinstance(e, CommandError):
                raise

            # SystemCheckError takes care of its own formatting.
            if isinstance(e, SystemCheckError):
                self.stderr.write(str(e), lambda x: x)
            else:
                self.stderr.write('%s: %s' % (e.__class__.__name__, e))
            sys.exit(1)
        finally:
            try:
                connections.close_all()
            except ImproperlyConfigured:
                # Ignore if connections aren't setup at this point (e.g. no
                # configured settings).
                pass

    def handle(self, *args, **options):
        subcommand = options['subcommand']
        if subcommand not in self.get_subcommands():
            return self.print_help('./manage.py', self.__module__)
        else:
            subcommand = self.get_subcommand(subcommand)
            subcommand.run_from_argv(options['__argv'])
        pass
