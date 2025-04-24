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
            src = random.randint(0, 124)
            dst = random.randint(0, 124)
            if src != dst:
                break
        flows.append((src, dst, random.randint(0,20)))
    
    return flows


# Example usage
h = 3
nodes = 5
sim = ShaleSimulator(h=h, nodes_per_phase=nodes)  # 2D grid with 4 nodes per dimension
# sim.stats()
# (source, dest, start_time)

#1000 - 42
flow_size = 100000
seed = 150
flows = generate_flows(flow_size, seed)
print(flows)
spray_method = "random"
direct_method = "choice"
max_lengths, max_sum_lengths = sim.simulate(flows, max_timeslots=100000, spray_method=spray_method, direct_method = direct_method)
plt.hist(max_sum_lengths)
plt.ylabel("Number of Nodes")
plt.xlabel("Max Queue Size")
plt.savefig(f'{spray_method}_{direct_method}_max_sum_length_{flow_size}_{h}_{nodes}_{seed}_test.png')


# Sample output:
# Packet 0->15 arrived at 7
# Packet 0->15 arrived at 8
# Packet 0->15 arrived at 9

