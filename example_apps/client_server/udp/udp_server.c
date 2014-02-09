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


int set_servinfo(struct addrinfo** servinfo) {
	struct addrinfo hints;
	memset(&hints, 0, sizeof hints);
	hints.ai_family = AF_INET; // IPv4
	hints.ai_socktype = SOCK_DGRAM; // UDP Datagram sockets
	hints.ai_flags = AI_PASSIVE; // use my IP

	return getaddrinfo(NULL, CNXN_PORT, &hints, servinfo);
}

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
	const char* shutdown_str = "done";

	if ((rv = set_servinfo(&servinfo)) != 0) {
		fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
		return 1;
	}
	
	if (get_socket_fd(servinfo, &sockfd) == NULL) {
		fprintf(stderr, "udp_server: failed to bind socket\n");
		return 2;
	}

	freeaddrinfo(servinfo);

	printf("udp_server: waiting to recvfrom...\n");
	int done = 1;
	addr_len = sizeof their_addr;
	do {    
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
		// printf("udp_server: packet contains \"%s\"\n", buf);
		done = strncmp(buf, shutdown_str, strlen(shutdown_str) - 1);
		memset(buf, 0x0, numbytes);
	} while (done != 0);
	printf("udp_server: received \"%s\", shutting down server\n", shutdown_str);
	close(sockfd);
	return 0;
}
