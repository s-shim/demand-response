import pandas as pd
import math
import random
import time
import copy
import datetime

def evaluate(theInvited,p,d):
    avgDemand = 0
    varDemand = 0
    for i in theInvited:
        avgDemand += p[i] * d[i]
        varDemand += (p[i] * (1 - p[i])) * (d[i] * d[i])
    stdDemand = math.sqrt(varDemand)
    return avgDemand,varDemand, stdDemand


# input parameters
z_d = 3 # critical z-value for demand
z_r = 3 # critical z-value for incentive
r = 1 # incentive ($) per kwh
numUsers, minReduction, timeLimit = 30, 15, 10 # demand reduction - buffer > minReduction
# numUsers, minReduction, timeLimit = 400, 200, 900 # demand reduction - buffer > minReduction


# read input data
demand = pd.read_csv('dr_%s.csv'%numUsers)

# store data
p = {}
d = {}
allUsers = []
for i in demand['user']:
    [p[i]] = demand.loc[demand['user']==i,'p'] 
    [d[i]] = demand.loc[demand['user']==i,'demand (kwh)'] 
    allUsers += [i]

# initial best known solution
bestInvited = []
invited_best = {}
for i in allUsers:
    bestInvited += [i]
    invited_best[i] = 1

avgDemand,varDemand, stdDemand = evaluate(bestInvited,p,d)

# avg demand    
print('avgDemand =',avgDemand)
print('varDemand =',varDemand)
print('stdDemand =',stdDemand)
    
evaDemand = avgDemand - z_d * stdDemand
evaIncentive = (avgDemand + z_r * stdDemand) * r    

bestIncentive = evaIncentive
bestDemand = evaDemand

avgDemand_best,varDemand_best, stdDemand_best = avgDemand,varDemand, stdDemand

print()
print('evaDemand =',evaDemand)
print('evaIncentive =',evaIncentive)

invited_zero = {}
invited_half = {}
invited_seed = {}
for i in allUsers:
    invited_zero[i] = 0
    invited_half[i] = 0.5
    invited_seed[i] = 0.5

tic = time.time()
toc = time.time()
trial = 0
nLocal = 0
while toc - tic < timeLimit:
    trial += 1
    
    invited_perturb = {}
    for i in allUsers:
        invited_perturb[i] = invited_seed[i] * random.random()
    
    sortedUsers = sorted(allUsers, key=lambda i: invited_perturb[i], reverse=True)
    
    theInvited = []
    theDemand_avg = 0
    theDemand_var = 0
    invited_now = copy.deepcopy(invited_zero)
    for i in sortedUsers:
        theInvited += [i]
        theDemand_avg += d[i] * p[i]
        theDemand_var += (d[i] ** 2) * (p[i] * (1 - p[i]))
        theDemand = theDemand_avg - z_d * math.sqrt(theDemand_var)
        invited_now[i] = 1
        if theDemand >= minReduction:
            break

    same = True
    for i in allUsers:
        if invited_best[i] != invited_now[i]:
            same = False
            break
        
    RMSD = 0
    for i in allUsers:
        RMSD += (invited_seed[i] - 0.5) ** 2
    RMSD = RMSD / len(allUsers)
    RMSD = math.sqrt(RMSD)
    
    reset = False
    
    if same == True:
        nLocal += 1
        if random.random() < RMSD * min(nLocal / 20, 1):
            reset = True
            invited_seed = copy.deepcopy(invited_half)

    if same == False:
        nLocal = 0
        evaIncentive = (theDemand_avg + z_r * math.sqrt(theDemand_var)) * r    
        
        if bestIncentive > evaIncentive:
            bestIncentive = evaIncentive
            bestDemand = theDemand
            theDemand_avg_best = theDemand_avg
            theDemand_var_best = theDemand_var
            theDemand_std_best = math.sqrt(theDemand_var_best)
            invited_best = copy.deepcopy(invited_now)
            bestInvited = copy.deepcopy(theInvited)
            toc = time.time()
            print()
            print('trial =', trial, '; bestIncentive =', bestIncentive, '; elapse time =', toc - tic)
            print('bestDemand =', bestDemand, '; theDemand_avg_best =', theDemand_avg_best, '; theDemand_std_best =', theDemand_std_best)
            print(datetime.datetime.now())
    
    if reset == False:
        alpha = 1 / (1 + math.exp(4 * RMSD))
        for i in allUsers:
            invited_seed[i] = invited_seed[i] * (1 - alpha)
        for i in bestInvited:
            invited_seed[i] += alpha
        
        
    toc = time.time()    
    
    
