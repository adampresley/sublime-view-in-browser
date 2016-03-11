#
# History:
#
# 		03/11/2016:
# 			- Fix issue where parenthesis in paths would cause a failure to load. Solves #52
#
# 		10/06/2014:
# 			- Rewrite for version 2.0.0
# 			- Using subprocess instead of webbrowser. Seems to solve #19
# 			- Smaller, simplier sublime-settings file
#
# 		05/15/2014:
# 			- Current view only saves if there are modifications
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
import sys
import re
import json
import urllib
import sublime
import tempfile
import subprocess
import sublime_plugin
import webbrowser

PLUGIN_VERSION = "2.0.0"

class ViewInBrowserCommand(sublime_plugin.TextCommand):
	_pythonVersion = sys.version_info[0]

	#
	# Takes a Windows variable, such as %APPDATA% and get the
	# proper path.
	#
	def expandWindowsUserShellFolder(self, command):
		browserCommand = ""

		windowsFolders = self.getWindowsUserShellFolders()
		specialFolder = re.sub(r"%([A-Za-z\s]+)%.*", "\\1", command)

		if specialFolder != command:
			expandedFolder = windowsFolders[specialFolder].replace("\\", "\\\\")
			browserCommand = re.sub(r"%[A-Za-z\s]+%(.*)", "%s\\1" % expandedFolder, command)
		else:
			browserCommand = command

		return browserCommand.encode("ascii", "ignore") if self._pythonVersion < 3 else browserCommand

	#
	# Returns the correct base command.
	#
	def getBaseCommand(self, command, osName):
		baseCommand = command

		if osName == "nt":
			baseCommand = self.expandWindowsUserShellFolder(baseCommand)

		return baseCommand

	#
	# Return the name of the running operating system.
	# i.e. darwin, nt, linux
	#
	def getOsName(self):
		return os.name

	#
	# Get the current running platform. i.e.
	# posix, win32
	#
	def getPlatform(self):
		return sys.platform

	#
	# Thanks to the Python for Windows site for this snippet.
	# http://win32com.goermezer.de/content/view/221/285/
	#
	def getWindowsUserShellFolders(self):
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
				return_dict[name] = value.encode("ascii")
				i += 1
			_winreg.CloseKey(Key)                           # Only use with for loop
			_winreg.CloseKey(Hive)                          # Only use with for loop
			return return_dict                              # Only use with for loop

		except WindowsError:
			# In case of failure before read completed, don't return partial results
			_winreg.CloseKey(Key)
			_winreg.CloseKey(Hive)
			return {}

	def giveFileAProjectPath(self, fileToOpen, basePath, baseUrl):
		return re.sub(r"\\", "/", fileToOpen.replace(basePath, baseUrl)).replace(" ", "%20").replace("(", "%28").replace(")", "%29")

	def loadPluginSettings(self, defaultBrowser):
		result = {
			"browser": "",
			"baseCommand": ""
		}

		#
		# Load default/user settings. The browser choice may
		# be overridden by custom commands.
		#
		settings = sublime.load_settings("View In Browser.sublime-settings")

		if not defaultBrowser:
			result["browser"] = settings.get("browser")
		else:
			result["browser"] = defaultBrowser

		#
		# Get the correct command based on platform and OS
		#
		osName = self.getOsName()
		platform = self.getPlatform()

		selectedOs = settings.get(osName)
		result["baseCommand"] = self.getBaseCommand(selectedOs[platform][result["browser"]], osName)

		return result

	def loadProjectSettings(self, view):
		return view.settings().get("sublime-view-in-browser")

	def normalizePath(self, fileToOpen):
		fileToOpen = fileToOpen.replace("\\", "/")
		fileToOpen = "file:///%s" % fileToOpen.replace(" ", "%20").replace("(", "%28").replace(")", "%29")

		return fileToOpen

	def openBrowser(self, command, osName):
		useShell = False if osName != "posix" else True
		subprocess.Popen(command, shell=useShell)

	def run(self, edit, browser=None):
		print("View In Browser plugin v{0}, Python {1}".format(PLUGIN_VERSION, self._pythonVersion))

		#
		# Load plugin settings and project settings, if any. A project settings may
		# affect the file to open based on local server
		# environment settings.
		#
		pluginSettings = self.loadPluginSettings(browser)
		projectSettings = self.loadProjectSettings(self.view)

		fileToOpen = self.view.file_name()

		#
		# If we've specified settings for a local server environment
		# use them
		#
		if projectSettings:
			fileToOpen = self.giveFileAProjectPath(fileToOpen, projectSettings["basePath"], projectSettings["baseUrl"])

		#
		# If the current view has not been saved, put it into
		# a temp file and open that instead. If the view
		# DOES have a name make sure it is save before
		# opening.
		#
		if fileToOpen == None:
			fileToOpen = self.normalizePath(self.saveCurrentViewInTempFile(self.view))

		else:
			if self.view.is_dirty():
				print("File %s is dirty. Saving..." % (fileToOpen,))
				self.view.window().run_command("save")

			if not projectSettings:
				fileToOpen = self.normalizePath(fileToOpen)

		#
		# And open. If the settings file contains a valid selected browser use that
		# command to open this file. Otherwise use the system default.
		#
		if pluginSettings["baseCommand"]:
			command = "%s %s" % (pluginSettings["baseCommand"], fileToOpen.decode().encode(sys.getfilesystemencoding()) if self._pythonVersion < 3 else fileToOpen,)

			print(command)
			self.openBrowser(command, self.getOsName())

		else:
			if self._pythonVersion < 3:
				webbrowser.open_new_tab(fileToOpen.encode(sys.getfilesystemencoding()))
			else:
				webbrowser.open_new_tab(fileToOpen)

	def saveCurrentViewInTempFile(self, view):
		#
		# Create a temporary file to hold our contents
		#
		tempFile = tempfile.NamedTemporaryFile(suffix = ".htm", delete = False)

		#
		# Get the contents of the current view
		#
		region = sublime.Region(0, view.size())
		text = view.substr(region)

		tempFile.write(text.encode("utf-8"))
		tempFile.close()

		return tempFile.name
