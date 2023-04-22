import subprocess
import sys
import os

def main():
    # if len(sys.argv) < 2:
    #     # also make sure the files are named appropriately
    #     raise Exception("Need more arguments, Usage: python3 118GPT_autograding_script.py <path/to/folder/containing/all/math/topic/folders/> <output_file_base_name> [debug_level]")
    debugLevel = "0"
    # if len(sys.argv) > 3:    
    #     debugLevel = sys.argv[3] if sys.argv[3].isnumeric() else debugLevel
    ''' 
    gets file paths, amount depending on option chosen
    for each folder (algebra, counting_and_probability, geometry, intermediate_algebra, number_theory, prealgebra, precalculus)
    run autograding script
    add results
    print results
    save results
    command line input is folder holding everything, output file base name, debug level
    '''
    math_topics = ["algebra", "counting_and_probability", "geometry", "intermediate_algebra", "number_theory", "prealgebra", "precalculus"]
    # file_base_name  = sys.argv[2] #"test_results.txt"
    # args = sys.argv[1:]
    # rootdir = sys.argv[1]

    folder_structure = ""
    while folder_structure != "y" and folder_structure != "n":
        folder_structure = input("Are the chatgpt answers a subfolder of a folder containing the original dataset's json files? (y/n): ")
    
    if folder_structure == "y":
        print("havent checked to see if this works yet, will do later, had to make the other method to deal with some new file structures i hadn't thought of")
        while not os.path.exists(rootdir):
            print("not checking for errors in your typing so please spell stuff correctly")
            rootdir = input("Please enter the path to the folder containing everything: ")
            file_base_name = input("Please enter the base name of the file to save the results in (ex: test_results (don't add .txt)): ")
            debugLevel = input("Please enter the debug level (0-4) for the results: ")
            answersInSameDirectory(math_topics, rootdir, file_base_name, debugLevel)
    else:
        rootdir = input("Please enter the path to the folder containing dataset answers: ")
        gptanswers = input("Please enter the path to the folder containing chatGPT's answers: ")
        file_base_name = input("Please enter the base name of the file to save the results in (ex: test_results (don't add .txt)): ")
        debugLevel = input("Please enter the debug level (0-4) for the results: ")
        answersInDiffDirectory(math_topics, rootdir, gptanswers, file_base_name, debugLevel)    

    # args_for_autograder = []
    '''for subdir, dirs, files in os.walk(rootdir):
        for dir in dirs:
            # find the math topics folders
            if dir in math_topics:
                # print(os.path.join(subdir, dir))
                args_for_autograder.append(os.path.join(subdir, dir))
                # looks for subdirectory called /answers/
                for subsubdir, subdirs, files in os.walk(os.path.join(subdir, dir)):
                    for answersubdir in subdirs:
                        # change this if the answers folder is not named answers
                        if answersubdir == "answers":
                            # print(os.path.join(subsubdir, answersubdir))
                            args_for_autograder.append(os.path.join(subsubdir, answersubdir))
                            # print(args_for_autograder)
                            args_for_autograder.append(debugLevel)
                            output_file = file_base_name + "_" + dir + ".txt"
                            print("Running autograder for " + dir + " in " + rootdir + " with output file: " + output_file)
                            run_autograder(args_for_autograder, output_file)
                            print("Finished running autograder for " + dir + " in " + rootdir + "\n")
                            args_for_autograder.clear()
                            break
                # couldn't find answers folder, clear args
                if len(args_for_autograder) < 2:
                    args_for_autograder.clear()'''
    print("Finished running autograder for all topics in " + rootdir)
    print("Adding the results for each folder...\n")
    '''
    for each test file
    extract result at the end of all the files
    and add them together
    output result in file_base_name.txt
    '''
    # find output files in this directory
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
            # print(file)
            # open file and get result at the end
            with open(file, "r") as f:
                # hardcoding this since it is hardcoded to print these out
                lines = f.readlines()
                if debugLevel != "0":
                    lines_subset = lines[-11:-8] + lines[-7:-3]
                    # print(lines_subset)
                else:
                    # no debug lines
                    lines_subset = lines[:3] + lines[4:]
                    # print(lines_subset)
                scores = calculate_score(lines_subset)
                totalMatchWFail += scores[0][0]
                fullTotalWFail += scores[0][1]
                totalMatchNoFail += scores[1][0]
                fullTotalNoFail += scores[1][1]
                failedExtractionCount += scores[2]
                output_to_file(result_file, lines_subset, scores, file)
                # add to total
                # with open(file_base_name + ".txt", "a") as g:
                #     g.write(f.readlines()[-1])
            # remove so no duplicates are added (why are they there in the first place?)
            math_topics_file_names.remove(file)
    with open(result_file, "a") as f:
        f.write("Total:" + "\n")
        f.write(str(totalMatchWFail) + "/" + str(fullTotalWFail) + " ~= " 
                + str(0 if fullTotalWFail == 0 else totalMatchWFail / fullTotalWFail)[:tdp] + " = " + str(0 if fullTotalWFail == 0 else totalMatchWFail / fullTotalWFail * 100)[:tdp] + "%\n\n")
        f.write("Total if Ignoring " + str(failedExtractionCount) + " Failed Extractions:"  + "\n")
        f.write(str(totalMatchNoFail) + "/" + str(fullTotalNoFail) + " ~= " 
                + str(0 if fullTotalNoFail == 0 else totalMatchNoFail / fullTotalNoFail)[:tdp] + " = " + str(0 if fullTotalWFail == 0 else totalMatchNoFail / fullTotalNoFail * 100)[:tdp] + "%\n")

    print("Results are in: " + file_base_name + ".txt" + "\n")
    # print(args_for_autograder)
    # for folder_name in math_topics:
    #     output_file = "test_results_" + folder_name + ".txt"
    #     run_autograder(args_for_autograder, output_file)

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
            # print(dir)
            # find the math topics folders
            if dir in math_topics:
                # print(os.path.join(subdir, dir))
                args_for_autograder.append(os.path.join(subdir, dir))
                for gptsubdir, gptdirs, files in os.walk(gptanswers): #datasets/persona_short_answer/persona_short_answer
                    for gptdir in gptdirs:
                        if gptdir == dir:
                            args_for_autograder.append(os.path.join(gptsubdir, gptdir))
                            args_for_autograder.append(debugLevel)
                            output_file = file_base_name + "_" + dir + ".txt"
                            # print(args_for_autograder)
                            print("Running autograder for " + dir + " in " + answers + " with output file: " + output_file)
                            run_autograder(args_for_autograder, output_file)
                            print("Finished running autograder for " + dir + " in " + answers + "\n")
                            args_for_autograder.clear()
                            break
                    # print(gptsubdir)
                # couldn't find answers folder, clear args
                if len(args_for_autograder) < 2:
                    args_for_autograder.clear()
                    
                #     for answersubdir in gptdirs:
                #         # change this if the answers folder is not named answers
                #         if answersubdir == "answers":
                #             # print(os.path.join(subsubdir, answersubdir))
                #             args_for_autograder.append(os.path.join(subsubdir, answersubdir))
                #             # print(args_for_autograder)
                #             args_for_autograder.append(debugLevel)
                #             output_file = file_base_name + "_" + dir + ".txt"
                #             print("Running autograder for " + dir + " in " + rootdir + " with output file: " + output_file)
                #             run_autograder(args_for_autograder, output_file)
                #             print("Finished running autograder for " + dir + " in " + rootdir + "\n")
                #             args_for_autograder.clear()
                #             break
                # # couldn't find answers folder, clear args
                # if len(args_for_autograder) < 2:
                #     args_for_autograder.clear()

def answersInSameDirectory(math_topics, rootdir, debugLevel, file_base_name):
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
                # print(os.path.join(subdir, dir))
                args_for_autograder.append(os.path.join(subdir, dir))
                # looks for subdirectory called /answers/
                for subsubdir, subdirs, files in os.walk(os.path.join(subdir, dir)):
                    for answersubdir in subdirs:
                        # change this if the answers folder is not named answers
                        if answersubdir == "answers":
                            # print(os.path.join(subsubdir, answersubdir))
                            args_for_autograder.append(os.path.join(subsubdir, answersubdir))
                            # print(args_for_autograder)
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

def calculate_score(lines):
    '''
    calculate score based on the file name
    '''
    matchingWithFails = int(''.join(filter(str.isdigit, lines[0])))
    # wrongWithFails = ''.join(filter(str.isdigit, lines[1]))
    totalWithFails = int(''.join(filter(str.isdigit, lines[2])))
    # scoreWithFails = '' + str(int(matchingWithFails) / int(totalWithFails))

    failedExtractionCount = int(''.join(filter(str.isdigit, lines[3])))

    matchingNoFails = int(''.join(filter(str.isdigit, lines[4])))
    # wrongNoFails = ''.join(filter(str.isdigit, lines[5]))
    totalNoFails = int(''.join(filter(str.isdigit, lines[6])))
    # scoreNoFails = '' + str(int(matchingNoFails) / int(totalNoFails))

    return ((matchingWithFails, totalWithFails), (matchingNoFails, totalNoFails), failedExtractionCount)

def output_to_file(file_name, lines, scores, file):
    with open(file_name, "a") as f:
        f.write("File: " + file + "\n\n")
        scoreWithFails = 0 if scores[0][1] == 0 else (scores[0][0]) / float(scores[0][1])
        f.write(lines[0] + lines[1] + lines[2] + "\n" + str(scores[0][0]) + "/" + str(scores[0][1]) 
                + " ~= " + str(scoreWithFails)[:tdp] + " = " +  str(scoreWithFails * 100)[:tdp] + "%\n\n")
        scoreNoFails = 0 if scores[1][1] == 0 else (scores[1][0]) / float(scores[1][1]) 
        f.write(lines[3] + lines[4] + lines[5] + lines[6] + "\n" + str(scores[1][0]) + "/" + str(scores[1][1]) 
                + " ~= " + str(scoreNoFails)[:tdp] + " = " +  str(scoreNoFails * 100)[:tdp] + "%\n")
        f.write("\n\n-------------------------\n\n")
    
def run_autograder(args, output_file):
    with open(output_file, "w") as f:
        # replace with python directory, you could use "which python" (this is what i used to find it)
        # print(args)
        subprocess.run(["/usr/bin/python3", "autograder_118.py"] + args, stdout=f)

if __name__ == "__main__":
    # truncate decimalplace
    global tdp
    tdp = 6
    main()