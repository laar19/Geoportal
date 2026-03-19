import re

with open('geoportal_app/templates/sidebar.html', 'r') as f:
    content = f.read()

# Extract user session parts
user_session_regex = re.compile(r'<!-- User session icon - FIRST in the list.*?</li>', re.DOTALL)
login_icon_regex = re.compile(r'<!-- Login icon \(not logged in\) -->.*?</li>', re.DOTALL)
auth_disabled_regex = re.compile(r'<!-- Disabled auth icon -->.*?</li>', re.DOTALL)

user_session = user_session_regex.search(content).group(0)
login_icon = login_icon_regex.search(content).group(0)
auth_disabled = auth_disabled_regex.search(content).group(0)

# Remove them from the top
content = content.replace(user_session, '')
content = content.replace(login_icon, '')
content = content.replace(auth_disabled, '')

# Now find the end of the first ul and insert the second ul
ul_end = '</ul>'
second_ul = f'''</ul>
        <ul role="tablist">
            {user_session}
            {login_icon}
            {auth_disabled}
        </ul>'''

content = content.replace(ul_end, second_ul, 1)

# Make the user dropdown point leftwards instead of rightwards, since sidebar is on the left
content = content.replace('right: 50px !important;', 'left: 50px !important; right: auto !important;')

with open('geoportal_app/templates/sidebar.html', 'w') as f:
    f.write(content)
