# artsGrabber.py

"""
testing: can I grab the full article from each headline in the NBAI.db table news
"""


#!/usr/bin/env python
# coding: utf-8

#-------------------------------------------------------------------------------------------
from urllib.request import Request, urlopen
from urllib.error import URLError
import dbMgr as dbm
import misc
import time
import sqlite3
from urllib.parse import urlsplit, urlunsplit, quote
import socket
import time

errLogFile = "artsGrabberErrors.txt"
beep       = chr(7)
lines2     = "\n\n"
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def gitArts( conn, curs ):

    """
    load all news source urls to urls[]
    change to: use the srcs table from the db
    """

    arts    = []
    #artLink = []
    theList = []

    sqlStmt = "SELECT artLink FROM news"
    try:
        theList = curs.execute( sqlStmt ).fetchall()
    except sqlite3.SQLITE_ERROR as err:
        misc.alrt()
        misc.log( "SQLITE_ERROR getting all data from NBAI.db: " + str(err), errLogFile )
    except sqlite3.OperationalError as err:
        misc.alrt()
        misc.log( "OperationalError - getting all data from NBAI.db: " + str(err), errLogFile )
    #except EXCEPTION as err:
        #misc.alrt()
        #misc.log( "OperationalError - getting all data from NBAI.db: " + str(err), errLogFile )

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

    data2 = data                 # base64.b64encode( data )

    sqlStmt = "UPDATE " + theTbl + " SET articles=? WHERE artLink = ?"

    try:
        #result = cursor.execute( sqlStmt, ( sqlite3.Binary(data2) ) )   # if artLink is a BLOB field
        result = cursor.execute( sqlStmt, (data2, artLink) )

        # TypeError: memoryview: a bytes-like object is required, not 'tuple'
        # result = cursor.execute( sqlStmt, ( sqlite3.Binary(data2), artLink) )

    except sqlite3.OperationalError as err:
        misc.alrt()
        print( "OperationalError - Failed to save the data for artLink: " + artLink + "\n" + " - error ==  " + str(err) + "\n" + " With sqlStmt == " + sqlStmt )
        misc.log( "OperationalError - Failed to save the data for artLink: " + artLink + "\n" + " - error ==  " + str(err) + "\n" + " With sqlStmt == " + sqlStmt, errLogFile ) 

    except TypeError as err:
        misc.alrt()
        print( "TypeError - Failed to save the data for artLink: " + artLink + "\n" + " - error ==  " + str(err) + "\n" + " With sqlStmt == " + sqlStmt )
        misc.log( "TypeError - Failed to save the data for artLink: " + artLink + "\n" + " - error ==  " + str(err) + "\n" + " With sqlStmt == " + sqlStmt, errLogFile ) 

    #except sqlite3.SQLITE_ERROR as err:
        #misc.alrt()
        #print( "SQLITE_ERROR - Failed to save the data for artLink: " + artLink + "\n" + " - error ==  " + str(err) + "\n" + " With sqlStmt == " + sqlStmt )
        #misc.log( "SQLITE_ERROR - Failed to save the data for artLink: " + artLink + "\n" + " - error ==  " + str(err) + "\n" + " With sqlStmt == " + sqlStmt, errLogFile ) 

    #except EXCEPTION as err:
        #misc.alrt()
        #print( "EXCEPTION - Failed to save the data for artLink: " + artLink + "\n" + " - error ==  " + str(err) + "\n" + " With sqlStmt == " + sqlStmt )
        #misc.log( "EXCEPTION - Failed to save the data for artLink: " + artLink + "\n" + " - error ==  " + str(err) + "\n" + " With sqlStmt == " + sqlStmt, errLogFile ) 

    try:
        connection.commit()

    except sqlite3.DatabaseError as err:
        misc.alrt()
        print( "DatabaseError - Failed to commit() this connection in updateDB(): " + str(err) )
        misc.log( "DatabaseError - Failed to commit() this connection in updateDB(): " + str(err), errLogFile )
    except sqlite3.DataError as err:
        misc.alrt()
        print( "DataError - Failed to commit() this connection in updateDB(): " + str(err) )
        misc.log( "DataError - Failed to commit() this connection in updateDB(): " + str(err), errLogFile )
#---------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def iri2uri( iri ):

    """
    Convert an IRI to a URI (Python 3).
    """

    uri = ''
    if isinstance( iri, str ):

        (scheme, netloc, path, query, fragment) = urlsplit(iri)
        scheme = quote(scheme)
        netloc = netloc.encode('idna').decode('utf-8')
        path = quote(path)
        query = quote(query)
        fragment = quote(fragment)
        uri = urlunsplit((scheme, netloc, path, query, fragment))

    else:
        uri = iri

    return uri
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
class grabMain():

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

        print( ele )

        if ( "news.163.com" in ele ) or ( "administradores.com.br" in ele ):
            continue

        try:

            encEle      = ele.encode( "utf-8" )
            encEle      = iri2uri( ele )
            requestObj  = Request( encEle, headers={'User-agent': 'Mozilla/5.0'} )
            responseObj = urlopen( requestObj, timeout=10 )
            theHtml     = responseObj.read()           #, "utf-8" ==> this format made theHtml a tuple  -  .encode( "utf-8" )

            #responseObj = urllib.request.urlopen( format(quote(ele) ) )
            #theHtml    = responseObj.read(), encoding="utf-8"
            #theHtml    = responseObj.read( encoding="utf-8" )
            #theHtml     = theHtml.decode( "utf-8" )
            #theHtml     = theHtml.encode( "utf-8" )

        except ConnectionResetError as err:
                misc.alrt()
                misc.log( "ConnectionResetError: Unable to download page: " + ele + " - Because: " + str(err) + lines2, errLogFile )
                continue

        except socket.timeout as err:
                misc.alrt()
                misc.log( "Timeout Error: Unable to download page: " + ele + " - Because: " + str(err) + lines2, errLogFile )
                continue

        except URLError as err:
            #if isinstance( err.reason, timeout ):
            #if ( "TIMEOUT" in err.reason.upper() ):          # socket.timeout
            if isinstance( err.reason, socket.timeout ):
                misc.alrt()
                misc.log( "Timeout Error: Unable to download page: " + ele + " - Because: " + str(err) + lines2, errLogFile )
                continue
            else:
                misc.alrt()
                misc.log( "URLError: Unable to download page: " + ele + " - Because: " + str(err) + lines2, errLogFile )
                continue

        except ValueError as err:
            #if isinstance( err.reason, http.client.IncompleteRead ):
            if ( "incompleteread" in str(err).lower() ):
                misc.log( "http.client.IncompleteRead - Unable to download page: " + ele + " - Because: " + str(err) + lines2, errLogFile )
                continue
            elif ( "unknown url type" in str(err).lower() ):
                misc.log( "ValueError - Unable to download page: " + ele + " - Because: " + str(err) + lines2, errLogFile )
                continue
            else:
                misc.log( "ValueError - Unable to download page: " + ele + " - Because: " + str(err) + lines2, errLogFile )
                continue

        except AttributeError as err:
            misc.log( "AttributeError - Unable to download page: " + ele + " - Because: " + str(err) + lines2, errLogFile )
            continue

        updateDB2( theHtml, conn, curs, theTbl, encEle )

    try:
        conn.commit()
        conn.close
    except sqlite3.DatabaseError as err:
        misc.alrt()
        print( "DataError - Failed to commit() this connection in startDB(): " + str(err) )
        misc.log( "Failed to commit() this connection in startDB(): " + str(err), errLogFile )
        pass
    except sqlite3.DataError as err:
        misc.alrt()
        print( "DataError - Failed to commit() this connection in startDB(): " + str(err) )
        misc.log( "Failed to commit() this connection in startDB(): " + str(err), errLogFile )
        pass
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
if __name__ == '__main__':

    start    = time.time()
    grabMain()
    dt = time.time() - start
    timeTaken = dt / 3600
    print( "Time elapsed = " + str(timeTaken) + " hours" )
#-------------------------------------------------------------------------------------------
