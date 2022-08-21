# 환경 설정
import logging
from .dbutil import DButils

logger = logging.getLogger()

class Personnel:
    def __init__(self):
        logger.info("인원 관련 질문처리")
        self.db_engine = DButils().get_engine()

        
    def chk_ner_valid(self, rank=None, miltype=None):
        rank_nm = ['장교', '부사관', '군무원', '병']
        ranks = [['중위', '소위', '대위','중령', '소령', '대령','준장', '소장', '대장', '별', '장교'], ['중사', '하사', '상사', '원사', '부사관'], ['군무원'], ['일병', '이병', '상병', '병장', '병', '병사']]
        miltypes = [['육군', '해군', '해병대', '공군'], ['카투사', '미군']]
        
        ret_rank = ""
        ret_miltype = ""
        for i, r in enumerate(ranks):
            if rank in r:
                ret_rank = rank_nm[i]
                break
        
        if miltype in miltypes[0]:
            ret_miltype = miltype
        elif miltype in miltypes[1]:
            ret_miltype = '기타'
        
        return ret_rank, ret_miltype
    
    def answer(self, rank=None, miltype=None):
        logger.info(f"{rank}, {miltype}")
        rank, miltype = self.chk_ner_valid(rank, miltype)
        if rank == "" and miltype == "":
            return "조건에 해당하는 정보를 찾지 못했어요."
        elif rank is None or rank=="" or len(rank)==0:
            # 군구분별 전체 인원 답변
            query = f'select * from `국방부_신분별_군_정원_20200101` where 연도 = 2019 and 구분 = "{miltype}"'
            query_result = self.db_engine.execute(query).fetchall()
            return f"2019년 기준 {miltype}의 전체 인원은 장교 {query_result[0][2]}만, 부사관 {query_result[0][3]}만, 병사 {query_result[0][4]}만, 군무원 {query_result[0][5]}만명 입니다."
        elif miltype is None or miltype=="" or len(miltype)==0:
            # 직급별 전체 인원 답변
            query = f'select {rank} from `국방부_신분별_군_정원_20200101` where 연도 = 2019'
            query_result = self.db_engine.execute(query).fetchall()
            return f"2019년 기준 {rank}의 전체 인원은 육군 {query_result[0][0]}만, 해군 {query_result[1][0]}만, 해병대 {query_result[2][0]}만, 공군 {query_result[3][0]}만 기타 {query_result[4][0]}만명입니다."
        else:
            # 군구분별 직급별 인원 답변
            query = f'select {rank} from `국방부_신분별_군_정원_20200101` where 연도 = 2019 and 구분 = "{miltype}"'
            query_result = self.db_engine.execute(query).fetchall()
            return f"2019년 기준 {miltype} {rank}의 전체 인원은 {query_result[0][0]}만명 입니다."

        return message
