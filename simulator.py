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

    def spray_route(self, current, packet, spray_method = "random", direct_method = "random"):
        """Spraying phase routing logic"""
        if packet.remaining_sprays is None:
            packet.remaining_sprays = self.h

        # if packet.remaining_sprays == self.h:


        if packet.remaining_sprays > 0:
            phase = self.h - packet.remaining_sprays
            current_node = self.nodes[current]
            available_links = list(range(self.nodes_per_phase - 1))

            chosen_link = available_links[0]
            #Power of Two Choices: Pick 2 random links, choose less congested
            #Assume complete knoweldge (compensated for with tokens later)
            if spray_method == "choice":
                link1, link2 = random.sample(available_links, 2)
                # q1 = self.nodes[current_node.adjacent[(phase, link1)]].cur_queue_length
                # q2 = self.nodes[current_node.adjacent[(phase, link2)]].cur_queue_length
                q1 = current_node.queue_lengths[(phase, link1)]
                q2 = current_node.queue_lengths[(phase,link2)]
                chosen_link = link1 if q1 <= q2 else link2
            elif spray_method == "random":
                chosen_link = random.choice(available_links)
            elif spray_method == "optimal":
                minq = self.nodes[current_node.adjacent[(phase, 0)]].cur_queue_length
                mini = 0
                for i in available_links:
                    q_len = self.nodes[current_node.adjacent[(phase, i)]].cur_queue_length
                    if q_len<minq:
                        minq=q_len
                        mini=i
                chosen_link=mini
            
            packet.remaining_sprays -= 1
            return phase, chosen_link
            
        # Start direct phase
        current_node = self.nodes[current]
        dest_coord = self.nodes[packet.dst].coord
        
        if direct_method == "random":
            for phase in range(self.h):
                curr_coord = current_node.coord[phase]
                dest_phase_coord = dest_coord[phase]
                
                if curr_coord != dest_phase_coord:
                    offset = (dest_phase_coord - curr_coord) % self.nodes_per_phase
                    link = offset - 1
                    return phase, link
                
        elif direct_method == "choice":
            if current_node.coord == dest_coord:
                return None, None # At destination
            else:

                for phase in range(self.h): #Find first misaligned phase
                    altPhase = (phase+self.h//2)%self.h
                    if current_node.coord[phase]==dest_coord[phase] and current_node.coord[altPhase]==dest_coord[altPhase]:
                        continue
                    else:
                        curr_coord = current_node.coord[phase]
                        dest_phase_coord = dest_coord[phase]
                        curr_coord2 = current_node.coord[altPhase]
                        dest_phase_coord2 = dest_coord[altPhase]
                        pairOne = None
                        pairTwo = None
                        offset = (dest_phase_coord - curr_coord) % self.nodes_per_phase
                        link = offset - 1
                        pairOne = (phase, link)
                        offset = (dest_phase_coord2 - curr_coord2) % self.nodes_per_phase
                        link = offset - 1
                        pairTwo = (altPhase, link)
                        if current_node.coord[phase]!=dest_coord[phase] and current_node.coord[altPhase]!=dest_coord[altPhase]:
                            
                            q1 = current_node.queue_lengths[current_node.adjacent[pairOne]]
                            q2 = current_node.queue_lengths[current_node.adjacent[pairTwo]]
                            chosen_path = pairOne if q1 <= q2 else pairTwo
                            return chosen_path
                        elif current_node.coord[phase]==dest_coord[phase]:
                            return pairTwo
                        elif current_node.coord[altPhase]==dest_coord[altPhase]:
                            return pairOne
            return None, None  # Reached destination

    def simulate(self, flows, max_timeslots=100, spray_method = "random", direct_method = "random"):
        """Run simulation with queueing and link contention"""
        # Initialize event queue with source transmissions
        all_packets = []
        delivered_packets = []
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
        
        while cur_time < max_timeslots:
            #Receiving
            while self.event_queue and self.event_queue[0][0] == cur_time:
                cur_time, dst, packet, arrival_phase, arrival_link = self.event_queue.pop(0)
                
                if dst == packet.dst:
                    #print(f"Packet {packet.id}, {packet.src}->{packet.dst} arrived at {cur_time}")
                    packet.delivered = True
                    delivered_packets.append(packet)
                    packet.delivered_time = cur_time
                    continue
                    
                # Determine next hop
                phase_to_take, link_to_take = self.spray_route(dst, packet, spray_method, direct_method)
                if phase_to_take is None:
                    continue  # Packet reached destination
                    
                # Add to queue in current node
                self.nodes[dst].receive_packet(packet, phase_to_take, link_to_take, cur_time)
            
            
            # Sending
            # Process all nodes for this timeslot
            for node in self.nodes:
                node.process_timeslot(cur_time, self, method=direct_method)

            # Simulate congestion control tokens backflow:
            for node in self.nodes:
                cur_phase, cur_link = node.schedule[cur_time%len(node.schedule.items())]
                dst_node = self.nodes[node.adjacent[(cur_phase, cur_link)]]
                node.receive_token(cur_phase, cur_link, dst_node.cur_queue_length)
                altPhase = (cur_phase+self.h//2)%self.h
                dst_node = self.nodes[node.adjacent[(altPhase, cur_link)]]
                node.receive_token(altPhase, cur_link, dst_node.cur_queue_length)

            self.event_queue.sort(key=lambda event: event[0])
    
            cur_time += 1
            if len(all_packets)==len(delivered_packets): # All delivered
                break
        max_lengths = []
        max_sum_lengths = []
        for i, node in enumerate(self.nodes):
            #print(i, node.max_queue_length, node.max_summed_queue_length)
            max_lengths.append(node.max_queue_length)
            max_sum_lengths.append(node.max_summed_queue_length)
        latencies = []
        for p in all_packets:
            latencies.append(p.delivered_time - p.creation_time)
        # for i, packet in enumerate(all_packets):
        #     print(i, packet.delivered, packet.path)
        throughput = len(delivered_packets)/cur_time
        return max_lengths, max_sum_lengths, throughput, latencies
    
    def stats(self):
        for node in self.nodes:
            print(node.id,node.coord, node.adjacent)
        