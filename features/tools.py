from langchain.tools import Tool
from faq import execute_chain
from suggestion import chatbot_response
from order_managment import chatbot_response_managment


# Define FAQ tool
faq_tool = Tool(
    name="FAQTool",
    func=execute_chain,
    description="Provides detailed answers to frequently asked questions about the e-commerce platform. "
                "This includes essential topics like shipping options, return policies, payment methods, account management, "
                "product categories, promotional offers, and customer support information. "
                "Input should be a specific question or topic you want information about, and the tool will retrieve "
                "accurate and concise answers tailored to the query."
)


# Define Suggestion tool
suggestion_tool = Tool(
    name="ProductSuggestionTool",
    func=chatbot_response,
    description="Provides product suggestions based on user preferences. "
                "Provides product information such as reviews and specific details based on user preferences"
                "Input should be the user query for product suggestions and product information nquiry."
)

order_managment_tool = Tool(
    name="OrderManagmenTool",
    func=chatbot_response_managment,
    description="Provides order status updates based on the order ID and customer name provided by the user."
                "Processes order cancellation requests, verifying eligibility and guiding the user through the process."
)



