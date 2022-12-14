# nbScraper.py

"""
testing: can I grab the full article from each headline in the NBAI.db table: _____
"""


#!/usr/bin/env python
# coding: utf-8

#-------------------------------------------------------------------------------------------
import os, sys
from urllib.request import Request, urlopen
from urllib.error import URLError
import dbMgr as dbm
import misc
import time
import sqlite3
import html

errLogFile = "Errors.txt"
beep       = chr(7)
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def gitArts( conn, curs ):

    """
    load all news source urls to urls[]
    change to: use the srcs table from the db
    """

    arts    = []
    artLink = []
    theList = []

    sqlStmt = "SELECT artLink FROM news"
    try:
        theList = curs.execute( sqlStmt ).fetchall()
    except sqlite3.Error as err:
        misc.alrt()
        misc.log( "Error getting all data from NBAI.db: " + str(err), errLogFile )

    for ele in theList:

        arts.append( ele[0] )

    return arts
#-------------------------------------------------------------------------------------------


#---------------------------------------------------------------------------
def updateDB2( data, connection, cursor, theTbl, artLink ):

    """
    inserts data to a specific field with a specific url to a specific table in the database
    11/30/22: currently only used for inserting articles into the news table
    """

    #sqlStmt = "UPDATE " + theTbl + " SET articles = BLOB( '" + data + "' ) WHERE url = " + '"' + artLink + '"'
    #sqlStmt = "UPDATE " + theTbl + " SET articles = '" + data + "' WHERE url = " + '"' + artLink + '"'
    #sqlStmt = """ UPDATE theTbl SET articles = VALUE (?) WHERE url = artLink """

    # ???
    # type(data) == <class 'bytes'>
    # ERROR: TypeError: a bytes-like object is required, not 'str'
    data = html.escape( data )
    sqlStmt = "UPDATE " + theTbl + """ SET articles = VALUE (?) WHERE url = """ + artLink

    try:
        result = cursor.execute( sqlStmt, data )

    except sqlite3.OperationalError as err:
        misc.alrt()
        print( "OperationalError - Failed to save the data for artLink: " + artLink + "\n" + " - error ==  " + str(err) + "\n" + " With sqlStmt == " + sqlStmt )
        misc.log( "OperationalError - Failed to save the data for artLink: " + artLink + "\n" + " - error ==  " + str(err) + "\n" + " With sqlStmt == " + sqlStmt, errLogFile ) 

    except sqlite3.SQLITE_ERROR as err:
        misc.alrt()
        print( "SQLITE_ERROR - Failed to save the data for artLink: " + artLink + "\n" + " - error ==  " + str(err) + "\n" + " With sqlStmt == " + sqlStmt )
        misc.log( "SQLITE_ERROR - Failed to save the data for artLink: " + artLink + "\n" + " - error ==  " + str(err) + "\n" + " With sqlStmt == " + sqlStmt, errLogFile ) 

    try:
        connection.commit()

    except Error as err:
        misc.alrt()
        misc.log( "Failed to commit() this connection in updateDB(): " + str(err), errLogFile )
#---------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
class grabMain():

    start    = time.time()
    theDB    = "NBAI.db"
    urls     = []
    titles   = []
    cntr     = 0
    theTbl = "news"


    # create a connection object with the database
    conn, curs = dbm.connToDB( theDB )
    if ( conn == None ):
        misc.alrt()
        quit

    # load all news article link urls to arts[]
    arts = gitArts( conn, curs )           # urls, 
    if ( arts == None ):
        misc.alrt()
        quit

    for ele in arts:

        try:
            requestObj  = Request( ele, headers={'User-agent': 'Mozilla/5.0'} )
            responseObj = urlopen( requestObj )
            #theHtml     = str( responseObj.read(), "utf-8" )
            #theHtml     = theHtml.decode( "utf-8" )
            theHtml     = responseObj.read()
        except URLError as err:
            print( "Unable to download page: " + str(err.reason) )

        updateDB2( theHtml, conn, curs, theTbl, ele )

    try:
        conn.commit()
    except Error as err:
        misc.alrt()
        misc.log( "Failed to commit() this connection in startDB(): " + str(err), errLogFile )
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
if __name__ == '__main__':

    grabMain()
#-------------------------------------------------------------------------------------------
