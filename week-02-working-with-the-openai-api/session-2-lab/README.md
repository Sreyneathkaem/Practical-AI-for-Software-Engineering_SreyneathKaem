# Configurable Text Assistant — Lab 2

Practical AI for Software Engineering · Week 2 · Lab 2

A command-line assistant built on the Chat Completions API. Its persona,
temperature, output length, and streaming behaviour are all configurable, and
it handles API failures gracefully instead of crashing.

> This is a **reference implementation**. If you are a student, your task is to
> build the equivalent yourself starting from your Lab 1 AskBot — use this only
> the way your instructor tells you to.

## Project layout

```
askbot/
├── main.py            # CLI, input/output loop, interactive commands
├── llm.py             # LLM service wrapper (errors, retries, usage)
├── config.py          # defaults + personas
├── requirements.txt   # dependencies
├── .env.example       # template for your key (copy to .env)
├── .gitignore         # ignores .env, .venv, __pycache__
└── README.md          # this file
```

The flow of control is a straight line:
`main.py → conversation logic → LLM service (llm.py) → OpenAI API`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\activate           # Windows

pip install -r requirements.txt

cp .env.example .env               # then edit .env and add your real key
```

Set the model name in `config.py` (`DEFAULT_MODEL`) to whatever your course
environment provides, or export `OPENAI_MODEL`.

## Running

```bash
python main.py
python main.py --persona tutor
python main.py --persona reviewer --temperature 0.2
python main.py --persona tutor --temperature 0.4 --max-tokens 500 --stream
```

### Flags

| Flag            | Default | Description                          |
| --------------- | ------- | ------------------------------------ |
| `--persona`     | default | tutor · reviewer · interviewer       |
| `--temperature` | 0.7     | 0.0 (focused) → 2.0 (varied)         |
| `--max-tokens`  | 500     | maximum length of the reply          |
| `--model`       | YOUR_MODEL | override the model name           |
| `--stream`      | off     | show the reply progressively         |

### Interactive commands

```
/help        /persona <name>     /temperature <value>
/tokens <n>  /usage              /clear            /save <file>
/load <file> /quit
```

## How the requirements map to the code

| Req | Where |
| --- | ----- |
| R1  API integration   | `llm.py` → `LLMService.ask` / `stream` |
| R2  Persona           | `config.py` personas + `--persona`     |
| R3  Temperature       | `--temperature`, `/temperature`        |
| R4  Output limit      | `--max-tokens`, `/tokens`              |
| R5  Conversation memory | `main.py` → `Session.messages`       |
| R6  Error handling    | `llm.py` error classes + friendly messages |
| R7  Token tracking    | `llm.py` → `Usage`, printed each turn  |
| R8  Streaming         | `llm.py` → `stream`, `--stream`        |
| R9  Security          | `.env` + `.gitignore`, no key in source |
| R10 Documentation     | this README                            |

## Stretch goals (optional)

Finished early, or want more of a challenge? Pick one of these. Each pushes past
what Lab 1 covered and touches a different part of the design.

### S1 — Handle "context too long" as its own error

**Goal:** teach the assistant to recognise when a request is too large for the
model and tell the user what to do about it, instead of showing a generic error.

**Why it matters:** not every failure is the same. A too long request will fail
again no matter how many times you retry, so it is a terminal error, and the
user needs a different message from "the service is busy".

**What to build:**

1. In `llm.py`, add a `ContextLengthError` (a terminal error, like `InvalidRequestError`) with a `user_message` that suggests clearing history or lowering `--max-tokens`.
2. Extend `_classify_error()` so a context length failure maps to it. Match on the class name and on message text such as "context length" or "maximum context".
3. Make sure the retry loop treats it as terminal, so it is never retried.
4. In `main.py`, when this error is raised, roll back the unanswered user message the same way other errors do.

**Done when:** sending a very long prompt (paste a large block of text, or set a
tiny model context) prints your friendly message once, with no retries, and the
conversation history stays clean.

### S2 — Save and restore a conversation

**Goal:** add `/save <file>` and `/load <file>` commands so a chat can be kept
between runs.

**Why it matters:** the conversation is just data, a list of role and content
messages. Once you see that, persisting it is a small step, and it makes the
memory idea from R5 concrete.

**What to build:**

1. In `main.py`, add `/save <file>` that writes `self.messages` to a JSON file.
2. Add `/load <file>` that reads the JSON back into `self.messages`, replacing the current history.
3. Validate the loaded file: it should be a list of dicts that each have a `role` and `content`. On a bad file, print a friendly message and keep the current conversation.
4. Update `/help` and the README command list to include the two new commands.

**Done when:** you can hold a short chat, run `/save chat.json`, quit, start a
fresh session, run `/load chat.json`, and the assistant answers the next
question with the earlier context in mind.

Add a short note in `NOTES.md` about which stretch goal you did and what you
learned from it.

## Reflection questions

_Answer these here as part of your submission._

1. **What happens when temperature is changed from 0.2 to 1.0?**

      To understand what happens when the temperature is changed from 0.2 to 1.0, we need to consider the context in which this temperature change is occurring. 

      1. **Context**: Is this change happening in a physical system, like a material or a gas, or is it related to a computational model or algorithm, such as simulated annealing? The impact of the temperature change would be vastly different depending on the context.

      2. **Physical System**: If we're talking about a physical system, changing the temperature from 0.2 to 1.0 (assuming these are in degrees Celsius or another temperature scale) could mean a variety of things. For instance, if we're discussing a phase transition, this change might not significantly affect the state of the material (e.g., from solid to liquid) unless it crosses a specific threshold (like the freezing or boiling point of a substance).

      3. **Computational Model or Algorithm**: In the context of computational models, especially those involving optimization techniques like simulated annealing, temperature is often a metaphorical concept used to control the exploration-exploitation trade-off. A lower temperature (like 0.2) might mean the algorithm is less likely to accept worse solutions, focusing more on exploitation (fine-tuning current solutions), whereas a higher temperature (like 1.0) increases the likelihood of accepting worse solutions, encouraging more exploration of the solution space.

      Without more specific details about the context or the system in question, it's challenging to provide a precise explanation of the effects of changing the temperature from 0.2 to 1.0. Could you provide more context or clarify in which domain this question is being asked?

2. **Why should an application not retry every API error?**
  **Reasons to Avoid Retrying Every API Error**:

    1. **Resource Exhaustion**: Retrying every API error can lead to resource exhaustion, both on the client-side and server-side. If an API is experiencing issues, repeatedly retrying requests can overwhelm the server, exacerbating the problem.

    2. **Increased Latency**: Excessive retries can introduce significant latency, affecting the overall performance of your application. Users may experience delays or timeouts, leading to a poor user experience.

    3. **Server-Side Consequences**: Some API errors, such as those related to rate limiting or quota exhaustion, may be triggered by excessive requests. Retrying these errors can lead to further restrictions or even account suspension.

    4. **Idempotence**: Not all API operations are idempotent, meaning that retrying a failed request can have unintended consequences, such as duplicate resource creation or incorrect data updates.

    5. **Error Types**: Different types of API errors require distinct handling strategies. For example:
            * **Transient errors** (e.g., network issues, server overload): Retrying these errors may be beneficial.
            * **Permanent errors** (e.g., invalid requests, authentication issues): Retrying these errors is unlikely to succeed and may waste resources.
            * **Rate limiting errors**: Retrying these errors can lead to further restrictions.

    6. **Backoff Strategies**: Blindly retrying API errors without a backoff strategy can lead to a "thundering herd" problem, where multiple clients retry requests simultaneously, overwhelming the server.

  **Best Practices for Retrying API Errors**:

    1. **Implement a backoff strategy**: Use exponential backoff or a similar strategy to gradually increase the delay between retries.
    2. **Limit the number of retries**: Set a reasonable limit on the number of retries to prevent resource exhaustion and avoid overwhelming the server.
    3. **Handle errors based on type**: Develop a strategy to handle different types of API errors, such as retrying transient errors while avoiding permanent errors.
    4. **Monitor and analyze errors**: Regularly monitor and analyze API errors to identify patterns and optimize your retry strategy.
    5. **Implement circuit breakers**: Use circuit breakers to detect when an API is experiencing issues and prevent further requests until the issue is resolved.

    By adopting a thoughtful approach to retrying API errors, you can minimize the negative consequences and improve the overall resilience of your application.

3. **Why should the API key not be stored directly in the source code?**

      **Security Risks**: Storing an API key directly in the source code poses significant security risks. Here are some reasons why it's not recommended:

      1. **Exposure to Unauthorized Access**: When you store an API key in your source code, it becomes accessible to anyone who has access to your code. This could include other developers working on the project, contributors, or even users if the code is open-sourced.

      2. **Version Control Systems**: If you're using a version control system like Git, your API key could be exposed in the commit history, even if you try to remove it later. This is because Git keeps a record of all changes made to the code, including previous versions that may contain the API key.

      3. **Public Exposure**: If your code is open-sourced or accidentally pushed to a public repository, your API key becomes publicly available. This could lead to unauthorized use of your API, potentially resulting in abuse, data breaches, or financial losses.

      4. **Limited Control**: Once your API key is exposed, you have limited control over how it's used. You may not be able to track or restrict access to your API, making it difficult to prevent misuse.

      5. **Security Best Practices**: Storing sensitive information like API keys in source code goes against security best practices. It's essential to keep sensitive data separate from your code to minimize the risk of exposure.

      **Alternatives**: Instead of storing API keys directly in your source code, consider the following alternatives:

      1. **Environment Variables**: Store API keys as environment variables. This way, you can keep them separate from your code and manage access to them more securely.

      2. **Secure Configuration Files**: Use secure configuration files that are not committed to version control. These files can store sensitive information like API keys, and you can restrict access to them.

      3. **Secret Management Services**: Utilize secret management services like HashiCorp's Vault or AWS Secrets Manager to securely store and manage yourAPI keys.

      4. **API Key Management**: Implement API key management practices, such as rotating API keys regularly, limiting their scope, and monitoring their usage.

      By following these best practices, you can minimize the risks associated with storing API keys and protect your sensitive information.

4. **Why does conversation history increase token usage?**

    **Conversation History and Token Usage**: In many AI models, conversation history refers to the context or the previous messages exchanged between the user and the model. This history is used to inform and improve the model's responses.

    **Why Conversation History Increases Token Usage**:

    1. **Contextual Understanding**: To understand the conversation history, the model needs to process and analyze the previous messages. This requires additional computational resources and, consequently, more tokens.
    2. **Increased Input Size**: As the conversation history grows, the input size for the model increases. This means the model needs to process more text, which requires more tokens to generate a response.
    3. **Memory and Attention Mechanisms**: Many AI models use memory and attention mechanisms to store and retrieve information from the conversation history. These mechanisms require additional tokens to function effectively.
    4. **Complexity of Responses**: As the conversation history becomes more complex, the model may need to generate more nuanced and context-dependent responses. This can lead to longer and more detailed responses, which require more tokens.

    **Token Usage and Conversation History**: The relationship between conversation history and token usage is often non-linear. As the conversation history grows, the token usage may increase exponentially. This is because the model needs to process and analyze the entire conversation history to generate a response.

    **Optimizing Token Usage**: To optimize token usage, it's essential to consider the following strategies:

    1. **Limit Conversation History**: Limiting the conversation history can help reduce token usage. This can be achieved by setting a maximum conversation length or by using techniques like summarization or pruning.
    2. **Use Efficient Models**: Using efficient models that are designed to handle conversation history can help reduce token usage. These models often use techniques like caching, pruning, or attention mechanisms to optimize performance.
    3. **Optimize Input Size**: Optimizing the input size by removing unnecessary information or using techniques like input pruning can help reduce token usage.

    By understanding the relationship between conversation history and token usage, you can optimize your AI model's performance and reduce costs.

5. **What is the main advantage of streaming?**

    **Main Advantage of Streaming**: The main advantage of streaming is that it allows for **real-time or near-real-time processing and analysis of data**. This enables applications to respond quickly to changing conditions, make timely decisions, and provide up-to-date information.

    **Key Benefits of Streaming**:

    1. **Low Latency**: Streaming enables data to be processed and analyzed in real-time, reducing latency and allowing for faster decision-making.
    2. **Improved Responsiveness**: Streaming allows applications to respond quickly to changing conditions, such as changes in user behavior or market trends.
    3. **Increased Efficiency**: Streaming can help reduce the need for batch processing and storage, making it a more efficient way to handle large amounts of data.
    4. **Enhanced Scalability**: Streaming architectures can be designed to scale horizontally, making it easier to handle large volumes of data and high traffic.
    5. **Better Data Utilization**: Streaming enables organizations to make the most of their data, by processing and analyzing it in real-time, rather than storing it for later use.

    **Use Cases for Streaming**:

    1. **Real-time Analytics**: Streaming is used in real-time analytics to analyze and process large amounts of data from various sources, such as social media, sensors, or applications.
    2. **IoT Applications**: Streaming is used in IoT applications to process and analyze data from devices, such as sensors, cameras, or other IoT devices.
    3. **Financial Services**: Streaming is used in financial services to analyze and process large amounts of financial data, such as stock prices, trading volumes, or market trends.
    4. **Gaming**: Streaming is used in gaming to provide real-time updates, such as player positions, scores, or game state.
    5. **Video and Audio Processing**: Streaming is used in video and audio processing to process and analyze large amounts of multimedia data, such as video or audio streams.

    Overall, the main advantage of streaming is its ability to enable real-time processing and analysis of data, which has numerous benefits and use cases across various industries.

6. **If 10,000 users use your application, what engineering problems might appear?**

    **Engineering Problems with 10,000 Users**:

    As the user base grows to 10,000, several engineering problems may arise:

    1. **Scalability Issues**:
            * Increased load on servers, databases, and networks.
            * Potential bottlenecks in application performance, leading to slow response times or errors.
    2. **Database Performance**:
            * Higher query volumes, leading to slower query execution times.
            * Increased disk I/O, potentially causing disk space and performance issues.
    3. **Network and Infrastructure**:
            * Increased network traffic, potentially leading to congestion, packet loss, or latency.
            * Higher demand on infrastructure resources, such as CPU, memory, and storage.
    4. **Cache and Session Management**:
            * Increased cache misses, leading to slower performance and higher latency.
            * Session management challenges, such as handling concurrent user sessions and maintaining session state.
    5. **Error Handling and Logging**:
            * Increased error rates, making it challenging to identify and debug issues.
            * Larger log volumes, requiring more efficient log management and analysis.
    6. **Security and Authentication**:
            * Higher risk of security breaches, such as brute-force attacks or unauthorized access.
            * Increased authentication and authorization requests, potentially leading to performance issues.
    7. **Content Delivery and Storage**:
            * Higher demand for content, such as images, videos, or files, leading to storage and bandwidth issues.
            * Potential for content delivery network (CDN) bottlenecks or caching issues.
    8. **Queue and Job Processing**:
            * Increased job volumes, leading to longer queue times and potential job failures.
            * Higher demand on worker nodes, potentially causing performance issues or node failures.
    9. **Monitoring and Alerting**:
            * Increased noise in monitoring systems, making it challenging to identify critical issues.
            * Higher risk of false positives or false negatives, leading to unnecessary alerts or missed critical issues.
    10. **Team and Process Challenges**:
            * Increased complexity in team communication, collaboration, and decision-making.
            * Higher demand on engineering resources, potentially leading to burnout or decreased productivity.

    **Solutions to These Problems**:

    1. **Horizontal Scaling**: Add more servers, nodes, or instances to distribute the load.
    2. **Caching and Content Delivery Networks (CDNs)**: Implement caching mechanisms and CDNs to reduce the load on origin servers.
    3. **Database Optimization**: Optimize