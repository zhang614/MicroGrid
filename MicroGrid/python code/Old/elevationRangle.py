#analysis of the trade off between the seasonal range of the pannels
#elevation range and the power gathered. Idea is to understant how
#much beniffit is gained from having to get tall in the winter

#estimated energy per day per meter squared
#kW/m^2/day
Energy = [2.76, 3.9,4.84,5.72,7.02,7.26,7.55,7.22,6.16,4.94,3.31,2.27]





def efficiency(angleFromOptimal):
    #the panel is deviating from the optimal in elevation, what is the efficiency?
    #returns between 1.0 and 0.0

