'''
# This script is intended to pull data from a google sheet that has 
# device mac addresses. If esports coaches have entered in their data
# correct this will add the device to the proper esports wireless or 
# wired MAB (MAC address bypass list) in ISE.
'''
import os, subprocess, json

def Esports_ISE_MAB(output_file,timestamp):
    ## with open(output_file, 'r') as csv_file:
        ## csv_reader = csv.reader(csv_file)
    iseUser = os.environ.get('ISE_USERNAME')
    isePass = os.environ.get('ISE_PASSWORD')
    iseBase = os.environ.get('ISE_BASE')
    csv_reader = output_file
    wired = '58301c30-0612-11ee-bff4-de234da43ac2'
    wireless = '7a5260c0-2fb1-11ee-bff4-de234da43ac2'
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

