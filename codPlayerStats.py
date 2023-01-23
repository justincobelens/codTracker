import json
import os

username = 'xxxx'
directory = os.path.join(os.path.dirname(__file__), 'Players', username, 'matchesInfo')


def loopDirectory(input):
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file = str(os.path.join(directory, filename))
            x = file.split("/")[-1].split(".")[0].split("-")

            if str(input) == x[0] or str(input) == x[1]:
                return x[0], x[1]
            continue
        else:
            continue


def publicMatchInfo(input):
    matchId, timestamp = loopDirectory(input)

    filename = os.path.join(directory, matchId + '-' + timestamp) + '.json'

    try:
        with open(filename, 'r') as f:
            # new data
            new_data = json.load(f)
            allPlayers = new_data['data']['allPlayers']
            return allPlayers
    except:
        print("File doesn't exist")

# matchId = 123456789
# items = publicMatchInfo(matchId)
#
# for item in items:
#     player = item['player']
#     playerStats = item['playerStats']
#
#     if player['username'] == 'xxxxx':
#         print(playerStats['kills'])
