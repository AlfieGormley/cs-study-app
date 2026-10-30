---
id: wm-sdn-vpc-addresses
title: AWS VPC subnets, addressing and routes
level: intermediate
minutes: 3
summary: An ordinary AWS IPv4 subnet reserves its first four addresses and last address; exceptions must be checked.
sourceLesson: wm-sdn
---

A cloud VPC is the software-defined network a tenant actually configures. Its address plan is hard to change later, and AWS's subnet rules differ slightly from textbook subnetting, so the planning decisions made on day one matter.

## A cloud VPC, piece by piece

An AWS VPC is a regional logical network supporting IPv4 and/or supported IPv6 configurations. The following describes a conventional private IPv4 example; other clouds have different scoping rules:

- **CIDR block**: e.g. `10.20.0.0/16`. Plan it so it does not overlap anything you may connect it to later (on-premises, other VPCs).
- **Subnets**: each lives in one availability zone. For an ordinary AWS private IPv4 subnet, the first four addresses and the last are reserved. These are offsets from the subnet base, not necessarily addresses ending .0–.3. The VPC DNS resolver is available at the primary VPC CIDR base plus two (and link-local addresses); each subnet’s base-plus-two is reserved, not necessarily its resolver endpoint. AWS does not support subnet broadcast. BYOIP has documented exceptions to the ordinary reservation rule.
- **Route tables**: a subnet is associated with one table, which can be shared by several subnets. A public IPv4 subnet has a direct Internet-gateway route; an instance also needs suitable public addressing, routes and filtering to communicate. Private subnets may use NAT, private connectivity or no Internet route. IPv6 outbound Internet access uses different mechanisms.
- **Security groups**: attached to instances or network interfaces.
- **Network ACLs**: attached to subnets.

```python
import ipaddress

vpc = ipaddress.ip_network("10.20.0.0/16")
# Divide the /16 into equal /20 blocks.
subnets = list(vpc.subnets(new_prefix=20))
# Pick three blocks; labels are
# illustrative.
for az, net in zip("abc", subnets):
    # Ordinary AWS IPv4 reserves five per
    # block.
    print(az, net, net.num_addresses - 5)
# a 10.20.0.0/20 4091
# b 10.20.16.0/20 4091
# c 10.20.32.0/20 4091
```

The arithmetic behind that output: each extra prefix bit halves a block, so a /20 has 4,096 addresses, and AWS keeps 5 of them in every ordinary subnet, leaving 4,091. A /16 holds sixteen /20s, so this plan leaves thirteen spare for private subnets and future growth.

Two practical consequences:

- **Small subnets lose proportionally more.** A /28 has 16 addresses but only 11 usable in AWS, so size subnets with the five reservations in mind.
- **Plan for growth and connection.** Resizing or renumbering a live subnet is painful, and overlapping ranges block later VPC peering, so allocate generous, non-overlapping blocks centrally from the start.

## Key takeaways
- An ordinary AWS IPv4 subnet reserves its first four addresses and last address; exceptions must be checked.
- A subnet’s route table, public addressing and filters all contribute to connectivity.

## Further reading
- [What is Amazon VPC? — AWS documentation](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)
- [Subnet CIDR blocks — AWS documentation](https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html)
