import json

class Frigate(object):
    def __init__(self):
        self.position = 0
        self.course = []
        self.velocity = 0

    def __repr__(self):
        return "Frigate details are, position: {0}, course: {1} and velocity: {2}".format(self.position, self.course, self.velocity)

    def update_position(self):
        self.velocity = sum(self.course)
        self.position += self.velocity * 1

    def plan_next_course(self, next_scenario):
        next_asteroid_positions, next_blast_position = next_scenario
        if not filter(lambda x:x[1] == 0 and x[0] == self.position + self.velocity + 1, next_asteroid_positions):
            self.course.append(1)
        elif not filter(lambda x:x[1] == 0 and x[0] == self.position + self.velocity, next_asteroid_positions):
            self.course.append(0)
        else:
            #self.course.append(-1)
            if self.position + self.velocity == -1:
                print(self.course)
                raise ValueError("Cannot escape eschaton, Dead")
            elif self.position + self.velocity == next_blast_position:
                print(self.course)
                raise ValueError("Cannot escape eschaton, Dead")
            elif len(filter(lambda x:x[1] == 0 and x[0] == self.position + self.velocity - 1, next_asteroid_positions)) == 0:
                self.course.append(-1)
            else:
                print(self.course)
                raise ValueError("Cannot escape eschaton, Dead")


class Asteroid(object):
    def __init__(self, offset, t_per_asteroid_cycle, field_number):
        self.offset = offset
        self.t_per_asteroid_cycle = t_per_asteroid_cycle
        self.field_number = field_number
        self.position = (self.t_per_asteroid_cycle - self.offset) % self.t_per_asteroid_cycle

    def __repr__(self):
        return "Asteroid number {0}, Offset is: {1} and cycle is: {2} current position is: {3}".format(self.field_number, self.offset, self.t_per_asteroid_cycle, self.position)

    def update_position(self):
        self.position = (self.position + 1)% self.t_per_asteroid_cycle
    
    def next_position(self):
        return [self.field_number, (self.position+1)% self.t_per_asteroid_cycle]

class AsteroidRing(object):
    def __init__(self):
        self.asteroid_ring_members = []

    def append(self, asteroid):
        self.asteroid_ring_members.append(asteroid)

    def ring_size(self):
        return len(self.asteroid_ring_members)

    def update_positions(self):
        for asteroid in self.asteroid_ring_members:
            asteroid.update_position()

    def next_positions(self):
        new_asteroid_positions = []
        for asteroid in self.asteroid_ring_members:
            new_asteroid_positions.append(asteroid.next_position())
        return new_asteroid_positions

class Eschaton(object):
    def __init__(self, t_per_blast_move):
        self.t_per_blast_move = t_per_blast_move
        self.blast_position = 0
        self.t_next_blast = self.t_per_blast_move

    def __repr__(self):
        return "Eschaton specs are, time per blast: {0}, blast position: {1}, time for next blast: {2}".format(self.t_per_blast_move, self.blast_position, self.t_next_blast)

    def update_position(self):
        if self.t_next_blast == 0:
            self.blast_position += 1
            self.t_next_blast = self.t_per_blast_move
        else:
            self.t_next_blast -= 1

    def next_position(self):
        if self.t_next_blast -1 == 0:
            return self.blast_position + 1
        else:
            return self.blast_position

class NavigateEscape(object):
    def __init__(self, eschaton, frigate, asteroids):
        self.frigate = frigate
        self.eschaton = eschaton
        self.asteroids = asteroids

    def update_all_positions(self):
        self.frigate.update_position()
        self.eschaton.update_position()
        self.asteroids.update_positions()

    def get_next_positions(self):
        return [self.asteroids.next_positions(), self.eschaton.next_position()]

    def frigate_destroyed(self):
        possible_hitting_eschaton = self.frigate.position == -1
        possible_hitting_asteroid = filter(lambda x: x.field_number == self.frigate.position and x.position == 0, self.asteroids.asteroid_ring_members)
        possible_blast_consumption = self.frigate.position == self.eschaton.blast_position and self.eschaton.t_next_blast == 0
        if possible_hitting_eschaton or possible_hitting_asteroid or possible_blast_consumption:
            return True
        else:
            return False

    def has_escaped(self):
        if self.frigate.position > self.asteroids.ring_size():
            return True
        else:
            return False

    def calculate_course(self):
        print(self.eschaton.t_per_blast_move * self.asteroids.ring_size())
        for current_time in xrange(0, self.eschaton.t_per_blast_move * self.asteroids.ring_size()):   
            print("t = " + str(current_time)) 
            #At time t update current astroid positions and blast position
            if current_time > 0:
                self.update_all_positions()
                print("All positions updated")
            #print(self.frigate, self.eschaton, self.asteroids.asteroid_ring_members)
            #if escaped return course
            if self.has_escaped():
                print("frigate escaped")
                return self.frigate.course
                
            #elseif dead report dead
            elif self.frigate_destroyed():
                print("frigate destroyed")
                return []

            else:
                print("calculating next course")
                #At time t get future astroid and blast positions for t+1
                next_scenario = self.get_next_positions()
                #else plan next course action
                self.frigate.plan_next_course(next_scenario)

def read_chart():
    chart_file = open('full-chart.json', 'r')
    chart_data = json.loads(chart_file.read())
    chart_file.close()
    return chart_data

def rejoin_family():
    #read chart
    chart_data = read_chart()

    #create scenario
    asteroids = AsteroidRing()
    for chart_key, chart_value in chart_data.iteritems():
        if chart_key == 't_per_blast_move':
            eschaton = Eschaton(chart_value)
        elif chart_key == 'asteroids':
            for field_number, asteroid_specs in enumerate(chart_value):
                asteroids.append(Asteroid(asteroid_specs['offset'], asteroid_specs['t_per_asteroid_cycle'], field_number+1))
        else:
            raise KeyError
    frigate = Frigate()
    
    #navigate
    navigator = NavigateEscape(eschaton, frigate, asteroids)

    #calculate course
    course = navigator.calculate_course()

    #Elvis has left the building
    return course

if __name__=="__main__":
    print(rejoin_family())
