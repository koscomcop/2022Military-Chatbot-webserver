import numpy as np
import pandas as pd
import pickle
from konlpy.tag import Mecab
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# 환경 설정
import logging
logger = logging.getLogger("intentclassifier")
intents = {
    0: 'pay',
    1: 'welfare',
    2: 'personnel',
    3: 'book',
    4: 'housing',
    5: 'menu',
    6: 'chat'
 }
max_len = 20

# Mecab 설정
mecab = Mecab()

# 모델 로드
work_dir = '/root/2022_chatbot/rest-server'
intent_model = load_model(work_dir+'/apps/models/intent_model.h5')
with open(work_dir+'/apps/models/intent_tokenizer.pickle', 'rb') as handle:
    intent_tokenizer = pickle.load(handle)

class IntentClassifier:
    def __init__(self):
        print("This is classifier")

    def classify(self, context):
        logger.info(f'input : {context}')

        context = mecab.morphs(context) # 토큰화
        encoded = intent_tokenizer.texts_to_sequences([context]) # 정수 인코딩
        pad_new = pad_sequences(encoded, maxlen = max_len, padding='post') # 패딩
        y_predicted = intent_model.predict(pad_new) # 예측
        max_predicted = np.argmax(y_predicted, axis=-1) # 원-핫 인코딩을 다시 정수 인코딩으로 변경함.
        return intents[max_predicted[0]], y_predicted