import requests
import pickle
import numpy as np
import os
import threading
import time

class DataPot:

    def __init__(self):
        # API urls to ibm
        self.url = []
        self.url.append("https://waterpoint-engine-challenge-dev.mybluemix.net/sensors")
        self.url.append("https://waterpoint-engine-challenge-dev.mybluemix.net/sensors/daily-county-readings/")
        self.url.append("https://waterpoint-engine-challenge-dev.mybluemix.net/sensors/site/")
        self.url.append('https://waterpoint-engine-challenge-dev.mybluemix.net/sensors/sites/summary')

        #pickle file names
        self.files = ['data', 'summary', 'countyDataDic', 'siteReadings', 'siteDailyReads', 'siteMonthly']
        self.repo = {}
        self.loadFiles()

        # pull data from API in the background
        thread = threading.Thread(target=self.keepAlive, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()

    def keepAlive(self, interval=300):
        while True:
            print ('Working')
            self.reloadAPI()
            time.sleep(interval)

    def loadFiles(self):
        for each in self.files:
            pth = "data/%s.pickle" %(each)
            if os.path.exists(pth):
                self.repo[each] = pickle.load(open(pth, 'rb'))
            else:
                self.repo[each] = None

    def reloadAPI(self):
        self.summary()
        self.sensors()
        self.latestCountyReadings()
        self.latestSiteReadings()

    def summary(self):
        url = self.url
        re = requests.get(url[3])
        summary = re.json()['data']
        pickle.dump(summary, open('data/summary.pickle', 'wb'))

        #self.repo['summary'] = summary
        self.loadFiles()

    def sensors(self):
        url = self.url
        re = requests.get(url[0])
        data = re.json()['data']

        counties = []
        siteId = {}

        for each in data:
            county = each['county']
            mwaterId = each['mwater_id']
            if county not in counties:
                counties.append(county)

            found = False
            for key, value in siteId.items():
                if mwaterId in value:
                    found = True

            if found is False:
                if county not in siteId.keys():
                    siteId[county] = []
                    siteId[county].append(mwaterId)
                else:
                    siteId[county].append(mwaterId)

        countyDataDic = {}
        for each in counties:
            rl = "%s%s" %(url[1], each)
            re = requests.get(rl)
            d = re.json()['data']
            countyDataDic[each] = d

        pickle.dump(data, open('data/data.pickle', 'wb'))
        pickle.dump(countyDataDic, open('data/countyDataDic.pickle', 'wb'))

        #self.repo['data'] = data
        #self.repo['countyDataDic'] = countyDataDic
        self.loadFiles()
        self.counties = counties
        self.siteId = siteId

    def latestCountyReadings(self):
        url = self.url
        siteId = self.siteId

        siteReadings = {}
        for county, sites in siteId.items():
            for each in sites:
                rl = "%s%s" %(url[2], each)
                print (rl)
                re = requests.get(rl)
                siteReadings[each] = re.json()['data']
                print (re.json()['statusMessage'])

        pickle.dump(siteReadings, open('data/siteReadings.pickle', 'wb'))
        #self.repo['siteReadings'] = siteReadings
        self.loadFiles()

    def latestSiteReadings(self):
        url = self.url
        countyDataDic = self.repo['countyDataDic']

        siteDailyReads = {}
        siteMonthly = {}
        #for site in siteId.keys():
        for county, sites in countyDataDic.items():
            for eachSite in sites:
                sId = eachSite['mWaterId']
                dat = eachSite['localDate']
                com = "%s-%s" %(dat.split('-')[0], dat.split('-')[1])

                if sId not in siteDailyReads.keys():
                    siteDailyReads[sId] = []
                    siteMonthly[sId] = {}
                    siteDailyReads[sId].append(eachSite)
                else:
                    siteDailyReads[sId].append(eachSite)

                if com not in siteMonthly[sId].keys():
                    siteMonthly[sId][com] = []
                    siteMonthly[sId][com].append(eachSite)
                elif com in siteMonthly[sId].keys():
                    siteMonthly[sId][com].append(eachSite)

        pickle.dump(siteDailyReads, open('data/siteDailyReads.pickle', 'wb'))
        pickle.dump(siteMonthly, open('data/siteMonthly.pickle', 'wb'))

        self.loadFiles()

    def test(self):
        for key, value in self.repo.items():
            if value is None:
                print (key, '=> is Not Initialized')

    def getCounties(self):
        counties = []

        try:
            for each in self.repo['data']:
                county = each['county']
                mwaterId = each['mwater_id']

                if county not in counties:
                    counties.append(county)
        except:
            return counties

        return counties

    def getSiteReadsByCounty(self, county = None):
        if county is None or county not in self.getCounties():
            # print (self.repo['siteDailyReads'].keys())
            return self.repo['siteDailyReads'][list(self.repo['siteDailyReads'].keys())[0]]
        else:
            lim = 300
            title = "{} Water Points".format(county)
            mod = {"title": title, "sites":{}, "siteNames":[]}


            for siteId, lst in self.repo['siteDailyReads'].items():
                for each in lst:
                    cnty = each['county']
                    houses = each['households']
                    date = each['localDate']
                    yieldDaily = each['yieldDaily']
                    siteName = each['siteName'].split(' - ')[1]
                    status = each['expertStatus']

                    if cnty == county:
                        if siteName not in mod['siteNames']:
                            mod['siteNames'].append(siteName)

                        tmp = {}
                        tmp['status'] = status
                        tmp['households'] = houses
                        tmp['name'] = siteName
                        tmp['date'] = date
                        tmp['latestYieldDaily'] = yieldDaily

                        if siteName not in mod['sites'].keys():
                            tmp['data'] = []
                            mod['sites'][siteName] = tmp
                            mod['sites'][siteName]['data'].append(yieldDaily)

                        elif len(mod['sites'][siteName]['data']) < lim:
                            mod['sites'][siteName]['data'].append(yieldDaily)
            return mod
