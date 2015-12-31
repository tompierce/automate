'''
Trigger Algorithm

Each job can have multiple triggers. 
All jobs are polled every X ms and are asked when they next want to run.
    The job will ask each of its triggers when it needs to be triggered
    Triggers can respond with either a datetime (e.g. datetime.now()) or 0 / Never
    The job is then inserted into the job queue based on this response.

TODO: trigger results should be asynchronous
      the trigger will be polled every 5 seconds, it doesn't need to complete its 
      check within 5 seconds, but should persist - SOMEHOW?

'''

import os
from datetime import datetime
from croniter import croniter
import constants as const

class Trigger():
    def __init__(self, trigger_data):
        self.trigger_data = trigger_data
        pass

    def next_run(self):
        raise NotImplementedError

class CronTrigger(Trigger):
    def next_run(self):
        iter = croniter(self.trigger_data['schedule'], datetime.now())
        return iter.get_next(datetime)

class FileExistsTrigger(Trigger):
    def next_run(self):
        if os.path.isfile(self.trigger_data['file']):
            return datetime.now()
        else:
            return const.DATETIME_NEVER
