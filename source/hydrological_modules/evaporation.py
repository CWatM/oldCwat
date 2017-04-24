# -------------------------------------------------------------------------
# Name:        Evaporation module
# Purpose:
#
# Author:      PB
#
# Created:     01/08/2016
# Copyright:   (c) PB 2016
# -------------------------------------------------------------------------

from management_modules.data_handling import *


class evaporation(object):
    """
    Evaporation module
    Calculate potential evaporation and pot. transpiration
    """

    def __init__(self, evaporation_variable):
        """The constructor evaporation"""
        self.var = evaporation_variable



# --------------------------------------------------------------------------
# --------------------------------------------------------------------------

    def dynamic(self, coverType, No):
        """
        Dynamic part of the soil module

        calculating potential Evaporation for each land cover class with kc factor
        get crop coefficient, use potential ET, calculate potential bare soil evaporation and transpiration

        :param coverType: Land cover type: forest, grassland  ...
        :param No: number of land cover type: forest = 0, grassland = 1 ...
        :return: potential evaporation from bare soil, potential transpiration
        """

        # get crop coefficient
        # to get ETc from ET0 x kc factor  ((see http://www.fao.org/docrep/X0490E/x0490e04.htm#TopOfPage figure 4:)
        # crop coefficient read for forest and grassland from file

        if dateVar['newStart'] or (dateVar['currDate'].day in [1,11,21]):
            self.var.cropKC = readnetcdf2(binding[coverType + '_cropCoefficientNC'], dateVar['10day'], "10day")
            self.var.cropKC = np.maximum(self.var.cropKC, self.var.minCropKC[No])


        # calculate potential ET
        ##  self.var.totalPotET total potential evapotranspiration for a reference crop for a land cover class
        #self.var.totalPotET[No] = np.minimum(1.0, self.var.cropCorrect  * self.var.cropKC) * self.var.ETRef
        self.var.totalPotET[No] = self.var.cropCorrect * self.var.cropKC * self.var.ETRef

        # calculate potential bare soil evaporation and transpiration
        #self.var.potBareSoilEvap[No] = np.minimum(1.0, self.var.cropCorrect * self.var.minCropKC[No]) * self.var.ETRef
        self.var.potBareSoilEvap[No] = self.var.cropCorrect * self.var.minCropKC[No] * self.var.ETRef
        ## potTranspiration: Transpiration for each land cover class
        #self.var.potTranspiration[No] = np.minimum(1.0, self.var.cropCorrect * self.var.cropKC) * self.var.ETRef - self.var.potBareSoilEvap[No]
        self.var.potTranspiration[No] = self.var.cropCorrect * self.var.cropKC * self.var.ETRef - self.var.potBareSoilEvap[No]

        # evaporation from bare soil for each land cover class


