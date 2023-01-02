# webr.py

"""
12/29/22: webrower test of downloaded articles stored in NBAI.db
web browser to show what each downloaded article looks like
"""

#!/usr/bin/env python
# coding: utf-8

#-------------------------------------------------------------------------------------------
import dbMgr as dbm
import misc
import time
import sqlite3
import webbrowser as wb
import os
from os.path import exists
from pathlib import Path

outPath    = Path( F"C:/Projects/DataViz/Deocracy/NewsBot/dockerVer/wbrOutput" )
nuTmpFname = Path( outPath/"plsHldr.html" )
errLogFile = "webrErrors.txt"
theDB      = "NBAI.db"
beep       = chr(7)
lines2     = "\n\n"
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def gitUrlsArts( conn, curs ):

    """
    get the url & article for every record in the news table
    """

    theseUrlsArts = []
    theList       = []

    sqlStmt = "SELECT url, articles FROM news"
    try:
        theList = curs.execute( sqlStmt ).fetchall()
    except sqlite3.OperationalError as err:
        misc.alrt()
        misc.log( "OperationalError - Failed to get all data from NBAI.db: " + str(err), errLogFile )
    except sqlite3.SQLITE_ERROR as err:
        misc.alrt()
        print( "SQLITE_ERROR - Failed to get all data from NBAI.db: " + str(err), errLogFile )
        misc.log( "SQLITE_ERROR - Failed to get all data from NBAI.db: " + str(err), errLogFile )

    for ele in theList:

        theseUrlsArts.append( (ele[0], ele[1]) )     # url & article as a tuple
        #theseArts.append( ele[1] )     # articles

    #return theseUrls, theseArts                  # gitUrlsArts()
    return theseUrlsArts                         # gitUrlsArts()
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def mkOutFile( theArt, outFile ):

    """
    This outputs theArt data (theArt) to a binary file (outFile)
    """

    theRslt = True

    finResult = chkEnv()

    if ( finResult == False ):
        misc.log( "Failed to make the output folder &/or temporary html file", errLogFile )
        theRslt = False
        return theRslt
    
    if ( "str" in str( type(theArt) ) ):
        theArt = theArt.encode( "utf-8" )

    try:
        with open( outFile, "wb" ) as oF:
            oF.write( theArt )

    except OSError as err:
        theRslt = False
        misc.log( "Unable to make a article html file ", + str(err), errLogFile )

    oF.close()
    return theRslt
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def mkTmpHtml( nuTmpFname ):

    finResult = True

    txt = '<!doctype html><html lang="en-US"><head><meta charset="UTF-8">'
    txt = txt + "\n"
    txt = txt + '</html>'

    try:

        with open( nuTmpFname, "w" ) as nh:

            nh.write( txt )

    except FileExistsError as err:
        finResult = True
        return finResult

    except OSError as err:
        finResult = False
        misc.log( "Unable to make a temporary html file ", + str(err), errLogFile )
        return finResult

    return finResult
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def showArt( theArt, outFile ):

    """
    calls mkOutFile() to write theArt to an html file
    try's to open a new tab in firefox to output the html file to
    """

    theResult = True

    if ( mkOutFile(theArt, outFile) ):

        try:
            wb.get( "firefox" ).open_new_tab( str(outFile) )

        except wb.Error as err:
            misc.alrt()
            print( "Unable to show the webbrowser html file ", + str(err) )
            misc.log( "Unable to show the webbrowser html file ", + str(err), errLogFile )
            theResult = False

    else:

        misc.log( "Failed to create the output file for " + theArt )
        theResult = False

    return theResult
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def doShow( urlsArts, conn, curs ):

    """
    In order to use webbrowser (wb) with data from the db
    It must 1st be written to a file (overwritten every time)
    And the wb will read that file
    """

    outFile    = Path( outPath/"thisPage.html" )
    ffpath     = r"C:\Program Files\Mozilla Firefox\firefox.exe"

    try:
        wb.register( "firefox", None, wb.BackgroundBrowser(ffpath) )
        wb.get( "firefox" ).open( str(nuTmpFname) )

    except wb.Error as err:
        misc.alrt()
        print( "Unable to make a webbrowser connection ", + str(err) )
        misc.log( "Unable to make a webbrowser connection ", + str(err), errLogFile )
        quit

    groupUrl = urlsArts[0][0]             # pre-set group as first url in urlsArts[] - was = ""
    for ele in urlsArts:

        thisUrl = ele[0]
        theArt  = ele[1]                  # MAY BE EMPTY

        if ( theArt.strip() == "" ):
            misc.log( "No article for this url " + thisUrl, errLogFile )
            continue

        if ( thisUrl != groupUrl ):

            groupUrl = thisUrl
            txt = input( "Press any key to continue" )
            showArt( theArt, outFile )

        else:
            showArt( theArt, outFile )

        time.sleep(1)
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def browMain():

    # Assumes that the outPath variable has been populated
    # Assumes that the nuTmpFname variable has been populated & the temp (blank) html file has been created
    start    = time.time()
    urlsArts = []

    # create a connection object with the database
    conn, curs = dbm.connToDB( theDB )
    if ( conn == None ):
        misc.alrt()
        misc.log( "Unable to make a database connection", errLogFile )
        quit

    # load all news source urls to allUrls[]
    #urls, arts = gitUrlsArts( conn, curs )
    urlsArts = gitUrlsArts( conn, curs )
    if ( urlsArts == None ) or ( urlsArts == [] ):
        misc.alrt()
        quit

    doShow( urlsArts, conn, curs )

    conn.close()
    dt = time.time() - start
    timeTaken = dt / 3600
    print( "Time elapsed = " + str(timeTaken) + " hours" )
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def chkEnv():

    # Final Result of make folder & file, if necessary - assumes already created (True)
    finResult = True

    if ( not os.path.exists(outPath) ):          # create only once

        try:
            os.mkdir( outPath )
            print( "Folder '%s' created" %outPath )
        except FileExistsError:
            finResult = True
            return finResult
        except OSError:
            finResult = False
            misc.log( "Output folder failed to be created", errLogFile )
            return finResult

    if ( not exists(nuTmpFname) ):              # create only once
        finResult = mkTmpHtml( nuTmpFname )
        if finResult:
            print( "Temp html '%s' created" %nuTmpFname )

    return finResult                             # chkEnv()
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
if __name__ == '__main__':

    # program quits if this fails
    finResult = chkEnv()

    if ( finResult == False ):
        misc.log( "Failed to make the output folder &/or temporary html file", errLogFile )
        quit
    
    browMain()
#-------------------------------------------------------------------------------------------
