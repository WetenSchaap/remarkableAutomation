'''
Initially created on 09-12-2020.

Download de nrc.next van vandaag en voer daar operaties op uit.

Gebruik selenium, aangezien inloggen mbv cookies lukt niet.
'''
#%% Imports
import os
import os.path
import datetime
import time
import logging
import json
import copy

import PyPDF4

import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pyvirtualdisplay

def download_nrcNext(options, logger, weekend = False):
    # before we do anything else, empty the download directory, so we do not accidentally upload yesterdays news
    filesToRemove = [os.path.join(downloaddir,f) for f in os.listdir(options['nrcLocalSaveDir'])]
    for f in filesToRemove:
        os.remove(f) 
    # start with the interesting websites:
    current = datetime.datetime.now()
    login_url = r"https://login.nrc.nl/login"
    # download_url is something like https://www.nrc.nl/next/2020/12/05/downloads/
    download_url = r"https://www.nrc.nl/next/{0}/{1:02}/{2:02}/downloads/".format(current.year, current.month, current.day)
    saveDir = options['nrcLocalSaveDir']

    display = pyvirtualdisplay.Display(visible=0, size=(1600, 1200))
    display.start()
    driver = webdriver.Chrome()
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('prefs',
                    {
                    "download.default_directory": saveDir,
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "plugins.plugins_disabled": ["Chrome PDF Viewer"]
                    }
    )
    logger.info("Loging into nrc website")
    driver.get( login_url )
    elementUs = driver.find_element_by_name("username")
    elementUs.send_keys( options['username'] )
    elementPw = driver.find_element_by_name("password")
    elementPw.send_keys( options['password'] )
    elementPw.submit()
    logger.info("Logged in")
    time.sleep(1) # let things load for a bit...
    driver.get( download_url )
    time.sleep(1)
    elements = driver.find_elements_by_class_name("de-downloads__button")
    try:
        downloadButton = [ i for i in elements if i.text == options["nrcformat"] ] [0]
    except IndexError:
        raise ValueError("No download button detected for format '.{0}'".format(options['nrcformat']) )
    download_url = downloadButton.get_attribute('href')
    logger.info("Found download url: {0}, now clicking button".format(download_url))
    logger.debug("Press download button")
    downloadButton.click()
    logger.info("Downloading now...")
    time.sleep( 20 ) # wait for download
    downloadFile =  os.listdir( saveDir )[0]
    if ".crdownload" in downloadFile:
        logger.debug("Download is slow")
        time.sleep( 30 ) # wait some more I guess? (esp in weekend)
        downloadFile =  os.listdir( saveDir )[0]
        if ".crdownload" in downloadFile:
            # give up
            raise ValueError("Dowload taking too long")
    driver.close()
    # check if file has appeared in download folder
    # that is not at temp/part file
    try:
        nrcFile =  os.listdir( saveDir )[0]
    except IndexError:
        raise ValueError("Download failed for some reason")
    if ".crdownload" in nrcFile:
        raise ValueError("Dowload failed for some reason")
    else:
        logger.info("nrc download succesful!")
        # it worked, change name to NRCnext.fileformat.
        if weekend:
            filename = "NRCweekend." + options['nrcformat']
        else:
            filename = "NRCnext." + options['nrcformat']
        os.rename( os.path.join(saveDir, nrcFile ),
                   os.path.join(saveDir, filename ) )
        return os.path.join(saveDir, filename )

def nrc_to_rmpdfs(nrcfile,tempfolder):
    """
    Converts a basic nrc pdf into many single files, with each page it's
    own file. It also cuts pages in 2 for easier reading.

    Args:
        nrcfile (str): path to nrc pdf
        tempfolder (str): path to dir to use for saving the individual pages.

    Returns:
        list_of_files (list of str): Location of all created files.
    """
    #split pdf into new file per page
    splitfiles = pdf_splitter(nrcfile,tempfolder)
    list_of_files = list()
    for f in splitfiles:
        basename =  os.path.basename(f)
        root,ext = os.path.splitext(basename)
        path_to = os.path.join(tempfolder,"{0}_h.pdf".format(root) )
        try:
            pdf_halver( f, path_to )
            list_of_files.append(path_to)
        except PyPDF4.utils.PdfReadError:
            # no sure what goes wrong, but just skip these pages?
            print("Warning: PDF read error at {0}".format(f))
        # remove old file to save space
        os.remove(f)
    return list_of_files

def pdf_splitter(path_from, path_to, verbose=False):
    """
    Split a pdf file into its constituent pages,
    and save each page individually.

    Args:
        path_from (str): Path to pdf.
        path_to (str): dir in which to save results
        verbose (bool): print generated filenames, etc.

    Returns:
        list_of_files (list of str): List of paths to all created files.
    """
    fname = os.path.splitext(os.path.basename(path_from))[0]
    pdf = PyPDF4.PdfFileReader(path_from)
    list_of_files = list()
    for page in range(pdf.getNumPages()):
        pdf_writer = PyPDF4.PdfFileWriter()
        pdf_writer.addPage(pdf.getPage(page))
        output_filename = os.path.join(path_to,
                                       '{0}_pagina_{1:03}.pdf'.format(
            fname, page+1))
        list_of_files.append(output_filename)
        with open(output_filename, 'wb') as out:
            pdf_writer.write(out)
        if verbose:
            print('Created: {}'.format(output_filename))
    return list_of_files

def pdf_halver(path_from, path_to, verbose=False):
    """
    Cuts a single page pdf in half, and save both sides as the same document.

    Args:
        path_from (str): Path to pdf.
        path_to (str): Path where to save results 
        verbose (bool): print generated filenames, etc.
    """
    pdf_writer = PyPDF4.PdfFileWriter()
    with open(path_from, 'rb') as f:
        pdf = PyPDF4.PdfFileReader(f)
        left_side = pdf.getPage(0)
        current_coords = left_side.mediaBox.upperRight
        new_coords = (current_coords[0] / 2, current_coords[1])
        left_side.mediaBox.upperRight = new_coords
        pdf_writer.addPage(left_side)

        with open(path_from, 'rb') as g:
            pdf = PyPDF4.PdfFileReader(g)
            right_side = pdf.getPage(0)
            right_side.mediaBox.upperLeft = new_coords
            pdf_writer.addPage(right_side)

            with open(path_to, mode="wb") as output_file:
                pdf_writer.write(output_file)
    if verbose:
        print('Created: {}'.format(path_to))
