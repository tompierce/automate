import os, threading, signal, time, logging, json
from server_base import http_server
from jobs import JobManager

SERVER_ROOT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')

def server():

    logging.getLogger().setLevel(logging.DEBUG)
    logging.getLogger("sh").setLevel(logging.WARNING)

    logging.debug('Starting server as ' + __name__ )
           
    job_manager = JobManager(os.path.join(SERVER_ROOT_DIR, 'jobs'))
    job_manager_thread = threading.Thread(target=job_manager.start)
    job_manager_thread.start()

    http_server.set_job_manager(job_manager)
    http_server.run(use_reloader = False)
    
    job_manager.stop()
    job_manager_thread.join()