running_params = {
    'llm':'gpt-3.5-turbo-0125',
    'run_llm':2, # 1:单轮问答，2：2论问答，3：三轮问答
    'cycle':10,
    'useCasecycle':5,
    'stateMachinecycle':5,
    'temperature': 0,# 控制prediction llm 的温度参数
    'temperature_relation' : 0.3,#控制识别关系的温度参数
    'base-temperature': 0.7, # baseline llm 的温度参数
    'temperature_inherit_relation':0.1,#控制识别继承关系的温度参数
    'max_tokens': 3000,
    'top_p': 1,
    'frequency_penalty': 0,
    'presence_penalty': 0,
    'ratio':0.9,
    'jaccard':0.6,
    'jaccard_ratio':0.9,
    'LLM3': 'gpt-3.5-turbo-0125',
    'LLM_DS': 'gpt-4o-mini',
    'API_KEY':'sk-SE0Gb46RPVRn3i9myvLP0GZ8clpnmpYIn3xVJk19k12n1CIU',
}

file = {
    'path': 'C:\AppAndData\codeAndproject\modelGeneratelab\selfSummaryModelGeneration',
    'baseline' : 'C:\AppAndData\codeAndproject\modelGeneratelab\selfSummaryModelGeneration\labResult\pre',
    'usecase_baseline' : 'C:\AppAndData\codeAndproject\modelGeneratelab\selfSummaryModelGeneration\labResult-usecase\pre',
    'statemachine_baseline' : 'C:\AppAndData\codeAndproject\modelGeneratelab\selfSummaryModelGeneration\labResult-statemachine\pre',
    'compare_usecase_baseline' : 'C:\AppAndData\codeAndproject\modelGeneratelab\selfSummaryModelGeneration\labResult-compare\pre',
    'ours' : 'C:\AppAndData\codeAndproject\modelGeneratelab\selfSummaryModelGeneration\labResult\ours',
    'usecase_ours' : 'C:\AppAndData\codeAndproject\modelGeneratelab\selfSummaryModelGeneration\labResult-usecase\ours',
    'statemachine_ours' : 'C:\AppAndData\codeAndproject\modelGeneratelab\selfSummaryModelGeneration\labResult-statemachine\ours',
    'compare_usecase_ours' : 'C:\AppAndData\codeAndproject\modelGeneratelab\selfSummaryModelGeneration\labResult-compare\ours',
}

class stateMachine:
    def __init__(self,startState,event,endState):
        self.startState = startState
        self.event = event
        self.endState = endState

#Original version of the prompt template for the class diagram
PROMPT_MODEL_INIT="""
Create a class diagram for the following description by giving the enumerations, classes, and relationships using format:
Enumerations:
enumerationName(literals)
(there might be no or multiple enumerations)

Class:
className(attributeName1 : attributeType1,attributeName2 : attributeType2 (there might be multiple attributes))
(there might be multiple classes)

Relationships:
mul1 class1 associate mul2 class2 (class1 and2 are classes above. mul1 and mul2 are one of the following options[0..*, 1, 0..1, 1..*]).
(there might be multiple associations)

class1 inherit class2 (class1 and class2 are classes above)
(there might be multiple inheritance)

mul1 class1 contain mul2 class2 (class1 and2 are classes above. mul1 and mul2 are one of the following options[0..*, 1, 0..1, 1..*])
(there might be multiple composition)

#Description 
{}
"""

#Original version of the prompt template for the use case diagram
PROMPT_USECASE_INIT="""
Generate a use case diagram from the given description by giving the actors, use cases and associations using format:
Actors:
+ actorName

Use Cases:
+ useCaseName

Relationships:
+ (actor) associate (useCase)
+ (useCase) include (useCase)
+ (useCase) extend (useCase)
+ (useCase) generalize (useCase)


#Description 
{}
"""

#Original version of the prompt template for the statechart
PROMPT_STATE_INIT="""
Create a state machine diagram for the following description by giving the states, events, and transitions using format:
States:
+ stateName
(there might be no or multiple states)
Events:
+ eventName
(there might be no or multiple events)
Transitions:
+ state1 (eventName) state2
(there might be multiple transitions)

#Description 
{}
"""

#compare with correct answer
PROMPT_MODEL_COMPARE="""
Compare the generated content with the correct enumerations, classes, and relationships to identify any errors in the generated content. Note: Only identify errors, do not modify them.

#Correct enumerations, classes, and relationships:
{}
"""

#compare with correct answer
PROMPT_USECASE_COMPARE="""
Compare the generated content with the correct use case diagram to identify any errors in the generated content. Note: Only identify errors, do not modify them.

#Correct use case diagram:
{}
"""

#compare with correct answer
PROMPT_STATE_COMPARE="""
Compare the generated content with the correct state machine diagram to identify any errors in the generated content. Note: Only identify errors, do not modify them.

#Correct state machine diagram:
{}
"""


#analyze the error
PROMPT_MODEL_ANALYZE=""" 
Based on the generated errors, perform an in-depth analysis of the root causes of these errors. 
Consider not only the immediate factors such as missing attribute and data type information within a class, but also look into the broader context. 
Provide a comprehensive and detailed explanation of the possible reasons behind the errors, 
including any assumptions that might have been made during the modeling process that could have led to the current situation.
#Generated errors 
{} 

"""

#analyze the error
PROMPT_USECASE_ANALYZE=""" 
Based on the generated errors, perform an in-depth analysis of the root causes of these errors. 
Consider not only the immediate factors, but also look into the broader context. 
Provide a comprehensive and detailed explanation of the possible reasons behind the errors, 
including any assumptions that might have been made during the modeling process that could have led to the current situation.
#Generated errors 
{} 

"""

#summary the rules
PROMPT_MODEL_SUMMARY="""
Based on the above errors and the results of the analysis, summarize some rules to follow when generating enums, classes, and relationships.
The rules should be presented in the following "Do and Don't" format:
- **Do**: List actions that should be taken when generating enums, classes, and relationships. For example, "Do clearly define the scope of each class."
- **Don't**: List actions that should be avoided when generating enums, classes, and relationships. For example, "Don't create overly complex inheritance hierarchies without proper justification."

#Generated errors
{}

#Results of the analysis
{}
"""

#summary the rules
PROMPT_USECASE_SUMMARY="""
Based on the above errors and the results of the analysis, summarize some rules to follow when generating use case diagram.
The rules should be presented in the following "Do and Don't" format:
- **Do**: List actions that should be taken when generating use case diagram. For example, "Do clearly define the scope of each class."
- **Don't**: List actions that should be avoided when generating use case diagram. For example, "Don't create overly complex inheritance hierarchies without proper justification."

#Generated errors
{}

#Results of the analysis
{}
"""

#simplify the rules
PROMPT_MODEL_SIMPLIFY="""
Please simplify the above rules and do not include specific systems or instances.
#Rules
{}
"""

#simplify the rules
PROMPT_USECASE_SIMPLIFY="""
Please simplify the above rules and do not include specific systems or instances.
#Rules
{}
"""

#our prompt
PROMPT_MODEL_TEACHER_GUIDE="""
You are a highly experienced professer in software engineering, teaching object-oriented class diagram modeling. You are reviewing (<Student Answers>) according to the (<System Description>) and (<Referenced Answer>). Generate some modeling rules that are not only accurate but also practical and easy for students to apply by summarizing the correct and the incorrect answers.

Let's do it step by step.

# Steps
1. Note that your goal is to help students to manage modeling methodology, rather than correcting a specific error.
2. Identify the incorrect and incomplete parts in (<Student Answers>).
3. For each wrong part, locate the exact sentences in (<System Description>) that are related to this part; then, explain why this part is incorrect or incomplete.
4. Inductively summarize common rules for OO modelings according to the problems found.
5. Ensure that the rules you generate are clear, concise, and easy to understand. The rules should be general enough to be applicable to all types of OO models, regardless of the specific application domain. 
6. DO NOT use concrete examples in rule descriptions. 

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

# Student Answers
{}

"""

PROMPT_MODEL_TEACHER_GUIDE_FEEDBACK="""
Based on the (<Generated rules>) and (<Students'answer>): please review and optimize the previously generated modeling rules. Consider if the rules need to be more detailed, more general, or if there are any misunderstandings in the initial rule - generation.

# Steps
1. Analyze the generated rules and students' answer to identify areas for improvement in the rules.
2. If the feedback points out that a rule is too specific or too general, adjust it accordingly.
3. If there are misunderstandings in the initial rule - generation, clarify the rules.
4. Keep the rules clear, concise, and easy to understand, and applicable to all types of OO models.
5. DO NOT use concrete examples in rule descriptions.

Output Format
+ Rule 1: <Updated What should or can be done>
+ Rule 2: <Updated What cannot be done>

# Generated rules
{}

# Students' answer
{}
"""


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

PROMPT_MODEL_IMPROVE="""
Create a class diagram for the following description by giving the enumerations, classes, and relationships using format:(Note: Follow the Rules given during the generation process)
Enumerations:
enumerationName(literals)
(there might be no or multiple enumerations)

Class:
className(attributeName1 : attributeType1,attributeName2 : attributeType2 (there might be multiple attributes))
(there might be multiple classes)

Relationships:
mul1 class1 associate mul2 class2 (class1 and2 are classes above. mul1 and mul2 are one of the following options[0..*, 1, 0..1, 1..*]).
(there might be multiple associations)

class1 inherit class2 (class1 and class2 are classes above)
(there might be multiple inheritance)

mul1 class1 contain mul2 class2 (class1 and2 are classes above. mul1 and mul2 are one of the following options[0..*, 1, 0..1, 1..*])
(there might be multiple composition)

#Rules
{}

#Description 
{}
"""

#初始版本useCase的prompt 模板
PROMPT_USECASE_IMPROVE="""
Generate a use case diagram from the given description by giving the actors, use cases and associations using format:
Actors:
actorName

Use Cases:
useCaseName

Associations:
(actor) can (useCase)
(useCase) include (useCase)
(useCase) extend (useCase)
(useCase) generalize (useCase)

#Rules
{}

#Description 
{}
"""

#state machine improve
PROMPT_STATE_IMPROVE="""
Create a state machine diagram for the following description by giving the states, events, and transitions using format:(Note: Follow the Rules given during the generation process)
States:
stateName
(there might be no or multiple states)
Events:
eventName
(there might be no or multiple events)
Transitions:
state1 (eventName) state2
(there might be multiple transitions)

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

#system description
USE_CASE_DESCRIPTION = """
In the train ticket booking system, customers can purchase tickets, cancel tickets, check the remaining tickets and check the train time four operations. Whether it is to buy a ticket or cancel a ticket, the user must log in to the system first. There are two ways to query the train time: station query and train number query. If you forget your password when logging in to the system, you can also retrieve your password. Draw a use case diagram.
"""

#state machine description
STATE_MACHINE_DESCRIPTION = """
Initial state When entering the boiling water process, the water burner is in the off state. When turning on the water burner switch, it is necessary to check whether there is water in the kettle. If so, the water burner is performed and the water burner enters the open state. When boiling water, if the water heater is broken, the boiling water process is terminated
"""

#correct answer
CORRECT_ANSWER = """
Enumeration:
Interval(weekly, monthly, everyHalfYear, yearly)
AccessType(reservable, walkIn, dropOff)
DayOfWeek(Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday)

Classes:

Patient(string dateOfBirth)
Doctor(string signature)
Requisition(string effectiveDate, int repetitionCount, Interval repetitionInterval)
TestResult(boolean negative, string report)
SpecificTest(Data date)
Appointment(string confirmation, Date date, string startTime, string endTime)
BusinessHour(DayOfWeek: dayOfWeek, string startTime, string endTime)
Lab(string registrationNumber, string name, string address, boolean changeCancelFee)
Test(string name, string duration)
TestType(string name, string durationAdditive, AccessType access)

Relationships:
1 Patient associate * Requisition
* Requisition associate *Appointment
* Appointment associate 1 Lab
1 Docter associate * Requisition
1 Requsition associate *SpecificTest
0..1 TestResult associate *SpecificTest
1 Lab associate 7 BusinessHour
1 Test associate *SpecificTest
1 TestType associate * Test
"""

#correct answer
USE_CASE_CORRECT_ANSWER = """
Actors:
Customer

Use Cases:
Purchase Tickets
Cancel Tickets Reservation
Query Tickets
Check Tickets Schedule
Log in
Retrieve Password
Query by Station
Query by Train Number

Associations:
(Customer) can (Purchase Tickets)
(Customer) can (Cancel Tickets Reservation)
(Customer) can (Query Tickets)
(Customer) can (Check Tickets Schedule)
(Purchase Tickets) include (Log in)
(Cancel Tickets Reservation) include (Log in)
(Retrieve) extend (Log in)
(Query by Station) generalize (Query Tickets)
(Query by Train Number) generalize (Query Tickets)

"""

#state machine correct answer
STATE_MACHINE_CORRECT_ANSWER = """
States:
Off
On
CheckWater
Terminated

Events:
TurnOn
WaterAvailable
NoWater
WaterBoiling
KettleIsBroken

Transitions:
Off (TurnOn) CheckWater
CheckWater (WaterAvailable) On
CheckWater (NoWater) Off
On (WaterBoiling) Off
On (KettleIsBroken) Terminated

"""
