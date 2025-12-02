This project uses AWS Bedrock models. In order to run SPARQ, you will need AWS API keys. 

# Prerequisites

- Install AWS CLI (see https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started-api.html)

# Important commands

```bash
aws configure sso
aws sts get-caller-identity --profile <aws_profile>
```
