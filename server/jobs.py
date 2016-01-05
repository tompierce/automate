import os, time, glob, json, datetime, Queue, logging
import triggers, actions
import constants as const

class Job(object):
    def __init__(self, parsed_json):
        self.parsed_json = parsed_json
        self.next_run    = const.DATETIME_NEVER
        self.last_run    = const.DATETIME_NEVER
        self.last_run_status = ''
        self.is_running  = False
        self.update_schedule()

    def serialize(self):

        next_run_str = 'NEVER' if self.next_run is const.DATETIME_NEVER else str(self.next_run)
        last_run_str = 'NEVER' if self.last_run is const.DATETIME_NEVER else str(self.last_run)

        return {
            'next_run' : next_run_str,
            'last_run' : last_run_str,
            'last_run_status' : self.last_run_status,
            'name' : self.name
        }
    
    def __repr__(self):
        return self.name
    
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
        logging.debug(self.parsed_json['actions'])
        self.last_run = datetime.datetime.now()
        
        job_status = const.SUCCESS

        for action_data in self.parsed_json['actions']:
            action = getattr(actions, action_data['className'])(action_data, working_dir)
            result = action.run()
            if result is not const.SUCCESS:
                job_status = result
            else:
                if job_status is const.SUCCESS:
                    job_status = const.SUCCESS                    

        self.last_run_status = job_status
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
    
    def refresh_job_schedules(self):
        for job in self.jobs:
            if not job.is_running:
                job.update_schedule()

    def refresh_job_queue(self):

        while not self.job_queue.empty():
            try:
                self.job_queue.get()
            except Empty:
                continue

        for job in self.jobs:
            self.job_queue.put((job.next_scheduled_run, job))

    def start(self):

        self.refresh_job_queue()

        timeout = 5

        logging.debug('starting job manager')

        # TODO: re-think the logic in this loop
        while(not self.interrupt):
            priority, job = self.job_queue.get()

            if datetime.datetime.now() > job.next_scheduled_run:
                logging.debug('Running ' + job.name + ' at ' + str(datetime.datetime.now()) + ' scheduled at ' + str(job.next_scheduled_run)) 
                job.run()
                time.sleep(timeout)

            self.refresh_job_schedules()
            self.refresh_job_queue()    

            time.sleep(timeout)
    
    def get_jobs_list(self):
        serializable_list = []
        for job in self.jobs:
            serializable_list.append(job.serialize())
        return serializable_list

    def stop(self):
        self.interrupt = True
