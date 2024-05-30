# API에 대한 동작
import re

from llm.modules import graphDB, db, docs
from rest_framework.views import APIView

from llmapp import settings
from llmapp.response import auto_response
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain


class ChatAPIView(APIView):
    memory_dict = {}
    DEFAULT_PROMPT = """
        이전 대화 내용 {history}를 기반으로 {input}에 대한 답변을 합니다.
        
        History: {history}
        Question: {input}
        
        답변은 명확하게 문자열만 출력해야하며 따옴표나 다른 것(Markdown)으로 둘러싸지 않아야 합니다.
    """
    @auto_response
    def post(self, request):
        """
        Chat API
        :param request: { chat : "", file: "", thread_id: ""}
        :return: LLM 답변 문자열
        """
        question = request.data["chat"]
        file = request.data["file"]
        thread_id = request.data["thread_id"]

        # 질문 확인
        if not question:
            return "질문을 입력해 주세요"

        # TODO: LLM 모델변경 기능 추가
        llm = ChatOpenAI(temperature=0, api_key=settings.OPENAI_API_KEY, model_name='gpt-3.5-turbo')

        # 메모리 가져오기
        memory = self.get_memory(thread_id)

        # Question 분석 / 질문 타입 찾기
        question_type = self.check_chain_type(llm, question, memory)
        print("question_type = ", question_type)

        result = ""
        # type에 따른 분기
        try:
            if question_type == "graph":
                graphDB_chain = graphDB.GraphDBModule.graphChain(llm, memory)
                response = graphDB_chain.invoke(question)
                result = response["result"]
            elif question_type == "db":
                db_chain = db.BasicDBModule.dbChain(llm, memory)
                response = db_chain.invoke(question)
                result = response["result"]
            elif question_type == "llm":
                llm_chain = ConversationChain(
                    llm=llm,
                    memory=memory,
                    prompt=ChatPromptTemplate.from_template(self.DEFAULT_PROMPT),
                    output_key="answer"
                )
                response = llm_chain.invoke({"input": question})
                result = response["answer"]
            elif question_type == "docs":
                url = self.parse_url(question)
                dcos_chain = None
                if url:
                    dcos_chain = docs.DoscModule.urlChain(llm, url, memory)
                elif file:
                    dcos_chain = docs.DoscModule.docsChain(llm, file, memory)

                response = dcos_chain.invoke({"input": question})
                result = response["answer"]

            # 메모리 저장
            memory.save_context({"input": question}, {"answer": result})
        except Exception as e:
            result =e
            # result = "정확한 답을 알수 없습니다."
        return result

    @staticmethod
    def check_chain_type(llm, question, memory):
        """
        질문을 분석서 질문의 타입을 반환해주는 정적 메소드이다.
        :param memory: 이전 대화내용
        :param llm: 선언 LLM 모델
        :param question: 사용자의 질문 입력값
        :return: graph | db | docs | llm
        """
        # Question 분석 찾기
        question_prompt = ChatPromptTemplate.from_template(
            """ 
                당신은 질문을 분석하는 프롬프트입니다.
                질문, History를 분석해서 graphDB(neo4j) 쿼리 질문, postgresql 쿼리 질문, 일반 LLM 질문, 문서 질문으로 분류합니다.
                graph db(neo4j) 관련 질문이면 'graph',
                DB 관련 질문이면 'db',
                Url이 있고 문서에 관련된 질문이면 'docs',
                모두 아니면 'llm'을 반환합니다.
                
                History: {history}
                Question: {input}
                
                답변은 명확하게 문자열만 출력해야하며 따옴표나 다른 것(Markdown)으로 둘러싸지 않아야 합니다.
            """
        )

        question_llm_chain = ConversationChain(
            llm=llm,
            memory=memory,
            prompt=question_prompt,
            output_key="answer"
        )
        response = question_llm_chain.invoke({"input": question})

        return response["answer"]

    @staticmethod
    def parse_url(question):
        """
        질문에서 URL을 파싱하기 위한 정적 메소드이다.
        :param question: 사용자의 질문 입력값
        :return: URL 문자열 또는 오류 문자열
        """
        url_regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$\-@\.&+:/?=]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        result = re.findall(url_regex, question)
        if result:
            return result[0]
        return None

    @classmethod
    def get_memory(cls, thread_id):
        """
        메모리에서 저장된 대화내역을 불러옴
        :param thread_id: 대화내역 ID
        :return: ConversationBufferMemory
        """
        if thread_id not in cls.memory_dict:
            cls.memory_dict[thread_id] = ConversationBufferMemory(memory_key="history")
        return cls.memory_dict[thread_id]
