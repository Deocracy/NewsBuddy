# nbScraper.py

"""
testing: can I grab the full article from each headline in the NBAI.db table: _____
"""


#!/usr/bin/env python
# coding: utf-8

#-------------------------------------------------------------------------------------------
import os, sys
from urllib.request import Request, urlopen
import dbMgr as dbm
import time
import urllib.request
from urllib.error import URLError

errLogFile = "Errors.txt"
beep       = chr(7)
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def alrt():
    print( beep )
    print( beep )
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def log( txt, outPutFileName=None ):

    # 02/03/20
    if ( outPutFileName == None ):
        outPutFileName = "logFile.txt"
    
    with open( outPutFileName, "a" ) as lF:
        
        if ( "list" in str( type( txt ) ) ):
           rng  = range(0,len( txt ))
           for i in rng:
               toWrite = str( txt[i] )
               #lF.write( toWrite.encode('ascii', 'ignore').decode('utf-8') )
               lF.write( toWrite )
               lF.write( "\n" )

        elif ( "dict" in str( type( txt ) ) ):
           for key in txt:
               lF.write( key + ": " + str( txt[key] ) )
               lF.write( "\n" )

        elif ( "str" in str( type( txt ) ) ):
            #txt = txt.decode('utf-8').encode('ascii', 'ignore').decode('utf-8')
            lF.write( txt )
            lF.write( "\n" )

        elif ( "bool" in str( type( txt ) ) ):
            if ( txt ):
                lF.write( "True" )
            else:
                lF.write( "False" )

        elif ( "int" in str( type( txt ) ) ) or ( "float" in str( type( txt ) ) ):
            lF.write( str( txt ) )
            lF.write( "\n" )

    lF.close
    return                        # log()
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
    except Error as err:
        misc.alrt()
        misc.log( "Error getting all data from NBAI.db: " + str(err), errLogFile )

    for ele in theList:

        arts.append( ele[0] )

    return arts
#-------------------------------------------------------------------------------------------


#---------------------------------------------------------------------------
def updateDB2( data, connection, cursor, theTable, artLink ):

    """
    inserts data to a specific field with a specific url to a specific table in the database
    11/30/22: currently only used for inserting articles into the news table
    """

    sqlStmt = "UPDATE " + theTable + " SET articles = BLOB( '" + data + "' ) WHERE url = " + '"' + artLink + '"'
    #sqlStmt = "UPDATE " + theTable + " SET articles = '" + data + "' WHERE url = " + '"' + artLink + '"'

    try:
        result = cursor.execute( sqlStmt )

    except OperationalError as err:               # sqlite.
        alrt()
        print( "sqlStmt == ", sqlStmt )
        print( "artLink == ", artLink )
        print( "err == ", err )
        log( "OperationalError - Failed to save the data for: " + artLink + ": " + str(err), errLogFile )

    except SQLITE_ERROR as err:
        alrt()
        log( "SQLITE_ERROR - Failed to save the data for: " + baseUrl + ": " + str(err), errLogFile )


    try:
        connection.commit()

    except Error as err:
        alrt()
        log( "Failed to commit() this connection in updateDB(): " + str(err), errLogFile )
#---------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
class grabMain():

    start    = time.time()
    theDB    = "NBAI.db"
    urls     = []
    titles   = []
    cntr     = 0
    theTable = "news"


    # create a connection object with the database
    conn, curs = dbm.connToDB( theDB )
    if ( conn == None ):
        alrt()
        quit

    # load all news article link urls to arts[]
    arts = gitArts( conn, curs )           # urls, 
    if ( arts == None ):
        alrt()
        quit

    for ele in arts:

        try:
            requestObj  = Request( ele, headers={'User-agent': 'Mozilla/5.0'} )
            responseObj = urlopen( requestObj )
            theHtml     = str( responseObj.read(), "utf-8" )
            #theHtml     = responseObj.read()
            #theHtml     = theHtml.decode( "utf-8" )
        except URLError as err:
            print( "Unable to download page: " + str(err.reason) )

        updateDB2( theHtml, conn, curs, theTable, ele )

    try:
        conn.commit()
    except Error as err:
        alrt()
        log( "Failed to commit() this connection in startDB(): " + str(err), errLogFile )
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
if __name__ == '__main__':

    grabMain()
#-------------------------------------------------------------------------------------------
