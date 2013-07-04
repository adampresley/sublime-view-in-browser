# Sublime Text - View In Browser

*<a href="http://adampresley.github.io/sublime-view-in-browser/">View In Browser</a>* is a Sublime Text plugin that will open whatever is in your
current view/tab. If the file current open is new and has not been saved a temporary 
file is created (in your default temp directory for your OS) with the extension of 
**.htm** and your browser will open it. However if the current open file is saved
and has a name this plugin will open it in whatever you have set to handle
its type.

By default the keystroke assigned to this plugin is *CTRL + ALT + V*.

## Installation
Using the Sublime Text Package Control plugin (http://wbond.net/sublime_packages/package_control)
press *CTRL + SHIFT + P* and find **Package Control: Install Package** and press *Enter*.
Find this plugin in the list by name **View In Browser**.

## Configuring Browsers
By default this plugin will open files in Firefox. You can configure it to open
using another browser of your choice. To do this, choose *Settings - User* from *Preferences > Package Settings > View In Browser*.

The browser you wish to use to open files is set in the key named **selectedBrowser**. The list of browsers
you can use and configure are in the key named **supportedBrowsers**.

The **supportedBrowsers** values can be configured to have paths to your browser installations.
Each browser listed is an array (list) of configurations that allow you to setup a browser
for multiple operating systems. For example under *chrome* there are two configurations.
The first is for your average Linux system. The second is for Windows. 

### Windows Considerations
One of the things you may notice in the Windows configuration for *chrome* is a variable in
the command path that looks like: **%Local AppData%**. This is a reference to your Windows
installation's **AppData** folder in your user profile directory. There is a variable
there because this value will differ for each user on your computer, and Chrome installs
to your **AppData** folder.

Here is a list of supported variables:

* **AppData** - Your main application data folder for your profile (usually roaming)
* **Personal** - Your documents location
* **Desktop** - The path to your Desktop location (may be unreliable)
* **Start Menu** - The path to your Start Menu items location
* **Local AppData** - Your local application data folder for your profile
* **My Video** - Path to your videos location
* **My Pictures** - Path to your pictures location
* **My Music** - Path to your music location

Note that many of these are not terribly useful for determining browser location, unless you
have decided to install Firefox in your My Music folder. 


## Configure to View on Local Server
The View In Browser plugin also supports the ability to view files in the context of
a local server. So if you have a local Apache, Tomcat, or some other server application running
you can configure this plugin to open your file prefixed with a URL. 

To configure this the View In Browser plugin reads the configuration of your currently
loaded project. You can edit a project file by opening the *sublime-project* file
by choosing **Project** -> **Edit Project**. In your project file you will need to specify 
two things:

* **baseUrl** - The root URL to prefix files with 
* **basePath** - The base path where your site/application lives

Here's how that looks.

```javascript
{
	"folders":
	[
		{
			"path": "/home/<username>/code/python/my-cool-website"
		}
	],
	"settings": {
		"sublime-view-in-browser": {
			"baseUrl": "http://localhost:8080",
			"basePath": "/home/<username>/code/python/my-cool-website"
		}
	}
}
```

Notice the key named **settings** which is a dictionary that contains another key named
**sublime-view-in-browser**. This is where you will put your **baseUrl** and **basePath**
settings.

Now when you activate View In Browser your file will open with the HTTP protocol instead
of the FILE protocol.

## Change History

* 07/03/2013:
   * Changes to support Sublime Text 3 and Python 3
* 06/15/2013:
   * Backslashes in Windows are now converted to forward slashes when using
     a local server configuration. Closes <a href="https://github.com/adampresley/sublime-view-in-browser/issues/16">#16</a>
* 04/16/2013:
   * Added support for muliple paths per browser configuration (jadient 
     <a href="https://github.com/adampresley/sublime-view-in-browser/pull/14">#14</a>)
* 03/08/2013:
   * Avoid loading Windows special folder references when on a Mac
   * Added Mac Chrome to the supported browsers list
* 02/18/2013:
   * Added ability to use Windows special folder references to browser commands. Closes 
     <a href="https://github.com/adampresley/sublime-view-in-browser/issues/10">#10</a>
* 01/30/2013:
   * All settings for this plugin now live in the file **View In Browser.sublime-settings**.
     This allows for a user to override them in their *User* directory. The old 
     **settings.json** file is no longer used. 
* 01/28/2013:
   * Merged in change from imaginationac to remove menu nesting
* 12/26/2012:
   * Added Linux Chromium to the supported browsers list
* 11/01/2012:
   * Altered command to open Safari on Mac
   * When invoked the current view is auto-saved
* 10/25/2012:
   * New settings.json file to map browser/commands to OSes
   * Plugin will use the specified browser to open files, or default to OS default when browser is unsupported
   * Addressed encoding issue when calling open_new_tab
   * Added ability to specify and respect local server config per project
* 05/21/2012:
   * Temp file only created if view is unsaved
* 05/18/2012:
   * Initial code

## Contributors
* Dorian Patterson - <a href="https://github.com/imaginationac">imaginationac</a>
* Neil Freeman - <a href="https://github.com/fitnr">fitnr</a>
* Michael MacDonald - <a href="https://github.com/schlick">schlick</a>
* Jadient - <a href="https://github.com/jadient">jadient</a>

## License
The MIT License (MIT)
Copyright (c) 2012 Adam Presley

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
IN THE SOFTWARE.
