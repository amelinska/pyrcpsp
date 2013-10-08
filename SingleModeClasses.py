'''
Created on 31 Jul 2013

@author: Aleksandra
'''
from random import choice, randint
from deap import algorithms, tools, base, creator
from copy import copy
from collections import defaultdict 
from bisect import bisect_left
from BaseProblem import BaseProblem

from ResourceUsage import update_resource_usages_in_time, ResourceUsage

import ListUtilities

class Activity(object):
    def __init__(self, name, duration, demand):
        self.duration = duration
        self.demand = demand
        self.name = name
        
    def __repr__(self):
        return self.name
    
    def __eq__(self, other):
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)
        
Activity.DUMMY_START = Activity("start",0, 0)
Activity.DUMMY_END = Activity("end",0, 0)
Activity.DUMMY_NODES = [Activity.DUMMY_START, Activity.DUMMY_END]

def activity_in_conflict_in_precedence(problem, solution, activity, proposed_start_time):
    for predecessor_activity in problem.predecessors(activity):
        if solution.get_start_time(predecessor_activity) + predecessor_activity.duration > proposed_start_time:   #samo zadanie nie wie o swoich poprzedniahc, ale wie o nich problem
            return True
    else:
        return False


                          
class Solution(dict):   # fenotyp rozwiazania
    def __init__(self):
        self.makespan = 0
        self[Activity.DUMMY_START] = 0
        
    def set_start_time_for_activity(self, activity, start_time):
        self[activity] = start_time
        
    def get_start_time(self, activity):
        return self[activity]
        
    def __str__(self):
        return "Solution: " + super.__str__(self)
    
    def __eq__(self, other):
        if len(self) != len(other):
            return False
        
        for i,j in self.iteritems():
            if other[i] != j:
                return False
        return True
    @staticmethod
    def generate_solution_from_serial_schedule_generation_scheme(sgs, problem):
        solution = Solution()
        resource_usages_in_time = defaultdict(ResourceUsage)
        time_points = [0]
        
        for activity in sgs:
            last_time = time_points[-1]
            start_time = 0
            for time_unit in reversed(time_points):
                actual_resource_usage = copy(resource_usages_in_time[time_unit])
                actual_resource_usage.add_resource_usage(activity.demand)
                if (actual_resource_usage.is_resource_usage_greater_than_supply(problem.resources) or (activity_in_conflict_in_precedence(problem, solution, activity, time_unit))):
                    start_time = last_time
                    break
                else:
                    last_time = time_unit
            solution.set_start_time_for_activity(activity, start_time)
            ListUtilities.insert_value_to_ordered_list(time_points, start_time)
            ListUtilities.insert_value_to_ordered_list(time_points, start_time + activity.duration)         
            update_resource_usages_in_time(resource_usages_in_time, activity, start_time)
        return solution         
        
class Problem(BaseProblem):
    def __init__(self, activity_graph, resources):
        self.ActivityClass = Activity
        self.activity_graph = activity_graph
        self.resources = resources
        self.activities_set = set() 
        for activity in activity_graph:
            self.activities_set.add(activity)
            for nested_act in activity_graph[activity]:
                self.activities_set.add(nested_act)
                
        self.predecessors_dict = defaultdict(list)
        for activity, activity_successors in self.activity_graph.iteritems():
            for successor in activity_successors:
                self.predecessors_dict[successor].append(activity)
        
        self.latest_starts = {}
        self.latest_finishes = {}
    
    def compute_latest_start(self, activity):
        """Computes latest possible start for activity with dependencies with other 
        activities defined in problem
        
        :param activity: activity which latest start will be computed
        :type activity: class_solver.Activity
        :param problem: problem definition which contains activity
        :type problem: class_solver.Problem
        :returns: point in time of latest start of activity
        """
        if activity in self.latest_starts:
            return self.latest_starts[activity]
        
        if activity is Activity.DUMMY_END:
            s = sum([x.duration for x in self.activities()])
            self.latest_starts[activity] = s
            self.latest_finishes[activity] = s
            return s
        else:
            current_min = sum([x.duration for x in self.activities()])
            for succ in self.successors(activity):
                self.compute_latest_start(succ)
                succ_latest_start = self.latest_starts[succ]
                if succ_latest_start < current_min:
                    current_min = succ_latest_start
            self.latest_finishes[activity] = current_min
            self.latest_starts[activity] = current_min - activity.duration
            return self.latest_starts[activity]
    
    def compute_makespan(self, activities_start_times):
        makespan = 0                                                                                                                                                                                                                                             
        for activity, start_time in activities_start_times.iteritems():
            when_activity_ends = activity.duration + start_time
            if when_activity_ends >= makespan:
                makespan = when_activity_ends
        return makespan
    
    def check_if_solution_feasible(self, solution):
        makespan = self.compute_makespan(solution)
        for i in xrange(makespan):
            resource_usage = ResourceUsage()
            for activity, start_time in solution.iteritems():
                if start_time <= i < start_time + activity.duration:
                    resource_usage.add_resource_usage(activity.demand)
            
            if resource_usage.is_resource_usage_greater_than_supply( self.resources):
                return False
        return True
    
    def find_all_elements_without_predecessors(self):
        return self.successors(Activity.DUMMY_START)
    
    def is_valid_sgs(self, sgs):
        for i in range(len(sgs)):
           for j in range(i,len(sgs)):
               activity1 = sgs[i] 
               activity2 = sgs[j]
               if activity2 in self.predecessors(activity1):
                   return False
        return True
           
        
        
        
        
        
        