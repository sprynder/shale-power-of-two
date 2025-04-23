import random
from collections import defaultdict, deque

class Node:
    def __init__(self, node_id, h, nodes_per_phase):
        self.id = node_id
        self.h = h
        self.nodes_per_phase = nodes_per_phase
        self.coord = self.id_to_coord(node_id)
        self.max_queue_length = 0
        self.max_summed_queue_length = 0
        self.cur_queue_length = 0
        # Queue state: { (phase, link): deque() }
        self.queues = defaultdict(deque)
        self.adjacent = {}  # { (phase, link): node_id }
        self.adjecent2 = {}
        self.schedule = {}
        self.schedule2 = {}
        self.queue_lengths = defaultdict(int)
        # Link busy state: { (phase, link): busy_until_timeslot }
        self.link_busy = defaultdict(int)

    def id_to_coord(self, node_id):
        coord = []
        for i in range(self.h):
            coord.append(node_id % self.nodes_per_phase)
            node_id //= self.nodes_per_phase
        return coord

    def coord_to_id(self, coord):
        node_id = 0
        for i in reversed(range(self.h)):
            node_id = node_id * self.nodes_per_phase + coord[i]
        return node_id

    def add_adjacent(self, phase, link, node_id):
        self.adjacent[(phase, link)] = node_id
        # Initilizae queue lengths:
        self.queue_lengths[(phase, link)] = 0
    
    def set_schedule(self, phase, link, id):
        self.schedule[id] = (phase,link)
    
    def construct_second_choice(self):
        pass



    def receive_token(self, phase, link, congest_val):
        self.queue_lengths[(phase, link)] = congest_val

    def receive_packet(self, packet, phase, link, cur_time):
        """Add packet to queue for specified phase/link"""
        self.queues[(phase, link)].append(packet)
        if len(self.queues[(phase,link)]) >= self.max_queue_length:
            self.max_queue_length = len(self.queues[(phase,link)])
        temp_sum = 0
        for q in self.queues.values():
            temp_sum+= len(q)
        if temp_sum>= self.max_summed_queue_length:
            self.max_summed_queue_length = temp_sum
        self.cur_queue_length = temp_sum
        
        
    def process_timeslot(self, cur_time, simulator):
        """Attempt to send one packet per non-busy link"""

        cur_phase, cur_link = self.schedule[cur_time%len(self.schedule.items())] # Link that is currently open and connected / dest

        if (cur_phase, cur_link) in self.queues.keys():
            cur_q = self.queues[(cur_phase, cur_link)]
            if cur_q and len(cur_q) > 0:
                packet = cur_q.popleft()
                next_hop = self.adjacent[(cur_phase, cur_link)]
                transmission_time = 1  # 1 timeslot per hop
                
                # Record hop details
                packet.path.append(next_hop)
                packet.timeslots.append(cur_time + transmission_time)
                simulator.schedule_forwarding(
                    next_hop,
                    packet,
                    cur_phase,
                    cur_link,
                    cur_time + transmission_time
                )

        # for (phase, link), queue in self.queues.items():
        #     if self.link_busy[(phase, link)] > cur_time:
        #         continue  # Link is busy
            
        #     if queue:
        #         packet = queue.popleft()
        #         next_hop = self.adjacent[(phase, link)]
        #         transmission_time = 1  # 1 timeslot per hop
                
        #         # Record hop details
        #         packet.path.append(next_hop)
        #         packet.timeslots.append(cur_time + transmission_time)
                
        #         # Schedule arrival at next node
        #         simulator.schedule_forwarding(
        #             next_hop,
        #             packet,
        #             phase,
        #             link,
        #             cur_time + transmission_time
        #         )
                
        #         # Mark link busy
        #         self.link_busy[(phase, link)] = cur_time + transmission_time
