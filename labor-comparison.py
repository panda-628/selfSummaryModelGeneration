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

import fileCompareSemantic

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
    prompt1 = PROMPT_MODEL_TEACHER_GUIDE_WITH_ERRORS.format(description,correct_answer,error_list)
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
    path = file['path']
    os.chdir(path)

    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime('%Y-%m-%d-%H-%M-%S')
    system_name = SYSTEM_NAME
    new_folder = 'Labor-comparison'+ '-' + system_name + '-' +running_params['llm'] + formatted_datetime
    os.mkdir(new_folder)

    cycle = running_params['cycle']
    #cycle = 1

    baseline_file = f'{path}/{new_folder}/baseline.csv'
    ours_file = f'{path}/{new_folder}/ours.csv'

    f_baseline_file = open(baseline_file,'w',encoding='UTF-8')
    f_ours_file = open(ours_file,'w',encoding='UTF-8')
    
    for c in range(1,cycle+1):
        #generate baseline prompt
        description = DESCRIPTION
        prompt_list = generate_baseline_prompt(description)
        error_list = []

        AI_answer = run_llm(prompt_list,running_params['llm'],running_params['temperature'])
        #print("初始prompt生成的内容: ",AI_answer)
        print(f'---------------------{c}/{cycle}---------:',file=f_baseline_file)
        print(f'Base_AI_answer:{AI_answer}',file=f_baseline_file)

        #将AI生成的结果转换为json文件
        output_json_file_path = 'C:/AppAndData/codeAndproject/selfSummaryModelGeneration/baseline/CeIO.json'
        output_json_file = open(output_json_file_path,'w',encoding='UTF-8')
        convert_string_to_json(AI_answer,output_json_file)
        output_json_file.close()

        #调用fileCopmare.py中的函数进行比较
        oracle_file_path = 'C:/AppAndData/codeAndproject/selfSummaryModelGeneration/oracle/CeIOoracle.json'
        # f_oracle_file = open(oracle_file_path,'r',encoding='UTF-8')
        #语法相似度比较
        #error_list = fileCompare.main(output_json_file_path,oracle_file_path)
        #语义相似度比较
        error_list = fileCompareSemantic.main(output_json_file_path,oracle_file_path)
        #print("错误列表: ",error_list)

        #summary the rules
        correct_answer = CORRECT_ANSWER
        prompt_summary = generate_summary_prompt(description,correct_answer,error_list)
        summary_rules = run_llm(prompt_summary,running_params['llm'],running_params['temperature'])
        #print("总结的规则: ",summary_rules)
        print(f'---------------------{c}/{cycle}---------:',file=f_ours_file)
        print("error_list:",error_list,file=f_ours_file)
        print(f'Summary_rules:{summary_rules}',file=f_ours_file)

        #generate improved results
        prompt_improve = generate_improve_prompt(summary_rules,description)
        improve_result = run_llm(prompt_improve,running_params['llm'],running_params['temperature'])
        #print("改进后的结果: ",improve_result)
        print(f'Improve_result:{improve_result}',file=f_ours_file)
    
    f_baseline_file.close()
    f_ours_file.close()

    print("十次实验完成！")



if __name__ == '__main__':
    main()