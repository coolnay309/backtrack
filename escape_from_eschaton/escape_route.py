import json
import copy

class Frigate(object):
    def __init__(self):
        self.position = 0
        self.course = []
        self.velocity = 0

    def __repr__(self):
        return "Frigate details are, position: {0}, course: {1} and velocity: {2}".format(self.position, self.course,
                                                                                          self.velocity)

    def update_position(self):
        self.velocity = sum(self.course)
        self.position += self.velocity

    def plan_next_course(self, next_scenario):
        next_asteroid_positions, next_blast_position = next_scenario
        increase = filter(lambda x:x[1] == 0 and x[0] == self.position + self.velocity + 1, next_asteroid_positions)
        same = filter(lambda x:x[1] == 0 and x[0] == self.position + self.velocity, next_asteroid_positions)
        decrease = filter(lambda x:x[1] == 0 and x[0] == self.position + self.velocity - 1, next_asteroid_positions)
        print(increase, same, decrease)
        if not increase:
            self.course.append(1)
        elif not same:
            self.course.append(0)
        else:
            if self.position + self.velocity == -1:
                raise ValueError("Cannot escape eschaton, Dead by hitting eschaton")
            elif self.position + self.velocity == next_blast_position:
                raise ValueError("Cannot escape eschaton, Dead by blast consumption")
            elif not decrease:
                self.course.append(-1)
            else:
                raise ValueError("Cannot escape eschaton, Dead because nowhere to go")

    def simulate(self):
        course = [1, 1, 0, 0, 1, 1, 1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 1, 1, 1, 1, 1, 1,
         -1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 1, 1, 1,
         1, 1, 1, 1, 1, 1, 1, 1, -1, -1, -1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
         -1, -1, -1,-1]

        print(type(course))

        velocity = sum(course)
        total = 0
        location = 0
        for c in course:
            total += c
            location = location + total

        print(location, velocity)



class Asteroid(object):
    def __init__(self, offset, t_per_asteroid_cycle, field_number):
        self.offset = offset
        self.t_per_asteroid_cycle = t_per_asteroid_cycle
        self.field_number = field_number
        self.position = self.offset

    def __repr__(self):
        return "Asteroid number {0}, Offset is: {1} and cycle is: {2} current position is: {3}".format(
            self.field_number, self.offset, self.t_per_asteroid_cycle, self.position)

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
        return "Eschaton specs are, time per blast: {0}, blast position: {1}, time for next blast: {2}".format(
            self.t_per_blast_move, self.blast_position, self.t_next_blast)

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
        self.backtrack = {}

    def update_all_positions(self):
        self.frigate.update_position()
        self.eschaton.update_position()
        self.asteroids.update_positions()

    def get_next_positions(self):
        return [self.asteroids.next_positions(), self.eschaton.next_position()]

    def frigate_destroyed(self):
        possible_hitting_eschaton = self.frigate.position == -1
        possible_hitting_asteroid = filter(lambda x: x.field_number == self.frigate.position and x.position == 0,
                                           self.asteroids.asteroid_ring_members)
        possible_blast_consumption = self.frigate.position == self.eschaton.blast_position and \
                                     self.eschaton.t_next_blast == 0
        if possible_hitting_eschaton or possible_hitting_asteroid or possible_blast_consumption:
            return True
        else:
            return False

    def has_escaped(self):
        if self.frigate.position > self.asteroids.ring_size():
            return True
        else:
            return False

    def find_escape_route(self):
        route = self.calculate_course(0)
        return route

    def calculate_course(self, current_time):
        #print(self.eschaton.t_per_blast_move * self.asteroids.ring_size())
        #for current_time in xrange(0, self.eschaton.t_per_blast_move * self.asteroids.ring_size()):
        print("--------------------------------------------------------------------------------------------------------")
        print("t = " + str(current_time))
        print(self.frigate.course)
        print("current backtrack is: ", self.backtrack)
        #print("Parameters are: ", eschaton, frigate, asteroids.asteroid_ring_members)
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
            return [-2]

        else:
            print("calculating next course")
            #At time t get future astroid and blast positions for t+1
            next_scenario = self.get_next_positions()
            #else plan next course action
            #self.frigate.plan_next_course(next_scenario)
            next_asteroid_positions, next_blast_position = next_scenario
            increase = filter(lambda x:x[1] == 0 and x[0] == self.frigate.position + self.frigate.velocity + 1, next_asteroid_positions)
            same = filter(lambda x:x[1] == 0 and x[0] == self.frigate.position + self.frigate.velocity, next_asteroid_positions)
            decrease = filter(lambda x:x[1] == 0 and x[0] == self.frigate.position + self.frigate.velocity - 1, next_asteroid_positions)

            f_ring = current_time+1 in self.backtrack.get(self.frigate.position + self.frigate.velocity+1, set())
            s_ring = current_time+1 in self.backtrack.get(self.frigate.position + self.frigate.velocity, set())
            t_ring = current_time+1 in self.backtrack.get(self.frigate.position + self.frigate.velocity-1, set())
            print(increase, same, decrease)
            if not increase and not f_ring:
                self.frigate.course.append(1)
                print("Accelerating: ", self.frigate.position, self.frigate.velocity)
                ret = self.calculate_course(current_time+1)
                print("Returned from accelerated next call, current time is: ", current_time)
                if len(ret) > 1:
                    return ret
                elif len(ret) == 1 and ret[0] == -2:
                    try:
                        self.backtrack[self.frigate.position+self.frigate.velocity+1].add(current_time + 1)
                    except KeyError as e:
                        self.backtrack[self.frigate.position+self.frigate.velocity+1] = set()
                        self.backtrack[self.frigate.position+self.frigate.velocity+1].add(current_time + 1)
            if not same and not s_ring:
                #restore
                print("restoring")
                #print("Restore Parameters are: ", eschaton, frigate, asteroids.asteroid_ring_members)
                self.frigate.course = self.frigate.course[:current_time]
                total = 0
                location = 0
                for c in self.frigate.course:
                    total += c
                    location = location + total
                self.frigate.position = location
                self.frigate.velocity = sum(self.frigate.course)

                for id, asteroid in enumerate(self.asteroids.asteroid_ring_members):
                    asteroid.position = (asteroid.offset + current_time) % asteroid.t_per_asteroid_cycle

                self.eschaton.blast_position = current_time / self.eschaton.t_per_blast_move
                self.eschaton.t_next_blast = self.eschaton.t_per_blast_move - current_time% self.eschaton.t_per_blast_move

                #if current_time > 0:
                    #self.update_all_positions()
                    #print("All positions updated after restore")
                #print(self.frigate, self.eschaton, self.asteroids.asteroid_ring_members)

                self.frigate.course.append(0)
                print("Maintain speed: ", self.frigate.position, self.frigate.velocity)
                ret = self.calculate_course(current_time+1)
                if len(ret) > 1:
                    return ret
                elif len(ret) == 1 and ret[0] == -2:
                    try:

                        self.backtrack[self.frigate.position+self.frigate.velocity].add(current_time + 1)
                    except KeyError as e:
                        self.backtrack[self.frigate.position+self.frigate.velocity] = set()
                        self.backtrack[self.frigate.position+self.frigate.velocity].add(current_time + 1)

                print("Returned from same speed next call, current time is: ", current_time)
            if not decrease and not t_ring:
                #restore
                print("restoring")
                #print("Restore Parameters are: ", eschaton, frigate, asteroids.asteroid_ring_members)
                self.frigate.course = self.frigate.course[:current_time]
                total = 0
                location = 0
                for c in self.frigate.course:
                    total += c
                    location = location + total
                self.frigate.position = location
                self.frigate.velocity = sum(self.frigate.course)

                for id, asteroid in enumerate(self.asteroids.asteroid_ring_members):
                    asteroid.position = (asteroid.offset + current_time) % asteroid.t_per_asteroid_cycle

                self.eschaton.blast_position = current_time / self.eschaton.t_per_blast_move
                self.eschaton.t_next_blast = self.eschaton.t_per_blast_move - current_time% self.eschaton.t_per_blast_move

                #if current_time > 0:
                    #self.update_all_positions()
                    #print("All positions updated after restore")
                #print(self.frigate, self.eschaton, self.asteroids.asteroid_ring_members)

                self.frigate.course.append(-1)
                print("Decelerating: ", self.frigate.position, self.frigate.velocity)
                ret = self.calculate_course(current_time+1)
                if len(ret) > 1:
                    return ret
                elif len(ret) == 1 and ret[0] == -2:
                    try:
                        self.backtrack[self.frigate.position+self.frigate.velocity-1].add(current_time + 1)
                    except KeyError as e:
                        self.backtrack[self.frigate.position+self.frigate.velocity-1] = set()
                        self.backtrack[self.frigate.position+self.frigate.velocity-1].add(current_time + 1)
                print("Returned from decelerated next call, current time is: ", current_time)

            #raise ValueError("Cannot escape eschaton, Dead because nowhere to go")
            print("Nowhere to go, return and retry: ", self.frigate.position, self.frigate.velocity)
            #self.backtrack[self.frigate.position+self.frigate.velocity+1] = current_time
            #self.backtrack[self.frigate.position+self.frigate.velocity] = current_time
            #self.backtrack[self.frigate.position+self.frigate.velocity-1] = current_time
            return [-3]


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
                asteroids.append(Asteroid(asteroid_specs['offset'], asteroid_specs['t_per_asteroid_cycle'],
                                          field_number+1))
        else:
            raise KeyError
    frigate = Frigate()
    
    #navigate
    navigator = NavigateEscape(eschaton, frigate, asteroids)

    #calculate course
    course = navigator.find_escape_route()

    #Elvis has left the building
    return course

if __name__=="__main__":
    print(rejoin_family())
