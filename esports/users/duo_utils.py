import duo_client

def send_duo_push_async(username, ikey, skey, host):
    try:
        auth_client = duo_client.Auth(
            ikey=ikey,
            skey=skey,
            host=host
        )

        pre_auth = auth_client.preauth(username=username)
        if pre_auth['result'] != 'auth':
            return None, pre_auth['status_msg']

        auth = auth_client.auth(factor='push', username=username, device='auto', async_txn=True)
        txid = auth.get('txid')

        if not txid:
            return None, "Failed to generate Duo transaction ID"

        return txid, "Push sent"
    except Exception as e:
        return None, str(e)


