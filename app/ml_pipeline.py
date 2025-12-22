# stats I want to use with model (start with forward)
# xg              based of goals
    #(total_goals / total_minutes) * 90
    #total assists   ^
    #total ppg
    #total minutes
    #total bps
    #total xg     ^
    #total xa    ^
    #for each last 5 results:
        #team_strenght
        #result.goals 
        #result.assists 
        #result.bp 
        #result.bps 
        #result.opponent_strenght

# xa               based off assists
    #(total_goals / total_minutes) * 90
    #total assists  ^

    #total ppg
    #total minutes
    #total bps
    #total xg    ^
    #total xa    ^
    #for each last 5 results:
        #team_strenght
        #result.goals 
        #result.assists 
        #result.bp 
        #result.bps 
        #result.opponent_strenght

# xpenalites missed           based of penalties missed
    #total penalties missed
    #minutes
    #for each last 5 results:
        #team_strenght
        #result.penalties missed
        #result.bps 
        #result.opponent_strenght

# xyellowcard         based of yellow card
    #total red cards
    #total yellow cards
    #minutes
    #for each last 5 results:
        #result.yell
        #result.red
        #result.bps 
        #result.opponent_strenght
        #team_strenght

# xredcard     based of red card
    #total red cards
    #total yellow cards
    #minutes
    #for each last 5 results:
        #result.yell
        #result.red
        #result.bps 
        #result.opponent
        #team_strenght

# xbp   - based of bp
    #total goals
    #total assists
    #team
    #total ppg
    #total minutes
    #total bps
    #total xg
    #total xa
    #for each last 5 results:
        #result.goals 
        #result.assists 
        #result.bp 
        #result.bps 
        #result.opponent
        #result.yell
        #result.red
        #result.penalties missed


#take into account player availablity at end and add flag to player  (dont change xp)
#remember to add penalties saved for gk,              dc, cs, etc


import pandas as pd

    




    