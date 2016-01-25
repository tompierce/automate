import os, logging, shutil
from base_action import Action
import constants as const

class DeleteWorkspaceAction(Action):
    def run(self):
        self.logger.debug('deleting workspace: ' + self.working_dir)
        try:
            shutil.rmtree(self.working_dir)
        except:
            pass
        os.mkdir(self.working_dir)
        return const.SUCCESS    
