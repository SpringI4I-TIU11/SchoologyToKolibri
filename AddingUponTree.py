import requests
import json
from pprint import pprint
from requests_oauthlib import OAuth1

class FolderNode:
    """This object will hold the data about this folder and point to each item it contains. Folders
       can point to folder-items or other folders"""
    type = 'folder'
    def __init__(self,title):
        """A node will be initialized with no child nodes"""
        self.title = title
        self._children = []
    def addChild(self, node):
        """Add a child to a folder. Can be another folder, page, or document"""
        self._children.append(node)
    def size(self):
        """Returns the amount of children a folder has"""
        return len(self._children)
    def children(self):
        """Returns a list of all of the children in a folder as references to it's object location to be iterated through."""
        return list(self._children)
    def setId(self, folderId):
        """Store json id of the folder"""
        self.id = folderId
    def setLocation(self, folderLoc):
        """Store json location of the folder"""
        self.location = folderLoc
    #TODO: Function to return number of folders

class DocumentNode:
    """This object will hold information regarding document nodes. Will be pointed to by a folder."""
    def __init__(self, title, type): ### Determine what info each Document node will have
        self.title = title
        self.type = type
    def setId(self, fileId):
        """Store json id of the folder"""
        self.id = fileId
    def setLocation(self, fileLoc):
        """Store json location of the folder"""
        self.location = fileLoc

# TODO: Create classes for each type of nodes and include the appropriate information

### Working theory is that we would start at the Tree root and do a breadth-first search. We can call type(object) to determine the class
### and from the class we can determine what type of ricecooker node to create. The BFS will recreate the directory structure


# Creation of Root Node in Tree Hierarchy
rootnode = FolderNode("Root Folder") # root

# Create API request to schoology root course folder with OAuth credentials. Store json response
url = "https://api.schoology.com/v1/sections/4631064973/folders/0"
auth = OAuth1("78742dd11a3f85f8f40e0b7c595e67050601ce052","2a06176984a9d08c9d9247438e79db9c","","")
response = requests.get(url, auth=auth)
#print(response.json())
#pprint(response.json())

data = response.json()
total = data['total']

#Arrays to store folders and folder api locations
jsonFolders = []
folders = []

#Loops through folders in call
#Grabs locations for child folders and stores in locations array
for x in range(total):
    #Stores folder (json) object from request in folders array
    jsonFolders.append(data['folders'][x])
    
    #json.dumps converts json object to a json string
    #json.loads converts string into dictionary
    contentDict = json.loads(json.dumps(jsonFolders[x]))
    
    #store folder location in locations array
    folders.append( [contentDict['location'], contentDict['title'], contentDict['id'] ])
    
nodeDict = {}
    
#Make api calls using locations
for folder in folders:
    #Creating folder node from title
    newFolderNode = FolderNode(folder[1]) #New Folder Node
    newFolderNode.setId(folder[2])
    newFolderNode.setLocation(folder[0])
    
    #Add node as child
    rootnode.addChild(newFolderNode)
    
    
    #Add new folder node to nodeDictionary
    nodeDict[folder[1]] = newFolderNode
    
    #Set url to folder location
    url = folder[0]
    
    #Execute request
    response = requests.get(url, auth=auth)
    
    #Store json object
    jsonObj = response.json();
    #pprint(jsonObj)
    
    #Get folder items from jsonObj and print
    for x in jsonObj['folder-item']:
        if(x['type'] != 'folder'):
            #Not a folder, create a new document node
            newDocumentNode = DocumentNode(x['title'], x['type'])
            newDocumentNode.setId(x['id'])
            newDocumentNode.setLocation(x['location'])
            
            #Add document folder to create parent in node Dictionar
            nodeDict[folder[1]].addChild(newDocumentNode)
            
        else:
            #Create a new folder node for nested folder
            childFolderNode = FolderNode(x['title'])
            childFolderNode.setId(x['id'])
            childFolderNode.setLocation(x['location'])
            
            #Use title to add node to proper folder in dictionary
            nodeDict[folder[1]].addChild(childFolderNode)  
            

#Both methods below show correct hierarchy
for i in rootnode.children(): #loop through children of root node and print title
    print()
    if(type(i) is FolderNode):
        print(i.title)
        for x in i.children():
            print("\t", x.title, "\tid: ", x.id, "\ttype: ", x.type, "\n\t\tlocation: ", x.location)
    else:
        print("\tCHILD FOLDER: ", i.title, "\tID: ", i.id, "\tLOCATION: ", i.location)
        
print("\n\n\n")
        
"""
for key in nodeDict:
    print("PARENT FOLDER/KEY: ", key)
    for i in nodeDict[key].children():
        if(type(i) is FolderNode):
            print("\tCHILD FOLDER: ", i.title, "\tID: ", i.id, "\tLOCATION: ", i.location)
        else:
            print("\t", i.title)
"""
        


    

    
    



