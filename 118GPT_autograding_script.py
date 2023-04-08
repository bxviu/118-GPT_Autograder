import json
import sys
import os
import re
 
def score(answer1, answer2):
    if (answer1 == answer2):
        global correctNum
        correctNum += 1
        if debugLevel > 1: print(str(answer1) + " matches " + str(answer2) + "")
        return
    global wrongNum
    wrongNum += 1
    if debugLevel > 1: print(str(answer1) + " doesn't match " + str(answer2) + "")

def openJsonFile(file):
    # Opening JSON file
    with open(file) as json_file:
        data = json.load(json_file)
        return data['solution']

def getJsonFiles(original_file_path, GPT_file_path):
    # https://www.geeksforgeeks.org/python-read-file-from-sibling-directory/
    # https://www.geeksforgeeks.org/python-list-files-in-a-directory/
    jsonListOrig = []
    jsonListGPT = []

    fileCount = 0;
    if debugLevel > 1: invalidFileNum = 0
    
    checkFileList = [876, 2257, 2253, 2216, 2193]
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
            elif debugLevel > 1:
                invalidFileNum += 1
                print(file + " does not have corresponding answer file in GPT directory")
            fileCount += 1
        if fileCount % 100 == 0:
            print("Found " + str(fileCount) + " files.")
        
    if debugLevel > 1 and invalidFileNum > 0: print("Found " + str(invalidFileNum) + " files that do not have corresponding answer file in GPT directory. Find them or something idk")

    return (jsonListOrig, jsonListGPT)

def count_opening_braces(s): # need to update this for frac{\sqrt{3}}{3}}$$
    count = 2
    open = 0
    closed = 0
    for c in s:
        if c == '{':
            open += 1
            count += 1
        elif c == '}':
            closed += 1
            # count -= 1
        if open != 0 and closed != 0 and open == closed:
            # print("eq " + str(count))
            return count
    # print("end " + str(count))
    return count

def extractAnswer(string):
    if debugLevel > 2: print("Extracting Answer from: " + string)
    string = string.replace("%", "").replace("$", "").replace(" ", "").replace("\n", "").replace("\'", "").replace("\"", "").replace("`", "")
    # print(string)
    if '\\boxed' in string:
        # return string
        # pattern = r'\\boxed{.*}'
        # pattern = r'\\boxed\([^()]+\)'
        # pattern = r'\\boxed{((?:[^{}]*{[^{}]*}){0,%d}[^{}]*)}' % count_opening_braces(string)
        pattern = r'\\boxed{((?:[^{}]*{[^{}]*}*){0,%d}[^{}]*)}' % count_opening_braces(string)
        # get rid of duplicates of same answer
        matches = list(set(re.findall(pattern, string)))
        if debugLevel > 1: print("Extracted Answer: " + str(matches))
        if len(matches) > 1:
            if debugLevel > 1: print("why is there more than one answer in the solution file??? -  " + str(matches) 
                            + "\nGoing to use answer in 0th index.")
            # raise Exception("why is there more than one answer in the solution file??? - " + str(matches))
        if len(matches) < 1:
            raise Exception("why is no answer???")
        # if "," in matches[0]:
        # matches[0] = re.sub(",", "", matches[0]).replace(" ", "")
        # matches[0] = matches[0].replace("%", "").replace("$", "")    
        try:
            if 'frac' in matches[0]:
                # pattern = r'\\boxed\{(-?).*{(\d+)}{(\d+)}}'
                # pattern = r'\\boxed\{(-?).*{(.*)}{(.*)}}'
                pattern = r'(-?).*{(.*)}{(.*)}'
                fractionNums = re.findall(pattern, matches[0])
                if debugLevel > 1: print("Found Fraction: " + str(fractionNums))
                result = str(fractionNums[0][1]) + "/" + str(fractionNums[0][2])
                if fractionNums[0][0] == "-":
                    result = "-" + result
                return result
                # str(fractionNums[0][0][1:-1]) + "/" + str(fractionNums[0][1][1:-1]) if fractionNums[0][0] != "-" else "-" + 
            # print(matches[0][7:-1])
            # Assuming that {} contains numbers that are part of a function now, like sqrt{324} becomes sqrt(324)
            matches[0] = matches[0].replace("{", "(").replace("}", ")")
            if debugLevel > 1: print("Replacing {} with (): " + matches[0])
            # matches[0][7:-1] cuts off the "\\boxed(" at the start of the string and ")" at the end
            return ''.join(x for x in matches[0] if x != "\\")
            # return ''.join(x for x in matches[0][7:-1] if x != "\\") # x.isdigit() or x == '-')
            # return ''.join(filter(str.isdigit, matches[0]))
        except:
            return "grader-error2"
    elif 'frac{' in string:
        # try:
            pattern = r'(-?).*{(.*)}{(.*)}'
            fractionNums = re.findall(pattern, string)
            if debugLevel > 1: print("No \"\\boxed{}\" Format but Found Fraction: " + str(fractionNums))
            result = str(fractionNums[0][1]) + "/" + str(fractionNums[0][2])
            if fractionNums[0][0] == "-":
                result = "-" + result
            if debugLevel > 1: print("Replacing {} with (): " + string)
            return result.replace("{", "(").replace("}", ")")
        # except:
        #     return "grader-error2"
    return string

'''def extractAnswer(string):
    # print(string)
    string = string.replace("%", "").replace("$", "")
    if '\\boxed{' not in string:
        return string
    pattern = r'\\boxed{.*}'
    # get rid of duplicates of same answer
    matches = list(set(re.findall(pattern, string)))
    if debug: print("Extracting Answer from: " + str(matches))
    if len(matches) > 1:
        if debug: print("why is there more than one answer in the solution file??? -  " + str(matches) 
                        + "\nGoing to use answer in 0th index.")
        # raise Exception("why is there more than one answer in the solution file??? - " + str(matches))
    if len(matches) < 1:
        raise Exception("why is no answer???")
    # if "," in matches[0]:
    # matches[0] = re.sub(",", "", matches[0]).replace(" ", "")
    # matches[0] = matches[0].replace("%", "").replace("$", "")
    try:
        if 'frac' in matches[0]:
            # pattern = r'\\boxed\{(-?).*{(\d+)}{(\d+)}}'
            pattern = r'\\boxed\{(-?).*{(.*)}{(.*)}}'
            fractionNums = re.findall(pattern, matches[0])
            if debug: print("Found Fraction: " + str(fractionNums))
            result = str(fractionNums[0][1]) + "/" + str(fractionNums[0][2])
            if fractionNums[0][0] == "-":
                result = "-" + result
            return result
            # str(fractionNums[0][0][1:-1]) + "/" + str(fractionNums[0][1][1:-1]) if fractionNums[0][0] != "-" else "-" + 
        # print(matches[0][7:-1])
        # Assuming that {} contains numbers that are part of a function now, like sqrt{324} becomes sqrt(324)
        matches[0] = matches[0].replace("{", "(").replace("}", ")")
        if debug: print("Replacing {} with (): " + matches[0])
        # matches[0][7:-1] cuts off the "\\boxed(" at the start of the string and ")" at the end
        return ''.join(x for x in matches[0][7:-1] if x != "\\") # x.isdigit() or x == '-')
        # return ''.join(filter(str.isdigit, matches[0]))
    except:
        return "error"'''

def gradeFiles(original_file_path, GPT_file_path): 
    (orig, gpt) = getJsonFiles(original_file_path, GPT_file_path)

    if debugLevel > 1: print("\n\nMatching Answers Now\n\n")
    for i in range(len(orig)):
        (originalFile, GPTFile) = (orig[i], gpt[i])

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

def main():
    global correctNum 
    global wrongNum
    global debugLevel

    correctNum = 0
    wrongNum = 0
    '''
        The higher the level, the more info is printed
         0 for only results at the end
         1 to see all answers from original and chatgpt
         2 to see logic running and file location
         3 to see the exact string where answers are extracted from
    '''
    debugLevel = 3

    if len(sys.argv) < 2:
        # raise Exception("Not enough directory paths provided. Usage: python3 GPT_autograding_script.py <path/to/original/answer/directory/> <path/to/GPT/answer/directory/>")
        original_file_path = "algebra/algebra/"
        GPT_file_path = "algebra/algebra/answers/"
    else:
        original_file_path = sys.argv[1]
        GPT_file_path = sys.argv[2]
    
    if os.path.isdir(original_file_path) and os.path.isdir(GPT_file_path):
        gradeFiles(original_file_path, GPT_file_path)
    else:
        raise Exception("These are not directory paths. Usage: python3 GPT_autograding_script.py <path/to/original/answer/directory/> <path/to/GPT/answer/directory/>")

if __name__ == '__main__':
    main()
