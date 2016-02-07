"""defines the routes for the http server"""
from flask import Flask, jsonify, abort, redirect, send_file

class HTTPServer(Flask):
    """wraps a flask server to augment it with a job_manager"""
    def __init__(self, import_name):
        Flask.__init__(self, import_name, static_folder='public', static_url_path='')

    def set_job_manager(self, job_manager):
        """lazily initialize the HTTP servers's job_manager"""
        self.job_manager = job_manager # pylint: disable=attribute-defined-outside-init

HTTP_SERVER = HTTPServer(__name__)
HTTP_SERVER.debug = True

@HTTP_SERVER.errorhandler(404)
def not_found(error):
    """error handler for 404s"""
    response = jsonify({'code': 404,'message': 'Not found'})
    response.status_code = 404
    return response

@HTTP_SERVER.route('/')
def index():
    """serve the homepage"""
    return redirect("/index.html")

@HTTP_SERVER.route('/jobs')
def list_jobs():
    """return a list of jobs"""
    return jsonify(job_list=HTTP_SERVER.job_manager.get_jobs_list())

@HTTP_SERVER.route('/logs/<job_id>')
def show_log_for_job(job_id):
    """return the most recent log for a job"""
    if HTTP_SERVER.job_manager.is_job(job_id):
        return send_file('../jobs/' + job_id + '/job.last_run.log')
    else:
        abort(404)

@HTTP_SERVER.route('/job/<job_id>', methods=['POST'])
def start_job(job_id):
    """trigger a job to start"""
    if not HTTP_SERVER.job_manager.request_run(job_id):
        abort(404)
    return jsonify(status='success', job_id=job_id)
