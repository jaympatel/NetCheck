/*
 ** udp_server.c -- a datagram sockets server
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

#include "cnxn_constants.h"


// populate the servinfo structure which is a 
// pointer to a linked list of useful network
// information about the host
//
// returns non-zero error code if failed,
//                  and zero otherwise.
int set_servinfo(struct addrinfo** servinfo) {
	struct addrinfo hints;
	memset(&hints, 0, sizeof hints);
	hints.ai_family = AF_INET; // IPv4
	hints.ai_socktype = SOCK_DGRAM; // UDP Datagram sockets
	hints.ai_flags = AI_PASSIVE; // use my IP

	return getaddrinfo(NULL, CNXN_PORT, &hints, servinfo);
}

// use the servinfo linkedlist to get a socket to bind to
// set sockfd to the socket that we binded to
//
// returns NULL if failed, the addrinfo of what we binded to if succeded
struct addrinfo* get_socket_fd(struct addrinfo* servinfo, int* sockfd) {
	struct addrinfo* p;
	// loop through all the results and bind to the first we can
	for(p = servinfo; p != NULL; p = p->ai_next) {
		if ((*sockfd = socket(p->ai_family, p->ai_socktype,
						p->ai_protocol)) == -1) {
			perror("udp_server: socket");
			continue;
		}

		if (bind(*sockfd, p->ai_addr, p->ai_addrlen) == -1) {
			close(*sockfd);
			perror("udp_server: bind");
			continue;
		}

		break;
	}
	return p;
}

// get sockaddr, IPv4 or IPv6:
void *get_in_addr(struct sockaddr *sa)
{
	if (sa->sa_family == AF_INET) {
		return &(((struct sockaddr_in*)sa)->sin_addr);
	}

	return &(((struct sockaddr_in6*)sa)->sin6_addr);
}

int main(void)
{
	int sockfd;
	struct addrinfo *servinfo;
	int rv;
	int numbytes;
	struct sockaddr_storage their_addr;
	char buf[MAX_PACKET_SIZE];
	socklen_t addr_len;
	char s[INET6_ADDRSTRLEN];
	int shutdown = 1;

	if ((rv = set_servinfo(&servinfo)) != 0) {
		fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
		return 1;
	}

	if (get_socket_fd(servinfo, &sockfd) == NULL) {
		fprintf(stderr, "udp_server: failed to bind socket\n");
		return 2;
	}

	// no longer need servinfo
	freeaddrinfo(servinfo);

	addr_len = sizeof their_addr;
	printf("udp_server: waiting to recvfrom...\n");

	// Main loop that runs until the shutdown message is received
	// The shutdown message is defined in cnxn_constants.h
	do {   
		// wait and receive messages on sockfd 
		if ((numbytes = recvfrom(sockfd, buf, MAX_PACKET_SIZE-1 , 0,
						(struct sockaddr *)&their_addr, &addr_len)) == -1) {
			perror("recvfrom");
			exit(1);
		}

		printf("udp_server: got packet from %s\n",
				inet_ntop(their_addr.ss_family,
					get_in_addr((struct sockaddr *)&their_addr),
					s, sizeof s));
		printf("udp_server: packet is %d bytes long\n", numbytes);
		buf[numbytes] = '\0';

		// check if the received message was the shutdown message
		shutdown = strncmp(buf, SHUTDOWN_MESSAGE, strlen(SHUTDOWN_MESSAGE) - 1);

		// reset the buffer for the next message
		memset(buf, 0x0, numbytes);
	} while (shutdown != 0);
	printf("udp_server: received \"%s\", shutting down server\n", SHUTDOWN_MESSAGE);
	close(sockfd);
	return 0;
}
