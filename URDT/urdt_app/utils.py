def superuser_required(user):
    return user.is_authenticated and user.role == "SUPER_USER"

def administrative_user_required(user):
    return user.is_authenticated and user.role == "ADMINISTRATIVE_USER"

def sub_admin_required(user):
    return user.is_authenticated and user.role == "SUB_ADMIN"

def epicenter_manager_required(user):
    return user.is_authenticated and user.role == "EPICENTER_MANAGER"

def trainee_required(user):
    return user.is_authenticated and user.role == "TRAINEE"

def sector_lead_required(user):
    return user.is_authenticated and user.role == "SECTOR_LEAD" and user.sector is not None

def trainer_required(user):
    return user.is_authenticated and user.role == "TRAINER"


