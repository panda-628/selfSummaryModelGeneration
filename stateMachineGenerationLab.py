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
    prompt1 = PROMPT_STATE_INIT.format(description)
    message = [
        {"role":"system","content":"Generate a state machine diagram from the given description."},
        {"role":"user","content":f"{prompt1}"},
    ]
    prompt_list['prompt'] = message

    return prompt_list

def generate_rules_prompt(description,correct_answer,error_list):
    prompt_list = {
        'prompt':''
    }
    message = []
    prompt1 = PROMPT_MODEL_TEACHER_GUIDE.format(description,correct_answer,error_list)
    message = [
        {"role":"system","content":"Compare the generated content with the correct use case diagram to identify any errors in the generated content and create rules. Note: Only identify errors, do not modify them."},
        {"role":"user","content":f"{prompt1}"},
    ]
    prompt_list['prompt'] = message

    return prompt_list


def generate_improve_prompt(simplify_rules,description):
    prompt_list = {
        'prompt':''
    }
    message = []
    prompt1 = PROMPT_STATE_IMPROVE.format(simplify_rules,description)
    message = [
        {"role":"system","content":"Based on the above rules, improve the generated content to avoid the errors in the future"},
        {"role":"user","content":f"{prompt1}"},
    ]
    prompt_list['prompt'] = message

    return prompt_list

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
    baseline_path = file['statemachine_baseline']
    os.chdir(baseline_path)
    time_now = datetime.datetime.now()
    a1 = tuple(time_now.timetuple()[0:9])
    start_time = time.mktime(a1)
    new_baseline_folder = 'baseline'+str(start_time)+'-'+running_params['llm']+'-tem'+str(running_params['temperature'])
    os.mkdir(new_baseline_folder)

    ours_path = file['statemachine_ours']
    os.chdir(ours_path)
    time_now = datetime.datetime.now()
    a1 = tuple(time_now.timetuple()[0:9])
    start_time = time.mktime(a1)
    new_ours_folder = 'ours'+str(start_time)+'-'+running_params['llm']+'-tem'+str(running_params['temperature'])
    os.mkdir(new_ours_folder)

    cycle = running_params['stateMachinecycle']

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
        description = STATE_MACHINE_DESCRIPTION
        prompt_list = generate_baseline_prompt(description)
        error_list = []
        for i in range(1,6):
            AI_answer = run_llm(prompt_list,running_params['llm'],running_params['temperature'])
            print("初始prompt生成的内容: ",AI_answer)
            print(f'---------------------{c}/{cycle}---------{i}/5:',file=f_baseline_file)
            print(f'Base_AI_answer:{AI_answer}',file=f_baseline_file)
            error_list.append(AI_answer)

        #summary the rules
        correct_answer = STATE_MACHINE_CORRECT_ANSWER
        prompt_summary = generate_rules_prompt(description,correct_answer, error_list)
        summary_rules = run_llm(prompt_summary,running_params['llm'],running_params['temperature'])
        print("总结的内容: ",summary_rules)
        print(f'---------------------{c}/{cycle}---------:',file=f_ours_file)
        print(f'Summary_rules:{summary_rules}',file=f_ours_file)

        #generate improved results
        prompt_improve = generate_improve_prompt(summary_rules,description)
        improve_result = run_llm(prompt_improve,running_params['llm'],running_params['temperature'])
        print("改进后的结果: ",improve_result)
        print(f'---------------------{c}/{cycle}---------:',file=f_ours_file)
        print(f'Improve_result:{improve_result}',file=f_ours_file)
    f_baseline_file.close()
    f_ours_file.close()


if __name__ == '__main__':
    main()