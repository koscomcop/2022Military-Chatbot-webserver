# 환경 설정
import logging
from .dbutil import DButils

logger = logging.getLogger()


class Welfare:
    def __init__(self):
        logger.info("복지 관련 질문처리")
        self.db_engine = DButils().get_engine()

    def answer(self, loc, fac):
        try:
            if loc == "" and fac == "":
                message = "복지문의의 검색결과가 존재하지 않습니다, 다시 문의 부탁드립니다."
            else:
                message = f"문의하신 "
                if loc != "":
                    message += f"지역은 {loc} "
                if fac != "":
                    message += f"시설은 {fac} "
                message += "입니다. \n"

                # Query 예시
                # 1 SELECT 구분, 시설명, 주소, 연락처 FROM `국군복지단_복지시설_20220426` WHERE 주소 LIKE '%%서울%%' AND 시설명 LIKE '%%대방%%'
                # 2 SELECT 시설명, 지역1, 지역2, 주소1, 주소2, 일반전화, 축제행사 FROM `국군복지단_복지지설_상세_현황_20220426` WHERE 주소1 LIKE '%%강원%%' AND 시설명 LIKE '%%화진포%%'
                # 3 SELECT 병원명, `병원 주소`, `병원 연락처` FROM `국방부_군병원_정보_20200701` WHERE `병원 주소` LIKE '%%강원%%' AND 병원명 LIKE '%%국군강릉병원%%'
                # 4 SELECT `시설 명`, `위치 주소`, `객실 수량`, 규모, 연락처, 부대시설, `홈페이지 주소` FROM `군_복지_휴양시설_10_01_2018` WHERE `위치 주소` LIKE '%%제주%%' AND `시설 명` LIKE '%%서귀포호텔%%'
                # 5 SELECT 사진제목, `관련 시설명`,  시설위치,  연락처 FROM `군_복지시설_주변_관광지_20200831` WHERE 시설위치 LIKE '%%강원%%' AND `관련 시설명` LIKE '%%청간정%%'

                querys = {
                    "복지시설": f"SELECT 시설명, 주소, 연락처 FROM `국군복지단_복지시설_20220426` WHERE 주소 LIKE '%%{loc}%%' AND 시설명 LIKE '%%{fac}%%'",
                    # "복지시설2": f"SELECT 시설명, 주소1, 주소2, 일반전화, 축제행사 FROM `국군복지단_복지지설_상세_현황_20220426` WHERE 주소1 LIKE '%%{loc}%%' AND 시설명 LIKE '%%{fac}%%'",
                    "병원시설": f"SELECT 병원명, `병원 주소`, `병원 연락처` FROM `국방부_군병원_정보_20200701` WHERE `병원 주소` LIKE '%%{loc}%%' AND 병원명 LIKE '%%{fac}%%'",
                    "휴양시설": f"SELECT `시설 명`, `위치 주소`, 규모, 연락처, 부대시설, `홈페이지 주소` FROM `군_복지_휴양시설_10_01_2018` WHERE `위치 주소` LIKE '%%{loc}%%' AND `시설 명` LIKE '%%{fac}%%'",
                    "관광지정보": f"SELECT `관련 시설명`, 사진제목, 시설위치,  연락처 FROM `군_복지시설_주변_관광지_20200831` WHERE 시설위치 LIKE '%%{loc}%%' AND `관련 시설명` LIKE '%%{fac}%%'",
                }
                temp_message = ""
                for key in querys.keys():
                    query = querys[key]
                    query_results = self.db_engine.execute(query).fetchall()
                    query_message = ""
                    if len(query_results) != 0:
                        for query_result in query_results:
                            for info in query_result:
                                query_message += f"{info},"
                            query_message += "\n"
                        query_message = f"[{key} 안내] \n {query_message}\n 있습니다."
                    temp_message += query_message
                if temp_message == "":
                    message += " 검색결과가 존재하지 않습니다."
                else:
                    message += temp_message
                logger.info(message)
            return message
        except Exception as e:
            logger.info(e)
            return "검색결과가 존재하지 않습니다."
