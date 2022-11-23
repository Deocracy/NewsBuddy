# wvw.py

"""
does all of the World View Window features
"""

#!/usr/bin/env python
# coding: utf-8

#-------------------------------------------------------------------------------------------
# imports
import streamlit as st
import dbMgr as dbm                   # for database access & storage
import misc
import sqlite3
import sys

nu2Lines = "\n\n"
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
class theWVW:

    def __init__( self, lang, newSrcS, topics ):
        self.topics = []
        self.doWVW( lang, newSrcS, topics )

    def doWVW( self, lang, newSrcS, topics ):

        userWinLbl = "Your News Feed in " + lang
        wvwLbl     = "World View Window"
        origTopic  = ""
        tranTopic  = ""
        for ele in topics:
            origTopic = origTopic + ele + nu2Lines

        topicTrans = topics                  #topicTrans = misc.doTrans( topics, lang )
        #print( nu2Lines, "topicTrans after doTrans() in theWVW ", topicTrans )
        for ele in topicTrans:
            tranTopic = tranTopic + ele + nu2Lines

        misc.doShow( userWinLbl + nu2Lines + tranTopic, wvwLbl + nu2Lines + origTopic )   # " ".join(topics) )
#-------------------------------------------------------------------------------------------




