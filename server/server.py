import os, threading, signal, time
import SimpleHTTPServer, SocketServer
from jobs import JobManager
from logging import log

PORT = 8000
SERVER_ROOT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')

log("Server Root: " + SERVER_ROOT_DIR)

def create_http_server(port):
    log('Running on port: ' + str(port))
    public_dir = os.path.join(SERVER_ROOT_DIR, 'public')
    os.chdir(public_dir)
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    return SocketServer.TCPServer(("", PORT), Handler)
        
def main():
    log('Starting server...')
    
    http_server = create_http_server(PORT)
    http_server_thread = threading.Thread(target=http_server.serve_forever)
    http_server_thread.start()
       
    job_manager = JobManager(os.path.join(SERVER_ROOT_DIR, 'jobs'))
    job_manager_thread = threading.Thread(target=job_manager.start)
    job_manager_thread.start()
    
    def signal_handler(signal, frame):
        log('Shutting down server...')
        http_server.shutdown()
        job_manager.stop()
        http_server_thread.join()
        job_manager_thread.join()
        log('Done.')
        exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    
    while(True):
        time.sleep(10)
    
if __name__ == "__main__":
    main()
