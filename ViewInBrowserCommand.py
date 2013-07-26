#
# History:
#
# 		07/03/2013:
# 			- Changes to support Sublime Text 3 and Python 3
#
# 		06/15/2013:
# 			- Forward slashes in paths on Windows are now converted prior to opening using local server path
#
# 		03/07/2013:
# 			- Changed loading of settings so that getting shell folders for Windows is only called on a Windows platform
#
# 		01/30/2013:
# 			- Changed to use the sublime-setting tiered loading scheme. This allow users to override
# 			  settings in their own user file in the User directory
#
# 		11/01/2012:
# 			- Altered command to open Safari on Mac
# 			- When invoked the current view is auto-saved
#
# 		10/25/2012:
# 			- New settings.json file to map browser/commands to OSes
# 			- Plugin will use the specified browser to open files, or default to OS default when browser is unsupported
# 			- Addressed encoding issue when calling open_new_tab
# 			- Added ability to specify and respect local server config per project
#
# 		05/21/2012:
# 			- Temp file only created if view is unsaved
#
# 		05/18/2012:
# 			- Initial code
#
import os
import re
import sys
import json
import sublime
import tempfile
import sublime_plugin
import webbrowser

PLUGIN_DIRECTORY = os.getcwd()

class ViewInBrowserCommand(sublime_plugin.TextCommand):
	_settings = None
	_browserCommand = ""
	_windowsFolders = {}

	_pythonVersion = sys.version_info[0]

	def run(self, edit):
		print("Python version {0}".format(self._pythonVersion))

		projectSettings = self.view.settings().get("sublime-view-in-browser")

		#
		# Load settings, if any
		#
		self._loadSettings(self.view)

		#
		# Attempt to open the file in the selected view. If there isn't a saved
		# file there save it to a temporary location.
		#
		fileToOpen = self.view.file_name()

		#
		# If we've specified settings for a local server environment 
		# use them
		#
		if projectSettings:
			fileToOpen = re.sub(r"\\", "/", fileToOpen.replace(projectSettings["basePath"], projectSettings["baseUrl"]))

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
		else:
			#
			# Ensure the current view is saved
			#
			self.view.window().run_command("save")

			
		# 
		# And open. If the settings file contains a valid selected browser use that
		# command to open this file. Otherwise use the system default.
		#
		print("Opening ", fileToOpen)

		if self._browserCommand:
			command = "%s %%s" % self._browserCommand
			print(command)

			if self._pythonVersion < 3:
				b = webbrowser.get(command.encode())
				b.open_new_tab(fileToOpen.encode())
			else:
				b = webbrowser.get(command)
				b.open_new_tab(fileToOpen)

		else:
			if self._pythonVersion < 3:
				webbrowser.open_new_tab(fileToOpen.encode())
			else:
				webbrowser.open_new_tab(fileToOpen)

	def _loadSettings(self, view):
		self._browserCommand = ""
		self._settings = sublime.load_settings("View In Browser.sublime-settings")

		if self._settings:
			if self._settings.has("selectedBrowser"):
				osname = os.name
				platform = sys.platform
				selectedBrowser = self._settings.get("selectedBrowser")
				supportedBrowsers = self._settings.get("supportedBrowsers")

				if not selectedBrowser in supportedBrowsers:
					raise Exception("The selected browser '%s' is not supported" % self._settings["selectedBrowser"])

				for env in supportedBrowsers[selectedBrowser]:
					print("OS name: %s, Platform: %s" % (env["osname"], env["platform"]))

					if type(env["command"]) == list:
						for cmd in env["command"]:
							if os.path.exists(cmd):
								env["command"] = cmd
								break

					if re.match(env["osname"], osname) and re.match(env["platform"], platform):
						print("Match! %s" % env["command"])

						if env["osname"] == "nt":
							self._windowsFolders = self.getUserShellFolders()
							specialFolder = re.sub(r"%([A-Za-z\s]+)%.*", "\\1", env["command"])

							if specialFolder != env["command"]:
								browserCommand = re.sub(r"%[A-Za-z\s]+%(.*)", "%s\\1" % self._windowsFolders[specialFolder], env["command"])
							else:
								browserCommand = env["command"]
							self._browserCommand = re.sub(r"\\", "/", browserCommand)
						else:
							self._browserCommand = env["command"]

	#
	# Thanks to the Python for Windows site for this snippet.
	# http://win32com.goermezer.de/content/view/221/285/
	#
	def getUserShellFolders(self):
		# Routine to grab all the Windows Shell Folder locations from the registry.  If successful, returns dictionary
		# of shell folder locations indexed on Windows keyword for each; otherwise, returns an empty dictionary.
		if self._pythonVersion < 3:
			import _winreg
		else:
			import winreg as _winreg
			
		return_dict = {}

		# First open the registry hive
		try:
			Hive = _winreg.ConnectRegistry(None, _winreg.HKEY_CURRENT_USER)
		except WindowsError:
			print("Can't connect to registry hive HKEY_CURRENT_USER.")
			return return_dict

		# Then open the registry key where Windows stores the Shell Folder locations
		try:
			Key = _winreg.OpenKey(Hive, "Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
		except WindowsError:
			print("Can't open registry key Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders.")
			_winreg.CloseKey(Hive)
			return return_dict

		# Nothing failed above, so enumerate through all the Shell Folder values and return in a dictionary
		# This relies on error at end of 
		try:
			for i in range(0, _winreg.QueryInfoKey(Key)[1]):
				name, value, val_type = _winreg.EnumValue(Key, i)
				return_dict[name] = value
				i += 1
			_winreg.CloseKey(Key)                           # Only use with for loop
			_winreg.CloseKey(Hive)                          # Only use with for loop
			return return_dict                              # Only use with for loop

		except WindowsError:
			# In case of failure before read completed, don't return partial results
			_winreg.CloseKey(Key)
			_winreg.CloseKey(Hive)
			return {}
