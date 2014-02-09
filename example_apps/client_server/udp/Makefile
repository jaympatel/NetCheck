CC=gcc
CFLAGS=-Wall -Werror -g -Wextra -Wno-unused-parameter

all: udp_server udp_client
udp_server: udp_server.o
udp_client: udp_client.o

udp_server.o: udp_server.c cnxn_constants.h
udp_client.o: udp_client.c cnxn_constants.h
clean:
	-rm -rf udp_server.o udp_client.o udp_server udp_client
