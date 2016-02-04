"""main application thread"""
import os
import threading
import logging
from server.server_base import HTTP_SERVER
from server.jobs import JobManager

SERVER_ROOT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')

def server():
    """launch the job manager and server threads"""
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger("sh").setLevel(logging.WARNING)

    logging.info('Starting AuTOMate server...')

    job_manager = JobManager(os.path.join(SERVER_ROOT_DIR, 'jobs'))
    job_manager_thread = threading.Thread(target=job_manager.start)
    job_manager_thread.start()

    HTTP_SERVER.set_job_manager(job_manager)
    HTTP_SERVER.run(use_reloader = False)

    job_manager.stop()
    job_manager_thread.join()
