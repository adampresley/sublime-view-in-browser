#
# History:
#  	10/25/2012:
# 			- New settings.json file to map browser/commands to OSes
# 			- Plugin will use the specified browser to open files, or default to OS default when browser is unsupported
# 			- Addressed encoding issue when calling open_new_tab
#
# 		05/21/2012:
# 			- Temp file only created if view is unsaved
#
# 		05/18/2012:
# 			- Initial code
#
import sublime, sublime_plugin
import os, tempfile, webbrowser
import json, re, sys

PLUGIN_DIRECTORY = os.getcwd()

class ViewInBrowserCommand(sublime_plugin.TextCommand):
	_settings = None
	_browserCommand = ""

	def run(self, edit):
		#
		# Load settings, if any
		#
		self._loadSettings()

		#
		# Attempt to open the file in the selected view. If there isn't a saved
		# file there save it to a temporary location.
		#
		fileToOpen = self.view.file_name()

		if fileToOpen == None:
			#
			# Create a temporary file to hold our contents
			#
			tempFile = tempfile.NamedTemporaryFile(suffix = ".htm", delete = False)

			#
			# Get the contents of the current view
			#
			region = sublime.Region(0, self.view.size())
			text = self.view.substr(region)

			tempFile.write(text)
			tempFile.close()

			fileToOpen = tempFile.name

		# 
		# And open. If the settings file contains a valid selected browser use that
		# command to open this file. Otherwise use the system default.
		#
		print "Opening ", fileToOpen

		if self._browserCommand:
			command = "%s %%s" % self._browserCommand
			print command

			b = webbrowser.get(command.encode())
			b.open_new_tab(fileToOpen.encode())
		else:
			webbrowser.open_new_tab(fileToOpen.encode())

	def _loadSettings(self):
		settingsFile = os.path.normpath("%s/settings.json" % PLUGIN_DIRECTORY)
		self._browserCommand = ""
		
		if os.path.exists(settingsFile):
			jsonData = open(settingsFile)
			self._settings = json.load(jsonData)
			jsonData.close()

			if "selectedBrowser" in self._settings:
				osname = os.name
				platform = sys.platform

				if not self._settings["selectedBrowser"] in self._settings["supportedBrowsers"]:
					raise	Exception("The selected browser '%s' is not supported" % self._settings["selectedBrowser"])

				for env in self._settings["supportedBrowsers"][self._settings["selectedBrowser"]]:
					print "OS name: %s, Platform: %s" % (env["osname"], env["platform"])

					if re.match(env["osname"], osname) and re.match(env["platform"], platform):
						print "Match! %s" % env["command"]
						self._browserCommand = env["command"]

