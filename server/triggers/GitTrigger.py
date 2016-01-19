# Name: Git Trigger
# Author: Tom Pierce
# Email: tom.pierce0@gmail.com

from base_trigger import Trigger
import sh
import constants as const
import logging, os
from datetime import datetime

logging.getLogger("sh").setLevel(logging.WARNING)

class GitTrigger(Trigger):
    def next_run(self):
        
        temp_repo_dir = '/tmp/automate/git-trigger/' + self.job_id
        temp_repo_git = temp_repo_dir + '/.git'

        git = sh.git

        if not os.path.isdir(temp_repo_dir):
            os.makedirs(temp_repo_dir)

        if not os.path.isdir(temp_repo_git):
            git.clone(self.trigger_data['repository'], temp_repo_dir)
            logging.debug('Firing Git Trigger')
            return datetime.now()
        else:
            git = git.bake('-C', temp_repo_dir)
            git.fetch('origin')
            status_str = git.status()
            logging.debug(status_str)
            if 'branch is behind' in status_str:
                git.merge('origin/master')
                logging.debug('Firing Git Trigger')
                return datetime.now()

        logging.debug('Not firing Git Trigger')
        return const.DATETIME_NEVER

