
import pandas as pd

def create_expected_excel():
    data = {
        'Question': ['What is the function of the `git rebase` command in Git?'],
        'Options': ['Merge branches, Create new branch, Modify commit history, Delete branch'],
        'Answer': ['Modify commit history'],
        'Analysis': ['STAR method analysis example: (S) Situation: Under what circumstances... (T) Task: What was your specific task... (A) Action: What steps did you take... (R) Result: What was the final outcome...'],
        'Competency Dimension': ['Professional Knowledge'],
        'Difficulty': ['Intermediate'],
        'Question Type': ['Single Choice']
    }
    df = pd.DataFrame(data)
    df.to_excel("C:\\Users\\wb_zhangyuan20\\Desktop\\CDT\\evaluation\\expected_question_bank.xlsx", index=False)

create_expected_excel()
