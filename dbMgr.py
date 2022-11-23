# dbMgr.py

import sqlite3
import csv
import string

beep = chr(7)
errLogFile = "Errors.txt"

# c.execute("INSERT INTO items (name, value) VALUES (?, ?)", ("one", 100))
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
def startDB( connection, cursor ):

    """
    1st: checks for existance of the 2 tables (news & srcs), and their indices
         if not present, creates them
    2nd: TO DO: if srcs not present, after creation, need to fill it with all the urls being used
         Source(s)/Option(s):
    """

    # create the news table if necessary
    # 10/09/22: removed title from the news table , as it is in the srcs table
    try:
        cursor.execute( "CREATE TABLE IF NOT EXISTS news (key text, url text, headlines text, artLink text, articles text, topic text)" )

    except Error as err:
        misc.alrt()
        misc.log( "Error with creating the table news: " + str(err), errLogFile )

    # create the 2 news indices if needed: headlineIdx(headlines), keyIdx(key)
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS headlineIdx ON news(headlines)")
    except Error as err:
        misc.alrt()
        misc.log( "Error with creating the headlineIdx index: " + str(err), errLogFile )

    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS keyIdx ON news(key)")
    except Error as err:
        misc.alrt()
        misc.log( "Error with creating the keyIdx index: " + str(err), errLogFile )

    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS topicIdx ON news(topic)")
    except Error as err:
        misc.alrt()
        misc.log( "Error with creating the topicIdx index: " + str(err), errLogFile )


    # test for existance of the srcs table
    findSrcs = None
    try:
        findSrcs = cursor.execute( 'SELECT name from sqlite_master where type= "table" AND name = "srcs"').fetchall()

    except Error as err:
        misc.alrt()
        misc.log( "Error with finding the table srcs: " + str(err), errLogFile )

    # create the srcs table if necessary
    # 10/09/22: if creating this table, need to fill it, as it is a source of urls & titles
    try:
        cursor.execute("CREATE TABLE IF NOT EXISTS srcs (url text, title text, language text)")

    except Error as err:
        misc.alrt()
        misc.log( "Error with creating the table srcs: " + str(err), errLogFile )


    # create the 2 srcs indices if needed: urlIdx(url), titleIdx(title)
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS titleIdx ON srcs(title)")

    except Error as err:
        misc.alrt()
        misc.log( "Error with creating the titleIdx index: " + str(err), errLogFile )

    if( findSrcs[0][0] != "srcs" ):

        # now need to fill the srcs table with data 
        # data source(s): srcs.csv
        wasFilled = fillSrcs( connection, cursor )
        if ( not wasFilled ):
            misc.alrt()
            misc.log( "fillSrcs() reports no fill of the srcs table", errLogFile )
            quit

    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS urlIdx ON srcs(url)")

    except Error as err:
        misc.alrt()
        misc.log( "Error with creating the urlIdx index: " + str(err), errLogFile )


    # create the synths table if necessary
    try:
        cursor.execute( "CREATE TABLE IF NOT EXISTS synths (skey text, synTopic text, hdlUrls text)" )

    except Error as err:
        misc.alrt()
        misc.log( "Error with creating the table synths: " + str(err), errLogFile )

    # create the 1 synths indices if needed: skeyIdx(skey)
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS skeyIdx ON synths(skey)")
    except Error as err:
        misc.alrt()
        misc.log( "Error with creating the skeyIdx index: " + str(err), errLogFile )


    # create the users table if necessary
    # NOTE: Configuration fields need to be added 
    try:
        cursor.execute( "CREATE TABLE IF NOT EXISTS users (uid text)" )

    except Error as err:
        misc.alrt()
        misc.log( "Error with creating the table users: " + str(err), errLogFile )

    # create the 1 synths indices if needed: skeyIdx(skey)
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS uidIdx ON synths(uid)")

    except Error as err:
        misc.alrt()
        misc.log( "Error with creating the uidIdx index: " + str(err), errLogFile )


    try:
        connection.commit()
    except Error as err:
        misc.alrt()
        misc.log( "Failed to commit() this connection in startDB(): " + str(err), errLogFile )
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
def addToDB( data, connection, cursor ):

    """
    adds to the end of the database
    """

    #value = ( data["key"], data["url"], data["title"], data["headlines"], data["artLink"], data["articles"], data["topic"] )
    value = ( data["key"], data["url"], data["headlines"], data["artLink"], data["articles"], data["topic"] )

    try:
        result = cursor.execute( "INSERT INTO news VALUES (?,?,?,?,?,?)", value )
    except Error as err:
        misc.alrt()
        misc.log( "Failed to save the data for: " + data["title"] + ": " + str(err), "InsertErrors.txt" )
    except KeyError as err:
        misc.alrt()
        misc.log( "Failed to save the data for - KeyError: " + data["title"] + ": " + str(err), "InsertErrors.txt" )
    
    try:
        connection.commit()
    except Error as err:
        misc.alrt()
        misc.log( "Failed to commit() this connection in addToDB(): " + str(err), errLogFile )
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
def fillSrcs( connection, cursor ):

    """
    fills the srcs table with the data in the srcs.csv file
    see archive\dbi1.py
    
    """

    csvFile = r"C:\Projects\DataViz\Deocracy\NewsBot\srcs.csv"
    result  = None
    cF      = open( csvFile, "r" )
    csvUrls = csv.reader( cF )
    theUrls = list( csvUrls )
    
    sqlStmt = "INSERT INTO srcs (url, title) VALUES (?,?)"
    
    try:
        result = cursor.executemany( sqlStmt, theUrls )
    except sqlite3.OperationalError as err:
        print( "OperationalError - Failed to save the data for: " + baseUrl + ": " + str(err) )
    except SQLITE_ERROR as err:
        misc.alrt()
        print( "SQLITE_ERROR - Failed to save the data for: " + baseUrl + ": " + str(err) )

    if ( not result == None ):
        toReturn = True
    else:
        toReturn = False

    connection.commit()
    return toReturn
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
def updateDB( data, connection, cursor, theTable, baseUrl ):

    """
    inserts data to a specific field with a specific url to a specific table in the database
    10/08/22: currently only used by nameHdls.daMain()
    still: need to add table parameter
    """

    nuData = data.translate( str.maketrans( "", "", string.punctuation ) )

    # only good for srcs w/2 fields
    #sqlStmt = "UPDATE " + theTable + " SET title = '" + data + "' WHERE url = " + '"' + baseUrl + '"'
    sqlStmt  = 'UPDATE ' + theTable + ' SET title = "' + nuData + '" WHERE url = ' + '"' + baseUrl + '"'

    try:
        result = cursor.execute( sqlStmt )
    except sqlite3.OperationalError as err:
        misc.alrt()
        print( "nuData == ", nuData )
        print( "sqlStmt == ", sqlStmt )
        print( "baseUrl == ", baseUrl )
        print( "err == ", err )
        misc.log( "OperationalError - Failed to save the data for: " + baseUrl + ": " + str(err), errLogFile )
    except SQLITE_ERROR as err:
        misc.alrt()
        misc.log( "SQLITE_ERROR - Failed to save the data for: " + baseUrl + ": " + str(err), errLogFile )

    try:
        connection.commit()
    except Error as err:
        misc.alrt()
        misc.log( "Failed to commit() this connection in updateDB(): " + str(err), errLogFile )
#---------------------------------------------------------------------------


#---------------------------------------------------------------------------
def connToDB( theDB ):
    #theDB = "F:/simplewiki-20210401/simplewiki-20210401.xml"
    dbcon = None
    try:
        dbcon = sqlite3.connect( theDB )
    except Error as err:
        misc.alrt()
        misc.log( "Error connecting to the database " + theDB + ": " + str(err), errLogFile )
        quit()

    try:
        dbcur = dbcon.cursor()
    except Error as err:
        #print( e )
        misc.alrt()
        misc.log( "Error creating a cursor: " + str(err), errLogFile )
        quit()

    startDB( dbcon, dbcur )

    return dbcon, dbcur
#---------------------------------------------------------------------------
