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

def download_traces(traces_dir, config_filename):
   """
   Download traces from the remote location specified in the constants
   REMOTE_BASE and REMOTE_TRACE_SETS.
   Save the downloaded traces in the traces_dir directory provided by user.
   """
   if config_filename != None:
      print 'TODO: Download from Config:', traces_dir
   else:
      path = os.path.dirname(os.path.abspath(__file__))
      subdirs = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
      ext_traces_dir = os.sep + traces_dir

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


def generate_expected(traces_dir, exp_dir, config_filename):
   if config_filename != None:
      print 'TODO: Expected from Config:', traces_dir, exp_dir
   else:
      path = os.path.dirname(os.path.abspath(__file__))
      subdirs = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]

      if (traces_dir not in subdirs):
         print 'Expected %s sub-directory, but it does not exist' % traces_dir
         sys.exit(1)
      else:
         ext_exp_dir = os.sep + exp_dir
         if (exp_dir not in subdirs):
   	      os.mkdir(path + ext_exp_dir)

      print 'Generating expected output from traces in ' + traces_dir + '...'

      i = 0
      for trace_set in REMOTE_TRACE_SETS:
         for trace in trace_set:
      	  src = path + os.sep + traces_dir + os.sep + trace
      	  copy(src, path + os.sep + trace)

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
   	      os.remove(path + os.sep + trace)

      print 'Completed generating expected outputs'

def generate_test(exp_dir, config_filename):
   if config_filename != None:
      print 'TODO: Test from Config:', exp_dir
   else:
      todo = 'TODO: Implement generate_test(). Need to check output of Netcheck with the'
      todo += ' expected output generated previously.'
      print todo

##############################################
# Helper functions for option/argument parsing
##############################################


def init_options(parser):
   DFLT_DWNLD_DIR = 'program_traces'
   DFLT_TEST_DIR = 'expected_outputs'

   hlp_d = 'Download the program traces and save them in the specified directory. '
   hlp_d += 'Default value is "' + DFLT_DWNLD_DIR + '"'
   
   hlp_e = 'Generate the expected NetCheck output from the downloaded program traces.'

   hlp_t = 'Test NetCheck against the generated expected outputs to be found in the specified directory. '
   hlp_t += 'Default value is "' + DFLT_TEST_DIR + '"'

   hlp_c = 'If this argument is passed, then the program will use the config file for getting traces or running NetCheck.'

   parser.add_argument('-d', '--download',nargs='?',const=DFLT_DWNLD_DIR,metavar=('DOWNLOAD_DIRECTORY'),type=str,help=hlp_d)
   parser.add_argument('-e', '--expected',nargs=2,metavar=('TRACES_DIRECTORY', 'OUTPUT_DIRECTORY'),type=str,help=hlp_e)
   parser.add_argument('-t', '--test',nargs='?',const=DFLT_TEST_DIR,metavar=('EXPECTED_OUTPUTS_DIRECTORY'),type=str,help=hlp_t)   
   parser.add_argument('-c', '--configfile',nargs='?',metavar=('CONFIG_FILE'),type=str,help=hlp_c)


def too_many_args(args):
   download = args.download != None 
   expected = args.expected != None
   test = args.test != None

   # XOR the input arguments to determine if more than 1 was passed
   if   (download != (expected or test)) \
	 and (expected != (download or test)) \
	 and (test != (download or expected)):
      return True
   else:
      return True


##############################################
# If this script is executed, then run the tests
##############################################
if __name__ == "__main__":
   import argparse
   desc = 'Run integration tests on NetCheck. The user must specify exactly 1 of '
   desc += 'the 3 action arguments: [-d, -e, -t]'
   parser = argparse.ArgumentParser(description=desc)
   init_options(parser)
   args = parser.parse_args()

   if too_many_args(args):
      err = 'Please specify exactly 1 action argument. Use the -h argument for help'
      print err
      sys.exit(1)

   if args.download != None:
      download_traces(args.download, args.configfile)
      sys.exit(0)
   elif args.expected != None:
      generate_expected(args.expected[0], args.expected[1], args.configfile)
      sys.exit(0)
   elif args.test != None:
      generate_test(args.test, args.configfile)
      sys.exit(0)
   else:
      print 'Please pass exactly 1 action argument. Use the -h argument for help'
      sys.exit(1)
