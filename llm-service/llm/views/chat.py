# API에 대한 동작
import re

from llm.modules import graphDB, db, docs
from rest_framework.views import APIView
from llmapp.settings import LLM

from llmapp.response import auto_response
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain


class ChatAPIView(APIView):
    memory_dict = {}
    file_memory_dict = {}
    @auto_response
    def post(self, request):
        """
        Chat API

        :param request: { chat : "", file: "", thread_id: ""}
        :return: LLM 답변 문자열
        """
        if (LLM == None):
            return "현재 Chat 기능을 사용할 수 없습니다."

        question = request.data["chat"]
        file = None
        if "file" in request.data:
            file = request.data["file"]
        thread_id = request.data["thread_id"]

        if not thread_id:
            return "대화 내용이 없습니다."

        if thread_id not in self.memory_dict:
            self.memory_dict[thread_id] = ConversationBufferMemory(memory_key="history")
        thread_memory = self.memory_dict[thread_id]
        print("thread_memory", thread_memory)

        # 질문 확인
        if not question:
            return "질문을 입력해 주세요"

        # Question 분석 / 질문 타입 찾기
        question_type = self.check_chain_type(LLM, question)

        # 현재 파일에 대한 질문만 타입 변경
        if file or thread_id in self.file_memory_dict:
            question_type="docs"
        print("question_type = ", question_type)

        result = ""
        try:
            # type에 따른 분기
            if question_type == "graph":
                graphDB_chain = graphDB.GraphDBModule.graphChain(LLM, thread_memory)
                response = graphDB_chain.invoke(question)
                result = response["result"]

            elif question_type == "db":
                db_chain = db.BasicDBModule.dbChain(LLM, thread_memory)
                response = db_chain.invoke(question)
                result = response["result"]

            elif question_type == "llm":
                # Question 분석 찾기
                question_prompt = ChatPromptTemplate.from_template(
                    """ History : {history}
                        Question: {input}
                        AI:"""
                )
                llm_chain = ConversationChain(
                    llm=LLM,
                    memory=thread_memory,
                    prompt=question_prompt,
                    output_key="answer"
                )
                response = llm_chain.invoke(question)
                result = response["answer"]

            elif question_type == "docs":

                if thread_id not in self.file_memory_dict:
                    self.file_memory_dict[thread_id] = None
                file_memory = self.file_memory_dict[thread_id]
                url = None

                # file, file_memory가 없을때 URL 파싱
                if not file and not file_memory:
                    url = self.parse_url(LLM, question, thread_memory)

                file_memory = self.update_file_memory(thread_id, file_memory, file, url)
                dcos_chain = self.create_dcos_chain(LLM, file_memory, file, url)

                response = dcos_chain.invoke({'input': question, 'history': thread_memory.chat_memory.messages})
                result = response["answer"]

                thread_memory.save_context({"input": question}, {"response": result})

                # NOTE: ConversationalRetrievalChain 사용시 memory 속성값 작동이 잘 되지 않아 input 값으로 history 이전 내용을 넣어줌
                response = dcos_chain.invoke({'input': question, 'history': thread_memory.chat_memory.messages})
                result = response["answer"]
                # 메모리에 대화 내용 저장
                thread_memory.save_context({"input": question}, {"response": result})

        except Exception as e:
            # result = "정확한 답변을 찾을 수 없습니다."
            result = e
        print("response = ", result)

        return result

    def update_file_memory(self, thread_id, file_memory, file, url):
        # 현재 파일 메모리가 없고, file 또는 URL 데이터가 있을때 file_memory 저장
        if not file_memory and (file or url):
            if file:
                file_memory = {"type": "file", "data": file}
            elif url:
                file_memory = {"type": "url", "data": url}
            self.file_memory_dict[thread_id] = file_memory
        return file_memory

    def create_dcos_chain(self, LLM, file_memory, file, url):
        dcos_chain = None
        if file_memory["type"] == "file":
            data = file if file else file_memory["data"]
            dcos_chain = docs.DoscModule.docsChain(LLM, data)
            if file:
                data.close()
        elif file_memory["type"] == "url":
            data = url if url else file_memory["data"]
            dcos_chain = docs.DoscModule.urlChain(LLM, data)
        return dcos_chain
    @staticmethod
    def check_chain_type(llm, question):
        """
        질문을 분석해서 질문의 타입을 반환해주는 정적 메소드이다.

        :param llm: 선언된 LLM 모델
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
    def parse_url(llm, question, memory):
        """
        질문에서 URL을 파싱하기 위한 정적 메소드이다.
        NOTE: 일반 정규식 파싱으로 진행해였지만, Thread 내의 History를 확인하고 URL 파싱이 필요하기 때문에 LLM 조회를 통해 파싱 진행

        :param llm: 선언된 LLM
        :param memory: 저장된 Thread의 메모리
        :param question: 사용자의 질문 입력값
        :return: URL 문자열 또는 오류 문자열
        """


        # Question 분석 찾기
        question_prompt = ChatPromptTemplate.from_template(
            """ 질문에서 'URL' 형식만 추출해 URL만 문자열로 반환해야 합니다.
                URL이 존재하지 않으면 빈 문자열을 반환합니다.
                정규식 r"http[s]?://(?:[a-zA-Z]|[0-9]|[$\-@\.&+:/?=]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+" 이 형식을 따릅니다.
                History: {history}
                Question: {input}
                AI:"""
        )
        question_llm_chain = question_prompt | llm
        response = question_llm_chain.invoke({"input": question, "history": memory})

        return response.content
