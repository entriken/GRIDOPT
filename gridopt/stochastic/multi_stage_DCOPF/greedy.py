#*****************************************************#
# This file is part of GRIDOPT.                       #
#                                                     #
# Copyright (c) 2015-2017, Tomas Tinoco De Rubira.    #
#                                                     #
# GRIDOPT is released under the BSD 2-clause license. #
#*****************************************************#

import time
import numpy as np
from types import MethodType
from .method import MS_DCOPF_Method
from .problem import MS_DCOPF_Problem
from optalg.stoch_solver import StochProblemMS_Policy

class MS_DCOPF_GR(MS_DCOPF_Method):
    """
    Greedy method for multi-stage DC OPF problem.
    """
    
    parameters = {'quiet': False}
    
    def __init__(self):
        """
        Greedy method for multi-stage DC OPF problem.
        """
  
        MS_DCOPF_Method.__init__(self)
        parameters = MS_DCOPF_Problem.parameters.copy()
        parameters.update(MS_DCOPF_GR.parameters)
        self.parameters = parameters

    def create_problem(self,net,forecast,parameters):
        
        return MS_DCOPF_Problem(net,forecast,parameters)
        
    def solve(self,net,forecast):
        
        # Local variables
        params = self.parameters

        # Parameters
        quiet = params['quiet']
        
        # Problem
        self.problem = self.create_problem(net,forecast,params)
        if not quiet:
            self.problem.show()
 
        # Construct policy
        def apply(cls,t,x_prev,W):
           
            T = cls.problem.get_num_stages()
 
            assert(0 <= t < T)
            assert(len(W) == t+1)
            
            x,H,gH,gHnext = cls.problem.solve_stages(t,
                                                     [W[-1]],
                                                     x_prev,
                                                     quiet=True,
                                                     tf=t)
            
            # Check feasibility
            if not cls.problem.is_point_feasible(t,x,x_prev,W[-1]):
                raise ValueError('infeasible point')
            
            # Return
            return x
            
        policy = StochProblemMS_Policy(self.problem,
                                       data=None,
                                       name='Greedy')
        policy.apply = MethodType(apply,policy)
        
        # Return
        return policy
