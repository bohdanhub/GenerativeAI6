import boto3
import json

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    s3 = boto3.client('s3')
    bucket_name = 'bkukl-ai-task6'
    
    # 1. Overall size of unattached disk volumes
    unattached_volumes = ec2.describe_volumes(
        Filters=[
            {
                'Name': 'status',
                'Values': ['available']
            }
        ]
    )['Volumes']
    total_size_unattached_volumes = sum([vol['Size'] for vol in unattached_volumes])
    num_unattached_volumes = len(unattached_volumes)

    # 2. Overall size of not encrypted disk volumes
    not_encrypted_volumes = ec2.describe_volumes(
        Filters=[
            {
                'Name': 'status',
                'Values': ['in-use']
            },
            {
                'Name': 'encrypted',
                'Values': ['false']
            }
        ]
    )['Volumes']
    total_size_encrypted_volumes = sum([vol['Size'] for vol in not_encrypted_volumes])
    num_not_encrypted_volumes = len(not_encrypted_volumes)
    

    # 3. Not encrypted snapshots
    not_encrypted_snapshots = ec2.describe_snapshots(
        Filters=[
            {
                'Name': 'encrypted',
                'Values': ['false']
            }
        ],
        OwnerIds=['self']
    )['Snapshots']
    total_size_not_encrypted_snapshots = sum([snap['VolumeSize'] for snap in not_encrypted_snapshots])
    num_not_encrypted_snapshots = len(not_encrypted_snapshots)

    results = {
        'total_size_unattached_volumes': total_size_unattached_volumes,
        'total_size_encrypted_volumes': total_size_encrypted_volumes,
        'total_size_not_encrypted_snapshots': total_size_not_encrypted_snapshots,
        'total_num_unattached_volumes': num_unattached_volumes,
        'total_num_not_encrypted_volumes': num_not_encrypted_volumes,
        'total_num_not_encrypted_snapshots': num_not_encrypted_snapshots
    }
    
    # Store results to S3
    s3.put_object(
        Bucket=bucket_name,
        Key='ec2_metrics.json',
        Body=json.dumps(results),
        ContentType='application/json'
    )

    return results
