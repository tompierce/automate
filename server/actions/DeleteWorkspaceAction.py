"""Action for deleting a job's workspace"""
import os
import shutil
from server.actions.base_action import Action
import server.constants as const

class DeleteWorkspaceAction(Action):
    """Deletes and recreates job's working dir"""
    def run(self):
        self.logger.info('deleting workspace: ' + self.working_dir)
        shutil.rmtree(self.working_dir, ignore_errors=True)
        os.mkdir(self.working_dir)
        return const.SUCCESS
