from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from llmapp.settings import NEO4J_URI
from llmapp.settings import NEO4J_USER
from llmapp.settings import NEO4J_PASSWORD


class GraphDBModule:
    @staticmethod
    def graphChain(llm):
        # graphDB 로드 및 설정
        graph = Neo4jGraph(url=NEO4J_URI, username=NEO4J_USER, password=NEO4J_PASSWORD)
        # graphDB 체인 설정
        chain = GraphCypherQAChain.from_llm(graph=graph, llm=llm, verbose=True)

        return chain
