"""
Steven Portzer
Start Date: 07/1/2012

Purpose: To order system calls from traces collected across multiple trace.

usage: python trace_ordering.py CONFIG_FILE

"""

import model_network_syscalls as model
import trace_output
import ip_matching
import sys



class NoValidOrderingException(Exception):
  pass


# System calls that received data over the network.
RECV_SYSCALLS = [
  "recv_syscall", "recvfrom_syscall", "recvmsg_syscall", "read_syscall"
]

# System calls that send data over the network.
SEND_SYSCALLS = [
  "send_syscall", "sendto_syscall", "sendmsg_syscall", "sendfile_syscall",
  "write_syscall", "writev_syscall"
]

# System calls whose relative ordering we care about across traces.
ORDERED_SYSCALLS = RECV_SYSCALLS + SEND_SYSCALLS + [
  "accept_syscall", "connect_syscall", "close_syscall", "implicit_close",
  "poll_syscall", "select_syscall", "shutdown_syscall", "listen_syscall"
]



def verify_traces(config_filename):
  """
  Takes the name of a configuration file and runs the traces referenced
  by the configuration file through the model.
  """

  traces_generators = ip_matching.initialize_hosts(config_filename)
  trace_output.log_intialize(traces_generators.keys())

  syscall_dict = {}

  for trace_id in traces_generators:
    try:
      syscall_dict[trace_id] = traces_generators[trace_id].next()
    except StopIteration:
      pass

  while syscall_dict:

    next_syscall_index = choose_next_syscall(syscall_dict.values())

    try:
      syscall_dict[next_syscall_index] = traces_generators[next_syscall_index].next()
    except StopIteration:
      del syscall_dict[next_syscall_index]

  trace_output.log_done()



def verify_unit_test(trace_filenames):
  """
  Takes a list of traces produced by a unit test and runs them through
  the model.
  """

  traces_generators = ip_matching.initialize_unit_test(trace_filenames)
  trace_output.log_intialize(traces_generators.keys())

  syscall_dict = {}

  for trace_id in traces_generators:
    try:
      syscall_dict[trace_id] = traces_generators[trace_id].next()
    except StopIteration:
      pass

  while syscall_dict:

    next_syscall_index = choose_next_syscall(syscall_dict.values())

    try:
      syscall_dict[next_syscall_index] = traces_generators[next_syscall_index].next()
    except StopIteration:
      del syscall_dict[next_syscall_index]

  trace_output.log_done()



def choose_next_syscall(syscall_list):
  """
  Takes a list of system call tuples and decides which of these calls to
  do next. The trace id for the system call we decided to perform is
  returned, or if no action is possible an exception is raised.
  """

  syscall_list.sort(key=syscall_priority)

  for syscall in syscall_list:
    if verify_syscall(syscall):
      return syscall[1][0]

  syscall_err_list = []
  for syscall in syscall_list:
    err = get_syscall_err(syscall)
    syscall_err_list.append((syscall, err))

  trace_output.log_execution_blocked(syscall_err_list)
  raise NoValidOrderingException("No valid action exists")


def syscall_priority(syscall):
  """
  Returns the priority of the system call. The lower the number, the
  higher the priority.
  """

  name, args, ret = syscall

  if name not in ORDERED_SYSCALLS:
    return 0

  if name == 'select_syscall':
    if model.care_about_fd_list(args[0], args[1]) and (isinstance(ret[0], int)
        or model.care_about_fd_list(args[0], ret[0])):
      return 1
    else: # Don't care about the call
      return 0

  if name == 'poll_syscall':
    if model.care_about_fd_list(args[0], args[1]) and (isinstance(ret[0], int)
        or model.care_about_fd_list(args[0], ret[0][0])):
      return 1
    else: # Don't care about the call
      return 0

  # Make sure the socket is one we care about.
  sock = syscall[1][:2]
  if sock not in model.active_sockets:
    return 0

  socket = model.sockets[sock]

  # Make sure if there is a remote address involved that we care about it.
  ip, port = None, None

  if name == 'accept_syscall':
    trace_id, fd, ip, port = args
  elif name == 'recvfrom_syscall':
    trace_id, sock, msg, buf_len, flags, ip, port = args
  elif name == 'recvmsg_syscall':
    trace_id, sock, msg, buf_len, ip, port, flags = args
  elif name == 'connect_syscall':
    trace_id, sock, ip, port = args
  elif name == 'sendto_syscall':
    trace_id, sock, msg, flags, ip, port = args
  elif name == "sendmsg_syscall":
    trace_id, sock, msg, ip, port, flags = args

  if not ip and socket['protocol'] == model.IPPROTO_UDP and name in SEND_SYSCALLS:
    ip, port = socket['peer_ip'], socket['peer_port']

  if ip and ip not in model.broadcast_ip and ip_matching.addr_dont_care(ip, port):
    return 0

  # We care about these calls, so now order them according to our rules.

  if name == 'accept_syscall':
    return 1
  elif name in RECV_SYSCALLS:
    return 1

  elif name == 'connect_syscall':
    if socket['protocol'] == model.IPPROTO_UDP:
      return 0
    return 2
  elif name in SEND_SYSCALLS:
    return 2

  elif name == 'listen_syscall':
    return 3
  elif name in ["close_syscall", "implicit_close", "shutdown_syscall"]:
    if socket['state'] not in ['CONNECTED', 'LISTEN']:
      return 0
    return 3

  raise Exception("Failed to handle priority of " + name)


def verify_syscall(syscall):
  """
  Tries to preform the given system call. If it succeeds True is returned
  and the model is updated accordingly. Otherwise, False is returned and
  the model is not updated.
  """

  try:
    model_call(syscall)

  except model.SyscallError, err:
    trace_output.log_syscall_attempt(syscall, err)
    return False

  except model.SyscallException, err:
    trace_output.log_syscall(syscall, err)

  else:
    trace_output.log_syscall(syscall)

  return True


def get_syscall_err(syscall):
  """
  Returns the Exception, if any, raised by executing the system call in
  the model.
  """

  try:
    model_call(syscall)

  except Exception, err:
    return err


def model_call(syscall):
  """
  Takes a given system call and attempts to execute it in the posix model.
  If we fail to model the call then we raise SyscallError, SyscallWarning,
  or SyscallDontCare depending on what failed.
  """

  name, args, ret = syscall
  impl_ret, impl_errno = ret

  try:

    ##### SOCKET #####
    if name == 'socket_syscall':
      trace_id, dom, typ, prot = args
      model_ret = model.socket_syscall(trace_id, dom, typ, prot, impl_ret)

    ##### BIND #####
    elif name == 'bind_syscall':
      trace_id, sock, addr, port = args
      model_ret = model.bind_syscall(trace_id, sock, addr, port, impl_errno)

    ##### LISTEN #####
    elif name == 'listen_syscall':
      trace_id, sock, log = args
      model_ret = model.listen_syscall(trace_id, sock, log, impl_errno)

    ##### ACCEPT #####
    elif name == 'accept_syscall':
      trace_id, fd, ip, port = args
      model_ret = model.accept_syscall(trace_id, fd, ip, port, impl_ret, impl_errno)

    ##### CONNECT ##### 
    elif name == 'connect_syscall':
      trace_id, sock, addr, port = args
      model_ret = model.connect_syscall(trace_id, sock, addr, port, impl_errno)

    ##### SEND #####
    elif name == 'send_syscall':
      trace_id, sock, msg, flag = args
      model_ret = model.send_syscall(trace_id, sock, msg, flag, impl_ret, impl_errno)
    
    ##### WRITE #####
    elif name == 'write_syscall':
      trace_id, sock, msg = args
      model_ret = model.send_syscall(trace_id, sock, msg, 0, impl_ret, impl_errno)
    
    ##### WRITEV #####
    elif name == 'writev_syscall':
      trace_id, sock, msg, count = args
      model_ret = model.send_syscall(trace_id, sock, msg, 0, impl_ret, impl_errno)

    ##### SENDTO #####
    elif name == 'sendto_syscall':
      trace_id, sock, msg, flags, remoteip, remoteport = args
      model_ret = model.sendto_syscall(trace_id, sock, msg, impl_ret, flags, remoteip, remoteport, impl_errno)

    ##### SENDMSG #####
    elif name == "sendmsg_syscall":
      trace_id, sock, msg, remoteip, remoteport, flags = args
      model_ret = model.sendto_syscall(trace_id, sock, msg, impl_ret, flags, remoteip, remoteport, impl_errno)

    ##### SENDFILE #####
    elif name == "sendfile_syscall":
      trace_id, out_sock, in_sock, offset, count = args
      model_ret = model.sendfile_syscall(trace_id, out_sock, in_sock, offset, count, impl_ret, impl_errno)

    ##### RECVFROM #####
    elif name == 'recvfrom_syscall':
      trace_id, sock, msg, buf_len, flags, ip, port = args
      model_ret = model.recvfrom_syscall(trace_id, sock, buf_len, flags, ip, port, msg, impl_ret, impl_errno)

    ##### RECVMSG #####
    elif name == "recvmsg_syscall":
      trace_id, sock, msg, buf_len, remoteip, remoteport, flags = args
      model_ret = model.recvfrom_syscall(trace_id, sock, buf_len, flags, remoteip, remoteport, msg, impl_ret, impl_errno)

    ##### RECV #####
    elif name == 'recv_syscall':
      trace_id, sock, msg, buf_len, flag = args
      model_ret = model.recv_syscall(trace_id, sock, buf_len, flag, msg, impl_ret, impl_errno)

    ##### READ #####
    elif name == 'read_syscall':
      trace_id, sock, msg, buf_len = args
      model_ret = model.recv_syscall(trace_id, sock, buf_len, 0, msg, impl_ret, impl_errno)

    ##### CLOSE #####
    elif name == 'close_syscall' or name == 'implicit_close':
      trace_id, sock = args
      model_ret = model.close_syscall(trace_id, sock, impl_errno)

    ##### SETSOCKOPT #####
    elif name == 'setsockopt_syscall':
      trace_id, sockfd, level, optname, optval = args
      model_ret = model.setsockopt_syscall(trace_id, sockfd, level, optname, optval)

    ##### GETSOCKOPT #####
    elif name == 'getsockopt_syscall':
      trace_id, sockfd, level, optname = args
      model_ret = model.getsockopt_syscall(trace_id, sockfd, level, optname)

    ##### GETPEERNAME #####
    elif name == 'getpeername_syscall':
      trace_id, sock = args
      peer_addr, peer_port = impl_ret
      model_ret = model.getpeername_syscall(trace_id, sock, peer_addr, peer_port)

    ##### GETSOCKNAME #####
    elif name == 'getsockname_syscall':
      trace_id, sock = args
      sock_ip, sock_port = impl_ret
      model_ret = model.getsockname_syscall(trace_id, sock, sock_ip, sock_port)

    ##### IOCTL #####
    elif name == 'ioctl_syscall':
      trace_id, fd, cmd, val = args
      model_ret = model.ioctl_syscall(trace_id, fd, cmd, val)

    ##### FCNTL #####
    elif name == 'fcntl_syscall':
      model_ret = model.fcntl_syscall(impl_ret, *args)

    ##### SELECT #####
    elif name == 'select_syscall':
      trace_id, readfds, writefds, errorfds, timeout = args
      model_ret = model.select_syscall(trace_id, readfds, writefds, errorfds, timeout, impl_ret, impl_errno)

    ##### POLL #####
    elif name == 'poll_syscall':
      trace_id, new_pollin, new_pollout, new_pollerr, timeout = args
      model_ret = model.poll_syscall(trace_id, new_pollin, new_pollout, new_pollerr, timeout, impl_ret, impl_errno)

    ##### SHUTDOWN #####
    elif name == 'shutdown_syscall':
      trace_id, sock, how = args
      model_ret = model.shutdown_syscall(trace_id, sock, how)

    else:
      raise model.SyscallNotice(name, 'UNKNOWN_SYSCALL', "'" + name + "' is not a recognized system call.")

  except model.SyscallError, err:
    if impl_ret == -1 and isinstance(impl_errno, str) and impl_errno in err.args[1]:
      return

    raise err

  if impl_ret == -1:
    raise model.SyscallWarning(name, 'UNEXPECTED_SUCCESS', "Model succeeded but implementation failed.")

  if impl_ret != model_ret[0]:
    raise model.SyscallWarning(name, 'UNEXPECTED_RETURN_VALUE', "Model returned " + str(model_ret[0]))



def main():

  if len(sys.argv) >= 2 and sys.argv[1] == '-u':
    try:
      verify_unit_test(sys.argv[2:])
    except NoValidOrderingException:
      pass

  elif len(sys.argv) == 2:
    try:
      verify_traces(sys.argv[1])
    except NoValidOrderingException:
      pass

  else:
    print "usage: python trace_ordering.py CONFIG_FILE"


if __name__ == "__main__":
  main()

