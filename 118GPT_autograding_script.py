import json
import sys
import os
import re
import answer_extraction as extract
 
def score(answer1, answer2):
    global correctNum
    if (answer1 == answer2):
        correctNum += 1
        if debugLevel > 1: print("Matches: \"" + str(answer1) + "\" matches \"" + str(answer2) + "\"")
        return
    pattern = r"[^\(\)\-+/*.\d]?([\(\)\-+/*.\d]+)[^\(\)\-+/*.\d]?"
    matches1 = re.findall(pattern, answer1)
    matches2 = re.findall(pattern, answer2)
    if len(matches1) == 1 and len(matches2) == 1:
        if "os" in matches1[0] or "os" in matches2[0]:
            if debugLevel > 3: print("oh, nope")
        else:
            # this is for matching answers such as 1/2 and 0.5 that aren't literally the same, but have the same value
            if debugLevel > 3: print("Trying eval to calculate the value")
            # https://lybniz2.sourceforge.net/safeeval.html hope this is true
            # if you get this error or similar: <string>:1: SyntaxWarning: 'int' object is not callable; perhaps you missed a comma?
            # it is because of equations like 1(2), there needs to be 1*(2) for it to evaluate correctly
            # not dealing with that because it seems like a small error right now
            try: 
                if eval(matches1[0],{"__builtins__":None},{}) == eval(matches2[0],{"__builtins__":None},{}):
                    if debugLevel > 3:
                        print("success")
                        print(matches1[0])
                        print(matches2[0])
                    correctNum += 1
                    if debugLevel > 1: print("Evaluation of: \"" + str(answer1) + "\" matches \"" + str(answer2) + "\"")
                    return
            except:
                if debugLevel > 3:
                    print("failed")
                    print(matches1[0])
                    print(matches2[0])
    # maybe ChatGPT has the answer within a larger string, comment out if you want the scoring to be more strict
    elif (answer1 in answer2):
        if debugLevel > 2: print("Can find: \"" + str(answer1) + "\" within \"" + str(answer2) + "\"\nChecking if it has an equation around it.\n")
        if check_not_surrounded_by_chars(answer1, answer2):
            correctNum += 1
            if debugLevel > 1: print("Matches: \"" + str(answer1) + "\" is found within \"" + str(answer2) + "\"")
            return
        if debugLevel > 2: print("Found equation characters around it. No match.\n")
    global wrongNum
    wrongNum += 1
    if debugLevel > 1: print("Wrong: \"" + str(answer1) + "\" doesn't match \"" + str(answer2) + "\"")

# this should deal with some instances of seeing a smaller length answer being found within chatgpt's answer
# like "2" being found in "(1+sqrt(5))/2"
def check_not_surrounded_by_chars(a: str, b: str) -> bool:
    chars = set(",0123456789+-/*^().")
    # this checks out by 2 surrounding chars  
    # for i in range(len(b) - len(a) + 1):
    #     if a == b[i:i+len(a)]:
    #         if i > 1 and b[i-2:i] not in chars:
    #             continue
    #         if i > 0 and b[i-1:i] not in chars:
    #             continue
    #         if i + len(a) < len(b) - 1 and b[i+len(a):i+len(a)+2] not in chars:
    #             continue
    #         if i + len(a) < len(b) and b[i+len(a):i+len(a)+1] not in chars:
    #             continue
    #         return True
    # return False

    # this checks out by 1 surrounding char  
    for i in range(len(b) - len(a) + 1):
        if b[i:i+len(a)] == a:
            if i > 0 and b[i-1] in chars:
                continue
            if i+len(a) < len(b) and b[i+len(a)] in chars:
                continue
            return True
    return False

def addErrorFile(reason):
    global errorFiles
    global currentFile
    errorFiles.append((currentFile, reason))

def openJsonFile(file):
    # Opening JSON file
    with open(file) as json_file:
        data = json.load(json_file)
        return data['solution']

def getJsonFiles(original_file_path, GPT_file_path):
    jsonListOrig = []
    jsonListGPT = []

    fileCount = 0
    if debugLevel > 1: invalidFileNum = 0
    
    checkFileList = []#[1123, 1569, 1724, 1810, 2395, 2486, 313]#[2]#,2]#,51,230,327,872,1043,1349,1123]#[291]#[1810]#[706]#[876, 2257, 2253, 2216, 2193]
    for file in checkFileList:
        file = str(file) + ".json"
        jsonListOrig.append(os.path.join(original_file_path, file))
        if os.path.exists(os.path.join(GPT_file_path, file[:-5] + "_answer" + file[-5:])):
            jsonListGPT.append(os.path.join(GPT_file_path, file[:-5] + "_answer" + file[-5:]))
        elif os.path.exists(os.path.join(GPT_file_path, file[:-5] + "_answer_answer_formatted" + file[-5:])):
            jsonListGPT.append(os.path.join(GPT_file_path, file[:-5] + "_answer_answer_formatted" + file[-5:]))
        elif os.path.exists(os.path.join(GPT_file_path, file)):
            jsonListGPT.append(os.path.join(GPT_file_path, file))
        
    if len(checkFileList) > 0:  return (jsonListOrig, jsonListGPT)

    for file in os.listdir(original_file_path):
        # if fileCount > 4: break
        if file.endswith(".json"):
            if os.path.exists(os.path.join(GPT_file_path, file[:-5] + "_answer" + file[-5:])):
                jsonListOrig.append(os.path.join(original_file_path, file))
                jsonListGPT.append(os.path.join(GPT_file_path, file[:-5] + "_answer" + file[-5:]))
            elif os.path.exists(os.path.join(GPT_file_path, file[:-5] + "_answer_answer_formatted" + file[-5:])):
                jsonListOrig.append(os.path.join(original_file_path, file))
                jsonListGPT.append(os.path.join(GPT_file_path, file[:-5] + "_answer_answer_formatted" + file[-5:]))
            elif os.path.exists(os.path.join(GPT_file_path, file)):
                jsonListOrig.append(os.path.join(original_file_path, file))
                jsonListGPT.append(os.path.join(GPT_file_path, file))
            elif debugLevel > 0:
                global currentFile
                currentFile = file
                addErrorFile("No Comparison File")
                if debugLevel > 1:
                    invalidFileNum += 1
                if debugLevel > 2: print(file + " does not have corresponding answer file in GPT directory")
            fileCount += 1
        if fileCount % 100 == 0 and debugLevel > 1:
            print("Found " + str(fileCount) + " files.")
        
    if debugLevel > 1 and invalidFileNum > 0: print("Found " + str(invalidFileNum) + " files that do not have corresponding answer file in GPT directory. Find them or something idk")

    return (jsonListOrig, jsonListGPT)

def gradeFiles(original_file_path, GPT_file_path): 
    (orig, gpt) = getJsonFiles(original_file_path, GPT_file_path)

    if debugLevel > 1: print("\n\nMatching Answers Now\n\n")
    for i in range(len(orig)):
        (originalFile, GPTFile) = (orig[i], gpt[i])
        if debugLevel >= 1: 
            pattern = r"/(\d+)\.json$"
            match = re.search(pattern, originalFile)
            global currentFile
            currentFile = match.group(1)
            if debugLevel == 1: 
                print("Problem #" + match.group(1))
        if debugLevel > 1: print("Original File: " + originalFile)
        correctSolution = extract.extractAnswer(openJsonFile(originalFile), debugLevel)
        if "ExtractionFailed" in correctSolution: 
            addErrorFile("Extraction Failed")
            global extractionFailureCount
            extractionFailureCount += 1
        if debugLevel > 0: print("Answer from Original: " + str(correctSolution))

        if debugLevel > 1: print("\nGPT File: " + GPTFile)
        GPTSolution = extract.extractAnswer(openJsonFile(GPTFile), debugLevel)
        if debugLevel > 0: print("Answer from ChatGPT : " + str(GPTSolution) + "\n")
        
        score(correctSolution, GPTSolution)

        if debugLevel > 1: print("\n---------------------------------\n")

    print("Matching Answers: " + str(correctNum) 
        + "\nWrong Answers   : " + str(wrongNum)
        + "\nTotal Answers   : " + str(correctNum+wrongNum)
        + "\n\nComparisons if Ignoring " + str(extractionFailureCount) + " Failed Extractions."
        + "\nMatching Answers: " + str(correctNum-extractionFailureCount if correctNum > extractionFailureCount else 0) 
        + "\nWrong Answers   : " + str(wrongNum-extractionFailureCount if wrongNum > extractionFailureCount else 0)
        + "\nTotal Answers   : " + str(correctNum+wrongNum-extractionFailureCount)
        )
    
    if debugLevel > 0: 
        global errorFiles
        print("\n" + str(len(errorFiles)) + " Files with Errors: \n" + str(errorFiles))


def main():
    global correctNum 
    global wrongNum
    global debugLevel
    global currentFile
    global errorFiles
    global extractionFailureCount

    currentFile = ""
    errorFiles = []
    correctNum = 0
    wrongNum = 0
    extractionFailureCount = 0
    '''
        The higher the level, the more info is printed
         0 for only results at the end
         1 to see all answers from original and chatgpt
         2 to see logic running and file location
         3 to see even more logic running and the substring from where the answers are found
         4 to see the whole string where the answers are extracted from
    '''
    debugLevel = 0

    if len(sys.argv) < 2:
        # also make sure the files are named appropriately
        raise Exception("Not enough directory paths provided. Usage: python3 GPT_autograding_script.py <path/to/original/answer/directory/> <path/to/GPT/answer/directory/>")
        # original_file_path = "algebra/algebra/"
        # GPT_file_path = "algebra/algebra/answers/"
    else:
        original_file_path = sys.argv[1]
        GPT_file_path = sys.argv[2]
    if len(sys.argv) > 3:
        debugLevel = int(sys.argv[3]) if sys.argv[3].isnumeric() else debugLevel
    
    if os.path.isdir(original_file_path) and os.path.isdir(GPT_file_path):
        gradeFiles(original_file_path, GPT_file_path)
    else:
        raise Exception("These are not directory paths. Usage: python3 GPT_autograding_script.py <path/to/original/answer/directory/> <path/to/GPT/answer/directory/> <debug level>")

if __name__ == '__main__':
    main()
