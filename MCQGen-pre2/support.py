import openai
import json
from collections import defaultdict

def amogus(phrase):
    return phrase

delimiter = "####"

step2_system_message1 = f"""
You will be given a text file delimited by {delimiter}. Find the phrase "Question <number> - <number>" in its exact forms and output it.
Note that the range between the numbers in the ouput should not exceed 8
Example: "Question 6 - 13"
Example: "Question 2 - 5"
"""
step2_system_message2 = f"""
You will be given a text file and a phrase delimited by {delimiter}. Find the phrase in the text file and output everything after the phrase.
Example 1: '''
Phrase: `Question 3 - 5`
Text File: `Question 3 - 5
Anything should do is anything should be`

Output: `Anything should do is anything should be`

Example 2: '''
Phrase: `Question 14 - 18`
Text File: `Question 14 -18
Reading Passage 2 has six sections, A–F.
Which section contains the following information?
Write the correct letter, A–F, in boxes 14–18 on your answer sheet.
14 an explanation of the need for research to focus on individuals with a fairly
consistent income
15 examples of the sources the database has been compiled from
16 an account of one individual’s refusal to obey an order
17 a reference to a region being particularly suited to research into the link between
education and economic growth
18 examples of the items included in a list of personal possessions`

Output: `
Reading Passage 2 has six sections, A–F.
Which section contains the following information?
Write the correct letter, A–F, in boxes 14–18 on your answer sheet.
14 an explanation of the need for research to focus on individuals with a fairly
consistent income
15 examples of the sources the database has been compiled from
16 an account of one individual’s refusal to obey an order
17 a reference to a region being particularly suited to research into the link between
education and economic growth
18 examples of the items included in a list of personal possessions`
'''
"""
#Note: Make more examples for the step2.2

step2_system_message3 = f"""
You will be given a chunk of text. Identify any lines that starts with a number and output them in a JSON format, with the numbers at the beginning the keys.
Example 1: '''
Text: `
Do the following statements agree with the information given in Reading Passage 1?
In boxes 1–6 on your answer sheet, write
TRUE if the statement agrees with the information
FALSE if the statement contradicts the information
NOT GIVEN if there is no information on this
1.Many Madagascan forests are being destroyed by attacks from insects.
2.Loss of habitat has badly affected insectivorous bats in Madagascar.
3.Ricardo Rocha has carried out studies of bats in different parts of the world.
4.Habitat modification has resulted in indigenous bats in Madagascar becoming useful to farmers.
5.The Malagasy mouse-eared bat is more common than other indigenous bat species in Madagascar.
6.Bats may feed on paddy swarming caterpillars and grass webworms.
`
Output (in a JSON format): `
1.Many Madagascan forests are being destroyed by attacks from insects.
2.Loss of habitat has badly affected insectivorous bats in Madagascar.
3.Ricardo Rocha has carried out studies of bats in different parts of the world.
4.Habitat modification has resulted in indigenous bats in Madagascar becoming useful to farmers.
5.The Malagasy mouse-eared bat is more common than other indigenous bat species in Madagascar.
6.Bats may feed on paddy swarming caterpillars and grass webworms.
`
'''
"""
#Again, add more examples for step2.3 pls


step3_system_message1 = f"""
You will be given a sentence. Extract the actor and the acted upon in the sentence.
Output the answer in a JSON format, with two keys: "actor", and "acted upon".

"""

#Step 3.2: Extract the details using the Wh- questions
step3_system_message2 = f"""
Please extract relevant information from the following sentence that you will be given in an IELTS Reading Passage to assist a user in answering questions. Your approach involves using two methods concurrently: the 'Verbs/Nouns/Adjectives' method and the 'Who/What/Where/Why/How' method.

Please fill in the following JSON format with the extracted information. If there is no information related to a specific question category, please indicate so:

{{
    "Verbs/Nouns/Adjectives": "",
    "Who/What/Where/Why/How": {{
        "Who": "Provide information related to 'Who.' (If none, indicate 'None')",
        "What": "Provide information related to 'What.' (If none, indicate 'None')",
        "Where": "Provide information related to 'Where.' (If none, indicate 'None')",
        "Why": "Provide information related to 'Why.' (If none, indicate 'None')",
        "How": "Provide information related to 'How.' (If none, indicate 'None')",
    }}
    "Key Information": ""
}}

"""

#Step 4.1: Generate MCQs based on statements
step4_system_message1 = f"""
You will be given a statement and a key.
With the info from the key, generate questions so that the answers will be similar to the phrase.

Use the key in the dict to determine what kind of question you should generate. \

Example 1: '''
Statement: "The capital of France is Paris, located in the middle of France"
Key: "'Where': 'in the middle of France'"
Output: "Where is Paris"
'''

Example 2: '''
Statement: "In the middle of the forest, there was a bear."
Key: "'What': 'bear'"
Output: "What is in the middle of the forest"
'''
"""

#Step 4.2: Generate options for the question
step4_system_message2 = f"""
You will be given a question, a statement and a passage summary. Extract any details necessary from the passage, as well as the statement \
to generate 3 OPTIONS for the question.
You should follow these steps:
Step 1: Extract the first word of the question
Step 2: Search for details relating to the first word in the statement, and the passage summary
Step 3: Pick 3 details, and put those as options, with ONLY 1 being the correct answer. The options must not be similar to one another.
Step 4: Output in the following format: '
Question: <question>
A. <option 1>
B. <option 2>
C. <option 3>
'
"""
#Step 5.1: Locate the place of possible answers in the passage using main subjects.
step5_system_message1 = f"""
You will be given an entire passage called ExtractedPassage.txt, and a statement.\
Output for me the paragraph that contains the most information related to the statement.
Aside from that, also output for me the paragraph number and your reasonings for the paragraph number.

Output in the following format:
{{
    "paragraph_number": <>,
    "paragraph": "<paragraph>",
    "explanation": "<explanation>"
}}
"""

#Step 6.1: Generate questions about the location of the paragraph.
step6_system_message1 = f"""
You will be given a statement. Find the main subject of the sentence.\
There can only be one main subject.
Output the following sentence using the main subject:
`In which paragraph can the <main_subject> be found>`
"""
#Change it from MCQs to free-response style

step7_system_message1 = f"""
You will be given a paragraph, and a statement. \
Output sentences from the paragraph that contains information related to the statement.
Output in the following format:
{{
    "sentence": []
}}
""" 
#Step 7.2: Extract the details of the sentence(s)
step7_system_message2 = f"""
Given a statement, provide answers to the following questions using only the information given in the sentence:

- What is currently happening? Answer in one or two sentences.
- Who is mentioned in the statement? List all individuals or groups mentioned.
- Where is the event or action taking place? If the statement does not mention a location, specify "None."
- Why is this event or action happening? If the statement does not provide a reason, specify "None."
- How is this event or action occurring? If the statement does not explain the process, specify "None."
- When is this event or action taking place? If the statement does not indicate a time, specify "None."

Please format your response in JSON with the following keys: "What," "Who," "Where," "Why," "How," and "When."

Example: ```
{{
    'What': '<>',
    'Who': '<>',
    'Where': '<>', 
    'Why': '<>', 
    'How': '<>', 
    'When': '<>'
}}
```
"""

#Step 8: Compare the answers
step8_system_message1 =  f"""
You will be given an array called `sentences` and a statement.\
Compare the contents of the statement with the content of the sentences in the array.
If the statement contains information that is conflicting with the sentences, output "False"
If the statement is similar to the sentences, output "True".
If it cannot be determined whether the given statement is True or False from the passage, \
due to lack of information, output "Not Given" instead of "False"


Along with that, output your explanation as well.

Output in the following format:
{{
    "decision": "<>",
    "explanation": "<explanation>"
}}

"""

def get_completion(prompt, model='gpt-3.5-turbo'):
    messages = [{"role":"user", "content":prompt}]
    response = openai.ChatCompletion.create(
        model = model,
        messages = messages,
        temperature = 0,
        top_p = 0.9
    )
    return response.choices[0].message["content"]

def get_completion_from_messages(messages, model = 'gpt-3.5-turbo', temperature = 0, top_p = 0.9, max_tokens = 500):
    response = openai.ChatCompletion.create(
        model = model,
        messages = messages,
        temperature = temperature,
        top_p = top_p,
        max_tokens = max_tokens,
    )
    
    return response.choices[0].message['content']

def summarise_passage(passage):
    prompt =f"""
    Your task is to identify the paragraphs in this passage.

    Output the answers in a python list format.

    Paragraph: ```{passage}```

    """
    #Refine to give consistent outputs
    response = get_completion(prompt)

    prompt2 = f"""
    Your task is to summarise each paragraph given in the following list.

    Each summary must emphasise what the paragraph is about, and it must be different than one another.
    Each summary must be only one setence.

    Output the answers in a JSON format

    List: '''{response}'''
    """

    summary = get_completion(prompt2)

    return summary

def extract_phrase(passage_input):
    messages = [
        {'role':'system', 'content': step2_system_message1},
        {'role': 'user', 'content': f"{delimiter}{passage_input}{delimiter}"}
    ]
    
    phrase = get_completion_from_messages(messages)
    
    print("Extracted the phrase")
    return phrase

def extract_questions_clump(passage_input):
    
    phrase = extract_phrase(passage_input)
    
    user_message = f"""
    Text file: {passage_input}
    Phrase: {phrase}
    """
    messages = [
        {'role':'system', 'content': step2_system_message2},
        {'role': 'user', 'content': f"{delimiter}{user_message}{delimiter}"}
    ]
    
    response = get_completion_from_messages(messages)
    
    print("Extracted the clump")
    return response

def extract_questions(passage_input):
    
    clump = extract_questions_clump(passage_input)
    
    user_message = f"""
    Text file: {clump}
    """ 
    messages = [
        {'role':'system', 'content': step2_system_message3},
        {'role': 'user', 'content': f"{delimiter}{user_message}{delimiter}"}
    ]
    
    response = get_completion_from_messages(messages)
    response_list:dict = output_to_string(response)
    
    print("Extracted the questions")
    return response_list

def extract_paragraphs(passage):
    system_message = f"""
    You will be given a passage. Most of the paragraphs are already seperated out with line breaks. \
    Your job is to identify any lines that ends with ".<punctuation marks>" that doesn't have a line break followed with it, and add a line break after that point.
    """
    
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': {passage}}
    ]

    paragraph = get_completion_from_messages(messages)
    return paragraph

def output_to_string(output:str):
    print("str output=== ", output)
    if output is None:
        return None
    try:
        # output = output.replace("'s", "`s")
        # output = output.replace("s'", "s`")
        # output = output.replace("'", "\"") #   '{ m''n}'
        data = json.loads(output)
        return data
    except json.JSONDecodeError:
        #print("Error: Invalid JSON String")
        return None
     
def extract_infos_statement(statement:str):
    #information_questions = []


#    statements = ["Many Madagascan forests are being destroyed by attacks from insects.", 
#            "Loss of habitat has badly affected insectivorous bats in Madagascar",
#            "Ricardo Rocha has carried out studies of bats in different parts of the world.",
#            "Habitat modification has resulted in indigenous bats in Madagascar becoming useful to farmers.",
#           "The Malagasy mouse-eared bat is more common than other indigenous bat species in Madagascar.",
#          "Bats may feed on paddy swarming caterpillars and grass webworms."]
    user_message = statement

    messages = [
        {'role': 'system', 'content': step3_system_message1},
        {'role': 'user', 'content': f"{user_message}"}
    ]

    actor_acted = output_to_string(get_completion_from_messages(messages))
    information_question = actor_acted
    
    #print(information_question)

    messages = [
    {'role': 'system', 'content': step3_system_message2},
    {'role': 'user', 'content': f"{user_message}"}
    ]

    output = output_to_string(get_completion_from_messages(messages))
    #print(output)
    information_question['questions'] = output

    return information_question

def generate_questions_for_statement(information_question, statement:str, passage_summary):
    MCQ_questions = []
    for i in information_question['questions']["Who/What/Where/Why/How"].keys():
        #print(i)
        if information_question['questions']["Who/What/Where/Why/How"][i] == None or information_question['questions']["Who/What/Where/Why/How"][i] == "None":
            pass #Temp solution, will output nothing in future
        else:
            user_message2 = f"""
            Statement: {statement} 
            Dictionary: "{i}": "{information_question['questions']["Who/What/Where/Why/How"][i]}"
            """
            messages = [
                {'role': 'system', 'content': step4_system_message1},
                {'role': 'user', 'content': f"{user_message2}"}
            ]

            question = get_completion_from_messages(messages)
            #print(question)
            
            user_message = f"""
            Statement: {statement}
            Question: {question}
            Passage Summary: {passage_summary}
            """
            messages = [
                {'role': 'system', 'content': step4_system_message2},
                {'role': 'user', 'content': f"{user_message}"}
            ]

            full_question = get_completion_from_messages(messages)
            MCQ_questions.append(full_question)
    
    return MCQ_questions

def find_location_of_answers(extractedPassage, statement):
    user_message = f"""
    Passage: {extractedPassage}
    Statement: {statement}
    """
    messages = [
        {'role': 'system', 'content': step5_system_message1},
        {'role': 'user', 'content': user_message}
    ]

    response = get_completion_from_messages(messages)
    location = output_to_string(response)

    return location

def generate_questions_for_locations(statement):
    user_message = f"""
    Statement: {statement}
    """

    messages = [
        {'role': 'system', 'content': step6_system_message1},
        {'role': 'user', 'content': user_message}
    ]

    questions = get_completion_from_messages(messages)
    return questions

def locate_sentences_in_paragraph(paragraph, statement):
    #main_subject = infos['main_subject']

    user_message = f"""
    Paragraph: {paragraph}
    Statement: {statement}
    """
    messages = [
        {'role': 'system', 'content': step7_system_message1},
        {'role': 'user', 'content': user_message}
    ]

    response = get_completion_from_messages(messages)
    sentences = output_to_string(response)

    return sentences  

def compare_sentences(sentences, statement):
    user_message = f"""
    Sentences: {sentences}
    Statement: {statement}
    """

    messages = [
        {'role': 'system', 'content': step8_system_message1},
        {'role': 'user', 'content': user_message}
    ]

    response = get_completion_from_messages(messages)
    verdict = output_to_string(response)

    return verdict