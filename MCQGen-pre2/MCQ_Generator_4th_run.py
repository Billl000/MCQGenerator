import openai
import os
import support
import panel as pn
pn.extension()

#from nltk.tokenize import sent_tokenize
#import re
#import nltk
#import backup_support

from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

openai.api_key = os.getenv("OPENAI_API_KEY")

m = open('QuestionDatabase.txt', 'w')
m.close()

#p = open('Passage.txt', 'w')
#p.close()

##################################################################

def get_completion_from_messages(messages, model = 'gpt-3.5-turbo', temperature = 0, top_p = 0.9, max_tokens = 500):
    response = openai.ChatCompletion.create(
        messages = messages,
        model = model,
        temperature = temperature,
        top_p = top_p,
        max_tokens = max_tokens,
    )
    
    return response.choices[0].message['content']


#passage_input = input("Enter your passage & questions: \n")
#Assumption that user inputs the passage in a right format.

########################################################################
summarised = {
  "1": "Madagascar's forests are being converted to agricultural land due to insect pests destroying crops, leading to habitat and biodiversity loss, but some insectivorous bats are thriving and providing pest control services.",
  "2": "A study by zoologist Ricardo Rocha shows that bats are helping rice farmers in Madagascar by eating insects, which can reduce the need for deforestation.",
  "3": "Madagascar is an important region for bat conservation, with one-fifth of all mammal species being bats.",
  "4": "Several species of indigenous bats in Madagascar are taking advantage of habitat modification to hunt insects above rice fields.",
  "5": "Six species of bat in Madagascar are preying on rice pests, which cause financial pressure on farmers and encourage deforestation.",
  "6": "A study investigated the feeding activity of bats in farmland bordering a national park in Madagascar.",
  "7": "Researchers used ultrasonic recorders and DNA barcoding techniques to study bat feeding habits in different sites.",
  "8": "Bats preferentially forage in rice fields due to lack of water and nutrient run-off, and DNA analysis showed they fed on economically important insect pests.",
  "9": "The study is the first to show bats acting as pest controllers in Madagascar, benefiting both farmers and conservationists.",
  "10": "Malagasy bats also feed on disease-carrying mosquitoes and blackflies, providing additional benefits to local people.",
  "11": "The relationship between bats and local people in Madagascar is complicated, as bats are a source of protein but can also be seen as unclean, yet they are associated with sacred caves and the ancestors.",
  "12": "Maximizing bat populations can help boost crop yields and promote sustainable livelihoods, and further research is needed to quantify this contribution."
}




steps = {
    "0": "Confirm whether the question list matches the user's input",
    "1": "Run through each statement in the question list and get the infos out of the statement",
    "2": "Find paragraph containing the answer",
    "3": "Find sentences containing the answer in the paragraph",
    "4": "Compares the sentences and the statement",
    "5": "Final Verdict"
}

step = 0
context = [
    {"role": "system", "content": "placeholder"},
]

 
inp = ''
end = False
repeat_count = 0
question_count = 0


def check_has_result(repeat_count):
    if repeat_count == 0:
        return False
    if repeat_count > 0:
        return True
def append_context(response):
    global inp

    print("\nAssistant: " + str(response))
    context.append({'role':'assistant', 'content':f"{response}"})   
    inp = input("\nUser: ")
    #print("User: " + str(inp))
    context.append({'role':'user', 'content':f"{inp}"})
#### Introduction

def respond_user_input(response):
    global inp
    if "y" in response["decision"]:
        context[0]['content'] = f"""
        You have just confirmed that the user answers your questions correctly. \
        With the text you are given called "Explanation", congratulate the user in selecting the right option.\
        Additionally, tell the user that you will be moving on to the next question.
        """

        #convo = ' '.join([str(elem) for elem in context[1:]])

        user_message = f"""

            Explanation: {response["explanation"]}
        """
        messages = [
        {'role': 'system', 'content': context[0]['content']},
        {'role': 'user', 'content': user_message}
        ]

        response = get_completion_from_messages(messages)
        print("\nAssistant: " + response)
        context.append({'role':'assistant', 'content':f"{response}"})
        
        inp = "yes"
    elif "n" in response["decision"]:
        context[0]['content'] = f"""
            You have just told the user answers your questions incorrectly. You will now need to explain why that option is incorrect\
            and you will also have to tell the user that they will have to answer the question again without stating the correct answer.
            """

        user_message = f"""

            Explanation: {response["explanation"]}
        """
        #convo = ' '.join([str(elem) for elem in context[1:]])
        messages = [
        {'role': 'system', 'content': context[0]['content']},
        {'role': 'user', 'content': user_message}
        ]
        
        print("==== Debug prompt", messages)
        response = get_completion_from_messages(messages)
        print("\nAssistant: " + response)
        context.append({'role':'assistant', 'content':f"{response}"})
    elif "o" in response["decision"]:
        system_message = f"""
        You are an IELTS Reading Assistant that will answer the user's questions. \
        However, the user just enter an unrelated response.\
        Assist the user's query and mention that it's unrelated, and ask the user to get back on topic.
        """
        messages = [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': ''}
        
        ]


        response = get_completion_from_messages(messages)
        append_context(response)
system_message = f"""
You are an IELTS Reading Assistant bot. Your job is to greet the user, introduce yourself\
Tell the user that you will help the user dissect any reading passage the user gives, and help the user\
get into the mindset of understanding the process of getting the right options\
"""

messages = [
    {'role': 'system', 'content': system_message},
    {'role': 'user', 'content': ''}
]
response = get_completion_from_messages(messages)

#append_context(response)

v = open("ExtractedPassage.txt", 'r')

f = open('Passage.txt', 'r')

print("Please hold on while we are analysing your input...")
questions = support.extract_questions(f.read())


questions_list = list(questions.values())
###Run the steps
def run_question_list(question):
    global step
    global inp
    global repeat_count
    
    while (steps[f"{step}"] != "Final Verdict"):
        print(f"Step: {step + 1} / {len(steps)}")
        if step == 0:

#             if check_has_result(repeat_count) == False:
#                 end = False
#                 ######
                


#                 question = que

            ######
            ##Add a bridge
            context[0]['content'] = """You will be given a dictionary called question_list.\
            Mention that you've received the user's input, \
            and ask if the sentence in the question_list matches the user's input."""
            messages = [
                {'role': 'system', 'content': context[0]['content']},
                {'role': 'user', 'content': str(question)}
            ]

            response = get_completion_from_messages(messages)
            
            append_context(response)
            
            #Add a situation if "No"
        elif step > 0:
            ####
            infos = support.extract_infos_statement(question)
            #print(infos, "\n")

            info = {}
            info['actor'] = infos['actor']
            info['acted upon'] = infos['acted upon']

            #print(info)
            ####
            if (step == 2):
                system_message = f"""
                You just finished {steps[f"{step - 1}"]}. The next step is now to {steps[f"{step}"]}\
                Now, your job is to guide the user from the previous step to this step.

                Mention that the user will be identifying the paragraph based on the information the user extracted out of the statement.\
                Suggest to the user that the user can skim and scan from the top to quickly identify where the main information can be, \
                as the order of the questions correlate to the order of the paragraphs.



                DO NOT metion any extra instructions.
                """
            elif (step == 5):
                system_message = f"""
                The user just finish all the steps. Congratulate the user on finding the right option on their own, and wish that they will use\
                the same approach for next questions.
                """
            else: 
                system_message = f"""
                You just finished {steps[f"{step - 1}"]}. The next step is now to {steps[f"{step}"]}\
                Now, your job is to guide the user from the previous step to this step. Structure your output like a conversation.
                """
            #Add like a blocker to this so that it doesn't run every time an "N" appear
            messages = [
                {'role': 'system', 'content': system_message},
                {'role': 'user', 'content':" "}
            ]
            print("====", messages)

            bridge = get_completion_from_messages(messages)
            print("\nAssistant: " + str(bridge))
            ####Todo: Change it into a function

            if (step == 1):
                ####
                if(check_has_result(repeat_count) == False):
                    MCQ_questions_for_statement = []
                    MCQ_questions_for_statement = support.generate_questions_for_statement(infos, question, summarised)
                    #print(MCQ_questions_for_statement)
                    ####
                    question_len = len(MCQ_questions_for_statement)
                count = 0
                while count != question_len:

                    context[0]['content'] = f"""
                    You will be given a question. Structure your output in a question format.\

                    Example Format: ```
                    Question: <question>
                    <option 1> 
                    <option 2>
                    <option 3>
                    ```
                    """

                    messages = [
                        {'role': 'system', 'content': context[0]['content']},
                        {'role': 'user', 'content': MCQ_questions_for_statement[count]}
                    ]

                    response = get_completion_from_messages(messages)

                    print("\nAssistant: \n" + MCQ_questions_for_statement[count])
                    context.append({'role':'assistant', 'content':f"{response}"})
                    inp = input("\nUser: ")
                    #print("User: " + str(inp))
                    context.append({'role':'user', 'content':f"{inp}"})


                    context[0]['content'] = f"""
                    You will be given a question, a statement and the user's answer. 

                    Output in the following JSON format:
                    ```
                    {{
                        "decision": "" 
                        "explanation": "<explanation>"
                    }}
                    ```
                    Your job is to check if the user is right, and generate an explanation WITHOUT STATING THE CORRECT OPTION for why the user is right, or wrong.
                    Put your decision in "decision" key, and your explanation in "explanation" key. \
                    If the user is correct, put "y" in the "decision" key.\
                    If the user is not correct or you are unsure, put "n" in the "decision" key.\

                    If the user enters an option not listed in the question, put "o" in the "decision" key.
                    """
                    user_message = f"""
                    Question : {MCQ_questions_for_statement[count]}
                    Statement: {question}
                    User's Answer: {inp}
                    """
                    messages = [
                        {'role': 'system', 'content': context[0]['content']},
                        {'role': 'user', 'content': user_message}
                    ]

                    response = get_completion_from_messages(messages)
                    print("===", response)
                    response = support.output_to_string(response)

    #                 if (response["decision"] == "neither"):
    #                     convo = ' '.join([str(elem) for elem in context[1:]])

    #                     messages = [
    #                         {'role': 'system', 'content': "Your job is to just assist the user with their queries."},
    #                         {'role': 'user', 'content': convo}
    #                     ]
    #                     outside_response = get_completion_from_messages(messages)
    #                     #print(outside_response)
    #                     print("\nAssistant: " + outside_response)
    #                     context.append({'role':'assistant', 'content':f"{outside_response}"})
                    #respond_user_input(response)

    #########                    
                    if "y" in response["decision"]:
                        context[0]['content'] = f"""
                        You have just confirmed that the user answers your questions correctly. \
                        With the text you are given called "Explanation", congratulate the user in selecting the right option.\
                        Additionally, tell the user that you will be moving on to the next question.
                        """

                        #convo = ' '.join([str(elem) for elem in context[1:]])

                        user_message = f"""

                            Explanation: {response["explanation"]}
                        """
                        messages = [
                        {'role': 'system', 'content': context[0]['content']},
                        {'role': 'user', 'content': user_message}
                        ]

                        response = get_completion_from_messages(messages)
                        print("\nAssistant: " + response)
                        context.append({'role':'assistant', 'content':f"{response}"})

                        count += 1

                    elif "n" in response["decision"]:
                        context[0]['content'] = f"""
                        You have just told the user answers your questions incorrectly. You will now need to explain why that option is incorrect\
                        and you will also have to tell the user that they will have to answer the question again without stating the correct answer.
                        """

                        user_message = f"""

                            Explanation: {response["explanation"]}
                        """
                        #convo = ' '.join([str(elem) for elem in context[1:]])
                        messages = [
                        {'role': 'system', 'content': context[0]['content']},
                        {'role': 'user', 'content': user_message}
                        ]

                        print("==== Debug prompt", messages)
                        response = get_completion_from_messages(messages)
                        print("\nAssistant: " + response)
                        context.append({'role':'assistant', 'content':f"{response}"})
                    #print(count) #Hasn't made sure this part worked successfully
                    elif "o" in response["decision"]:
                        system_message = f"""
                        You are an IELTS Reading Assistant that will answer the user's questions. \
                        However, the user just enter an unrelated response.\
                        Assist the user's query and mention that it's unrelated, and ask the user to get back on topic.
                        """
                        messages = [
                            {'role': 'system', 'content': system_message},
                            {'role': 'user', 'content': ''}

                        ]


                        response = get_completion_from_messages(messages)
                        append_context(response)

                inp = "Yes"
            elif (step == 2):
                ####
                if (check_has_result(repeat_count) == False):
                    location = support.find_location_of_answers(v.read(), question)
                    #print(location)
                    question_location = support.generate_questions_for_locations(question)
                    #print(question_location)

                    question_for_statement = {
                        'question': question_location,
                        'answer': location['paragraph_number'],
                        'paragraph': location['paragraph'],
                        'explanation': location['explanation']
                    }  
                ####

                append_context(question_location)

                context[0]['content'] = f"""
                You will be given a dictionary called `question_for_statment` containing a question, an answer to that question, and an explanation to the answer.\
                You will also be given the user's answer to the same question.
                Output in the following JSON format:
                ```
                {{
                    "decision": "" 
                    "explanation": "<explanation>"
                }}
                ```
                Your job is to check if the user is right, and generate an explanation for why the user is right, or wrong.
                Put your decision in "decision" key, and your explanation in "explanation" key. \
                If the user is correct, put "y" in the "decision" key.\
                If the user is wrong, put "n" in the "decision" key.\
                If the user doesn't put an answer, put "o" in the "decision" key.
                """
                user_message = f"""
                Dictionary: {question_for_statement}
                User's input: {inp}
                """
                messages = [
                    {'role': 'system', 'content': context[0]['content']},
                    {'role': 'user', 'content': user_message}
                ]

                response = support.output_to_string(get_completion_from_messages(messages))

                respond_user_input(response)
    
            elif (step == 3):
                if (check_has_result(repeat_count) == False):
                    sentences = support.locate_sentences_in_paragraph(question_for_statement['paragraph'], question)

                question_sentences = "Now that we know what paragraph to look at, can you provide for me the sentences that you think are related to the statement the most?"

                append_context(question_sentences)

                system_message = f"""
                You will be given an array called "sentences" and an user's input.
                Check if the user's input exactly matches the sentences in the array.
                If the user's input does, output "y".
                If the user's input doesn't, output "n".
                If the user's input is unrelated to the sentences, output "o".

                Output in the following format:
                {{
                    "decision": "<>",
                    "explanation": "<explanation>"

                }}

                """
                user_message = f"""
                Sentences: {sentences}
                User's input: {inp}
                """
                messages = [
                    {'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': user_message}
                ]
                response = support.output_to_string(get_completion_from_messages(messages))
                respond_user_input(response)

            elif (step == 4):
                if (check_has_result(repeat_count) == False):
                    comparison = support.compare_sentences(sentences, question)

                system_message = f"""
                You are given the following question:
                `Now that you have the sentences that contain the answer, compare them with our original statement. Can you tell me what's your answer?`

                Rewrite that question and output it to the user. Keep it at most 2 sentences.
                """

                messages = [
                    {'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': ''}
                ]
                response = get_completion_from_messages(messages)

                append_context(response)

                system_message = f"""
                You will be given a dictionary called `verdict` and an user's input.
                Check if the user's input matches the `decision` key in the dictionary
                If the user's input does, output "y".
                If the user's input doesn't, output "n".
                If the user's input is unrelated to the sentences, output "o".

                Output in the following format:
                {{
                    "decision": "<>",
                    "explanation": "<explanation>"

                }}

                """
                user_message = f"""
                Verdict: {comparison}
                User's input: {inp}
                """
                messages = [
                    {'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': user_message}
                ]
                response = support.output_to_string(get_completion_from_messages(messages))

                respond_user_input(response)
            elif(step == 5):
                
                inp = "Yes"
                repeat_count = 0
                if (question_count >= len(question) - 1):
                    system_message = f"""
                    You are an IELTS Reading Assistant bot. The user just finish answering a strings of questions they asked you\
                    with the approach you provided for the user.
                    Your job is to congratulate the user, ask them if they have any questions, and wish that they will continue this approach\
                    in many other questions of the same type.
                    """

                    messages = [
                    {'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': ''}
                    ]

                    response = get_completion_from_messages(messages)
                    append_context(response)

                


        ###Todo: Function
        system_message_check = f"""
        You will be given an user's response. Here are two categories:
        "Y": The response gives a positive sentiment
        "N": The response gives a negative sentiment
        Categorise the user's response into one of those two categories.
        ONLY OUTPUT THE CATEGORY'S NAME.
        """
        messages = [
            {'role': 'system', 'content': system_message_check},
            {'role': 'user', 'content': inp}
        ]

        check = get_completion_from_messages(messages)
        if "Y" in check:
            step += 1
            repeat_count = 0
            inp = ''
        if "N" in check:
            repeat_count += 1

            
            
for i in questions_list:
    run_question_list(i)
    step = 0
#run_question_list(questions_list[5])