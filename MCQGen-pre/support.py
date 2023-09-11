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

###Step 3.1: Extract the main subject of the statement

# step3_system_message1 = f"""
# You will be given a statement. Follow these steps:
# Step 1: Identify the main subject and other subjects of the sentence. The main subject should specify explicitly what it is. \
# If main subject is not found, put the key main_subject as " ".
# Step 2: Identify all the subjects, putting them as seperate values in a key called subjects.



# Example 1: '''
# Statement: `Loss of habitat has badly affected insectivorous bats in Madagascar`
# Process(DO NOT OUTPUT THIS): `
# Step 1: The main subject of the sentence is "insectivorous bats", because they contain a specific animal.
# Step 2: The  subjects are "habitat, Madagascar", "insectivorous bats"

# `
# Output: {{
#     "main_subject": "insectivorous bats",
#     "subjects": "habitat", "Madagascar", "insectivorous bats"
# }}
# '''

# Example 2: '''
# Statement: `Many Madagascan forests are being destroyed by attacks from insects.`
# Process(DO NOT OUTPUT THIS): `
# Step 1: The main subject of the sentence is "Madasgascan's forests", because it contains a specific location.\
# Step 2: The subjects are "insects", "Madagascar's forests"
# `
# Output : {{
#     "main_subject": "Madagascar's forests",
#     "subjects": "insects", "Madagascar's forests"
# }}
# '''

# Example 3: '''
# Statement: `The animals are crazy for the farmer.`
# Process(DO NOT OUTPUT THIS): `
# Step 1: There are no main subject found.
# Step 2: The subjects are "animals", "farmer".

# Output: {{
#     "main_subjects": "",
#     "subjects": "animals", "farmer"
# }}
# `
# '''

# OUTPUT THE ANSWER IN A JSON FORMAT

# """

step3_system_message1 = f"""
You will be given a sentence. Extract the actor and the acted upon in the sentence.
Output the answer in a JSON format, with two keys: "actor", and "acted upon".

"""

#Step 3.2: Extract the details using the Wh- questions
step3_system_message2 = f"""
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
<options>
'
"""
#Step 5.1: Locate the place of possible answers in the passage using main subjects.
step5_system_message1 = f"""
You will be given a passage summary, two subjects called 'actor' and 'acted upon'. \
Find which summary the main subject belong to and output the summary number. \
Limit the locations to one.
Output that summary number and explain your process in the following format.

Example: '''
{{
    "paragraph": "7",
    "explanation": "<explanation>"
}}
'''
"""

#Step 6.1: Generate questions about the location of the paragraph.
step6_system_message1 = f"""
You will be given a two subjects, 'actor' and 'acted upon', and a key in a dictionary called "summarised". 
Use the value in the keys to generate a question in the following format.
'Which paragraph can you find <main_subject>'

Output the question in the following format:
{{
    "question": "<question 1>"
}}
"""
#Change it from MCQs to free-response style

#MASSIVE ERROR#MASSIVE ERROR#MASSIVE ERROR#MASSIVE ERROR#MASSIVE ERROR#MASSIVE ERROR#MASSIVE ERROR#MASSIVE ERROR#MASSIVE ERROR#MASSIVE ERROR#MASSIVE ERROR

#Step 6.2: Generate options for the questions
# step6_system_message2 = f"""
# You will be given a question, a main subject, and a dictionary of summary of paragraphs. 
# Generate 3 options for the question using the following step:
# Step 1: Identify where the main subject appear in the summaries. If the main subject appear once, move to Step 2. Else, move to Step 1.5
# Step 1.5: Avoid those summaries containing the main subject, and pick 2 random summary. Move to Step 3.
# Step 2: Pick 2 random summary from the dictionary. Move to Step 3.
# Step 3: Put the correct summary to the question as another option.
# Step 4: Output the question as well as the options.

# """

#Step 7.1: Inside a paragraph, find the sentences containing the information.


# step7_system_message1 = f"""
# You are given a sentence and dictionary called "infos". \
# Extract values from infos[acted upon] and find synonyms of the value, in its entirety, in the sentence.
# If there is no synonyms, output "None"
# If there are, output the sentence and the words you used to decide sentiment.
# """
step7_system_message1 = f"""
You are given two subjects called 'acted' and 'acted upon'. For each subject, find ONLY 1 sentence in the paragraph that mentions the subject.\

If the two subjects are in the same sentence, only output that sentence.
If the two subjects are in different sentences, output those 2 sentences.
Output the sentences and your specific explanation in a JSON format with two keys, 'sentence' and 'explanation'.

Example: ```
{{
    'sentences': ['<sentence 1>', '<sentence 2>'],
    'explanation': '<explanation>'
}}
```
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
You will be given two set of dictionaries. For each corresponding keys in each dictionaries, compare the similarity between the values.
If there are any differences, output it and specify what is different.
If there are no differences, output it.

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
    if output is None:
        return None
    try:
        output = output.replace("'", "\"")
        data = json.loads(output)
        return data
    except json.JSONDecodeError:
        print("Error: Invalid JSON String")
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
    
    print(information_question)

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
    for i in information_question['questions'].keys():
        #print(i)
        if information_question['questions'][i] == None or information_question['questions'][i] == "None":
            pass #Temp solution, will output nothing in future
        else:
            user_message2 = f"""
            Statement: {statement} 
            Dictionary: "{i}": "{information_question['questions'][i]}"
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

def find_location_of_answers(summary, main_subject):
    user_message = f"""
    Passage Summary: {summary}
    Main subject: {main_subject['actor']}
    Subjects: {main_subject['acted upon']}
    """
    messages = [
        {'role': 'system', 'content': step5_system_message1},
        {'role': 'user', 'content': user_message}
    ]

    location = get_completion_from_messages(messages)

    return location

def generate_questions_for_locations(infos, paragraph_summary):
    main_subject = infos['actor']

    user_message = f"""
    Main subject: {main_subject}
    Paragraph summmary: {paragraph_summary}
    """

    messages = [
        {'role': 'system', 'content': step6_system_message1},
        {'role': 'user', 'content': user_message}
    ]

    questions = get_completion_from_messages(messages)
    return questions

def locate_sentences_in_paragraph(paragraph, infos):
    #main_subject = infos['main_subject']

    user_message = f"""
    Subjects: {infos}
    Paragraph: {paragraph}
    """
    messages = [
        {'role': 'system', 'content': step7_system_message1},
        {'role': 'user', 'content': user_message}
    ]

    sentences = get_completion_from_messages(messages)
    return sentences   