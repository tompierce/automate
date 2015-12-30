import os, time, glob, json, subprocess, datetime, Queue
from croniter import croniter
from logging import log

class Job(object):
    def __init__(self, parsed_json):
        self.parsed_json = parsed_json
    
    def __repr__(self):
        return self.name + ' ' + str(self.next_scheduled_run)
    
    @property
    def name(self):
        return self.parsed_json['name']
    
    @property
    def next_scheduled_run(self):
        iter = croniter(self.parsed_json['schedule'], datetime.datetime.now())
        return iter.get_next(datetime.datetime)
        
    def run(self):

        working_dir = self.parsed_json['jobDir']

        scriptFile = self.parsed_json['scriptFile']
        if not os.path.isabs(scriptFile):
            scriptFile = os.path.join(working_dir, scriptFile)

        job_process = subprocess.Popen(scriptFile, cwd=working_dir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = job_process.communicate()
        if out:
            log(out, prefix=self.name)
        if err:
            log(err, prefix=self.name)

class JobManager(object):
    def __init__(self, jobs_dir):
        self.interrupt = False
        self.job_queue = Queue.PriorityQueue()
        self.jobs_dir = jobs_dir
       
    def start(self):
        job_files = glob.glob(self.jobs_dir + '/*/*.json')
        jobs = []
        
        for job_file in job_files:
            with open(job_file) as file:
                job_json = json.load(file)
                job_json['jobDir'] = os.path.dirname(job_file)
                job = Job(job_json)
                self.job_queue.put((job.next_scheduled_run, job))
               
        priority, job = self.job_queue.get()       
        timeout = 5
        while(not self.interrupt):
            if (job.next_scheduled_run - datetime.datetime.now()).total_seconds() < timeout:
                job.run()
                self.job_queue.put((job.next_scheduled_run, job))
                priority, job = self.job_queue.get()
            time.sleep(timeout)
    
    def get_queue_copy(self):
        temp_list = []
        for i in range(self.job_queue.qsize()):
            temp_list.append(self.job_queue.queue[i]) 
        temp_list.sort()
        return temp_list

    def stop(self):
        self.interrupt = True
