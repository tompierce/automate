"""Ugly hack to force a single job to trigger on server startup"""
from datetime import datetime
from server.triggers.base_trigger import Trigger
import server.constants as const

RUN_ONCE = False
class DebugTrigger(Trigger):
    """Ugly hack to force a single job to trigger on server startup"""
    def next_run(self):
        global RUN_ONCE
        if not RUN_ONCE:
            RUN_ONCE = True
            self.logger.info('DebugTrigger - Executing job immediately')
            return datetime.now()
        else:
            return const.DATETIME_NEVER
