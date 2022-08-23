# 환경 설정
import logging
from .dbutil import DButils

import re
import requests
import json

logger = logging.getLogger()

class Menu:
    def __init__(self):
        logger.info("식단 관련 질문처리")
        self.db_engine = DButils().get_engine()

    def answer(self, troops=None):
        logger.info(f"부대명 공백제거 전: {troops}")
        troops = troops.replace(' ', '')
        logger.info(f"부대명 공백제거 후: {troops}")
        
        if troops is None or troops=="" or len(troops)==0:
            return "식단을 찾을 수 없어요."
        
        p = re.compile("(\d{4})")
        m = p.search(troops)
        
        try:
            troops_no = m.group()
            logger.info(f"부대번호: {troops_no}")
            query = f'SELECT API FROM `식단제공부대` WHERE 부대명 = "{troops}" OR 부대번호 = {troops_no}'
        except:
            logger.info(f"부대번호 찾을 수 없음 => 부대명으로만 검색")
            query = f'SELECT API FROM `식단제공부대` WHERE 부대명 = "{troops}"'
        
        query_result = self.db_engine.execute(query).fetchall()
        
        if len(query_result) > 0:
            logger.info(query_result[0][0])
            logger.info(type(query_result[0][0]))
            # query_result[0][0] : 'https://openapi.mnd.go.kr/sample/xml/DS_TB_MNDT_DATEBYMLSVC_1968
            url = query_result[0][0].replace('sample', '.....')
            url = query_result[0][0].replace('xml', 'json')
            url += '/1/5/'
        
            r = requests.get(url)   

            logger.info(r.text)
            jo = json.loads(r.text)
            logger.info(jo)

            if 'RESULT' in jo.keys():
                return "식단을 제공하지 않는 부대입니다."

            message = f'{troops} 식단을 알려드릴게요.'
            svc_name = query_result[0][0].split('/')[-1]
            menus = jo[svc_name]['row']
            
            '''
{
   "DS_TB_MNDT_DATEBYMLSVC_1968":{
      "list_total_count":229,
      "row":[
         {
            "dinr_cal":"",
            "lunc":"배추김치",
            "sum_cal":"89971.07kcal",
            "adspcfd":"",
            "adspcfd_cal":"",
            "dates":"2022-07-14",
            "lunc_cal":"7.5kcal",
            "brst":"",
            "dinr":"",
            "brst_cal":""
         },
         {
            "dinr_cal":"",
            "lunc":"포도주스",
            "sum_cal":"89971.07kcal",
            "adspcfd":"",
            "adspcfd_cal":"",
            "dates":"2022-07-14",
            "lunc_cal":"108kcal",
            "brst":"",
            "dinr":"",
            "brst_cal":""
         },
         {
            "dinr_cal":"363kcal",
            "lunc":"찹쌀밥",
            "sum_cal":"7257.87kcal",
            "adspcfd":"",
            "adspcfd_cal":"",
            "dates":"2022-07-15",
            "lunc_cal":"388.13kcal",
            "brst":"바비큐볶음밥(완)",
            "dinr":"밥1",
            "brst_cal":"527.63kcal"
         },
         {
            "dinr_cal":"807.95kcal",
            "lunc":"삼계탕(완제품)(18)",
            "sum_cal":"7257.87kcal",
            "adspcfd":"",
            "adspcfd_cal":"",
            "dates":"2022-07-15",
            "lunc_cal":"764.14kcal",
            "brst":"얼갈이된장국(05)(06)",
            "dinr":"쇠고기장터국(완)(05)",
            "brst_cal":"36.67kcal"
         },
         {
            "dinr_cal":"91.15kcal",
            "lunc":"갑오징어야채볶음(05)(06)(17)",
            "sum_cal":"7257.87kcal",
            "adspcfd":"",
            "adspcfd_cal":"",
            "dates":"2022-07-15",
            "lunc_cal":"187.33kcal",
            "brst":"곡물과자",
            "dinr":"감자채카레볶음(02)(05)(06)(16)",
            "brst_cal":"482kcal"
         }
      ]
   }
}
            '''
            
            for m in menus:
                message += '\n' + m['dates'] + ' ' + m['lunc']
            return message
        else:
            return "식단을 제공하지 않는 부대입니다."
