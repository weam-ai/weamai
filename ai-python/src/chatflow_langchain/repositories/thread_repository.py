from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from src.db.config import db_instance
from src.logger.default_logger import logger
from src.chat.repositories.thread_abstract_repository import ThreadAbstractRepository
from src.chatflow_langchain.repositories.openai_error_messages_config import OPENAI_MESSAGES_CONFIG,HF_ERROR_MESSAGES_CONFIG,GENAI_ERROR_MESSAGES_CONFIG,ANTHROPIC_ERROR_MESSAGES_CONFIG, WEAM_ROUTER_MESSAGES_CONFIG

class ThreadRepostiory(ThreadAbstractRepository):
    """Repository for managing threads in a database."""
    def __init__(self):
        """
        Initialize the repository.

        Args:
            db_instance: An instance of the database.
        """
        self.db_instance = db_instance

    def initialization_thread_id(self, thread_id: str, collection_name: str):
        """
        Initializes the repository with a thread ID and a collection name, and sets up a default token dictionary.

            thread_id (str): The unique identifier for the thread.
            collection_name (str): The name of the database collection to associate with the thread.

        Attributes:
            thread_id (str): Stores the provided thread ID.
            instance: The database collection instance retrieved using the collection name.
            default_token_dict (dict): A dictionary containing default token-related values:
                - "totalCost" (str): The total cost initialized to "$0.000".
                - "promptT" (int): The prompt token count initialized to 0.
                - "completion" (int): The completion token count initialized to 0.
                - "totalUsed" (int): The total token usage initialized to 0.

        """
        self.thread_id = thread_id
        self.instance = self.db_instance.get_collection(collection_name)
        self.result=self._safe_fetch_thread_data()
        self.default_token_dict={"totalCost":"$0.000","promptT":0,"completion":0,"totalUsed":0}

    def initialization(self, thread_id: str, collection_name: str):
        """
        Initialize the repository with thread ID and collection name.

        Args:
            thread_id (str): The ID of the thread.
            collection_name (str): The name of the collection.
        """
        self.thread_id = thread_id
        self.instance = self.db_instance.get_collection(collection_name)
        self.result = self._fetch_thread_model_data()
        self.default_token_dict={"totalCost":"$0.000","promptT":0,"completion":0,"totalUsed":0}
        

    def _fetch_thread_model_data(self):
        """Fetch data related to the thread model."""
        query = {'_id': ObjectId(self.thread_id)}
        try:
            result = self.instance.find_one(query)
            if not result:
                raise ValueError(f"No data found for thread id: {self.thread_id}")
            logger.info(
                "Successfully accessing the database",
                extra={"tags": {
                    "method": "ThreadRepostiory._fetch_thread_model_data",
                    "api_id": self.thread_id
                }}
            )
            return result
        except PyMongoError as e:
            logger.error(
                f"An error occurred while accessing the database: {e}",
                extra={"tags": {
                    "method": "ThreadRepostiory._fetch_thread_model_data",
                    "thread_id": self.thread_id
                }}
            )

    def _safe_fetch_thread_data(self):
        """Fetch data related to the thread model."""
        query = {'_id': ObjectId(self.thread_id)}
        try:
            result = self.instance.find_one(query)
            if result is None:
                result={}
            logger.info(
                "Successfully accessing the database",
                extra={"tags": {
                    "method": "ThreadRepostiory._fetch_thread_model_data",
                    "api_id": self.thread_id
                }}
            )
            return result
        except PyMongoError as e:
            logger.error(
                f"An error occurred while accessing the database: {e}",
                extra={"tags": {
                    "method": "ThreadRepostiory._fetch_thread_model_data",
                    "thread_id": self.thread_id
                }}
            )

    def update_fields(self, data):
        """
        Update fields of the thread model.

        Args:
            data (dict): Data to update.
        """
        query = {'_id': ObjectId(self.thread_id)}
        try:
            self.instance.update_one(query, data)
        except PyMongoError as e:
            logger.error(
                f"An error occurred while updating the collection fields: {e}",
                extra={"tags": {
                    "method": "ThreadRepostiory.update_fields",
                    "thread_id": self.thread_id
                }}
            )

    def update_token_fields(self, token_data):
        """
        Update token fields of the thread model.

        Args:
            token_data (dict): Token data to update.
        """
        query = {'_id': ObjectId(self.thread_id)}
        try:
            self.instance.update_one(query, token_data)
        except PyMongoError as e:
            logger.error(
                f"An error occurred while updating the token fields: {e}",
                extra={"tags": {
                    "method": "ThreadRepostiory.update_token_fields",
                    "thread_id": self.thread_id
                }}
            )

    def update_system(self, system):
        """
        Update the system field of the thread model.

        Args:
            system: The system to update.
        """
        query = {'_id': ObjectId(self.thread_id)}
        data = {
            "$set": {
                "system": system
            }
        }
        try:
            self.instance.update_one(query, data)
        except PyMongoError as e:
            logger.error(
                f"An error occurred while updating the system field: {e}",
                extra={"tags": {
                    "method": "ThreadRepostiory.update_system",
                    "thread_id": self.thread_id
                }}
            )

    def update_sumhistory_checkpoint(self, sumhistory_checkpoint):
        """
        Update the sumhistory_checkpoint field of the thread model.

        Args:
            sumhistory_checkpoint: The sumhistory_checkpoint to update.
        """
        query = {'_id': ObjectId(self.thread_id)}
        data = {
            "$set": {
                "sumhistory_checkpoint": sumhistory_checkpoint
            }
        }
        try:
            self.instance.update_one(query, data)
        except PyMongoError as e:
            logger.error(
                f"An error occurred while updating the system field: {e}",
                extra={"tags": {
                    "method": "ThreadRepostiory.update_sumhistory_checkpoint",
                    "thread_id": self.thread_id
                }}
            )

    def overwrite_token_usage(self,cb):
        """
        Overwrites the token usage data in the repository.

        Parameters
        ----------
        cb : Callback
            The callback object containing token usage information.
        """
        token_data = {
            "$set": {
                "tokens.totalUsed": cb.total_tokens,
                "tokens.promptT": cb.prompt_tokens,
                "tokens.completion": cb.completion_tokens,
                "tokens.totalCost": f"${cb.total_cost}"
            }
        }
        self.update_token_fields(token_data)

    def token_usage_dict(self,token_usage:dict):
        """
        Creates a token usage dictionary.

        Parameters
        ----------
        token_usage : dict
            A dictionary containing token usage information.

        Returns
        -------
        dict
            A dictionary with token usage data.
        """
        token_data =  {
            "$set": {
                "tokens.totalUsed": token_usage['total_tokens'],
                "tokens.promptT": token_usage['prompt_tokens'],
                "tokens.completion": token_usage['completion_tokens'],
                "tokens.totalCost": f"${token_usage['total_cost']}"
            }
        }
        self.update_token_fields(token_data)

        
    def update_token_usage(self, cb, tokens_old=None):
        """
        Updates the token usage data in the repository.

        Parameters
        ----------
        cb : Callback
            The callback object containing token usage information.
        tokens_old : dict
            The old token usage data.
        """
        if tokens_old is None:
            tokens_old=self.result.get('tokens',self.default_token_dict)
            if 'totalCost' not in tokens_old:
                tokens_old = self.default_token_dict
        
        total_old_cost = float(tokens_old['totalCost'].replace("$", ""))
        total_new_cost = total_old_cost + cb.total_cost

        token_data = {
            "$set": {
                "tokens.totalUsed": tokens_old['totalUsed'] + cb.total_tokens,
                "tokens.promptT": tokens_old['promptT'] + cb.prompt_tokens,
                "tokens.completion": tokens_old['completion'] + cb.completion_tokens,
                "tokens.totalCost": f"${total_new_cost}"
            }
        }
        self.update_token_fields(token_data)

    def update_tools_token_data(self,token_data,tokens_old=None,additional_data:dict=None):
        if tokens_old is None:
            tokens_old=self.result.get('tokens',self.default_token_dict)
            if 'totalCost' not in tokens_old:
                tokens_old = self.default_token_dict

        total_old_cost = float(tokens_old['totalCost'].replace("$", ""))
        total_web_cost = float(tokens_old.get('webCost',"0").replace("$", ""))
        total_web_cost = total_web_cost + additional_data.get('webCost',0)
        total_new_cost = total_old_cost + token_data['totalCost']
        token_usage_dict = {
                "tokens.totalUsed": tokens_old['totalUsed'] + token_data["totalUsed"],
                "tokens.promptT": tokens_old['promptT'] + token_data["promptT"],
                "tokens.completion": tokens_old['completion'] + token_data["completion"],
                "tokens.totalCost": f"${total_new_cost}",
                "tokens.imageT": tokens_old.get('imageT',0) + additional_data['imageT'],
                "tokens.webCost": f"${total_web_cost}",
                "isMedia":additional_data['isMedia']
            }
        token_data = {
            "$set": token_usage_dict    
        }
        self.update_token_fields(token_data)

    def update_token_usage_summary(self, cb, tokens_old=None):
        """
        Updates the token usage data in the repository.

        Parameters
        ----------
        cb : Callback
            The callback object containing token usage information.
        tokens_old : dict
            The old token usage data.
        """
        

        token_data = {
            "$set": {
                "tokens.summary.totalUsed":cb.total_tokens,
                "tokens.summary.promptT": cb.prompt_tokens,
                "tokens.summary.completion": cb.completion_tokens,
                "tokens.summary.totalCost": f"${cb.total_cost}"
            }
        }
        self.update_token_fields(token_data)
    


    def update_cache_token_usage(self, cache_tokens_dict:dict,tokens_old=None):
        """
        Updates the token usage data in the repository.

        Parameters
        ----------
        cache_tokens_dict : dict
            A dictionary containing cache token usage information.
        Notes
        -----
        This method updates the cache token usage fields in the database. If `tokens_old` is not provided,
        it defaults to the current token data in the result or the default token dictionary.
        """
        if tokens_old is None:
            tokens_old = self.result.get('tokens', self.default_token_dict)
            if 'totalCost' not in tokens_old.get('cache_tokens', {}):
                tokens_old['cache_tokens'] = self.default_token_dict.get('cache_tokens', {})

        # Parse old total cost
        total_old_cost = float(tokens_old.get('cache_tokens', {}).get('totalCost', "$0").replace("$", ""))
        total_new_cost = total_old_cost + cache_tokens_dict.get("cache_total_cost", 0)

        # Parse old prompt tokens
        old_prompt_tokens = tokens_old.get('cache_tokens', {}).get('promptT', 0)
        new_prompt_tokens = old_prompt_tokens + cache_tokens_dict.get("cache_prompt_tokens", 0)

        # Update both total cost and prompt tokens
        token_data = {
            "$set": {
                "tokens.cache_tokens.totalCost": f"${total_new_cost}",
                "tokens.cache_tokens.promptT": new_prompt_tokens,
            }
        }

        self.update_token_fields(token_data)
   

    def update_img_gen_prompt(self,gen_prompt=''):
        img_gen_prompt={"$set":{"img_gen_prompt":gen_prompt}}
        self.update_fields(data=img_gen_prompt)

    def add_message_openai(self, error_code: str = "common_response") -> None:
        """
        Add an OpenAI-related message to the database based on the error code.

        Args:
            error_code (str): The code that determines which message to use.
        """
        message = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
        if 'ai' not in self.result:
            openai_message = {
                "$set": {
                    "openai_error": message
                }
            }
            self.update_fields(openai_message)

    def add_message_huggingface(self, error_code: str = "common_response") -> None:
        """
        Add an hugging face message to the database based on the error code.

        Args:
            error_code (str): The code that determines which message to use.
        """
        message = HF_ERROR_MESSAGES_CONFIG.get(error_code, HF_ERROR_MESSAGES_CONFIG.get("common_response"))
        if 'ai' not in self.result:
            openai_message = {
                "$set": {
                    "openai_error": message
                }
            }
            self.update_fields(openai_message)

    def add_message_gemini(self, error_code: str = "common_response") -> None:
        """
        Add an hugging face message to the database based on the error code.

        Args:
            error_code (str): The code that determines which message to use.
        """
        message = GENAI_ERROR_MESSAGES_CONFIG.get(error_code, GENAI_ERROR_MESSAGES_CONFIG.get("common_response"))
        if 'ai' not in self.result:
            openai_message = {
                "$set": {
                    "openai_error": message
                }
            }
            self.update_fields(openai_message)

    def add_message_anthropic(self, error_code: str = "common_response") -> None:
        """
        Add an hugging face message to the database based on the error code.

        Args:
            error_code (str): The code that determines which message to use.
        """
        message = ANTHROPIC_ERROR_MESSAGES_CONFIG.get(error_code, ANTHROPIC_ERROR_MESSAGES_CONFIG.get("common_response"))
        if 'ai' not in self.result:
            openai_message = {
                "$set": {
                    "openai_error": message
                }
            }
            self.update_fields(openai_message)

    def add_message_weam_router(self, error_code: str = "common_response") -> None:
        """
        Add an Weamrouter-related message to the database based on the error code.

        Args:
            error_code (str): The code that determines which message to use.
        """
        message = WEAM_ROUTER_MESSAGES_CONFIG.get(error_code, WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
        if 'ai' not in self.result:
            openai_message = {
                "$set": {
                    "openai_error": message
                }
            }
            self.update_fields(openai_message)
    
    def get_api_type(self):
        """
        Retrieves the type of API from the result.

        This method extracts the 'responseAPI' key from the 'result' dictionary
        and returns its corresponding value, which represents the type of API being used.

        Returns:
            str: The type of API as indicated by the 'responseAPI' value in the result dictionary.
        
        Raises:
            KeyError: If the 'responseAPI' key is not found in the result dictionary.

        Example:
            # Assuming self.result = {'responseAPI': 'REST'}
            api_type = self.get_api_type()
            print(api_type)  # Output: 'REST'
        """
        return self.result['responseAPI']
    
    def get_api_type(self):
        """
        Retrieves the type of API from the result.

        This method extracts the 'responseAPI' key from the 'result' dictionary
        and returns its corresponding value, which represents the type of API being used.

        Returns:
            str: The type of API as indicated by the 'responseAPI' value in the result dictionary.
        
        Raises:
            KeyError: If the 'responseAPI' key is not found in the result dictionary.

        Example:
            # Assuming self.result = {'responseAPI': 'REST'}
            api_type = self.get_api_type()
            print(api_type)  # Output: 'REST'
        """
        return self.result['responseAPI']
    
    def get_file_data(self):
        """
        Retrieves the file data from the object.

        This method accesses the 'cloneMedia' key in the current object (assumed to be a dictionary-like structure)
        and returns its corresponding value, which represents the file data.

        Returns:
            Any: The value associated with the 'cloneMedia' key, which can be of any data type.
        
        Raises:
            KeyError: If the 'cloneMedia' key is not found in the object.

   
        """
        
        return self.result['cloneMedia']
    
    def check_gpt_doc_exists(self):
      
        # Check if 'result' and 'cloneMedia' exist in self
        if 'cloneMedia' in self.result:
            # Check if '_id' exists and is not equal to 0
            if self.result['cloneMedia'].get('_id') != 0:
                return True
            else:
                return False
        else:
            return False
        
       

    
    def get_brain_data(self):
        """
        Retrieves the file data from the object.

        This method accesses the 'cloneMedia' key in the current object (assumed to be a dictionary-like structure)
        and returns its corresponding value, which represents the file data.

        Returns:
            Any: The value associated with the 'cloneMedia' key, which can be of any data type.
        
        Raises:
            KeyError: If the 'cloneMedia' key is not found in the object.

   
        """
        return self.result['brain']
    

    def get_custom_gpt_id(self):
        """
        Retrieves the file data from the object.

        This method accesses the 'cloneMedia' key in the current object (assumed to be a dictionary-like structure)
        and returns its corresponding value, which represents the file data.

        Returns:
            Any: The value associated with the 'cloneMedia' key, which can be of any data type.
        
        Raises:
            KeyError: If the 'cloneMedia' key is not found in the object.

   
        """
        return self.result['customGptId']

    def get_model_data(self, model_code):
        """
        Retrieves the model data from the object.

        Args:
            model_code (str): The code of the model to retrieve.

        Returns:
            dict: The model data associated with the given model code.
        
        Raises:
            ValueError: If no data is found for the given model code.
        """
        model_collection = self.db_instance.get_collection('model')
        query = {'code': model_code}
        projection = {'title': 1, '_id': 1, 'code': 1}
        try:
            model_data = model_collection.find_one(query, projection)
            if not model_data:
                raise ValueError(f"No data found for model code: {model_code}")
            return model_data
        except PyMongoError as e:
            logger.error(
                f"An error occurred while accessing the model data: {e}",
                extra={"tags": {
                    "method": "ThreadRepostiory.get_model_data",
                    "model_code": model_code
                }}
            )
            raise


    def update_response_model(self, responseModel,model_code):
        """
        Update the Response Model field of the thread model.

        Args:
            response model: The response model to update.
        """
        query = {'_id': ObjectId(self.thread_id)}
        model_data = self.get_model_data(model_code)
        data = {
            "$set": {
            "responseModel": responseModel,
            "model.title": model_data['title'],
            "model.id": model_data['_id'],
            "model.code": model_data['code']
            }
        }
        try:
            self.instance.update_one(query, data)
        except PyMongoError as e:
            logger.error(
                f"An error occurred while updating the Response Model field: {e}",
                extra={"tags": {
                    "method": "ThreadRepostiory.update_response_model",
                    "thread_id": self.thread_id
                }}
            )

    def update_credits(self,msgCredit):
        """
        Increment the usedCredit field of the thread model.

        Args:
            msgCredit: The credit to increment.
        """
        query = {'_id': ObjectId(self.thread_id)}
        data = {
            "$inc": {
            "usedCredit": msgCredit
            }
        }
        try:
            self.instance.update_one(query, data)
        except PyMongoError as e:
            logger.error(
            f"An error occurred while updating the usedCredit field: {e}",
            extra={"tags": {
                "method": "ThreadRepostiory.update_credits",
                "thread_id": self.thread_id
            }}
            )
    def update_fields_insert(self, data):
        """ 
        Updates or inserts fields in the thread model.

        This method updates the fields of a thread document in the database. If the document
        does not exist, it inserts a new one with the provided data.

        Args:
            data (dict): A dictionary containing the fields to update or insert.

        Raises:
            PyMongoError: If an error occurs during the update or insert operation.

        Logs:
            Logs an error message if the update or insert operation fails, including the
            method name and thread ID for debugging purposes.
        """

        
        query = {'_id': ObjectId(self.thread_id)}
        try:
            self.instance.update_one(query, data,upsert=True)
        except PyMongoError as e:
            logger.error(
                f"An error occurred while updating the collection fields: {e}",
                extra={"tags": {
                    "method": "ThreadRepostiory.update_fields",
                    "thread_id": self.thread_id
                }}
            )

    def get_agent_extra_info(self):
        """
        Fetches agent_extra_info from the result data.
    
        Returns:
            dict: Extracted agent_extra_info. If fields are missing, default values will be returned.
        """
        # Extract the proAgentData and step1 data from result
        pro_agent_data = self.result.get("proAgentData", {})
        chat_session_id=str(self.result.get("chat_session_id",None))
        brain_id=str(self.result.get("brain",{}).get("id",None))
        step1_data = pro_agent_data.get("step1", {})
        step3_data=pro_agent_data.get("step3",{})
    
        # Safely extract fields with default values if missing
        business_summary = step1_data.get("business_summary", "")  # Default to empty string
        target_audience = step1_data.get("target_audience", "")    # Default to empty string
        website_url = step1_data.get("website", "")               # Default to empty string
        target_keywords = step1_data.get("target_keywords", [])   # Default to empty list
        primary_keywords=step3_data.get("primary_keywords",[])
        secondary_keywords=step3_data.get("secondary_keywords",[])

        location = step1_data.get("location", "")                # Default to empty string
        language = step1_data.get("language", "")              # Default to empty string
    
        # Construct the agent_extra_info dictionary with the extracted data
        agent_extra_info = {
            "business_summary": business_summary,
            "target_audience": target_audience,
            "website_url": website_url,
            "target_keywords": target_keywords,
            "primary_keywords":primary_keywords,
            "secondary_keywords":secondary_keywords,
            "chat_session_id":chat_session_id,
            "brain_id":brain_id,
            "location": location,
            "language": language
        }
    
        return agent_extra_info
