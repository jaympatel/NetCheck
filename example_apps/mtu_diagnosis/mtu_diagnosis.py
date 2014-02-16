"""
Gurkaran Singh Poonia
Start Date: February 12, 2014

Purpose: 
To analyze the provided data about packet transmission and determine
whether or not an MTU issue has occured. 

The statistical analysis done by this file to determine MTU issue are based
on the imports from diagnosis_constants.py. The heuristics used are as follows:
- Create buckets of size BUCKET_SIZE and put all the message tuples in these 
  buckets based on the size of the messages.
- The following 3 criteria need to hold in order to declare MTU issue:

  1) PACKET_LOSS_PACKETS_SENT percent of the packets sent must be lost 
     from the messages sent. Ex: If 10 'aaa's are sent, then
     PACKET_LOSS_PACKETS_SENT percent of these must be lost.
     
  2) PACKET_LOSS_TOTAL_SENT percent of the packets sent must be lost 
     from the total messages sent during the entire trace.
     Ex: If 10 'aaa' messages are sent, and 20 'bbb' messages are sent,
     then PACKET_LOSS_TOTAL_SENT percent of these must be lost from each of
     the 'aaa' and 'bbb' messages for them to contribute to the MTU issue.
     
  3) Atleast MIN_BUCKETS_WITH_LOSS must have enough packet loss as decribed
     above.


The main interface function for this file is check_mtu_issue().
"""


import diagnosis_constants as const
from operator import itemgetter
import math



def check_mtu_issue(accept_tuples, connect_tuples):
    """
    listof (int,int,int), listof (int,int,int) -> Bool

    produces True if MTU issue occured, False otherwise
    
    Both the parameters must be tuples that contain (per message sent):
    (packets_sent, packets_lost, packet_size)

    ### test0: empty lists means no MTU error ###
    
    >>> check_mtu_issue([], [])
    False
    
    
    #### test1: 0 packets lost means no MTU issue ####
    
    >>> test_tuples1 = [(10,0,100)]
    >>> check_mtu_issue([], test_tuples1)
    False

    >>> check_mtu_issue(test_tuples1, [])
    False
    
    >>> check_mtu_issue(test_tuples1, test_tuples1)
    False
    
    
    ### test2: Not enough buckets for MTU issue ###
    
    >>> test_tuples2 = [(10,10,100)]
    >>> check_mtu_issue([], test_tuples2)
    False

    >>> check_mtu_issue(test_tuples2, [])
    False
    
    >>> check_mtu_issue(test_tuples2, test_tuples2)
    False
    
    
    ### test3: MTU issue in the tuples and enough buckets ###
    
    >>> test_tuples3 = [(10,10,500), (50,50,250), (5,5,50)]
    >>> check_mtu_issue(test_tuples3, [])
    True
    
    >>> check_mtu_issue([], test_tuples3)
    True
    
    >>> check_mtu_issue(test_tuples3, test_tuples3)
    True
    
    
    ### test4: MTU issue, and spread out buckets with issues ###
    
    >>> test_tuples4 = [(5,0,500), (10,10,50), (15,15,150), (10,2,400), (8,1, 240), (14,14,1000), (7,1,789)]
    >>> check_mtu_issue(test_tuples4, [])
    True
    
    >>> check_mtu_issue([], test_tuples4)
    True
    
    >>> check_mtu_issue(test_tuples4, test_tuples4)
    True
    """
    if not accept_tuples and not connect_tuples:
        return False
    
    # Put the packets into buckets
    buckets_a = create_buckets(accept_tuples)
    buckets_c = create_buckets(connect_tuples)
    
    # Get total packets sent from all messages
    total_p_sent_a = get_total_packets_sent(accept_tuples)
    total_p_sent_c = get_total_packets_sent(connect_tuples)
    
    buckets_w_ploss = 0
    
    # See if there's messages that contribute to the MTU issue
    # in the buckets for accept_tuples.
    for bucket in buckets_a:
        if not bucket:
            continue
        else:
            for packets_sent, packets_lost, packet_size in bucket:
                ploss_total_sent = get_ploss_total(packets_lost, total_p_sent_a)
                if packets_lost >= const.PACKET_LOSS_PACKETS_SENT \
                   and ploss_total_sent >= const.PACKET_LOSS_TOTAL_SENT:
                    buckets_w_ploss += 1
                
    # See if there's messages that contribute to the MTU issue
    # in the buckets for connect_tuples.                
    for bucket in buckets_c:
        if not bucket:
            continue
        else:        
            for packets_sent, packets_lost, packet_size in bucket:
                ploss_total_sent = get_ploss_total(packets_lost, total_p_sent_c)
                if packets_lost >= const.PACKET_LOSS_PACKETS_SENT \
                   and ploss_total_sent >= const.PACKET_LOSS_TOTAL_SENT:
                    buckets_w_ploss += 1    
    
    # If enough buckets have lost enough packets, then 
    # we declare that an MTU issue has occured in the 
    # tranimission trace.
    if buckets_w_ploss >= const.MIN_BUCKETS_WITH_LOSS:
        return True
    else:
        return False



def create_buckets(input_tuples):
    """
    listof (int,int,int) -> listof listof (int,int,int)
        
    Creates buckets with sizes as specified in 'const' import
    
    >>> create_buckets([])
    []
    
    >>> create_buckets([(5,0,100)])
    [[(5, 0, 100)]]
    
    >>> create_buckets([(5,0,100), (10,2,50), (2,1,150)])
    [[(5, 0, 100), (10, 2, 50)], [(2, 1, 150)]]
    
    >>> create_buckets([(5,0,100), (10,2,50), (2,1,350)])
    [[(5, 0, 100), (10, 2, 50)], [], [], [(2, 1, 350)]]
    """
    if not input_tuples:
        return []
    else:
        total_buckets = get_total_buckets(input_tuples)
        
        # initialize list with total_buckets lists in it representing the buckets
        buckets = []
        for i in xrange(total_buckets):
            buckets.append([])
              
        for packets_sent, packets_lost, packet_size in input_tuples:
            bucket = buckets[get_bucket_num(packet_size)]
            bucket.append((packets_sent, packets_lost, packet_size))
        
        return buckets



def get_total_packets_sent(input_tuples):
    """
    listof (int,int,int) -> int
        
    Return the total packets sent in all the messages
    
    >>> get_total_packets_sent([])
    0
    
    >>> get_total_packets_sent([(5,0,100)])
    5
    
    >>> get_total_packets_sent([(5,0,100), (10,2,50), (2,1,150)])
    17
    
    >>> get_total_packets_sent([(55,0,100), (10,2,50), (105,1,350)])
    170
    """
    total_packets_sent = 0
    for packets_sent, _, _ in input_tuples:
        total_packets_sent += packets_sent
    return total_packets_sent



def get_ploss_total(packets_lost, total_packets_sent):
    """
    int, int -> float
    
    Return percentage of packet loss that occured in packet_lost
    compared to the total_number of packet sent
    
    >>> get_ploss_total(0, 0)    
    0.0
    
    >>> get_ploss_total(10, 100)
    0.1
    
    >>> get_ploss_total(100, 100)
    1.0
    
    >>> get_ploss_total(200, 0)
    0.0
    
    >>> get_ploss_total(12, 150)
    0.08
    """
    if total_packets_sent == 0:
        return 0.0
    else:
        return float(packets_lost) / total_packets_sent



def get_total_buckets(input_tuples):
    """    
    listof (int,int,int) -> int
    
    Returns the number of buckets that will be needed
    based on constants specified in 'const' import
    
    >>> get_total_buckets([])
    0
    
    >>> get_total_buckets([(2, 0, 100)])
    1
    
    >>> get_total_buckets([(2, 0, 100), (2,0,200)])
    2
    
    >>> get_total_buckets([(2, 0, 100), (2,0,210)])
    3
    """
    if not input_tuples:
        return 0
    else:
        largest_packet_size = max(input_tuples, key=itemgetter(2))[2]
        total_buckets = math.ceil(float(largest_packet_size) / const.BUCKET_SIZE)
        return math.trunc(total_buckets)



def get_bucket_num(packet_size):
    """
    int -> int
    
    Determine which bucket this packet goes into based on its size
    
    >>> get_bucket_num(0)
    0
    
    >>> get_bucket_num(80)
    0
    
    >>> get_bucket_num(100)
    0
    
    >>> get_bucket_num(150)
    1
    
    >>> get_bucket_num(200)
    1
    
    >>> get_bucket_num(201)
    2
    """
    if packet_size == 0:
        return 0
    else:
        bucket_num = math.ceil(float(packet_size) / const.BUCKET_SIZE)
        return math.trunc(bucket_num) - 1



def convert_to_percentage(input_tuples):
    """
    listof (int,int,int) -> listof (int,float,int)
    
    Converts the given list of (packets_sent, packets_lost, packet_size) tuples
    into (packets_sent, packets_lost_percentage, packet_size)
    
    >>> convert_to_percentage([])
    []
    
    >>> convert_to_percentage([(2, 1, 100)])
    [(2, 0.5, 100)]
    
    >>> convert_to_percentage([(5, 0, 100)])
    [(5, 0.0, 100)]

    >>> convert_to_percentage([(2, 1, 100), (4, 1, 100)])
    [(2, 0.5, 100), (4, 0.25, 100)]
    
    >>> convert_to_percentage([(2, 0, 100), (4, 1, 100), (5, 2, 100)])
    [(2, 0.0, 100), (4, 0.25, 100), (5, 0.4, 100)]
    """
    perc_list = []
    for packets_sent, packets_lost, packet_size in input_tuples:
        perc_packets_lost = float(packets_lost) / packets_sent
        perc_list.append((packets_sent, perc_packets_lost, packet_size))
        
    return perc_list



# Make sure doctests run when script is run
if __name__ == '__main__':
    import doctest
    EPS = 1.0e-6  # for testing equality on floats
    print doctest.testmod(verbose=False)