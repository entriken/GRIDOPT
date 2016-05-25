#*****************************************************#
# This file is part of GRIDOPT.                       #
#                                                     #
# Copyright (c) 2015-2016, Tomas Tinoco De Rubira.    #
#                                                     #
# GRIDOPT is released under the BSD 2-clause license. #
#*****************************************************#

import time
import numpy as np
from types import MethodType
from method import MS_DCOPF_Method
from problem import MS_DCOPF_Problem
from scipy.sparse import eye,coo_matrix,bmat
from optalg.stoch_solver import StochObjMS_Policy
from optalg.opt_solver import OptSolverIQP, QuadProblem

class MS_DCOPF_GR(MS_DCOPF_Method):
    """
    Greedy method for multi-stage DC OPF problem.
    """
    
    parameters = {'quiet': False}
    
    def __init__(self):
        
        MS_DCOPF_Method.__init__(self)
        self.parameters = MS_DCOPF_GR.parameters.copy()
        self.parameters.update(MS_DCOPF_Problem.parameters)

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
        def apply(cls,t,x_prev,Wt):
            
            assert(0 <= t < cls.problem.T)
            assert(len(Wt) == t+1)
            
            x_list,Q_list,gQ_list,results = cls.problem.eval_stage_approx(t,[Wt[-1]],x_prev,quiet=True,tf=t)
            assert(len(x_list) == 1)
            
            # Check feasibility
            if not cls.problem.is_point_feasible(t,x_list[0],x_prev,Wt[-1]):
                raise ValueError('infeasible point')
            
            # Return
            return x_list[0]
            
        policy = StochObjMS_Policy(self.problem,data=None,name='Greedy')
        policy.apply = MethodType(apply,policy)
        
        # Return
        return policy
