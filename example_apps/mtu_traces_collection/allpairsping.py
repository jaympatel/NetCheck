import sys, socket, threading

DEBUG = True
TIMEOUT_SECONDS = 5

def send_to_neighbours(neighbours):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
	for neighbour in neighbours:
		their_ip = neighbour['ip']
		their_port = neighbour['port']
		sock.sendto('ping', (their_ip, their_port))

def recv_from_neighbours(my_port):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
		sock.bind(('', my_port)) # listen on all available interfaces
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

	send_to_neighbours(neighbours)
	recv_from_neighbours(my_port)

	if DEBUG:
		print 'Done!'
	sys.exit(0)
	