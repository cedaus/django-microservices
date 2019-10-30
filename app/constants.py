admin_status = {
    'ADMIN': 'ADMIN',
    'SUPER_ADMIN': 'SUPER_ADMIN'
}
admin_status_choices = [tuple([v, k]) for k, v in admin_status.items()]

currency = {
    'USD': 'USD',
    'INR': 'INR',
}
currency_choices = [tuple([v, k]) for k, v in currency.items()]

sex = {
    'FEMALE': 'FEMALE',
    'MALE': 'MALE',
    'TRANSGENDER': 'TRANSGENDER',
    'NOT_SPECIFIED': 'NOT_SPECIFIED'
}
sex_choices = [tuple([v, k]) for k, v in sex.items()]
sex_list = [k[0] for k in sex.items()]

chat_type_states = {
    'TEXT': 'TEXT',
    'FILE': 'FILE',
    'ACTIONABLE': 'ACTIONABLE',
}
chat_type_states_choices = [tuple([v, k]) for k, v in chat_type_states.items()]

message_type_states = {
    'TEXT': 'TEXT',
    'FILE': 'FILE',
    'ACTIONABLE': 'ACTIONABLE',
}
message_type_states_choices = [tuple([v, k]) for k, v in message_type_states.items()]

notification_type_states = {
    'ADD-TO-PROJECT':'ADD-TO-PROJECT',
    'ADD-TO-TASK': 'ADD-TO-TASK',
    'TASK-ACCEPTED':'TASK-ACCEPTED',
    'TASK-DENIED':'TASK-DENIED',
    'TASK-COMPLETED':'TASK-COMPLETED',
    'NEW-MSG':'NEW-MSG'
}
notification_type_states_choices = [tuple([v, k]) for k, v in notification_type_states.items()]

reference_type_states = {
    'CONNECTION': 'CONNECTION'
}
reference_type_states_choices = [tuple([v, k]) for k, v in reference_type_states.items()]


ERROR_CONFIG = {
    'ERR-DJNG-001': ("No CODE Passed", "Error Message"),
    'ERR-DJNG-002': ("No Object found", "Error Message"),
    'ERR-DJNG-003': ("Multiple Objects Returned", "Error Message"),
    'ERR-DJNG-004': ("Invalid operation", "Error Message"),
    'ERR-GNRL-001': ("Invalid Phone Number", "Error Message"),
    'ERR-GNRL-002': ("Invalid Email Address", "Error Message"),
    'ERR-AUTH-001': ("Invalid Credentials", "Error Message"),
    'ERR-AUTH-002': ("Unsuccessful exchange of Authorization Code for an Access Token", "Error Message"),
    'ERR-AUTH-003': ("Incorrect password", "Error Message"),
    'ERR-AUTH-004': ("Passwords do not match", "Error Message"),
    'ERR-AUTH-005': ("Invalid Phone OTP", "Error Message"),
    'ERR-USER-001': ("No User found", "Error Message"),
    'ERR-USER-002': ("User Already Exists", "Error Message"),
    'ERR-USER-003': ("User Blocked", "Error Message"),
    'ERR-USER-004': ("User Already Exists with Phone Number", "Error Message"),
    'ERR-USER-005': ("User Already Exists with Email ID", "Error Message"),
    'ERR-USER-006': ("User missing OTP details", "Error Message"),
    'ERR-USER-007': ("User permission denied", "Error Message"),
    'ERR-USER-008': ("User Already Exists with username", "Error Message"),
    'ERR-USER-009': ("User does not exists for given token", "Error Message"),
    'ERR-USER-010': ("User do not have permission to edit the Entity", "Error Message"),
    'ERR-USER-011': ("Admin do not have permission", "Error Message"),
    'ERR-USER-012': ("User account no longer exists", "Error Message"),
    'ERR-CONT-001': ("No such contact founder with email", "Error Message"),
    'ERR-CONT-002': ("No such contact founder with phone", "Error Message"),
    'ERR-COUR-001': ("No such course found", "Error Message"),
    'ERR-COUR-002': ("User is not enrolled into any such course", "Error Message"),
    'ERR0007': ("Invalid Phone Number", "Error Message"),
    'ERR0009': ("Invalid Email Address", "Error Message"),
    'ERR0011': ("Invalid Phone OTP", "Error Message"),
    'ERR0012': ("No OTP in Database", "Error Message"),
    'ERR-ENT-001': ("No Entity found", "Error Message"),
    'ERR-ROL-001': ("No Job Role found", "Error Message"),
}

profile_pic_source = {
    'CAMERA': 'CAMERA',
    'GALLERY': 'GALLERY',
}

profile_pic_source_choices = [tuple([v, k]) for k, v in profile_pic_source.items()]
profile_pic_source_list = [k[0] for k in profile_pic_source.items()]
