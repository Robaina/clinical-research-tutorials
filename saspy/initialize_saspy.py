#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Prepare work environment to connect to SAS On Demand for Academics
Following: https://support.sas.com/ondemand/saspy.html

Download Jar files from: https://support.sas.com/downloads/package.htm?pid=2494#
"""

import os
import shutil
import argparse
from tempfile import TemporaryDirectory
from zipfile import ZipFile, is_zipfile

import saspy


def extract_zip_to_dir(zip_file, dir):
    with ZipFile(zip_file, "r") as zip:
        zip.extractall(path=dir)


def write_personal_config(region):
    if "Euro" in region:
        region_mirrors = ["odaws01-euw1.oda.sas.com", "odaws02-euw1.oda.sas.com"]
    elif "US" in region and "1" in region:
        region_mirrors = [
            "odaws01-usw2.oda.sas.com",
            "odaws02-usw2.oda.sas.com",
            "odaws03-usw2.oda.sas.com",
            "odaws04-usw2.oda.sas.com",
        ]
    elif "US" in region and "2" in region:
        region_mirrors = ["odaws01-usw2-2.oda.sas.com", "odaws02-usw2-2.oda.sas.com"]
    elif "Asia" in region and "1" in region:
        region_mirrors = ["odaws01-apse1.oda.sas.com", "odaws02-apse1.oda.sas.com"]
    elif "Asia" in region and "2" in region:
        region_mirrors = ["odaws01-apse1-2.oda.sas.com", "odaws02-apse1-2.oda.sas.com"]
    else:
        raise ValueError("Invalid region code")

    path_to_java = shutil.which("java")
    path_to_config = saspy.__file__.replace("__init__.py", "sascfg_personal.py")

    template = """
SAS_config_names = ['oda']
oda = {{
    'java': '{java}',
    'iomhost': {mirrors},
    'iomport': 8591,
    'authkey': 'oda',
    'encoding': 'utf-8'
}}
    """.format(
        java=path_to_java, mirrors=region_mirrors
    )
    with open(path_to_config, "w+", encoding="UTF-8") as file:
        file.write(template)


def write_authinfo(user, password):
    path_to_auth = os.path.join(os.path.expanduser("~"), ".authinfo")
    with open(path_to_auth, "w+") as file:
        file.write(f"oda user {user} password {password}")


def copy_jar_files(zip_file):
    """
    Copy required JAR files to install location
     https://sassoftware.github.io/saspy/configuration.html#attn-as-of-saspy-version-3-3-3-the-classpath-is-no-longer-required-in-your-configuration-file
    """
    path_to_saspy_java_dir = saspy.__file__.replace(
        "__init__.py", "java%siomclient" % os.sep
    )
    if not is_zipfile(zip_file):
        raise ValueError("Failed to located Zip file containing JAR files")
    else:
        with TemporaryDirectory() as temp:
            extract_zip_to_dir(zip_file, temp)
            for file in os.listdir(temp):
                shutil.copy(os.path.join(temp, file), path_to_saspy_java_dir)


parser = argparse.ArgumentParser(
    prog="saspy_setup",
    description="Setup SASpy in Linux",
    epilog="  \n",
    formatter_class=argparse.RawTextHelpFormatter,
)

parser.add_argument("-z", "--zip", dest="zip", help="path to zip file")
parser.add_argument(
    "-r",
    "--region",
    dest="region",
    help="mirror region: US 1, US 2, Euro, Asia 1 or Asia 2",
)
parser.add_argument("-u", "--user", dest="user", help="ODA User ID")
parser.add_argument("-p", "--password", dest="password", help="ODA password")
args = parser.parse_args()


write_authinfo(args.user, args.password)
write_personal_config(args.region)
copy_jar_files(args.zip)
print("All done!")