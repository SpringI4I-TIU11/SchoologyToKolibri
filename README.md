# SchoologyToKolibri

Schoology is a course management website that hosts coursework for different schools, teachers, and classes. Kolibri operates in a similar way, but it instead acts an resource that students can download and access offline. The Schoology to Kolibri project's goal was to create a tool that pulls content from a course section in Schoology and import into it a channel(acts as a course in Kolibri) in Kolibri.

The python file, SchoologyKolibriChannel.py, is the main tool of our project. Before this can be run, there are several steps to setting up needed packages and getting required information. 

## Required Software
  * Python 3.7.0 is needed in order to run the package installation. 
   * The download for Python 3.7.0 cna be found here: https://www.python.org/downloads/release/python-370/ .
  * Pip is also needed for installing packages.
  * wkhtmltopdf is needed for some file conversions in the tool.
    * The instructions for installation can be found at https://wkhtmltopdf.org/.

## Required Keys and Tokens:
  Using the tool requires the use of two keys for Schoology's API and a token for Kolibri's API.
  
  The Schoology API keys can be found at https://app.schoology.com/api. 
  Accessing this site requires a Schoology account. Also, our tool will not be of any use if the acccount is not apart of any courses.
  Once the site is accessed, two tokens will be found:
   * Current Consumer Key
   * Current Consumer Secret
  These tokens will be entered into the tool during runtime. 
  
  The Kolibri/Ricecooker API token will also be needed:
    A Kolibri Studio account is needed to get the API token. 
    The token can be found at https://studio.learningequality.org/ in the settings. 
    This token is used in the command line to run the script, and it can be done in two different ways.
    Run this script on the command line using:
    
       ```
        python SchoologyKolibriChannel.py  --token=<your-token>
        or you can store the token in an empty .txt file and use that to run the command.
        python SchoologyKolibriChannel.py --token=<file-path-to-.txt-file>
       ```
       
   The Ricecooker token will ensure that the created channel will be saved to your account.
  
## Installing Packages
  * Python 3.7 and pip are needed to install packages.
  * All of the required packages can be installed by running the installs.py file in command line. Navigate in the directory holding both the installs.py and SchoologyKolibriChannel.py by using the cd command in command line. Run the installs.py file by using this command:
   ```
   python installs.py
   ```
 * The installs.py file run multiple pip commands to install all of the required packages for the main tool. 
  
## Running the Tool
After the installation of the packages, everything should be set up to run the tool, SchoologyKolibriChannel.py.
In the command line, you should still be in the program's directory after running the installs.py file. If not, navigate into the directory where SchoologyKolibriChannel.py is stored using the cd command.
The tool can then be run on the command line using one of two commands:
  
    python SchoologyKolibriChannel.py  --token=<your-token>
    or if you stored the token in a .txt file, you will run the command below
    python SchoologyKolibriChannel.py --token=<file-path-to-.txt-file>
  
During the runtime of the tool, you will be asked to enter the Schoology Consumer Key and Consumer Secret. 
After this, it will ask what course and section you would like to import into Kolibri.
Once those are selected, it will run the tool.
The tool may take some time to run. Links that are being imported into Kolibri can take an especially long time to be imported. 
Oce the tool is finished, you should be able to find the channel in Kolibri Studio. 
