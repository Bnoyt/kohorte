from notify.signals import notify

def send(users, label, extra_context):
    object = extra_context['pm_message']
    notify.send(object.sender, recipient_list=users, actor=object.sender, verb="envoyé un MP", target=object, nf_type="mp")
    pass

#send(users=[user], label=label, extra_context={'pm_message': #object, 'pm_action': action, 'pm_site': site})

#notify.send(request.user, recipient_list=followers, #actor=request.user, verb='uploaded.', target=video, #nf_type='video_upload_from_following')