import random
from collections import defaultdict, deque
from node import Node
from simulator import ShaleSimulator
import matplotlib.pyplot as plt
import numpy as np
import copy

def generate_flows(n,h,phase, seed=None):
    """
    Generate `n` flows in the form (src, dst, time) with:
    - src and dst being distinct integers between 0 and 15
    - time being monotonically increasing from 0 to n-1
    - randomness in src and dst controlled by the `seed`
    """
    if seed is not None:
        random.seed(seed)
    bound = (phase**h)-1
    flows = []
    for t in range(n):
        while True:
            src = random.randint(0, bound)
            dst = random.randint(0, bound)
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


# print(flows)
# spray_method = "random"
# direct_method = "choice"
# max_lengths, max_sum_lengths, throughput, latencies = sim.simulate(flows, max_timeslots=1000000, spray_method=spray_method, direct_method = direct_method)
# plt.hist(latencies)
# plt.title(f'{spray_method}, {direct_method}')
# plt.ylabel("Number of Packets")
# plt.xlabel("Latencies")
# plt.savefig(f'{spray_method}_{direct_method}_throughput_{flow_size}_{h}_{nodes}_{seed}_fixed.png')

seed = 150
flows = generate_flows(100000, h, nodes,seed)
flow_list = []
intervals = [1,2,3,4]
for i in intervals:
    flow_list.append(generate_flows(100000, i, 5, seed))

configs = [
    ("random", "random"),
    ("choice", "random"),
    ("random", "choice"),
    ("choice", "choice"),

]
all_arrs = []
all_arrs_lat = []
for spray, direct in configs:
    throughs = []
    latencies_arr = []
    counter = 0
    for i in intervals:
        print(spray,direct,i)
        sim = ShaleSimulator(i, 5)
        max_lengths, max_sum_lengths, throughput, latencies = sim.simulate(flow_list[counter], max_timeslots=1000000, spray_method=spray, direct_method = direct)
        throughs.append(throughput)
        latencies_arr.append(np.median(latencies))
        counter+=1
    all_arrs.append(copy.deepcopy(throughs))
    all_arrs_lat.append(copy.deepcopy(latencies_arr))

config_labels = [f"{s}/{d}" for s, d in configs]

fig, axs = plt.subplots(2, 2, figsize=(12, 10))
axs = axs.flatten()
for i in range(len(config_labels)):
    axs[i].plot(intervals, all_arrs[i], marker='o')
    axs[i].set_title(config_labels[i])
    axs[i].set_xlabel("h")
    axs[i].set_ylabel("Throughput (median)")
    axs[i].grid(True)
plt.tight_layout()
plt.savefig("ThroughputVsh.png")

# ---------- Overlapping Plot ----------
# plt.figure(figsize=(10, 6))
# for throughs, label in zip(all_arrs, config_labels):
#     plt.plot(intervals, throughs, marker='o', label=label)

# plt.title("Throughput vs. Flow Size (All Configs Overlapped)")
# plt.xlabel("Flow Size")
# plt.ylabel("Throughput")
# plt.xscale("log")
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# plt.savefig("Throughput_Overlapped_N.png")

# # ---------- Subplots ----------
# fig, axs = plt.subplots(2, 2, figsize=(12, 8))
# axs = axs.flatten()

# for ax, throughs, label in zip(axs, all_arrs, config_labels):
#     ax.plot(intervals, throughs, marker='o')
#     ax.set_title(f"Config: {label}")
#     ax.set_xlabel("Flow Interval Size")
#     ax.set_ylabel("Throughput")
#     ax.set_xscale("log")
#     ax.grid(True)

# fig.suptitle("Throughput vs. Flow Interval Size (Per Configuration)", fontsize=14)
# plt.tight_layout(rect=[0, 0.03, 1, 0.95])
# plt.savefig("Throughput_Subplots_PerConfig_N.png")

# Sample output:
# Packet 0->15 arrived at 7
# Packet 0->15 arrived at 8
# Packet 0->15 arrived at 9

