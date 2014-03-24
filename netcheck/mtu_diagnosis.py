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
    total_packets_sent = 0
    for packets_sent, _, _ in input_tuples:
        total_packets_sent += packets_sent
    return total_packets_sent



def get_ploss_total(packets_lost, total_packets_sent):
    if total_packets_sent == 0:
        return 0.0
    else:
        return float(packets_lost) / total_packets_sent



def get_total_buckets(input_tuples):
    if not input_tuples:
        return 0
    else:
        largest_packet_size = max(input_tuples, key=itemgetter(2))[2]
        total_buckets = math.ceil(float(largest_packet_size) / const.BUCKET_SIZE)
        return math.trunc(total_buckets)



def get_bucket_num(packet_size):
    if packet_size == 0:
        return 0
    else:
        bucket_num = math.ceil(float(packet_size) / const.BUCKET_SIZE)
        return math.trunc(bucket_num) - 1



def convert_to_percentage(input_tuples):
    perc_list = []
    for packets_sent, packets_lost, packet_size in input_tuples:
        perc_packets_lost = float(packets_lost) / packets_sent
        perc_list.append((packets_sent, perc_packets_lost, packet_size))
        
    return perc_list
