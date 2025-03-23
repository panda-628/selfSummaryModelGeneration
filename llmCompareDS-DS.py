import csv
import datetime
import time
from openai import OpenAI
import openai
from config import *
import os

#generate baseline prompt
def generate_baseline_prompt(description):
    prompt_list = {
        'prompt':''
    }
    message = []
    prompt1 = PROMPT_USECASE_INIT.format(description)
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
    prompt1 = PROMPT_MODEL_TEACHER_GUIDE.format(description,correct_answer,error_list)
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
    prompt1 = PROMPT_USECASE_IMPROVE.format(simplify_rules,description)
    message = [
        {"role":"system","content":"Based on the above rules, improve the generated content to avoid the errors in the future"},
        {"role":"user","content":f"{prompt1}"},
    ]
    prompt_list['prompt'] = message

    return prompt_list

def run_llm_DS(prompt_list,llm,temperature):
    client = OpenAI(
        api_key=running_params['API_KEY'],
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
    return chat_completion.choices[0].message.content

def run_llm_DS(prompt_list,llm,temperature):
    client = OpenAI(
        api_key=running_params['API_KEY'],
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
        model="gpt-4o-mini",
    )
    return chat_completion.choices[0].message.content

def main():
    baseline_path = file['compare_usecase_baseline']
    os.chdir(baseline_path)

    new_baseline_folder = 'baseline'+'-'+running_params['LLM_DS']+ '-'+ running_params['LLM_DS']
    os.mkdir(new_baseline_folder)

    ours_path = file['compare_usecase_ours']
    os.chdir(ours_path)

    new_ours_folder = 'ours'+ '-' +running_params['LLM_DS']+ '-'+ running_params['LLM_DS']
    os.mkdir(new_ours_folder)

    cycle = running_params['cycle']

    baseline_file = f'{baseline_path}/{new_baseline_folder}/baseline.csv'
    ours_file = f'{ours_path}/{new_ours_folder}/ours.csv'

    f_baseline_file = open(baseline_file,'w',encoding='UTF-8')
    f_ours_file = open(ours_file,'w',encoding='UTF-8')

    # with open(baseline_file,'w',encoding='UTF-8') as baseline_f:
    #     baseline_writer = csv.writer(baseline_f)

    # with open(ours_file,'w',encoding='UTF-8') as ours_f:
    #     ours_writer = csv.writer(ours_f)

    for c in range(1,cycle+1):
        #generate baseline prompt
        description = USE_CASE_DESCRIPTION
        prompt_list = generate_baseline_prompt(description)
        error_list = []
        for i in range(1,4):
            AI_answer = run_llm_DS(prompt_list,running_params['llm'],running_params['temperature'])
            print("初始prompt生成的内容: ",AI_answer)
            print(f'---------------------{c}/{cycle}---------{i}/3:',file=f_baseline_file)
            print(f'Base_AI_answer:{AI_answer}',file=f_baseline_file)
            error_list.append(AI_answer)

        # #compare with correct answer
        # correct_answer = CORRECT_ANSWER
        # prompt_compare = generate_compare_prompt(correct_answer)
        # error_list = run_llm(prompt_compare,running_params['llm'],running_params['temperature'])
        # print("错误的内容: ",error_list)
        # print(f'---------------------{c}/{cycle}------:',file=f_ours_file)
        # print(f'Error_list:{error_list}',file=f_ours_file)

        # #analyze the error
        # prompt_analyze = generate_analyze_prompt(error_list)
        # analyze_result = run_llm(prompt_analyze,running_params['llm'],running_params['temperature'])
        # print("分析的内容: ",analyze_result)
        # print(f'Analyze_result:{analyze_result}',file=f_ours_file)

        #summary the rules
        correct_answer = USE_CASE_CORRECT_ANSWER
        prompt_summary = generate_summary_prompt(description,correct_answer,error_list)
        summary_rules = run_llm_DS(prompt_summary,running_params['llm'],running_params['temperature'])
        print("总结的规则: ",summary_rules)
        print(f'---------------------{c}/{cycle}---------:',file=f_ours_file)
        print(f'Summary_rules:{summary_rules}',file=f_ours_file)

        # #simplify the rules
        # prompt_simplify = generate_simplify_rules(summary_rules)
        # simplify_rules = run_llm(prompt_simplify,running_params['llm'],running_params['temperature'])
        # print("简化后的规则: ",simplify_rules)
        # print(f'Simplify_rules:{simplify_rules}',file=f_ours_file)

        #generate improved results
        prompt_improve = generate_improve_prompt(summary_rules,description)
        improve_result = run_llm_DS(prompt_improve,running_params['llm'],running_params['temperature'])
        print("改进后的结果: ",improve_result)
        print(f'---------------------{c}/{cycle}---------:',file=f_ours_file)
        print(f'Improve_result:{improve_result}',file=f_ours_file)
    f_baseline_file.close()
    f_ours_file.close()


if __name__ == '__main__':
    main()