from src.celery_service.celery_worker import celery_app
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from src.crypto_hub.services.openai.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from sklearn.metrics.pairwise import cosine_similarity
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from src.celery_service.openai.config import PROMPT
from src.chatflow_langchain.service.config.model_config_openai import DefaultGPT4oMiniModelRepository
from src.logger.default_logger import logger
from fastapi import status, HTTPException
import xlrd

# Initialize Celery
class CSVHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.dfs = {}
        self.current_sheet = None
        self.file_type = None

    def preprocess_sheet(self, df):
        """
        Preprocess a dataframe to clean and prepare it for analysis.
        
        Args:
            df (pandas.DataFrame): The dataframe to preprocess
            
        Returns:
            pandas.DataFrame: The preprocessed dataframe
        """
        # Remove completely empty rows
        df = df[~df.apply(lambda row: all(pd.isna(val) or str(val).strip() == '' for val in row), axis=1)]
        
        # Remove columns where more than 50% of the values are empty
        cols_to_keep_final = [
            col for col in df.columns
            if self.count_valid(df[col]) > self.count_invalid(df[col])
        ]

        df = df[cols_to_keep_final]
        
        # Remove rows until a valid header is found
        while len(df) > 0:
            if any(str(col).startswith('Unnamed') or str(col).isspace() or str(col) == '' for col in df.columns):
                new_columns = [
                    f'Unnamed: {i}' if pd.isna(val) or str(val).isspace() or str(val) == '' else str(val).strip()
                    for i, val in enumerate(df.iloc[0])
                ]
                df.columns = new_columns
                df = df.iloc[1:].reset_index(drop=True)
            else:
                break
        
        # Remove rows where all values are the same as the column names
        df = df[~df.apply(lambda row: all(str(row[col]).strip() == str(col).strip() for col in df.columns), axis=1)]
        
        return df

    def count_valid(self, col):
        """
        Count valid (non-empty) values in a column.
        
        Args:
            col (pandas.Series): The column to check
            
        Returns:
            int: Count of valid values
        """
        return col.apply(lambda x: pd.notna(x) and str(x).strip() != '').sum()

    def count_invalid(self, col):
        """
        Count invalid (empty) values in a column.
        
        Args:
            col (pandas.Series): The column to check
            
        Returns:
            int: Count of invalid values
        """
        return col.apply(lambda x: pd.isna(x) or str(x).strip() == '').sum()

    def load_and_preprocess_data(self):
        """
        Load and preprocess data from the file path.
        
        Returns:
            pandas.DataFrame: The current dataframe after loading
        """
        if self.file_path.endswith('.csv'):
            self.file_type = 'csv'
            df = pd.read_csv(self.file_path,encoding_errors="ignore")
            self.dfs['default'] = self.preprocess_sheet(df)
            self.current_sheet = 'default'
        elif self.file_path.endswith(('.xls', '.xlsx')):
            if(self.file_path.endswith('.xls')):
                xlrd.__version__ = '2.0.1'  # Ensure xlrd version is compatible with .xls files
            self.file_type = 'excel'
            excel_file = pd.ExcelFile(self.file_path)
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(self.file_path, sheet_name=sheet_name)
                processed_df = self.preprocess_sheet(df)
                if not processed_df.empty:
                    self.dfs[sheet_name] = processed_df
            if self.dfs:
                self.current_sheet = next(iter(self.dfs))
            else:
                raise ValueError("No valid data found in any sheet")
        elif self.file_path.endswith('.json'):
            self.file_type = 'json'
            df = pd.read_json(self.file_path)
            self.dfs['default'] = self.preprocess_sheet(df)
            self.current_sheet = 'default'
        else:
            raise ValueError("Unsupported file type. Only CSV, XLS, and XLSX files are supported.")
        return self.get_current_df()

    def get_current_df(self):
        """
        Get the current dataframe.
        
        Returns:
            pandas.DataFrame: The current dataframe
        """
        if not self.dfs:
            raise ValueError("No data loaded. Call load_and_preprocess_data first.")
        return self.dfs[self.current_sheet]

    def list_sheets(self):
        """
        List all available sheets.
        
        Returns:
            list: List of sheet names
        """
        return list(self.dfs.keys())

    def switch_sheet(self, sheet_name):
        """
        Switch to a different sheet.
        
        Args:
            sheet_name (str): The name of the sheet to switch to
            
        Returns:
            pandas.DataFrame: The dataframe for the selected sheet
        """
        if sheet_name not in self.dfs:
            raise ValueError(f"Sheet '{sheet_name}' not found. Available sheets: {self.list_sheets()}")
        self.current_sheet = sheet_name
        return self.get_current_df()

    def calculate_sheet_relevance(self, query, sheet_name):
        """
        Calculate the relevance of a sheet to a query.
        
        Args:
            query (str): The query to check relevance against
            sheet_name (str): The name of the sheet to check
            
        Returns:
            float: Relevance score
        """
        df = self.dfs[sheet_name]
        headers = ' '.join(df.columns.astype(str))
        sample_data = ' '.join(df.head(10).astype(str).values.flatten())
        sheet_name_text = sheet_name.replace("_", " ").replace("-", " ")
        # Give more weight to headers and sheet name
        text = (sheet_name_text + " ") * 3 + (headers + " ") * 2 + sample_data
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        try:
            tfidf_matrix = vectorizer.fit_transform([text, query])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            # Also boost score if query words appear in sheet name
            if any(word in sheet_name_text.lower() for word in query.lower().split()):
                similarity += 0.15
            return similarity
        except Exception:
            return 0

    def find_most_relevant_sheet(self, query):
        """
        Find the most relevant sheet for a query.
        
        Args:
            query (str): The query to find the most relevant sheet for
            
        Returns:
            str: The name of the most relevant sheet
        """
        if len(self.dfs) == 1:
            return next(iter(self.dfs))
        relevance_scores = {
            sheet: self.calculate_sheet_relevance(query, sheet)
            for sheet in self.dfs.keys()
        }
        most_relevant_sheet = max(relevance_scores.items(), key=lambda x: x[1])
        return most_relevant_sheet[0]

    def find_most_relevant_sheets(self, query, top_n=3):
        """
        Find the most relevant sheets for a query.
        
        Args:
            query (str): The query to find relevant sheets for
            top_n (int): Number of top sheets to return
            
        Returns:
            list: List of the most relevant sheet names
        """
        if len(self.dfs) == 1:
            return [next(iter(self.dfs))]
        relevance_scores = {
            sheet: self.calculate_sheet_relevance(query, sheet)
            for sheet in self.dfs.keys()
        }
        sorted_sheets = sorted(relevance_scores.items(), key=lambda x: x[1], reverse=True)
        return [sheet for sheet, _ in sorted_sheets[:top_n]]

class AgentManager:
    def __init__(self, df, company_id=None, companymodel=None):
        """
        Initialize the agent manager.
        
        Args:
            llm: The language model to use
            df (pandas.DataFrame): The dataframe to analyze
        """
        self.df = df
        self.agent = None
        self.llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
        self.company_id = company_id
        self.companymodel = companymodel

    def initialize_llm(self):
        """
        Initializes the LLM with the specified API key and company model.

        Parameters
        ----------
        api_key_id : str, optional
            The API key ID used for decryption and initialization.
        companymodel : str, optional
            The company model configuration for the LLM.

        Exceptions
        ----------
        Logs an error if the initialization fails.
        """
        try:
            default_api_key = DefaultGPT4oMiniModelRepository(company_id=self.company_id,companymodel=self.companymodel).get_default_model_key()
            self.llm_apikey_decrypt_service.initialization(default_api_key, self.companymodel)
            self.model_name =self.llm_apikey_decrypt_service.model_name
            self.bot_data = self.llm_apikey_decrypt_service.bot_data
            self.api_key = self.llm_apikey_decrypt_service.decrypt()

            self.llm = ChatOpenAI(model= self.model_name,
                temperature=0,
                verbose=False,
                api_key=self.api_key,
                stream_usage=True)

        except Exception as e:
            logger.error(
                f"Failed to initialize LLM: {e}",
                extra={"tags": {"method": "AgentManager.initialize_llm"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize LLM: {e}")
        
    def create_agent(self):
        """
        Create a pandas dataframe agent.
        """
        prefix = PROMPT.PREFIX.format(
            df_shape=self.df.shape,
            columns=self.df.columns.to_list(),
            total_rows=len(self.df)
        )

        suffix = PROMPT.SUFFIX

        self.agent = create_pandas_dataframe_agent(
            llm=self.llm,
            df=self.df,
            agent_type="tool-calling",
            verbose=False,
            early_stopping_method="generate",
            allow_dangerous_code=True,
        )

    def run_agent(self, query):
        """
        Run the agent with a query.
        
        Args:
            query (str): The query to run
            
        Returns:
            str: The agent's response
        """
        if not self.agent:
            raise ValueError("Agent not initialized. Call create_agent first.")
        res = self.agent.invoke({"input": query})
        return res["output"] if "output" in res else "No response generated"

# Celery Task from main()
@celery_app.task(bind=True, retry_kwargs={'max_retries': 0, 'countdown': 0}, queue="excel_agent")
def run_excel_query(self, file_path: str, query: str, company_id: str = None, companymodel: str = None):
    csv_handler = CSVHandler(file_path)
    try:
        df = csv_handler.load_and_preprocess_data()
    except Exception as e:
        return {"error": f"Error loading data: {str(e)}"}

    agent_manager = AgentManager(df=df, company_id=company_id, companymodel=companymodel)
    agent_manager.initialize_llm()
    agent_manager.create_agent()

    try:
        relevant_sheets = csv_handler.find_most_relevant_sheets(query, top_n=len(csv_handler.dfs))
        last_error = None

        for sheet in relevant_sheets:
            if sheet != csv_handler.current_sheet:
                df = csv_handler.switch_sheet(sheet)
                agent_manager = AgentManager(df=df, company_id=company_id, companymodel=companymodel)
                agent_manager.initialize_llm()
                agent_manager.create_agent()

            try:
                response = agent_manager.run_agent(query)
                if (
                    response
                    and "error" not in response.lower()
                    and "not found" not in response.lower()
                    and "no relevant" not in response.lower()
                ):
                    return {
                        "response": response,
                        "used_sheet": sheet
                    }
                else:
                    last_error = response
            except Exception as e:
                last_error = str(e)
                continue

        return {
            "response": "No valid answer found in any relevant sheet.",
            "last_error": last_error
        }

    except Exception as e:
        return {"error": str(e)}
