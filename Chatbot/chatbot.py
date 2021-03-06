#Rohit Mishra

import random
import json
import pickle
import numpy as np

import nltk 
from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import load_model

import NBATest
import Weather

lemmatizer = WordNetLemmatizer()
intents = json.loads(open('intents.json').read())

words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))
model = load_model('chatbotmodel.h5')

def clean_up_sentence(sentence):
    
    sentence_words = nltk.word_tokenize(sentence)
    
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    
    return sentence_words

def bag_of_words(sentence):
    
    sentence_words = clean_up_sentence(sentence)
    
    bag = [0]*len(words)
    
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    
    return np.array(bag)

def predict_class(sentence):
    
    bow = bag_of_words(sentence)
    
    res = model.predict(np.array([bow]))[0]
    
    ERROR_THRESHOLD = 0.2
    
    results = [[i,r] for i,r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key = lambda x: x[0], reverse=True)

    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

def get_response(intents_list,intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

def nba_retrieve(message):
    player_list = NBATest.get_team_players(message)    
    return player_list

def weather_retrieve(location):
    weather_dict = Weather.get_temp(location)
    return dict(weather_dict)

print("Welcome! Speak to the chatbot!")
check = True
while check:
    message = input("")
    if message == "False":
        check = False

    if "nba" in message.lower():
        print("Enter a team name to see all the players")
        team = input()
        m = nba_retrieve(str(team))
        [print(i) for i in m]
        continue
    
    if "weather" in message.lower():
        print("Enter a location in form \'City,Country(Abbreviated)\'")
        print("Ex: Waco,US")
        loc = input("")
        
        m = weather_retrieve(str(loc))
        new_str = "Temperature (Degrees F): {}, High: {}, Low: {}".format(m['temp'],m['temp_max'],m['temp_min'])
        if m['feels_like'] < 50:
            print("Wear a jacket!")
        elif m['feels_like'] > 80:
            print("Maybe rock that hat!")
        else:
            print("Wonderful weather we're having!")
        print(new_str)
        continue
    
    ints = predict_class(message)
    
    res = get_response(ints,intents)
    
    print(res)

print("Goodbye.")
    