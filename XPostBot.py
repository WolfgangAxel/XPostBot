#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  XPosterBot.py
#  
#  Copyright 2017 Keaton Brown <linux.keaton@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

def loadCreds(myPath):
    """
    loads the config file, if anything is empty, cause panic
    """
    config = configparser.RawConfigParser()
    config.optionxform = lambda option: option
    config.read(myPath+"credentials.ini")
    if not config.sections():
        raise Exception
    for item in config.sections():
        if not [thing[1] for thing in config[item].items()]:
            raise Exception
    return config

def makeCreds(myPath):
    print("Either this is the first time this script is being run, or there "
          "was an error reading the config file. You will now be walked "
          "through obtaining all the credentials this bot needs in order "
          "to function.")
    config = configparser.ConfigParser()
    config.optionxform = lambda option: option
    input("Press enter to continue... ")
    ############################################################# Reddit
    print(" 1) Go to https://www.reddit.com/prefs/apps and sign in with your "
          "bot account. The bot must have moderator privileges.\n"
          " 2) Press the 'create app' button, then enter the following :\n\n"
          "    Name: XPosterBot (or another name if you so wish)\n"
          "    App type: script\n"
          "    description: (leave this blank or enter whatever you wish)\n"
          "    about url: https://github.com/WolfgangAxel/XPosterBot\n"
          "    redirect url: http://127.0.0.1:65010/authorize_callback\n\n"
          " 3) Finally, press the 'create app' button.")
    input("Press enter to continue... ")
    print("Underneath the name of the app, there should be a string of letters and numbers.\n"
          "That is the bot's client-id.\n"
          "The bot's secret is displayed in the table.")
    redCreds = {}
    for short,thing in [["u","username"],["p","password"],["c","client-id"],["s","secret"]]:
        while True:
            value = input("Please enter the bot's "+thing+":\n==> ")
            confirm = input("Is '"+value+"' correct? (y/n)\n==> ")
            if confirm.lower() == "y":
                redCreds[short] = value
                break
            print("Confirmation failed. Restarting entry")
    print("Almost done! Just a few more items to define.")
    input("Press enter to continue... ")
    ############################################################### Misc
    mscCreds = {}
    for variable,question in [ ["mySub","Enter the name of your subreddit."],
                               ["watchedSub","Enter the name of the subreddit you wish to watch."],
                               ["botMaster","Enter your personal Reddit username. (This is used for Reddit's user-agent, nothing more)"]
                             ]:
        while True:
            value = input(question+"\n==>")
            confirm = input("Is '"+value+"' correct? (y/n)\n==> ")
            if confirm.lower() == "y":
                mscCreds[variable] = value
                break
            print("Confirmation failed. Restarting entry.")
    
    config["R"] = redCreds
    config["M"] = mscCreds
    with open(myPath+"credentials.ini","w") as cfg:
        config.write(cfg)
    print("Config file written successfully")
    return config

########################################################################
#                                                                      #
#    Script Startup                                                    #
#                                                                      #
########################################################################

myPath = __file__.replace("XPosterBot.py","")

try:
    mod = "praw"
    import praw
    mod = "configparser"
    import configparser
    mod = "time"
    import time
except:
    exit(mod+" was not found. Install "+mod+" with pip to continue.")

try:
    creds = loadCreds(myPath)
except:
    creds = makeCreds(myPath)

for variable in creds["M"]:
    exec(variable+' = creds["M"]["'+variable+'"]')
sleepTime = 60*60*24 # one day

## Reddit authentication
R = praw.Reddit(client_id = creds["R"]["c"],
                client_secret = creds["R"]["s"],
                password = creds["R"]["p"],
                user_agent = "XPosterBot, a bot for /r/"+mySub.replace("/r/","").replace("r/","")+"; hosted by /u/"+botMaster.replace("/u/","").replace("u/",""),
                username = creds["R"]["u"].replace("/u/","").replace("u/",""))

########################################################################
#                                                                      #
#    Script Actions                                                    #
#                                                                      #
########################################################################
print("Bot started successfully. Entering main loop...")
offset = 0
while True:
    try:
        startTime = time.time()
        top = R.subreddit(watchedSub.replace("/r/","").replace("r/","")).top('day').__next__()
        if top.is_self:
            post = R.subreddit(mySub.replace("/r/","").replace("r/","")).submit(top.title,selftext=top.selftext)
        else:
            post = R.subreddit(mySub.replace("/r/","").replace("r/","")).submit(top.title,url=top.url)
        print('"'+top.title+'" successfully cross-posted')
        comment = post.reply(
            "User: `/u/"+top.author.name+"`\n\n"+
            "Original date: "+time.strftime("%d %h, %Y, %H:%M %p GMT",time.gmtime(top.created_utc))+"\n\n"+
            "[Link to original submission]("+top.shortlink+")"+
            "\n\n****\n\n[^(I am a bot)](https://github.com/WolfgangAxel/XPostBot)")
        _=comment.mod.distinguish(sticky=True)
        print("Comment made. Sleeping...")
        time.sleep(sleepTime-(time.time()-startTime)-offset) # makes it exactly 24 hours
        offset = 0
    except Exception as e:
        print(time.strftime('%D %T')+" - Error during main loop. Details:\n"+str(e.args)+"\nTrying again in one minute.")
        offset += 60
        time.sleep(60)
