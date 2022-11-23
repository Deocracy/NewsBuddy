# multiView.py

# Frameworks for running multiple Streamlit versions of NewsBuddyAI as a single app
# 10/01/22: now in C:\Projects\DataViz\Deocracy\NewsBot\guiNBAI\strPy
# with a copy of dbMgr.py from NewsBot
# with a copy of newsBot.py from nbApps 
#    renamed: nbai.py

#!/usr/bin/env python
# coding: utf-8

#-------------------------------------------------------------------------------------------
import streamlit as st
import nbai
import dbMgr as dbm                   # for database storage
import misc
import grabber

errLogFile = "Errors.txt"
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def doSpeech( speech ):
    if ( speech == "Yes" ):
        st.sidebar.write( "You can talk with your NewBuddyAI now, and it will talk with you!" )
        isSpeech = True
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def getGlangs( gLangFile ):

    theLangs = []
    theCodes = []
    with open( gLangFile, "r" ) as theF:

        theList = theF.read().split("\n")
        theLangs.append( "english" )
        theCodes.append( "en" )
        for itm in theList:
            cln = itm.find( ": " )
            theLangs.append( itm[cln+2:] )
            theCodes.append( itm[:cln] )

    return theLangs, theCodes
#-------------------------------------------------------------------------------------------


#----------------------------------------------------------------------
def getLang( whatLangStr, languages ):
    #misc.log( languages, "languages2.txt" )
    lang = st.sidebar.selectbox( whatLangStr, languages )
    return lang
#----------------------------------------------------------------------


#----------------------------------------------------------------------
def getNewsSrcs( srcsLbl, srcs ):

    # TO DO: implement multiselect() in nbai.py
    #newSrcS = st.sidebar.multiselect( srcsLbl, srcs )
    newSrcS = st.sidebar.selectbox( srcsLbl, srcs )
    return newSrcS
#----------------------------------------------------------------------


#----------------------------------------------------------------------
def setAlarms( lang ):

    alrmLbl  = "Select an alarm type"
    alrmOpts = ["Topic", "Date(s)", "Region(s)"]
    alarmS = st.sidebar.selectbox( alrmLbl, alrmOpts )
    return alarmS
#----------------------------------------------------------------------


#----------------------------------------------------------------------
def getAlarmTypes( theLabel ):

    alarmSet  = st.sidebar.radio( theLabel, ("No", "Yes"), horizontal=True )
    return alarmSet
#----------------------------------------------------------------------


#----------------------------------------------------------------------
def getSpeech( theLabel ):

    speech  = st.sidebar.radio( theLabel, ("No", "Yes"), horizontal=True )
    return speech
#----------------------------------------------------------------------


#----------------------------------------------------------------------
def getToTrack( theLabel, lang, srcs ):

    toTrack  = st.sidebar.multiselect( theLabel, srcs )

    #if ( len(toTrack) > 0 ):
        #topics = misc.getTopics( lang )

    return toTrack
#----------------------------------------------------------------------


#----------------------------------------------------------------------
def doGrab( theLabel ):

    ok2grab = st.sidebar.radio( theLabel, ("No", "Yes"), horizontal=True )
    return ok2grab
#----------------------------------------------------------------------


#----------------------------------------------------------------------
class MultiView:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append( {"title": title, "function": func} )

    def run(self):

        titles       = [a["title"] for a in self.apps]
        functions    = [a["function"] for a in self.apps]
        whatPart     = "What part of the news do you want to see?"
        whatPartLst  = ["All", "Summary", "Key Points", "Key Words", "Critique"]
        parts        = []
        filters      = {}
        location     = []
        dates        = []
        topics       = []
        toTrack      = []
        srcs         = []
        languages    = []                              # ["English", "Spanish", "French", "German"]
        vocab        = ""
        otherF       = "Other News Filters"
        byLoc        = "Filter by Location"
        bySrc        = "Choose your news source"
        byDates      = "Filter by Date(s)"
        otherFilters = [ byLoc, byDates ]
        locsLbl      = "Where do you want your news from?"
        locs         = ["United States", "Mexico", "Canada"]
        newLoc       = ""
        newSrcS      = ""
        startDate    = ""
        endDate      = ""
        urlFile      = "allNCGoodUrls.txt"
        isSpeech     = False       # default: no talking with NBAI
        uSure        = False

        gLangFile    = "googletransLanguages.txt"
        languages, codes = getGlangs( gLangFile )

        st.sidebar.header( "Configuration Options" )

        whatLangStr  = "What language do you want your news in?"
        lang         = getLang( whatLangStr, languages )    # if needed: langCode = getCode( lang )   # pulls from languages[] & codes[]

        srcs         = misc.getSrcs( lang )
        #print( "srcs after misc.getSrcs() == ", srcs)
        if ( len(srcs) == 0 ):
            st.write( "No 'srcs' returned from misc.getSrcs()" )

        srcsLbl      = "Which news source(s) do you want?"
        newSrcS      = getNewsSrcs( srcsLbl, srcs )         # Which news source do you want?
        #print( "newSrcS after getNewsSrcs() == ", newSrcS)

        topics       = misc.getTopics( lang )

        trackLbl     = "What topics do you want to keep track of?"
        toTrack      = getToTrack( trackLbl, lang, topics ) # Which Topics to track

        # Set alarms 
        # By: Topic, News Source(s), ...
        alarmSetLbl  = "Do you want to set any alarms?"
        alarmSet     = getAlarmTypes( alarmSetLbl )
        if ( alarmSet == "Yes" ):
            alarmS   = setAlarms( lang )

        # Speech on/off
        spchLbl = "Do you want to talk with your NewsBuddyAI?"
        speech = getSpeech( spchLbl )
        doSpeech( speech )

        grabLbl = "Do you want to grab headlines?"
        ok2grab = doGrab( grabLbl )
        #st.write( "ok2grab == ", ok2grab )
        if ( ok2grab.upper() == "YES" ):
            uSureLbl = "Are you sure? This takes up to 4 hours to run"
            uSure = st.sidebar.radio( uSureLbl, ("No", "Yes"), horizontal=True )
            #st.write( "uSure == ", uSure )

        #st.write( "ok2grab & uSure == ", ok2grab, uSure )
        if ( (ok2grab.upper() == "YES") and ( uSure.upper() == "YES") ):
            grabber.grabMain()
        else:
            nbai.app( lang, srcs, topics )
#----------------------------------------------------------------------
