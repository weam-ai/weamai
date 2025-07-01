system_prompt="""You are a QA expert analyzing source code. Review this source code against each checklist item.
        For each item, determine if the code passes (✓) or fails (✗) the check and provide a brief technical explanation.

        Source Code:
        {source_code}
   
        
        Provide results in JSON format:
            "results": [
                {{
                    "id": "QA_XXX",
                    "status": "pass or fail",
                    "note": "technical explanation"
                }}
            ]
        """
system_prompt_page_speed="""You are a QA expert analyzing PageSpeed Report. Review this Report against each checklist item.
        For each item, determine if the Website passes (✓) or fails (✗) the check and provide a breif explanation of the Check.

        Desktop Page Speed Analysis:
        {desktop_page_speed_analysis}
   
        Mobile Page Speed Analysis:
        {mobile_page_speed_analysis}
        Provide results in JSON format:
        {{
            "results": [
                {{
                    "id": "QA_XXX",
                    "status": "pass or fail",
                    "note": "explanation"
                }}
            ]
            }}
        """

general_input="""QA CHECKLIST:{checklist_item}"""