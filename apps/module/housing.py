# 환경 설정
import logging
from .dbutil import DButils
import pandas as pd

logger = logging.getLogger()

class Housing:
    def __init__(self):
        logger.info("주거 관련 질문처리")
        self.db_engine = DButils().get_engine()
        
    def chk_ner_valid(self, loc=None, house=None, miltype=None):
        ners = [loc, house, miltype]
        ret = [0,0,0]
        dbs = ['chatbot2022.`국방부_영외_군인아파트 현황_20201231`', 'chatbot2022.`국방부_현역군인_내_집_마련_정보_20210816`']
        cols = [
            [['시도', '시군구'], ['단지명'], ['군구분']],
            [['위치', '주택공급명'], ['주택공급명'], 0],
        ]
        
        n_ner = len(cols[0]) # Number of ner tag
        for j, db in enumerate(dbs):
            for i, col in enumerate(cols[j]): # cols[0] = [['시도', '시군구'], ['단지명'], ['군구분']],
                if col == 0 or ners[i] == None or ners[i]=="": # col = ['시도', '시군구'], i=0
                    pass
                else:
                    for c in col: # c = '시도'
                        query = f'SELECT * FROM {db} where {c} LIKE "%%{ners[i]}%%";'
                        query_result = self.db_engine.execute(query).fetchall()
                        if len(query_result)>0 and ret[i]==0:
                            logger.info(f"QUERY : {query}")
                            ret[i] = 1
        
        return ''.join(str(x) for x in ret)
        
    def answer(self, loc=None, house=None, miltype=None):
        logger.info(f"{loc}, {house}, {miltype}")
        message = f"요청하신 조건에 해당하는 군인주거시설이 없습니다."
        # type = f"{self.valid(loc)}{self.valid(house)}{self.valid(miltype)}"
        type = self.chk_ner_valid(loc, house, miltype)
        logger.info(f"TYPE {type}")
        
        if type=="000":
            return "주거 관련 정보를 찾지 못했어요."

        elif type=="001":
            # 군구분별 관리중인 시설목록 반환
            query = f'SELECT 시도, 건물형태, COUNT(*) FROM chatbot2022.`국방부_영외_군인아파트 현황_20201231` where 군구분="{miltype}" GROUP BY 시도, 건물형태 order by 시도;'
            query_result = self.db_engine.execute(query).fetchall()
            ret_df = pd.DataFrame(query_result)
            
            message = f"전국 {ret_df[0].nunique()}개 시도에서 {miltype}이 관리중인 군인주거지는 총 {ret_df[2].sum()}곳 입니다.\n\n[상세목록(지역/건물형태/개수)]"
            
            for col in query_result:
                message += f"{col[0]}({col[1]}):\t{col[2]}\n"
                
        elif type.endswith("1"):
            where_clause = f'where 군구분="{miltype}"'
            message = f"2019년 {miltype}에서 관리중인"
            
            if type[0]=="1":
                where_clause = f'{where_clause} and (시도 LIKE "%%{loc}%%" OR 시군구 LIKE "%%{loc}%%")'
                message += f" {loc}"
            if type[1]=="1":
                where_clause = f'{where_clause} and 단지명 LIKE "%%{house}%%"'
                message += f" {house}"

            query = f'SELECT 시군구, 단지명, 건물형태, 준공연도, 공급세대 FROM chatbot2022.`국방부_영외_군인아파트 현황_20201231` {where_clause}'
            query_result = self.db_engine.execute(query).fetchall()
            
            if len(query_result)==0:
                return f"요청하신 조건에 해당하는 군인주거시설이 없습니다."

            message += f" 군인주거시설은 아래와 같습니다.\n\n[시설목록(건물형태/준공연도/공급세대)]\n"
            for idx, col in enumerate(query_result):
                message += f"[{col[0]}]{col[1]} {col[2]}/{col[3]}/{col[4]}\n"

        elif type.endswith("0"):
            
            query1 = ""
            query2 = ""

            if type=="010":
                query1 = f'SELECT * FROM chatbot2022.`국방부_영외_군인아파트 현황_20201231` where 단지명 like "%%{house}%%"'
                query2 = f'SELECT * FROM chatbot2022.`국방부_현역군인_내_집_마련_정보_20210816` where 주택공급명 LIKE "%%{house}%%"'
            elif type=="100":
                query1 = f'SELECT * FROM chatbot2022.`국방부_영외_군인아파트 현황_20201231` where (시도 LIKE "%%{loc}%%" or 시군구 LIKE "%%{loc}%%")'
                query2 = f'SELECT * FROM chatbot2022.`국방부_현역군인_내_집_마련_정보_20210816` where (주택공급명 LIKE "%%{loc}%%" OR 위치 LIKE "%%{loc}%%")'
            else:
                query1 = f'SELECT * FROM chatbot2022.`국방부_영외_군인아파트 현황_20201231` where 단지명 LIKE "%%{house}%%" and (시도 LIKE "%%{loc}%%" OR 시군구 LIKE "%%{loc}%%")'
                query2 = f'SELECT * FROM chatbot2022.`국방부_현역군인_내_집_마련_정보_20210816` where 주택공급명 LIKE "%%{house}%%" and (주택공급명 LIKE "%%{loc}%%" OR 위치 LIKE "%%{loc}%%")'

            # logger.info(query1)
            # logger.info(query2)
            query_result1 = self.db_engine.execute(query1).fetchall()
            query_result2 = self.db_engine.execute(query2).fetchall()

            if len(query_result1)==0 and len(query_result2)==0:
                return f"요청하신 조건에 해당하는 군인주거시설이 없습니다."

            message = f"{house} 관련 군인주거시설 정보는 아래와 같습니다.\n\n"
            for col in query_result1:
                message += f"[{col[1]} {col[2]}]{col[3]} (공급 {col[9]}세대, 준공 {col[8]}년)\n"
            for col in query_result2:
                message += f"{col[1]} (공급 {col[3]}세대, 분양모집일 {col[4]})\n"

        return message

    def valid(self, var):
        if var is None or var=="" or len(var)==0:
            return "0"
        else:
            return "1"