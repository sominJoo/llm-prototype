from llmapp import settings
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain


class BasicDBModule:
    @classmethod
    def dbChain(cls, llm):
        """
        일반 DB을 LLM에 연동하는 모듈.
        :param llm: 선언한 LLM 모델
        :return: SQLDatabaseChain
        """
        sql_url = f"postgresql+psycopg2://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DATABASE}"
        db = SQLDatabase.from_uri(sql_url)
        db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)

        return db_chain
