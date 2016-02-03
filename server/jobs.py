"""Module for classes relating to job handling"""
import os
import time
import glob
import json
import datetime
import Queue
import logging
from logging.handlers import RotatingFileHandler
import constants as const # pylint: disable=relative-import

def dynamic_import_trigger(class_name):
    """load a trigger from the triggers directory"""
    module = __import__('triggers.' + class_name, fromlist = [class_name])
    return getattr(module, class_name)

def dynamic_import_action(class_name):
    """load an action from the actions directory"""
    module = __import__('actions.' + class_name, fromlist = [class_name])
    return getattr(module, class_name)

class Job(object):
    """Holds the state of a job in memory"""
    def __init__(self, job_id, job_dir, parsed_json, previous_stats = None):
        self.job_id      = job_id
        self.job_dir     = job_dir
        self.parsed_json = parsed_json
        self.next_run    = const.DATETIME_NEVER

        self.last_run = const.DATETIME_NEVER
        self.last_run_status = ""

        if previous_stats:
            if 'last_run' in previous_stats:
                self.last_run = previous_stats['last_run']
            if 'last_run_status' in previous_stats:
                self.last_run_status = previous_stats['last_run_status']

        self.must_run_now = False
        self.is_running  = False

        self.job_logger = logging.getLogger('jobs.' + job_id)
        log_file_handler = logging.FileHandler(os.path.join(self.job_dir, 'job.log'))
        log_file_handler.setLevel(logging.DEBUG)
        self.job_logger.addHandler(log_file_handler)

        self.job_run_logger = logging.getLogger('jobs.' + self.job_id + '.last_run')
        self.job_run_file_handler = RotatingFileHandler(
                                                    os.path.join(self.job_dir, 'job.last_run.log'),
                                                    backupCount = 3)
        self.job_run_file_handler.setLevel(logging.DEBUG)
        self.job_run_logger.addHandler(self.job_run_file_handler)

        self.update_schedule()

    def serialize(self):
        """create a serializable dict from the job's fields"""
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
        """accessor for human readable job name"""
        return self.parsed_json['name']

    @property
    def next_scheduled_run(self):
        """accessor for next scheduled run as a datetime"""
        return self.next_run

    def run_now(self):
        """schedules the job to run immediately"""
        self.next_run = datetime.datetime.now()
        self.must_run_now = True

    def update_schedule(self):
        """ polls all of the job's triggers to see if anything changes
            require an update of the schedule
        """
        if self.must_run_now:
            self.next_run = datetime.datetime.now()
            return

        next_run = const.DATETIME_NEVER

        self.job_logger.debug('evaluating triggers...')

        for trigger_data in self.parsed_json['triggers']:
            trigger_class = dynamic_import_trigger(trigger_data['className'])
            trigger = trigger_class(self.job_id, trigger_data, self.job_logger)
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
        """runs the actions of a job"""
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
            action_class = dynamic_import_action(action_data['className'])
            action = action_class(action_data, working_dir, self.job_run_logger)

            result = action.run()

            if ((result is not const.SUCCESS) and
                    (result is not const.UNSTABLE) and
                        (result is not const.FAILURE)):
                logging.error('job action returned an invalid result: ' + result)
                # TODO: throw/error job here

            job_status = result

        self.job_run_logger.info(job_status)

        self.last_run_status = job_status

        with open(os.path.join(self.job_dir, 'job.stats'), 'w') as stats_file:
            json.dump({
                       "last_run": self.last_run.isoformat(),
                       "last_run_status": self.last_run_status},
                      stats_file)

        self.is_running = False


class JobManager(object):
    """manages the loading and scheduling of jobs
        maintains a list of jobs and a queue
    """
    def __init__(self, jobs_dir):
        self.interrupt = False
        self.job_queue = Queue.PriorityQueue()
        self.jobs_dir = jobs_dir

        job_files = glob.glob(self.jobs_dir + '/*/*.json')
        self.jobs = []

        for job_file in job_files:
            with open(job_file) as job_file_handle:
                job_id = os.path.basename(os.path.dirname(job_file))
                job_json = json.load(job_file_handle)
                job_dir = os.path.dirname(job_file)
                stats_file = os.path.join(job_dir, 'job.stats')
                stats = {}
                if os.path.isfile(stats_file):
                    with open(stats_file) as stats:
                        stats = json.load(stats)
                self.jobs.append(Job(job_id, job_dir, job_json, stats))

    def refresh_job_schedules(self):
        """calls update_schedule on all jobs"""
        for job in self.jobs:
            if not job.is_running:
                job.update_schedule()

    def refresh_job_queue(self):
        """clears and re-initializes the job queue"""
        while not self.job_queue.empty():
            try:
                self.job_queue.get()
            except Queue.Empty:
                continue

        for job in self.jobs:
            self.job_queue.put((job.next_scheduled_run, job))

    def start(self):
        """starts executing jobs"""
        self.refresh_job_queue()

        timeout = 5

        logging.debug('starting job manager')

        while not self.interrupt:
            job = self.job_queue.get()[1] # 0th tuple value is priority

            if datetime.datetime.now() > job.next_scheduled_run:
                logging.debug('Running ' + job.name + ' at ' + str(datetime.datetime.now()) +
                              ' scheduled at ' + str(job.next_scheduled_run))
                job.run()
                time.sleep(timeout)

            self.refresh_job_schedules()
            self.refresh_job_queue()

            time.sleep(timeout)

    def request_run(self, job_name):
        """request a job to run immediately"""
        for job in self.jobs:
            if job_name == job.job_id:
                job.run_now()
                return True
        return False

    def is_job(self, job_id):
        """returns true if the job is in the job_list, false otherwise"""
        for job in self.jobs:
            if job_id == job.job_id:
                return True
        return False

    def get_jobs_list(self):
        """returns the job_list"""
        serializable_list = []
        for job in self.jobs:
            serializable_list.append(job.serialize())
        return serializable_list

    def stop(self):
        """interrupts the job handling loop"""
        self.interrupt = True
