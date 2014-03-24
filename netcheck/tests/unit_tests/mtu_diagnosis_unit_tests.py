"""
Gurkaran Singh Poonia
Start Date: March 23, 2014

- This file contains unit doc tests for the functions in mtu_diagnosis.py.
- To run the tests, run the following command from the netcheck/ directory:
  'python -m tests.unit_tests.mtu_diagnosis_unit_tests'

- Also note that the functions below are not necessary, the tests
  are divided as such simply for clarity.
"""

import mtu_diagnosis as mtu


def test_check_mtu_issue():
    """
    listof (int,int,int), listof (int,int,int) -> Bool

    produces True if MTU issue occured, False otherwise
    
    Both the parameters must be tuples that contain (per message sent):
    (packets_sent, packets_lost, packet_size)

    ### test0: empty lists means no MTU error ###
    
    >>> mtu.check_mtu_issue([], [])
    False
    
    
    #### test1: 0 packets lost means no MTU issue ####
    
    >>> test_tuples1 = [(10,0,100)]
    >>> mtu.check_mtu_issue([], test_tuples1)
    False

    >>> mtu.check_mtu_issue(test_tuples1, [])
    False
    
    >>> mtu.check_mtu_issue(test_tuples1, test_tuples1)
    False
    
    
    ### test2: Not enough buckets for MTU issue ###
    
    >>> test_tuples2 = [(10,10,100)]
    >>> mtu.check_mtu_issue([], test_tuples2)
    False

    >>> mtu.check_mtu_issue(test_tuples2, [])
    False
    
    >>> mtu.check_mtu_issue(test_tuples2, test_tuples2)
    False
    
    
    ### test3: MTU issue in the tuples and enough buckets ###
    
    >>> test_tuples3 = [(10,10,500), (50,50,250), (5,5,50)]
    >>> mtu.check_mtu_issue(test_tuples3, [])
    True
    
    >>> mtu.check_mtu_issue([], test_tuples3)
    True
    
    >>> mtu.check_mtu_issue(test_tuples3, test_tuples3)
    True
    
    
    ### test4: MTU issue, and spread out buckets with issues ###
    
    >>> test_tuples4 = [(5,0,500), (10,10,50), (15,15,150), (10,2,400), (8,1, 240), (14,14,1000), (7,1,789)]
    >>> mtu.check_mtu_issue(test_tuples4, [])
    True
    
    >>> mtu.check_mtu_issue([], test_tuples4)
    True
    
    >>> mtu.check_mtu_issue(test_tuples4, test_tuples4)
    True
    """
    return

def test_create_buckets():
    """
    listof (int,int,int) -> listof listof (int,int,int)
        
    Creates buckets with sizes as specified in 'const' import
    
    >>> mtu.create_buckets([])
    []
    
    >>> mtu.create_buckets([(5,0,100)])
    [[(5, 0, 100)]]
    
    >>> mtu.create_buckets([(5,0,100), (10,2,50), (2,1,150)])
    [[(5, 0, 100), (10, 2, 50)], [(2, 1, 150)]]
    
    >>> mtu.create_buckets([(5,0,100), (10,2,50), (2,1,350)])
    [[(5, 0, 100), (10, 2, 50)], [], [], [(2, 1, 350)]]
    """
    return

def test_get_total_packets_sent():
    """
    listof (int,int,int) -> int
        
    Return the total packets sent in all the messages
    
    >>> mtu.get_total_packets_sent([])
    0
    
    >>> mtu.get_total_packets_sent([(5,0,100)])
    5
    
    >>> mtu.get_total_packets_sent([(5,0,100), (10,2,50), (2,1,150)])
    17
    
    >>> mtu.get_total_packets_sent([(55,0,100), (10,2,50), (105,1,350)])
    170
    """
    return

def test_get_ploss_total():
    """
    int, int -> float
    
    Return percentage of packet loss that occured in packet_lost
    compared to the total_number of packet sent
    
    >>> mtu.get_ploss_total(0, 0)    
    0.0
    
    >>> mtu.get_ploss_total(10, 100)
    0.1
    
    >>> mtu.get_ploss_total(100, 100)
    1.0
    
    >>> mtu.get_ploss_total(200, 0)
    0.0
    
    >>> mtu.get_ploss_total(12, 150)
    0.08
    """
    return

def test_get_total_buckets():
    """    
    listof (int,int,int) -> int
    
    Returns the number of buckets that will be needed
    based on constants specified in 'const' import
    
    >>> mtu.get_total_buckets([])
    0
    
    >>> mtu.get_total_buckets([(2, 0, 100)])
    1
    
    >>> mtu.get_total_buckets([(2, 0, 100), (2,0,200)])
    2
    
    >>> mtu.get_total_buckets([(2, 0, 100), (2,0,210)])
    3
    """
    return

def test_get_bucket_num():
    """
    int -> int
    
    Determine which bucket this packet goes into based on its size
    
    >>> mtu.get_bucket_num(0)
    0
    
    >>> mtu.get_bucket_num(80)
    0
    
    >>> mtu.get_bucket_num(100)
    0
    
    >>> mtu.get_bucket_num(150)
    1
    
    >>> mtu.get_bucket_num(200)
    1
    
    >>> mtu.get_bucket_num(201)
    2
    """
    return

def test_convert_to_percentage():
    """
    listof (int,int,int) -> listof (int,float,int)
    
    Converts the given list of (packets_sent, packets_lost, packet_size) tuples
    into (packets_sent, packets_lost_percentage, packet_size)
    
    >>> mtu.convert_to_percentage([])
    []
    
    >>> mtu.convert_to_percentage([(2, 1, 100)])
    [(2, 0.5, 100)]
    
    >>> mtu.convert_to_percentage([(5, 0, 100)])
    [(5, 0.0, 100)]

    >>> mtu.convert_to_percentage([(2, 1, 100), (4, 1, 100)])
    [(2, 0.5, 100), (4, 0.25, 100)]
    
    >>> mtu.convert_to_percentage([(2, 0, 100), (4, 1, 100), (5, 2, 100)])
    [(2, 0.0, 100), (4, 0.25, 100), (5, 0.4, 100)]
    """
    return

# Make sure doctests run when script is run
if __name__ == '__main__':
    import doctest
    print doctest.testmod(verbose=False)
