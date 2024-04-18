import time
import sys
from selenium import webdriver
from bs4 import BeautifulSoup
import os
import jsbeautifier
import re
import requests
import argparse

verboseMode = False
hideSelenium = True


flagParser = argparse.ArgumentParser()

flagParser.add_argument("-u", metavar="targetURL", required = True, help="URL of the target Website")
flagParser.add_argument("-v", action="store_true", help="More detailed output")
flagParser.add_argument("-s", action="store_true", help="Don't hide the selenium window")
flagParser.add_argument("-o", metavar="nameOfOutputDir", help="Custom name for output directory")

flagInput = flagParser.parse_args()

if(flagInput.v):
    verboseMode = True

target = str(flagInput.u)

outputDirectoryNameFromFlag = flagInput.o

if(flagInput.s):
    hideSelenium = False

currentGlobalCounter = 0;

# Makes firefox browser headless -> Prevents selenium from opening window


if(hideSelenium):
    os.environ['MOZ_HEADLESS'] = '1'

# Prepares firefox driver for selenium

browser = webdriver.Firefox()

# Sends a GET request to the provided target by opening the browser

print("Fetching HTML and parsing it ...\n\n")

try:
    browser.get(target)
except:
    print(f"Couldn't reach the website: {target}\n")
    onErrorUsageHelp()

# Gets the HTML source code of the target

targetSourceCode = browser.page_source

# Delay of 5 seconds, because after browser is opened scripts take time to load

time.sleep(5)

# Close the browser, from now on targetSourceCode is set

browser.close()

# Creates a parsable object out of the HTML source code

soup = BeautifulSoup(targetSourceCode, 'html.parser')

# Parse all <script> tags and their content respectivly

allScriptTags = soup.find_all("script")


print(f"Fetching {len(allScriptTags)} scripts\n\n")
print(f"Expecting more than {len(allScriptTags)} Scripts? The website might be blocking you based on your IP.") 
print("Please wait a while and then try again or consider using a vpn/proxy\n\n")


# Creates outputDirectory name after full target URL(replace for compatability)

outputDirectory = target.replace("/", "SLASH").replace("?", "QUESTION")

if(outputDirectoryNameFromFlag != None):
    outputDirectory = outputDirectoryNameFromFlag

# Cuts the length if it exceededs 255 bytes(Linux maxFileNameLength)

if (len(outputDirectory) > 255):

    outputDirectory = outputDirectory[:252] + "CUT"
    print("Name of outputDirectory > 255 -> Cutting it off\n\n")

try:
    os.mkdir(outputDirectory)
except:
    print(f"The directory {outputDirectory} already exists!\nPlease delete it or use the -o flag to set a custom name for the outputDirectory")
    exit()

# Used for naming of the outputFile

i = 0

# Iterate through all parsed scriptTags

for scriptTag in allScriptTags:

    # Increase counter for naming convention

    i += 1

    # Checks if the scriptTag is available locally(main website(already fetched)) or remotely(different website(still has to be fetched))

    if " src=" in str(scriptTag) or " src =" in str(scriptTag):

        # Open and create the outputFile for remote source code

        with open(outputDirectory + "/" + str(i) + ".js", "w") as file:

            # Parses the url(as string) of the remote script out of script tag
            try:
                urlOfRemoteScript = str(scriptTag["src"])
            except:
                print(f"Failed to parse URL out of {scriptTag}")
            # Checks if src is given as "/something" instead of https://example.com/something

            if (urlOfRemoteScript[:1] == "/"):
                # Parse domain out of target url from command line argument

                targetDomain = target.replace("https://", "")
                targetDomain = re.sub(r"/.*", "", targetDomain)

                # Get the urlScheme from the target command line argument

                urlScheme = ""

                if (target[:7] == "http://"):
                    urlScheme = "http://"
                elif (target[:8] == "https://"):
                    urlScheme = "https://"
                else:
                    print(
                        f"ERROR: --->  Unkown urlScheme({target}) <---")

                # Combine the domain and path back to a URL

                urlOfRemoteScript = f"{urlScheme}{targetDomain}{urlOfRemoteScript}"

            # GETs the remote javascript and converts it to a string(same as at top basically)
            try:
                #remoteScript = os.system("curl -s " + urlOfRemoteScript + " > /dev/null")          First attempt of doing this but this would introduce command injection vulns...
                remoteScript = requests.get(url = urlOfRemoteScript).text
                if(verboseMode):
                    print(f"Fetched remote script {i} from: {urlOfRemoteScript} ...")
                else:
                    print(f"Fetched remote script {i} ...")

            except:
                print(f"Failed to fetch the URL: '{urlOfRemoteScript}'")
                continue
                
            
            # Beautify the remoteDecodedJavascript

            finalJavascript = jsbeautifier.beautify(str(remoteScript))

            # Writes the remoteDecodedJavascript to the file

           
            file.write(finalJavascript)

    else:

        # Open and create the outputFile for local source code

        with open(outputDirectory + "/" + str(i) + ".js", "w") as file:

            # Write the beautified javascript the file("string" remove <script)

            file.write(str(jsbeautifier.beautify(scriptTag.string)))
            if(verboseMode):
                print(f"Fetched local script {i} from {target} ...")
            else:
                print(f"Fetched local script {i} ...")


    if (i == len(allScriptTags)):
        print(f"----------------\n\nSuccesfully fetched {i} scripts from: {target}\n\nOutput directory is {outputDirectory}\n\n----------------")
    currentGlobalCounter += 1

