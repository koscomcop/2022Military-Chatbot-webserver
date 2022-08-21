# 환경 설정
import logging
from .dbutil import DButils

logger = logging.getLogger()

class Book:
    def __init__(self):
        logger.info("도서 관련 질문처리")
        self.db_engine = DButils().get_engine()

    def answer(self, books=None, author=None):
        logger.info(f"{books}, {author}")
        message = f"요청하신 조건 ({books}, {author})에 해당하는 도서가 없습니다."
        
        # 도서정보 (제목, 저자) 질문 => 해당 도서가 있는 도서관명 답변
        if books is None or books=="" or len(books)==0:         # 도서명이 없고, 저자로 검색
            query1 = f'SELECT * FROM `국방부_한국국방연구원 도서관 보유 국내외 정기간행물 목록_20210930` WHERE 출판사 LIKE "%%{author}%%"'
            '''
            분류	       간행물명	                        출판사	                간기
            국외 간행물	    Academy of Management Journal	Academy of Management   BM(6)
            국외 간행물	    Academy of Management Review	Academy of Management   QR(4)
            ...
            '''
            
            logger.info(query1)
            query_result1 = self.db_engine.execute(query1).fetchall()
            logger.info(query_result1)

            query2 = f'SELECT * FROM `국방전자도서관_도서정보` WHERE 저작자 LIKE "%%{author}%%"'
            '''
            도서 KEY    제목	        저작자	    발행자	    발행년도 ISBN	    분류 구분	KDC 분류 번호	DDC 분류 번호	기타 분류 번호	페이지	크기	가격	도서관 코드	도서관 명	상태
            2001280940	동원된 근대화	조희연 지음	후마니타스	2010	8964371054	1	340.911					                                            20000	M1	국방대학교 도서관	U
            2001280941	동원된 근대화	조희연 지음	후마니타스	2010	8964371054	1	340.911					                                            20000	M1	국방대학교 도서관	U
            ...
            '''
            
            logger.info(query2)
            query_result2 = self.db_engine.execute(query2).fetchall()
            logger.info(query_result2)

            if len(query_result1)==0 and len(query_result2)==0:
                return message
            
            message = f"{author} 관련 도서 정보는 아래와 같습니다.\n\n"
            for col in query_result1:
                message += f"(한국국방연구원 도서관) {col[1]}, {col[2]}\n"
            for col in query_result2:
                message += f"(국방대학교 도서관) {col[1]}, {col[2]}, {col[3]}\n"
                
        elif author is None or author=="" or len(author)==0:    # 저자가 없고, 도서명으로 검색
            query1 = f'SELECT * FROM `국방부_한국국방연구원 도서관 보유 국내외 정기간행물 목록_20210930` WHERE 간행물명 LIKE "%%{books}%%"'
            query2 = f'SELECT * FROM `국방전자도서관_도서정보` WHERE 제목 LIKE "%%{books}%%"'
            
            logger.info(query1)
            logger.info(query2)
            query_result1 = self.db_engine.execute(query1).fetchall()
            query_result2 = self.db_engine.execute(query2).fetchall()
            
            if len(query_result1)==0 and len(query_result2)==0:
                return message
            
            message = f"{books} 관련 도서 정보는 아래와 같습니다.\n\n"
            for col in query_result1:
                message += f"(한국국방연구원 도서관) {col[1]}, {col[2]}\n"
            for col in query_result2:
                message += f"(국방대학교 도서관) {col[1]}, {col[2]}, {col[3]}\n"
        
        return message
