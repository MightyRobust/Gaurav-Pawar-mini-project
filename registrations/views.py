import json
import logging
from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import ContactMessage, Registration

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Participant Registration Form
# ------------------------------------------------------------------
class ParticipantRegistrationForm(forms.ModelForm):
    age = forms.IntegerField(required=False)

    class Meta:
        model = Registration
        fields = [
            'full_name', 
            'email', 
            'phone', 
            'team_name', 
            'branch_sem', 
            'age', 
            'gender', 
            'sport'
        ]


# ------------------------------------------------------------------
# Participant Registration Endpoint
# ------------------------------------------------------------------
@csrf_exempt
@require_POST
def register_participant(request):
    # Parse payload based on Content-Type
    if request.content_type == 'application/json':
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON structure.'}, status=400)
    else:
        payload = request.POST.dict()

    # Field alias normalization (fullname -> full_name)
    if 'fullname' in payload and 'full_name' not in payload:
        payload['full_name'] = payload.pop('fullname')

    # Gender normalization to model keys ('M', 'F', 'O')
    raw_gender = str(payload.get('gender', '')).strip().lower()
    gender_map = {
        'm': 'M', 'male': 'M', 'boys': 'M', 'boys registration': 'M',
        'f': 'F', 'female': 'F', 'girls': 'F', 'girls registration': 'F',
        'o': 'O', 'other': 'O'
    }
    if raw_gender in gender_map:
        payload['gender'] = gender_map[raw_gender]

    # Sport normalization (e.g., 'Cricket' -> 'cricket')
    if 'sport' in payload and isinstance(payload['sport'], str):
        payload['sport'] = payload['sport'].strip().lower()

    form = ParticipantRegistrationForm(payload)

    if not form.is_valid():
        print("\n--- FORM VALIDATION ERRORS ---")
        print(form.errors.as_json())
        print("------------------------------\n")
        return JsonResponse(
            {'status': 'error', 'errors': form.errors}, 
            status=400
        )

    # 1. Save participant instance
    registration = form.save()

    # 2. Prepare confirmation email details
    sport_display = registration.get_sport_display() if hasattr(registration, 'get_sport_display') else registration.sport
    subject = f"Registration Confirmed for {sport_display}!"
    message = (
        f"Hello {registration.full_name},\n\n"
        f"Thank you for registering! Here are your details:\n"
        f"- Sport: {sport_display}\n"
        f"- Contact: {registration.phone}\n"
        f"- Team: {registration.team_name or 'N/A'}\n"
        f"- Branch/Sem: {registration.branch_sem or 'N/A'}\n\n"
        f"We look forward to seeing you at the event.\n\n"
        f"Best regards,\n"
        f"SDT Kalani Sports Committee"
    )

    # 3. Attempt confirmation email delivery
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[registration.email],
            fail_silently=False,
        )
    except Exception as exc:
        logger.error(f"Failed to send confirmation email to {registration.email}: {exc}")
        return JsonResponse({
            'status': 'warning',
            'message': 'Registration successful, but confirmation email could not be delivered.'
        }, status=200)

    return JsonResponse({
        'status': 'success',
        'message': 'Registration successful! Confirmation email sent.'
    }, status=200)


#------------------------------------------------------------------
# Contact Us Endpoint
# ------------------------------------------------------------------
@csrf_exempt
def contact_view(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body.decode('utf-8'))
            except json.JSONDecodeError:
                return JsonResponse({'status': 'error', 'message': 'Invalid JSON structure.'}, status=400)
            fullname = data.get('fullname')
            phone = data.get('phone')
            student_email = data.get('email')
            user_message = data.get('message')
        else:
            fullname = request.POST.get('fullname')
            phone = request.POST.get('phone')
            student_email = request.POST.get('email')
            user_message = request.POST.get('message')

        # 1. Save submission to database
        ContactMessage.objects.create(
            fullname=fullname,
            phone=phone,
            email=student_email,
            message=user_message
        )

        # 2. Build Thank You Email
        subject = "Thank You for Contacting SDT Kalani College Sports Department!"
        message = (
            f"Dear {fullname},\n\n"
            f"Thank you for reaching out to us with your message/feedback!\n\n"
            f"We have safely received your message and our team will review it shortly in our dashboard. "
            f"If a response is required, we will reach out directly using this email address or your contact number ({phone}).\n\n"
            f"--- Summary of Your Message ---\n"
            f"\"{user_message}\"\n\n"
            f"Best regards,\n"
            f"Sports Committee\n"
            f"SDT Kalani College"
        )

        # 3. Send email to student
        try:
            if student_email:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[student_email],
                    fail_silently=False,
                )
                logger.info(f"Thank you email successfully sent to {student_email}")

            return JsonResponse({
                'status': 'success',
                'message': 'Message saved and thank you email sent to student!'
            })

        except Exception as e:
            logger.error(f"SMTP Error for {student_email}: {e}")
            return JsonResponse({
                'status': 'warning',
                'message': f'Message saved in Admin panel, but email could not be sent: {str(e)}'
            })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)