import csv
import datetime
import re
import time
from openai import OpenAI
import openai
from config import *
import os
import fileCompare
import json

PROMPT_MODEL_TEACHER_GUIDE_WITH_ERRORS="""
You are a highly experienced professer in software engineering, teaching object-oriented class diagram modeling. You are reviewing (<Student Answers>) according to the (<System Description>) and (<Referenced Answer>). Generate some modeling rules that are not only accurate but also practical and easy for students to apply by summarizing the correct and the incorrect answers.

Let's do it step by step.

# Steps
1. Note that your goal is to help students to manage modeling methodology, rather than correcting a specific error.
2. Based on the errors given, inductively summarize common rules for OO modelings.
3. Ensure that the rules you generate are clear, concise, and easy to understand. The rules should be general enough to be applicable to all types of OO models, regardless of the specific application domain. 
4. DO NOT use concrete examples in rule descriptions. 

# Output Format
Output the final rules in the following format.
```rule
+ Rule 1: <What should or can be done>
+ Rule 2: <What cannot be done>
```

# System Description
{}

# Referenced Answer
{}

# Students' Errors
{}

"""

PROMPT_MODEL_TEACHER_GUIDE_WITH_ERRORS_V2="""
You are a highly experienced professor in software engineering, specializing in object-oriented class diagram modeling. Your task is to review the following student responses based on the provided system description and referenced answer. The goal is to generate a set of clear and practical modeling rules that students can easily apply, focusing on improving their understanding of modeling methodology rather than correcting individual errors.

# Steps
1. Your objective is to help students grasp modeling principles rather than focus solely on their mistakes.
2. Analyze the common errors presented and derive general rules for object-oriented modeling.
3. Ensure the rules are clear, concise, and easily understandable. They should be broadly applicable to various object-oriented models, regardless of the specific context.
4. Avoid using concrete examples in the rules.

# Output Format
Output the final rules in the following format.
```rule
+ Rule 1: <What should or can be done>
+ Rule 2: <What cannot be done>
```

# System Description
{}

# Referenced Answer
{}

# Students' Errors
{}
"""

PROMPT_MODEL_INIT="""
Create a class diagram for the following description by giving the enumerations, classes, and relationships using PlantUML format:

#Description 
{}
"""

PROMPT_MODEL_IMPROVE="""
Create a class diagram for the following description by giving the enumerations, classes, and relationships using PlantUML format:(Note: Follow the Rules given during the generation process)

#Rules
{}

#Description 
{}
"""

#system description
DESCRIPTION = """
The LabTracker software helps (i) doctors manage the requisition of tests and examinations for patients and (ii) patients book appointments for tests and examinations at a lab. For the remainder of this description, tests and examinations are used interchangeably. 

For a requisition, a doctor must provide their numeric practitioner number and signature for verification as well as their full name, their address, and their phone number. The signature is a digital signature, i.e., an image of the actual signature of the doctor. Furthermore, the doctor indicates the date from which the requisition is valid. The requisition must also show the patient’s information including their alpha-numeric health number, first name and last name, date of birth, address, and phone number. A doctor cannot prescribe a test for themselves but can prescribe tests to someone else who is a doctor. 

Several tests can be combined on one requisition but only if they belong to the same group of tests. For example, only blood tests can be combined on one requisition or only ultrasound examinations can be combined. It is not possible to have a blood test and an ultrasound examination on the same requisition. For each test, its duration is defined by the lab network, so that it is possible to schedule appointments accordingly. The duration of a test is the same at each lab. For some kinds of tests, it does not matter how many tests are performed. They take as long as a single test. For example, several blood tests can be performed on a blood sample, i.e., it takes as long to draw the blood sample for a single blood test as it does for several blood tests. 

A doctor may also indicate that the tests on a requisition are to be repeated for a specified number of times and interval. The interval is either weekly, monthly, every half year, or yearly. All tests on a requisition are following the same repetition pattern. 

The doctor and the patient can view the results of each test (either negative or positive) as well as the accompanying report. 

A patient is required to make an appointment for some tests while others are walk-in only. For example, x-ray examinations require an appointment, but blood tests are walk-in only (i.e., it is not possible to make an appointment for a blood test). On the other hand, some tests only require a sample to be dropped off (e.g., a urine or stool sample). 

To make an appointment for a requisition, a patient selects the desired lab based on the lab’s address and business hours. For requisitions with repeated tests, a patient is only allowed to make one appointment at a time. The confirmation for an appointment also shows a confirmation number, the date as well as start/end times, and the name of the lab as well as its registration number. It is possible to change or cancel an appointment at any time but doing so within 24 hours of the appointment incurs a change/cancellation fee. Each lab determines its own fee and business hours. All labs are open every day of the year and offer all tests. The business hours of a lab do not change from one week to the next. Each day a lab is open from the day’s start time to its end time, i.e., there are no breaks. 
"""

#correct answer
CORRECT_ANSWER = """
classDiagram
    enum Interval {
        weekly
        monthly
        everyHalfYear
        yearly
    }
    enum AccessType {
        reservable
        walkIn
        dropOff
    }
    enum DayOfWeek {
        Monday
        Tuesday
        Wednesday
        Thursday
        Friday
        Saturday
        Sunday
    }
    class Patient {
        - dateOfBirth: string
    }
    class Doctor {
        - signature: string
    }
    class Requisition {
        - effectiveDate: string
        - repetitionCount: int
        - repetitionInterval: Interval
    }
    class TestResult {
        - negative: boolean
        - report: string
    }
    class SpecificTest {
        - date: Data
    }
    class Appointment {
        - confirmation: string
        - date: Date
        - startTime: string
        - endTime: string
    }
    class BusinessHour {
        - dayOfWeek: DayOfWeek
        - startTime: string
        - endTime: string
    }
    class Lab {
        - registrationNumber: string
        - name: string
        - address: string
        - changeCancelFee: boolean
    }
    class Test {
        - name: string
        - duration: string
    }
    class TestType {
        - name: string
        - durationAdditive: string
        - access: AccessType
    }
    Patient "1" -- "*" Requisition : associate
    Requisition "*" -- "*" Appointment : associate
    Appointment "*" -- "1" Lab : associate
    Doctor "1" -- "*" Requisition : associate
    Requisition "1" -- "*" SpecificTest : associate
    TestResult "0..1" -- "*" SpecificTest : associate
    Lab "1" -- "7" BusinessHour : associate
    Test "1" -- "*" SpecificTest : associate
    TestType "1" -- "*" Test : associate
"""

#generate baseline prompt
def generate_baseline_prompt(description):
    prompt_list = {
        'prompt':''
    }
    message = []
    prompt1 = PROMPT_MODEL_INIT.format(description)
    message = [
        {"role":"system","content":"Generate the lists of model classes and associations from a given description. There are only 3 types of associations: associate, inherit, contain. Do not use other name for associations."},
        {"role":"user","content":f"{prompt1}"},
    ]
    prompt_list['prompt'] = message

    return prompt_list

def generate_summary_prompt(description,correct_answer,error_list):
    prompt_list = {
        'prompt':''
    }
    message = []
    prompt1 = PROMPT_MODEL_TEACHER_GUIDE_WITH_ERRORS_V2.format(description,correct_answer,error_list)
    message = [
        {"role":"system","content":"Based on the above errors and the results of the analysis, summarize some rules to follow when generating enums, classes, and relationships."},
        {"role":"user","content":f"{prompt1}"},
    ]
    prompt_list['prompt'] = message

    return prompt_list

def generate_improve_prompt(simplify_rules,description):
    prompt_list = {
        'prompt':''
    }
    message = []
    prompt1 = PROMPT_MODEL_IMPROVE.format(simplify_rules,description)
    message = [
        {"role":"system","content":"Based on the above rules, improve the generated content to avoid the errors in the future"},
        {"role":"user","content":f"{prompt1}"},
    ]
    prompt_list['prompt'] = message

    return prompt_list

def convert_string_to_json(input_string, output_file_path):
        # 初始化数据结构
    data = {
        "enumeration": {},  # 确保这是一个字典
        "class": {},        # 确保这是一个字典
        "relationships": []
    }

    # 处理 PlantUML 输入字符串
    lines = input_string.strip().splitlines()
    current_section = None

    for line in lines:
        line = line.strip()
        
        # 检查是否进入不同的部分
        if line.startswith('@startuml'):
            continue  # 跳过开始标记
        elif line.startswith('enum'):
            # 记录枚举名称
            enum_name = line.split()[1]
            current_section = 'enumeration'
            data["enumeration"][enum_name] = []  # 初始化枚举属性列表
            continue
        elif line.startswith('class'):
            # 记录类名称
            class_name = line.split()[1]
            current_section = 'class'
            data["class"][class_name] = []  # 初始化类属性列表
            continue
        elif "--" in line or "-->" in line:
            current_section = 'relationships'
        elif line.startswith('@enduml'):
            break  # 跳过结束标记
        
        # 处理枚举
        if current_section == 'enumeration':
            if line.endswith('{'):
                continue  # 跳过开始的 '{'
            elif line == '}':
                continue  # 跳过结束的 '}'
            data["enumeration"][enum_name].append(line.strip())
        
        # 处理类
        elif current_section == 'class':
            if line.endswith('{'):
                continue  # 跳过开始的 '{'
            elif line == '}':
                continue  # 跳过结束的 '}'
            data["class"][class_name].append(line.strip())
        
        # 处理关系
        elif current_section == 'relationships':
            data["relationships"].append(line)
    # 将数据写入 JSON 文件
    #with open(output_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(data, output_file_path, indent=4, ensure_ascii=False)

    print(f"JSON 文件已保存为 {output_file_path}")
    
def run_llm(prompt_list,llm,temperature):
    client = OpenAI(
        api_key="sk-BV2aBFTlr7PelZvY422PqkmFsIctGFiCMufuBSgOqXKu7QVR",
        base_url="https://www.dmxapi.com/v1",
    )

    prompt = prompt_list['prompt']

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt[-1]['content']        
        }
        ],
        model="gpt-3.5-turbo-0125",
    )
    #print(chat_completion)
    return chat_completion.choices[0].message.content

def main():
    #在指定路径下创建一个文件夹
    baseline_path = file['baseline']
    os.chdir(baseline_path)

    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime('%Y-%m-%d-%H-%M-%S')
    new_baseline_folder = 'baseline'+'-'+running_params['llm'] + 'givenErrors' + formatted_datetime
    os.mkdir(new_baseline_folder)

    ours_path = file['ours']
    os.chdir(ours_path)

    new_ours_folder = 'ours'+'-'+running_params['llm'] + 'givenErrors' + formatted_datetime
    os.mkdir(new_ours_folder)

    baseline_file = f'{baseline_path}/{new_baseline_folder}/baseline.csv'
    ours_file = f'{ours_path}/{new_ours_folder}/ours.csv'

    f_baseline_file = open(baseline_file,'w',encoding='UTF-8')
    f_ours_file = open(ours_file,'w',encoding='UTF-8')

    #generate baseline prompt
    description = DESCRIPTION
    prompt_list = generate_baseline_prompt(description)
    error_list = []

    AI_answer = run_llm(prompt_list,running_params['llm'],running_params['temperature'])
    print("初始prompt生成的内容: ",AI_answer)
    print(f'Base_AI_answer:{AI_answer}',file=f_baseline_file)

    #将AI生成的结果转换为json文件
    output_json_file_path = 'C:/AppAndData/codeAndproject/modelGeneratelab/baseline/LBTK.json'
    output_json_file = open(output_json_file_path,'w',encoding='UTF-8')
    convert_string_to_json(AI_answer,output_json_file)
    output_json_file.close()

    #调用fileCopmare.py中的函数进行比较
    oracle_file_path = 'C:/AppAndData/codeAndproject/modelGeneratelab/oracle/LBTKoracle.json'
    # f_oracle_file = open(oracle_file_path,'r',encoding='UTF-8')
    error_list = fileCompare.main(output_json_file_path,oracle_file_path)
    print("错误列表: ",error_list)

    #summary the rules
    correct_answer = CORRECT_ANSWER
    prompt_summary = generate_summary_prompt(description,correct_answer,error_list)
    summary_rules = run_llm(prompt_summary,running_params['llm'],running_params['temperature'])
    print("总结的规则: ",summary_rules)
    print(f'Summary_rules:{summary_rules}',file=f_ours_file)

    #generate improved results
    prompt_improve = generate_improve_prompt(summary_rules,description)
    improve_result = run_llm(prompt_improve,running_params['llm'],running_params['temperature'])
    print("改进后的结果: ",improve_result)

    print(f'Improve_result:{improve_result}',file=f_ours_file)
    
    f_baseline_file.close()
    f_ours_file.close()


if __name__ == '__main__':
    main()