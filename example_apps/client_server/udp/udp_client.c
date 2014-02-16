/*
 ** udp_client.c -- a datagram client
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
int set_servinfo(const char* hostname, struct addrinfo** servinfo) {
	struct addrinfo hints;	
	memset(&hints, 0, sizeof hints);
	hints.ai_family = AF_INET; // IPv4
	hints.ai_socktype = SOCK_DGRAM; // UDP Datagram sockets

	return getaddrinfo(hostname, CNXN_PORT, &hints, servinfo);
}

// use the servinfo linkedlist to get a socket to use
// set sockfd to the socket that we will use
//
// returns NULL if failed, the addrinfo of the socket if succeded
struct addrinfo* get_socket_fd(struct addrinfo* servinfo, int* sockfd) {
	struct addrinfo* p;
	// loop through all the results and make a socket
	for(p = servinfo; p != NULL; p = p->ai_next) {
		if ((*sockfd = socket(p->ai_family, p->ai_socktype,
						p->ai_protocol)) == -1) {
			perror("udp_client: socket");
			continue;
		}

		break;
	}
	return p;
}

// Send the shudown message to the server
void send_shutdown_message(int sockfd, const struct addrinfo* p) {
	int numbytes = -1;
	if ((numbytes = sendto(sockfd, SHUTDOWN_MESSAGE, strlen(SHUTDOWN_MESSAGE), 0,
					p->ai_addr, p->ai_addrlen)) == -1) {
		perror("udp_client: sendto");
		exit(1);
	}
	printf("udp_client: sent \"%s\" to shutdown server\n", SHUTDOWN_MESSAGE);
}

int main(int argc, char *argv[])
{
	struct addrinfo* p;
	int sockfd;
	struct addrinfo *servinfo;
	int rv;
	int numbytes;
	const char* hostname = argv[1];

	if (argc != 2) {
		fprintf(stderr,"usage: %s hostname\n", argv[0]);
		exit(1);
	}

	if ((rv = set_servinfo(hostname, &servinfo)) != 0) {
		fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
		return 1;
	}

	if ((p = get_socket_fd(servinfo, &sockfd)) == NULL) {
		fprintf(stderr, "udp_client: failed to bind socket\n");
		return 2;
	}

	// do not need servinfo anymore
	freeaddrinfo(servinfo);

	int packet_size = 0;
	int packet_count = 0;
	for (packet_size = INIT_PACKET_SIZE;
			packet_size <= MAX_PACKET_SIZE;
			packet_size += PACKET_SIZE_INCREMENT) {
		
		packet_count++;
		// If we have sent 10 packets already...
		if (packet_count > 10) {
			// resent packet_count
			packet_count = 0;

			// ... then sleep for 10 milliseconds to prevent conjestion
			sleep(0.01);
	
		}
		// Fill up a buffer of size packet_size with
		// 'a's to send a packet to server
		char msg[packet_size];
		memset(msg, 'a', packet_size-1);
		msg[packet_size] = '\0';

		// send the 'packet' just made to the server
		if ((numbytes = sendto(sockfd, msg, packet_size, 0,
						p->ai_addr, p->ai_addrlen)) == -1) {
			perror("udp_client: sendto");
			exit(1);
		}
		printf("udp_client: sent %d bytes to %s\n", numbytes, hostname);
	}

	send_shutdown_message(sockfd, p);
	close(sockfd);
	return 0;
}
