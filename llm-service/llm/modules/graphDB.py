from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from llmapp.settings import NEO4J_URI
from llmapp.settings import NEO4J_USER
from llmapp.settings import NEO4J_PASSWORD
from langchain_core.prompts import ChatPromptTemplate


class GraphDBModule:
    @classmethod
    def graphChain(cls, llm, memory):
        # graphDB 로드 및 설정
        graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USER, password=NEO4J_PASSWORD)

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

                SQL 쿼리는 명확하게 출력되어야 하며 따옴표나 다른 것(Markdown)으로 둘러싸지 않아야 합니다.
                아래에 나열된 표만 사용하십시오.
                
                {table_info}
                
                History: {history}
                Question: {input}
            """
        )
        # graphDB 체인 설정
        chain = GraphCypherQAChain.from_llm(graph=graph, llm=llm, prompt=prompt, memory=memory, verbose=True)

        return chain
