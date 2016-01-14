from datetime import datetime
from croniter import croniter
from base_trigger import Trigger

class CronTrigger(Trigger):
    def next_run(self):
        iter = croniter(self.trigger_data['schedule'], datetime.now())
        return iter.get_next(datetime)