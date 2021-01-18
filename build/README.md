# Build Set up

### Set up permissions


- Set up fraud detector data access role [cfn_fraud_detector_role.json](cfn_fraud_detector_role.json)
- Set up code build role [cfn_train_deploy_role.json](cfn_train_deploy_role.json)

For multi account with shared bucket 

- Make sure that u deploy bucket policy [build/cfn_fd_crossaccount_bucket_policy.json](build/cfn_fd_crossaccount_bucket_policy.json), ,in the account that owns the bucket 