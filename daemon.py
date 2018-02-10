import sys, os, time, atexit, signal, yaml
import os, sys
import time, datetime
import atexit
import signal


global config
with open("/home/pi/BatteryMonitor/config.yaml", 'r') as stream:
	config = yaml.load(stream)

def xfrange(start, stop, step=0.01):
        i = 0
        while start + i * step < stop:
                yield round(start + i * step, 2)
                i += 1

if 'voltages' not in config.keys():

        config['voltages'] = { tuple(xfrange(3.25,3.34)) : 0,
                                  tuple(xfrange(3.35,3.45)) : 25,
                                  tuple(xfrange(3.46,3.67)) : 50,
                                  tuple(xfrange(3.68,4.09)) : 75,
                                  tuple(xfrange(4.09,5.00)) : 100}


class LogginSystem(object):

        def __init__(self, file_location='./battery-monitor.log'):
                self.log_file = open(file_location, 'a+')

        def write(self, message):
                self.log_file.write(message)

        def __del__(self):
                self.log_file.close()



class Daemon(object):

        def __init__(self, pidfile=config['agent']['pidfile'], stdin='/dev/null',
                     stdout='/dev/null', stderr='/dev/null'):
		self.log_file = LogginSystem()
                self.stdin = stdin
                self.stdout = stdout
                self.stderr = stderr
                self.pidfile = pidfile


        def daemonize(self):
                def daemonize(self):
                        """
                        do the UNIX double-fork magic, see Stevens' "Advanced
                        Programming in the UNIX Environment" for details (ISBN 0201563177)
                        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
                        """
                        try:
                                pid = os.fork()
                                if pid > 0:
                                        # exit first parent
                                        sys.exit(0)
                        except OSError, e:
                                sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
                                sys.exit(1)
               
                        # decouple from parent environment
                        os.chdir("/")
                        os.setsid()
                        os.umask(0)
               
                        # do second fork
                        try:
                                pid = os.fork()
                                if pid > 0:
                                        # exit from second parent
                                        sys.exit(0)
                        except OSError, e:
                                sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
                                sys.exit(1)
               
                        # redirect standard file descriptors
                        sys.stdout.flush()
                        sys.stderr.flush()
                        si = file(self.stdin, 'r')
                        so = file(self.stdout, 'a+')
                        se = file(self.stderr, 'a+', 0)
                        os.dup2(si.fileno(), sys.stdin.fileno())
                        os.dup2(so.fileno(), sys.stdout.fileno())
                        os.dup2(se.fileno(), sys.stderr.fileno())
               
                        # write pidfile
                        atexit.register(self.delpid)
                        pid = str(os.getpid())
                        file(self.pidfile,'w+').write("%s\n" % pid)
                        #self.create_pidfile()

        def attach_stream(self, name, mode):

                stream = open(getattr(self, name), mode)
                os.dup2(stream.fileno(), getattr(sys, name).fileno())


        def dettach_env(self):

                os.chdir("/")
                os.setsid()
                os.umask(0)


        def delpid(self):

                os.remove(self.pidfile)


        def start(self):
                pid = self.get_pid()
                if pid:
                    message = "BatteryMonitor agent already running?"
                    sys.stderr.write(message % self.pidfile)
                    sys.exit(1)

                self.daemonize()
                
                self.run()


        def get_pid(self):

                try:
                        pf = open(self.pidfile,'r')
                        pid = int(pf.read().strip())
                        pf.close()
                except (IOError, TypeError):
                        pid = None
                return pid


        def stop(self, silent=False):

                pid = self.get_pid()

                if not pid:
                        if not silent:
                                message = "BatteryMonitor agent not running?"
                                sys.stderr.write(message % self.pidfile)
                        return
                try:
                        while True:
                                os.kill(pid, signal.SIGTERM)
                                time.sleep(0.1)
                except OSError as err:
                        err = str(err)
                        if err.find("No such process") > 0:
                                if os.path.exists(self.pidfile):
                                        os.remove(self.pidfile)
                        else:
                                sys.stdout.write(str(err))
                                sys.exit(1)


        def restart(self):

                self.stop(silent=True)
                self.start()


        def run(self):

                raise NotImplementedError


