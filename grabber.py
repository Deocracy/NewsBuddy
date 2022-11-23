# grabber.py

"""
testing the newscatcher library
see also: NewsCatcherLibNotes.txt
"""


#!/usr/bin/env python
# coding: utf-8

#-------------------------------------------------------------------------------------------
import os, sys, re, requests
from newscatcher import Newscatcher as NC
from newscatcher import describe_url
from newscatcher import urls
#from urllib.parse import urlparse
import urllib3
import json                           # for jsonLog()
import dbMgr as dbm                   # for database storage instead of log()
import misc
import datetime
import time
#from googletrans import Translator
from bs4 import BeautifulSoup as soup
#import multiprocessing
#from multiprocessing import Pool, TimeoutError

errLogFile = "Errors.txt"
theDB      = "NBAI.db"
beep       = chr(7)
#__spec__   = None
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def savePage(url, pagepath='page'):
    def savenRename(soup, pagefolder, session, url, tag, inner):
        if not os.path.exists(pagefolder): # create only once
            os.mkdir(pagefolder)
        for res in soup.findAll(tag):   # images, css, etc..
            if res.has_attr(inner): # check inner tag (file object) MUST exists  
                try:
                    filename, ext = os.path.splitext(os.path.basename(res[inner])) # get name and extension
                    filename = re.sub('\W+', '', filename) + ext # clean special chars from name
                    # urljoin() not defined
                    fileurl = urljoin(url, res.get(inner))
                    filepath = os.path.join(pagefolder, filename)
                    # rename html ref so can move html and folder of files anywhere
                    res[inner] = os.path.join(os.path.basename(pagefolder), filename)
                    if not os.path.isfile(filepath): # was not downloaded
                        with open(filepath, 'wb') as file:
                            filebin = session.get(fileurl)
                            file.write(filebin.content)
                except Exception as exc:
                    print(exc, file=sys.stderr)
    session = requests.Session()
    #... whatever other requests config you need here
    response = session.get(url)
    soup = soup( response.text, "html.parser" )
    path, _ = os.path.splitext(pagepath)
    pagefolder = path+'_files' # page contents folder
    tags_inner = {'img': 'src', 'link': 'href', 'script': 'src'} # tag&inner tags to grab
    for tag, inner in tags_inner.items(): # saves resource files and rename refs
        savenRename(soup, pagefolder, session, url, tag, inner)
    with open(path+'.html', 'wb') as file: # saves modified html doc
        file.write(soup.prettify('utf-8'))
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
    s4Lnk   = str( str4Link )
    #s4LnkEN = misc.doTrans( s4Lnk, "en", "str" )
    toFind  = "'href': '"
    l2f     = len( toFind )
    #fnd     = s4LnkEN.find( toFind )
    fnd     = s4Lnk.find( toFind )

    if ( fnd < 0 ):

        toFind  = 'article < a rel="nofollow" href="'
        l2f     = len( toFind )
        fnd     = s4Lnk.find( toFind )
        if ( fnd < 0 ):
            toFind  = 'article <a rel="nofollow" href="'
            l2f     = len( toFind )
            fnd     = s4Lnk.find( toFind )   # s4LnkEN
            prtStr  = s4Lnk[fnd+l2f:]        # s4LnkEN

    else:
        prtStr  = s4Lnk[fnd+l2f:-2]          # s4LnkEN

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
    load all news source urls to urls[]
    10/13/22: was: using allNCGoodUrls.txt as the url source
    change to: use the srcs table from the db
    """

    urls    = []
    titles  = []
    theList = []

    sqlStmt = "SELECT * FROM srcs"
    try:
        theList = curs.execute( sqlStmt ).fetchall()
    except Error as err:
        misc.alrt()
        misc.log( "Error getting all data from NBAI.db: " + str(err), errLogFile )

    for ele in theList:

        urls.append( ele[0] )
        titles.append( ele[1] )

    return urls, titles
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

    """
    with Pool( processes=4 ) as daPool:
        lst = daPool.map( NC.get_headlines(theNews, 10) )
    """

    try:
        lst = NC.get_headlines(theNews, 10)   # was 10 / 5
    except:
        misc.log( "Failed to Get Headlines", errLogFile )

    return lst
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def prepAndSave( theUrl, conn, curs, lst, arts ):

    """
    find the article that matches each headline in lst[]
    for each headline and article save to the database
    """

    artLoc   = ""
    toInsert = ""
    artHtml  = ""
    artLink  = ""
    
    for hdl in lst:

        for ele in range( len(arts) ):

            # get this article's title - if there is one
            if ( "title" not in arts[ele] ):
                artLink = ""
                continue

            thisArt = arts[ele]["title"]

            # if this article's title is the same as this headline
            if ( thisArt == hdl ):

                # find the source of the full article on this website
                # NOT present in arts[]
                # use either the links key or the content key to get the url for this article on this same site 
                if ( "links" in arts[ele].keys() ):
                    artLoc = arts[ele]["links"]
                elif ( "link" in arts[ele].keys() ):
                    artLoc = arts[ele]["link"]
                else:
                    artLoc = arts[ele]["content"]

                # parse the link to the full article from either the article links or content data
                artLink  = gitArtLink( str(artLoc) )

                # grab this article and store in the artHtml variable
                #artHtml  = gitArt( artLink )
                artHtml  = ""     # 08/30/22: place-holder for eventual article grabbing

                # got the article that matches this headline, leave this loop
                break

        tmpNow = str( datetime.datetime.now() )
        # time stamp to help locate past stories, range of stories, etc.
        now    = tmpNow[:tmpNow.find(".")]

        # save to the database either the headline & article, or the headline & error message
        # 08/30/22: artHtml not used - NOT grabbing the article
        #if ( artHtml != "" ):
        #toInsert       = { "key": now, "url": str(theUrl), "title": "", "headlines": hdl, "artLink": artLink, "articles": artHtml, "topic": "" }
        toInsert       = { "key": now, "url": str(theUrl), "headlines": hdl, "artLink": artLink, "articles": artHtml, "topic": "" }
        dbm.addToDB( toInsert, conn, curs )

        #else:
            #toInsert       = { "key": now, "title": str(theUrl), "headlines": hdl, "artLink": artLink, "articles": "No articles matching this headline: " + hdl }
            #dbm.addToDB( toInsert, conn, curs )
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def doGrab( urls ):

    for theUrl in urls:

        st.write( theUrl )
        misc.log( theUrl, "UrlsRan.txt" )

        # create a newscatcher object
        theNews = gitNewsObj( theUrl )
        if ( theNews == None ):
            misc.alrt()
            continue

        # create a newscatcher results object
        #with Pool( processes=4 ) as daPool:
            #results = gitRslts( theNews )
        try:
            results = gitRslts( theNews )
        except Error as err:
            misc.alrt()
            misc.log( str(theUrl) + ": No Results: " + str(err), errLogFile )

        if ( results == None ):
            misc.alrt()
            misc.log( str(theUrl) + ": No Results: ", errLogFile )
            continue

        # all the headlines using the newscatcher object (theNews) to a list
        lstHeadlines = gitHeads( theNews ) 

        if ( "articles" in results ):
            arts     = results["articles"]
        else:
            misc.log( "No articles for this url: " + theUrl, errLogFile )
            continue

        if ( lstHeadlines != None ):

            # find the article that matches each headline in lstHeadlines[]
            # for each headline and article save to the database
            prepAndSave( theUrl, conn, curs, lstHeadlines, arts )

        else:
            misc.alrt()
            misc.log( str(theUrl) + ": No headlines!", errLogFile )
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def grabMain():

    #newsSrc = "allNCGoodUrls.txt"
    start   = time.time()
    urls    = []
    titles  = []

    # create a connection object with the database
    conn, curs = dbm.connToDB( theDB )
    if ( conn == None ):
        misc.alrt()
        quit

    # load all news source urls to urls[]
    urls, titles = gitUrls( conn, curs )
    if ( urls == None ) or ( urls == [] ):
        misc.alrt()
        quit

    for theUrl in urls:

        print( theUrl )                # "The url is: " + 
        misc.log( theUrl, "UrlsRan.txt" )

        # create a newscatcher object
        theNews = gitNewsObj( theUrl )
        if ( theNews == None ):
            misc.alrt()
            continue

        try:
            results = gitRslts( theNews )
        except Error as err:
            misc.alrt()
            misc.log( str(theUrl) + ": No Results: " + str(err), errLogFile )

        if ( results == None ):
            misc.alrt()
            misc.log( str(theUrl) + ": No Results: ", errLogFile )
            continue

        # all the headlines using the newscatcher object (theNews) to a list
        lstHeadlines = gitHeads( theNews ) 

        if ( "articles" in results ):
            arts     = results["articles"]
        else:
            misc.log( "No articles for this url: " + theUrl, errLogFile )
            continue

        if ( lstHeadlines != None ):

            # find the article that matches each headline in lstHeadlines[]
            # for each headline and article save to the database
            prepAndSave( theUrl, conn, curs, lstHeadlines, arts )

        else:
            misc.alrt()
            misc.log( str(theUrl) + ": No headlines!", errLogFile )

    conn.close()
    dt = time.time() - start
    timeTaken = dt / 3600
    print( "Time elapsed = " + str(timeTaken) + " hours" )
    print( "\n\n", result )
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
if __name__ == '__main__':

    grabMain()
#-------------------------------------------------------------------------------------------


