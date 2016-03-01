report_experience = lambda s, n: True
report_experience_only_valuable = \
    lambda s, n: 'valuable' in n.content and 'not' not in n.content

fetch_experience = lambda s, n, u: True
fetch_experience_skip_badexperience = \
    lambda s, n, u: 'badexperience' not in u
