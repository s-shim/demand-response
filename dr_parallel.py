import pandas as pd
import math
import random
import time
import copy
import datetime
import socket
import multiprocessing as mp

machineName = socket.gethostname()

def ARR(iteration, inst, numUsers, allUsers, p, d, z_d, z_r, r, tic, timeLimit,machineName,minReduction):
    # inst, numUsers, allUsers, p, d, z_d, z_r, r, tic, timeLimit = inputPackage
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

    machineArray = [machineName]
    iterArray = [iteration]
    popArray = [numUsers]
    instArray = [inst]
    
    z_d_Array = [z_d]
    z_r_Array = [z_r]
    r_Array = [r]
    min_Array = [minReduction]
    tlArray = [timeLimit]
    
    toc = time.time()
    timeArray = [toc - tic]
    trialArray = [0]
    biArray = [bestIncentive]
    bdArray = [bestDemand]
    avgArray = [avgDemand_best]
    varArray = [varDemand_best]
    stdArray = [stdDemand_best]
    
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

                machineArray += [machineName]
                iterArray += [iteration]
                popArray += [numUsers]
                instArray += [inst]
                
                z_d_Array += [z_d]
                z_r_Array += [z_r]
                r_Array += [r]
                min_Array += [minReduction]
                tlArray += [timeLimit]
                
                timeArray += [toc - tic]
                trialArray += [trial]
                biArray += [bestIncentive]
                bdArray += [bestDemand]
                avgArray += [theDemand_avg_best]
                varArray += [theDemand_var_best]
                stdArray += [theDemand_std_best]

                listColumn = list(zip(machineArray,iterArray,popArray,instArray,z_d_Array,z_r_Array,r_Array,min_Array,tlArray,timeArray,trialArray,biArray,bdArray,avgArray,varArray,stdArray))
                nameColumn = ['Machine','Iteration','Users','Instance','z_d','z_r','r','minReduction','timeLimit','Time','Trial','Incentive','Demand','Average','Variance','STD']
                process = pd.DataFrame(listColumn,columns = nameColumn)
                process.to_csv(r'mp/process/dr_process_%s_inst%s_iter%s.csv'%(numUsers,inst,iteration), index = False)#Check
        
        if reset == False:
            alpha = 1 / (1 + math.exp(4 * RMSD))
            for i in allUsers:
                invited_seed[i] = invited_seed[i] * (1 - alpha)
            for i in bestInvited:
                invited_seed[i] += alpha
            
            
        toc = time.time()    
        
    bestPackage0 = bestInvited, invited_best 
    bestPackage1 = bestIncentive, bestDemand
    bestPackage2 = theDemand_avg_best, theDemand_var_best, theDemand_std_best         

    return iteration, bestPackage0, bestPackage1, bestPackage2


def ARR2(arg):    
    iteration, inst, numUsers, allUsers, p, d, z_d, z_r, r, tic, timeLimit, machineName, minReduction = arg    
    return ARR(iteration, inst, numUsers, allUsers, p, d, z_d, z_r, r, tic, timeLimit, machineName, minReduction)

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
#numUsers, minReduction, timeLimit = 30, 15, 10 # demand reduction - buffer > minReduction
numUsers, minReduction, timeLimit = 400, 200, 30 # demand reduction - buffer > minReduction
# numUsers, minReduction, timeLimit = 10000, 5000, 600 # demand reduction - buffer > minReduction


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

inst = 0
iteration = 0
tic = time.time()
 
bestInvited = []
invited_best = {}
for i in allUsers:
    bestInvited += [i]
    invited_best[i] = 1
avgDemand_initial, varDemand_initial, stdDemand_initial = evaluate(bestInvited,p,d)
initialIncentive = r * (avgDemand_initial + z_r * stdDemand_initial)
    
if __name__ == '__main__':
    
    numCores = mp.cpu_count()
    poo = mp.Pool(numCores)

    tic = time.time()        

    # bestPackage0, bestPackage1, bestPackage2 = ARR(iteration, inputPackage)

    multiArgs = []  
    for iteration in range(numCores):
        multiArgs += [(iteration, inst, numUsers, allUsers, p, d, z_d, z_r, r, tic, timeLimit, machineName, minReduction)]  

    results = poo.map(ARR2, multiArgs)
    
    grandIncentive = initialIncentive
    print(grandIncentive)
    for iteration, bestPackage0, bestPackage1, bestPackage2 in results:
        bestIncentive, bestDemand = bestPackage1
        if grandIncentive > bestIncentive:
            grandIteration = iteration
            grandIncentive = bestIncentive
            grandDemand = bestDemand

            bestInvited, invited_best = bestPackage0 
            grandInvited = copy.deepcopy(bestInvited)
            invited_grand = copy.deepcopy(invited_best)
            
            theDemand_avg_grand, theDemand_var_grand, theDemand_std_grand = bestPackage2        

    grand_varName = ['iteration']
    grand_varVal = [grandIteration]
    grand_varName += ['incentive']
    grand_varVal += [grandIncentive]
    grand_varName += ['initial']
    grand_varVal += [initialIncentive]
    grand_varName += ['r']
    grand_varVal += [r]
    grand_varName += ['z_r']
    grand_varVal += [z_r]
    grand_varName += ['z_d']
    grand_varVal += [z_d]
    grand_varName += ['demand']
    grand_varVal += [grandDemand]
    grand_varName += ['demand_avg']
    grand_varVal += [theDemand_avg_grand]
    grand_varName += ['demand_std']
    grand_varVal += [theDemand_std_grand]
    
    for i in allUsers:
        grand_varName += ['X[%s]'%i]
        grand_varVal += [int(invited_grand[i] + 0.0001)]

    listColumn = list(zip(grand_varName,grand_varVal))
    nameColumn = ['varName','varVal']
    summary = pd.DataFrame(listColumn,columns = nameColumn)
    summary.to_csv(r'mp/dr_lopt_%s_inst%s_iter%s.csv'%(numUsers,inst,iteration), index = False)#Check
        