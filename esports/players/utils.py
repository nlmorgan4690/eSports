import ldap3, random, csv, os
from ldap3.core.exceptions import LDAPChangeError
from ldap3.utils.conv import to_unicode

def Esports_User_Acct (output_file):
    # Define the LDAP server connection
    ad_server = os.environ.get('AD_SERVER')
    ad_user = os.environ.get('AD_USER')
    ad_pass = os.environ.get('AD_PASS')
    comms = []
    for row in output_file:
        if row[3] == 'Device':
            continue
        else: 

            server = ldap3.Server(ad_server)

            # Create a connection to the server
            conn = ldap3.Connection(server, ad_user, ad_pass, auto_bind=None)
            conn.bind()

            # Create password by joining 10 words from the following list. 
            word_list = ["Esports", "Player", "Tournament", "Controller", "Competition",
                        "Console", "Victory", "Defeat", "Gamer", "Team", "Challenge",
                        "Score", "Highscore", "Skill", "Strategy", "Power-up", "Level",
                        "Avatar", "Character", "Quest", "Adventure", "Mission",
                        "Multiplayer", "Solo", "Squad", "Streaming", "Twitch", "Mixer",
                        "YouTube", "Fans", "Spectator", "Cheering", "Arena", "Leaderboard",
                        "Training", "Keyboard", "Mouse", "Headset", "Monitor", "GamingChair",
                        "Tag", "Community", "Arcade", "Earnings", "Cosplay", "Convention",
                        "LAN", "Mod", "Coach", "Organization", "League", "Finals", "Pro",
                        "Amateur", "Novice", "Practice", "Simulation", "Respawn", "EasterEgg",
                        "Achievement", "Loot", "Glitch", "Speedrun", "Select", "Health",
                        "PowerLevel", "Inventory", "Questline", "Storyline", "Difficulty",
                        "PvP", "PvE", "Map", "Weapon", "Armor", "Health Bar", "ExperiencePoints",
                        "Cutscene", "DLC", "Emote", "Chat", "Graphics", "VR", "AR", "MMORPG",
                        "FPS", "RPG", "RTS", "MOBA", "HUD", "Beta", "Alpha", "Patch", "Campaign",
                        "AI", "Raid", "Cooldown", "Hitbox", "Critical", "Customization",
                        "Voice", "Timer", "Hunter", "GameOver", "Pixel", "Gamepad",
                        "Frag", "Party", "First-Person", "Third-Person", "Teamwork", "Guild", 
                        "Streamer", "Fanbase", "Platform", "Jersey", "Intensity",
                        "Athlete", "Online", "Offline", "Farming", "Leader", "Caster",
                        "Exploit", "Speedrunning", "Lore", "Items",
                        "Mechanics", "Acting", "Development", "Testing", "Fixing",
                        "Balance", "Physics", "Engine", "Modding", "Trailer"]
            
            random_words = random.sample(word_list, 3) 
            random_pass = to_unicode(''.join(random_words).lower())
            hashed_pass = ('"%s"' %random_pass).encode('utf-16-le')

            # hashed_pass = hashlib.sha1(random_pass.encode()).hexdigest()
            if "@" in row[10]:
                uname = row[10].split('@')[0]+'-esports'
            else:
                uname = row[10]+'-esports'
            # setting up user_dn in advance     
            user_dn = f'CN={uname},OU=eSports User Accounts,OU=Network Access and Managment,OU=District Groups,OU=Administrative Area,DC=dcsdk12,DC=org'
            # setting up group dn in advance
            group_dn = 'CN=802.1x-eSports,OU=Network Security Roles,OU=Network Access and Managment,OU=District Groups,OU=Administrative Area,DC=dcsdk12,DC=org'
            # Define the user's attributes
            new_u_att = {'sAMAccountName': uname, 
                         'userPrincipalName': uname, 
                         'givenName': uname, 'sn': row[2] + '-eSports',
                         'userPrincipalName': uname + '@dcsdk12.org', 
                         'userPassword': random_pass,
                         'unicodePwd': hashed_pass,
                         'userAccountControl': '66080',
                         }
            
            # Add the user to AD
            if conn.add(user_dn, 'user', new_u_att ):
                print(f"{uname} added successfully ")
            else: 
                print(f"Failed to add user {uname}. Here is why:")
                print(conn.result['result'])

            # Add the user to the 802.1x-dSports group in AD. 
            add_member = [(ldap3.MODIFY_ADD, [user_dn])]
            
            try:
                # Apply the modification to add the user to the group
                if conn.modify(group_dn, {'member': add_member}):
                    print("User added to the group.")
                else:
                    print("Failed to add the user to the group.")
                    print(conn.result['result'])
            except LDAPChangeError as e:
                print(f"LDAPChangeError: {e}")

            # Close the connection
            conn.unbind()
            
            added_user = [row[1], row[2], row[10], uname, random_pass]
            comms.append(added_user)
            accounts = 'esports_user_acct.csv'

            with open(accounts, 'a', newline='') as update_csv:
                csv.writer(update_csv).writerow(added_user)
    return(comms)  




