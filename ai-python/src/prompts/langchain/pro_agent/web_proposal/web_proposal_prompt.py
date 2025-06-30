system_proposal_prompt ="""You are an expert proposal writer.Your response must be a valid JSON object without any additional text or explanation.Do not include any markdown formatting or code block syntax."""

general_proposal_input="""Create a project proposal with the following details:  
                - Client Name: {client_name}  
                - Project Name: {project_name}  
                - Project Description: {project_description}  

                ### Instructions:  
                - **Strictly use** the project description to determine the time and cost estimates.  
                - Ensure the timeline is realistic for the project's actual complexity.  
                - Accurately calculate costs based on the described work without unnecessary inflation.  
                - Avoid generic estimations—derive values directly from the project scope.  

                Return only a JSON object with the following structure:  

                {{
                    "project_overview": {{
                        "clientName": "{client_name}",
                        "projectName": "{project_name}",
                        "project_description": "{project_description}",
                        "totalTime": "Provide an accurate duration based only on the {project_description}. Example: A simple 5-page website should take 3-6 weeks, while a complex e-commerce platform may take 3-6 months."
                    }},
                    "timeline": {{
                        "research": "Determine a research timeline based on the actual project scope.",
                        "presentWireframes": "Calculate wireframe time according to project size and requirements.",
                        "presentFinishedMockups": "Estimate mockup completion time specific to the design complexity.",
                        "cssTemplates": "Provide realistic front-end styling completion time.",
                        "backend": "Set backend development time based only on described features.",
                        "qaTesting": "Estimate testing phase length relevant to the project scale.",
                        "deployment": "Define deployment duration tailored to project needs."
                    }},
                    "core_budget": {{
                        "researchCost": number,  # Changed from integer to number for float support
                        "designCost": number,
                        "frontEndCost": number,
                        "backEndCost": number,
                        "qaTestingCost": number,
                        "totalCoreCost": number  # This will be auto-calculated
                    }},
                    "recommended_addons": {{
                        "userTestingCost": number,
                        "maintenanceCost": number,
                        "totalRecommandedCost": number  # This will be auto-calculated
                    }}
                }}  

                Ensure the time and budget are **strictly derived from the project description** without arbitrary values or inflated estimates."""


general_requirements_input = """
Create a summary of the project requirements for {project_name} based on the following project description: {project_description}.  

                The response must be in JSON format with the following key-value structure:  

                {{
                    "projectSummary": "Clearly define the main goal of the project, emphasizing what the company wants to achieve and how it benefits users. Example: You wants to turn your highly popular online vegan restaurant guide into a web-based mobile app so that diners-on-the-go can find what they want to eat, where they want to eat it, and how much they're going to pay for it, faster than you can say organic kale salad.",

                    "userExperience": "Highlight the user experience expectations, including performance, responsiveness, and compatibility across devices. Example: The user experience must be seamless; high-performing, fast, and responsive whether it's being viewed on iOS, Android, Blackberry, Windows Phone, or any other type of mobile device.",

                    "designDevelopment": "Explain how the solution will be designed and developed, focusing on technology, user needs, and branding. Example: We'll design and develop a powerful universal HTML5 mobile app that will anticipate and respond to user needs and expectations, provide a smooth navigational experience, and appropriately reflect your brand in look and feel."
                }}  

                Ensure the JSON output is properly formatted and accurately reflects the project details."""

general_company_summary_prompt="""You are a helpful assistant that generates concise company summaries."""

general_company_summary_input="""Based on the following website analysis, provide a 140 to 160 word summary of the company in two paragraph. 
    Focus on their main business, products/services, and value proposition: {page_analysis}.
    summary format should be 'Here at company name, it wouldn't be overstating the case to say we’re ape for apps. We love how the rise of the app and the ubiquity of mobile devices is empowering users with information while providing a new platform for businesses to engage customers. Our designers and developers are experts in user experience, mobile engagement, and HTML5. We develop apps that users can’t live without for innovative companies who understand they can’t live without mobile.'"""