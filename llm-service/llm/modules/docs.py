import os
import tempfile
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import WebBaseLoader
from llmapp.settings import OPENAI_API_KEY
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains.combine_documents import create_stuff_documents_chain


class DoscModule:
    @classmethod
    def docsChain(cls, llm, file, memory):

        tmp_file_path = cls.read_file(file)

        # 문서 로드
        data = CSVLoader(file_path=tmp_file_path)
        docs = data.load()

        chain = cls.setup_retrieval_pipeline(llm, docs, memory)

        # 임시 파일 삭제
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

        return chain

    @classmethod
    def urlChain(cls, llm, url, memory):

        # 문서 로드
        data = WebBaseLoader(url)
        docs = data.load()

        chain = cls.setup_retrieval_pipeline(llm, docs, memory)

        return chain

    @staticmethod
    def read_file(file):
        if file.name.endswith('.csv'):
            # 임시 파일 생성 및 저장
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                for chunk in file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name

        return tmp_file_path

    @staticmethod
    def setup_retrieval_pipeline(llm, docs, memory):

        # OpenAI 임베딩 생성기 초기화
        embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=OPENAI_API_KEY)

        # 텍스트 분할
        text_splitter = RecursiveCharacterTextSplitter()
        documents = text_splitter.split_documents(docs)

        # 벡터스토어에 임베딩
        vector = FAISS.from_documents(documents, embeddings)

        # 프롬프트 지정
        prompt = ChatPromptTemplate.from_template(
            """
                기존에 알고 있었던 정보는 모두 잊어.
                주어진 정보를 참고 하여 답변을 해야해.
                주어진 정보를 참고 해도 알 수 없을 경우 항상 "제가 가진 정보로는 알 수 없습니다."로 응답 해줘.
                History: {history}
                Context: {context}
                Question: {input}
            """
        )

        retriever = vector.as_retriever()
        document_chain = create_stuff_documents_chain(llm=llm, prompt=prompt, memory=memory)
        chain = create_retrieval_chain(retriever, document_chain)

        return chain

