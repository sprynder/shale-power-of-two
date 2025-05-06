class Packet:
    def __init__(self, src, dst, creation_time, id):
        self.id = id
        self.src = src
        self.dst = dst
        self.creation_time = creation_time
        self.path = [src]
        self.timeslots = [creation_time]
        self.remaining_sprays = None  # Set during routing
        self.delivered = False
        self.delivered_time = -1


    def __str__(self):
        data = (self.src, self.dst, self.creation_time)
        return str(data)

    def __repr__(self):
        data = (self.src, self.dst, self.creation_time, self.id)
        return str(data)