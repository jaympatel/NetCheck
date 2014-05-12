import sys, socket, time

DEBUG = True
TIMEOUT_SECONDS = 15


def send_to_neighbours(neighbours, sock):
	packet_size = 100
	while packet_size <= 4800:
		msg = 'A' * packet_size
		for i in range(10):
			for neighbour in neighbours:
				their_ip = neighbour['ip']
				their_port = neighbour['port']
				sock.sendto(msg, (their_ip, their_port))
		packet_size += 100


def recv_from_neighbours(my_port, sock):		
		sock.settimeout(TIMEOUT_SECONDS)
		while True:
			data, addr = sock.recvfrom(4096) # buffer size is 4096 bytes
			if DEBUG:
			 	print 'Received Message: ', data
			  	print 'Message Length: ', len(data)
			  	print 'Address recv\'d from: ', addr
			 	print


def get_neighbours(file_name):
	neighbours = []
	neighbours_file = open(file_name, 'U')
	for line in neighbours_file:
		if line.strip() != '':
			split_line = line.split(',')
			n_ip = split_line[0].strip()
			n_port = int(split_line[1].strip())
			neighbours.append({'ip':n_ip, 'port':n_port}) 
	return neighbours


if __name__ == '__main__':
	if (len(sys.argv) != 3):
		print 'usage: %s <my port number> <file with neighbours>' % sys.argv[0]
		sys.exit(1)
	
	my_port = int(sys.argv[1])
	neighbours = get_neighbours(sys.argv[2])
	
	if DEBUG:
		print
		print 'My Port: ', my_port
		i = 0
		while i < len(neighbours):
			print 'My Neighbour #%i: ' % i, neighbours[i]
			i += 1
		print

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	sock.bind(('', my_port)) # listen on all available interfaces
	time.sleep(15) # so all nodes can bind to sockets

	send_to_neighbours(neighbours, sock)
	recv_from_neighbours(my_port, sock)

	if DEBUG:
		print 'Done!'
	sys.exit(0)
	