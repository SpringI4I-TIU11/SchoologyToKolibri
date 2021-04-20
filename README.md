# SchoologyToKolibri

Schoology is a course management website that hosts coursework for different schools, teachers, and classes. Kolibri operates in a similar way, but it instead acts an resource that students can download and access offline. The Schoology to Kolibri project's goal was to create a tool that pulls content from a course section in Schoology and import into it a channel(acts as a course in Kolibri) in Kolibri.

The python file, SchoologyKolibriChannel.py, is the main tool of our project. Before this can be run, there are several steps to setting up needed packages and getting required information. 

## Required Software
  * Python 3.7.0 is needed in order to run the package installation. 
    * The download for Python 3.7.0 can be found here: https://www.python.org/downloads/release/python-370/ .
    * If you have a different or higher version of Python already downloaded, Python 3.7 will still be needed. "py -3.7" rather than "python" can be used to specify Python 3.7 when running scripts. An example is shown below: 
   ```
   py -3.7 installs.py
   rather than
   python installs.py
   ```
 The rest of this document will use "py -3.7" as the command since it will always specify Python 3.7. However, if you only have that version of Python downloaded, you can just use "python"
  * Pip is also needed for installing packages.
  * wkhtmltopdf is needed for some file conversions in the tool.
    * The instructions for installation can be found at https://wkhtmltopdf.org/. Here, you can select "Precompiled Binary" and then select your operating system for the exectuable installer.
  * ffmpeg will need to be set up. For ease of use, I have included the files needed in the project. Just in case, the ffmpeg builds can be found at this link: https://github.com/btbn/ffmpeg-builds/releases. 
  * poopler will also need to be set up. For ease of use, I have included the files needed in the project. Just in case, the poppler builds can be found at this link: http://blog.alivate.com.au/poppler-windows/ . 
    * Instructions for how to set up ffmpeg and poppler will be included in the next section.  

## Setting Up Ffmpeg and Poppler
 * Before anything else, the zip file for this repository will need to be downloaded and extracted to a location where you can find it.  
 * Next, ffmpeg and poppler both need to be set up as a Path variable.
 * To do this on Windows, on the bottom left search bar, enter "enviroment variables". An option to "Edit enviroment variables for your account" should appear. Click on this. 
 * You will get this window shown below: 
![Path Variable](https://user-images.githubusercontent.com/79809432/115325854-59c2cf80-a15a-11eb-81ec-f27f185f95e7.png)
 * Click on the user variable in the top section that says "Path" to highlight it.
  * After it is highlighted, select "Edit..." and a wdinow should open:
 ![edit environment variable image](https://user-images.githubusercontent.com/79809432/115325935-7f4fd900-a15a-11eb-8dec-35c614b075e4.png)
  * Once this window is open, go to folder that contains the files from the repository. Select the ffmpeg folder and open it, then open the bin folder. 
   * Once the bin folder is open, grab the path to it by highlighting the top bar as shown in the picture below:
  ![ffmpeg bin path](https://user-images.githubusercontent.com/79809432/115326024-97bff380-a15a-11eb-8ec9-7aa6fc85c0c4.png)
  * Finally, go back to the "Edit environment variable" screen and select new. 
   * Copy the path into the field. 
 ![New path Variable](https://user-images.githubusercontent.com/79809432/115326102-baeaa300-a15a-11eb-95a2-479cd8cd5656.png)
  * Now the same must be done for the poppler bin folder. 
  * Return to the folder containing the files of the repository. Select the poppler folder and open it, then open the bin folder. 
   * Once the bin folder is open, grab the path to it by highlighting the top bar as shown in the picture below:
  * Finally, go back to the "Edit environment variable" screen and select new. 
   * Copy the path into the field. 
 ![New path Variable](https://user-images.githubusercontent.com/79809432/115326124-c4740b00-a15a-11eb-962b-35d2c0f49191.png)
  * Once done, the environment variables should look like this:
  ![Finished Environment Variables](https://user-images.githubusercontent.com/79809432/115326188-e2da0680-a15a-11eb-8272-b2f83fb6cf5d.png)


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
   When the script is eventually run, it will be done using one of these two commands:
    
```
 py -3.7 SchoologyKolibriChannel.py  --token=<your-token>
 or you can store the token in an empty .txt file and use that to run the command.
 py -3.7 SchoologyKolibriChannel.py --token=<file-path-to-.txt-file>
```
       
   The Ricecooker token will ensure that the created channel will be saved to your account.
  
## Installing Packages
  * Python 3.7 and pip are needed to install packages.
  * All of the required packages can be installed by running the installs.py file in command line. Navigate in the directory holding both the installs.py and SchoologyKolibriChannel.py by using the cd command in command line. Run the installs.py file by using this command:
   ```
   py -3.7 installs.py
   ```
 * The installs.py file run multiple pip commands to install all of the required packages for the main tool. 
  
## Running the Tool
After the installation of the packages, everything should be set up to run the tool, SchoologyKolibriChannel.py.
In the command line, you should still be in the program's directory after running the installs.py file. If not, navigate into the directory where SchoologyKolibriChannel.py is stored using the cd command.
The tool can then be run on the command line using one of two commands:
  
    py -3.7 SchoologyKolibriChannel.py  --token=<your-token>
    or if you stored the token in a .txt file, you will run the command below
    py -3.7 SchoologyKolibriChannel.py --token=<file-path-to-.txt-file>
  
During the runtime of the tool, you will be asked to enter the Schoology Consumer Key and Consumer Secret. 
After this, it will ask what course and section you would like to import into Kolibri.
Once those are selected, it will run the tool.
The tool may take some time to run. Links that are being imported into Kolibri can take an especially long time to be imported. 
Oce the tool is finished, you should be able to find the channel in Kolibri Studio. 
