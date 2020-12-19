import logging
import json
import datetime
import os
import os.path

import remarkable
import nrc
import messaging

def initialize_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
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
    with open("options.json",'r') as o:
        options = json.load( o )

    # connect to cloud
    rm = remarkable.ReMarkable( options )

    # now acually do stuff
    dt = datetime.datetime.now()
    if dt.isoweekday() in [1,2,3,4,5]: # workday
        # first try downloading nrc.next newspaper
        try:
            nrcpath = nrc.download_nrcNext(options, logger)
            logger.debug("nrc.next downloaded")
            # split into pieces before upload:
            rmpdfs = nrc.nrc_to_rmpdfs(nrcpath, options["nrcSaveDir"])
            logger.debug("nrc split into pieces for upload")
            # clean up original file
            os.remove(nrcpath)
            # delete old/upload new newspaper
            rm.empty_dir( options["nrcRemoteSaveDir"] )
            logger.debug("Old newspaper was deleted")
            for pdf in rmpdfs:
                rm.upload(pdf, options["nrcRemoteSaveDir"] )
                logger.debug("uploaded {0}".format(pdf))
                # and clean locally
                os.remove(pdf)
            logger.info("new newspaper was uploaded")
        except:
            logger.error("Newspaper failed, sending warning")
            messaging.telegram_message("Newspaper to ReMarkable failed!",
                                       options["telegramBotBaseURL"])
        # make new labjournal day folder (and later add a notes notebook in this folder)
        rm.make_labjournal_subfolder( dt.strftime("%Y%m%d") )

    elif dt.isoweekday() in [6]: # saturday
        # first try downloading nrc.next newspaper
        try:
            nrcpath = nrc.download_nrcNext(options, logger)
            logger.debug("nrc.next downloaded")
            # split into pieces before upload:
            rmpdfs = nrc.nrc_to_rmpdfs(nrcpath, options["nrcSaveDir"])
            logger.debug("nrc split into pieces for upload")
            # clean up original file
            os.remove(nrcpath)
            # delete old/upload new newspaper
            rm.empty_dir( options["nrcRemoteSaveDir"] )
            logger.debug("Old newspaper was deleted")
            for pdf in rmpdfs:
                rm.upload(pdf, options["nrcRemoteSaveDir"] )
                logger.debug("uploaded {0}".format(pdf))
                # and clean locally
                os.remove(pdf)
            logger.info("new newspaper was uploaded")
        except:
            logger.error("Newspaper failed, sending warning")
            messaging.telegram_message("Newspaper to ReMarkable failed!",
                                       options["telegramBotBaseURL"])

    logger.info("All done, stopping for today.")