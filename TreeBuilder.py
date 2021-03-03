import requests
import json
from requests_oauthlib import OAuth1

class FolderNode:
    """This object will hold the data about this folder and point to each item it contains. Folders
       can point to folder-items or other folders"""
    type = 'folder'
    def __init__(self,title, id, location):
        """A node will be initialized with no child nodes"""
        self.title = title
        self.id = id
        self.location = location
        self._children = []
        self._childFolders = []
    def addChild(self, node):
        """Adds a child to a folder. Can be another folder, page, or document"""
        self._children.append(node)
        if(type(node)==FolderNode): # If it's another folder, add to child folders
            self._childFolders.append(node)
    def size(self):
        """Returns the amount of children a folder has"""
        return len(self._children)
    def children(self):
        """Returns a list of all of the children in a folder as references to it's object location to be iterated through."""
        return list(self._children)
    def folders(self):
        """Returns a list of all children that are folders"""
        return list(self._childFolders)
    def hasChildrenFolder(self):
        """Returns a boolan value representing whether a folder has child folders"""
        if len(self._childFolders) == 0:
            return False
        return True
    def totalFolders(self):
        """Returns a number of child folders a folder has"""
        return len(_childFolders)
    def __str__(self):
        """String Represent a node with its title"""
        return self.title
    def __repr__(self):
        """Represent a node with its title"""
        return self.title
        #return "Title: {}\nID: {}\nLocation: {}\nChildren: {}\nChild Folders: {}\n".format(self.title, self.id, self.location, self._children, self._childFolders)
    #TODO: Function to return number of folders

class DocumentNode:
    """This object will hold information regarding document nodes. Will be pointed to by a folder."""
    def __init__(self, title, type, id, location): # TODO: Determine what info each Document node will have
        self.title = title
        self.type = type
        self.id = id
        self.location = location
    def hasChildren(self):
        """A node other than folder cannot have children"""
        return False
    def __str__(self):
        """String represent as title"""
        return self.title
    def __repr__(self):
        """Represent as title"""
        return self.title
        #return "Title: {}\nID: {}\nLocation: {}\nType: {}\n".format(self.title, self.id, self.location, self.type)
# TODO: Create classes for each type of nodes and include the appropriate information

### Working theory is that we would start at the Tree root and do a breadth-first search. We can call type(object) to determine the class
### and from the class we can determine what type of ricecooker node to create. The BFS will recreate the directory structure

url = "https://api.schoology.com/v1/sections/4631064973/folders/0"

# Creation of Root Node in Tree Hierarchy
rootnode = FolderNode("Root Folder", 0, url) # root

# Create API request to schoology root course folder with OAuth credentials. Store json response
auth = OAuth1("78742dd11a3f85f8f40e0b7c595e67050601ce052","2a06176984a9d08c9d9247438e79db9c","","")
response = requests.get(url, auth=auth)

data = response.json()
url = data['folders'][0]['location']
# request folder in root folder ("Athens - Remote Instruction")
response = requests.get(url, auth=auth)
data = response.json()
#create node object for nested folder and add to root children
currentFolderNode = FolderNode(data['self']['title'], data['self']['id'], data['self']['location'])
rootnode.addChild(currentFolderNode)

# folder nodes that have been visited
visited = []
# folder nodes to visit
queue = []
queue.append(currentFolderNode)

while queue: # while there are still nodes to be visited
    currentFolderNode = queue.pop(0) # get next node and remove from front of line
    visited.append(currentFolderNode) # add to visited
    url = currentFolderNode.location # get url
    response = requests.get(url, auth=auth) # make API request
    data = response.json()
    for item in data['folder-item']: # loop through items other than self in request
        if item['type'] == 'folder': # if it's a folder, create a folder node
            newFolderNode = FolderNode(item['title'], item['id'], item['location'])
            currentFolderNode.addChild(newFolderNode) # add new node as child of current node
            queue.append(newFolderNode) # add the new folder to the queue
        else: # otherwise create a document node
            newDocumentNode = DocumentNode(item['title'], item['type'],item['id'], item['location'])
            currentFolderNode.addChild(newDocumentNode) # add as child of current folder

# test outputs
print(rootnode , "Children")
print(rootnode.children())
print()
print(rootnode.folders()[0], "Children")
print(rootnode.folders()[0].children())
print()
print(rootnode.folders()[0].folders()[0], "Children")
print(rootnode.folders()[0].folders()[0].children())
print()
print(rootnode.folders()[0].folders()[0].folders()[0], "Children")
print(rootnode.folders()[0].folders()[0].folders()[0].children())
print()
print(rootnode.folders()[0].folders()[0].folders()[1], "Children")
print(rootnode.folders()[0].folders()[0].folders()[1].children())
print()
