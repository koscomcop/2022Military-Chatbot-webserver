import numpy as np
import pandas as pd
import pickle
from konlpy.tag import Mecab
import numpy as np
import pandas as pd
import pickle
from konlpy.tag import Mecab
from keras.models import load_model
from keras_contrib.layers import CRF
from keras_preprocessing.sequence import pad_sequences
from keras_contrib.losses import crf_loss
from keras_contrib.metrics import crf_viterbi_accuracy
from enum import Enum
from pororo import Pororo

# 환경 설정
import logging

logger = logging.getLogger()
max_len = 35

# Mecab 설정
mecab = Mecab()

# 모델 로드
model_dir = "/root/2022_chatbot/rest-server/apps/models"

with open(model_dir + "/ner_src_tokenizer.pickle", "rb") as handle:
    ner_src_tokenizer = pickle.load(handle)

with open(model_dir + "/ner_tar_tokenizer.pickle", "rb") as handle:
    ner_tar_tokenizer = pickle.load(handle)

ner_model = load_model(
    model_dir + "/ner_model.h5",
    custom_objects={
        "CRF": CRF,
        "crf_loss": crf_loss,
        "crf_viterbi_accuracy": crf_viterbi_accuracy,
    },
)

index_to_ner = ner_tar_tokenizer.index_word
index_to_ner[0] = "PAD"


class NerTag(Enum):
    # 부대명 | TROOPS
    # 시간 | DATES
    # 도서명 | BOOKS
    # 저자명 | PERSON
    # 직급 | RANK
    # 급여 | PAY
    # 시설 | FAC
    # 지역 | LOC
    # 주택 | HOUSE
    # 군구분 | MILTYPE
    TROOPS = 1 
    DATES = 2
    BOOKS = 3
    AUTHOR = 4
    RANK = 5
    PAY = 6
    FAC = 7
    LOC = 8
    HOUSE = 9
    MILTYPE = 10

    @classmethod
    def get_pororo_map_list(cls, nertag):

        if nertag == cls.TROOPS:
            return ['ORGANIZATION','QUANTITY']
        elif nertag == cls.DATES:
            return ['DATE','TIME']
        elif nertag == cls.BOOKS:
            return ['COUNTRY','THEORY']
        elif nertag == cls.AUTHOR:
            return ['PERSON','ORGANIZATION']
        elif nertag == cls.RANK:
            return ['CIVILIZATION','OCCUPATION']
        elif nertag == cls.PAY:
            return ['QUANTITY']
        elif nertag == cls.LOC:
            return ['CITY','LOCATION']
        elif nertag == cls.FAC:
            return ['ARTIFACT']
        elif nertag == cls.HOUSE:
            return ['ARTIFACT']
        elif nertag == cls.MILTYPE:
            return ['ORGANIZATION']



class NamedEntityRecognition:
    def __init__(self):
        self.pororo_ner = Pororo(task="ner", lang="ko")
        logger.info("This is NamedEntityRecognition")

    def predict(self, context):
        # logger.info(f"NER input : {context}")

        morphs = mecab.morphs(context)  # 토큰화

        encoded = ner_src_tokenizer.texts_to_sequences([morphs])  # 정수 인코딩
        pad_new = pad_sequences(encoded, maxlen=max_len)  # 패딩
        y_predicted = ner_model.predict(np.array(pad_new))
        y_predicted = np.argmax(y_predicted, axis=-1)

        ner_predict = []
        for pred in y_predicted[0]:
            if pred != 0:  # PAD값은 제외함.
                ner_predict.append(index_to_ner[pred])

        return morphs, ner_predict

    def get_named_entity(self, context: str, ner_tag: NerTag):
        # logger.info(f"NER input : {context}")
        morphs, ner_predict = self.predict(context)
        # logger.info(f"NER output : {morphs}")
        logger.info(f"NER output : {ner_predict}")
        named_entity = ""

        for morph, named_entity_tag in zip(morphs, ner_predict):
            if ner_tag.name in named_entity_tag:  # PAD값은 제외함.
                named_entity += morph

        # 개체명인식기가 원하는 태그를 못찾은 경우 카카오브레인 뽀로로로 개체명인식시도
        if named_entity == "" :
            logger.info(f"Pororo Ner start")
            pororo_tag_list = NerTag.get_pororo_map_list(ner_tag)
            pororo_result = self.pororo_ner(context)
            logger.info(f"Pororo Ner Search Tag : {pororo_tag_list}")
            logger.info(f"Pororo Ner : {pororo_result}")
            for pororo_tag in pororo_tag_list:
                for pororo_morph in pororo_result:
                    if pororo_morph[1] == pororo_tag:
                        return pororo_morph[0]
        
        return named_entity
