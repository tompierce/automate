import os, logging
from base_action import Action
import constants as const
import sh

class GitCloneAction(Action):
    def run(self):

        git = sh.git

        if not self.action_data.get('localDir', False):
            local_dir = self.working_dir
        else:
            if not os.path.isabs(self.action_data['localDir']):
                local_dir = os.path.join(self.working_dir, self.action_data['localDir'])
            else:
                local_dir = self.action_data['localDir']

        self.logger.info('cloning ' + self.action_data['repository'] + ' to ' + local_dir)

        output = git.clone(self.action_data['repository'], local_dir)

        return const.SUCCESS if output.exit_code is 0 else const.FAILED 