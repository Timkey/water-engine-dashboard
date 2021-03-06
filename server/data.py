import requests
#import joblib as pickle
from klepto.archives import file_archive
import numpy as np
import os
import threading
import time

import zlib, json, base64

ZIPJSON_KEY = 'base64(zip(o))'

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

    def pickleDump(self, data=None, fileName=None):
        if data is not None and fileName is not None:
            #json.dump(data, open(fileName, 'wb'))
            #data = json.dumps(data)
            data = self.json_zip(data)
            with open(fileName, 'w') as outfile:
                json.dump(data, outfile, sort_keys=True)
            # tmp = file_archive(fileName)
            # tmp['payLoad'] = data
            # tmp.dump()

    def pickleLoad(self, fileName=None):
        if fileName is None:
            return None
        else:
            #data = json.load(open(pth))
            with open(fileName) as infile:
                data = json.load(infile)
            # tmp = file_archive(pth)
            # tmp.load()
            data = self.json_unzip(data)
            return data

    def json_zip(self, j):
        j = {
            ZIPJSON_KEY: base64.b64encode(
                zlib.compress(
                    json.dumps(j).encode('utf-8')
                )
            ).decode('ascii')
        }

        return j

    def json_unzip(self, j, insist=True):
        try:
            assert (j[ZIPJSON_KEY])
            assert (set(j.keys()) == {ZIPJSON_KEY})
        except:
            if insist:
                raise RuntimeError("JSON not in the expected format {" + str(ZIPJSON_KEY) + ": zipstring}")
            else:
                return j

        try:
            j = zlib.decompress(base64.b64decode(j[ZIPJSON_KEY]))
        except:
            raise RuntimeError("Could not decode/unzip the contents")

        try:
            j = json.loads(j)
        except:
            raise RuntimeError("Could interpret the unzipped contents")

        return j

    def keepAlive(self, interval=7000):
        while True:
            print ('Working')
            self.reloadAPI()
            time.sleep(interval)

    def loadFiles(self, block=True):
        pth = "data/%s.pickle" %(block)
        if block is False:
            for each in self.files:
                pth = "data/%s.pickle" %(each)
                if os.path.exists(pth):

                    self.repo[each] = self.pickleLoad(pth)
                    #self.repo[each] = pickle.load(open(pth, 'rb'))
                else:
                    self.repo[each] = None
        elif os.path.exists(pth):
            print (block, ' Found')
            return self.pickleLoad(pth)
            #self.repo[each] = pickle.load(open(pth, 'rb'))
        else:
            print (block, ' not found')

    def reloadAPI(self):
        self.summary()
        self.sensors()
        self.latestCountyReadings()
        self.latestSiteReadings()

    def summary(self):
        url = self.url
        re = requests.get(url[3])
        summary = re.json()['data']
        #pickle.dump(summary, open('data/summary.pickle', 'wb'))
        self.pickleDump(summary, 'data/summary.pickle')

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

        #pickle.dump(data, open('data/data.pickle', 'wb'))
        self.pickleDump(data, 'data/data.pickle')
        #pickle.dump(countyDataDic, open('data/countyDataDic.pickle', 'wb'))
        self.pickleDump(countyDataDic, 'data/countyDataDic.pickle')

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


        #pickle.dump(siteReadings, open('data/siteReadings.pickle', 'wb'))
        self.pickleDump(siteReadings, 'data/siteReadings.pickle')
        #self.repo['siteReadings'] = siteReadings
        self.loadFiles()

    def latestSiteReadings(self):
        url = self.url
        countyDataDic = self.loadFiles(block='countyDataDic')

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

        #pickle.dump(siteDailyReads, open('data/siteDailyReads.pickle', 'wb'))
        self.pickleDump(siteDailyReads, 'data/siteDailyReads.pickle')
        #pickle.dump(siteMonthly, open('data/siteMonthly.pickle', 'wb'))
        self.pickleDump(siteMonthly, 'data/siteMonthly.pickle')

        self.loadFiles()

    def test(self):
        for key, value in self.repo.items():
            if value is None:
                print (key, '=> is Not Initialized')

    def getCounties(self):
        data = self.loadFiles(block='data')
        counties = []

        try:
            for each in data:
                county = each['county']
                mwaterId = each['mwater_id']

                if county not in counties:
                    counties.append(county)
        except:
            return counties

        return counties

    def getSiteReadsByCounty(self, county = None):
        siteDailyReads = self.loadFiles(block='siteDailyReads')
        if county is None or county not in self.getCounties():
            # print (self.repo['siteDailyReads'].keys())
            try:
                return siteDailyReads[list(siteDailyReads.keys())[0]]
            except:
                return []
        else:
            lim = 300
            title = "{} Water Points".format(county)
            mod = {"title": title, "sites":{}, "siteNames":[], "status":{}, "st":{}}
            xL = 0


            for siteId, lst in siteDailyReads.items():
                for each in lst:
                    cnty = each['county']
                    houses = each['households']
                    date = each['localDate']
                    yieldDaily = each['yieldDaily']
                    siteName = each['siteName']
                    status = each['expertStatus']

                    if cnty == county:
                        if siteName not in mod['siteNames']:
                            mod['siteNames'].append(siteName)

                        if yieldDaily > xL:
                            xL = yieldDaily

                        tmp = {}
                        tmp['status'] = status
                        tmp['households'] = houses
                        tmp['name'] = siteName.split(' - ')[1]
                        tmp['date'] = date
                        tmp['latestYieldDaily'] = yieldDaily

                        if siteName not in mod['sites'].keys():
                            tmp['data'] = []
                            mod['sites'][siteName] = tmp
                            mod['sites'][siteName]['data'].append(yieldDaily)

                            if tmp['status'] not in mod['status'].keys():
                            	mod['status'][tmp['status']] = 1
                            else:
                                mod['status'][tmp['status']] += 1

                            mod['st']['status'] = list(mod['status'].keys())
                            mod['st']['data'] = list(mod['status'].values())

                        elif len(mod['sites'][siteName]['data']) < lim:
                            mod['sites'][siteName]['data'].append(yieldDaily)

            mod['maxYield'] = xL
            return mod

    def getSummary(self):
        return self.loadFiles(block='summary')
