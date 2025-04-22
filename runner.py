import random
from collections import defaultdict, deque
from node import Node
from simulator import ShaleSimulator
import matplotlib.pyplot as plt
import numpy as np


def generate_flows(n, seed=None):
    """
    Generate `n` flows in the form (src, dst, time) with:
    - src and dst being distinct integers between 0 and 15
    - time being monotonically increasing from 0 to n-1
    - randomness in src and dst controlled by the `seed`
    """
    if seed is not None:
        random.seed(seed)
    
    flows = []
    for t in range(n):
        while True:
            src = random.randint(0, 15)
            dst = random.randint(0, 15)
            if src != dst:
                break
        flows.append((src, dst, random.randint(0,20)))
    
    return flows


# Example usage
sim = ShaleSimulator(h=2, nodes_per_phase=4)  # 2D grid with 4 nodes per dimension
# sim.stats()
# (source, dest, start_time)


flows = generate_flows(10, 42)

max_lengths, max_sum_lengths = sim.simulate(flows, max_timeslots=1000000)
# plt.hist(max_sum_lengths)
# plt.savefig('max_sum_length_500000.png')


# Sample output:
# Packet 0->15 arrived at 7
# Packet 0->15 arrived at 8
# Packet 0->15 arrived at 9


