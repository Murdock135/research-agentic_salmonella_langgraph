# Usage

> **Prerequisites**
>  
> - Ensure a `config.toml` file exists in the `config` directory. See [Configuration](#configuration)
> - Ensure that you have the API keys for every provider defined within `config.toml`. See [Setting API keys](#setting-api-keys)

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

## Optional

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

# Setting API keys

You will need an API key for every provider defined in `config/config.toml`. The default configuration
only uses "google_genai" as the provider for all agents. So this particular configuration needs one API 
key; from google.

## Where does the code look for APIs?

First, it will look for API keys set within any `.env` file you create within this directory. Secondly,
it will look for them within `~/.secrets/.llm_apis` (On windows this will be `C:\Users\username\.secrets\.llm_apis`). If you don't have any of these two files, simply create a `.env` within this directory. 

> Note: `config/load_env.py` is responsible for looking for API keys