# misc.py

"""
holds most of the display, logging, & string/list/dictionary manipulation functions

CONTENTS:
jsonLog( txt, outPutFileName=None )
log( txt, outPutFileName=None )
alrt()
tup2str( tup )
tpls2str( theList )
tranEle( ele, lang )
doTrans( toTrans, lang, dType=None )
doShow( strToShow1, strToShow2 )
getConn()
getUrls( urlFile )
getSrcs( lang )
getTopics( lang )
"""

#!/usr/bin/env python
# coding: utf-8

#-------------------------------------------------------------------------------------------
# imports
import streamlit as st
import dbMgr as dbm                   # for database access & storage
import sqlite3
import sys
import time
#import googletrans
#from googletrans import Translator

theDB      = "NBAI.db"
errLogFile = "Errors.txt"
beep       = chr(7)
nu2Lines = "\n\n"
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def jsonLog( txt, outPutFileName=None ):

    # for logging data to a json format, from C:\Projects\DataViz\libraries\openAI\PlainTextWikipedia-d8497cf9085046147937186c8ce27a2a1a23a65e\simple_wikipedia_to_sqlite.py
    # pass only the base part of the name, no file suffix

    if( "json" not in outPutFileName ):
        outPutFileName = ( outPutFileName + ".json" )

    with open(filename, "w", encoding="utf-8") as outfile:
        json.dump( txt, outPutFileName, sort_keys=True, indent=1, ensure_ascii=False )

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
               #lF.write( toWrite.encode("ascii", "ignore").decode("utf-8") )
               lF.write( toWrite )
               lF.write( "\n" )

        elif ( "dict" in str( type( txt ) ) ):
           for key in txt:
               lF.write( key + ": " + str( txt[key] ) )
               lF.write( "\n" )

        elif ( "str" in str( type( txt ) ) ):
            #txt = txt.decode("utf-8").encode("ascii", "ignore").decode("utf-8")
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
def alrt():
    print( beep )
    print( beep )
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def tup2str( tup ):
# Convert a tuple into a string using str.join() method

    str = "".join(tup)
    return str           # + "\n"
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def tpls2str( theList ):

    """
    this always receives a list of tuples & returns a list that isn't
    """

    theStr = ""
    for itm in theList:

        tmpStr = tup2str( itm )
        theStr = theStr + tmpStr + "\n"

    lstStr     = theStr.split("\n")

    return lstStr
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def tranEle( ele, lang ):

    transTxt   = None
    translator = Translator()

    try:
        transTxt = translator.translate( ele, dest=lang ).text
    except IndexError as err:
        alrt()
        print( "Error translating: ", ele, str(err) )  #, errLogFile )
        transTxt = ele
        #print( transList, "transList.txt" )
    except:
        alrt()
        print( "Error translating", ele )                     #, errLogFile )
        transTxt = ele
        #print( transList, "transList.txt" )

    return transTxt
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def doTrans( toTrans, lang, dType=None ):

    """
    makes the call the the currently used translator
    10/27/22: works for Both toTrans being a String, or a List
    If passed a string, it returns a translated string,
    Ditto for lists, where each element in the list has been translated

    If dType hasn't been passed, doTrans will try to determine if it's one of the 2 data types currently working: string, & list
    """

    """
    NOTE: google translate can accept lists
    theList could be as long as 2350 elements
    ?? How to chunk out, e.g., 5k of elements and send that to translate() ??
    """

    transList  = []
    tempList   = []
    transText  = None
    maxLen     = 1000

    if ( dType == None ):

        if   ( "LIST" in str(type(toTrans)).upper() ):
            dType = "list"

        elif ( "STR" in str(type(toTrans)).upper() ):
            dType = "str"

    if   ( dType == "str" ):
        transText = tranEle( toTrans, lang )
        #print( "transText == " + transText )

    elif ( dType == "list" ):

        theList  = tpls2str( toTrans )          # tpls2str() always returns a de-tupled list  "\n" + 

        for ele in theList:

            if ( ele != None ):                 #print( ele, "\n" )

                if ( "www" not in ele ) and ( "http" not in ele ) and ( len(ele.strip() ) != 0 ) and ( ele != "\n" ):

                    #print( "ele == " + ele )
                    transText = tranEle( ele, lang )
                    #print( "transText == " + transText )
                    transList.append( transText )

    if   ( dType == "str" ):
        return transText
    elif ( dType == "list" ):
        #print( nu2Lines, "transList == ", nu2Lines, transList, nu2Lines )
        return transList
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def doShow( strToShow1, strToShow2 ):

    """
    10/27/22: currently expects a string, shows a list as a collapable & number set of strings [not a bad approach :)]
    """

    col1, col2 = st.columns(2)
    with st.container():
        col1.write( strToShow1 )
        col2.write( strToShow2 )
#-------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------
def getConn():

    try:
        conn, cur = dbm.connToDB( theDB )
    except Error as err:
        log( "Error connecting to NBAI.db: " + str(err), "getNewsrcsErrors.txt" )

    return conn, cur
#-------------------------------------------------------------------------------------------


#----------------------------------------------------------------------
def getUrls( urlFile ):

    """
    08/19/22: for text files formatted: <url>
    """

    tmpUrls = [""]   # makes 1st selection empty
    try:
        with open( urlFile, "r" ) as news:

            theUrls = news.read()
            theUrls = theUrls.split( "\n" )

        for source in theUrls:
            tmpUrls.append( source )

    except:
        print( "Either the file couldn't be opened, or trouble with parsing" )
        quit()

    return tmpUrls
#----------------------------------------------------------------------


#----------------------------------------------------------------------
def getSrcs( lang ):

    """
    gets a list of all of the news sources from the database
    pulls either the title field or the url field if title == None
    """

    theSrcs = [" "]
    conn    = None 
    cur     = None

    conn, cur = getConn()

    if ( conn != None ) and ( cur != None ):

        sqlStmt       = "SELECT DISTINCT title, url FROM srcs"
        result        = cur.execute( sqlStmt )
        lstHeadsOrig  = result.fetchall()
        conn.close()

        for ele in lstHeadsOrig:
            if ( ele[0] != None ):
                toAdd = ele[0]
            else:
                toAdd = ele[1]

            theSrcs.append( toAdd )

        transSrcs = theSrcs                   # temp until doTrans() issues resolved
        #transSrcs = doTrans( theSrcs, lang )

    else:
       st.write( "getConn() failed in getSrcs()" )

    return transSrcs
#----------------------------------------------------------------------


#----------------------------------------------------------------------
def getTopics( lang ):

    """
    for demo purposes, I'm pulling from a pre-massaged text file generated by GPT-3
    version 2 of the text file has 179 headlines
    version 3 has 20 headlines
    """

    topicSrc  = r"C:\Projects\DataViz\Deocracy\NewsBot\nbaiTopics3.txt"

    with open( topicSrc, "r" ) as ts:
        theTopics = ts.read().split("\n")
        #theTopics.append( ts.read().split("\n") )
        theTopics.insert( 0, " " )

    transTopics = theTopics              # temp for Demo
    #transTopics = doTrans( theTopics, lang )

    return transTopics
#----------------------------------------------------------------------
