import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

from botocore.config import Config

def lambda_handler(event, context):
    sender_email_address = 'notificationsvctest@gmail.com'
    
    aws_region_name = "us-east-2"
  
    email_subject = "Assignment Added"
    confg = Config(retries={'max_attempts': 0}, read_timeout=900)
    verifiedemails= getVerifiedEmails(aws_region_name,confg)
    print("=====Verfied users=====")
    print(verifiedemails)
    db_users_address = getusersFromDB()
    print("======Database Users=======")
    print(db_users_address)
    receiver_email_address = verified_users_only(db_users_address,verifiedemails)
    unverifiedusers=unverified_users(db_users_address,verifiedemails)
    print("======Final Users=======")
    print(receiver_email_address)
    print("Unverified_users")
    print(unverifiedusers)
    
    
    #create_table_with_gsi()
    #create_user()
    #getusersFromDB()
  
    html_body = ("<html>"
        "<body>"
        "<p>Hello Student</p>"
        "<br>"
        "<p>New Assignment is added. Please check.</p>"
        "</body>"
        "</html>")
  
    charset = "UTF-8"
    ses_resource = boto3.client('ses', region_name = aws_region_name, config=confg)
  
    try:
        response = ses_resource.send_email(
                Destination = {
                    'ToAddresses': receiver_email_address
                },
                Message = {
                    'Body': {
                        'Html': {
                            'Charset': charset,
                            'Data': html_body,
                        },
                    },
                    'Subject': {
                        'Charset': charset,
                        'Data': email_subject,
                    },
                },
                Source = sender_email_address,
            )
  
    except ClientError as e:
        print(e)
        print("Email Delivery Failed! ", e.response['Error']['Message'])
    else:
        print("Email successfully sent to email address!")
        
def getusersFromDB():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('notifusers')
    response=table.scan()
    items =response['Items']
    users_emails=[]
    for item in items:
        users_emails.append(item['email'])
    print(users_emails)
    return users_emails;

def getVerifiedEmails(aws_region_name,confg):
    ses_resource = boto3.client('ses', region_name = aws_region_name, config=confg)
    response= ses_resource.list_verified_email_addresses()
    verified_emails=response['VerifiedEmailAddresses']
    return verified_emails;
    
def verified_users_only(dbusers,verifiedusers):
    return [element for element in dbusers if element in verifiedusers]

def unverified_users(dbusers,verifiedusers):
    lis=[]
    for ele in dbusers:
        if ele not in verifiedusers:
            lis.append(ele)
    return lis
    
        
    