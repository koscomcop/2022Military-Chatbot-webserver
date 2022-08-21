from tqdm import tqdm
import numpy as np
from numpy import dot
from numpy.linalg import norm
from sentence_transformers import SentenceTransformer

import pandas as pd
import urllib.request

# 로깅
import logging

logger = logging.getLogger("casualtalker")


class CasualTalker:
    def __init__(self):

        self.model = SentenceTransformer(
            "sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens",
        )
        self.answers = pd.read_csv(
            "./data/chatData.csv",
            engine="python",
            encoding="utf-8-sig",
            error_bad_lines=False,
        )

    def return_similar_answer(self, input):
        logger.info(f"input : {input}")

        def cos_sim(A, B):
            return dot(A, B) / (norm(A) * norm(B))

        ret = dict()
        embedding = self.model.encode(
            input,
        )
        self.answers["score"] = self.answers.apply(
            lambda x: cos_sim(
                np.fromstring(
                    x["embedding"].replace("[", "").replace("]", ""),
                    dtype="float32",
                    sep=" ",
                ),
                embedding,
            ),
            axis=1,
        )
        ret["answer"] = self.answers.loc[self.answers["score"].idxmax()]["A"]
        logger.info(f"output : {ret['answer']}")
        return ret["answer"]
