"""Trigger jobs using a cron schedule"""
from datetime import datetime
from croniter import croniter
from server.triggers.base_trigger import Trigger

class CronTrigger(Trigger):
    """trigger wrapper around croniter library"""
    def next_run(self):
        cron_scheduler = croniter(self.trigger_data['schedule'], datetime.now())
        return cron_scheduler.get_next(datetime)
