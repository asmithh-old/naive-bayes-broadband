import pandas as pd
import csv, urllib2, json, ast
import numpy as np
import matplotlib.pyplot as plt

dataFramedByCounty = pd.DataFrame.from_csv('naivebayesbroadbanddata.csv')
fr = dataFramedByCounty.to_dict()

dataByCountyBinned = {}

occupationDict = {'workers agr, forestry, fishing, hunting, mining': 0.0, 'workers construction' : 1.0, 'workers manufacturing' : 2.0, 'workers wholesale trade' : 3.0, 'workers retail trade' : 4.0, 'workers transp, util' : 5.0, 'workers info' : 6.0, 'workers finance, real estate, insurance' : 7.0, 'workers professional, sci, mgmt, admin' : 8.0, 'workers healthcare, edu, soc. asst' : 9.0, 'workers arts, ent, rec, accom, food' : 10.0, 'workers other services' : 11.0,'workers public adim' : 12.0, 'workers armed forces' : 13.0 }

#okay so maybe this is not the ideal solution but i will be making a prime number hash of the top 4 jobs (assuming n^2 + n + 41 is prime for n < 40) so the set of the top 4 industries in a census tract will correspond to a unique product of primes.

jobHash = {}

def make_prime(n):
    #makes a prime given an integer less than 40.
    res =  n ** 2 + n + 41.0
    return res
    

def gaussian_bin_var(var, varMean, varSigma):
    #bins value based on the distance (in standard deviations) it is from the mean.
    var = float(var)
    varMean = float(varMean)
    varSigma = float(varSigma)
    if var < varMean - 3.0 * varSigma:
        return -3
    elif var >= varMean - 3.0 * varSigma and var < varMean - 2.0 * varSigma:
        return -2
    elif var >= varMean - 2.0 * varSigma and var < varMean - 1.0 * varSigma:
        return -1
    elif var >= varMean - 1.0 * varSigma and var < varMean + 1.0 * varSigma:
        return 1
    elif var >= varMean + 1.0 * varSigma and var < varMean + 2.0 * varSigma:
        return 2
    elif var >= varMean + 2.0 * varSigma:
        return 3
        
def sketchy_bin_var(var, step, minVal, maxVal):
    #bins variable based on simple linear divisions at equal intervals. starts at min value of the variable, ends at the maximum value.
    marker = minVal
    iteration = 0
    while marker < maxVal and marker < var:
        marker += step
        iteration += 1           
    return iteration - 1

for c in fr.keys(): 
    dataByCountyBinned[c] = {}
    url = 'http://www.broadbandmap.gov/broadbandmap/analyze/dec2012/summary/population/county/ids/'
    url += fr[c]['FIPS']
    url += '?format=json'
    nextfileobj = urllib2.urlopen(url)
    broadband = json.loads(nextfileobj.read())
    dataByCountyBinned[c]['percent with broadband'] = broadband['Results'][0]['downloadSpeedGreaterThan3Mbps']
    #find the percent of people who have broadband internet (technically defined by the fcc as download speed > 4mbps but here defined as > 3mbps because that's        what the api returns)
    if broadband['Results'][0]['downloadSpeedGreaterThan3Mbps'] < .95:
        #here we use >95% of people have broadband as the cutoff for 'good internet' 
        #TODO: find a better metric of "good" internet--adoption vs access; mobile vs wired connections.
        dataByCountyBinned[c]['internet'] = False
    else:
        dataByCountyBinned[c]['internet'] = True
        
    #computing prime number hash of top 4 industries.
    industry = 1.0
    for i in ast.literal_eval(fr[c]['top four industries']):
        industry *= float(occupationDict[i]) ** 2 + float(occupationDict[i]) + 41.0
    dataByCountyBinned[c]['top industries'] = industry
    #bin variables (gini index, high school grads, population density, and poverty level are all vaguely gaussian, but the other aren't).
    #population density is log-gaussian.
    gini = fr[c]['gini index']
    dataByCountyBinned[c]['gini index'] = gaussian_bin_var(float(gini), 0.458730148599, 0.0343579451109 )
    highschool = fr[c]['percent gt 25 at least high school diploma']
    dataByCountyBinned[c]['high school grads'] = gaussian_bin_var(float(highschool), 84.1482823965,  7.35303247189 )
    foreignborn = fr[c]['percent foreign-born']
    dataByCountyBinned[c]['percent foreign-born'] = sketchy_bin_var(float(foreignborn)/100.0,0.05,  0.0, 0.4 )
    raceentropy = fr[c]['race entropy']
    dataByCountyBinned[c]['race entropy'] = sketchy_bin_var(float(raceentropy), 0.25,  0.0, 1.5)
    popdensity = np.log2(float(fr[c]['population density']))
    dataByCountyBinned[c]['population density'] = gaussian_bin_var(popdensity,5.42975803462,  2.59012290328 )
    english = fr[c]['relative english skill']
    dataByCountyBinned[c]['relative english skill'] = sketchy_bin_var(float(english), 0.2,  2.6, 4.0 )
    povertylvl = fr[c]['poverty level']
    dataByCountyBinned[c]['poverty level'] = gaussian_bin_var(float(povertylvl),0.166444522379,  0.0791955637825 )

processedData = pd.DataFrame.from_dict(dataByCountyBinned)
processedData.to_csv('bayesprocesseddata.csv')
#write to pandas dataframe and then to .csv for easier access.