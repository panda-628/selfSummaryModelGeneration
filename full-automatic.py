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
    prompt1 = PROMPT_MODEL_INIT.format(description)
    message = [
        {"role":"system","content":"Generate the lists of model classes and associations from a given description. There are only 3 types of associations: associate, inherit, contain. Do not use other name for associations."},
        {"role":"user","content":f"{prompt1}"},
    ]
    prompt_list['prompt'] = message

    return prompt_list

def generate_compare_prompt(generated_contents,correct_answer):
    prompt_list = {
        'prompt':''
    }
    message = []
    prompt1 = PROMPT_MODEL_COMPARE.format(generated_contents,correct_answer)
    message = [
        {"role":"system","content":"Compare the generated content with the correct enumerations, classes, and relationships to identify any errors in the generated content. Note: Only identify errors, do not modify them."},
        {"role":"user","content":f"{prompt1}"},
    ]
    prompt_list['prompt'] = message

    return prompt_list

# def generate_analyze_prompt(error_list):
#     prompt_list = {
#         'prompt':''
#     }
#     message = []
#     prompt1 = PROMPT_MODEL_ANALYZE.format(error_list)
#     message = [
#         {"role":"system","content":"Based on the generated errors, analyze the causes of these errors"},
#         {"role":"user","content":f"{prompt1}"},
#     ]
#     prompt_list['prompt'] = message

#     return prompt_list

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

# def generate_improve_rules_prompt(summary_rules,student_answer):
#     prompt_list = {
#         'prompt':''
#     }
#     message = []
#     prompt1 = PROMPT_MODEL_TEACHER_GUIDE_FEEDBACK.format(summary_rules,student_answer)
#     message = [
#         {"role":"system","content":"Based on the above rules and students' answer, improve the generated rules to avoid the errors in the future"},
#         {"role":"user","content":f"{prompt1}"},
#     ]
#     prompt_list['prompt'] = message

#     return prompt_list

# def generate_simplify_rules(summary_rules):
#     prompt_list = {
#         'prompt':''
#     }
#     message = []
#     prompt1 = PROMPT_MODEL_SIMPLIFY.format(summary_rules)
#     message = [
#         {"role":"system","content":"Based on the above rules, simplify the rules to follow when generating enums, classes, and relationships.Note:do not include specific systems or instances."},
#         {"role":"user","content":f"{prompt1}"},
#     ]
#     prompt_list['prompt'] = message

#     return prompt_list

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
    path = file['path']
    os.chdir(path)

    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime('%Y-%m-%d-%H-%M-%S')
    system_name = SYSTEM_NAME
    new_folder = 'full-automatic'+'-'+ system_name + '-' +running_params['llm'] + formatted_time
    os.mkdir(new_folder)

    cycle = running_params['cycle']

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

        #compare the results
        correct_answer = CORRECT_ANSWER
        prompt_compare = generate_compare_prompt(AI_answer,correct_answer)
        compare_result = run_llm(prompt_compare,running_params['llm'],running_params['temperature'])
        #print("比较得出的错误结果: ",compare_result)
        print(f'---------------------{c}/{cycle}---------:',file=f_baseline_file)
        print(f'Compare_result:{compare_result}',file=f_baseline_file)
        error_list = compare_result

        #summary the rules
        prompt_summary = generate_summary_prompt(description,correct_answer,error_list)
        summary_rules = run_llm(prompt_summary,running_params['llm'],running_params['temperature'])
        #print("总结的规则: ",summary_rules)
        print(f'---------------------{c}/{cycle}---------:',file=f_ours_file)
        print(f'Summary_rules:{summary_rules}',file=f_ours_file)

        # #improve the rules
        # prompt_improve_rules = generate_improve_rules_prompt(summary_rules,error_list)
        # improve_rules = run_llm(prompt_improve_rules,running_params['llm'],running_params['temperature'])
        # print("改进的规则: ",improve_rules)
        # print(f'---------------------{c}/{cycle}---------:',file=f_ours_file)
        # print(f'Improve_rules:{improve_rules}',file=f_ours_file)

        #generate improved results
        prompt_improve = generate_improve_prompt(summary_rules,description)
        improve_result = run_llm(prompt_improve,running_params['llm'],running_params['temperature'])
        print("改进后的结果: ",improve_result)
        print(f'---------------------{c}/{cycle}---------:',file=f_ours_file)
        print(f'Improve_result:{improve_result}',file=f_ours_file)
        
    f_baseline_file.close()
    f_ours_file.close()

    print("full-automatic 十次实验完成！")


if __name__ == '__main__':
    main()