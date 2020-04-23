# database.py String validation for jonapp2
# Authors: Nate Sales
#
# This file provides string validators by regex.
# It may be imported and used anywhere.

import re


def email(raw):
    return re.search("^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$", raw)


def phone(raw):
    return re.search("^[\dA-Z]{3}-[\dA-Z]{3}-[\dA-Z]{4}$", raw)
