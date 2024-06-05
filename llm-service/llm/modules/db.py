from llmapp import settings
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_core.prompts import ChatPromptTemplate



class BasicDBModule:
    @staticmethod
    def dbChain(llm, memory):
        """
        일반 DB을 LLM에 연동하는 모듈.
        :param llm: 선언한 LLM 모델
        :return: SQLDatabaseChain
        """
        sql_url = f"postgresql+psycopg2://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DATABASE}"
        db = SQLDatabase.from_uri(sql_url)

        # 프롬프트 지정
        prompt = ChatPromptTemplate.from_template(
            """
                입력 질문이 주어지면, 먼저 구문적으로 올바른 {dialect}개의 쿼리를 생성하여 실행한 다음 쿼리 결과를 보고 답을 반환합니다. 
                사용자가 질문에서 얻고자 하는 특정한 수의 예제를 지정하지 않는 한, 쿼리를 최대 {top_k}개의 결과로 제한합니다. 
                데이터베이스에서 가장 적합한 예제를 반환하려면 관련 열로 결과를 반환할 수 있어야 합니다.
                특정 테이블의 모든 열에 대해 쿼리하지 말고 질문이 주어지면 관련 열 몇 개만 요청합니다.
                스키마 설명에서 볼 수 있는 컬럼 이름만 사용하도록 주의합니다. 존재하지 않는 컬럼은 쿼리하지 않도록 주의합니다. 또한 어느 컬럼이 어느 테이블에 있는지도 주의해야 합니다.
  
                다음 형식을 사용합니다:
                
                Question: "Question"
                SQL Query: "실행할 SQL Query"
                SQLResult: "SQL 쿼리의 결과"
                Answer: "최종 답변"
                
                SQL Query는 명확하게 출력되어야 하며 따옴표나 다른 것(Markdown)으로 둘러싸지 않아야 합니다.
                아래에 나열된 표만 사용하십시오. 
                아래 나열된 표 이외에 조회하길 원한다면 SQL 쿼리를 "select * from sys"로 조회합니다.
                
                {table_info}
                
                History: {history}
                Question: {input}"""
        )
        db_chain = SQLDatabaseChain.from_llm(llm, db, prompt,memory=memory, verbose=True)
        return db_chain
