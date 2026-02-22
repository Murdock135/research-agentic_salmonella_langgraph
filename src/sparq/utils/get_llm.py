import os


def _make_native(model: str, provider: str):
    from langchain.chat_models import init_chat_model
    return init_chat_model(model=model, model_provider=provider)


def _make_openrouter(model: str, provider: str):
    from langchain_openai import ChatOpenAI

    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found")

    base_url = os.getenv('OPENROUTER_BASE_URL')
    if not base_url:
        raise ValueError("OPENROUTER_BASE_URL not found")

    return ChatOpenAI(
        openai_api_key=api_key,
        openai_api_base=base_url,
        model_name=model or "meta-llama/llama-4-maverick:free",
    )

def _make_bedrock(model: str, provider: str):
    from langchain_aws import ChatBedrock
    import boto3

    region = os.getenv('AWS_DEFAULT_REGION')
    if not region:
        raise ValueError("AWS_DEFAULT_REGION not found")

    profile = os.getenv('AWS_PROFILE')
    session = boto3.Session(profile_name=profile, region_name=region)
    client = session.client(service_name='bedrock-runtime')

    try:
        return ChatBedrock(model=model, client=client)
    except Exception as e:
        raise ValueError(f"Error initializing AWS Bedrock model {model}:\n{e}")


_PROVIDER_FACTORIES = {
    'openai':       _make_native,
    'google_genai': _make_native,
    'openrouter':   _make_openrouter,
    'aws_bedrock':  _make_bedrock,
}


def get_llm(model: str = 'gpt-4o', provider: str = 'openai'):
    factory = _PROVIDER_FACTORIES.get(provider)
    if factory is None:
        supported = ', '.join(f"'{p}'" for p in _PROVIDER_FACTORIES)
        raise ValueError(f"Provider '{provider}' not supported. Choose from: {supported}.")
    return factory(model, provider)