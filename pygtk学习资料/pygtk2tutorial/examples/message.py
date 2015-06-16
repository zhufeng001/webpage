#!/usr/bin/env python

# message.py -- example program illustrating use of message dialog widget 

import pygtk
pygtk.require('2.0')
import gtk

if __name__ == "__main__":
    message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
    message.set_markup("An example error popup.")
    message.run()
