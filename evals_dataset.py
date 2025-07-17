import csv

data = [
    {
        "Input": "Call me Chinonso",
        "Output": "Welcome, Chinonso! Please provide your income, savings goal (as a number or percentage, e.g., '40%'), and preferred currency (e.g., NGN or USD) to set up your budget."
    },
    {
        "Input": "My income is 500,000 NGN, savings goal is 20%, currency is NGN",
        "Output": "Budget set! Income: 500,000 NGN, Savings Goal: 100,000 NGN (20%), Currency: NGN. Your budget for expenses is 400,000 NGN. Want to log any expenses or set specific goals?"
    },
    {
        "Input": "Log an expense of 50,000 NGN for groceries",
        "Output": "Expense logged: 50,000 NGN for groceries. Remaining budget: 350,000 NGN. Anything else you'd like to log or review?"
    },
    {
        "Input": "Do you love me?",
        "Output": "I am Aza man, here to help with your budget and expenses. Let's focus on your financial goals—how can I assist you?"
    },
    {
        "Input": "Add 30,000 NGN to savings",
        "Output": "Added 30,000 NGN to savings. Current savings: 30,000 NGN (30% of 100,000 NGN goal). Remaining budget: 350,000 NGN. Anything else?"
    }
]

csv_file = "data/finance_eval_dataset.csv"
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=["Input", "Output"])
    writer.writeheader()
    for row in data:
        writer.writerow(row)
print(f"CSV file '{csv_file}' has been generated successfully.")
