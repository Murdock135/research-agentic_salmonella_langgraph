This project uses AWS Bedrock models. In order to run SPARQ, you will need AWS API keys. 

# Prerequisites

- Install AWS CLI (see https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started-api.html)

# Important commands

For first time setup:
```bash
aws configure sso
aws sts get-caller-identity --profile <aws_profile>
```

Then to login after token expiration:
```bash
aws sso login --profile <aws_profile>
```
