# API에 대한 동작
import re

from llm.modules import graphDB, db, docs
from rest_framework.views import APIView

from llmapp import settings
from llmapp.response import auto_response
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


class ChatAPIView(APIView):
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

        # Question 분석 / 질문 타입 찾기
        question_type = self.check_chain_type(llm, question)
        print("question_type = ", question_type)

        result = ""
        try:
            # type에 따른 분기
            if question_type == "graph":
                graphDB_chain = graphDB.GraphDBModule.graphChain(llm)
                response = graphDB_chain.invoke(question)
                result = response["result"]
            elif question_type == "db":
                db_chain = db.BasicDBModule.dbChain(llm)
                response = db_chain.invoke(question)
                result = response["result"]
            elif question_type == "llm":
                response = llm.invoke(question)
                result = response.content
            elif question_type == "docs":
                url = self.parse_url(question)
                # db_chain = db.BasicDBModule.dbChain(llm, file, url)
                # response = db_chain.invoke({"input": question})
                # result = response["result"]
        except Exception as e:
            result = "정확한 답을 찾을 수 없습니다."

        print("response = ", result)

        return result

    @staticmethod
    def check_chain_type(llm, question):
        """
        질문을 분석서 질문의 타입을 반환해주는 정적 메소드이다.
        :param llm: 선언 LLM 모델
        :param question: 사용자의 질문 입력값
        :return: graph | db | docs | llm
        """
        # Question 분석 찾기
        question_prompt = ChatPromptTemplate.from_template(
            """ 질문을 분석해서 graphDB(neo4j) 쿼리 질문, postgresql 쿼리 질문, 일반 LLM 질문, 문서 질문으로 분류합니다.
                graph db(neo4j) 관련 질문이면 'graph',
                DB 관련 질문이면 'db',
                Url이 있고 문서에 관련된 질문이면 'docs',
                모두 아니면 'llm'을 반환합니다.
                Question: {input}"""
        )
        question_llm_chain = question_prompt | llm
        response = question_llm_chain.invoke({"input": question})
        return response.content

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
        return "문서를 찾을 수 없습니다."
