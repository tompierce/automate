import os, time, glob, json, subprocess, datetime, Queue
from logging import log
import triggers
import constants as const

class Job(object):
    def __init__(self, parsed_json):
        self.parsed_json = parsed_json
        self.next_run = const.DATETIME_NEVER
        self.is_running = False

        self.update_schedule()
    
    def __repr__(self):
        return self.name + ' ' + str(self.next_scheduled_run)
    
    @property
    def name(self):
        return self.parsed_json['name']
    
    @property
    def next_scheduled_run(self):
        return self.next_run    

    def update_schedule(self):
        next_run = const.DATETIME_NEVER
        for trigger_data in self.parsed_json['triggers']:
            trigger = getattr(triggers, trigger_data['className'])(trigger_data)
            temp_next_run = trigger.next_run()
            next_run = min(next_run, temp_next_run)
        
        self.next_run = next_run

    def run(self):
        self.is_running = True
        self.update_schedule()
        working_dir  = self.parsed_json['jobDir']
        scriptFile   = self.parsed_json['scriptFile']

        if not os.path.isabs(scriptFile):
            scriptFile = os.path.join(working_dir, scriptFile)

        job_process = subprocess.Popen(scriptFile, cwd=working_dir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = job_process.communicate()
        if out:
            log(out, prefix=self.name)
        if err:
            pass
            log(err, prefix=self.name)
        self.is_running = False


class JobManager(object):
    def __init__(self, jobs_dir):
        self.interrupt = False
        self.job_queue = Queue.PriorityQueue()
        self.jobs_dir = jobs_dir
        
        job_files = glob.glob(self.jobs_dir + '/*/*.json')
        self.jobs = []
        
        for job_file in job_files:
            with open(job_file) as file:
                job_json = json.load(file)
                job_json['jobDir'] = os.path.dirname(job_file)
                self.jobs.append(Job(job_json))

        self.refresh_job_queue()
    
    def refresh_job_schedules(self):
        for job in self.jobs:
            if not job.is_running:
                job.update_schedule()

    def refresh_job_queue(self):
        self.job_queue = Queue.PriorityQueue()
        for job in self.jobs:
            self.job_queue.put((job.next_scheduled_run, job))

    def start(self):

        self.refresh_job_queue()

        timeout = 5

        while(not self.interrupt):
            priority, job = self.job_queue.get()

            if datetime.datetime.now() > job.next_scheduled_run:
                log('Running ' + job.name + ' at ' + str(datetime.datetime.now()) + ' scheduled at ' + str(job.next_scheduled_run)) 
                job.run()
            else:
                self.refresh_job_queue()

            if self.job_queue.qsize() == 0:
                self.refresh_job_schedules()
                self.refresh_job_queue()    

            time.sleep(timeout)
    
    def get_queue_copy(self):
        temp_list = []
        for i in range(self.job_queue.qsize()):
            temp_list.append(self.job_queue.queue[i]) 
        temp_list.sort()
        return temp_list

    def stop(self):
        self.interrupt = True
