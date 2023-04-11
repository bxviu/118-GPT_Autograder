import json
import sys
import os
import re
 
def score(answer1, answer2):
    global correctNum
    if (answer1 == answer2):
        correctNum += 1
        if debugLevel > 1: print("Matches: \"" + str(answer1) + "\" matches \"" + str(answer2) + "\"")
        return
    # maybe ChatGPT has the answer within a larger string, comment out if you want the scoring to be more strict
    # elif (answer1 in answer2):
    #     correctNum += 1
    #     if debugLevel > 1: print("Matches: \"" + str(answer1) + "\" is found within \"" + str(answer2) + "\"")
    #     return
    global wrongNum
    wrongNum += 1
    if debugLevel > 1: print("Wrong: \"" + str(answer1) + "\" doesn't match \"" + str(answer2) + "\"")

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

    fileCount = 0;
    if debugLevel > 1: invalidFileNum = 0
    
    checkFileList = []#[291]#[1810]#[706]#[876, 2257, 2253, 2216, 2193]
    for file in checkFileList:
        file = str(file) + ".json"
        jsonListOrig.append(os.path.join(original_file_path, file))
        jsonListGPT.append(os.path.join(GPT_file_path, file[:-5] + "_answer" + file[-5:]))
    if len(checkFileList) > 0:  return (jsonListOrig, jsonListGPT)

    for file in os.listdir(original_file_path):
        # if fileCount > 4: break
        if file.endswith(".json"):
            if os.path.exists(os.path.join(GPT_file_path, file[:-5] + "_answer" + file[-5:])):
                jsonListOrig.append(os.path.join(original_file_path, file))
                jsonListGPT.append(os.path.join(GPT_file_path, file[:-5] + "_answer" + file[-5:]))
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

def count_opening_braces(s):
    count = 2
    open = 0
    closed = 0
    for c in s:
        if c == '{':
            open += 1
            count += 1
        elif c == '}':
            closed += 1
        if open != 0 and closed != 0 and open == closed:
            return count
    return count

def extractAnswer(string):
    if debugLevel > 3: print("Extracting Answer from: \n" + string + "\n")
    string = string.replace("%", "").replace("$", "").replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "").replace("`", "")
    if debugLevel > 3: print("Removing %,$, ,\\n,\',\",`: \n" + string + "\n")
    if '\\boxed' in string:
        pattern = r'\\boxed{.*}'
        matches = list(set(re.findall(pattern, string)))
        if debugLevel > 2: print("Found Answer in String: " + matches[0])
        pattern = r'\\boxed{((?:[^{}]*{[^{}]*}*){0,%d}[^{}]*)}' % count_opening_braces(string)
        # get rid of duplicates of same answer
        matches = list(set(re.findall(pattern, string)))
        if debugLevel > 1: print("Extracted Answer: " + str(matches))
        if len(matches) > 1:
            if debugLevel > 0:
                addErrorFile("Multiple Answers")
            if debugLevel > 1: 
                print("why is there more than one answer in the solution file??? -  " + str(matches) 
                + "\nGoing to use answer in 0th index.")
        if len(matches) < 1:
            if debugLevel > 0: 
                addErrorFile("No Answer")
            if debugLevel > 1:
                print("why is no answer???")
        try:
            if 'frac' in matches[0]:
                pattern = r'(-?).*?{(.*)}{(.*)}'
                fractionNums = re.findall(pattern, matches[0])
                if len(fractionNums) != 0:
                    if debugLevel > 1: print("Found Fraction: " + str(fractionNums))
                    # formatting numerator
                    if (fractionNums[0][1].isnumeric()):
                        result = str(fractionNums[0][1])
                    else:
                        result = "(" + str(fractionNums[0][1]) + ")"
                    result += "/"
                    # formatting denominator
                    if (fractionNums[0][2].isnumeric()):
                        result += str(fractionNums[0][2])
                    else:
                        result += "(" + str(fractionNums[0][2]) + ")"
                    if fractionNums[0][0] == "-":
                        result = "-" + result
                else:
                    pattern = r'(-?)[\\A-Za-z_]+(\d+)'
                    fractionNums = re.findall(pattern, matches[0])
                    if debugLevel > 1: print("Found Fraction: " + str(fractionNums))
                    # formatting numerator
                    if (fractionNums[0][1].isnumeric()):
                        result = str(fractionNums[0][1][:int(len(str(fractionNums[0][1]))/2)])
                    else:
                        result = "(" + str(fractionNums[0][1][:int(len(str(fractionNums[0][1]))/2)]) + ")"
                    result += "/"
                    # formatting denominator
                    if (fractionNums[0][1].isnumeric()):
                        result += str(fractionNums[0][1][int(len(str(fractionNums[0][1]))/2):])
                    else:
                        result += "(" + str(fractionNums[0][1][int(len(str(fractionNums[0][1]))/2):]) + ")"
                    # result = str(fractionNums[0][1]) + "/" + str(fractionNums[0][2])
                    if fractionNums[0][0] == "-":
                        result = "-" + result
                '''
                some answers are formatted like this "\boxed{\frac19}" this is not helpful as "1" and "9" aren't seperated
                and they are supposed to be like "\boxed{\frac{1}{9}}""" 
                so this else statement should deal with stuff like that
                '''
            else:   
                result = ''.join(x for x in matches[0] if x != "\\")
            # Assuming that {} contains numbers that are part of a function now, like sqrt{324} becomes sqrt(324)
            result = result.replace("{", "(").replace("}", ")").replace("\\","")
            if debugLevel > 2: print("Replacing {} with () and removing \\: " + result)
            return result
        except:
            if debugLevel > 0: addErrorFile("Extraction Failed")
            return "Extraction Failed"
    elif 'frac{' in string:
            try:
                pattern = r'(-?).*?{(.*)}{(.*)}'
                fractionNums = re.findall(pattern, string)
                if debugLevel > 1: print("No \"\\boxed{}\" Format but Found Fraction: " + str(fractionNums))
                result = str(fractionNums[0][1]) + "/" + str(fractionNums[0][2])
                if fractionNums[0][0] == "-":
                    result = "-" + result
                if debugLevel > 2: print("Replacing {} with (): " + string)
                return result.replace("{", "(").replace("}", ")")
            except:
                if debugLevel > 0: addErrorFile("Extraction Failed")
                return "Extraction Failed"
    return string

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
        correctSolution = extractAnswer(openJsonFile(originalFile))
        if debugLevel > 0: print("Answer from Original: " + str(correctSolution))

        if debugLevel > 1: print("\nGPT File: " + GPTFile)
        GPTSolution = extractAnswer(openJsonFile(GPTFile))
        if debugLevel > 0: print("Answer from ChatGPT : " + str(GPTSolution) + "\n")
        
        score(correctSolution, GPTSolution)

        if debugLevel > 1: print("\n---------------------------------\n")

    print("Matching Answers: " + str(correctNum) 
        + "\nWrong Answers   : " + str(wrongNum))
    
    if debugLevel > 0: 
        global errorFiles
        print(str(len(errorFiles)) + " Files with Errors: \n" + str(errorFiles))


def main():
    global correctNum 
    global wrongNum
    global debugLevel
    global currentFile
    global errorFiles

    currentFile = ""
    errorFiles = []
    correctNum = 0
    wrongNum = 0
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
        # raise Exception("Not enough directory paths provided. Usage: python3 GPT_autograding_script.py <path/to/original/answer/directory/> <path/to/GPT/answer/directory/>")
        original_file_path = "algebra/algebra/"
        GPT_file_path = "algebra/algebra/answers/"
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
