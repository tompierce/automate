"""Clones a Git repo to a job's workspace"""
import os
import sh
from server.actions.base_action import Action
import server.constants as const

class GitCloneAction(Action):
    """Clones a Git repo to a job's workspace"""
    def run(self):

        git = sh.git #@UndefinedVariable # pylint: disable=no-member

        if not self.action_data.get('localDir', False):
            local_dir = self.working_dir
        else:
            if not os.path.isabs(self.action_data['localDir']):
                local_dir = os.path.join(self.working_dir, self.action_data['localDir'])
            else:
                local_dir = self.action_data['localDir']

        self.logger.info('cloning ' + self.action_data['repository'] + ' to ' + local_dir)

        output = git.clone(self.action_data['repository'], local_dir)

        return const.SUCCESS if output.exit_code is 0 else const.FAILURE
