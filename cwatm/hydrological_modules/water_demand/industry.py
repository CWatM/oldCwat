# -------------------------------------------------------------------------
# Name:        Waterdemand modules
# Purpose:
#
# Author:      PB, YS, MS, JdB
#
# Created:     15/07/2016
# Copyright:   (c) PB 2016
# -------------------------------------------------------------------------

from cwatm.management_modules import globals
import numpy as np
from cwatm.management_modules.data_handling import returnBool, binding, cbinding, loadmap, readnetcdf2, divideValues

class waterdemand_industry:
    """
    WATERDEMAND domestic

    calculating water demand -
    industry based on precalculated maps

    **Global variables**

    ====================  ================================================================================  =========
    Variable [self.var]   Description                                                                       Unit     
    ====================  ================================================================================  =========
    InvCellArea           Inverse of cell area of each simulated mesh                                       m-1      
    M3toM                 Coefficient to change units                                                       --       
    demand_unit                                                                                                      
    industryTime                                                                                                     
    indWithdrawalVar                                                                                                 
    indConsumptionVar                                                                                                
    industryDemand                                                                                                   
    pot_industryConsumpt                                                                                             
    ind_efficiency                                                                                                   
    ====================  ================================================================================  =========

    **Functions**
    """
    def __init__(self, model):
        self.var = model.var
        self.model = model

    def initial(self):
        """
        Initial part of the water demand module - industry

        """
        if "industryTimeMonthly" in binding:
            if returnBool('industryTimeMonthly'):
                self.var.industryTime = 'monthly'
            else:
                self.var.industryTime = 'yearly'
        else:
            self.var.industryTime = 'monthly'

        if "industryWithdrawalvarname" in binding:
            self.var.indWithdrawalVar = cbinding("industryWithdrawalvarname")
        else:
            self.var.indWithdrawalVar = "industryGrossDemand"
        if "industryConsuptionvarname" in binding:
            self.var.indConsumptionVar = cbinding("industryConsuptionvarname")
        else:
            self.var.indConsumptionVar = "industryNettoDemand"

    def dynamic(self,wd_date):
        """
        Dynamic part of the water demand module - industry
        read monthly (or yearly) water demand from netcdf and transform (if necessary) to [m/day]

        """
        if self.var.industryTime == 'monthly':
            new = 'newMonth'
        else:
            new = 'newYear'

        if globals.dateVar['newStart'] or globals.dateVar[new]:
            self.var.industryDemand = readnetcdf2('industryWaterDemandFile', wd_date, self.var.industryTime, value=self.var.indWithdrawalVar)
            self.var.pot_industryConsumption = readnetcdf2('industryWaterDemandFile', wd_date, self.var.industryTime, value=self.var.indConsumptionVar)
            self.var.industryDemand = np.where(self.var.industryDemand > self.var.InvCellArea, self.var.industryDemand, 0.0)
            self.var.pot_industryConsumption = np.where(self.var.pot_industryConsumption > self.var.InvCellArea, self.var.pot_industryConsumption, 0.0)
            self.var.ind_efficiency = divideValues(self.var.pot_industryConsumption, self.var.industryDemand)

            # transform from mio m3 per year (or month) to m/day if necessary
            if not self.var.demand_unit:
                if self.var.industryTime == 'monthly':
                    timediv= globals.dateVar['daysInMonth']
                else:
                    timediv = globals.dateVar['daysInYear']
                self.var.industryDemand = self.var.industryDemand * 1000000 * self.var.M3toM / timediv
                self.var.pot_industryConsumption = self.var.pot_industryConsumption * 1000000 * self.var.M3toM / timediv