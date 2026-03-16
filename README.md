Daily learning...

# IA Generativa Pipeline ETL Python

Project developed at the Santander 2023 Bootcamp - Data Science with Python, under the guidance of specialist [Venilton Falvo Jr](https://github.com/falvojr "Venilton Falvo Jr").
Building an ETL (Extraction, Transformation, and Loading) pipeline, demonstrating the relationship between data, Artificial Intelligence (AI), and APIs.

- **Extraction**: The adventure begins with a simple spreadsheet, from which we will extract user IDs. Then, we will use these IDs to access the 'Santander Dev Week 2023' API and obtain more detailed data, a process that highlights the versatility in data collection in Data Science.

- **Transformation**: We will enter the world of AI with OpenAI's GPT-4, transforming this data into personalized marketing messages. We will see how AI can be used in an innovative and practical way!

- **Loading**: We will finalize the process by sending these messages back to the 'Santander Dev Week 2023' API.
This step illustrates how transformed data is reintegrated into systems, completing the cycle of an ETL pipeline.

## Adjusting the Extract Step

🟢 **Option 1: Simpler (Data Directly in Code)**  

Ideal if you want to focus exclusively on the logic and AI usage without relying on external files.

## Simulates data extraction (replacing the API GET)

```Markdown
users = [
    {'id': 1, 'name': 'Naruto', 'news': []},
    {'id': 2, 'name': 'Hinata', 'news': []}
]
```

🟡 **Option 2: More Complete (Reading from File)**  

You can adapt the file SDW2023.csv, including the name column, and use it as a data source.

```Markdonw
import pandas as pd
```

<!--Reads the CSV and converts it into a list of dictionaries-->
users = pd.read_csv('SDW2023.csv').to_dict(orient='records')

<!--Ensures the expected structure for the Transformation step-->
```Markdonw
for user in users:
    user['news'] = []
```

**And the Load Step?**

Since the API is unavailable, the PUT call will not work. To finish the Lab, simply save the result locally (in a CSV, JSON file, or even print it to the console).

The most important thing is to demonstrate that you understand how the data flows through all ETL stages, regardless of the tool or source used 😉

## Santander Dev Week 2023 (ETL with Python)

**Context**: You are a data scientist at Santander and have been tasked with engaging customers in a more personalized way. Your goal is to use the power of Generative AI to create personalized marketing messages that will be delivered to each customer.

**Problem Conditions:**

1. You received a simple spreadsheet in CSV format (SDW2023.csv) with a list of bank user IDs:

```Markdown
UserID
1
2
3
4
5
```

2. Your job is to consume the endpoint GET [https://sdw-2023-prd.up.railway.app/users/{id}] (Santander Dev Week 2023 API) to obtain each customer’s data.

3. After retrieving the customer data, you will use the ChatGPT (OpenAI) API to generate a personalized marketing message for each customer. This message must emphasize the importance of investments.

4. Once the message for each customer is ready, you will send this information back to the API, updating the list of "news" for each user using the endpoint PUT [https://sdw-2023-prd.up.railway.app/users/{id}].

(You can use your own URL if you prefer 😉)  
API Repository: Santander Dev Week 2023 API

## Extract

Extract the list of user IDs from the CSV file. For each ID, make a GET request to obtain the corresponding user data.

```Markdonw
import pandas as pd

df = pd.read_csv('SDW2023.csv')
user_ids = df['UserID'].tolist()
print(user_ids)
```

```Markdown
import requests
import json

def get_user(id):
    response = requests.get(f'{sdw2023_api_url}/users/{id}')
    return response.json() if response.status_code == 200 else None

users = [user for id in user_ids if (user := get_user(id)) is not None]
print(json.dumps(users, indent=2))
```

```Markdown
[
  {
    "id": 4,
    "name": "Pyterson",
    "account": {
      "id": 7,
      "number": "00001-1",
      "agency": "0001",
      "balance": 0.0,
      "limit": 500.0
    },
    "card": {
      "id": 4,
      "number": "**** **** **** 1111",
      "limit": 1000.0
    },
    "features": [],
    "news": [
      {
        "id": 9,
        "icon": "https://digitalinnovationone.github.io/santander-dev-week-2023-api/icons/credit.svg",
        "description": "Pyterson, invest today to secure a safe and prosperous future. Your future will thank you!"
      }
    ]
  },
  {
    "id": 5,
    "name": "Pip",
    "account": {
      "id": 8,
      "number": "00002-2",
      "agency": "0001",
      "balance": 0.0,
      "limit": 500.0
    },
    "card": {
      "id": 5,
      "number": "**** **** **** 2222",
      "limit": 1000.0
    },
    "features": [],
    "news": [
      {
        "id": 10,
        "icon": "https://digitalinnovationone.github.io/santander-dev-week-2023-api/icons/credit.svg",
        "description": "Invest today for a safe and stable future, Pip. Your financial future depends on it!"
      }
    ]
  },
  {
    "id": 6,
    "name": "Pep",
    "account": {
      "id": 9,
      "number": "00003-3",
      "agency": "0001",
      "balance": 0.0,
      "limit": 500.0
    },
    "card": {
      "id": 6,
      "number": "**** **** **** 3333",
      "limit": 1000.0
    },
    "features": [],
    "news": [
      {
        "id": 11,
        "icon": "https://digitalinnovationone.github.io/santander-dev-week-2023-api/icons/credit.svg",
        "description": "Hi Pep, investing is the key to multiplying your money. Don't let your cash sit idle!"
      }
    ]
  }
]

```

## Transform

Use the OpenAI GPT‑4 API to generate a personalized marketing message for each user.

```Markdown
!pip install openai
```

```Markdown
import openai

openai.api_key = 'YOUR_API_KEY'

def generate_ai_news(user):
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a banking marketing specialist."},
            {"role": "user", "content": f"Create a message for {user['name']} about the importance of investments (max 100 characters)"}
        ]
    )
    return completion.choices[0].message.content.strip('"')

for user in users:
    news = generate_ai_news(user)
    print(news)
    user['news'].append({
        "icon": "https://digitalinnovationone.github.io/santander-dev-week-2023-api/icons/credit.svg",
        "description": news
    })
```

Pyterson, invest to make your money grow. Your financial future depends on it!
Pip, investing is the way to multiply your money. Let's strengthen your financial future!
Pep, investments are the key to your financial future. Grow your money, don't just save it!

## Load

Update each user’s "news" list in the API with the newly generated message.

```Markdown
def update_user(user):
    response = requests.put(f"{sdw2023_api_url}/users/{user['id']}", json=user)
    return True if response.status_code == 200 else False

for user in users:
    success = update_user(user)
    print(f"User {user['name']} updated? {success}!")
```

User Pyterson updated? True!
User Pip updated? True!
User Pep updated? True!

**[LICENSE](/LICENSE)**

See **[original repository](https://github.com/falvojr/santander-dev-week-2023)**
