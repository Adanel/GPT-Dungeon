import os
from dotenv import find_dotenv, load_dotenv
from PIL import Image
from io import BytesIO
import requests
import gradio as gr
import openai

dotenv_path = find_dotenv()
load_dotenv(dotenv_path) 

openai.api_key = os.getenv("API_KEY")


message_history = [{"role": "user", "content": f"You are a Game Master that have to guide a user troughout an adventure. You will first ask him the subject of the story, it could be fantasy, post apocalyptic, sci fi, anything he wants. You will then describe step by step what happens to him and whar choices he has to do to advance the game. At each step of the story, you will propose different choices to the user so that it can advance. You can propose him choices that involve honour, treachery, logic, fun, anything but the choices should come by 4 and be different. Each choices should have consequences, they can give him useful rewards for the next stes, meet companions to help him in his quest, or hurt him and even kill him, putting an end to the adventure.  If you understand, say OK."},
                   {"role": "assistant", "content": f"OK"}]

def predict(input):
    # tokenize the new input sentence
    message_history.append({"role": "user", "content": f"{input}"})

    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo", #10x cheaper than davinci, and better. $0.002 per 1k tokens
      messages=message_history
    )
    #Just the reply:
    reply_content = completion.choices[0].message.content#.replace('```python', '<pre>').replace('```', '</pre>')

    print(reply_content)
    message_history.append({"role": "assistant", "content": f"{reply_content}"}) 
    
    # get pairs of msg["content"] from message history, skipping the pre-prompt:              here.
    response = [(message_history[i]["content"], message_history[i+1]["content"]) for i in range(2, len(message_history)-1, 2)]  # convert to tuples of list
    
    image_response = openai.Image.create(
                                    prompt=reply_content,
                                    n=1,
                                    size="512x512"
                                    )
    
    # Get the URL of the generated image
    image_url = image_response['data'][0]['url']

    # Create a Gradio component to display the image
    reponse_url = requests.get(image_url)
    img = Image.open(BytesIO(reponse_url.content))
    image = gr.Image(img)

    # Combine the response text and the image into a Gradio component
    response_component = gr.Group([gr.Text(reply_content), image])

    return response, response_component

# creates a new Blocks app and assigns it to the variable demo.
with gr.Blocks() as demo: 

    # creates a new Chatbot instance and assigns it to the variable chatbot.
    chatbot = gr.Chatbot() 
    
    title = gr.Text("Adventure-GPT")

    # creates a new Row component, which is a container for other components.
    with gr.Row(): 
        '''creates a new Textbox component, which is used to collect user input. 
        The show_label parameter is set to False to hide the label, 
        and the placeholder parameter is set'''
        txt = gr.Textbox(show_label=False, placeholder="Enter text and press enter").style(container=False)
    '''
    sets the submit action of the Textbox to the predict function, 
    which takes the input from the Textbox, the chatbot instance, 
    and the state instance as arguments. 
    This function processes the input and generates a response from the chatbot, 
    which is displayed in the output area.'''
    txt.submit(predict, txt, chatbot) # submit(function, input, output)
    #txt.submit(lambda :"", None, txt)  #Sets submit action to lambda function that returns empty string 

    '''
    sets the submit action of the Textbox to a JavaScript function that returns an empty string. 
    This line is equivalent to the commented out line above, but uses a different implementation. 
    The _js parameter is used to pass a JavaScript function to the submit method.'''
    txt.submit(None, None, txt, _js="() => {''}") # No function, no input to that function, submit action to textbox is a js function that returns empty string, so it clears immediately.
         
demo.launch()