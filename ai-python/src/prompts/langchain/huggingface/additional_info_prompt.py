
brand_info_template = """  
Brand Info:-
    Brand Name:{name}
    ---------------------
    Brand Slogan/Tagline:{tagline}
    ---------------------    
    Brand Mission:{mission}
    ---------------------
    Brand Values:{values}
    ---------------------
    Target Audience:{audience}
    ---------------------
    Industry:{industry}
"""

company_info_template = """
Company Info:-
    Company Name:{name}
    ---------------------
    Company Slogan/Tagline:{tagline}
    ---------------------
    Company Overview:{overview}
    ---------------------
    Company Mission:{mission}
    ---------------------
    Company Values:{values}
    ---------------------
    Company Vision:{vision}
    ---------------------   
    Industry:{industry}
    ---------------------
    Headquarters:{headquarter}
"""

product_info_template = """
Product Info:-
    Product Name:{name}
    ---------------------
    Product Description:{description}
    ---------------------
    Product Category:{category}
    ---------------------
    Unique Selling Proposition (USP):{usp}
    ---------------------
    Target Market:{market}
    ---------------------
    Product Specifications:{specification}
    ---------------------
    Product Benefits:{benifits}
    --------------------- 
    Product Usage:{usage}
    ---------------------
    SKUS:{skus}
"""

prompt_mapper = {
    'productInfo':product_info_template,
    'brandInfo':brand_info_template,
    'companyInfo':company_info_template,
}
