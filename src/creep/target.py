#!/usr/bin/env python

import re
import urllib

def build (connection, options):
	# FIXME: should use urllib.parse
	match = re.match ('([+0-9A-Za-z]+)://(?:([^#/:@]+)(?::([^#/@]+))?@)?(?:([^#/:]+)(?::([0-9]+))?)?(?:/+([^#]*))?', connection)

	if match is None:
		return None

	host = match.group (4)
	password = urllib.unquote_plus (match.group (3))
	path = match.group (6) or '.'
	port = match.group (5) is not None and int (match.group (5)) or None
	scheme = match.group (1)
	user = urllib.unquote_plus (match.group (2))

	if scheme == 'console':
		from targets.console import ConsoleTarget

		return ConsoleTarget ()

	if scheme == 'ftp':
		from targets.ftp import FTPTarget

		return FTPTarget (host, port, user, password, path, options)

#	if scheme == 'local':
#		from targets.ssh import LocalTarget

#		return LocalTarget (path)

	if scheme == 'ssh':
		from targets.ssh import SSHTarget

		return SSHTarget (host, port, user, path)

	return None
