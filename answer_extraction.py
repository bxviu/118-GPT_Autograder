import re
import math_equivalence as m_eq
import util

def extractInside(string):
    if '\\boxed' in string:
        return extractInside(handle_boxed(string))
    elif "\\frac" in string or "\\dfrac" in string:
        return extractInside(handle_frac(string))
    elif "\\sqrt" in string:
        return extractInside(handle_sqrt(string))
    elif "\\text" in string:
        return extractInside(handle_text(string))
    else: 
        return handle_singleItem(string)

def extractAnswer(string, level, ):
    global debugLevel
    debugLevel = level
    if debugLevel > 3: print("Extracting Answer from: \n" + string + "\n")
    #recursively check inside boxed for commands
    string = m_eq._strip_string(string)
    if debugLevel > 3: print("Stripped String: \n" + string + "\n")
    return extractInside(string.replace("\n", "").replace("\\end{align*}", "").replace("\\begin{align*}", ""))

def handle_singleItem(string):
    string = string.replace("%", "").replace("$", "").replace(" ", "").replace("\'", "").replace("\"", "").replace("`", "").replace("\\", "")
    if debugLevel > 3: print("Removing %,$, ,\\n,\',\",`,\\: \n" + string + "\n")
    # hopefully deal with answers such as "2." which should just be "2"
    if string[-1:] == ".":
        return string[:-1]
    return string

def handle_text(string):
    pattern = r'(.*)?\\text{((?:[^{}]*{[^{}]*}*){0,%d}[^{}]*)}(.*)?' % count_opening_braces(string)
    matches = re.findall(pattern, string)
    # print(len(matches))
    if len(matches) != 0:
        # print(matches)
        result = extractInside(str(matches[0][0])) + extractInside(str(matches[0][1])) + extractInside(str(matches[0][2]))
    else:
        result = string
    return result

def handle_sqrt(string):
    pattern = r'(.*)?\\sqrt{((?:[^{}]*{[^{}]*}*){0,%d}[^{}]*)}(.*)?' % count_opening_braces(string)
    matches = re.findall(pattern, string)
    # print(len(matches))
    try:
        if len(matches) != 0:
            # print(matches)
            result = extractInside(str(matches[0][0])) + "sqrt("
            result += extractInside(str(matches[0][1])) + ")"
            result += extractInside(str(matches[0][2]))
        else:
            pattern = r'(.*)?\\sqrt(\d+)(.*)?'
            matches = re.findall(pattern, string)
            # print(str(matches))
            result = extractInside(str(matches[0][0])) + "sqrt("
            result += extractInside(str(matches[0][1])) + ")"
            # if they forget parenthesis like in "\\sqrt7" from algebra #1239, i doubt there will be another number multiplied after it
            result += extractInside(str(matches[0][2]))
        return result
    except:
        return "Extraction Failed"

def handle_boxed(string):

    # pattern = r'\\boxed{.*}'
    # matches = list(set(re.findall(pattern, string)))
    # if debugLevel > 2: print("Found Answer in String: " + matches[0])
    # pattern = r'\\boxed{((?:[^{}]*{[^{}]*}*){0,%d}[^{}]*)}' % count_opening_braces(string)
    # # get rid of duplicates of same answer
    # matches = list(set(re.findall(pattern, string)))
    # # get rid of answers within a large block of text that the regex matched with
    # answersWithin = []
    # # this should be the real answer, rest is the same, but with unneeded text
    # shortestAnswer = min(matches, key=len)
    # for answer in matches:
    #     if shortestAnswer in answer:
    #         continue
    #     answersWithin.append(answer)
    # answersWithin.append(shortestAnswer)
    # matches = answersWithin
    

    ans = util.last_boxed_only(string)
    # ans = m_eq._strip_string(ans)
    # print("got " + ans + "|")
    # def remove_boxed(s): from https://github.com/hendrycks/math/blob/main/modeling/evaluate_gpt3.py
    left = "\\boxed{"
    try:
        assert ans[:len(left)] == left
        assert ans[-1] == "}"
        return ans[len(left):-1]
    except:
        return "Extraction Failed"

    # return ""
    # if debugLevel > 1: print("Extracted Answer: " + str(matches))
    # if len(matches) > 1:
    #     # if debugLevel > 0:
    #         # addErrorFile("Multiple Answers")
    #     if debugLevel > 1: 
    #         print("why is there more than one answer in the solution file??? -  " + str(matches) 
    #         + "\nGoing to use answer in 0th index.")
    # if len(matches) < 1:
    #     # if debugLevel > 0: 
    #         # addErrorFile("No Answer")
    #     if debugLevel > 1:
    #         print("why is no answer???")
    # result = ''.join(x for x in matches[0] if x != "\\")
        # Assuming that {} contains numbers that are part of a function now, like sqrt{324} becomes sqrt(324)
        # result = result.replace("{", "(").replace("}", ")").replace("\\","")
        # if debugLevel > 2: print("Replacing {} with () and removing \\: " + result)
    # return matches[0]

def handle_frac(string):
    try:
        pattern = r'(-?).*?{(.*)}{(.*)}'
        fractionNums = re.findall(pattern, string)
        if len(fractionNums) != 0:
            if debugLevel > 1: print("Found Fraction: " + str(fractionNums))
            # formatting numerator
            if (fractionNums[0][1].isnumeric()):
                result = extractInside(fractionNums[0][1])
            else:
                result = "(" + extractInside(fractionNums[0][1]) + ")"
            result += "/"
            # formatting denominator
            if (fractionNums[0][2].isnumeric()):
                result += extractInside(fractionNums[0][2])
            else:
                result += "(" + extractInside(fractionNums[0][2]) + ")"
            if fractionNums[0][0] == "-":
                result = "-" + result
        else:
            pattern = r'(-?)[\\A-Za-z_]+(\d+)'
            fractionNums = re.findall(pattern, string)
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
        # Assuming that {} contains numbers that are part of a function now, like sqrt{324} becomes sqrt(324)
        # result = result.replace("{", "(").replace("}", ")").replace("\\","")
        # if debugLevel > 2: print("Replacing {} with () and removing \\: " + result)
        return result
    except:
        # if debugLevel > 0: addErrorFile("Extraction Failed")
        return "Extraction Failed"
    # elif 'frac{' in string:
    #         try:
    #             pattern = r'(-?).*?{(.*)}{(.*)}'
    #             fractionNums = re.findall(pattern, string)
    #             if debugLevel > 1: print("No \"\\boxed{}\" Format but Found Fraction: " + str(fractionNums))
    #             result = str(fractionNums[0][1]) + "/" + str(fractionNums[0][2])
    #             if fractionNums[0][0] == "-":
    #                 result = "-" + result
    #             if debugLevel > 2: print("Replacing {} with (): " + string)
    #             return result.replace("{", "(").replace("}", ")")
    #         except:
    #             if debugLevel > 0: addErrorFile("Extraction Failed")
    #             return "Extraction Failed"

def count_opening_braces(s):
    count = 1
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
