class GoogleDownloader():
    """Downloader object to download different forms of files from Google"""
    def downloadPowerpoint(self, id):
        """Accepts a string ID. Reads byte data from request content and writes into PDF"""
        url = "https://docs.google.com/presentation/d/{}/export/pdf".format(id)
        req = requests.get(url)
        contentDisposition = req.headers['Content-Disposition']
        fileName = re.findall("filename=.*;", req.headers['content-disposition'])[0].split("\"")[1]
        with open(fileName, 'wb') as f:
            f.write(req.content)

    def downloadDocument(self, id):
        """Accepts a string ID. Reads byte data from request content and writes into PDF"""
        url = "https://docs.google.com/presentation/d/{}/export/pdf".format(id)
        req = requests.get(url)
        fileName = re.findall("filename=.*;", req.headers['content-disposition'])[0].split("\"")[1]
        with open(fileName, 'wb') as f:
            f.write(req.content)
            f.write(req.content)

testID = "1tlHWo9PlhyjX36hDB0yovv8owKIdz3ZlYRbGrcQaot4"

downloader = GoogleDownloader()
downloader.downloadPowerpoint(testID)
