import random
from collections import defaultdict, deque
from node import Node
from simulator import ShaleSimulator
import matplotlib.pyplot as plt
import numpy as np
import concurrent.futures


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

def run_simulation(spray_method, direct_method, flows):
    print("starting sim")
    sim = ShaleSimulator(h=3, nodes_per_phase=5)  # 2D grid with 4 nodes per dimension
    max_lengths, max_sum_lengths, throughput, latencies = sim.simulate(
        flows,
        max_timeslots=100000,
        spray_method=spray_method,
        direct_method=direct_method
    )
    print("sim end")
    return max_sum_lengths #max_sum_lengths

configs = [
    ("random", "random"),
    ("choice", "random"),
    ("random", "choice"),
    ("choice", "choice"),

]

flow_size = 100000
seed = 150
flows = generate_flows(flow_size, seed)

results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(run_simulation, spray, direct, flows) for spray, direct in configs]
    for future in concurrent.futures.as_completed(futures):
        results.append(future.result())

# Optional: Sort results to maintain order if needed
# (because as_completed doesn't guarantee order)
results_sorted = [future.result() for future in futures]  # keeps order as in configs

labels = ['random/random', 'choice/random', 'random/choice','choice/choice']
colors = ['blue', 'orange', 'red', 'green']

fig, axs = plt.subplots(2, 2, figsize=(12, 8))  # 2x2 grid of subplots
axs = axs.flatten()  # Flatten the 2D array of axes for easy iteration

for ax, data, label, color in zip(axs, results_sorted, labels, colors):
    ax.hist(data, alpha=0.7, color=color)
    ax.set_title(f"{label}")
    ax.set_xlabel("Latencies (ticks)")
    ax.set_ylabel("Packets")

fig.suptitle("Histograms of Max Queue Lengths for Different Routing Strategies", fontsize=14)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout to accommodate the main title
plt.savefig('Queue_Lengths_Subplots_Fixed')
# plt.show()


# plt.figure(figsize=(10, 6))
# for data, label, color in zip(results_sorted, labels, colors):
#     plt.plot(data,alpha=0.5, label=label, color=color)

# plt.title("Histogram of Packet Latencies for Different Routing Strategies")
# plt.xlabel("Latencies (ticks)")
# plt.ylabel("Packets")
# plt.legend()
# plt.savefig(f'Latency Overlapping Histograms Fixed')

# Example usage



# h = 3
# nodes = 5
# sim = ShaleSimulator(h=h, nodes_per_phase=nodes)  # 2D grid with 4 nodes per dimension
# # sim.stats()
# # (source, dest, start_time)

# #1000 - 42

# print(flows)
# spray_method = "choice"
# direct_method = "random"
# max_lengths, max_sum_lengths = sim.simulate(flows, max_timeslots=1000000, spray_method=spray_method, direct_method = direct_method)
# plt.hist(max_sum_lengths)
# plt.ylabel("Number of Nodes")
# plt.xlabel("Max Queue Size")
# plt.savefig(f'{spray_method}_{direct_method}_max_sum_length_{flow_size}_{h}_{nodes}_{seed}_test.png')


# Sample output:
# Packet 0->15 arrived at 7
# Packet 0->15 arrived at 8
# Packet 0->15 arrived at 9

