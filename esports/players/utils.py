import ldap3, random, csv, os
from ldap3.core.exceptions import LDAPChangeError, LDAPBindError, LDAPException
from ldap3.utils.conv import to_unicode
from flask import current_app
import random
import logging

from ldap3.utils.conv import to_unicode

logger = logging.getLogger(__name__)

def get_user_dn(username: str) -> str:
    template = os.environ.get("AD_USER_DN_TEMPLATE")
    if not template:
        raise ValueError("❌ Environment variable AD_USER_DN_TEMPLATE is not set.")
    return template.format(username=username)

def generate_account(email: str) -> tuple[str, str, bytes]:
    """
    Generate esports-style AD username and passphrase from email.
    Returns (username, passphrase, hashed unicodePwd)
    """
    if "@" in email:
        username = email.split("@")[0] + "-esports"
    else:
        username = email + "-esports"

    word_list = [
        "aim", "ally", "arc", "area", "armor", "arena", "auto", "ban", "base", "beta",
        "blink", "bot", "buff", "camp", "cap", "carry", "cast", "chat", "clan", "clash",
        "click", "combo", "cool", "crate", "creep", "dash", "data", "death", "def", "demo",
        "dodge", "drift", "drop", "duels", "edge", "event", "fan", "fast", "fight", "fire",
        "flank", "frag", "game", "gamer", "gold", "grind", "guild", "hack", "heals", "hype",
        "icon", "item", "items", "join", "jump", "kick", "kills", "lag", "lane", "laser",
        "lead", "level", "load", "loot", "loots", "macro", "main", "mana", "map", "match",
        "meta", "mods", "mobs", "mouse", "nades", "nexus", "node", "patch", "ping", "play",
        "plays", "pro", "pvp", "push", "quest", "raid", "rank", "rift", "roam", "role",
        "rush", "score", "shot", "skin", "skins", "squad", "stack", "stats", "storm", "strat"
    ]
    passphrase = to_unicode("".join(random.sample(word_list, 3)).lower())
    hashed_passphrase = ('"%s"' % passphrase).encode('utf-16-le')

    return username, passphrase, hashed_passphrase

def provision_ad_account(username: str, passphrase: str, hashed_pass: bytes):
    server = ldap3.Server(os.environ.get('AD_SERVER'))
    conn = ldap3.Connection(
        server,
        os.environ.get('AD_USER'),
        os.environ.get('AD_PASS'),
        auto_bind=True
    )


    user_dn = get_user_dn(username)
    group_dn = current_app.config['AD_GROUP_DN']
    
    attributes = {
        'sAMAccountName': username,
        'userPrincipalName': username + '@dcsdk12.org',
        'givenName': username,
        'sn': "eSports",
        'userPassword': passphrase,
        'unicodePwd': hashed_pass,
        'userAccountControl': '66080',
    }

    if conn.add(user_dn, 'user', attributes):
        print(f"✅ AD user {username} added.")
    else:
        print(f"❌ Failed to add {username}: {conn.result['description']}")

    try:
        if conn.modify(group_dn, {'member': [(ldap3.MODIFY_ADD, [user_dn])]}):
            print(f"✅ Added {username} to group.")
        else:
            print(f"❌ Failed to add {username} to group: {conn.result['description']}")
    except LDAPChangeError as e:
        print(f"LDAPChangeError: {e}")
    finally:
        conn.unbind()

def sync_player_to_ad(player):
    """
    Sync a player to Active Directory by adding them to a specific group.
    Uses the player's email to construct their AD username (UPN format).
    """
    try:
        # Load configuration from Flask app config
        server_uri = current_app.config["AD_SERVER"]
        bind_user = current_app.config["AD_USER"]
        bind_password = current_app.config["AD_PASS"]
        base_dn = current_app.config["AD_BASE_DN"]
        group_dn = current_app.config["AD_GROUP_DN"]

        server = ldap3.Server(server_uri, get_info=ldap3.ALL)
        conn = ldap3.Connection(server, user=bind_user, password=bind_password, auto_bind=True)

        # Construct user UPN from email (e.g., user@domain.local)
        # user_upn = player.email.strip().lower()
        user_upn = player.name.strip().lower()


        # Find DN of the user based on UPN
        conn.search(
            search_base=base_dn,
            search_filter=f"(userPrincipalName={user_upn})",
            attributes=['distinguishedName']
        )

        if not conn.entries:
            raise ValueError(f"No AD user found for {user_upn}")

        user_dn = conn.entries[0].distinguishedName.value

        # Add user to the group
        conn.modify(
            group_dn,
            {'member': [(ldap3.MODIFY_ADD, [user_dn])]}
        )

        if conn.result['result'] == 0:
            logger.info(f"✅ Successfully synced {user_upn} to AD group.")
        else:
            logger.warning(f"⚠️ Failed to sync {user_upn}: {conn.result}")

        conn.unbind()

    except Exception as e:
        logger.error(f"❌ AD sync failed for {user_upn}: {e}")
        raise


def user_exists_in_ad(username):
    """
    Check if a user with the given esports AD username exists in Active Directory.
    """
    try:
        server_uri = current_app.config["AD_SERVER"]
        bind_user = current_app.config["AD_USER"]
        bind_password = current_app.config["AD_PASS"]
        base_dn = current_app.config["AD_BASE_DN"]
        user_upn = f"{username}@dcsdk12.org"  # Constructed from esports username

        server = ldap3.Server(server_uri)
        conn = ldap3.Connection(server, user=bind_user, password=bind_password, auto_bind=True)

        conn.search(
            search_base=base_dn,
            search_filter=f"(userPrincipalName={user_upn})",
            attributes=['distinguishedName']
        )

        exists = bool(conn.entries)
        conn.unbind()
        return exists

    except (LDAPBindError, LDAPException) as e:
        logger.error(f"LDAP error checking existence of {username}: {e}")
        raise


def delete_ad_account(username: str):
    """
    Delete an Active Directory user account based on the provided username.
    """
    try:
        server = ldap3.Server(os.environ.get("AD_SERVER"))
        conn = ldap3.Connection(
            server,
            os.environ.get("AD_USER"),
            os.environ.get("AD_PASS"),
            auto_bind=True
        )

        user_dn = get_user_dn(username)

        if conn.delete(user_dn):
            print(f"🗑️ AD user {username} deleted.")
        else:
            print(f"❌ Failed to delete {username} from AD: {conn.result['description']}")

        conn.unbind()

    except Exception as e:
        logger.error(f"❌ AD delete failed for {username}: {e}")
        raise


# def Esports_User_Acct (output_file):
#     # Define the LDAP server connection
#     ad_server = os.environ.get('AD_SERVER')
#     ad_user = os.environ.get('AD_USER')
#     ad_pass = os.environ.get('AD_PASS')
#     comms = []
#     for row in output_file:
#         if row[3] == 'Device':
#             continue
#         else: 

#             server = ldap3.Server(ad_server)

#             # Create a connection to the server
#             conn = ldap3.Connection(server, ad_user, ad_pass, auto_bind=None)
#             conn.bind()

#             # Create password by joining 10 words from the following list. 
#             word_list = ["Esports", "Player", "Tournament", "Controller", "Competition",
#                         "Console", "Victory", "Defeat", "Gamer", "Team", "Challenge",
#                         "Score", "Highscore", "Skill", "Strategy", "Power-up", "Level",
#                         "Avatar", "Character", "Quest", "Adventure", "Mission",
#                         "Multiplayer", "Solo", "Squad", "Streaming", "Twitch", "Mixer",
#                         "YouTube", "Fans", "Spectator", "Cheering", "Arena", "Leaderboard",
#                         "Training", "Keyboard", "Mouse", "Headset", "Monitor", "GamingChair",
#                         "Tag", "Community", "Arcade", "Earnings", "Cosplay", "Convention",
#                         "LAN", "Mod", "Coach", "Organization", "League", "Finals", "Pro",
#                         "Amateur", "Novice", "Practice", "Simulation", "Respawn", "EasterEgg",
#                         "Achievement", "Loot", "Glitch", "Speedrun", "Select", "Health",
#                         "PowerLevel", "Inventory", "Questline", "Storyline", "Difficulty",
#                         "PvP", "PvE", "Map", "Weapon", "Armor", "Health Bar", "ExperiencePoints",
#                         "Cutscene", "DLC", "Emote", "Chat", "Graphics", "VR", "AR", "MMORPG",
#                         "FPS", "RPG", "RTS", "MOBA", "HUD", "Beta", "Alpha", "Patch", "Campaign",
#                         "AI", "Raid", "Cooldown", "Hitbox", "Critical", "Customization",
#                         "Voice", "Timer", "Hunter", "GameOver", "Pixel", "Gamepad",
#                         "Frag", "Party", "First-Person", "Third-Person", "Teamwork", "Guild", 
#                         "Streamer", "Fanbase", "Platform", "Jersey", "Intensity",
#                         "Athlete", "Online", "Offline", "Farming", "Leader", "Caster",
#                         "Exploit", "Speedrunning", "Lore", "Items",
#                         "Mechanics", "Acting", "Development", "Testing", "Fixing",
#                         "Balance", "Physics", "Engine", "Modding", "Trailer"]
            
#             random_words = random.sample(word_list, 3) 
#             random_pass = to_unicode(''.join(random_words).lower())
#             hashed_pass = ('"%s"' %random_pass).encode('utf-16-le')

#             # hashed_pass = hashlib.sha1(random_pass.encode()).hexdigest()
#             if "@" in row[10]:
#                 uname = row[10].split('@')[0]+'-esports'
#             else:
#                 uname = row[10]+'-esports'
#             # setting up user_dn in advance     
#             user_dn = f'CN={uname},OU=eSports User Accounts,OU=Network Access and Managment,OU=District Groups,OU=Administrative Area,DC=dcsdk12,DC=org'
#             # setting up group dn in advance
#             group_dn = 'CN=802.1x-eSports,OU=Network Security Roles,OU=Network Access and Managment,OU=District Groups,OU=Administrative Area,DC=dcsdk12,DC=org'
#             # Define the user's attributes
#             new_u_att = {'sAMAccountName': uname, 
#                          'userPrincipalName': uname, 
#                          'givenName': uname, 'sn': row[2] + '-eSports',
#                          'userPrincipalName': uname + '@dcsdk12.org', 
#                          'userPassword': random_pass,
#                          'unicodePwd': hashed_pass,
#                          'userAccountControl': '66080',
#                          }
            
#             # Add the user to AD
#             if conn.add(user_dn, 'user', new_u_att ):
#                 print(f"{uname} added successfully ")
#             else: 
#                 print(f"Failed to add user {uname}. Here is why:")
#                 print(conn.result['result'])

#             # Add the user to the 802.1x-dSports group in AD. 
#             add_member = [(ldap3.MODIFY_ADD, [user_dn])]
            
#             try:
#                 # Apply the modification to add the user to the group
#                 if conn.modify(group_dn, {'member': add_member}):
#                     print("User added to the group.")
#                 else:
#                     print("Failed to add the user to the group.")
#                     print(conn.result['result'])
#             except LDAPChangeError as e:
#                 print(f"LDAPChangeError: {e}")

#             # Close the connection
#             conn.unbind()
            
#             added_user = [row[1], row[2], row[10], uname, random_pass]
#             comms.append(added_user)
#             accounts = 'esports_user_acct.csv'

#             with open(accounts, 'a', newline='') as update_csv:
#                 csv.writer(update_csv).writerow(added_user)
#     return(comms)  




