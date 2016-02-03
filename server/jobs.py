import os, time, glob, json, datetime, Queue, logging
from logging.handlers import RotatingFileHandler
import actions, triggers
import constants as const

class Job(object):
    def __init__(self, job_id, job_dir, parsed_json, previous_stats = {}):
        self.job_id      = job_id
        self.job_dir     = job_dir
        self.parsed_json = parsed_json
        self.next_run    = const.DATETIME_NEVER
        self.last_run    = previous_stats['last_run'] if 'last_run' in previous_stats else const.DATETIME_NEVER
        self.must_run_now = False
        self.last_run_status = previous_stats['last_run_status'] if 'last_run' in previous_stats else const.DATETIME_NEVER
        self.is_running  = False

        self.job_logger = logging.getLogger('jobs.' + job_id)
        log_file_handler = logging.FileHandler(os.path.join(self.job_dir, 'job.log'))
        log_file_handler.setLevel(logging.DEBUG)
        self.job_logger.addHandler(log_file_handler)

        self.job_run_logger = logging.getLogger('jobs.' + self.job_id + '.last_run')
        self.job_run_file_handler = RotatingFileHandler(os.path.join(self.job_dir, 'job.last_run.log'), backupCount = 3)
        self.job_run_file_handler.setLevel(logging.DEBUG)
        self.job_run_logger.addHandler(self.job_run_file_handler)
        

        self.update_schedule()

    def serialize(self):

        next_run_str = 'NEVER' if self.next_run is const.DATETIME_NEVER else str(self.next_run)
        last_run_str = 'NEVER' if self.last_run is const.DATETIME_NEVER else str(self.last_run)

        return {
            'next_run' : next_run_str,
            'last_run' : last_run_str,
            'last_run_status' : self.last_run_status,
            'name' : self.name,
            'id' : self.job_id
        }
    
    def __repr__(self):
        return self.name
    
    @property
    def name(self):
        return self.parsed_json['name']
    
    @property
    def next_scheduled_run(self):
        return self.next_run    

    def run_now(self):
        self.next_run = datetime.datetime.now()
        self.must_run_now = True

    def update_schedule(self):

        if self.must_run_now:
            self.next_run = datetime.datetime.now()
            return       

        next_run = const.DATETIME_NEVER
        working_dir = self._resolve_workspace_dir()
        
        self.job_logger.debug('evaluating triggers...')

        for trigger_data in self.parsed_json['triggers']:
            trigger_module = __import__('triggers.' + str(trigger_data['className']) , fromlist = [str(trigger_data['className'])])
            trigger = getattr(trigger_module, trigger_data['className'])(self.job_id, trigger_data, self.job_logger)
        
            temp_next_run = trigger.next_run()
            next_run = min(next_run, temp_next_run)
        
        self.next_run = next_run

    def _resolve_workspace_dir(self):
        if not 'workspace' in self.parsed_json:
            working_dir = os.path.join(self.job_dir, 'workspace')
        else:
            working_dir = self.parsed_json['workspace']['workspace_path']
            if not os.path.isabs(working_dir):
                working_dir = os.path.join(self.job_dir, working_dir)
        return working_dir

    def run(self):
        self.must_run_now = False
        self.is_running = True
        self.update_schedule()
        
        working_dir = self._resolve_workspace_dir()

        if not os.path.isdir(working_dir):
            os.mkdir(working_dir)

        logging.debug(self.parsed_json['actions'])
        self.last_run = datetime.datetime.now()

        job_status = const.SUCCESS
        self.job_logger.info('executing job...')
        self.job_run_file_handler.doRollover()
        self.job_run_logger.handlers[0].doRollover()
        for action_data in self.parsed_json['actions']:

            action_module = __import__('actions.' + str(action_data['className']) , fromlist = [str(action_data['className'])])
            action = getattr(action_module, action_data['className'])(action_data, working_dir, self.job_run_logger)
            
            result = action.run()
            
            if (result is not const.SUCCESS) and (result is not const.UNSTABLE) and (result is not const.FAILURE):
                logging.error('job action returned an invalid result: ' + result); 
                # TODO: throw/error job here

            job_status = result

        self.last_run_status = job_status

        with open(os.path.join(self.job_dir, 'job.stats'), 'w') as stats_file:
            json.dump({"last_run": self.last_run.isoformat(), "last_run_status": self.last_run_status}, stats_file)

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
                job_id = os.path.basename(os.path.dirname(job_file))
                job_json = json.load(file)
                job_dir = os.path.dirname(job_file)
                stats_file = os.path.join(job_dir, 'job.stats')
                stats = {}
                if os.path.isfile(stats_file):
                    with open(stats_file) as stats:
                        stats = json.load(stats)
                self.jobs.append(Job(job_id, job_dir, job_json, stats))
    
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

        while(not self.interrupt):
            priority, job = self.job_queue.get()

            if datetime.datetime.now() > job.next_scheduled_run:
                logging.debug('Running ' + job.name + ' at ' + str(datetime.datetime.now()) + ' scheduled at ' + str(job.next_scheduled_run)) 
                job.run()
                time.sleep(timeout)

            self.refresh_job_schedules()
            self.refresh_job_queue()    

            time.sleep(timeout)
    
    def request_run(self, job_name):
        for job in self.jobs:
            if job_name == job.job_id:
                job.run_now()
                return True
        return False
    
    def is_job(self, job_id):
        for job in self.jobs:
            if job_id == job.job_id:
                return True
        return False
        
    def get_jobs_list(self):
        serializable_list = []
        for job in self.jobs:
            serializable_list.append(job.serialize())
        return serializable_list

    def stop(self):
        self.interrupt = True
