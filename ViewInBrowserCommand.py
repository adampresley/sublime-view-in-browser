#
# History:
# 		5/18/2012:
# 			- Initial code
#
import sublime, sublime_plugin
import os, tempfile, webbrowser

class ViewInBrowserCommand(sublime_plugin.TextCommand):
	def run(self, edit):
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

		# 
		# And open.
		#
		print "Opening ", tempFile.name
		webbrowser.open_new_tab(tempFile.name)
