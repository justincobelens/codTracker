import json
import os
import requests


####################################
##
# Call of Duty API
# -- Go to "SETUP" to fill in missing data (username, gamecode, gamemode)
#
# Calls
# -- Save Matches Detailed information
#
######################################

class matchStats:
    def __init__(self):

        # SETUP: You have to enter values for these.
        self.username = 'xxxxx'
        self.gamecode = 'psn'
        self.gamemode = 'wz'

        self.dir = os.path.join(os.path.dirname(__file__), 'Players', self.username)

        self.directoryMatchList = os.path.join(self.dir, 'matchesList')
        self.directoryMatchInfo = os.path.join(self.dir, 'mmatchesInfo')

        self.data_total = {"data": []}

    # Returns dictionary with all match info.
    # Duplicates are removed
    # Order last played match first
    def MergeFiles(self):
        # Creates 1 variable with all match info
        for filename in os.listdir(self.directoryMatchList):
            if filename.endswith(".json"):
                # print(os.path.join(directory, filename))

                filename = os.path.join(self.directoryMatchList, filename)
                with open(filename) as json_file_read:
                    data = json.load(json_file_read)
                    temp = data['data']

                    self.data_total['data'].extend(temp)
                continue
            else:
                continue

        # Removes duplicates
        seen = set()
        new_l = []
        l = self.data_total['data']
        for d in l:
            t = tuple(d.items())
            if t not in seen:
                seen.add(t)
                new_l.append(d)

        # reverse for order
        new_l.sort(key=lambda k: k['timestamp'], reverse=True)

        return new_l

    # Returns list of matchIds and timestamps
    def Update_MatchIds_Timestamps(self, files, amount):
        items = files[0:amount]
        match_lst = []
        timestamp_lst = []
        for item in items:
            match_lst.append(item['matchId'])
            timestamp_lst.append(item['timestamp'])

        return match_lst, timestamp_lst

    # Creates file with match Info
    def CreateMatchInfo(self, matchId, timestamp):
        url = 'https://www.callofduty.com/api/papi-client/crm/cod/v2/title/mw/platform/battle/fullMatch/wz/' + \
              matchId + \
              '/it'

        # Create directory if needed
        if not os.path.exists(self.directoryMatchInfo):
            os.makedirs(self.directoryMatchInfo)
            print("Directory ", self.directoryMatchInfo, " Created ")

        # Defines filename
        filename = self.directoryMatchInfo + "/" + timestamp + '-' + matchId + ".json"

        # Check if match already exists
        if not os.path.exists(filename):
            # Requests player info from COD
            payload = {}
            headers = {
                "content-type": "application/json",
                'User-Agent': 'Mozilla/5.0'
            }
            response = requests.request("GET", url, headers=headers, data=payload)
            response.encoding = 'utf-8'
            responsetext = response.text

            # Creates file with player matchInfo
            with open(filename, "w", encoding="utf-8") as f:
                f.write(responsetext)

            print("File created", matchId)

    # SEARCH -- Returns matching timestamp by MatchId
    def FindTimestamp_byMatchId(self, files, matchId):
        for item in files:
            if item["matchId"] == matchId:
                return item['timestamp']

    # SEARCH -- Returns matching matchId by Timestamp
    def FindMatchId_byTimestamp(self, files, timestamp):
        for item in files:
            if item["timestamp"] == timestamp:
                return item['matchId']


def main():
    b = matchStats()
    mergedFiles = b.MergeFiles()

    # Fill in how many matches you want info of
    AddLastMatches = 201
    matchId, timestamps = b.Update_MatchIds_Timestamps(mergedFiles, AddLastMatches)

    for i in range(0, len(matchId)):
        b.CreateMatchInfo(str(matchId[i]), str(timestamps[i]))



if __name__ == '__main__':
    main()
