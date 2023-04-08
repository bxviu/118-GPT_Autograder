import json
import sys
import os
import re
 
def score(answer1, answer2):
    if (answer1 == answer2):
        global correctNum
        correctNum += 1
        return
    global wrongNum
    wrongNum += 1

def openJsonFile(file):
    # Opening JSON file
    with open(file) as json_file:
        data = json.load(json_file)

        # Print the type of data variable
        # print("Type:", type(data))
    
        # Print the data of dictionary
        # print("\nproblem:", data['problem'])
        # print("\nsolution:", data['solution'])
        return data['solution'].replace(" ", "")

def getJsonFiles(original_file_path, GPT_file_path):
    # https://www.geeksforgeeks.org/python-read-file-from-sibling-directory/
    # https://www.geeksforgeeks.org/python-list-files-in-a-directory/
    jsonListOrig = []
    jsonListGPT = []
    # for file in os.listdir():
    #     if file.endswith(".json"):
    #         print(file)
    #         jsonList.append(file)

    # for file in os.listdir(os.path.join(path, 'algebra', 'algebra')):
    #     # print(file)
    #     if file.endswith(".json"):
    #         jsonListOrig.append(os.path.join(path, 'algebra', 'algebra', file))
    
    # for file in os.listdir(os.path.join(path, 'algebra', 'algebra', 'answers')):
    #     # print(file)
    #     if file.endswith(".json"):
    #         jsonListGPT.append(os.path.join(path, 'algebra', 'algebra', 'answers', file))
    fileCount = 0;
    if debug: invalidFileNum = 0
    for file in os.listdir(original_file_path):
        # print(file)
        # print(file[:-5] + "_answer" + file[-5:])
        
        if file.endswith(".json"):
            if os.path.exists(os.path.join(GPT_file_path, file[:-5] + "_answer" + file[-5:])):
                jsonListOrig.append(os.path.join(original_file_path, file))
                jsonListGPT.append(os.path.join(GPT_file_path, file[:-5] + "_answer" + file[-5:]))
            elif debug:
                invalidFileNum += 1
                print(file + " does not have corresponding answer file in GPT directory")
            fileCount += 1
        if fileCount % 100 == 0:
            print("Found " + str(fileCount) + " files.")
        

    if debug and invalidFileNum > 0: print("Found " + str(invalidFileNum) + " files that do not have corresponding answer file in GPT directory. Find them or something idk")
    
    # for file in os.listdir(GPT_file_path):
    #     if file.endswith(".json"):
    #         jsonListGPT.append(os.path.join(GPT_file_path, file))

    return (jsonListOrig, jsonListGPT)

def extractAnswer(string):
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
        return "error"

def gradeFiles(original_file_path, GPT_file_path): 
    (orig, gpt) = getJsonFiles(original_file_path, GPT_file_path)

    print("\n\nMatching Answers Now\n\n")
    for i in range(len(orig)):
        (originalFile, GPTFile) = (orig[i], gpt[i])

        if debug: print("Original File: " + originalFile)
        correctSolution = extractAnswer(openJsonFile(originalFile))
        if debugOnlyFinalAnswer or debug: print("Answer from Original: " + str(correctSolution))

        if debug: print("\nGPT File: " + GPTFile)
        GPTSolution = extractAnswer(openJsonFile(GPTFile))
        if debugOnlyFinalAnswer or debug: print("Answer from ChatGPT : " + str(GPTSolution) + "\n")
        
        if debug: print("\n---------------------------------\n")
        
        score(correctSolution, GPTSolution)

    print("Matching Answers: " + str(correctNum) 
        + "\nWrong Answers   : " + str(wrongNum))

def main():
    global correctNum 
    global wrongNum
    global debug
    global debugOnlyFinalAnswer
    correctNum = 0
    wrongNum = 0
    debug = True
    debugOnlyFinalAnswer = False
    if debugOnlyFinalAnswer: debug = False
    
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
