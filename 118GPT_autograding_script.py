import subprocess
import sys
import os

global tdp
tdp = 6

def main():
    ''' 
    gets file paths, amount depending on option chosen
    for each folder (algebra, counting_and_probability, geometry, intermediate_algebra, number_theory, prealgebra, precalculus)
    run autograding script
    add results
    print results
    save results
    '''
    if len(sys.argv) == 1: 
        rootdir, gptdir, file_base_name, debugLevel = getManualSettings()
    elif len(sys.argv) > 1:
        try: 
            rootdir, gptdir, file_base_name, debugLevel = getShortcutSettings(sys.argv[1:])
        except:
            print("\nNeed more arguments for shortcut mode. \n\nUsage:\n" + 
                            "To type in settings seperately:\n" + 
                            "python3 118GPT_autograding_script.py\n" +
                            "\nTo type in settings in the command line:\n" + 
                            "python3 118GPT_autograding_script.py grouped <path/to/folder/containing/all/math/topic/folders/> <output_file_base_name> [debug_level]\n" +
                            "python3 118GPT_autograding_script.py seperate <path/to/folder/containing/math/topic/folders/answers> <path/to/folder/containing/gpt/topic/folders/answers> <output_file_base_name> [debug_level]\n")
            return
        
    math_topics = ["algebra", "counting_and_probability", "geometry", "intermediate_algebra", "number_theory", "prealgebra", "precalculus"]
    
    if gptdir != "":
        answersInDiffDirectory(math_topics, rootdir, gptdir, file_base_name, debugLevel) 
    else:
        answersInSameDirectory(math_topics, rootdir, file_base_name, debugLevel)

    print("Finished running autograder for " + rootdir)
    print("Adding the results for each folder...\n")

    output_to_file(math_topics, file_base_name, debugLevel)

    print("Results are in: " + file_base_name + ".txt" + "\n")

def getShortcutSettings(args):
    if args[0] == "grouped":
        rootdir = args[1]
        gptdir = ""
        file_base_name = args[2]
        # just in case user meant to use the "seperate" method but forgot to change it in the command
        user_input = ""
        if os.path.exists(file_base_name):
            while user_input != "y" and user_input != "n":
                user_input = input("Did you intend to have the file name be the same as a directory? (y to continue/n to abort): ")
            if (user_input == "n"):
                raise Exception("User Aborted")
        debugLevel = args[3] if len(args) > 3 and args[3].isnumeric() else "0"
        return rootdir, gptdir, file_base_name, debugLevel
    elif args[0] == "seperate":
        rootdir = args[1]
        gptdir = args[2]
        file_base_name = args[3]
        debugLevel = args[4] if len(args) > 4 and args[4].isnumeric() else "0"
        return rootdir, gptdir, file_base_name, debugLevel
    else:
        raise Exception("Invalid arguments")

def getManualSettings():
    folder_structure = ""
    rootdir = ""
    gptdir = ""
    debugLevel = ""

    while folder_structure != "y" and folder_structure != "n":
        folder_structure = input("Are the chatgpt answers a subfolder of a folder containing the original dataset's json files? (y/n): ")

    print("This program will change your \"\\\" automatically to a \"/\" (this is for me to easily copy and paste the file paths)")
    
    if folder_structure == "y":
        while not os.path.exists(rootdir):
            rootdir = input("Please enter the path to the folder containing everything: ")
            rootdir = rootdir.replace("\\", "/")
        file_base_name = input("Please enter the base name of the file to save the results in (ex: test_results (don't add .txt)): ")
        while not debugLevel.isnumeric() or int(debugLevel) < 0 or int(debugLevel) > 4:
            debugLevel = input("Please enter the debug level (0-4) for the results: ")
    else:
        while not os.path.exists(rootdir):
            rootdir = input("Please enter the path to the folder containing dataset answers: ")
            rootdir = rootdir.replace("\\", "/")
        while not os.path.exists(gptdir):
            gptdir = input("Please enter the path to the folder containing chatGPT's answers: ")
            gptdir = gptdir.replace("\\", "/")
        file_base_name = input("Please enter the base name of the file to save the results in (ex: test_results (don't add .txt)): ")
        while not debugLevel.isnumeric() or int(debugLevel) < 0 or int(debugLevel) > 4:
            debugLevel = input("Please enter the debug level (0-4) for the results: ")

    print("Finished getting manual settings\n")

    return rootdir, gptdir, file_base_name, debugLevel

def answersInDiffDirectory(math_topics, answers, gptanswers, file_base_name, debugLevel):
    '''
    autogrades chatGPT's answer in one folder with the dataset's answer in
    a different folder. Each math topic folder contains the original dataset's 
    .json files (the stuff containing the original question and answer):

    Example:
    dataset_folder
    |
    |- math_topic1_folder (such as algebra, counting and probability, etc)
    |  |- .json files for each question and answer
    |  
    |- math_topic2_folder 
    |  |- .json files for each question
    .
    .
    . repeats until all topics are graded

    chatGPT_folder
    |
    |- math_topic1_folder (such as algebra, counting and probability, etc)
    |  |- .json files for each question and answer
    |  
    |- math_topic2_folder 
    |  |- .json files for each question
    .
    .
    . repeats until all topics are graded
    '''
    args_for_autograder = []
    for subdir, dirs, files in os.walk(answers):
        for dir in dirs:
            # find the math topics folders
            if dir in math_topics:
                args_for_autograder.append(os.path.join(subdir, dir))
                for gptsubdir, gptdirs, files in os.walk(gptanswers): # datasets/persona_short_answer/persona_short_answer
                    for gptdir in gptdirs:
                        if gptdir == dir:
                            args_for_autograder.append(os.path.join(gptsubdir, gptdir))
                            args_for_autograder.append(debugLevel)
                            output_file = file_base_name + "_" + dir + ".txt"
                            print("Running autograder for " + dir + " in " + answers + " with output file: " + output_file)
                            run_autograder(args_for_autograder, output_file)
                            print("Finished running autograder for " + dir + " in " + answers + "\n")
                            args_for_autograder.clear()
                            break
                # couldn't find answers folder, clear args
                if len(args_for_autograder) < 2:
                    args_for_autograder.clear()                 

def answersInSameDirectory(math_topics, rootdir, file_base_name, debugLevel):
    '''
    autogrades a folder structure that has master folder, 
    with each math topic folder containing the original dataset's 
    .json files (the stuff containing the original question and answer)
    and also has an answer folder within:

    Example:
    master_folder
    |
    |- math_topic1_folder (such as algebra, counting and probability, etc)
    |  |- .json files for each question and answer
    |  |- answers_for_math_topic1_folder 
    |  |  |- .json files for chatgpt's response
    |  
    |- math_topic2_folder 
    |  |- .json files for each question
    |  |- answers_for_math_topic2_folder
    |  |  |- .json files for chatgpt's response
    .
    .
    . repeats until all topics are graded
    '''
    args_for_autograder = []
    for subdir, dirs, files in os.walk(rootdir):
        for dir in dirs:
            # find the math topics folders
            if dir in math_topics:
                args_for_autograder.append(os.path.join(subdir, dir))
                # looks for subdirectory called /answers/
                for subsubdir, subdirs, files in os.walk(os.path.join(subdir, dir)):
                    for answersubdir in subdirs:
                        # change this if the answers folder is not named answers
                        if answersubdir == "answers":
                            args_for_autograder.append(os.path.join(subsubdir, answersubdir))
                            args_for_autograder.append(debugLevel)
                            output_file = file_base_name + "_" + dir + ".txt"
                            print("Running autograder for " + dir + " in " + rootdir + " with output file: " + output_file)
                            run_autograder(args_for_autograder, output_file)
                            print("Finished running autograder for " + dir + " in " + rootdir + "\n")
                            args_for_autograder.clear()
                            break
                # couldn't find answers folder, clear args
                if len(args_for_autograder) < 2:
                    args_for_autograder.clear()

def run_autograder(args, output_file):
    with open(output_file, "w") as f:
        # replace with python directory, you could use "which python" (this is what i used to find it)
        subprocess.run(["/usr/bin/python3", "autograder_118.py"] + args, stdout=f)

def output_to_file(math_topics, file_base_name, debugLevel):
    '''
    for each test file,
    extract result at the end of all the files
    and add them together,
    output result in file_base_name.txt
    '''
    totalMatchWFail = 0
    fullTotalWFail = 0
    totalMatchNoFail = 0
    fullTotalNoFail = 0
    failedExtractionCount = 0
    math_topics_file_names = [file_base_name + "_" + topic + ".txt" for topic in math_topics]
    result_file = file_base_name + ".txt"
    # clear result_file
    with open(result_file, "w") as f:
        pass
    for file in os.listdir(os.getcwd()):
        if file in math_topics_file_names:
            # open file and get result at the end
            with open(file, "r") as f:
                # hardcoding this since it is hardcoded to print these out
                lines = f.readlines()
                if debugLevel != "0":
                    lines_subset = lines[-11:-8] + lines[-7:-3]
                else:
                    # no debug lines
                    lines_subset = lines[:3] + lines[4:]
                scores = calculate_score(lines_subset)
                totalMatchWFail += scores[0][0]
                fullTotalWFail += scores[0][1]
                totalMatchNoFail += scores[1][0]
                fullTotalNoFail += scores[1][1]
                failedExtractionCount += scores[2]
                output_score_to_file(result_file, lines_subset, scores, file)
            # remove so no duplicates are added (why are they there in the first place?)
            math_topics_file_names.remove(file)
    with open(result_file, "a") as f:
        f.write("Total:" + "\n")
        f.write(str(totalMatchWFail) + "/" + str(fullTotalWFail) + " ~= " 
                + str(0 if fullTotalWFail == 0 else totalMatchWFail / fullTotalWFail)[:tdp] + " = " + str(0 if fullTotalWFail == 0 else totalMatchWFail / fullTotalWFail * 100)[:tdp] + "%\n\n")
        f.write("Total if Ignoring " + str(failedExtractionCount) + " Failed Extractions:"  + "\n")
        f.write(str(totalMatchNoFail) + "/" + str(fullTotalNoFail) + " ~= " 
                + str(0 if fullTotalNoFail == 0 else totalMatchNoFail / fullTotalNoFail)[:tdp] + " = " + str(0 if fullTotalWFail == 0 else totalMatchNoFail / fullTotalNoFail * 100)[:tdp] + "%\n")

def calculate_score(lines):
    '''
    calculate score based on the file name
    '''
    matchingWithFails = int(''.join(filter(str.isdigit, lines[0])))
    totalWithFails = int(''.join(filter(str.isdigit, lines[2])))

    failedExtractionCount = int(''.join(filter(str.isdigit, lines[3])))

    matchingNoFails = int(''.join(filter(str.isdigit, lines[4])))
    totalNoFails = int(''.join(filter(str.isdigit, lines[6])))

    return ((matchingWithFails, totalWithFails), (matchingNoFails, totalNoFails), failedExtractionCount)

def output_score_to_file(file_name, lines, scores, file):
    with open(file_name, "a") as f:
        f.write("File: " + file + "\n\n")
        # to deal with division by 0
        scoreWithFails = 0 if scores[0][1] == 0 else (scores[0][0]) / float(scores[0][1])
        f.write(lines[0] + lines[1] + lines[2] + "\n" + str(scores[0][0]) + "/" + str(scores[0][1]) 
                + " ~= " + str(scoreWithFails)[:tdp] + " = " +  str(scoreWithFails * 100)[:tdp] + "%\n\n")
        scoreNoFails = 0 if scores[1][1] == 0 else (scores[1][0]) / float(scores[1][1]) 
        f.write(lines[3] + lines[4] + lines[5] + lines[6] + "\n" + str(scores[1][0]) + "/" + str(scores[1][1]) 
                + " ~= " + str(scoreNoFails)[:tdp] + " = " +  str(scoreNoFails * 100)[:tdp] + "%\n")
        f.write("\n\n-------------------------\n\n")

if __name__ == "__main__":
    # truncate decimalplace
    # global tdp
    # tdp = 6
    main()