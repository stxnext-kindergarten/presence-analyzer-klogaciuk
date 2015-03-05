# -*- encoding: utf-8 -*-
"""
Cron function
"""

import urllib2

from presence_analyzer.config import (
    USERS_XML_FILE,
    USERS_XML_URL,
)


def update_users_file():
    """
    Download actual users data XML.
    """
    remote_file = urllib2.urlopen(USERS_XML_URL)
    local_file = open(USERS_XML_FILE, "w")
    data = remote_file.read()
    local_file.write(data)
    local_file.close()
    remote_file.close()
    return data


if __name__ == '__main__':
    update_users_file()
