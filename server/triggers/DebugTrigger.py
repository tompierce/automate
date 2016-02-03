from datetime import datetime
from base_trigger import Trigger
import constants as const

RUN_ONCE = False
class DebugTrigger(Trigger):
    def next_run(self):
        global RUN_ONCE
        if not RUN_ONCE:
            RUN_ONCE = True
            self.logger.info('DebugTrigger - Executing job immediately')
            return datetime.now()
        else:
            return const.DATETIME_NEVER
