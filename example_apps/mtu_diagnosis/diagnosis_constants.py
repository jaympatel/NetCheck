"""
Gurkaran Singh Poonia
Start Date: February 12, 2014

Purpose: 
This file contains constants used by the diagnosis logic to determine
whether certain issues have occured or not.
"""

############################################
# Below the MTU issue diagnosis constants.
#
# For more information on how these are used,
# see the documentation in mtu_diagnosis.py
############################################

# This 'percentage' (specified as a fraction) of the total
# packets must be lost by the specific message beign analyzed
# for it to be declared as contributing to the MTU issue.
PACKET_LOSS_TOTAL_SENT = .05

# This 'percentage' (specified as a fraction) of the packets
# sent in the specific message must be lost for it to be 
# declared as contributing to the MTU issue.
PACKET_LOSS_PACKETS_SENT = 1

# Create buckets of this size while calculating MTU issue.
# Remember to change tests in mtu_diagnosis.py if this value changes.
BUCKET_SIZE = 100

# If this many buckets have enough packet loss, then we declare
# that an MTU issue has occured.
MIN_BUCKETS_WITH_LOSS = 3