from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import openai

# Create your views here.

# Initialize an empty conversation history
conversation_history = []

def reset_conversation():
    global conversation_history
    conversation_history = []

def ask_openai(message):
    openai.api_key = settings.OPENAI_API_KEY2

    # Append the user's message to the conversation history
    conversation_history.append({"role": "user", "content": message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k", messages=conversation_history, max_tokens=15000)

    # Get the assistant's reply from the response
    try:
        answer = response['choices'][0]['message']['content'].replace('<br>', '').replace('\n', '')
    except:
        answer = 'Oops try again'

    # Append the assistant's reply to the conversation history
    conversation_history.append({"role": "assistant", "content": answer})

    return answer

def chatbot(request):
    if request.method == 'GET':
        reset_conversation()  # Reset conversation history when the page is reloaded

    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)
        return JsonResponse({'message': message, 'response': response})
    
    return render(request, 'chatbot.html')