# nbai.py - 10/01/22: renamed, was nApps\newsBot.py

#!/usr/bin/env python
# coding: utf-8

# imports
import streamlit as st
import dbMgr as dbm                   # for database access & storage
import misc
import wvw
import sqlite3
import sys
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def app( lang, newSrcS, topics=None ):

    # 10/01/22: this is where I put the WVW in the right column via misc.doShow()

    if ( topics == None ) or ( topics == "" ):
    
        topics   = misc.getTopics( lang )

    wvw.theWVW( lang, newSrcS, topics )

    return
#-------------------------------------------------------------------------------------------


#----------------------------------------------------------------------
if __name__ == '__main__':

    app( "en", "abc11.com" )
#----------------------------------------------------------------------
