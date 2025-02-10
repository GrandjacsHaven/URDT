
from django.db.models import Q
from .models import SafeguardingMessage, TraineeApplication

def safeguarding_notifications(request):
    if not request.user.is_authenticated:
        return {}

    user = request.user

    # For trainees: check if there are unread staff messages
    if user.role == 'TRAINEE':
        try:
            trainee = TraineeApplication.objects.get(created_by=user)
            has_unread = SafeguardingMessage.objects.filter(
                trainee=trainee,
                sender__role__in=['SUB_ADMIN', 'ADMIN']
            ).exclude(read_by=request.user).exists()
            return {'trainee_unread_count': 1 if has_unread else 0}
        except TraineeApplication.DoesNotExist:
            return {}

    # For safeguarding officers & stakeholders:
    # This includes users with role 'SUB_ADMIN', users with specific designations, 
    # or those identified as 'sector_lead'
    if (user.role == 'SUB_ADMIN' or 
        (user.designation and user.designation.lower() in [
            'm&e officer', 'principal', 'sector lead', 'accountant', 'project manager', 'safe guarding officer'
        ]) or
        (user.role and user.role.lower() == 'sector_lead')):

        unread_from_trainees = SafeguardingMessage.objects.filter(
            sender__role='TRAINEE'
        ).exclude(read_by=request.user)

        # If the user is a sector lead, only count messages from trainees in their sector
        if user.role and user.role.lower() == 'sector_lead':
            unread_from_trainees = unread_from_trainees.filter(trainee__sector=user.sector)

        staff_unread_count = unread_from_trainees.values('trainee').distinct().count()
        return {'staff_unread_count': staff_unread_count}

    return {}









def dynamic_base_template(request):
    """Returns the appropriate base template based on the logged-in user's role and sector."""
    base_template = "base.html"  # Default fallback

    if request.user.is_authenticated:
        # Determine base template based on role
        role_templates = {
            "SUPER_USER": "superuser/base.html",
            "ADMINISTRATIVE_USER": "adminuser/base.html",
            "SUB_ADMIN": "subadmin/base.html",
            "EPICENTER_MANAGER": "epicentermanager/base.html",
            "SECTOR_LEAD": "sectorlead/base.html",  # Placeholder, refined further below
            "TRAINEE":"trainee/base.html",
            "TRAINER":"trainer/base.html"
        }

        base_template = role_templates.get(request.user.role, "base.html")

        # If user is a Sector Lead, refine base_template based on their sector
        if request.user.role == "SECTOR_LEAD" and request.user.sector:
            sector_name = request.user.sector.name.lower()
            sector_templates = {
                "tourism": "sectorlead/tourism_base.html",
                "agriculture": "sectorlead/agriculture_base.html",
                "construction": "sectorlead/construction_base.html",
            }
            for key, template in sector_templates.items():
                if key in sector_name:
                    base_template = template
                    break  # Stop once we find a match

    return {"base_template": base_template}
