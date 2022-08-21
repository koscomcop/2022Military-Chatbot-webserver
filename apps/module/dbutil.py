import pandas as pd
from sqlalchemy import create_engine


class DButils:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        cls = type(self)
        if not hasattr(cls, "_init"):
            self.engine = create_engine(
                "mysql+pymysql://",
                echo=False,
                pool_recycle=3600,
                pool_pre_ping=True,
            )
            cls._init = True

    def get_engine(self):
        return self.engine
