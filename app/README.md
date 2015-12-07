Dashboard Setup
===============

Copyright (C) 2015 CS431. All rights reserved.

1. Getting Started
------------------

- Obtain source

2. Install Web2Executable
-------------------------

  On windows 7+ go to "https://github.com/jyapayne/Web2Executable",
  download and install: 

  	- Windows 7+ installer - v0.2.4b

  	- Create a "release" folder inside of the source directory.

  Run Web2Executable:

  	- Go to the File menu > Open Project (Ctrl+O) and navigate to the 
  	source folder "cs431/app".

  	- Applications settings should automatically be set. If they are not set
  	make sure to enter appropriate settings before exporting. Ensure that the 
  	output directory is set to be the release folder inside "cs431/app".

  	- Under the download settings tab set the download location of your choice.

  	- Export the project. This will generate the dashboard.exe and place it in the folder
  	release/dashboard/windows-x64.


3. Install Inno Setup
---------------------

  On Windows go to "http://www.jrsoftware.org/isdl.php",
  download and install:

  	- ispack-5.5.5.exe installer

  Run Inno Setup Compiler:

  	- Select 'Open an existing script' > 'More Files' and choose the 'setup.iss'
  	script in the source folder.

  	- Click 'run' in order to generate the installer.
  	This will be placed in the "cs431/app/release/dashboard"
  	folder.

4. Run the Dashboard Installer
------------------------------

  - Install the dashboard application

  - Run the application using the desktop shortcut created

  - Test data is provided in the source folder under the "data" folder



Alternative Execution
=====================

1. Download the source
----------------------

  - Follow the sets as above from step 1: "Obtaining the source"

2. Install nw.js
----------------

  - Download and install nw.js from "http://nwjs.io/"

  - Add nw.js to your environment path


3. Run the application
----------------------

  - Open the command window inside the source folder and run 'nw .'


