# main.py

"""
Streamlit program to roughly draw out some of the options I described in NewsBotNotes.txt
"""

#!/usr/bin/env python
# coding: utf-8

import os
from multiView import MultiView
import nbai
import grabber
import streamlit as st
st.set_page_config( layout="wide" )


def main():

    app = MultiView()

    # Add all the application here
    app.add_app( "NBAI", nbai.app )   # WordViewWindow
    app.add_app( "Grabber", grabber.grabMain )

    # The main app
    app.run()

if __name__ == '__main__':

    st.header( "This is the Deocracy NewsBuddyAI" )    # .title
    main()




