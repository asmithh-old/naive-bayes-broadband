import pandas as pd
import csv, urllib2, json, random
import numpy as np
import matplotlib.pyplot as plt

processedData = pd.DataFrame.from_csv('bayesprocesseddata.csv')
data = processedData.to_dict()
occupationDict = {'workers agr, forestry, fishing, hunting, mining': 0.0, 'workers construction' : 1.0, 'workers manufacturing' : 2.0, 'workers wholesale trade' : 3.0, 'workers retail trade' : 4.0, 'workers transp, util' : 5.0, 'workers info' : 6.0, 'workers finance, real estate, insurance' : 7.0, 'workers professional, sci, mgmt, admin' : 8.0, 'workers healthcare, edu, soc. asst' : 9.0, 'workers arts, ent, rec, accom, food' : 10.0, 'workers other services' : 11.0,'workers public adim' : 12.0, 'workers armed forces' : 13.0 }

def make_prime(n):
    res =  n ** 2 + n + 41.0
    return res
    
falsePos = 0
falseNeg = 0        

def test_and_train(features):
    yes = {}
    no = {}
    yesTup = {}
    for f in features:
        yes[f] = {}
        no[f] = {}
        yesTup[f] = []
    
        if f == 'top industries':
            #for all possible prime number hash values, instantiate an entry in the dictionary of probabilities to 0.
            for job1 in occupationDict.keys():
                for job2 in occupationDict.keys():
                    for job3 in occupationDict.keys():
                        for job4 in occupationDict.keys():
                            yes[f][make_prime(occupationDict[job1]) * make_prime(occupationDict[job2]) * make_prime(occupationDict[job3]) * make_prime(occupationDict[job4])] = 0
                            no[f][make_prime(occupationDict[job1]) * make_prime(occupationDict[job2]) * make_prime(occupationDict[job3]) * make_prime(occupationDict[job4])] = 0
        else:
        
            for n in range(-3, 9):
                #otherwise for all conceivable binnings, instantiate an entry in the dictionary of probabilities to 0.
                yes[f][n] = 0
                no[f][n] = 0
            
    featurePts = {}
    for f in features:
        featurePts[f] = {'x':[], 'y':[]}
        
    def train(trainSet):
        catDict = True
        for k in trainSet:
        
            internet = data[k]['internet']
            if internet == 'True':
                catDict = yes
            elif internet == 'False':
                #print "foo"
                catDict = no
           
            for f in features:
                if f == 'top industries':
                    catDict[f][float(data[k][f])] += 1
                else:
                    catDict[f][int(data[k][f])] += 1
            
                #for feature in k.features:
                #add to priors for P(x_i|B) 
                #using half of the data, we "train" by computing the priors P(X_i = x_i|B) where B is the classification (yes/no), X_i is a feature, and x_i is a                   value the given feature can take.  
                
        for f in features:
            
            #creates probabilities by dividing totals for each value of a feature by total number of census tracts that fall into the category.
            if f == 'top industries':
                yesSum = 0.0
                noSum = 0.0
                for n in yes[f].keys():
                    yesSum += float(yes[f][n])
                    noSum += float(no[f][n])
                for n in yes[f].keys():
                    yes[f][n] = float(yes[f][n])/yesSum
                    no[f][n] = float(no[f][n])/noSum
                    if yes[f][n] != 0:
                        yesTup[f].append((n, no[f][n]/yes[f][n]))
            else:
                yesSum = 0.0
                noSum = 0.0
                for n in range(-3, 9):
                    yesSum += float(yes[f][n])
                    noSum += float(no[f][n])
                for n in range(-3, 9):
                    yes[f][n] = float(yes[f][n])/yesSum
                    no[f][n] = float(no[f][n])/noSum
                    if yes[f][n] != 0:
                        yesTup[f].append((n, no[f][n]/yes[f][n]))
                        
        #finds the prior--the probability, given no other information, that a randomly chosen county has good internet or doesn't.
        #sorry good internet is so vaguely defined.
        
        priorYes = yesSum/(yesSum + noSum)
        priorNo = noSum/(yesSum + noSum)
        return (yes, no, priorYes, priorNo)

    def test((yes, no, priorYes, priorNo), testSet, ):
        falsePos = 0
        falseNeg = 0
        #count number of false positives and false negatives to see if there's a trend (it ends up being about 50/50 i think)
        successes = 0.0
        failures = 0.0
        failList = []
        #get a list of failures--do they have something in common?
        
        for t in testSet:
            #evaulate probabilities as log-likelihood--ok to do because log(x) increases monotonically, and a good idea because multiplying very small numbers                  together tends to lead to python being sad because floating point arithmetic. 
            Pyes = np.log2(priorYes)
            Pno = np.log2(priorNo)
            for f in features:
                x = data[t][f]
                Pyes += np.log2(yes[f][float(x)])
                Pno += np.log2(no[f][float(x)])
            Pyes = 2.0 ** Pyes 
            Pno = 2.0 ** Pno
            #we use maximum-likelihood decision rule--the bigger probability, whether that be P(yes|features) or P(no|features), wins.
            if Pyes >= Pno  and data[t]['internet'] == 'True':
                #print 'success'
                successes += 1.0
            elif Pno > Pyes  and data[t]['internet'] == 'False':
                #print 'success'
                successes += 1.0
            else:
                #print 'failure'
                failures += 1.0
                failList.append((t, data[t]))
                
                if Pyes >= Pno and data[t]['internet'] == 'False':
                    falsePos += 1.0
                elif Pno > Pyes and data[t]['internet'] == 'True':
                    falseNeg += 1.0

        for f in features:
            for i in yesTup[f]:
                featurePts[f]['x'].append(i[0])
                featurePts[f]['y'].append(i[1])

        return (successes, failures, failList, successes/(successes + failures)) 

    total = 0.0
    good = 0.0

    for i in range(0,100):   
        allData = data.keys() 
        random.shuffle(allData)       
        trainSet = allData[0:1611]  
        testSet = allData[1611:]
        good += test(train(trainSet), testSet)[3]
        total += 1.0
    print good / total
    
    #for f in features:
       #  print f
       # x = featurePts[f]['x']
       # y = featurePts[f]['y']
       #  plt.plot(x, y, linestyle = ':', color = 'm')
       #  plt.show()
       
#iteratively getting rid of features doesn't change much--adding/subtracting any of the below features doesn't substantially change the accuracy
#which right now is around 72%.

masterFeatures = ['high school grads', 'poverty level', 'relative english skill', 'population density', 'percent foreign-born', 'race entropy', 'gini index', 'top industries']

#for m in range(len(masterFeatures)):

  #  featureList = masterFeatures[0:m] + masterFeatures[m+1:]
  #  print masterFeatures[m]
  #  print featureList
  #  test_and_train(featureList, falsePos, falseNeg)
  #  print falsePos
  #  print falseNeg
test_and_train(masterFeatures)