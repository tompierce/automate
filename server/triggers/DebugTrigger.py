from datetime import datetime
from base_trigger import Trigger
import constants as const

RUN_ONCE = False
class DebugTrigger(Trigger):
    def next_run(self):
        global RUN_ONCE
        if not RUN_ONCE:
            RUN_ONCE = True
            return datetime.now()
        else:
            return const.DATETIME_NEVER
