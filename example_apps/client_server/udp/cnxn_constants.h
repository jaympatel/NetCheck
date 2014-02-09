#ifndef _CONNECTION_CONSTANTS_H_
#define _CONNECTION_CONSTANTS_H_

// the port that the client and server talk through
#define CNXN_PORT "54453"

// the message that client sends to shutdown the server
#define SHUTDOWN_MESSAGE "done"

// client sends packets based on constants below
#define INIT_PACKET_SIZE        100
#define MAX_PACKET_SIZE         4800
#define PACKET_SIZE_INCREMENT  100

#endif // _CONNECTION_CONSTANTS_H_
