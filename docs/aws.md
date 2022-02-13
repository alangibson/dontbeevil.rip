
# Setup

- Allocate Elastic IP address
  https://console.aws.amazon.com/vpc/home?region=us-east-1#AllocateAddress:

- Create VPC with Public and Private Subnets
  https://console.aws.amazon.com/vpc/home?region=us-east-1#wizardSelector:
  VPC name: search-vpc
  public subnet name: search-public-subnet
  private subnet name: search-private-subnet
  Subnets must be in different AZs!

- Create EC2 Target Group
  https://console.aws.amazon.com/ec2/home?region=us-east-1#CreateTargetGroup:
  target type: instances
  target group name: search-elasticsearch-tg
  vpc: search-vpc
  port: http 9200
  next: Add an Application Load Balancer later

- Create Network Load Balancer
  https://console.aws.amazon.com/ec2/home?region=us-east-1#CreateALBWizard:
  name: search-elasticsearch-nlb
  scheme: internal
  vpc: search-vpc
  mappings: (check one)
  subnet: search-private-subnet

- Create EC2 instance for ES
  https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#LaunchInstanceWizard:
  network: search-vpc
  subnet: search-private-subnet
  hostname type: resource name
  Assign a security group: Create a new security group
  Security group name: search-sg
  rules:
    - ssh
    - http
    - https
  name: search-es-master-1

- Create EC2 instance for processor
  image: t2.micro
  network: search-vpc
  subnet: search-public-subnet
  Auto-assign Public IP: enable
  Hostname type: resource name
  security group: search-sg
  name: search-processor

- Create API GW VPC link
  https://console.aws.amazon.com/apigateway/main/vpc-links/create?region=us-east-1
  Choose a VPC link version: VPC link for REST APIs
  name: search-vpc-link
  target nlb: search-elasticsearch-nlb