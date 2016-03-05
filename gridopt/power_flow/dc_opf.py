#*****************************************************#
# This file is part of GRIDOPT.                       #
#                                                     #
# Copyright (c) 2015-2016, Tomas Tinoco De Rubira.    #
#                                                     #
# GRIDOPT is released under the BSD 2-clause license. #
#*****************************************************#

import pfnet
import numpy as np
from method_error import *
from method import PFmethod
from scipy.sparse import triu,coo_matrix,bmat,eye
from optalg.opt_solver import OptSolverError,OptSolverIQP,QuadProblem

class DCOPF(PFmethod):
    """
    DC optimal power flow class.
    """
        
    parameters = {'quiet' : False}
                                    
    def __init__(self):

        PFmethod.__init__(self)
        self.parameters = DCOPF.parameters.copy()
        self.parameters.update(OptSolverIQP.parameters)

    def create_problem(self,net):
        
        # Parameters
        params = self.parameters
        
        # Clear flags
        net.clear_flags()
        
        # Set flags
        net.set_flags(pfnet.OBJ_BUS,
                      pfnet.FLAG_VARS,
                      pfnet.BUS_PROP_NOT_SLACK,
                      pfnet.BUS_VAR_VANG)
        net.set_flags(pfnet.OBJ_GEN,
                      pfnet.FLAG_VARS|pfnet.FLAG_BOUNDED,
                      pfnet.GEN_PROP_P_ADJUST,
                      pfnet.GEN_VAR_P)

        try:
            assert(net.num_bounded == net.get_num_P_adjust_gens())
            assert(net.num_vars == (net.num_buses-net.get_num_slack_buses()+
                                    net.get_num_P_adjust_gens()))
        except AssertionError:
            raise PFmethodError_BadProblem(self)
            
        # Set up problem
        problem = pfnet.Problem()
        problem.set_network(net)
        problem.add_constraint(pfnet.CONSTR_TYPE_DCPF)
        problem.add_constraint(pfnet.CONSTR_TYPE_DC_FLOW_LIM)
        problem.add_constraint(pfnet.CONSTR_TYPE_LBOUND)
        problem.add_function(pfnet.FUNC_TYPE_GEN_COST,1.)
        problem.analyze()
        
        # Return
        return problem
            
    def solve(self,net):
        
        # Parameters
        params = self.parameters

        # Problem
        problem = self.create_problem(net)
       
        # Construct QP
        x = problem.get_init_point()
        problem.eval(x)
        c_flows = problem.find_constraint(pfnet.CONSTR_TYPE_DC_FLOW_LIM)
        c_bounds = problem.find_constraint(pfnet.CONSTR_TYPE_LBOUND)
        
        Hx = problem.Hphi + problem.Hphi.T - triu(problem.Hphi)
        gx = problem.gphi - Hx*x
        
        Ax = problem.A
        bx = problem.b
        
        lz = c_flows.l
        uz = c_flows.u
        Gz = c_flows.G
        
        lx = c_bounds.l
        ux = c_bounds.u
        Gx = c_bounds.G

        nx = net.num_vars
        nz = Gz.shape[0]
        n = nx+nz

        Iz = eye(nz)
        Oz = coo_matrix((nz,nz))
        oz = np.zeros(nz)
        
        H = bmat([[Hx,None],[None,Oz]],format='coo')/net.base_power
        g = np.hstack((gx,oz))/net.base_power

        A = bmat([[Ax,None],[Gz,-Iz]],format='coo')
        b = np.hstack((bx,oz))

        l = np.hstack((lx,lz))
        u = np.hstack((ux,uz))

        y = np.hstack((x,oz))

        # Check flow limits
        if not np.all(lz < uz):
            raise PFmethodError_BadFlowLimits(self)
        
        # Check variable limits
        if not np.all(lx < ux):
            raise PFmethodError_BadVarLimits(self)

        # Other checks
        try:
            assert(Gx.shape == (nx,nx))
            assert(np.all(Gx.row == Gx.col))
            assert(np.all(Gx.data == np.ones(nx)))
            assert(Gz.shape == (net.num_branches,nx))
            assert(l.shape == (n,))
            assert(u.shape == (n,))
            assert(np.all(l < u))
            assert(np.abs(problem.phi-net.base_power*(0.5*np.dot(y,H*y)+np.dot(g,y))) < 1e-8)
            assert(H.shape == (n,n))
            assert(A.shape == (net.num_buses+nz,n))
        except AssertionError:
            raise PFmethodError_BadProblem(self)
            
        QPproblem = QuadProblem(H,g,A,b,l,u)
        
        # Set up solver
        solver = OptSolverIQP()
        
        # Solve
        try:
            solver.solve(QPproblem)
        except OptSolverError,e:
            raise PFmethodError_SolverError(self,e)
        finally:
            
            # Get results
            self.set_status(solver.get_status())
            self.set_error_msg(solver.get_error_msg())
            self.set_iterations(solver.get_iterations())
            self.set_primal_variables(solver.get_primal_variables())
            self.set_dual_variables(solver.get_dual_variables())
            self.set_net_properties(net.get_properties())
            self.set_problem(problem)
            
    def update_network(self,net):
    
        pass
        
        """
        # Get data
        problem = self.results['problem']
        x = self.results['primal_variables']
        lam,nu,mu,pi = self.results['dual_variables']
       
        # No problem
        if problem is None:
            raise PFmethodError_NoProblem(self)
 
        # Checks
        assert(problem.x.shape == x.shape)
        assert(net.num_vars == x.size)
        assert(problem.A.shape[0] == lam.size)
        assert(problem.f.shape[0] == nu.size)
        assert(mu is None)
        assert(pi is None)

        # Network quantities
        net.set_var_values(x)
        
        # Network sensitivities
        net.clear_sensitivities()
        problem.store_sensitivities(None,nu,None,None)
        """