# grabber.py

"""
testing the newscatcher library
see also: NewsCatcherLibNotes.txt
"""


#!/usr/bin/env python
# coding: utf-8

#-------------------------------------------------------------------------------------------
import requests
from newscatcher import Newscatcher as NC
import dbMgr as dbm                   # for database storage instead of log()
import misc
import datetime
import time
import os.path
import sqlite3

errLogFile = "Errors.txt"
theDB      = "NBAI.db"
beep       = chr(7)
lines2     = "\n\n"
#__spec__   = None
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def gitArt( theLink ):

    req     = None
    theHTML = ""

    print( "theLink == " + theLink )
    #misc.log( theLink, "ArtLinksGrabbed.txt" )
    try:
        req = requests.get( theLink )

    except requests.exceptions.InvalidSchema as err:
        misc.alrt()
        misc.log( "Problem getting article with reqests.get() - InvalidSchema: " + str( err ), errLogFile )

    except requests.exceptions.MissingSchema as err:
        misc.alrt()
        misc.log( "Problem getting article with reqests.get() - MissingSchema: " + str( err ), errLogFile )

    except requests.exceptions.ConnectionError as err:
        misc.alrt()
        misc.log( "Problem getting article with reqests.get() - ConnectionError: " + str( err ), errLogFile )

    except requests.exceptions.InvalidURL as err:
        misc.alrt()
        misc.log( "Problem getting article with reqests.get() - InvalidURL: " + str( err ), errLogFile )

    except requests.exceptions.RequestException as err:
        misc.alrt()
        misc.log( "Problem getting article with reqests.get() - RequestException: " + str( err ), errLogFile )

    if ( req != None ):
        
        if ( req.status_code == requests.codes.ok ):
            theHTML = req.text
        else:
            misc.alrt()
            misc.log( "Problem getting article with reqests.get() for : " + theLink + " - " + str( req.status_code ), errLogFile )

    return theHTML
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def gitArtLink( str4Link ):

    strHtml = ""
    #s4LnkEN = misc.doTrans( str4Link, "en", "str" )


#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def gitArtLink1( str4Link ):

    strHtml = ""
    #s4LnkEN = misc.doTrans( str4Link, "en", "str" )
    toFind  = "'href': '"
    l2f     = len( toFind )
    #fnd     = s4LnkEN.find( toFind )
    fnd     = str4Link.find( toFind )

    if ( fnd < 0 ):

        toFind  = 'article < a rel="nofollow" href="'
        l2f     = len( toFind )
        fnd     = str4Link.find( toFind )

        if ( fnd < 0 ):
            toFind  = 'article <a rel="nofollow" href="'
            l2f     = len( toFind )
            fnd     = str4Link.find( toFind )
            prtStr  = str4Link[fnd+l2f:]

    else:
        prtStr  = str4Link[fnd+l2f:-2]

    q2f     = prtStr.find( '"' )
    if ( q2f < 0 ):                  # " not found
        q2f = prtStr.find( "'" )

        if ( q2f < 0 ):
            q2f = prtStr.find( "/" )

    strHtml = prtStr[:q2f]

    return strHtml
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def gitUrls( conn, curs ):                  # newsSrc ):

    """
    load all news source urls to theseUrls[]
    10/13/22: was: using allNCGoodUrls.txt as the url source
    change to: use the srcs table from the db
    """

    theseUrls = []
    titles    = []
    theList   = []

    sqlStmt = "SELECT * FROM srcs"
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

        theseUrls.append( ele[0] )
        titles.append( ele[1] )

    return theseUrls, titles
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def gitNewsObj( theUrl ):

    """
    create a newscatcher object
    """

    try:
        theNews = NC( theUrl )
    except Error as err:
        theNews = None
        misc.alrt()
        misc.log( "Failure to set up newscatcher for url == " + theUrl + ": " + str(err), errLogFile )

    return theNews
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def gitRslts( theNews ):

    """
    create a newscatcher results object
    10/08/22: with a pool
    """

    results = None
    #try:

    results = theNews.get_news()

    #except Error as err:
        #theNews = None
        #misc.alrt()
        #misc.log( str(theUrl) + ": No Results: " + str(err), errLogFile )

    return results
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def gitHeads( theNews ):

    lst = None

    try:
        lst = NC.get_headlines(theNews, 10)
    except:
        misc.log( "Failed to Get Headlines", errLogFile )

    return lst
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def doSave( conn, curs, theUrl, hdl, artLink, artHtml ):

    toInsert  = ""
    theResult = True    # was dbm.addToDB() successful or not

    # time stamp to help locate past stories, range of stories, etc.
    tmpNow = str( datetime.datetime.now() )
    now    = tmpNow[:tmpNow.find(".")]

    # save to the database either the headline & article, or the headline & error message
    # 08/30/22: artHtml not used - NOT grabbing the article
    #if ( artHtml != "" ):
        #toInsert = { "key": now, "url": str(theUrl), "title": "", "headlines": hdl, "artLink": artLink, "articles": artHtml, "topic": "" }

    toInsert      = { "key": now, "url": str(theUrl), "headlines": hdl, "artLink": artLink, "articles": artHtml, "topic": "" }
    saveResult = dbm.addToDB( toInsert, conn, curs )    # Failed: == None

    if ( saveResult != None ):
        theResult = True
    else:
        theResult = False

    #else:      (*if using real artHtml value*)
        #toInsert = { "key": now, "title": str(theUrl), "headlines": hdl, "artLink": artLink, "articles": "No articles matching this headline: " + hdl }
        #dbm.addToDB( toInsert, conn, curs )

    return theResult          # doSave()
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def prepAndSave( theUrl, conn, curs, hdlsList, artsList ):

    """
    find the article that matches each headline in hdlsList[]
    for each headline and article save to the database
    """

    artUrl   = ""
    artLink  = ""
    artHtml  = ""
    cntr     = 0
    
    # For each headline in the list of headlines
    for hdLine in hdlsList:

        # For each article in the list of articles
        for ele in range( len(artsList) ):

            # get this article's title - if there is one
            if ( "title" not in artsList[ele] ):
                artLink = ""
                continue

            thisArtTitle = artsList[ele]["title"]

            # if this article's title is the same as this headline
            if ( thisArtTitle == hdLine ):

                # find the source of the full article on this website
                # NOT present in artsList[]
                # use either the links key or the content key to get the url for this article on this same site 

                if ( "link" in artsList[ele].keys() ):
                    artUrl = artsList[ele]["link"]
                elif ( "links" in artsList[ele].keys() ):
                    artUrl = artsList[ele]["links"]
                else:
                    artUrl = artsList[ele]["content"]


                # parse the link to the full article from either the article link(s) or content data
                #artLink  = gitArtLink( str(artUrl) )

                artLink  = str(artUrl)

                # grab this article and store in the artHtml variable ==> artHtml  = gitArt( artLink )
                artHtml  = ""     # 08/30/22: place-holder for eventual article grabbing

                # got the article that matches this headline, leave this loop
                break
            cntr +=1

        if ( artLink == None ) or ( artLink == "" ):
            misc.log( "No article for " + theUrl + " for the " + str(cntr) + " headline", "noArts.txt" )

        # for each headline and article save to the database
        # 12/20/22: don't know if/how to use saveResult, since dbMgr:addToDB() logs all failures
        # &&& this is just one result of many
        saveResult = doSave( conn, curs, theUrl, hdLine, artLink, artHtml )

    return saveResult                 # prepAndSave()
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def doGrab( urls, conn, curs ):

    tmpLogFile = "UrlsRan.txt"
    grabRslt   = True

    for theUrl in urls:

        #st.write( theUrl )
        print( theUrl )
        misc.log( theUrl, tmpLogFile )
        wasSaved = False

        # create a newscatcher object
        theNews = gitNewsObj( theUrl )
        if ( theNews == None ):
            misc.alrt()
            continue

        # create a newscatcher results object
        #try:
        results = gitRslts( theNews )
        #except Error as err:
            #misc.alrt()
            #misc.log( str(theUrl) + ": No Results: " + str(err), errLogFile )

        if ( results == None ):
            misc.alrt()
            misc.log( str(theUrl) + ": No Results: ", errLogFile )
            continue

        # all the headlines using the newscatcher object (theNews) to a list
        lstHeadlines = gitHeads( theNews ) 

        if ( "articles" in results ):
            artsList = results["articles"]
        else:
            misc.log( "No articles for this url: " + theUrl, errLogFile )
            continue

        if ( lstHeadlines != None ):

            # find the article that matches each headline in lstHeadlines[]
            #hdl, artLink, artHtml = doPrep( theUrl, lstHeadlines, artsList )
            wasSaved = prepAndSave( theUrl, conn, curs, lstHeadlines, artsList )
            # wasSaved is for all of the headlines & article links,
            # so grabRslt is probably useless
            if wasSaved:
                grabRslt = True
            else:
                grabRslt = False

        else:
            misc.alrt()
            misc.log( str(theUrl) + ": No headlines!", errLogFile )
            grabRslt = False

    return grabRslt                   # doGrab()
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def grabMain():

    start    = time.time()
    allUrls  = []
    titles   = []

    # create a connection object with the database
    conn, curs = dbm.connToDB( theDB )
    if ( conn == None ):
        misc.alrt()
        misc.log( "Unable to make a database connection", errLogFile )
        quit

    # load all news source urls to allUrls[]
    allUrls, titles = gitUrls( conn, curs )
    if ( allUrls == None ) or ( allUrls == [] ):
        misc.alrt()
        quit

    finalResult = doGrab( allUrls, conn, curs )
    if ( finalResult ):
        rslt = "was Successful"
    else:
        rslt = "Failed"
    print( "The grab " + rslt )
    print( lines2 )

    conn.close()
    dt = time.time() - start
    timeTaken = dt / 3600
    print( "Time elapsed = " + str(timeTaken) + " hours" )
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
if __name__ == '__main__':

    grabMain()
#-------------------------------------------------------------------------------------------


