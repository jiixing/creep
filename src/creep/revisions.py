#!/usr/bin/env python

import json

class Revisions:
	def __init__ (self, data):
		revs = {}	

		if data is not None:
			try:
				for (name, rev) in json.loads (data).iteritems ():
					revs[name] = rev

			except IOError:
				raise ValueError ('invalid revisions file')

		self.revs = revs

	def get (self, name):
		return self.revs.get (name, None)

	def serialize (self):
		return json.dumps (self.revs, indent = 4, sort_keys = True)

	def set (self, name, data):
		self.revs[name] = data
