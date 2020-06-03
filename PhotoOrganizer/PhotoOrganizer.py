import sys, os, time, datetime, shutil, calendar, ctypes, getopt, filecmp;
from os.path import isfile, join

def GetYearDict(fileTimeStamp, fileDict):
    """ Helper func returning the dict holding the fileReferences in the month of the fileTimeStamp

    :param fileTimeStamp: The timestamp of the file to be placed in the dict
    :type fileTimeStamp: dateTime
    :param fileDict: The dict of the month corresponding to fileTimeStamp
    :type fileDict: dict {str:dict}
    :returns: The dict in fileDict corresponding to the fileTimeStamp year
    :rtype: dict
    """
    yearString = fileTimeStamp.strftime("%Y")
    if not yearString in fileDict:
        fileDict[yearString] = {}
    return fileDict[yearString]

def GetMonthDict(fileTimeStamp, yearDict):
    """ Helper func returning the dict holding the months in the year of the fileTimeStamp

    :param fileTimeStamp: The timestamp of the file to be placed in the dict
    :type fileTimeStamp: dateTime
    :param yearDict: The dict to hold the year of the given file
    :type yearDict: dict {str:dict}
    :returns: The dict in yearDict corresponding to the fileTimeStamp year
    :rtype: dict
    """
    monthString = fileTimeStamp.strftime("%m_%b")
    if not monthString in yearDict:
        yearDict[monthString] = {}
    return yearDict[monthString]

def AddAllSubfileStringsToList(fileList, fileTypeDict, directoryString):
    """ Adds all files in directoryString path (recursively) to fileList, and their type to filetype dict

        :param fileList: List to be populated with all files in subfolders, recursively
        :type fileList: [string]
        :param fileTypeDict: A Dict to hold filetypes and their count
        :type fileTypeDict: {str:int}
        :param directoryString: The directory in which to recursively search for files
        :type directoryString: str
    """
    for root, dirs, files in os.walk(directoryString, topdown=False):
       for name in files:
          filename, file_extension = os.path.splitext(os.path.join(root, name))
          if not file_extension in fileTypeDict:
              fileTypeDict[file_extension] = 1
          else:
              fileTypeDict[file_extension] += 1
          fileList.append(os.path.join(root, name))

def GetFileModificationDatetime(fullPath):
    """ Gets the earliest time between the modification or creation time and returns the dateTime representation

    :param fullPath: File Fullpath for checking modification and creation time
    :type fullPath: str
    """
    modTime = os.path.getmtime(fullPath)
    creationTime = os.path.getctime(fullPath)
    fileTimestamp = min(modTime, creationTime)
    return datetime.datetime.strptime(time.ctime(fileTimestamp), "%a %b %d %H:%M:%S %Y")

class FileReferences:
    def __init__(self, sourcePath, creationDate):
        self.sourcePaths = []
        self.sourcePaths.append(sourcePath)
        self.fileBaseName = os.path.basename(sourcePath)
        self.creationDate = creationDate
        filename, file_extension = os.path.splitext(self.fileBaseName)
        self.fileNameOnly = filename
        self.fileExtension = file_extension

    def AlreadyHasPath(self, fullPath):
        return fullPath in self.sourcePaths

    def AddFileReference(self, fullPath):
        self.sourcePaths.append(fullPath)

    def AreDuplicates(self):
        return len(self.sourcePaths) > 1

    def EnsureIsPureDuplicate(self):
        if self.AreDuplicates():
            #We check against all duplicates. I'm paranoid, what can I say.
            for i in range(1, len(self.sourcePaths)):
                #We use a full cmp here. Very inefficient. I'm paranoid, what can I say.
                if not filecmp.cmp(self.sourcePaths[0], self.sourcePaths[i], False):
                    print("FALSE DUPLICATE FOUND: \n" + possibleDupe)
                    print("IS NOT A DUPLICATE OF " + self.sourcePaths[i])
                    return False
        return True


    def logString(self):
        prntStr = "FILE: " + self.sourcePaths[0] + "; DATE: " + self.creationDate.strftime("%Y-%b") + "\n"
        if self.AreDuplicates():
            for i in range(1, len(self.sourcePaths)):
                prntStr += "\tDUPE: " + self.sourcePaths[i] + "\n"
        return prntStr



def main(argv):
    #Instantiating important variables
    inDir = ""
    outDir = ""
    yearTable = {}
    copied = 0
    duplicates = 0
    alreadyExisted = 0
    fileTypes = {}
    fileList = []
    dumpDuplicates = False
    logFile = False

    #Getting relevant command line arguments
    try:
        opts, args = getopt.getopt(argv,"i:o:dl",["idir=","odir="])
    except getopt.GetoptError:
        print ("PhotoOrganizer.py -i <inputdirectory> -o <outputdirectory> -d -l")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-i", "--idir"):
            inDir = arg
        elif opt in ("-o", "--odir"):
            outDir = arg
        elif opt == "-d":
            dumpDuplicates = True
        elif opt == "-l":
            logFile = True
    if not inDir or not outDir:
        print ("PhotoOrganizer.py -i <inputdirectory> -o <outputdirectory> -d -l")
        sys.exit(2)

    duplicateDir = outDir + "\\duplicates"

    #Getting all files that we'll be acting upon
    AddAllSubfileStringsToList(fileList, fileTypes, inDir)

    #Setting up the file reference for each photo.
    for fullPath in fileList:
        timestampDatetime = GetFileModificationDatetime(fullPath);
        fileBaseName = os.path.basename(fullPath);

        correctYearDict = GetYearDict(timestampDatetime, yearTable)
        correctMonth = GetMonthDict(timestampDatetime, correctYearDict)

        #if we end up with a name collision, so long as they're dated in the same month bucket, we assume they're the same.
        #   We'll confirm with a filecmp.cmp later
        if fileBaseName in correctMonth:
            if correctMonth[fileBaseName].creationDate.date() != timestampDatetime.date():
                #If they're not in the same month bucket, popup a little prompt for choosing the newer or older timestamp
                if correctMonth[fileBaseName].creationDate.month != timestampDatetime.month:
                    errorboxStr = "First filepath: " + correctMonth[fileBaseName].sourcePaths[0] + "\n" + "Second filepath: " + fullPath + "\n"
                    errorboxStr += "First FileTime: \t" + str(correctMonth[fileBaseName].creationDate) + "\n" + "Second FileTime: \t" + str(timestampDatetime) + "\n";
                    errorboxStr += "\n\nClick OK to take the older, Cancel to take the newer"
                    popupRet = ctypes.windll.user32.MessageBoxW(0, errorboxStr, "Time Mismatch", 1)
                    if popupRet == 1:
                        correctMonth[fileBaseName].creationDate = min(correctMonth[fileBaseName].creationDate, timestampDatetime)
                    elif popupRet == 2:
                        correctMonth[fileBaseName].creationDate = max(correctMonth[fileBaseName].creationDate, timestampDatetime)
                    else:
                        print("Unexpected value, bailing")
                        sys.exit(2)
                else:
                    correctMonth[fileBaseName].creationDate = min(correctMonth[fileBaseName].creationDate, timestampDatetime)
            #Sanity check
            if fileBaseName != correctMonth[fileBaseName].fileBaseName:
                print("Mismatched filenames somehow, this is a problem")
                sys.exit(2)
            correctMonth[fileBaseName].AddFileReference(fullPath)
        else:
            correctMonth[fileBaseName] = FileReferences(fullPath, timestampDatetime);

    #Validating that all name collisions truly are duplicates. Also logging file list state if requested
    with open("PhotoOrganizerLog.txt", "a") as text_file:
        for year in yearTable:
            for month in yearTable[year]:
                for file, fileRefs in yearTable[year][month].items():
                    if logFile:
                        text_file.write(fileRefs.logString())
                    if fileRefs.AreDuplicates():
                        print ("Validating " + fileRefs.fileBaseName + " copies")
                        if not fileRefs.EnsureIsPureDuplicate():
                            print("Same filename, Non duplicate found, halting run")
                            sys.exit(2)

    #Getting each year, making a dir for it...
    for year in yearTable:
        yearDir = os.path.join(outDir, year)
        print(yearDir)
        if not os.path.exists(yearDir):
            os.makedirs(yearDir)
        #Getting each month in the year, making a dir for it...
        for month in yearTable[year]:
            monthDir = os.path.join(yearDir, month)
            if not os.path.exists(monthDir):
                os.makedirs(monthDir)
            print("\t" + monthDir)
            print("\tMONTH: " + month)
            #Getting each file in the month...
            for file, fileRefs in yearTable[year][month].items():
                inFilePath = fileRefs.sourcePaths[0];
                outFilePath = os.path.join(monthDir, fileRefs.fileBaseName)
                print("\t\tIN:\t" + inFilePath)
                print("\t\tOUT:\t" + outFilePath)
                #If the file exists, lets not pave it. #TODO: Be even more paranoid and filecmp against the existing file.
                if os.path.isfile(outFilePath):
                    alreadyExisted += 1
                else:
                    shutil.copy2(inFilePath, outFilePath)
                    copied += 1
                #If we have duplicates, note that for reporting statistics
                if fileRefs.AreDuplicates():
                    duplicates += (len(fileRefs.sourcePaths) - 1)
                    #If we wanna be SUPER PARANOID and visually compare all duplicates, we put all sources of pics with dupes
                    #   into a duplicate folder for viewing.
                    if dumpDuplicates:
                        if not os.path.exists(duplicateDir):
                            os.makedirs(duplicateDir)
                        for i in range(0, len(fileRefs.sourcePaths)):
                            duplicateOutFilePath = os.path.join(duplicateDir, fileRefs.fileNameOnly + "(" + str(i) + ")" + fileRefs.fileExtension)
                            shutil.copy2(inFilePath, duplicateOutFilePath)
                            print("\t\t\tDUPE:\t" + duplicateOutFilePath)

    #Report all copies, duplicates and already existing files with a total for ensuring the correct file count was processed
    print ("Copied " + str(copied) + " files.")
    print (str(duplicates) + " duplicate files found. Only copied 1 instance of the duplicates")
    print (str(alreadyExisted) + " files were not copied, as they already existed")
    print ("Total files read: " + str(alreadyExisted + copied + duplicates))

if __name__ == "__main__":
   main(sys.argv[1:])
