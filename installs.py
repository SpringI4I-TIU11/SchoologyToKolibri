import subprocess
import sys


#Packages that need to be installed to run Schoology Kolibri Channel Builder tool
packages = ['ricecooker', 'requests_oauthlib', 'pdfkit', 'CairoSVG', 'unicode_slugify']
    
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
for package in packages:
    install(package)



