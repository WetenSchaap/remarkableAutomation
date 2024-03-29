import rmapy
import rmapy.document
import subprocess
import zipfile
import os
import os.path
import tempfile
import json
import shutil

import sys
sys.path.append("/home/pi/easyrmapy")
import easyrmapy as er

# Parameters:
#upload_path = "generated by rest of script."
#hcl_file = "notes.hcl"

def generate_rm_from_hcl(hcl_file,outfilename):
    """ 
    Generates rm zipfile ready for upload from given .hcl file. 
    Drawj2d must be installed, find it here: https://drawj2d.sourceforge.io/
    Just be warry: the generated file contains some weird stuff that the remarkable
    may not like, so run fix_hclgenerated_file after genearation.

    Returns something like True if things worked, raises error if not.
    """
    outfilename = os.path.join(os.path.split(hcl_file)[0],"notes.zip")
    drawj2d = ["drawj2d", "-Trmapi", hcl_file, "-o", outfilename]
    result = subprocess.check_output( drawj2d, text=True, )
    return result

def fix_hclgenerated_file(file_to_fix,template=r"b'P Dots S\n'",content_template="content-template.json"): #last_pen="Ballpointv2"):
    """
    rm files generated with Drawj2d have some errors in them. Use this function to fix them.
    This function solves: 
        * Change last used pencil to ballpointpen. Or whatever is specified in the content-template.json

    TODO:
    This function should fix nonexistent file template errors, but it does not and I don't understand why.
    Uh. yeah. Ok.

    To use, just give this function the location of the generated zipfile, it will replace it with the fixed verison.
    It needs a content template, so I know what the .content file should look like.
    """
    # first unpack zipfile
    file_to_fix = os.path.abspath(file_to_fix)
    file_to_fix_wo_ext = os.path.splitext(file_to_fix)[0]
    with tempfile.TemporaryDirectory() as tempfolder:
        with zipfile.ZipFile(file_to_fix,"r") as zip_ref:
            zip_ref.extractall(tempfolder)

        # now make the changes I want.
        # In this unpacked folder, there are 2 files, (uuid.pagedata & uuid.content), 1 folder
        # in the folder nothing of interest is found
        # the .pagedata contains the file background, so probably you want "b'P Dots S\n'"
        pagedata_path = [each for each in os.listdir(tempfolder) if each.endswith('.pagedata')][0]
        with open(os.path.join(tempfolder,pagedata_path),"w") as f:
            f.write(template)
        # the .content file contains stuff like the last used pen, set that to something nice as well:
        content_path = [each for each in os.listdir(tempfolder) if each.endswith('.content')][0]
        with open(content_template,"r") as f:
            l = json.load(f)
        with open(os.path.join(tempfolder,content_path),"w") as f:
            json.dump(l,f)
        
        # now put everything back in .zip file
        shutil.make_archive(file_to_fix_wo_ext, 'zip', tempfolder)
    # print("All done!")
    return None


def make_rm_notes(upload_path, hcl_file, rmfilename, logger=None):
    """
    I was to lazy to use relative paths, so make sure to use absolute paths.
    """
    outfilename = os.path.join(os.path.split(hcl_file)[0],"notes.zip")

    # first generate file and fix it:
    generate_rm_from_hcl(hcl_file,outfilename)
    fix_hclgenerated_file(outfilename,content_template=r"/home/pi/remarkableAutomation/content-template.json")
    print("File generated and fixed")
    if logger:
        logger.info("generated file from hcl file")

    # find correct UUID (nessecary due to bug in rmapy)
    zipf = zipfile.ZipFile(outfilename)
    names = zipf.namelist()
    uuid = os.path.splitext(names[0])[0]
    uuid = uuid.replace("/",'')
    print("UUID found:", uuid)
    if logger:
        logger.info( "Found correct UUID: {}".format(uuid) )


    print("now upload:")
    # upload the generated zip
    rm = er.ReMarkable()
    zipdoc = rmapy.document.ZipDocument(file=outfilename,_id=uuid)
    parentID = rm.path_to_ID(upload_path)
    dirobj = rm.rma.get_doc(parentID)
    result = rm.rma.upload(zipdoc,dirobj)
    if not result:
        if logger:
            logger.error( "Upload of zipdocument to rmcloud failed!" )
        raise ValueError("upload failed :.(")

    print("Rename file in cloud...")
    # Finally, rename file to notes
    doc = rm.rma.get_doc(uuid)
    doc.VissibleName = rmfilename
    rm.rma.update_metadata(doc)
    if logger:
        logger.info( "VissibleName of uploaded file corrected." )
    print("Complete!")


def make_rm_notes_old(upload_path, hcl_file):
    """
    I was to lazy to use relative paths, so make sure to use absolute paths.
    """
    # first generate file for today:
    outfilename = os.path.join(os.path.split(hcl_file)[0],"notes.zip")
    drawj2d = ["drawj2d", "-Trmapi", hcl_file, "-o", outfilename]
    result = subprocess.check_output( drawj2d, text=True, )

    # find correct UUID (nessecary due to bug in rmapy)
    zip = zipfile.ZipFile(outfilename)
    names = zip.namelist()
    uuid = os.path.splitext(names[0])[0]

    # upload the generated zip
    rm = er.ReMarkable()
    zipdoc = rmapy.document.ZipDocument(file=outfilename,_id=uuid)
    parentID = rm.path_to_ID(upload_path)
    dirobj = rm.rma.get_doc(parentID)
    result = rm.rma.upload(zipdoc,dirobj)
    if not result:
        raise ValueError("upload failed :.(")

    # Finally, rename file to notes
    doc = rm.rma.get_doc(uuid)
    doc.VissibleName = "Notes"
    rm.rma.update_metadata(doc)