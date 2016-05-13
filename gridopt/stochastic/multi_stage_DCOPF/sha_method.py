#*****************************************************#
# This file is part of GRIDOPT.                       #
#                                                     #
# Copyright (c) 2015-2016, Tomas Tinoco De Rubira.    #
#                                                     #
# GRIDOPT is released under the BSD 2-clause license. #
#*****************************************************#

from problem import MS_DCOPF
from method import MS_DCOPF_Method
from optalg.stoch_solver.stoch_hyb_ms import MultiStage_StochasticHybrid

class MS_DCOPF_sha(MS_DCOPF_Method):
    """
    Stochatic Hybrid Approximation method for multi-stage DC OPF problem.
    """
    
    parameters = {'quiet': False}
    
    def __init__(self):

        MS_DCOPF_Method.__init__(self)
        self.parameters = MC_DCOPF_sha.parameters.copy()

    def create_problem(self,net,forecast):
        
        return None
        
    def solve(self,net,forecast):
        
        pass
