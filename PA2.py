import sys
from queue import PriorityQueue
import random
import math

#Creating/initializing global vars
clock = -1
serverIdle = True
readyQueueCount = -1
eventQ = PriorityQueue()
arrivalRate = int(sys.argv[1])
serviceTime = float(sys.argv[2])
totalTurnaround = -1 #Tracks total turnaround time, for averaging later.
completedProcesses = -1
busyTime = -1 #Time the CPU is busy

#weightedProcsInQueue stores number of procsInQueue weighted by their time in queue
#needs to be updated on each departure and arrival.
weightedProcsInQueue = -1

#Essentially equivalent to the struct, but in python.
#Type = 1 if arrival
#Type = -1 if departure
#Arrival time will be used to calculate turnaround times. departure - arrival time = turnaround
class Event():
    def __init__(self, type: int, time: float, arrivalTime: float):
        self.type = type
        self.time = time
        self.arrivalTime = arrivalTime

#uniform_dist and exponential_dist to generate exponential and poisson variables
def uniform_dist(max_value):
    rand_int = random.randint(0,max_value)
    return (rand_int / max_value + 0.0000000001)   

def exponential_dist(t):
    uni_float = uniform_dist(10000000)
    return -t*math.log(uni_float)

#init to initialize the beginning state of the system
def init():
    global clock, serverIdle, readyQueueCount, totalTurnaround, eventQ
    global completedProcesses, weightedProcsInQueue, busyTime
    clock = 0
    serverIdle = True
    readyQueueCount = 0
    t = clock + exponential_dist(1/arrivalRate) #Generating first event time t
    eventQ.queue.clear()
    totalTurnaround = 0
    completedProcesses = 0
    weightedProcsInQueue = 0
    busyTime = 0
    sched_event(1, t)

#Adds single event to priority queue, based on time and time
#time dictates priority in queue.
def sched_event(type: int, time: float, arrivalTime: float = 0.0):
    global eventQ
    event = Event(type, time, arrivalTime)
    eventQ.put((time, event))

def arr_handler(e: Event, beginClock: float):
    global clock, serverIdle, readyQueueCount, totalTurnaround, eventQ
    global completedProcesses, weightedProcsInQueue, busyTime

    weightedProcsInQueue += readyQueueCount * (clock - beginClock)

    sched_event(1, clock + exponential_dist(1/arrivalRate))
    
    if serverIdle:
        serverIdle = False
        service_duration = exponential_dist(serviceTime)
        busyTime += service_duration
        sched_event(-1, clock + service_duration, e.time)
    else: 
        readyQueueCount += 1

def dep_handler(e: Event, beginClock: float):
    global clock, serverIdle, readyQueueCount, totalTurnaround, eventQ
    global completedProcesses, weightedProcsInQueue, busyTime

    weightedProcsInQueue += readyQueueCount * (clock - beginClock)
    completedProcesses += 1

    turnaround_time = clock - e.arrivalTime
    totalTurnaround += turnaround_time

    if readyQueueCount == 0:
        serverIdle = True
    else:
        readyQueueCount -= 1
        service_duration = exponential_dist(serviceTime)
        busyTime += service_duration
        # Schedule departure with the arrival time of the next process
        sched_event(-1, clock + service_duration, e.arrivalTime)

def print_metrics():
    print(f'For an arrival rate of {arrivalRate} processes per second', end = '')
    print(f' and a service time of {serviceTime}, here are the results: ')
    print(f'The number of completed processes was: {completedProcesses}')
    print(f'The average turnaround time was: {totalTurnaround/completedProcesses}')
    print(f'The total throughput was: {completedProcesses/clock}')
    print(f'The average CPU utilization was: {busyTime/clock}')
    print(f'The average processes in the Ready Queue was: {weightedProcsInQueue/clock}\n')

#run() handles the loops and logic of the simulation
def run():
    global clock, serverIdle, readyQueueCount, totalTurnaround, eventQ
    global completedProcesses, weightedProcsInQueue, busyTime
    init()
    while (completedProcesses != 10000):
        e = eventQ.get()[1]
        old_clock = clock
        clock = e.time #update clock to the time the event begins
        if e.type == 1:
            arr_handler(e, old_clock)
            continue
        elif e.type == -1:
            dep_handler(e, old_clock)
            continue

    print_metrics()

run()