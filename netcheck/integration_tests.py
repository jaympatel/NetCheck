#! /usr/bin/env python
#
# Gurkaran Singh Poonia
# Start Date: March 24, 2014
#
# Purpose: Run integration tests for NetCheck
#
# NOTE: Assumes that the system running this is Linux and 
# has the 'wget' shell tool available.

from shutil import copy
import subprocess as sp
import os, sys


##############################################
# Main functions for the 3 options/arguments
##############################################

REMOTE_BASE = 'http://blackbox.poly.edu/program_traces/semantic_traces/'
REMOTE_TRACE_SETS = [ 
      ('close_block_recv.strace.client.linux','close_block_recv.strace.server.linux'),
      ('conn_progress_recv.strace.linux.client','conn_progress_recv.strace.linux.server')
      ]

def download_traces(traces_dir):
   """
   Download traces from the remote location specified in the constants
   REMOTE_BASE and REMOTE_TRACE_SETS.
   Save the downloaded traces in the traces_dir directory provided by user.
   """
   path = os.path.dirname(os.path.abspath(__file__))
   subdirs = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
   ext_traces_dir = '/' + traces_dir

   if (traces_dir in subdirs):
      os.chdir(path + ext_traces_dir)
   else:
      os.mkdir(path + ext_traces_dir)
      os.chdir(path + ext_traces_dir)

   print 'Downloading traces...'

   for trace_set in REMOTE_TRACE_SETS:
      for trace in trace_set:
	 trace = REMOTE_BASE + trace 
	 if (sp.call(['wget', '-q', '-nc', trace]) != 0):
	    print 'Error retreiving file:', trace

   print 'Successfully downloaded all traces'


def generate_expected(exp_dir, traces_dir):
   path = os.path.dirname(os.path.abspath(__file__))
   subdirs = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

   if (traces_dir not in subdirs):
      print 'Expected %s sub-directory, but it does not exist' % traces_dir
      sys.exit(1)
   else:
      ext_exp_dir = '/' + exp_dir
      if (exp_dir not in subdirs):
	 os.mkdir(path + ext_exp_dir)

   print 'Generating expected output from traces in ' + traces_dir + '...'

   i = 0
   for trace_set in REMOTE_TRACE_SETS:
      for trace in trace_set:
	 src = path + '/' + traces_dir + '/' + trace
	 copy(src, path + '/' + trace)

      cmd = ['python', 'netcheck.py', '-u']
      cmd.extend(trace_set[:])
      output = sp.check_output(cmd, stderr=sp.STDOUT)
      if output == '':
	 print 'Error running NetCheck on:', trace_set
      else:
	 os.chdir(path + ext_exp_dir)
	 f = open('test' + str(i) + '.txt', 'w')
	 i += 1
	 f.write(output)
	 f.close()
	 os.chdir(path)

      for trace in trace_set:
	 os.remove(path + '/' + trace)

   print 'Completed generating expected outputs'

def generate_test(exp_dir):
   todo = 'TODO: Implement generate_test(). Need to check output of Netcheck with the'
   todo += ' expected output generated previously.'
   print todo

##############################################
# Helper functions for option/argument parsing
##############################################


def init_options(parser):
   dft_d = 'program_traces'
   hlp_d = 'download the program traces and save them in the specified directory.'
   hlp_d += ' Default value is "' + dft_d + '"'
   
   e_dir = '[dir to save expected output in]'
   d_dir = '[dir to find program traces in]'
   hlp_e = 'generate the expected NetCheck output from the downloaded program traces.'
   hlp_e += ' Need 2 parameters: %s %s' % (e_dir, d_dir)
   
   dft_t = 'expected_outputs'
   hlp_t = 'test NetCheck against the generated expected outputs to be found in the specified directory.'
   hlp_t += ' Default value is "' + dft_t + '"'

   parser.add_argument('-d', '--download',nargs='?',const=dft_d,type=str,help=hlp_d)
   parser.add_argument('-e', '--expected',nargs=2,type=str,help=hlp_e)
   parser.add_argument('-t', '--test',nargs='?',const=dft_t,type=str,help=hlp_t)


def too_many_args(args):
   download = args.download != None 
   expected = args.expected != None
   test = args.test != None

   if (download and expected) \
	 or (download and test) \
	 or (expected and test):
      return True
   else:
      return False


##############################################
# If this script is executed, then run the tests
##############################################
if __name__ == "__main__":
   import argparse
   desc = 'Run integration tests on NetCheck.'
   parser = argparse.ArgumentParser(description=desc)
   init_options(parser)
   args = parser.parse_args()

   if too_many_args(args):
      err = 'Too many arguments specified.'
      err += ' Please specify exactly 1 argument: [-d, -e, -t]'
      print err
      sys.exit(1)

   if args.download != None:
      download_traces(args.download)
      sys.exit(0)
   elif args.expected != None:
      generate_expected(args.expected[0], args.expected[1])
      sys.exit(0)
   elif args.test != None:
      generate_test(args.test)
      sys.exit(0)
   else:
      print 'Please pass exactly 1 argument: [-d, -e, -t]'
      sys.exit(1)


