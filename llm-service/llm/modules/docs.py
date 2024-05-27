from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
import pandas as pd


class DoscModule:
    @classmethod
    def docsChain(cls, llm, file):

        # 입력 검증
        error_response = validate_inputs(file)
        if error_response:
            return error_response

        # 파일 읽기
        df, error_response = read_file(file)
        if error_response:
            return error_response

        # 에이전트 객체 생성
        agent = create_pandas_dataframe_agent(llm, df)

        return agent


def validate_inputs(file):
    if not file:
        return "No file provided"

    return None


def read_file(file):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        df = pd.read_excel(file)
    else:
        return None, "Unsupported file type"

    if df.empty:
        return None, "The file is empty"

    return df, None

