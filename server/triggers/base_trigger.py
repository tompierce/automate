'''
Trigger Algorithm

Each job can have multiple triggers. 
All jobs are polled every X ms and are asked when they next want to run.
    The job will ask each of its triggers when it needs to be triggered
    Triggers can respond with either a datetime (e.g. datetime.now()) or 0 / Never
    The job is then inserted into the job queue based on this response.
'''

class Trigger():
    def __init__(self, job_id, trigger_data):
        self.job_id = job_id
        self.trigger_data = trigger_data
        pass

    def next_run(self):
        raise NotImplementedError