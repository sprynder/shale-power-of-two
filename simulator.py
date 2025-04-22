from node import Node
from packet import Packet
import random
import matplotlib.pyplot as plt
import numpy as np


class ShaleSimulator:
    def __init__(self, h, nodes_per_phase):
        self.h = h
        self.nodes_per_phase = nodes_per_phase
        self.num_nodes = nodes_per_phase ** h
        self.nodes = [Node(i, h, nodes_per_phase) for i in range(self.num_nodes)]
        self.event_queue = []
        
        # Initialize adjacency tables
        for node in self.nodes:
            counter = 0
            for phase in range(h):
                for link in range(nodes_per_phase - 1):
                    neighbor_coord = node.coord.copy()
                    neighbor_coord[phase] = (neighbor_coord[phase] + link + 1) % nodes_per_phase
                    neighbor_id = node.coord_to_id(neighbor_coord)
                    node.add_adjacent(phase, link, neighbor_id)
                    node.set_schedule(phase,link, counter)
                    counter+=1

    def schedule_forwarding(self, src, packet, phase, link, arrival_time):
        """Schedule packet arrival at next node"""
        self.event_queue.append( (arrival_time, src, packet, phase, link) )
       #print(self.event_queue)

    def spray_route(self, current, packet):
        """Spraying phase routing logic"""
        if packet.remaining_sprays is None:
            packet.remaining_sprays = self.h

        if packet.remaining_sprays > 0:
            phase = self.h - packet.remaining_sprays
            current_node = self.nodes[current]
            available_links = list(range(self.nodes_per_phase - 1))

            # Power of Two Choices: Pick 2 random links, choose less congested
            # if len(available_links) >= 2:
            #     link1, link2 = random.sample(available_links, 2)
            #     q1 = current_node.queue_lengths.get((phase, link1), 0)
            #     q2 = current_node.queue_lengths.get((phase, link2), 0)
            #     chosen_link = link1 if q1 <= q2 else link2
            # else:
            chosen_link = random.choice(available_links)

            packet.remaining_sprays -= 1
            return phase, chosen_link
            
        # Start direct phase
        current_node = self.nodes[current]
        dest_coord = self.nodes[packet.dst].coord
        
        for phase in range(self.h):
            curr_coord = current_node.coord[phase]
            dest_phase_coord = dest_coord[phase]
            
            if curr_coord != dest_phase_coord:
                offset = (dest_phase_coord - curr_coord) % self.nodes_per_phase
                link = offset - 1
                return phase, link
        
        return None, None  # Reached destination

    def simulate(self, flows, max_timeslots=100):
        """Run simulation with queueing and link contention"""
        # Initialize event queue with source transmissions
        all_packets = []
        counter = 0
        for src, dst, arrival_time in flows:
            packet = Packet(src, dst, arrival_time, counter)
            all_packets.append(packet)
            self.schedule_forwarding(src, packet, -1, -1, arrival_time)
            counter+=1
        # Process events in temporal order
        self.event_queue.sort(key=lambda event: event[0])


        #start simulation loop
        cur_time = 0
        
        while self.event_queue and cur_time < max_timeslots:
            while self.event_queue and self.event_queue[0][0] == cur_time:
                cur_time, dst, packet, arrival_phase, arrival_link = self.event_queue.pop(0)
                
                if dst == packet.dst:
                    print(f"Packet {packet.id}, {packet.src}->{packet.dst} arrived at {cur_time}")
                    continue
                    
                # Determine next hop
                phase, link = self.spray_route(dst, packet)
                if phase is None:
                    continue  # Packet reached destination
                    

                # Assume global knowledge
                # Add to queue in current node
                self.nodes[dst].receive_packet(packet, phase, link, cur_time)
            
            # Process all nodes for this timeslot
            for node in self.nodes:
                node.process_timeslot(cur_time, self)
            self.event_queue.sort(key=lambda event: event[0])

            cur_time += 1
        max_lengths = []
        max_sum_lengths = []
        for i, node in enumerate(self.nodes):
            print(i, node.max_queue_length, node.max_summed_queue_length)
            max_lengths.append(node.max_queue_length)
            max_sum_lengths.append(node.max_summed_queue_length)
        # for i, packet in enumerate(all_packets):
        #     print(i, packet.path)
        return max_lengths, max_sum_lengths
    
    def stats(self):
        for node in self.nodes:
            print(node.id,node.coord, node.adjacent)
        