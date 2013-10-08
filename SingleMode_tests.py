'''
Created on 31 Jul 2013

@author: Aleksandra
'''
import unittest

from SingleModeClasses import Problem, Solution, Activity

from GeneticAlgorithmSolver import GeneticAlgorithmSolver, crossover_sgs_nonrandom, SerialScheduleGenerationSchemeGenerator

class Test(unittest.TestCase):
    
    def setUp(self): #funkcja ktora framework testowy bedzie wykonywala przed kazda funkcja testowa
        self.activity1=Activity("a1",3,{1:2})
        self.activity2=Activity("a2",4,{1:3})
        self.activity3=Activity("a3",2,{1:4})
        self.activity4=Activity("a4",2,{1:4})
        self.activity5=Activity("a5",1,{1:3})
        self.activity6=Activity("a6",4,{1:2})
        
        activity_graph = {Activity.DUMMY_START:[self.activity1,self.activity2],
                          self.activity1:[self.activity3], 
                          self.activity3:[self.activity5], 
                          self.activity2:[self.activity4],
                          self.activity4:[self.activity6],
                          self.activity5:[Activity.DUMMY_END],
                          self.activity6:[Activity.DUMMY_END]}
        
        resources = {1:4}
        
        self.problem = Problem(activity_graph, resources)
        
        self.start_times = Solution()
        self.start_times.set_start_time_for_activity(self.activity1, 6)
        self.start_times.set_start_time_for_activity(self.activity2, 0)
        self.start_times.set_start_time_for_activity(self.activity3, 10)
        self.start_times.set_start_time_for_activity(self.activity4, 4)
        self.start_times.set_start_time_for_activity(self.activity5, 12)
        self.start_times.set_start_time_for_activity(self.activity6, 6)
                       
        
        self.sgs = [self.activity2, self.activity4, self.activity1, self.activity6, self.activity3, self.activity5]
        self.sgs2 = [self.activity2, self.activity1, self.activity4, self.activity3, self.activity6, self.activity5]
    def test_solve(self):
        solver = GeneticAlgorithmSolver(self.problem)
        solution = solver.solve()
        makespan = self.problem.compute_makespan(solution)
        self.assertEqual(makespan, 13, "Makespan is not equal to 13, in fact it is %d, %s" % (makespan, str(solution)))
        
        
    def test_check_if_solution_is_feasible(self):
        is_feasible = self.problem.check_if_solution_feasible(self.start_times)  
        self.assertTrue(is_feasible, "solution is shown as unfeasible")

    def test_compute_makespan(self):
        makespan = self.problem.compute_makespan(self.start_times)
        self.assertEqual(makespan, 13, "Makespan is not equal to 13")
    
    def test_sgs_2_dict(self):
        solution = Solution.generate_solution_from_serial_schedule_generation_scheme(self.sgs, self.problem)
        self.assertEqual(solution, self.start_times, "Expected %s, got %s" % (self.start_times, solution) )  
        
    def test_sgs_2_dict_2(self):
        activity1=Activity("a1",3,{1:2})
        activity2=Activity("a2",4,{1:3})
        
        activity_graph = {Activity.DUMMY_START:[activity1],
                          activity1:[activity2], 
                          activity2:[Activity.DUMMY_END]}
        resources = {1:7}
        problem = Problem(activity_graph, resources)  
        solution_sgs = Solution.generate_solution_from_serial_schedule_generation_scheme([activity1, activity2], problem)
        self.assertEqual(problem.compute_makespan(solution_sgs), 7, "Makespan is not egual 7")
    
    def test_sgs_2_dict_3(self):             
        solution = Solution.generate_solution_from_serial_schedule_generation_scheme(self.sgs2, self.problem)
        #self.assertEqual(solution, self.start_times, "Expected %s, got %s" % (self.start_times, solution) )  
        
    def test_compute_latest_start(self):
        latest_start = self.problem.compute_latest_start(self.activity1)
        self.assertEqual(latest_start, 10, "Latest start of the first activity should be 10")
    
    def test_successors(self):
        succ_list = self.problem.successors(self.activity3)
        self.assertEqual(len(succ_list), 1, "activity3 should have only one successor")
        self.assertIs(succ_list[0], self.activity5, "activity5 should be successor of the activity3")
        
    def test_solution_equality(self):
        s = Solution()
        o = Solution()
        s.set_start_time_for_activity(self.activity1, 5)
        s.set_start_time_for_activity(self.activity2, 3)
        
        o.set_start_time_for_activity(self.activity2, 3)
        o.set_start_time_for_activity(self.activity1, 5)
        self.assertEqual(s, o, "These solutions should be equal %s, %s" % (str(s), str(o)))
    
    def test_push_ready_activities_to_ready_to_schedule(self):
        activity_graph = {Activity.DUMMY_START: [self.activity1],
                          self.activity1: [self.activity2, self.activity3],
                          self.activity2: [self.activity4],
                          self.activity3: [self.activity4],
                          self.activity4: [Activity.DUMMY_END]}
        problem = Problem(activity_graph, {})
        ready_to_schedule = set()
        not_ready_to_schedule = set([self.activity2, self.activity3, self.activity4])
        current_activity = self.activity1
        generator = SerialScheduleGenerationSchemeGenerator(problem)
        generator._push_ready_activities_to_ready_to_schedule(current_activity, not_ready_to_schedule, ready_to_schedule)
        self.assertEqual(ready_to_schedule, set([self.activity2, self.activity3]), "Ready to schedule should be update correctly")
        self.assertEqual(not_ready_to_schedule, set([self.activity4]), "Not ready to schedule should be update correctly")
        
    def test_generate_random_sgs_from_problem(self):
        generator = SerialScheduleGenerationSchemeGenerator(self.problem)
        sgs_to_return = generator.generate_random_sgs()
        self.assertEqual(set(sgs_to_return), self.problem.non_dummy_activities(), "Sgs should have all activities")
        n = len(sgs_to_return)     
        self.assertTrue(self.problem.is_valid_sgs(sgs_to_return), "Sgs should be valid")
                             
    def test_crossover_sgs_nonrandom(self):
        sgs_mum = [1,3,2,5,4,6]
        sgs_dad = [2,4,6,1,3,5]
        q = 3
        sgs_daughter, sgs_son = crossover_sgs_nonrandom(sgs_mum, sgs_dad, q)
        self.assertEqual(sgs_daughter, [1,3,2,4,6,5],"Daughter is not correctly generated %s" % str(sgs_daughter))
        self.assertEqual(sgs_son, [2,4,6,1,3,5],"Son is not correctly generated %s" % str(sgs_son))
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_solve']
    unittest.main()