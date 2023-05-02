import subprocess
import os
import shutil
import glob

def main():
    '''
    run script that get's gpt's answers
    then run autograding pipeline
    '''
    # get gpt's answers (this will take a bit)
    settings = get_Settings()
    get_answer_script = settings["answer_script"]
    try:
        subprocess.run(["/usr/bin/python3", get_answer_script], check=True)
    except subprocess.CalledProcessError as e:
        print("An error occurred:", e)

    # now run autograding
    # done: wait gotta check that global truncate variable
    subprocess.run(["/usr/bin/python3", "118GPT_autograding_script.py", "grouped", settings["grade_folder"], settings["file_base_name"], settings["debug_level"]])
  
    # path
    path = os.getcwd() + "/" + settings["file_base_name"] + "/"
    
    try:
        os.mkdir(path)
    except OSError as error:
        print(error)
        print("Moving result files into found directory.") 
    
    dst_folder = moveFilesToFolder(settings["file_base_name"], path)

    print("Done! Check the results in the folder: " + dst_folder)

def moveFilesToFolder(file_base_name, path):
    '''
    move all files whose name starts with file base name
    '''
    src_folder = r""+os.getcwd() + "/"
    dst_folder = r""+path
    # print(dst_folder)
    # move file whose name starts with file base name
    pattern = src_folder + "/" + file_base_name + "*"
    for file in glob.iglob(pattern, recursive=True):
        # extract file name from file path
        if os.path.isdir(file):
            continue
        file_name = os.path.basename(file)
        shutil.move(file, dst_folder + file_name)
        # print('Moved:', file)
    return dst_folder

def get_Settings():
    print("This program will change your \"\\\" automatically to a \"/\" (this is for me to easily copy and paste the file paths)")
    ans = input("Enter the name of the script that gets gpt's answers: ")
    ans = ans.replace("\\", "/")
    debugLevel = input("Enter the debug level (0-4): ")
    folder_that_has_the_test_files_and_solutions = input("Enter the folder that has the test files and solutions (should be the same one that you have in the script that gets GPT's answers): ")
    folder_that_has_the_test_files_and_solutions = folder_that_has_the_test_files_and_solutions.replace("\\", "/")
    file_base_name = input("Please enter the base name of the file to save the results in (ex: test_results (don't add .txt)): ")
    return {
        "answer_script": ans,
        "debug_level": debugLevel,
        "grade_folder": folder_that_has_the_test_files_and_solutions,
        "method": "grouped",
        "file_base_name": file_base_name
    }

if __name__ == "__main__":
    # moveFilesToFolder("deleteThis", os.getcwd() + "/" + "deleteThis" + "/")
    main()