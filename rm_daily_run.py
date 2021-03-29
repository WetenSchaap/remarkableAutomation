import logging
import json
import datetime
import os
import os.path

import remarkable
import nrc
import messaging
import generate_rm_notes as grn

def initialize_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler('rmconnect.log')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

if __name__ == "__main__":
    # setup logging
    logger = initialize_logging()
    logger.info('Starting new session')

    # load options
    script_dir = os.path.dirname(__file__)
    options_path = os.path.join( script_dir, "options.json" )
    with open(options_path,'r') as o:
        options = json.load( o )

    # connect to cloud
    rm = remarkable.ReMarkable( options )

    # notes hcl generation location
    hcl_file = "./notes.hcl"

    # now acually do stuff
    dt = datetime.datetime.now()
    if dt.isoweekday() in [1,2,3,4,5]: # workday
        logger.info( "Today is a working day (ISOwday = {0})".format(dt.isoweekday()) )
        # make new labjournal day folder (and later add a notes notebook in this folder)
        date_str = dt.strftime("%Y%m%d")
        rm.make_labjournal_subfolder( date_str )
        upload_path = r"Labjournal/" + date_str
        grn.make_rm_notes(upload_path, hcl_file)

        # also try downloading nrc.next newspaper
#        try:
#            nrcpath = nrc.download_nrcNext(options, logger)
#            logger.debug("nrc.next downloaded")
#            # split into pieces before upload:
#            rmpdfs = nrc.nrc_to_rmpdfs(nrcpath, options["nrcLocalSaveDir"])
#            logger.debug("nrc split into pieces for upload")
 #           # clean up original file
 #           os.remove(nrcpath)
            # delete old/upload new newspaper
#            rm.empty_dir( options["nrcRemoteSaveDir"] )
#            logger.debug("Old newspaper was deleted")
#            for pdf in rmpdfs:
#                rm.upload(pdf, options["nrcRemoteSaveDir"] )
#                logger.debug("uploaded {0}".format(pdf))
#                # and clean locally
#                os.remove(pdf)
#            logger.info("new newspaper was uploaded")
#        except Exception:
#            logger.exception( "Newspaper handling failed:" )
#            logger.info("Sending failure warning")
#            messaging.telegram_message("Newspaper to ReMarkable failed!",
#                                       options["telegramBotBaseURL"])

    elif dt.isoweekday() in [6]: # Saturday
        logger.info( "Today is Saturday (ISOwday = {0})".format(dt.isoweekday()) )
        # first try downloading nrc.next newspaper
#        try:
#            nrcpath = nrc.download_nrcNext(options, logger)
 #           logger.debug("nrc.next downloaded")
 #           # split into pieces before upload:
 #           rmpdfs = nrc.nrc_to_rmpdfs(nrcpath, options["nrcLocalSaveDir"])
 #           logger.debug("nrc split into pieces for upload")
  #          # clean up original file
  #          os.remove(nrcpath)
  #          # delete old/upload new newspaper
  #          rm.empty_dir( options["nrcRemoteSaveDir"] )
  #          logger.debug("Old newspaper was deleted")
  #          for pdf in rmpdfs:
#                rm.upload(pdf, options["nrcRemoteSaveDir"] )
 #               logger.debug("uploaded {0}".format(pdf))
                # and clean locally
  #              os.remove(pdf)
  #          logger.info("new newspaper was uploaded")
  #      except Exception as e:
#            logger.exception( "Newspaper handling failed:" )
 #           logger.info("Sending failure warning")
  #          messaging.telegram_message("Newspaper to ReMarkable failed!",
   #                                    options["telegramBotBaseURL"])
    messaging.telegram_message( "Completed the ReMarkable jobs for today!",
                                options["telegramBotBaseURL"])
    logger.info("All done, stopping for today.")
