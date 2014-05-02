#! /usr/bin/env python

"""
Gurkaran Singh Poonia
Start Date: March 24, 2014

This file runs integration tests on NetCheck. There are 3 action arguments [-d, -e, -t].
The user must specify exactly 1 of these every time integration_tests.py is run.

The 3 Action Arguments:

1) Download Traces (-d, --download):
   - downloads traces (that will be used to run NetCheck) using the 'wget' tool.
   - either (if config file is specified by '-c') parses config file to determine trace names
     and uses REMOTE_BASE as the remote base.
   - otherwise uses the REMOTE_BASE and REMOTE_TRACE_SETS constants specified below.
   - the default directory to save the downloaded traces to is 'program_traces/'.

2) Generate Expected Outputs (-e, --expected):
   - generates expected outputs of NetCheck
   - assumes that the NetCheck version this runs on is semantically correct
   - if no config file is provided (via the '-c' argument), then this will run NetCheck using 
     the '-u' argument.

3) Test Current Version of NetCheck (-t, --test):
   - tests the output of NetCheck against expected outputs using the 'diff' tool.
   - saves output of all 'diff's in integration_test_results/ if the outputs differ.
   - Reports integration tests as fail if any outputs differ, pass if all outputs are the same
   - if no config file is provided (via the '-c' argument), then this will run NetCheck using 
     the '-u' argument.

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

from shutil import copy, move
import subprocess as sp
import os, sys


##############################################
# Main functions for the 3 options/arguments
##############################################

# a string indicating the root base URL of the traces to be downloaded
REMOTE_BASE = 'http://blackbox.poly.edu/program_traces/semantics/'

# a list of tuples, where each tuple has the trace names that will be used 
# together to run NetCheck. All traces in this list are downloaded.
REMOTE_TRACE_SETS = [ 
      ('close_block_recv.strace.client.linux','close_block_recv.strace.server.linux'),
      ('conn_progress_recv.strace.linux.client','conn_progress_recv.strace.linux.server')
      ]

def download_traces(traces_dir, config_filename):
   """
   Download traces from the remote location specified in the constants
   REMOTE_BASE and either REMOTE_TRACE_SETS or the config file argument.
   Save the downloaded traces in the traces_dir directory provided by user.
   """
   use_config_file = config_filename != None

   # If using config file, then fetch trace names from the config file
   if use_config_file:
      remote_traces = get_trace_names(config_filename)
   # otherwise use the constant in this file
   else:
      remote_traces = REMOTE_TRACE_SETS

   path = get_path()
   subdirs = get_subdirs(path)
   ext_traces_dir = os.sep + traces_dir

   # if the directory with traces exists, then chdir to it
   if (traces_dir in subdirs):
      os.chdir(path + ext_traces_dir)
   # otherwise make that directory and chdir to it
   else:
      os.mkdir(path + ext_traces_dir)
      os.chdir(path + ext_traces_dir)

   print 'Downloading traces...'

   # get the all specfied traces (specified in remote_traces)
   # from the REMOTE_BASE constant
   for trace_set in remote_traces:
      for trace in trace_set:
   	  trace = REMOTE_BASE + trace 
   	  if (sp.call(['wget', '-q', '-nc', trace]) != 0):
   	     print 'Error retreiving file:', trace

   print 'Successfully downloaded all traces'


def generate_expected(traces_dir, output_dir, config_filename):
   """
   Run NetCheck and save the outputs in the output_dir directory provided by user.
   """
   use_config_file = config_filename != None

   path = get_path()
   subdirs = get_subdirs(path)

   # if traces directory is not a subdirectory, then report error and exit
   if (traces_dir not in subdirs):
      print 'Expected %s sub-directory, but it does not exist' % traces_dir
      sys.exit(1)

   # if the outputs directory does not exist, then create it
   ext_output_dir = os.sep + output_dir
   if (output_dir not in subdirs):
	   os.mkdir(path + ext_output_dir)

   print 'Generating expected output from traces in ' + traces_dir + '...'

   # If using config file, then fetch trace names from the config file
   if use_config_file:
      traces = get_trace_names(config_filename)
   # otherwise use the constant in this file
   else:
      traces = REMOTE_TRACE_SETS

   # loop through the trace sets and run NetCheck on all of them.
   i = 0
   for trace_set in traces:
      
      # copy all the traces from the traces_dir into NetCheck's working directory
      for trace in trace_set:
   	  src = path + os.sep + traces_dir + os.sep + trace
   	  copy(src, path + os.sep + trace)

      if use_config_file:
         cmd = ['python', 'netcheck.py', config_filename]
      else:
         cmd = ['python', 'netcheck.py', '-u']
         cmd.extend(trace_set[:])
      
      # run Netcheck and save the output in the specified directory in file
      output = sp.check_output(cmd, stderr=sp.STDOUT)
      if output == '':
   	  print 'Error running NetCheck on: ', trace_set
      else:
   	  os.chdir(path + ext_output_dir)
   	  f = open('expected_output-' + str(i) + '.txt', 'w')
   	  i += 1
   	  f.write(output)
   	  f.close()
   	  os.chdir(path)

      # done with the traces, so remove them from NetCheck's working directory
      for trace in trace_set:
	      os.remove(path + os.sep + trace)

   print 'Completed generating expected outputs'


def generate_test(traces_dir, output_dir, config_filename):
   """
   Run NetCheck and compare output against the expected output (obtained from the
   output_dir provided by user).
   """
   use_config_file = config_filename != None

   path = get_path()
   subdirs = get_subdirs(path)

   # if traces directory is not a subdirectory, then report error and exit
   if (traces_dir not in subdirs):
      print 'Expected %s sub-directory, but it does not exist' % traces_dir
      sys.exit(1)

   # if output directory is not a subdirectory, then report error and exit
   if (output_dir not in subdirs):
      print 'Expected %s sub-directory, but it does not exist' % output_dir
      sys.exit(1)
   else:
      ext_output_dir = os.sep + output_dir

   # if the integration_test_results dir does not exist, then create it
   test_results = 'integration_test_results'
   ext_test_results = os.sep + test_results
   if (test_results not in subdirs):
      os.mkdir(path + ext_test_results)

   print 'Creating current NetCheck outputs...'

   # If using config file, then fetch trace names from the config file
   if use_config_file:
      traces = get_trace_names(config_filename)
   # otherwise use the constant in this file
   else:
      traces = REMOTE_TRACE_SETS

   i = 0
   for trace_set in traces:
      for trace in trace_set:
        src = path + os.sep + traces_dir + os.sep + trace
        copy(src, path + os.sep + trace)

      if use_config_file:
         cmd = ['python', 'netcheck.py', config_filename]
      else:
         cmd = ['python', 'netcheck.py', '-u']
         cmd.extend(trace_set[:])

      output = sp.check_output(cmd, stderr=sp.STDOUT)
      if output == '':
        print 'Error running NetCheck on: ', trace_set
      else:
        os.chdir(path + ext_output_dir)
        f = open('current_output-' + str(i) + '.txt', 'w')
        i += 1
        f.write(output)
        f.close()
        os.chdir(path)

      for trace in trace_set:
         os.remove(path + os.sep + trace)

   os.chdir(path + ext_output_dir)
   files = get_files(path + ext_output_dir)
   output_dict = create_output_tuples(files)

   print 'Completed creating NetCheck outputs'
   print
   print 'Testing current NetCheck output against the expected NetCheck output...'

   test_fail = False
   for output_num, output_files in output_dict.iteritems():
      cur_output_file = output_files[0]
      exp_output_file = output_files[1]
      cmd = ['diff', exp_output_file, cur_output_file]
      try:
         shell_output = sp.check_output(cmd, stderr=sp.STDOUT)
      except sp.CalledProcessError as e:
         os.chdir(path + ext_test_results)
         f = open('diff_outputs-' + str(output_num) + '.txt', 'w')
         f.write(e.output)
         f.close()
         os.chdir(path + ext_output_dir)
         test_fail = True
      
   print 'Completed testing NetCheck outputs'

   print
   print '------------------ RESULT -----------------'
   if test_fail:
      print 'NetCheck did not pass the integration tests. Please see the diff_output files in \'tests/integration_tests/%s\' for more information' % test_results
   else:
      print 'NetCheck passed the intergration tests!'
   print '-------------------------------------------'

   clean_up(path + os.sep + traces_dir, path + ext_output_dir, path + ext_test_results)


def get_trace_names(config_filename):
   """
   Returns a list with a single tuple in it. 
   The tuple is of the traces that are used in the config file.
   """
   traces = []
   f = open(config_filename, 'U')
   for line in f:
      if line.strip() != '':
         if 'trace' in line:
            trace_name = line.strip().split(' ')[1]
            traces.append(trace_name)
   return [tuple(traces)]


##############################################
# Helper functions for the 3 action arguments
##############################################

def get_path():
   """
   Return the path to the current directory
   """
   return os.path.dirname(os.path.abspath(__file__))


def get_subdirs(current_dir):
   """
   Returns a list of all the subdirectories in current_dir
   """
   return [name for name in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, name))]


def get_files(current_dir):
   """
   Returns a list of all the files in current_dir
   """
   return [name for name in os.listdir(current_dir) if os.path.isfile(os.path.join(current_dir, name))]


def create_output_tuples(files):
   """
   Return a dict of current output and the corresponding expected output files.
   Key:   The Number of the files [0,1,...]
   Value: A List of the files as [current output file, expected output file]
   """
   output_dict = {}
   
   for file_name in sorted(files):
      key = file_name.split('-')[-1].split('.')[0]
      if key in output_dict:
         output_dict[key].append(file_name)
      else:
         output_dict[key] = [file_name]

   return output_dict


def clean_up(traces_path, output_path, integ_results_path):
   """
   Move all the integration tests related directories to the appropriate spot
   (i.e., under tests/integration_tests)
   """
   path = get_path()

   # create a time-stamp based folder to store all integration tests results
   results_folder_name = get_time_stamp()
   results_folder_path = path + os.sep + 'tests' + os.sep + 'integration_tests' + os.sep + results_folder_name
   os.mkdir(results_folder_path)
   move(traces_path, results_folder_path)
   move(output_path, results_folder_path)
   move(integ_results_path, results_folder_path)

def get_time_stamp():
   """
   Returns the current time stamp 
   """
   from time import gmtime, strftime
   return strftime("%Y-%m-%d-%H-%M-%S", gmtime())

##############################################
# Helper functions for option/argument parsing
##############################################

def init_options(parser):
   """
   Initialize the command line options for this script.
   """
   DFLT_DWNLD_DIR = 'program_traces'

   hlp_d = 'Download the program traces and save them in the specified directory. '
   hlp_d += 'Default value is "' + DFLT_DWNLD_DIR + '"'
   
   hlp_e = 'Generate the expected NetCheck output from the downloaded program traces.'

   hlp_t = 'Test NetCheck against the generated expected outputs to be found in the specified directory.'

   hlp_c = 'If this argument is passed, then the program will use the config file for getting traces or running NetCheck.'

   parser.add_argument('-d', '--download',nargs='?',const=DFLT_DWNLD_DIR,metavar=('DOWNLOAD_DIRECTORY'),type=str,help=hlp_d)
   parser.add_argument('-e', '--expected',nargs=2,metavar=('TRACES_DIRECTORY', 'OUTPUT_DIRECTORY'),type=str,help=hlp_e)
   parser.add_argument('-t', '--test',nargs=2,metavar=('TRACES_DIRECTORY', 'OUTPUT_DIRECTORY'),type=str,help=hlp_t)   
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
      generate_test(normalize_dir(args.test[0]), normalize_dir(args.test[1]), args.configfile)
      sys.exit(0)
   else:
      print 'Please specify exactly 1 action argument. Use the -h argument for help'
      sys.exit(1)
