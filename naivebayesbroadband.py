import urllib2, json, ast, re, sys, csv
import numpy as np
import pandas as pd

#gets demographic data from the census api and puts it into data tables.
#TODO: residential data about physical structure of neighborhood (e.g. vacant buildings, public housing, owner-occupied buildings)

codes = {}
#codes stores API codes by what they code for.  

codes['total population'] = 'B01001_001E'

############random notes###############
#sequence 44 is area of degree (STEM, etc. by gender, age.)

################################
#api likes this one too.
codes['population white'] = 'B01001A_001E'
codes['population black/afr am'] = 'B01001B_001E'
codes['population native am/ak native'] = 'B01001C_001E'
codes['population asian'] = 'B01001D_001E'
codes['population native hi/pac isl'] = 'B01001E_001E'
codes['population other race'] = 'B01001F_001E'

race = ['total population', 'population white', 'population black/afr am', 'population native am/ak native', 'population asian', 'population native hi/pac isl', 'population other race']
#around seq. 2 excel spreadsheets for race-related codes.
#################################

######################################
#api likes
codes['population foreign-born'] = 'B05006_001E'
codes['population born in europe'] = 'B05006_002E'
codes['population born in asia'] = 'B05006_047E'
codes['population born in africa'] = 'B05006_091E'
codes['population born in oceania'] = 'B05006_116E'
codes['population born in americas outside US'] = 'B05006_123E'
#these codes are from seq. 10 of excel spreadsheets.
#foreign-born excludes those born at sea
#are these useful classifications to make, or is classifying with e.g. western europe, southeast asia, etc. better? which classifications are most useful? halp....

placeOfOrigin = ['total population', 'population foreign-born', 'population born in europe','population born in asia', 'population born in africa', 'population born in oceania', 'population born in americas outside US' ]
########################################

#############################################
#all are for workers 16+ in the industry
#seq. 26 in spreadsheets
#api likes these codes too.
codes['total workers 16+'] = 'B08126_001E'
codes['workers agr, forestry, fishing, hunting, mining'] = 'B08126_002E'
codes['workers construction'] = 'B08126_003E'
codes['workers manufacturing'] = 'B08126_004E'
codes['workers wholesale trade'] = 'B08126_005E'
codes['workers retail trade'] = 'B08126_006E'
codes['workers transp, util'] = 'B08126_007E'
codes['workers info'] = 'B08126_008E'
codes['workers finance, real estate, insurance'] = 'B08126_009E'
codes['workers professional, sci, mgmt, admin'] = 'B08126_010E'
codes['workers healthcare, edu, soc. asst'] = 'B08126_011E'
codes['workers arts, ent, rec, accom, food'] = 'B08126_012E'
codes['workers other services'] = 'B08126_013E'
codes['workers public adim'] = 'B08126_014E'
codes['workers armed forces'] = 'B08126_015E'

whereWork = ['total population', 'total workers 16+', 'workers agr, forestry, fishing, hunting, mining', 'workers construction', 'workers manufacturing', 'workers wholesale trade', 'workers retail trade', 'workers transp, util', 'workers info', 'workers finance, real estate, insurance','workers professional, sci, mgmt, admin', 'workers healthcare, edu, soc. asst', 'workers arts, ent, rec, accom, food', 'workers other services', 'workers public adim', 'workers armed forces' ]
###########################################

############################################
#primary lang
#speaks only english; or, for language in other languages, (speaks x and y proficiency level in english)
#all the data is for population 5+
#works in api

codes['pop 5+'] = 'B16005_001E'
codes['pop 5+ native to US'] = 'B16005_002E'
codes['pop 5+ native only English'] = 'B16005_003E'
codes['pop 5+ native speak Spanish'] = 'B16005_004E'
codes['pop 5+ native sp, eng v well'] = 'B16005_005E'
codes['pop 5+ native sp, eng well']= 'B16005_006E'
codes['pop 5+ native sp, eng not well']= 'B16005_007E'
codes['pop 5+ native sp, eng not at all'] = 'B16005_008E'
codes['pop 5+ native speak other indo-euro']  = 'B16005_009E'
codes['pop 5+ native other indo-euro, eng v well'] = 'B16005_010E'
codes['pop 5+ native other indo-euro, eng well'] = 'B16005_011E'
codes['pop 5+ native other indo-euro, eng not well'] = 'B16005_012E'
codes['pop 5+ native other indo-euro, eng not at all'] = 'B16005_013E'
codes['pop 5+ native speak asian/pi'] = 'B16005_014E'
codes['pop 5+ native asian/pi, eng v well'] = 'B16005_015E'
codes['pop 5+ native asian/pi, eng well'] = 'B16005_016E'
codes['pop 5+ native asian/pi, eng not well'] = 'B16005_017E'
codes['pop 5+ native asian/pi, eng not at all'] = 'B16005_018E'
codes['pop 5+ native speak other'] = 'B16005_019E'
codes['pop 5+ native other, eng v well'] = 'B16005_020E'
codes['pop 5+ native other, eng well'] = 'B16005_021E'
codes['pop 5+ native other, eng not well'] = 'B16005_022E'
codes['pop 5+ native other, eng not at all'] = 'B16005_023E'
codes['pop 5+ foreign-born speak Spanish'] = 'B16005_026E'
codes['pop 5+ foreign-born sp, eng v well']= 'B16005_027E'
codes['pop 5+ foreign-born sp, eng well'] = 'B16005_028E'
codes['pop 5+ foreign-born sp, eng not well'] = 'B16005_029E'
codes['pop 5+ foreign-born sp, eng not at all'] = 'B16005_030E'

primaryLang = ['pop 5+','pop 5+ native to US', 'pop 5+ native only English', 'pop 5+ native speak Spanish', 'pop 5+ native sp, eng v well', 'pop 5+ native sp, eng well' , 'pop 5+ native sp, eng not well','pop 5+ native sp, eng not at all', 'pop 5+ native speak other indo-euro', 'pop 5+ native other indo-euro, eng v well', 'pop 5+ native other indo-euro, eng well', 'pop 5+ native other indo-euro, eng not well', 'pop 5+ native other indo-euro, eng not at all', 'pop 5+ native speak asian/pi', 'pop 5+ native asian/pi, eng v well', 'pop 5+ native asian/pi, eng well','pop 5+ native asian/pi, eng not well',  'pop 5+ native asian/pi, eng not at all', 'pop 5+ native speak other', 'pop 5+ native other, eng v well', 'pop 5+ native other, eng well', 'pop 5+ native other, eng not well', 'pop 5+ native other, eng not at all', 'pop 5+ foreign-born speak Spanish','pop 5+ foreign-born sp, eng v well',  'pop 5+ foreign-born sp, eng well','pop 5+ foreign-born sp, eng not well',  'pop 5+ foreign-born sp, eng not at all' ]

##################################################

############################################
#educational attainment.
#am assuming figures are cumulative (# of people where highest education lvl attained = x)
#sequence 43 in excel spreadsheets
#do i need more granularity in education levels less than hs diploma? 
#api doesn't like current codes. fuuuuuck
#need to figure out a fix for this. 
#LITERALLY THE WORST
codes['pop 25+'] = 'B15003_001E'
#codes['pop 25+ no schooling'] = 'B15003_002E'
#codes['pop 25+ 3rd grade education'] = 'B15003_007E'
#codes['pop 25+ 6th grade education'] = 'B15003_010E'
#codes['pop 25+ 9th grade education'] = 'B15003_013E'
codes['pop 25+ regular diploma hs'] = 'B15003_017E'
codes['pop 25+ alt diploma hs'] = 'B15003_018E'
codes['pop 25+ lt 1yr college'] = 'B15003_019E'
codes['pop 25+ gt 1yr college no deg'] = 'B15003_020E'
codes["pop 25+ associate's degree"] = 'B15003_021E'
codes["pop 25+ bachelor's"] = 'B15003_022E'
codes["pop 25+ master's"] = 'B15003_023E'
codes["pop 25+ professional deg"] = 'B15003_024E'
codes['pop 25+ doctorate'] = 'B15003_025E'

eduAttain = ['pop 25+', 'pop 25+ regular diploma hs',  'pop 25+ alt diploma hs', 'pop 25+ lt 1yr college', 'pop 25+ gt 1yr college no deg', "pop 25+ associate's degree", "pop 25+ bachelor's", "pop 25+ master's",  "pop 25+ professional deg", 'pop 25+ doctorate']

#eduAttain = ['pop 25+', 'pop 25+ no schooling','pop 25+ 3rd grade education', 'pop 25+ 6th grade education', 'pop 25+ 9th grade education','pop 25+ regular diploma hs',  'pop 25+ alt diploma hs', 'pop 25+ lt 1yr college', 'pop 25+ gt 1yr college no deg', "pop 25+ associate's degree", "pop 25+ bachelor's", "pop 25+ master's",  "pop 25+ professional deg", 'pop 25+ doctorate']

##################################################

############################################
#poverty level
#seq 54
#is household the right unit of measure?
#api call works
codes['households'] = 'B17017_001E'
codes['households income last 12 mo below poverty lvl'] = 'B17017_002E'

povertyLevel = ['households', 'households income last 12 mo below poverty lvl']
##################################################

##################################################
#household income
#seq 59
#gini-ify?
#requesting to api works
codes['num of households'] = 'B19001_001E'
codes['households income < 10k'] = 'B19001_002E'
codes['households income 10k-15k'] = 'B19001_003E'
codes['households income 15k-20k'] = 'B19001_004E'
codes['households income 20k-25k'] = 'B19001_005E'
codes['households income 25k-30k'] = 'B19001_006E'
codes['households income 30-35k'] = 'B19001_007E'
codes['households income 35-40k'] = 'B19001_008E'
codes['households income 40-45k'] = 'B19001_009E'
codes['households income 45-50k'] = 'B19001_010E'
codes['households income 50-60k'] = 'B19001_011E'
codes['households income 60-75k'] = 'B19001_012E'
codes['households income 75-100k'] = 'B19001_013E'
codes['households 100-125k'] = 'B19001_014E'
codes['households 125-150k'] = 'B19001_015E'
codes['households 150-200k'] = 'B19001_016E'
codes['households 200k+'] = 'B19001_017E'


incomeBrackets = ['num of households','households income < 10k','households income 10k-15k', 'households income 15k-20k',  'households income 20k-25k', 'households income 25k-30k', 'households income 30-35k','households income 35-40k', 'households income 40-45k', 'households income 45-50k',  'households income 50-60k', 'households income 60-75k', 'households income 75-100k',  'households 100-125k', 'households 125-150k','households 150-200k', 'households 200k+' ]
##################################################

#to get avg household size, divide population by # households.

apiKey = 'YOUR API KEY HERE'



dataPointsByCounty = {}
giniTotal = 0.0
ginis = 0.0
for figList in [povertyLevel, race, incomeBrackets, primaryLang, whereWork, placeOfOrigin,  eduAttain]:
    categoryCode = ''
    for figure in figList:
        categoryCode += codes[figure] + ','
    addr = 'http://api.census.gov/data/2013/acs5?get=' + categoryCode[0:-1] + ',NAME&for=county:*&key=' + apiKey
    #for each county, use the census api to get the relevant data, making requests in batches by figure.
    data = urllib2.urlopen(addr).read()
    try:
        dataList = ast.literal_eval(data)
    except:
        z = 0
        dataList = []
        for i in data.split('['):
            if i != '' and i != '\n':
                z += 1
                try:
                    whale  = ast.literal_eval('[' + i)[0]
                except:
                    i = re.sub('null', '"0"', i)
                    i = re.sub('\]\]', ']', i )
                    whale = ast.literal_eval('[' + i)[0]
                dataList.append(whale)
   # the above are string-manipulation methods to turn the data, which is returned as a string, into a format that python can easily read and parse.  
   #sometimes it is easily parsable (in which case we can use literal_eval) and in other cases we need to remove newlines, brackets, and other intervening
   #characters in order to evaluate the string as a literal. 
   #the end goal is to return a Python list.  
   
#####################################################################
#####################################################################   

    if figList == incomeBrackets:
        for d in dataList[1:]:
            #the following block of code computes the gini index, which is a measure of economic inequality.  
            #0 represents perfect equality (everyone contributes the same amount of income to the total income of the community) 
            #and 1 represents perfect inequality (one person has all the income)
            totalhh = float(d[0])
            lt10kcontrib = float(d[1])* 5000.0
            contrib10to15k = float(d[2]) * 12500.0
            contrib15to20k = float(d[3])* 17500.0
            contrib20to25k = float(d[4]) * 22500.0
            contrib25to30k = float(d[5]) * 27500.0
            contrib30to35k = float(d[6])* 32500.0
            contrib35to40k = float(d[7])* 37500.0
            contrib40to45k = float(d[8]) * 42500.0
            contrib45to50k = float(d[9])* 47500.0
            contrib50to60k = float(d[10]) * 55000.0
            contrib60to75k = float(d[11]) * 67500.0
            contrib75to100k = float(d[12]) * 87500.0
            contrib100to125k = float(d[13]) * 112500.0
            contrib125to150k = float(d[14]) * 137500.0
            contrib150to200k = float(d[15]) * 175000.0
            contribgt200k = float(d[16]) * 450000.0

            totalIncome = lt10kcontrib + contrib10to15k + contrib15to20k + contrib20to25k + contrib25to30k + contrib30to35k + contrib35to40k + contrib40to45k + contrib45to50k + contrib50to60k + contrib60to75k + contrib75to100k + contrib100to125k + contrib125to150k + contrib150to200k + contribgt200k
            avgIncome = totalIncome/1.0
            
            #the above calculates the contribution of each income bracket to the given census tract's total income.
            if totalIncome == 0:
                print "no total income"
                break
            allx = 0.0
            sharelt10k = lt10kcontrib/totalIncome
            giniB = sharelt10k * 0.5 * float(d[1])/totalhh
            allx += sharelt10k
            share10to15k = contrib10to15k/totalIncome
            giniB += allx * float(d[2])/totalhh + 0.5 * share10to15k * float(d[2])/totalhh
            allx += share10to15k
            share15to20k = contrib15to20k/totalIncome
            giniB += allx * float(d[3])/totalhh + 0.5 * share15to20k * float(d[3])/totalhh
            allx += share15to20k
            share20to25k = contrib20to25k/totalIncome
            giniB += allx * float(d[4])/totalhh + 0.5 * share20to25k * float(d[4])/totalhh
            allx += share20to25k
            share25to30k = contrib25to30k/totalIncome
            giniB += allx * float(d[5])/totalhh + 0.5 * share25to30k * float(d[5])/totalhh
            allx += share25to30k
            share30to35k = contrib30to35k/totalIncome
            giniB += allx * float(d[6])/totalhh + 0.5 * share30to35k * float(d[6])/totalhh
            allx += share30to35k
            share35to40k = contrib35to40k/totalIncome
            giniB += allx * float(d[7])/totalhh + 0.5 * share35to40k * float(d[7])/totalhh
            allx += share35to40k
            share40to45k = contrib40to45k/totalIncome
            giniB += allx * float(d[8])/totalhh + 0.5 * share40to45k * float(d[8])/totalhh
            allx += share40to45k
            share45to50k = contrib45to50k/totalIncome
            giniB += allx * float(d[9])/totalhh + 0.5 * share45to50k * float(d[9])/totalhh
            allx += share45to50k
            share50to60k = contrib50to60k/totalIncome
            giniB += allx  * float(d[10])/totalhh + 0.5 * share50to60k * float(d[10])/totalhh
            allx += share50to60k
            share60to75k = contrib60to75k/totalIncome
            giniB += allx * float(d[11])/totalhh + 0.5 * share60to75k * float(d[11])/totalhh
            allx += share60to75k
            share75to100k = contrib75to100k/totalIncome
            giniB += allx * float(d[12])/totalhh + 0.5 * share75to100k * float(d[12])/totalhh
            allx += share75to100k
            share100to125k = contrib100to125k/totalIncome
            giniB += allx * float(d[13])/totalhh + 0.5 * share100to125k * float(d[13])/totalhh
            allx += share100to125k
            share125to150k = contrib125to150k/totalIncome
            giniB += allx * float(d[14])/totalhh + 0.5 * share125to150k * float(d[14])/totalhh
            allx += share125to150k
            share150to200k = contrib150to200k/totalIncome
            giniB += allx * float(d[15])/totalhh + 0.5 * share150to200k * float(d[15])/totalhh
            allx += share150to200k
            sharegt200k = contribgt200k/totalIncome
            giniB += allx * float(d[16])/totalhh + 0.5 * sharegt200k * float(d[16])/totalhh
            allx += sharegt200k
            gini = 1.0 -2 * giniB
            giniTotal += gini
            ginis += 1.0
            dataPointsByCounty[d[-3]]['gini index'] = gini
            dataPointsByCounty[d[-3]]['FIPS'] = d[-2] + d[-1]
            #the gini index is the ratio between the area under the line of perfect equality (slope = 1) and the area under the curve that represents the 
            #share in total income of the bottom x% of earners.  the code above iteratively computes the area under that curve (albeit a trapezoidal approximation              of the curve); for each income bracket, it approximates the area contributed as a trapezoid with height the percentage of people in that income bracket             and widths the share of income before and after the earnings of the income bracket are added.
            #this produces an average gini index of approximately .46 which is pretty damn close to the national average.  
      
    elif figList == povertyLevel:
        for d in dataList[1:]:
            dataPointsByCounty[d[-3]] = {}
            dataPointsByCounty[d[-3]]['poverty level'] = float(d[1])/float(d[0])
            #gets the fraction of people living below the poverty level.
      
    elif figList == primaryLang:
        for d in dataList[1:]:
            dataPointsByCounty[d[-3]]['total population'] = d[0]
            langData = d[0:-3]
            overFive = int(langData[0])
            natEng = int(langData[2])
            #weighted at 4 for native english speakers
            engVWell = int(langData[4]) + int(langData[9]) + int(langData[14]) + int(langData[19]) + int(langData[24])
            #people whose first language a language other than English and speak English 'very well.' weighted at 4 for avg 
            engWell = int(langData[5]) + int(langData[10]) + int(langData[15]) + int(langData[20]) + int(langData[25])
            #first language != English; speak English 'well'. weighted as 3.
            engNotWell = int(langData[6]) + int(langData[11]) + int(langData[16]) + int(langData[21]) + int(langData[26])
            #1st lang != English; speak English 'not well'. weighted as 2.
            noEng = int(langData[7]) + int(langData[12]) + int(langData[17]) + int(langData[22]) + int(langData[27])
            #1st lang != English; don't speak English. weighted as 1.
            engScore = (4.0 * float(natEng + engVWell) + 3.0 * float(engWell) + 2.0 * float(engNotWell) + 1.0 * float(noEng))/float(overFive)
            dataPointsByCounty[d[-3]]['relative english skill'] = engScore
            #approximates average english skill of a given census tract.
        #bin avg skill w/english from 1-4 (not at all -> very well) by rounding average.
  
    elif figList == whereWork:
        #get number of people working in each industry and gets top 4. 
        for d in dataList[1:]:
            y = 2
            peopleInJobs = {}

            for k in d[2:-3]:
                peopleInJobs[whereWork[y]] = k
                y += 1
            peopleJobsSorted = sorted(peopleInJobs, key = peopleInJobs.get, reverse = True)
            dataPointsByCounty[d[-3]]['top four industries'] = peopleJobsSorted[0:4]
    

        
    elif figList == placeOfOrigin:
        for d in dataList[1:-1]:
            continentOfOrigin = {}
            y = 2
            for c in d[2:-3]:
                continentOfOrigin[placeOfOrigin[y]] = c
                y += 1
            continentsSorted = sorted(continentOfOrigin, key = continentOfOrigin.get, reverse = True)
            dataPointsByCounty[d[-3]]['top 2 continents of origin'] = continentsSorted[0:4]
            dataPointsByCounty[d[-3]]['percent foreign-born'] = 100.0 * float(d[1]) / float(dataPointsByCounty[d[-3]]['total population'])
            #does what it says on the tin--top 4 continents of origin and percent foreign-born.

            
    elif figList == race:
        
        def careful_log(n):
            #the virtues of numpy's binary log method are many, but it freaks out if you give it 0 as input. we will assume log(0) is 0 for these purposes.
            if n != 0.0:
                return np.log2(float(n))
            else:
                return 0.0
                
        for d in dataList[1:]:
            #gets shannon entropy of race in bits (log base 2).  lower entropy suggests less diversity. 0 entropy means homogenous population. 
            #if there are 5 race categories evenly distributed the best you're going to get is 2.3ish but i doubt that ever actually happens.
            entropy = 0
            totalPop = float(d[0])
            name = d[-3]
            for r in d[1:-3]:
                entropy -= float(r)/totalPop * careful_log(float(r)/totalPop)
            dataPointsByCounty[d[-3]]['race entropy'] = entropy
        
    elif figList == eduAttain:
        for d in dataList[1:]:
            diploma = 0.0
            for i in d[1:-3]:
                diploma += float(i)
            dataPointsByCounty[d[-3]]['percent gt 25 at least high school diploma'] = 100.0 * diploma / float(d[0])
            #does what it says on the tin--percent of people older than 25 who have graduated high school (includes GED as well as traditional diplomas).
    else:
        pass
        
        
#####################################################################
#####################################################################
for countyName in dataPointsByCounty.keys():
    county = dataPointsByCounty[countyName]['FIPS']
    url = 'http://www.broadbandmap.gov/broadbandmap/demographic/dec2012/county/ids/'
    url += str(county) + ','
    url += '?format=json'
    fileobj = urllib2.urlopen(url)
    allResponse = json.loads(fileobj.read())
    #gets population density (population divided by land area)
    dataPointsByCounty[countyName]['population density'] = float(dataPointsByCounty[countyName]['total population'])/float(allResponse['Results'][0]['landArea'])
#####################################################################
#####################################################################    
    
#TODO: (?) get avg household size and store by county (FIPS): population/#households. bin by histogram.
print dataPointsByCounty['Bristol County, Rhode Island']   
print giniTotal/ginis    
#write this to pandas and then pandas to .csv
dataPoints = pd.DataFrame.from_dict(dataPointsByCounty)
#writes to pandas dataFrame and then to .csv (is easiest and most foolproof way to store/retrieve data.)
print dataPoints
dataPoints.to_csv('naivebayesbroadbanddata.csv')