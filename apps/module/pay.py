# 환경 설정
import logging
import re
from .dbutil import DButils

logger = logging.getLogger()


class Pay:
    def __init__(self):
        logger.info("급여 관련 질문처리")
        self.db_engine = DButils().get_engine()

    def answer(self, rank, pay):
        try:
            message = f"직급 : {rank} "
            query = f"select {rank} from `국방부_군인(간부)_봉급표_20200930`"
            if pay != "":
                pay = int(re.sub(r'[^0-9]', '', pay))
                query += f" where 호봉 = {pay}"
            query_result = self.db_engine.execute(query).fetchall()

            if len(query_result) == 1:
                message += f" {pay} 호봉의 급여는 {query_result[0]}원 입니다."
            else:
                idx = 1
                for result in query_result:
                    if result.values()[0] is None:
                        break
                    message += f"{idx} 호봉의 급여는 {result.values()[0]}원 입니다."
                    idx += 1

            logger.info(message)
            return message
        except Exception as e:
            logger.info(e)
            return "검색결과가 존재하지 않습니다."
