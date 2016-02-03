"""Trigger a job when a specified file exists"""
import os
from datetime import datetime
import server.constants as const
from server.triggers.base_trigger import Trigger

class FileExistsTrigger(Trigger):
    """Trigger a job when a specified file exists"""
    def next_run(self):
        if os.path.isfile(self.trigger_data['file']):
            self.logger.info('FileExistsTrigger: ' + self.trigger_data['file'])
            return datetime.now()
        else:
            return const.DATETIME_NEVER
