'''
# This script is intended to pull data from a google sheet that has 
# device mac addresses. If esports coaches have entered in their data
# correct this will add the device to the proper esports wireless or 
# wired MAB (MAC address bypass list) in ISE.
'''
import os, subprocess, json, csv, requests
from flask import current_app
from esports.models import Device
from datetime import datetime
from urllib.parse import quote


def Esports_ISE_MAB(output_file,timestamp):
    ## with open(output_file, 'r') as csv_file:
        ## csv_reader = csv.reader(csv_file)
    iseUser = current_app.config['ISE_API_USER']
    isePass = current_app.config['ISE_API_PASSWORD']
    iseBase = current_app.config['ISE_API_URL']
    csv_reader = output_file
    wired = current_app.config['ISE_WIRED']
    wireless = current_app.config['ISE_WIRELESS']
    iseCreds = iseUser + ':' + isePass
    iseAddEndpoint = "https://" + iseBase + ":443/api/v1/endpoint/"
    iseGetEnpoint = "https://" + iseBase + ":9060/ers/config/endpoint/name/"
    iseUpdateEndpoint = "https://" + iseBase + ":443/api/v1/endpoint/"
    message = []
    # Skip the header row
    ## next(csv_reader)
    # print (len(csv_reader))
    for row in csv_reader:
        # print (row)
        if row[3] != 'Device':
            continue
        else:
            # Checking to see if the device exists in ISE. If it does we are going to
            # update the divece to be in the proper MAB. 
            expected_status_code = '200'
            getEndpoint = subprocess.run(["curl", "--insecure", "--silent", "-o", "/dev/null", "-w", str("%{http_code}"), 
                            "--user", iseCreds,
                            "--header", "Accept: application/json",
                            iseGetEnpoint+row[7]], capture_output=True, text=True)
            
            # Does the Device exist: searching the name by mac (default for ise to add mac as device name)
            # print( getEndpoint.stdout.strip() )
            if getEndpoint.returncode == 0:
                actual_status_code = getEndpoint.stdout.strip()
                if actual_status_code == expected_status_code:
                    getEndpoint = subprocess.run(["curl", "--insecure", "--silent", 
                            "--user", iseCreds,
                            "--header", "Accept: application/json",
                            iseGetEnpoint+row[7]], capture_output=True, text=True)
                    result_getEndpoint = getEndpoint.stdout
                    iseEndpointID = json.loads(result_getEndpoint)['ERSEndPoint']['id']
                    # print(iseEndpointID)
                    if row[4] == 'Wi-Fi':
                        group = wireless
                    else:
                        group = wired
                    # Custom attributes have to be built in ISE before you can assign values to them. 
                    payload = {
                        "id" : iseEndpointID,
                        "name" : row[5],
                        "description" : row[2] + ' Esports device',
                        "mac" : row[7],
                        "groupId" : group,
                        "staticGroupAssignment" : True,
                        "customAttributes" : {
                                "deviceType" : row[8],
                                "school" : row[2],
                                "coachEmail" : row[1],
                                "created" : timestamp
                            }
                        }
                    json_payload = json.dumps(payload, indent=4)
                    
                    subprocess.run(["curl", "-X", "PUT", iseUpdateEndpoint+iseEndpointID, 
                                "--insecure", "--silent", "-o", "/dev/null", "-w", str("%{http_code}"),
                                "--user", iseCreds,
                                "--header", "Accept: application/json" ,
                                "--header", "Content-Type: application/json",
                                "--data", json_payload])
                    message.append(row[7] + " updated")
                # Else add new device:    
                else:
                    if row[4] == 'Wi-Fi':
                        group = wireless
                    else:
                        group = wired
                    payload = {
                            "description" : row[2] + 'Esports device',
                            "mac" : row[7],
                            "groupId" : group,
                            "staticGroupAssignment" : True,
                            "customAttributes" : {
                                "deviceType" : row[8],
                                "school" : row[2],
                                "coachEmail" : row[1],
                                "created" : timestamp
                            }
                        }
                    json_payload = json.dumps(payload, indent=4)
                    # print(json_payload)
                    subprocess.run(["curl", "-X", "POST", iseUpdateEndpoint, 
                                "--insecure", "--silent", "-o", "/dev/null", "-w", str("%{http_code}"),
                                "--user", iseCreds,
                                "--header", "Accept: application/json" ,
                                "--header", "Content-Type: application/json",
                                "--data", json_payload])
                    message.append(row[7] + " added")
                
            else:
                message.append("ERROR: " + getEndpoint.stderr)
                
    return(message)

def sync_device_to_ise(device):
    ise_api_url = current_app.config['ISE_BASE']
    ise_username = current_app.config['ISE_USERNAME']
    ise_password = current_app.config['ISE_PASSWORD']
    ise_wired = current_app.config['ISE_WIRED']
    ise_wireless = current_app.config['ISE_WIRELESS']

    group_id = ise_wireless if device.is_wireless else ise_wired
    mac_address = device.device_mac.lower()

    get_headers = {
        "Accept": "application/json"
    }

    post_put_headers = {
        "Content-Type": "application/json"
    }

    # Build customAttributes
    custom_attributes = {
        "deviceType": device.platform.device_type if device.platform else "Unknown",
        "school": device.school.name if device.school else "Unknown",
        "coachEmail": "",  # Optional if you have it
        "created": datetime.utcnow().isoformat()
    }

    # Build base payload
    payload = {
        "mac": mac_address,
        "staticGroupAssignment": True,
        "groupId": group_id,
        "description": f"{device.device_name}",
        "customAttributes": custom_attributes
    }

    # Try to GET the endpoint first
    get_url = f"https://{ise_api_url}/api/v1/endpoint/name/{mac_address}"

    get_response = requests.get(
        get_url,
        auth=(ise_username, ise_password),
        headers=get_headers,  # 👈 Correct for GET
        verify=False
    )

    if get_response.status_code == 200:
        # Device exists -> PUT update
        endpoint_id = get_response.json()['ERSEndPoint']['id']
        put_url = f"https://{ise_api_url}/api/v1/endpoint/{endpoint_id}"


        print("=== Payload being sent to Cisco ISE (PUT) ===")
        print(payload)

        response = requests.put(
            put_url,
            auth=(ise_username, ise_password),
            headers=post_put_headers,  # 👈 Correct for PUT
            json=payload,
            verify=False
        )

        print("=== ISE Response Status Code ===")
        print(response.status_code)
        print("=== ISE Response Body ===")
        print(response.text)

    elif get_response.status_code == 404:
        # Device not found -> POST create
        post_url = f"https://{ise_api_url}/api/v1/endpoint"

        print("=== Payload being sent to Cisco ISE (POST) ===")
        print(payload)

        response = requests.post(
            post_url,
            auth=(ise_username, ise_password),
            headers=post_put_headers,  # 👈 Correct for POST
            json=payload,
            verify=False
        )

        print("=== ISE Response Status Code ===")
        print(response.status_code)
        print("=== ISE Response Body ===")
        print(response.text)

    else:
        raise Exception(f"Failed to check if endpoint exists. Status {get_response.status_code}: {get_response.text}")

    response.raise_for_status()

    if response.content and response.headers.get('Content-Type', '').startswith('application/json'):
        return response.json()
    else:
        return {"status": "success", "message": "Device synced or updated successfully"}


def delete_device_from_ise(mac_address):
    ise_api_url = current_app.config['ISE_BASE']
    ise_username = current_app.config['ISE_USERNAME']
    ise_password = current_app.config['ISE_PASSWORD']

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "ERS-Media-Type": "identity.endpoint.1.2"
    }

    mac_variants = [
        mac_address.upper(),
        mac_address.lower(),
        mac_address.upper().replace(":", "-"),
        mac_address.lower().replace(":", "-")
    ]

    for variant in mac_variants:
        current_app.logger.info(f"Trying MAC search: {variant}") 
        lookup_url = f"https://{ise_api_url}/ers/config/endpoint?filter=mac.EQ.{variant}"

        response = requests.get(
            lookup_url,
            auth=(ise_username, ise_password),
            headers=headers,
            verify=False
        )

        if response.status_code == 200:
            search_result = response.json()
            if 'SearchResult' in search_result and search_result['SearchResult']['total'] > 0:
                endpoint_id = search_result['SearchResult']['resources'][0]['id']
                delete_url = f"https://{ise_api_url}/ers/config/endpoint/{endpoint_id}"

                delete_response = requests.delete(
                    delete_url,
                    auth=(ise_username, ise_password),
                    headers=headers,
                    verify=False
                )
                delete_response.raise_for_status()
                current_app.logger.info(f"✅ Successfully deleted device with MAC {variant} from ISE.")
                return True
        elif response.status_code == 404:
            continue  # try next variant
        else:
            current_app.logger.error(f"❌ Failed during GET lookup for MAC {variant}: {response.text}")
            continue

    current_app.logger.warning(f"⚠ Device with MAC {mac_address} not found in ISE after all attempts.")
    return False





