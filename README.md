# CS40 - Incremental Learnable Dialog System
 
### Project description
This repository shows the code for our Capstone project (20s1, Group CS40). The code aims to implement a dialog system that is able to automatically fill a flight-booking webform based on input from the user. Our user interface consists of a chatbox and a webform, in which customers' input in the chatbox is extracted using slot filling from our deep learning NLU model. The slot information is then updated on the webform using JavaScript. Based on the acquired information, the chatbot would search for appropriate responses in our template-based NLG system, which includes a variation of natural-language phrases. After all the necessary slots are filled, the chatbot would reassure the flight details with the user before proceeding. 


### Setup
The system is written in Python 3.7 environment, and mainly relies on the following libraries: \
flask, version 1.0.3, https://flask.palletsprojects.com/en/1.0.x/ \
flask_sijax, version 0.4.1, (https://github.com/spantaleev/flask-sijax) \
six, version 1.12.0, (https://github.com/benjaminp/six) \
nltk, version 3.4.1, (https://www.nltk.org/install.html) \
tensorflow, version 1.13.1, (https://www.tensorflow.org/api_docs/) \
All application dependencies are included in the requirements.txt file and the dependency graph in the repository.

### Usage
To run the model, move the current directory in command prompt to the project root folder, and type in the following command: 
```
cd src
python chat.py
```
After the flask server is set, enter http://127.0.0.1:1234/ in your browser and you can start typing in the chatbox to start filling the flight-booking form. The chatbot also supports TTS(text-to-speech) to receive voice commands.

### Reference
 
Our NLU slot filling model is based on the repository at: https://github.com/HadoopIt/rnn-nlu#attention-based-rnn-model-for-spoken-language-understanding-intent-detection--slot-filling. We have removed the intent detection module, since we define the model to only handle ticket-booking scenarios. Additionally, we have added code for model inference, since the there would be no ground-truth labels for the slots during the prediction stage. Lastly, we have adjusted the code to store the current tensorflow session, so that the model do not have to initialise the layers every time a new utterance is detected.

The dataset used for model training contains dialogues and IOB tags from the ATIS dataset at: https://github.com/yvchen/JointSLU/tree/master/data
