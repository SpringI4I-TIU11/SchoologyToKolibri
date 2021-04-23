"""
Import tool that takes resources from a Schoology section and 
    uses them to a Kolibri Channel. Schoology and Kolibri accounts 
    will be needed to run this tool.
Using the tool requires access to a Schoology site and the API tokens.
The API tokens can be found at https://app.schoology.com/api.
The two tokens needed are:
    - Current Consumer Key
    - Current Consumer Secret
These will be entered when running the tool. 
    
The Kolibri/Ricecooker API token will also be needed:
This can be found at https://studio.learningequality.org/ in the settings. 
This token is used in the command line to run the script, and itcan be done in two different ways.
Run this script on the command line using:
    python SchoologyKolibriChannel.py  --token=<your-token>
    or you can store the token in an empty .txt file and use that to run the command.
    python SchoologyKolibriChannel.py --token=<file-path-to-.txt-file>
    
The Ricecooker token will ensure that the created channel will be saved to your account.
"""
import sys
import requests
import json
from requests_oauthlib import OAuth1
from pprint import pprint

#Regular Expressio Import
import re

#Prasing YouTube URL for ID
import urllib

from urllib.parse import urlparse # if we're pre-2.6, this will not include parse_qs

try:
    from urlparse import parse_qs
except ImportError: # old version, grab it from cgi
    import cgi
    urlparse.parse_qs = cgi.parse_qs


#Making Link Node from URL
#import tempfile
import os

import shutil
from ricecooker.utils.downloader import download_static_assets
from ricecooker.utils.html import download_file
import time

#Convert svg to png
#There were issues with this converter. Commenting for now. 
#import cairosvg

#Converting URL to PDF
    #Involves other installs
import pdfkit

#!/usr/bin/env python
from le_utils.constants import licenses, exercises
from le_utils.constants.languages import getlang

from ricecooker.chefs import SushiChef
from ricecooker.classes.nodes import DocumentNode, AudioNode, VideoNode, HTML5AppNode, TopicNode
from ricecooker.classes.files import DocumentFile, AudioFile, WebVideoFile, VideoFile, YouTubeVideoFile, YouTubeSubtitleFile, HTMLZipFile
from ricecooker.classes.licenses import get_license

import copy
from slugify import slugify

#Web Scraper Libraries
from ricecooker.utils.html_writer import HTMLWriter
import bs4

from urllib.parse import urljoin
    
#For deleting files are they are imported into Kolibri
filesCreated = []    

#SCHOOLOGY API CONSUMER KEY AND SECRET

#Set as global varibales to be accessed in functions
print("To get your course material from Schoology, two codes are needed that can be found at https://app.schoology.com/api.")
print("Visit this site, and enter the codes in the designated section below.")
print("Please enter your current consumer key: ")
consumerKey = input()
print("Please enter your current consumer secret: ")
consumerSecret = input()

#Authentication to make the requests
auth = OAuth1(consumerKey,consumerSecret,"","")

#END SCHOOLOGY TOKEN BLOCK

#GETTING COURSE AND SECTION ID

#APi to get user info
url = "https://api.schoology.com/v1/app-user-info"
response = requests.get(url, auth=auth)
data = response.json()

userID = data['api_uid']

#API call using user id to get section ids
url = "https://api.schoology.com/v1/users/" + str(userID) + "/sections"
response = requests.get(url, auth=auth)
data = response.json()

courses = {}
sections = {}

print("\n")

#Store all section ids and course ids
for section in data['section']:
    courseID = section['course_id']
    sectionID = section['id']

    #If a course id found is not already in courses dictionary, add it
    if courseID not in courses:
        courses[courseID] = section['course_title']
    #If a section id found is not already in sections dictionary, add it
    if sectionID not in sections:
        sections[sectionID] = section['section_title']
        
i = 0
for key, value in courses.items():
    i += 1
    print(str(i) + "\tCourse ID: " + key + "\tCourse Title: " + value)
print()

#User chooses a course 
courseSelect = int(input('Which COURSE would you like to import into Kolibri? \nSelect by using the number on the left\n'))

#Store course id
courseKeys = list(courses)
courseID = courseKeys[i - 1]

print()

i = 0
for key, value in sections.items():
    i += 1
    print(str(i) + "\tSection ID: " + key + "\tSection Title: " + value)
print()

#User chooses a section
sectionSelect = int(input('Which SECTION would you like to import into Kolibri? \nSelect by using the number on the left\n'))

#Store section id
sectionKeys = list(sections)
sectionID = sectionKeys[i - 1]
#COURSE AND SECTION ID SAVED



#LINK NODE CODE STARTS HERE
#Variables used in Link Node Function
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0",
    "Accept-Encoding": "gzip, deflate, utf-8",
    "Connection": "keep-alive"
}

url_blacklist = {}

sess = requests.Session()

zipId = 1

#Used in Link Node function
def make_request(url, headers=headers, timeout=60, *args, **kwargs):
    retry_count = 0
    max_retries = 5
    while True:
        try:
            response = sess.get(url, headers=headers, timeout=timeout, *args, **kwargs)
            break
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
            retry_count += 1
            print("Error with connection ('{msg}'); about to perform retry {count} of {trymax}."
                  .format(msg=str(e), count=retry_count, trymax=max_retries))
            time.sleep(retry_count * 1)
            if retry_count >= max_retries:
                return Dummy404ResponseObject(url=url)

    if response.status_code != 200:
        print("NOT FOUND:", url)

    return response

#Current Link Node Function
    #Issues with not downloading some images and styles...
def linkAssignment(linkData):
    #Get URL and Title from JSON info
    url = linkData['attachments']['links']['link'][0]['url']
    title = linkData['attachments']['links']['link'][0]['title']
    
    #Make session and request to get HTML
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    html = session.get(url).content
    
    #HTML parser
    soup = bs4.BeautifulSoup(html, "html.parser")

    #Path for folder to hold content
    global zipId
    filename = 'myzipper' + str(zipId)
    print("\n\n\n" + filename + "\n\n\n")
    zipId = zipId + 1
    
    #Delete folder if it already exists
    if(os.path.exists(filename)):
       shutil.rmtree(filename)
       #os.unlink(filename)

    #Download all assets(html, css, js,...) from url
    doc = download_static_assets(soup, filename,
            url, request_fn=make_request,
            url_blacklist=url_blacklist)
    
    # Write out the HTML source.
    with open(os.path.join(filename, "index.html"), "w", encoding="utf-8") as f:
        f.write(str(doc))

    #Outputs files being downloaded
    print("        ... downloaded to %s" % filename)
    
    filesCreated.append(filename)
    
    #Make zip file from folder contents
    shutil.make_archive(filename, 'zip', filename)
    
    filesCreated.append(filename + '.zip')
    
    #Creation of file and node
    link_file = HTMLZipFile(path = (filename + '.zip'))
    link_node = HTML5AppNode(
        source_id = url,
        title = title,
        license = get_license(licenses.CC_BY, copyright_holder='Copyright holder name'),
        language = getlang('en').id,
        derive_thumbnail = False,
        thumbnail = None,
        files=[link_file]
    )
    return link_node

#LINK NODE CODE ENDS HERE


#YOUTUBE VIDEO CODE STARTS HERE
#Create a Video Node from YouTube URL - FINISHED
def youtubeNode(url):
    #Picking out youtube video ID from URL
    url_data = urlparse(url)
    query = urlparse.parse_qs(url_data.query)
    videoID = query["v"][0]
    
    r = requests.get(url).text # grabs request of the URL
    
    #Get video title
    bs = bs4.BeautifulSoup(r, "html.parser")
    videoTitle = bs.find_all('title', limit=1)
    
    #videoTitle includes html tags, stripping them
    newTitle = str(re.sub('<.*?>', '', str(videoTitle)))
    
    #May have to delete if there are brackets in title
    newTitle = newTitle.replace("]", '')
    newTitle = newTitle.replace("[", '')
    
    #Create Video Node
    video_node = VideoNode(
        source_id= videoID,  # usually set source_id to youtube_id
        title = str(newTitle),
        license=get_license(licenses.CC_BY, copyright_holder='Copyright holder name'),
        language=getlang('en').id,
        derive_thumbnail=True,  # video-specicig flag
        thumbnail=None,
        files=[
                YouTubeVideoFile(youtube_id=videoID, high_resolution=False, language='en'),
                YouTubeSubtitleFile(youtube_id=videoID, language='en')
            ]
    )
    
    #Return Video Node
    return video_node

def vimeoNode(url):
    r = requests.get(url).text # grabs request of the URL
    
    #Get video title
    bs = bs4.BeautifulSoup(r, "html.parser")
    videoTitle = bs.find_all('title', limit=1)
                 
    #videoTitle includes html tags, stripping them
    newTitle = str(re.sub('<.*?>', '', str(videoTitle)))
    
    #May have to delete if there are brackets in title
    newTitle = newTitle.replace("]", '')
    newTitle = newTitle.replace("[", '')
    
    
    #Create Video Node
    video_node = VideoNode(
        source_id= url,  # set to url
        title = str(newTitle),
        license=get_license(licenses.CC_BY, copyright_holder='Copyright holder name'),
        language=getlang('en').id,
        derive_thumbnail=True,  # video-specicig flag
        thumbnail=None,
        files=[
                WebVideoFile(web_url = url, language='en'),
            ]
    )
    
    #Return Video Node
    return video_node
#YOUTUBE VIDEO CODE END HERE

#GOOGLE PDF NODE CODE STARTS HERE

def checkIfDownloadNeededFromPage(body):
    download = re.findall("\".*docs.google.com.*\"", body)
    if download:
        link = download[0].split(' ')[0]
        if (link.find('document') != -1):
            type = 'document'
        elif(link.find('presentation') != -1):
            type = 'presentation'
        elif(link.find('spreadsheets') != -1):
            type = 'spreadsheets'
        
        #Get id from link
        id = re.findall("/d/.*/", link)[0].split('/d/')[1]
        
        return [id, type]
    else:
        return None
    
#Downloads Google Slides as pdf
def downloadPowerpoint(id):
    """Accepts a string ID. Reads byte data from request content and writes into PDF"""
    url = "https://docs.google.com/presentation/d/{}/export/pdf".format(id)
    req = requests.get(url)
    fileName = re.findall("filename=.*;", req.headers['content-disposition'])[0].split("\"")[1]
    with open(fileName, 'wb') as f:
        f.write(req.content)
        
    #Issue where pdfs are being downloaded as HTML documents
        #This ensures it is a pdf file type
    if(fileName.find('.html') != -1):
        filesCreated.append(fileName)
        
        #Get filename without extension and replace with'.pdf'
        pdfName = os.path.splitext(fileName)[0] + '.pdf'
        print(pdfName)

        #pdfName = pdfkit.from_file(fileName, False)
        
        print("\nHTML found instead of PDF.\nConverting to PDF using pdfkit...")
        
        #INFO: Could not find files for the given pattern(s).
            #wkhtmltopdf install needed
            #I would prefer to find a different way, or figure out why it is downloading as html, but this will do for now
        pdfkit.from_file(fileName, pdfName)
        
        print("PDF Conversion Complete")
        
        fileName = pdfName
        
    filesCreated.append(fileName)
    
    return fileName

#Downloads Google Doc as pdf
def downloadDocument(id):
    """Accepts a string ID. Reads byte data from request content and writes into PDF"""
    url = "https://docs.google.com/document/d/{}/export/pdf".format(id)
    req = requests.get(url)
    fileName = re.findall("filename=.*;", req.headers['content-disposition'])[0].split("\"")[1]
    with open(fileName, 'wb') as f:
        f.write(req.content)
        
    #Issue where pdfs are being downloaded as HTML documents
        #This ensures it is a pdf file type
    if(fileName.find('.html') != -1):
        filesCreated.append(fileName)
        
        #Get filename without extension and replace with'.pdf'
        pdfName = os.path.splitext(fileName)[0] + '.pdf'
        print(pdfName)

        #pdfName = pdfkit.from_file(fileName, False)
        
        print("\nHTML found instead of PDF.\nConverting to PDF using pdfkit...")
        
        #INFO: Could not find files for the given pattern(s).
            #wkhtmltopdf install needed
            #I would prefer to find a different way, or figure out why it is downloading as html, but this will do for now
        pdfkit.from_file(fileName, pdfName)
        
        print("PDF Conversion Complete")
        
        fileName = pdfName
        
    filesCreated.append(fileName)
    return fileName

def downloadSpreadsheet(id):
    #https://docs.google.com/spreadsheets/d/{}/export?format=pdf
    """Accepts a string ID. Reads byte data from request content and writes into PDF"""
    url = "https://docs.google.com/spreadsheets/d/{}/export?format=pdf".format(id)
    req = requests.get(url)
    fileName = re.findall("filename=.*;", req.headers['content-disposition'])[0].split("\"")[1]
    with open(fileName, 'wb') as f:
        f.write(req.content)
        
    #Issue where pdfs are being downloaded as HTML documents
        #This ensures it is a pdf file type
    if(fileName.find('.html') != -1):
        filesCreated.append(fileName)
        
        #Get filename without extension and replace with'.pdf'
        pdfName = os.path.splitext(fileName)[0] + '.pdf'
        print(pdfName)
        
        print("\nHTML found instead of PDF.\nConverting to PDF using pdfkit...")
        
        #INFO: Could not find files for the given pattern(s).
            #wkhtmltopdf install needed
            #I would prefer to find a different way, or figure out why it is downloading as html, but this will do for now
        pdfkit.from_file(fileName, pdfName)
        
        print("PDF Conversion Complete")
        
        fileName = pdfName
        
    filesCreated.append(fileName)
    return fileName


def googleNode(url):
    #Get doc id
    id = getIdFromUrl(url)

    #Call proper google download function
    if(url.find('document') != -1):
        print("Found Document")
        #Uses download function to get pdf of document, returns filename
        fileName = downloadDocument(id)
    elif(url.find('presentation') != -1):
        print("Found Presentation")
        #Uses download function to get pdf of powerpoint, returns filename
        fileName = downloadPowerpoint(id)
    elif(url.find('spreadsheets') != -1):
        print("Found Spreadsheet")
        fileName = downloadSpreadsheet(id)
    
    #Use download and filename to create node
    googleNode = DocumentNode(
        source_id=id,
        title = fileName,
        language="en",
        description="",
        license=get_license(licenses.CC_BY, copyright_holder='Copyright holder name'),
        files=[
            DocumentFile(
                path=fileName,
                language="en",
            )
        ],
    )
    return googleNode
#GOOGLE PDF NODE CODE ENDS HERE

#DOCUMENT PDF NODE STARTS HERE
pdfCopy = 1
def pdfNode(infoDict):
    #Get response from converted-to-pdf path
    response = requests.get(infoDict['pdfPath'], auth=auth)
    
    global pdfCopy
    if os.path.exists(infoDict['pdfTitle']):
        infoDict['pdfTitle'] = infoDict['pdfTitle'].replace(".pdf", str(pdfCopy) + ".pdf")
        pdfCopy += 1
        
    #Write pdf to local file
    with open(infoDict['pdfTitle'], 'wb') as f:
        f.write(response.content)
        
    filesCreated.append(infoDict['pdfTitle'])
        
    #Create Document Node
    pdfNode = DocumentNode(
        source_id= str(infoDict['id']),
        title = infoDict['pdfTitle'],
        language="en",
        description="",
        license=get_license(licenses.CC_BY, copyright_holder='Copyright holder name'),
        files=[
            DocumentFile(
                path=infoDict['pdfTitle'],
                language="en",
            )
        ],
    )
    return pdfNode
    
#DOCUMENT PDF NODE ENDS HERE


#NON-NODE FUNCTIONS BELOW
#GET GOOGLE DOC ID
def getIdFromUrl(url):
    x = re.search(r"/[-\w]{25,}/", url)
    id = x.group().replace("/", '')
    return id

#FIND ITEM IN ARRAY
def inArray(arr, item):
    for obj in arr:
        if item == obj:
            return True
    return False


#WORKER FUNCTION
    #Using the Schoology location, it returns the proper node for the file/link
def getNodeFromLocation(loc):
    response = requests.get(loc, auth=auth)
    data = response.json()
    
    #Found attachments attribute in JSON (Could be link, video, google file...)
    if 'attachments' in data:
        
        #Check for links
        if 'links' in data['attachments']:
            #Store link
            innerData = data['attachments']['links']['link'][0]
            print("Link - Title:" + innerData['title'] + "\tURL:" + innerData['url'])
            urlString = str(innerData['url'])
            
            #If link to Google File, then handle and download Google File
            if(urlString.find('docs.google.com') != -1):
                print("Downloading Google File...")
                try:
                    return googleNode(urlString)
                    print("Google File:" + urlString)
                except:
                    print("Error when Downloading Google File")
            
            #Not Google File, download as linkNode
            else:
                print("Link Node Reached")
                #Link Assignment creation is very slow, comment out to test other things
                    #Could add pdf creation in case WebApp is bad
                return linkAssignment(data)
        
        #Video found in attachments
        elif 'videos' in data['attachments']:
            #Currently handles only Youtube videos
            innerData = data['attachments']['videos']['video'][0]
            print("Video - Title:" + innerData['title'])
            urlString = str(innerData['url'])
            
            if 'youtube' in urlString:
                return youtubeNode(urlString)
            elif 'vimeo' in urlString:
                return vimeoNode(urlString)
            else:
                print("Error: Video source not supported")
            
            #Url -> YouTubeNode
            return youtubeNode(urlString)
        
        #File found in attachments
        elif 'files' in data['attachments']:
            fileInfo = {}
            fileInfo['id'] = data['id']
            fileInfo['pdfPath'] = data['attachments']['files']['file'][0]['converted_download_path']
            fileInfo['pdfTitle'] = data['attachments']['files']['file'][0]['converted_filename']
            return pdfNode(fileInfo)
            
    else:
        #Sometimes, URL for Google Docs/Slides is stored in a different call
            #This checks that call to make sure these Docs/Slides aren't skipped
        loc = loc.replace("page", "pages")
        response = requests.get(loc, auth=auth)
        data = response.json()
        
        #Checks for Google File, and returns type of Google File and id
            #If no Google File found, returns None
        valueArray = checkIfDownloadNeededFromPage(data['body'])
        if(valueArray != None):
            id = valueArray[0]
            type = valueArray[1]
            url = "https://docs.google.com/{}/d/{}/export/pdf".format(type, id)
            return googleNode(url)
#END OF WORKER FUNCTION
                    
    
#CHANNEL CREATION BEGINS HERE
class SimpleChef(SushiChef):
    #Variables for Channel Creation
        #Finding channel title, thumbnail, description, etc'
    url = "https://api.schoology.com/v1/sections/" + sectionID
    
    response = requests.get(url, auth=auth)
    sectionData = response.json()

    #Getting info from JSON
    courseTitle = sectionData['course_title']
    courseID = sectionData['course_id']
    sectionTitle = sectionData['section_title']
    imageURL = sectionData['profile_url']
    description = sectionData['description']
    
    #Channel title is combination fo course and section title
    channelTitle = courseTitle + ": " + sectionTitle
    
    #Getting thumbnail
        #Can be jpg, jpeg, png
    filename, file_extension = os.path.splitext(imageURL)
    
    thumbnail = "output" + file_extension
    
    #If image is an svg, convert to png
    if file_extension == '.svg':
        thumbnail = 'DefaultThumbnail.jpg'
        
        """
        #There were issues with the svg converter, cairosvg.
        #Instead, if the photo is an svg, it will refer to a default image.
        thumbnail = "output.png"
        outputSVG = 'output.svg'
        
        filesCreated.append(thumbnail)
        filesCreated.append(outputSVG)
        
        urllib.request.urlretrieve(imageURL, outputSVG)
        cairosvg.svg2png(url=outputSVG, write_to=thumbnail)
        """
        
    else:
        thumbnail = "output" + file_extension
        filesCreated.append(thumbnail)
        urllib.request.urlretrieve(imageURL, thumbnail)

    channel_info = {
        "CHANNEL_TITLE": channelTitle,
        "CHANNEL_SOURCE_DOMAIN": "Schoology",  # where content comes from
        "CHANNEL_SOURCE_ID": "TIU11",  # CHANGE ME!!!
        "CHANNEL_LANGUAGE": "en",  # le_utils language code
        "CHANNEL_THUMBNAIL": thumbnail,  # (optional)
        "CHANNEL_DESCRIPTION": description,  # (optional)
    }

    def construct_channel(self, **kwargs):
        channel = self.get_channel(**kwargs)
        
        sys.setrecursionlimit(10**6)
        
        #URL to get all folders in the section
        url = "https://api.schoology.com/v1/sections/" + sectionID + "/folders/0"

        # Create API request to schoology root course folder with OAuth credentials. Store json response
        response = requests.get(url, auth=auth)

        data = response.json()

        folderDict = {}
        
        #Create root node in folderDict
        folderDict[0] = []
        
        #Populate root node because the API call is handled differently than other folders
        url = "https://api.schoology.com/v1/courses/" + sectionID + "/folder/0"
        response = requests.get(url, auth=auth)
        rootData = response.json()
        for child in rootData['folder-item']:
            #Folders and their parents are handled next along with other child files
            if child['type'] != 'folder':
                folderDict[0].append(child['location'])

        #Put IDs of folders as keys in folderDict, empty arrays for value 
        for folder in data['folders']:
            folderDict[folder['id']] = []
            
            #If the parent of the folder is the root node, add it to the root
            if folder['parent_id'] == '0':
                #When a folder is found, it adds a list to the dictionary with the folder's id and the topic node associated with the folder
                folderDict[0].append([folder['id'], TopicNode(title=folder['title'], source_id=str(folder['id']))])
            
            #Call the folder's location to get the files in it
            folderUrl = folder['location']
            response = requests.get(folderUrl, auth=auth)
            
            #Contains the data for the folder, including info for the files in it
            folderData = response.json()
        
            #get the folder-itme out of data (references the object holding the files in the folder...
                #... there are self-references and other references in the JSON)
            if 'folder-item' in folderData:
                #Loop through children of folder
                for child in folderData['folder-item']:
                    #If the child is a folder, add list into dictionary value array with id and TopicNode
                    if child['type'] == 'folder':
                        folderDict[folder['id']].append( [child['id'], TopicNode(title=child['title'], source_id=str(child['id']))] )
                    #I fthe child is not a folder, add the location of the file dictionary value array
                    else:
                        folderDict[folder['id']].append(child['location'])
        
        #Used to recognize when break statements need to be hit
        parentFound = False
        
        #Search through dictionary keys and values
        for key, value in folderDict.items():
            print("Looking for Folders/Files")
            
            #Search through the value list
            for item in value:            
                #If child is folder/TopicNode
                if type(item) is list:
                    #List found, means stored data is for a folder
                    
                    #Save parent id (need to find the actual topic node, only have id)
                    parentID = key
                    
                    #Folder to be added to the parent topic node
                    itemToAdd = item[1]
                    print("\t\tFound a Child Folder")
                                #Not a list, it is a file, will be put into node
                else:
                    print("\t\tFound a File")
                    #Save parent id (need to find the actual topic node, only have id)
                    parentID = key
                    
                    #Node to be added to the parent topic node
                    itemToAdd = getNodeFromLocation(item)
                    
                print("Searching for Parent Folder")
                #Find Child's Parent
                #Check if parent is root 
                if parentID == 0:
                    print("\t\tParent is Root - ", end='')
                    if itemToAdd is not None:
                        #Item is not empty, add it to channel/root node
                        channel.add_child(itemToAdd)
                        print("Item has been Added to Root.")
                    else:
                        print("Item to be Added has 'None' Value. Cannot be added")
                else:
                    #Search for its parent, id would be the key it was in
                    for searchKey, searchValue in folderDict.items():
                        
                        #Search value array for each key
                        for searchItem in searchValue:            
            
                            #If a list is found, check if id matches parentID
                            if (type(searchItem) is list) and (not parentFound):
                                if searchItem[0] == parentID:
                                    print("\t\t\tParent Folder Found - ", end='')
                                    parentFound = True
                                    if itemToAdd is not None:
                                        #If item is not None, add it
                                        searchItem[1].add_child(itemToAdd)
                                        print("Item has been Added to Parent ", searchItem[0])
                                    else:
                                        print("Item to be Added has 'None' Value. Cannot be added")
                                    break
                        if parentFound:
                            parentFound = False
                            break
            
        
        return channel


if __name__ == "__main__":
    """
    Run this script on the command line using:
        python SchoologyKolibriChannel.py  --token=<your-token>
        
        or you can store the token in an empty .txt file and use that to run the command.
        
        python SchoologyKolibriChannel.py --token=<file-path-to-.txt-file>
    """
    simple_chef = SimpleChef()
    simple_chef.main()
    
    
    #Delete files stores locally
    #They have been uploaded, not needed anymore
    for file in filesCreated:
        if os.path.isdir(file):
            shutil.rmtree(file)
        else:
            os.remove(file)
