#! /usr/bin/env python

"""
Gurkaran Singh Poonia
Start Date: March 24, 2014

This file runs integration tests on NetCheck. There are 3 action arguments [-d, -e, -t].
The user must specify exactly 1 of these every time integration_tests.py is run.

The 3 Action Arguments:

1) Download Traces (-d, --download):
   - downloads traces (that will be used to run NetCheck) using the 'wget' tool.
   - either (if config file is specified by '-c') parses config file to determine trace names.
   - otherwise uses the REMOTE_BASE and REMOTE_TRACE_SETS constants specified below.
   - the default directory to save the downloaded traces to is 'program_traces/'.

2) Generate Expected Outputs (-e, --expected):
   - generates expected outputs of NetCheck
   - assumes that the NetCheck version this runs on is semantically correct
   - if no config file is provided (via the '-c' argument), then this will run NetCheck using 
     the '-u' argument.

3) Test Current Version of NetCheck (-t, --test):
   - tests the output of NetCheck against expected outputs using the 'diff' tool.
   - if no config file is provided (via the '-c' argument), then this will run NetCheck using 
     the '-u' argument.
   - the default directory to find expected outputs in is 'expected_outputs/'

----------------------

Using Config Files (-c, --configfile):
- used to specify a NetCheck config file. 
- the configfile is used for the 3 cases above as follows:

1) Download traces:
   In this case, integration_tests.py will parse the provided config file and determine
   which traces to download. It will NOT use the constants REMOTE_BASE, and REMOTE_TRACE_SETS.

2) Generate Expected Outputs and Test NetCheck:
   In both of these cases, integration_tests.py will use the config file for running
   NetCheck, instead of using the '-u' argument to run NetCheck.

---------------------

Assumptions and Dependencies:
1) Since integration_tests.py uses the 'wget' and 'diff' command line tools,
   the user should have these tools installed and run integration_tests.py in a 
   Linux environment (cygwin also works).
"""

from shutil import copy
import subprocess as sp
import os, sys


##############################################
# Main functions for the 3 options/arguments
##############################################

# a string indicating the root base URL of the traces to be downloaded
REMOTE_BASE = 'http://blackbox.poly.edu/program_traces/semantic_traces/'

# a list of tuples, where each tuple has the trace names that will be used 
# together to run NetCheck. All traces in this list are downloaded.
REMOTE_TRACE_SETS = [ 
      ('close_block_recv.strace.client.linux','close_block_recv.strace.server.linux'),
      ('conn_progress_recv.strace.linux.client','conn_progress_recv.strace.linux.server')
      ]

def download_traces(traces_dir, config_filename):
   """
   Download traces from the remote location specified in the constants
   REMOTE_BASE and REMOTE_TRACE_SETS or the config file argument.
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
   """
   Run NetCheck and save the outputs in the exp_dir directory provided by user.
   """
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
   """
   Run NetCheck and compare output against the expected output (obtained from the
   exp_dir provided by user).
   """
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
   """
   Initialize the command line options for this script.
   """
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


def normalize_dir(dir_name):
   """
   Removes the '/' from the end of dir_name is it exists.
   Returns the normalized directory name
   """
   if (dir_name[-1] == os.sep):
      dir_name = dir_name[:-1]

   return dir_name


def too_many_args(args):
   """
   Return True is user passed in more than 1 action argument, False otherwise
   """
   download = args.download != None 
   expected = args.expected != None
   test = args.test != None

   if (download and (expected or test)) \
	 or (expected and (download or test)) \
	 or (test and (download or expected)):
      return True
   else:
      return False


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
      err = 'Too Many Action Arguments. '
      err += 'Please specify exactly 1 action argument. Use the -h argument for help'
      print err
      sys.exit(1)

   if args.download != None:
      download_traces(normalize_dir(args.download), args.configfile)
      sys.exit(0)
   elif args.expected != None:
      generate_expected(normalize_dir(args.expected[0]), normalize_dir(args.expected[1]), args.configfile)
      sys.exit(0)
   elif args.test != None:
      generate_test(normalize_dir(args.test), args.configfile)
      sys.exit(0)
   else:
      print 'Please specify exactly 1 action argument. Use the -h argument for help'
      sys.exit(1)
