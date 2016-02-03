import os
from datetime import datetime
import constants as const
from base_trigger import Trigger

class FileExistsTrigger(Trigger):
    def next_run(self):
        if os.path.isfile(self.trigger_data['file']):
            self.logger.info('FileExistsTrigger: ' + self.trigger_data['file'])
            return datetime.now()
        else:
            return const.DATETIME_NEVER
