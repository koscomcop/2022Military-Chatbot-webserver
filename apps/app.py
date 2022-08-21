# 플라스크 적용
from flask import Flask, request, send_file
from flask_api import status
import json

from datetime import datetime
from pytz import timezone
import module.mylogging as mylogging
import logging

from module.casualtalker import CasualTalker
from module.intentclassifier import IntentClassifier
from module.ner import NamedEntityRecognition
from module.ner import NerTag
from module.pay import Pay
from module.welfare import Welfare
from module.personnel import Personnel
from module.housing import Housing
from module.book import Book
from module.menu import Menu

# 로깅설정
def timetz(*args):
    return datetime.now(tz).timetuple()

tz = timezone("Asia/Seoul")  # UTC, Asia/Shanghai, Europe/Berlin
logging.Formatter.converter = timetz
mylogging.setup_logging()
logger = logging.getLogger()

app = Flask(__name__)
# 일상대화
casualtalker = CasualTalker()
# 의도분류
intentclassifier = IntentClassifier()
# 개체명인식
ner = NamedEntityRecognition()

# 급여
pay = Pay()
# 복지
welfare = Welfare()
# 정원
personnel = Personnel()
# 주거
housing = Housing()
# 도서
book = Book()
# 식단
menu = Menu()

@app.route("/")
def greeting():
    return "This is 2022Chatbot Python API ! "


@app.route("/chat", methods=["POST"])
def get_answer():
    logger.info(f"In Chat => {request}")
    if request.method == "POST":
        params = request.form
        logger.info(f"request body {params}")
        text = params["input1"]

        try:
            invs_intent = {
                'pay': '급여',
                'welfare': '복지시설',
                'personnel': '인원',
                'book': '도서',
                'housing': '주거',
                'menu': '식단',
                'chat': '일상대화'
            }
            intent, possibilities = intentclassifier.classify(text)
            result = f"{invs_intent[intent]}정보에 대해 물어보신 것 같네요! 제가 찾은 정보는..\n\n"
            logger.info(f"intent : {intent}")

            if intent == "menu":
                logger.info("식단")
                result += menu.answer(
                    ner.get_named_entity(text, NerTag.TROOPS)
                )
            elif intent == "book":
                logger.info("도서")
                result += book.answer(
                    ner.get_named_entity(text, NerTag.BOOKS),
                    ner.get_named_entity(text, NerTag.AUTHOR),
                )

            elif intent == "pay":
                logger.info("급여")
                result += pay.answer(
                    ner.get_named_entity(text, NerTag.RANK),
                    ner.get_named_entity(text, NerTag.PAY),
                )
                
            elif intent == "welfare":
                logger.info("복지")
                result += welfare.answer(
                    ner.get_named_entity(text, NerTag.LOC),
                    ner.get_named_entity(text, NerTag.FAC),
                )
                
            elif intent == "personnel":
                logger.info("정원")
                result += personnel.answer(
                    rank=ner.get_named_entity(text, NerTag.RANK),
                    miltype=ner.get_named_entity(text, NerTag.MILTYPE),
                )
                
            elif intent == "housing":
                logger.info("주거")
                result += housing.answer(
                    loc=ner.get_named_entity(text, NerTag.LOC),
                    house=ner.get_named_entity(text, NerTag.HOUSE),
                    miltype=ner.get_named_entity(text, NerTag.MILTYPE),
                )
            else:
                logger.info("일상대화 or etc")
                result = casualtalker.return_similar_answer(text)

            resbody = {
                "outputs": {
                    "text": result,
                },
            }
            jsonres = json.dumps(resbody, ensure_ascii=False)

            return (
                jsonres,
                status.HTTP_200_OK,
                {
                    "Content-Type": "application/json; charset=utf-8",
                    "Access-Control-Allow-Origin": "*",
                },
            )

        except Exception as e:
            raise Exception("Fail to predict", e)


@app.route("/casualtalk", methods=["POST"])
def get_casual_response():
    logger.info(f"In Casual => {request}")
    if request.method == "POST":
        params = request.get_json()
        logger.info(f"request body {params}")
        text = params["inputs"]["text"]
        try:
            result = casualtalker.return_similar_answer(text)
            resbody = {
                "outputs": {
                    "text": result,
                },
            }

            jsonres = json.dumps(resbody, ensure_ascii=False)
            logger.info(f"json response : {jsonres}")

            return (
                jsonres,
                status.HTTP_200_OK,
                {
                    "Content-Type": "application/json; charset=utf-8",
                    "Access-Control-Allow-Origin": "*",
                },
            )

        except Exception as e:
            raise Exception("Fail to get casual response", e)

@app.route('/get_image')
def get_image():   
    if request.args.get('type') == '1':
        today = datetime.now().strftime('%Y%m%d')
        filename = '/root/2022_chatbot/news_wordcloud/%s/wordcloud.png' % today
    else:
        filename = '/root/2022_chatbot/news_wordcloud/error.png'
    return send_file(filename, mimetype='image/gif')

# 메인 테스트
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
