# Usage

> **Prerequisites**
>  
> - Ensure a `config.toml` file exists in the `config` directory. See [Configuration](#configuration)
> - Ensure that you have the API keys for every provider defined within `config.toml`

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