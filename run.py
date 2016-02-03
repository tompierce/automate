"""
Main entry point for AuTOMate - an automation and continuous integration server
Author: Tom Pierce - tom.pierce0@gmail.com
"""
import sys
sys.path.append('server')
from server.server import server

if __name__ == "__main__":
    server()
