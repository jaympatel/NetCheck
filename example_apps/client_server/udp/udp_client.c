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

int main(int argc, char *argv[])
{
	int sockfd;
	struct addrinfo hints, *servinfo, *p;
	int rv;
	int numbytes;

	if (argc != 2) {
		fprintf(stderr,"usage: %s hostname\n", argv[0]);
		exit(1);
	}

	memset(&hints, 0, sizeof hints);
	hints.ai_family = AF_INET; // IPv4
	hints.ai_socktype = SOCK_DGRAM; // UDP Datagram sockets

	if ((rv = getaddrinfo(argv[1], CNXN_PORT, &hints, &servinfo)) != 0) {
		fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
		return 1;
	}

	// loop through all the results and make a socket
	for(p = servinfo; p != NULL; p = p->ai_next) {
		if ((sockfd = socket(p->ai_family, p->ai_socktype,
						p->ai_protocol)) == -1) {
			perror("udp_client: socket");
			continue;
		}

		break;
	}

	if (p == NULL) {
		fprintf(stderr, "udp_client: failed to bind socket\n");
		return 2;
	}

	int packet_size = 0;
	for (packet_size = INIT_PACKET_SIZE; packet_size <= MAX_PACKET_SIZE; packet_size += PACKET_SIZE_INCREMENT) {
		char msg[packet_size];
		memset(msg, 'a', packet_size-1);
		msg[packet_size] = '\0';
		if ((numbytes = sendto(sockfd, msg, packet_size, 0,
						p->ai_addr, p->ai_addrlen)) == -1) {
			perror("udp_client: sendto");
			exit(1);
		}
		printf("udp_client: sent %d bytes to %s\n", numbytes, argv[1]);
	}

	// Send the shudown message numberous times to ensure
	// that it gets through to the server
	int i = 0;
	for (i = 0; i < 10; i++) {
		if ((numbytes = sendto(sockfd, SHUTDOWN_MESSAGE, strlen(SHUTDOWN_MESSAGE), 0,
						p->ai_addr, p->ai_addrlen)) == -1) {
			perror("udp_client: sendto");
			exit(1);
		}
	}

	printf("udp_client: sent \"%s\" to shutdown server\n", SHUTDOWN_MESSAGE);
	freeaddrinfo(servinfo);
	close(sockfd);
	return 0;
}
