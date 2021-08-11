import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tbp.v20190627 import tbp_client, models
try:
    cred = credential.Credential("SecretId", "SecretKey")
    httpProfile = HttpProfile()
    httpProfile.endpoint = "tbp.tencentcloudapi.com"

    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = tbp_client.TbpClient(cred, "", clientProfile)

    req = models.TextProcessRequest()
    params = {

    }
    req.from_json_string(json.dumps(params))

    resp = client.TextProcess(req)
    print(resp.to_json_string())

except TencentCloudSDKException as err:
    print(err)
