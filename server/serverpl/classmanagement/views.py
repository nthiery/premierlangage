#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Python [Version]
#
#  Author: Coumes Quentin     Mail: qcoumes@etud.u-pem.fr
#  Created: 2017-07-30
#  Last Modified: 2017-07-30


import json, logging

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse

from classmanagement.models import Role, Course, PLUser

from playexo.models import Answer, Activity
from playexo.views import activity_view


logger = logging.getLogger(__name__)


#Give the right state number for the css class according to answer's state of the course and summaries pages
STATE = {
    Answer.SUCCEEDED: "1",
    Answer.FAILED: "2",
    Answer.STARTED: "3",
    Answer.NOT_STARTED: "4",
}

#Give the right state number for the css class according to user color blindness
BLINDNESS = {
    PLUser.NONE: "",
    PLUser.DEUTERANOPIA: "-deuteranopia",
    PLUser.PROTANOPIA: "-protanopia",
    PLUser.TRITANOPIA: "-tritanopia",
}



@login_required
@csrf_exempt
def index(request):
    course = list()
    for item in request.user.course_set.all():
        summary = Answer.user_course_summary(item, request.user)
        completion = [
            {'name': "Réussi", 'count': summary['succeeded'][1]},
            {'name': "Echoué", 'count': summary['failed'][1]},
            {'name': "Commencé", 'count': summary['started'][1]},
            {'name': "Non Commencé", 'count': summary['not_started'][1]},
        ]
        
        course.append({
            'id': item.id,
            'name': item.name,
            'completion': completion,
            'nb_square': int(summary['succeeded'][1])+ int(summary['failed'][1]) + int(summary['started'][1]) + int(summary['not_started'][1]),
        })
        
    return render(request, 'classmanagement/index.html', {
        'course': course,
    })



@csrf_exempt
@login_required
def course_view(request, id):
    try:
        course = Course.objects.get(id=id)
    except:
        raise Http404("Impossible d'accéder à la page, cette classe n'existe pas.")
    if not request.user in course.user.all() and not request.user.pluser.is_admin():
        raise PermissionDenied("Vous n'appartenez pas à cette classe et ne pouve donc y accéder.")
    
    #Getting profs
    query = course.user.all()
    prof = list()
    for user in query:
        if user.pluser.have_role(Role.INSTRUCTOR):
            if not prof:
                prof.append("- "+user.get_full_name().title()+" ("+user.email+")")
            else:
                prof.append("- "+user.get_full_name().title()+" ("+user.email+")")
    
    #Getting activities
    activities = course.activity.all().order_by("id")
    activity = list()
    for item in activities:
        pl = list()
        for elem in item.pltp.pl.all():
            pl.append({
                'name': json.loads(elem.json)['title'],
                'state': STATE[Answer.pl_state(elem, request.user)]+BLINDNESS[request.user.pluser.color_blindness],
            })
        
        
        len_pl = len(pl) if len(pl) else 1
        activity.append({
            'name': item.name,
            'pltp_sha1': item.pltp.sha1,
            'title': json.loads(item.pltp.json)['title'],
            'strategy_name': item.strategy.name,
            'activity_id': item.id,
            'pl': pl,
            'width':str(100/len_pl),
        })
        
    return render(request, 'classmanagement/course.html', {
        'name': course.name,
        'activity': activity,
        'prof': prof,
        'instructor': True if request.user.pluser.have_role(Role.INSTRUCTOR) else False,
        'course_id': id,
    })



@csrf_exempt
@login_required
def course_summary(request, id):
    try:
        course = Course.objects.get(id=id)
    except:
        raise Http404("Impossible d'accéder à la page, cette classe n'existe pas.")
    if not request.user.pluser.is_admin() and (not request.user in course.user.all() or not request.user.pluser.have_role(Role.INSTRUCTOR)):
        raise PermissionDenied("Vous n'êtes pas professeur de cette classe.")
    
    activities = course.activity.all().order_by("id")
    student = list()
    for user in course.user.all():
        tp = list()
        for activity in activities:
            tp.append({
                'state': Answer.pltp_summary(activity.pltp, user),
                'name': json.loads(activity.pltp.json)['title'],
                'activity_name': activity.name,
            })
        student.append({
            'lastname': user.last_name,
            'name': user.get_full_name(),
            'id': user.id,
            'activities': tp,
        })
    
    #Sort list by student's name
    student = sorted(student, key=lambda k: k['lastname'])
    
    return render(request, 'classmanagement/course_summary.html', {
        'name': course.name,
        'student': student,
        'range_tp': range(len(activities)),
        'course_id': id,
    })



@csrf_exempt
@login_required
def activity_summary(request, id, name):
    try:
        course = Course.objects.get(id=id)
    except:
        raise Http404("Impossible d'accéder à la page, cette classe n'existe pas.")
    if not request.user.pluser.is_admin() and (not request.user in course.user.all() or not request.user.pluser.have_role(Role.INSTRUCTOR)):
        raise PermissionDenied("Vous n'êtes pas professeur de cette classe.")
    
    activity = Activity.objects.get(name=name)
    student = list()
    for user in course.user.all():
        tp = list()
        for pl in activity.pltp.pl.all():
            tp.append({
                'name': json.loads(pl.json)['title'],
                'state': STATE[Answer.pl_state(pl, user)]+BLINDNESS[request.user.pluser.color_blindness],
            })
        student.append({
            'lastname': user.last_name,
            'name': user.get_full_name(),
            'id': user.id,
            'question': tp,
        })
    
    #Sort list by student's name
    student = sorted(student, key=lambda k: k['lastname'])
    
    return render(request, 'classmanagement/activity_summary.html', {
        'course_name': course.name,
        'activity_name': activity.name,
        'student': student,
        'range_tp': range(len(activity.pltp.pl.all())),
        'course_id': id,
    })



@csrf_exempt
@login_required
def student_summary(request, course_id, student_id):
    try:
        course = Course.objects.get(id=course_id)
    except:
        raise Http404("Impossible d'accéder à la page, cette classe n'existe pas.")
    if not request.user.pluser.is_admin() and (not request.user in course.user.all() or not request.user.pluser.have_role(Role.INSTRUCTOR)):
        raise PermissionDenied("Vous n'êtes pas professeur de cette classe.")
        
    student = User.objects.get(id=student_id)
    activities = course.activity.all().order_by("id")
    
    tp = list()
    for activity in activities:
        question = list()
        for pl in activity.pltp.pl.all():
            state = STATE[Answer.pl_state(pl, student)]+BLINDNESS[request.user.pluser.color_blindness]
            question.append({
                'state': state,
                'name':  json.loads(pl.json)['title'],
            })
        len_tp = len(question) if len(question) else 1
        tp.append({
            'name': json.loads(activity.pltp.json)['title'],
            'activity_name': activity.name,
            'width': str(100/len_tp),
            'pl': question,
        })
        
    return render(request, 'classmanagement/student_summary.html', {
        'course_name': course.name,
        'student_name': student.get_full_name(),
        'activities': tp,
        'course_id': course_id,
    })


@login_required
def activity_correction(request, course_id, activity_id):
    try:
        course = Course.objects.get(id=course_id)
    except:
        raise Http404("Impossible d'accéder à la page, cette classe n'existe pas ("+str(course_id)+").")
    try:
        activity = Activity.objects.get(id=activity_id)
    except:
        raise Http404("Impossible d'accéder à la page, cette activité n'existe pas ("+str(activity_id)+").")
    if not request.user.pluser.is_admin() and (not request.user in course.user.all() or not request.user.pluser.have_role(Role.INSTRUCTOR)):
        raise PermissionDenied("Vous n'êtes pas professeur de cette classe.")
    
    pltp = activity.pltp
    action = None
    user_id = None
    if request.method == 'GET':
        action = request.GET.get("action", None)
        user_id = request.GET.get("current", None)
        
    user_list = course.user.all()
    user = user_list[0] if not user_id else User.objects.get(id=user_id)
    if action == 'next':
        if list(user_list).index(user)+1 == len(list(user_list)):
            index = 0
        else:
            index = list(user_list).index(user)+1
        user = user_list[index]
    elif action == 'previous':
        if not list(user_list).index(user):
            index = len(list(user_list))-1
        else:
            index = list(user_list).index(user)-1
        user = user_list[index]
    elif  action == 'direct':
        user = User.objects.get(id=user_id)
        
    answers = list()
    for pl in pltp.pl.all():
        try:
            answer = Answer.objects.filter(pl=pl, user=user).order_by("-date")
            answer = {'value': "L'élève n'a pas répondu à cette exercice\n"} if not answer else answer[0]
        except Exception as e:
            answer = {'value': "La récupération de la réponse à échoué ("+str(type(e))+": "+ str(e)+").\n"}
        
        if isinstance(answer, dict):
            height = 32
            state = "Non Commencé"
        else:
            height = len(answer.value.split('\n'))*16
            state = "Non Commencé" if not answer else answer.get_state_display()
            
        answers.append({
            'title': json.loads(pl.json)['title'],
            'answer': answer if answer else {'value': "L'élève n'a pas répondu à cette exercice\n"},
            'height': height,
            'state': state,
        })
    
    return render(request, 'classmanagement/correction.html', {
        'current_pltp': json.loads(pltp.json)['title'],
        'current_user': user,
        'answers': answers,
        'user_list': user_list,
    })


@login_required
def redirect_activity(request, activity_name):
    request.session['current_activity'] = activity_name
    request.session['exercise'] = None
    return HttpResponseRedirect(reverse(activity_view))


@login_required
def cycle_color_blindness(request):
    request.user.pluser.color_blindness = PLUser.COLOR_BLINDNESS[(PLUser.COLOR_BLINDNESS.index((request.user.pluser.color_blindness, request.user.pluser.get_color_blindness_display()))+1)%len(PLUser.COLOR_BLINDNESS)][0]
    request.user.pluser.save()
    redirect_url = request.GET.get('from', None)
    return HttpResponseRedirect(redirect_url)
