# database.py String validation for jonapp2
# Authors: Nate Sales
#
# This file provides string validators by regex.
# It may be imported and used anywhere.

import re


def email(raw):
    _regex = "^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
    return re.search(_regex, raw)


def phone(raw):
    _regex = "^[\dA-Z]{3}-[\dA-Z]{3}-[\dA-Z]{4}$"
    return re.search(_regex, raw)
