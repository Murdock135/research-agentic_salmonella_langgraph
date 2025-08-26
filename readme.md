# Setup

> **Recommendation**
> I highly recommend using a UNIX based OS or VM to run this project. If you're on windows, install [WSL (Windows Subsystem for linux)](https://learn.microsoft.com/en-us/windows/wsl/install) and run it in there (I recommend Ubuntu).

1. Clone this repo with git or download as a zip file and then extract it.
2. In your terminal, 'cd' into the project folder.
3. Install python 3.13.3 if you haven't already.
4. Create a virtual environment with your preferred *virtual environment manager* (python, pyenv, conda, etc.). For example, with python you can use the following code in your terminal (make sure you 'cd' into the project folder.)

```
python3 -m venv .venv 
```

Explanation: '-m' is a flag and tells python to run the 'venv' script (came with the python installation) as a module. The module needs your preferred name for the virtual environment as a parameter. Here, we're using the name '.venv'

3. Activate the virtual environment. If you used python to create the virtual environent like in the previous step, you can use,

```
source .venv/bin/activate
```

4. Install packages with

```
pip install -r requirements.txt
```

# Get access to the data
Go to https://huggingface.co/zayanhugsAI, click on the relevant datasets and request access. The datasets used in this project are - 
    
1. Pulsenet
2. National Outbreak Reporting System (NORS)
3. Social Vulnerability Index (SVI)
4. Map The Meal Gap
5. Census Population

# Usage

> **Prerequisites**
> - Ensure you have python 3.13.3 installed.
> - Ensure a `config.toml` file exists in the `config` directory. See [Configuration](#configuration)
> - Ensure that you have the API keys for every provider defined within `config.toml`. See [Setting API keys](#setting-api-keys)
> - Ensure you have access to the [data](https://huggingface.co/zayanhugsAI).

First download the data using the following command.

```
python -m utils.download_data
```

Then, run the agentic system using a test query already defined (in `config/config.toml`) using

```
python -m core.main -t
```

If you want to use your own query, simply use

```
python -m core.main
```

If you have tracing enabled (see [enable tracing](#enable-tracing-optional)), you will see the trace of the system in your langsmith account.

## Enable tracing (Optional)

If you want to enable tracing using langsmith, create an account in [langsmith](https://www.langchain.com/langsmith), obtain an API key and do the following-

- Set the API key. See [Setting API keys](#setting-api-keys).
- In your `.env` file within this directory, add the following,

```
LANGSMITH_TRACING=True
LANGSMITH_PROJECT=<your_project_name>
```

# Configuration

2 things can be configured via the `config/config.toml` file: (1) The 'test query' and (2) The models used in the agentic system.

The default configuration is as follows.
```
test_query = "What are the main factors contributing to salmonella rates in Missouri in a statistical sense?"

[router]
model = "gemini-2.0-flash"
provider = "google_genai"

[explorer]
model = "gemini-2.0-flash"
provider = "google_genai"

[analyzer]
model = "gemini-2.0-flash"
provider = "google_genai"

[planner]
model = "gemini-2.0-flash"
provider = "google_genai"

[executor]
model = "gemini-2.0-flash"
provider = "google_genai"

[aggregator]
model = "gemini-2.0-flash"
provider = "google_genai"
```

If you want to use models from other providers, you will need to (1) Get the API keys from the respective providers and set them (See [Setting API keys](#setting-api-keys)) (2) Set the `model` and `provider` keys as per your preference in `config/config.toml`.

# Setting API keys

You will need an API key for every provider defined in `config/config.toml`. The default configuration
only uses "google_genai" as the provider for all agents. So this particular configuration needs one API 
key; from google.

## Where to put your API keys?

I recommend putting your llm-provider-specific API keys in `~/.secrets/.llm_apis` (On windows this will be `C:\Users\username\.secrets\.llm_apis`). You could also simply create a `.env` file within the project directory and put the API keys in there.

Example:

```
GOOGLE_GENAI_API_KEY=<YOUR KEY HERE>
OPENAI_API_KEY=<YOUR KEY HERE>
```


> If you want to inspect the related code, `config/load_env.py` is responsible for looking for API keys

# FAQ

1. Does this download any models to my computer?

    No

2. What is langgraph, langsmith?

    Langgraph is a python library for creating a system of multiple language models. Imagine each node of a graph as a language model (although that does not need to be the case, it is easy to imagine so). Langgraph has helpful code to build such a system.

    Langsmith is a platform where the 'trace' or step-by-step log of the system can be inspected. Here, you can observe what each language model is generating.
