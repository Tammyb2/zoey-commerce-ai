from app.agents.sales_agent import run_sales_agent


result = run_sales_agent(
    customer_phone="+2348012345678",
    message="Hello",
)

print(result)