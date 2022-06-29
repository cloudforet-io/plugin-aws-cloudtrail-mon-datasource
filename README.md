# plugin-aws-cloudtrail-mon-datasource

![AWS Cloud Services](https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/aws-cloudtrail.svg)
**Plugin to collect AWS Cloudtrail log data**

> SpaceONE's [plugin-aws-cloudtrail-mon-datasource](https://github.com/spaceone-dev/plugin-aws-cloudtrail-mon-datasource) is a convenient tool to get Cloudtrail log data from AWS.


Find us also at [Dockerhub](https://hub.docker.com/repository/docker/spaceone/plugin-aws-cloudtrail-mon-datasource)
> Latest stable version : 1.1.0

Please contact us if you need any further information. (<support@spaceone.dev>)

---

## AWS Service Endpoint (in use)

 There is an endpoints used to collect AWS resources information.
AWS endpoint is a URL consisting of a region and a service code. 
<pre>
https://cloudtrail.[region-code].amazonaws.com
</pre>

We use a lots of endpoints because we collect information from many regions.  


---
## Authentication Overview

Registered service account on SpaceONE must have certain permissions to collect cloud service data Please, set
authentication privilege for followings:

<pre>
<code>
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "cloudtrail:LookupEvents"
            ],
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}
</code>
</pre>


---

# Release Note

## Version 1.1.0
  * Overall structural improvement