import requests
import json
from datetime import date
import os


####################################
#
# Call of Duty API
# -- Go to "SETUP" to fill in missing data (username, password, deviceID)
#
# Calls
# -- Save Matches General Information (matchId, timestamp, etc.)
# -- Save Profile
##
######################################

class CODAPI:
    def __init__(self):
        # You have to enter values for these three items.
        # User name and password is in plain text, that you'd use for my.callofduty.com.
        self.userName = ""
        self.password = ""

        # DeviceID is a random string (20-30 characters)
        self.deviceId = ""

        self.baseAPIURL = "https://my.callofduty.com/api/papi-client/"
        self.baseCookie = "new_SiteId=cod; " \
                          "ACT_SSO_LOCALE=en_US;" \
                          "country=US;" \
                          "XSRF-TOKEN=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        self.authObject = self.CreateAuth()
        self.theWholeCookie = self.baseCookie + ";rtkn=" + self.authObject[0] + ";ACT_SSO_COOKIE=" + self.authObject[
            1] + ";atkn=" + self.authObject[2]

    def CreateAuth(self):
        device_url = "https://profile.callofduty.com/cod/mapp/registerDevice"
        device_header = {'Content-Type': 'application/json',
                         "Cookie": self.baseCookie}
        device_payload = "{\n\t\"deviceId\": \"" + self.deviceId + "\"\n}"
        device_response = requests.request("POST", device_url, headers=device_header, data=device_payload)
        device_data = json.loads(device_response.text)
        authheader = ""

        if device_data["status"] == "success":
            authheader = device_data["data"]["authHeader"]
            auth_url = "https://profile.callofduty.com/cod/mapp/login"
            auth_header = {"x_cod_device_id": self.deviceId,
                           'Authorization': 'Bearer ' + authheader,
                           'Content-Type': 'application/json'}
            auth_payload = "{\n\t\"email\": \"" + self.userName + "\", \"password\": \"" + self.password + "\"\n}"
            auth_response = requests.request("POST", auth_url, headers=auth_header, data=auth_payload)
            auth_data = json.loads(auth_response.text)
            if auth_data["success"] == True:
                return auth_data["rtkn"], auth_data["s_ACT_SSO_COOKIE"], auth_data["atkn"]
            else:
                print("An error occurred when trying to get the authorization cookie.")

        else:
            print("An error occurred when trying to create device.")

    def SavePlayerMatches(self, gamecode, gamemode, users):
        #
        # This function saves a file for each user for the game
        #

        today = date.today()
        d1 = today.strftime("%Y%m%d")

        for user in users:
            print("\n")
            print("Running..." + user[1])

            # Create target directory & all intermediate directories if don't exists
            directory = 'Players/' + \
                        user[1] + \
                        '/matchesList/'

            if not os.path.exists(directory):
                os.makedirs(directory)
                print("Directory ", directory, " Created ")
            else:
                print("Adding to directory ", directory)

            # Find all played matches, 1000 matches per json file
            url = self.baseAPIURL + "crm/cod/v2/title/" + gamecode + \
                  "/platform/" + user[2] + "/gamer/" + \
                  user[3] + "/matches/" + gamemode + "/start/0/end/0"

            file_len = 1000
            file_counter = 0

            while file_len == 1000:
                # print(url)
                # Requests player info from COD
                payload = {}
                headers = {
                    "content-type": "application/json",
                    'Cookie': self.theWholeCookie,
                    'userAgent': 'Node/1.0.27'
                }
                response = requests.request("GET", url, headers=headers, data=payload)
                response.encoding = 'utf-8'
                responsetext = response.text

                # Creates file with player matches
                filename = directory + d1 + "-wz-matches-" + user[1].lower() + "-" + str(file_counter) + ".json"

                # Checks length of file. Because COD API gives back max 1000 matches per file
                # Creates new end_timestamp for next list of matches
                with open(filename) as json_file_read:
                    data = json.load(json_file_read)

                    file_len = len(data['data'])
                    end_timestamp = str(data["data"][-1]["timestamp"])

                # Set new timestamp on url for next batch of matches
                url = self.baseAPIURL + "crm/cod/v2/title/" + gamecode + "/platform/" + user[2] + "/gamer/" + user[
                    3] + "/matches/" + gamemode + "/start/0/end/" + end_timestamp
                file_counter += 1

    def SavePlayerProfile(self, gamecode, gamemode, users):
        #
        # Saves a json file for each user's profile.
        #
        today = date.today()
        d1 = today.strftime("%Y%m%d")

        for user in users:
            print("Running..." + user[1])

            directory = 'Players/' + \
                        user[1] + \
                        '/'

            if not os.path.exists(directory):
                os.makedirs(directory)
                print("Directory ", directory, " Created ")
            else:
                print("Adding to directory ", directory)

            url = self.baseAPIURL + "/stats/cod/v1/title/" + gamecode + \
                  "/platform/" + user[2] + "/gamer/" + \
                  user[3] + "/profile/type/" + gamemode

            payload = {}
            headers = {
                "content-type": "application/json",
                'Cookie': self.theWholeCookie,
                'userAgent': 'Node/1.0.27'
            }

            response = requests.request("GET", url, headers=headers, data=payload)
            response.encoding = 'utf-8'

            responsetext = response.text

            filename = directory + d1 + "-wz-profile-" + user[1].lower() + ".json"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(responsetext)


def main():
    # platform codes -- blizz battle.net: "battle", steam: "steam", playstation: "psn", xbox: "xbl", acti: "uno"
    # game codes -- infiniteWarfare: "iw", worldWar2: "wwii", blackops3: "bo3", blackops4: "bo4", modernwarfare: "mw"
    # game types -- zombies: "zm", multiplayer: "mp", warzone: "wz"

    gamecode = "mw"
    gamemode = "wz"

    # each user has a first name, friendly user name (without numbers), platform code, full user name tuple
    users = [
        ("first_name1", "friendly_user_name1", "psn", "full_user_name1"),
        ("first_name2", "friendly_user_name2", "psn", "full_user_name2"),
        ("first_name3", "friendly_user_name3", "psn", "full_user_name3")
    ]

    c = CODAPI()
    c.SavePlayerMatches(gamecode, gamemode, users)
    c.SavePlayerProfile(gamecode, gamemode, users)


if __name__ == '__main__':
    main()
