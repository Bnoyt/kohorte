# -*- coding: utf-8 -*-
"""
Created on Tue May  1 11:18:41 2018
"""

from app.management.reccommand import RecCommand
import traceback
import pathlib

import app.clustering.parameters as param


def createControlFile(databaseID):
    """Initialises a control file for the project with id databaseID"""

    memory_path = pathlib.Path(param.memory_path)
    # Actuellement le path de la mémoire est noté dans app/clustering/parameters.
    # Il est probablement préférable de le mettre ailleurs.
    # Il faut alors modifier la ligne ci-dessus et une ligne de ProjectController

    if not memory_path.exists():
        raise IOError

    project_path = memory_path / str(databaseID)
    project_path.mkdir()

    with (project_path / "control.txt").open('w') as control_file:
        control_file.write("project " + str(databaseID) + "\n")
        control_file.write(str(databaseID) + "\n")
        control_file.write("true")

    (project_path / "logs").mkdir()


class Command(RecCommand):
    def handle(self, *args, **kwargs):
        try:
            createControlFile(0)
        except Exception as err:
            print('The following exception occured')
            traceback.print_tb(err.__traceback__)
            print(err)
