""" 
Super simple script that uploads a file with todays date as name to the remarkable. 
You are supposed to run this as a cronjob.
"""

import logging
import json
import datetime
import os
import os.path

import remarkable
import messaging
import generate_rm_notes as grn

def initialize_logging(logpath):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(logpath)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    upload_path = r"/Labjournal"

    # setup logging
    logger = initialize_logging( os.path.join(script_dir,'rmconnect.log') )
    logger.info('Starting new session')

    # load options
    options_path = os.path.join( script_dir, "options.json" )
    with open(options_path,'r') as o:
        options = json.load( o )
    logger.info("Options loaded from: '{}'".format(options_path))

    # connect to cloud
    # rm = remarkable.ReMarkable( options )

    # notes hcl generation location
    hcl_file = os.path.join( script_dir, "notes.hcl" )

    dt = datetime.datetime.now()
    logger.info( "Today is ISOday = {0}".format(dt.isoweekday()) )
    # make printable date
    rmfilename = dt.strftime("%Y%m%d")

    # now acually do stuff
    grn.make_rm_notes(upload_path, hcl_file, rmfilename, logger)
    
    # and log...
    messaging.telegram_message( "Completed the ReMarkable labjournal upload for today!",
                                options["telegramBotBaseURL"])
    logger.info("All done, stopping for today.")
