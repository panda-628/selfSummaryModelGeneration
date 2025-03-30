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
    'path': 'C:\AppAndData\codeAndproject\selfSummaryModelGeneration\labResult',
    'baseline' : 'C:\AppAndData\codeAndproject\selfSummaryModelGeneration\labResult\pre',
    'usecase_baseline' : 'C:\AppAndData\codeAndproject\selfSummaryModelGeneration\labResult-usecase\pre',
    'statemachine_baseline' : 'C:\AppAndData\codeAndproject\selfSummaryModelGeneration\labResult-statemachine\pre',
    'compare_usecase_baseline' : 'C:\AppAndData\codeAndproject\selfSummaryModelGeneration\labResult-compare\pre',
    'ours' : 'C:\AppAndData\codeAndproject\selfSummaryModelGeneration\labResult\ours',
    'usecase_ours' : 'C:\AppAndData\codeAndproject\selfSummaryModelGeneration\labResult-usecase\ours',
    'statemachine_ours' : 'C:\AppAndData\codeAndproject\selfSummaryModelGeneration\labResult-statemachine\ours',
    'compare_usecase_ours' : 'C:\AppAndData\codeAndproject\selfSummaryModelGeneration\labResult-compare\ours',
}

class stateMachine:
    def __init__(self,startState,event,endState):
        self.startState = startState
        self.event = event
        self.endState = endState

#Original version of the prompt template for the class diagram
PROMPT_MODEL_INIT="""
Create a class diagram for the following description by giving the enumerations, classes, and relationships using PlantUML format:

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

#Generated content:
{}

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
Based on the above errors, summarize some rules to follow when generating enums, classes, and relationships.
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

PROMPT_MODEL_IMPROVE="""
Create a class diagram for the following description by giving the enumerations, classes, and relationships using PlantUML format:(Note: Follow the Rules given during the generation process)

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

#system name
SYSTEM_NAME = "CeIO"

#system description
DESCRIPTION = """
The CelO application helps families and groups of friends to organize birthday celebrations and other events. Organizers can keep track of which tasks have been completed and who attends. Attendees can indicate what they are bringing to the event. For a small event, there is typically one organizer, but larger events require several organizers. An organizer provides their first and last name, their email address (which is also used as their username), their postal address, their phone number, and their password. Furthermore, an organizer indicates the kind of event that needs to be planned by selecting from a list of events (e.g., birthday party, graduation party…) or creating a new kind of event. The start date/time and end date/time of the event must be specified as well as the occasion and location of the event. The location can again be selected from a list, or a new one can be created by specifying the name of the location and its address. An organizer then invites the attendees by entering their first and last names as well as their email addresses. Sometimes, an organizer is only managing the event but not attending the event. Sometimes, an organizer also attends the event. When an attendee receives the email invitation, the attendee can create an account (if they do not yet have an account) with a new password and their email address from the invitation as their username. Afterwards, the attendee can indicate whether they will attend the event, maybe will attend the event, or cannot attend the event. An organizer can view the invitation status of an event, e.g., how many attendees have replied or have not yet replied and who is coming for sure or maybe will be coming. When an organizer selects an event, an event-specific checklist is presented to the organizer. For example, a birthday party may have a task to bring a birthday cake. For each task on the checklist, an organizer can indicate that the task needs to be done, has been done, or is not applicable for the event. An organizer can also add new tasks to the list, which will then also be available for the next event. For example, an organizer can add to bring birthday candles to the list for a birthday party and this task will then be available for the next birthday party, too. An organizer can also designate a task on the checklist for attendees to accomplish. For example, an organizer can indicate that the birthday cake should be brought to the event by an attendee. If this is the case, then the list of tasks to be accomplished by attendees is shown to attendees that have confirmed their attendance to the event. An attendee can then select their tasks, so that the organizer can see who is bringing what to the event.
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
{
    "enumerations": {
        "RepeatInterval": [
            "WEEKLY",
            "MONTHLY",
            "HALF_YEARLY",
            "YEARLY"
        ],
        "AppointmentType": [
            "APPOINTMENT_REQUIRED",
            "DROP_OFF"
        ],
        "TestResultType": [
            "POSITIVE",
            "NEGATIVE"
        ],
        "DayOfWeek": [
            "MONDAY",
            "TUESDAY",
            "WEDNESDAY",
            "THURSDAY",
            "FRIDAY",
            "SATURDAY",
            "SUNDAY"
        ]
    },
    "classes": {
        "Requisition": [
            "validFrom: Date",
            "doctor: String",
            "repeatInterval: RepeatInterval"
        ],
        "Doctor": [
            "practitionerNumber: String",
            "specialty: String",
            "name: String",
            "address: String",
            "phone: String"
        ],
        "Patient": [
            "healthNumber: String",
            "firstName: String",
            "lastName: String",
            "address: String",
            "phone: String"
        ],
        "TestGroup": [
            "name: String",
            "isCombinedTest: boolean"
        ],
        "RequisitionItem": [
            "result: TestResultType",
            "report: String"
        ],
        "Appointment": [
            "name: String",
            "appointmentNumber: String",
            "appointmentType: AppointmentType",
            "confirmationDate: Date",
            "startTime: DateTime",
            "endTime: DateTime"
        ],
        "Test": [],
        "Lab": [
            "registrationNumber: String",
            "address: String",
            "capacity: double",
            "cancellationFee: double"
        ],
        "BusinessHour": [
            "dayOfWeek: DayOfWeek",
            "openTime: Time",
            "closeTime: Time"
        ]
    },
    "relationships": [
        "Requisition \"1\" -- \"1\" Doctor (doctor)",
        "Requisition \"1\" -- \"1\" Patient (patient)",
        "Requisition \"1\" -- \"*\" TestGroup (testGroup)",
        "Requisition \"*\" -- \"*\" RequisitionItem (items)",
        "TestGroup \"*\" -- \"*\" Test (tests)",
        "Test \"1\" -- \"1\" Appointment (appointment)",
        "Appointment \"1\" -- \"1\" Lab (lab)",
        "Lab \"1\" -- \"*\" BusinessHour (businessHours)"
    ]
}
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
