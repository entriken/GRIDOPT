#*****************************************************#
# This file is part of GRIDOPT.                       #
#                                                     #
# Copyright (c) 2015-2016, Tomas Tinoco De Rubira.    #
#                                                     #
# GRIDOPT is released under the BSD 2-clause license. #
#*****************************************************#

import numpy as np

class TS_DCOPF_Method:

    def __init__(self):
        """
        Two-stage DC OPF method class.
        """
        
        #: Results dictionary
        self.results = {}

        #: Parameters dictionary
        self.parameters = {}

    def create_problem(self,net):
        """
        Creates optimization problem.

        Parameters
        ----------
        net : PFNET Network

        Returns
        -------
        prob : OPTALG StochObj_Problem
        """
        
        return None

    def get_results(self):
        """
        Gets dictionary with results.

        Returns
        -------
        results : dict
        """

        return self.results

    def set_results(self,results):
        """
        Sets method results.

        Parameters
        ----------
        results : dict
        """

        self.results = results
                
    def solve(self,net):
        """
        Solves power flow problem.
        
        Parameters
        ----------
        net : PFNET Network
        """        
        
        pass
