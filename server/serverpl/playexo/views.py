#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Python [Version]
#
#  Author: Coumes Quentin     Mail: qcoumes@etud.u-pem.fr
#  Created: 2017-07-05
#  Last Modified: 2017-07-05

import json

from sympy import evaluate

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse
from django.contrib import messages

from gitload.models import PLTP, PL, Strategy

from playexo.exercise import Exercise, ExerciseTest
from playexo.builder import PythonBuilder, PythonBuilderTest
from playexo.models import Activity, Answer

from classmanagement.models import Course



@csrf_exempt
@login_required
def activity_view(request):
    activity_name = request.session.get("current_activity", None)
    exercise = request.session.get("exercise", None)
    pl_sha1 = None
    success = None
    feedback = None
    
    if exercise:
        exercise = Exercise(exercise)
        
    if request.method == 'GET' or request.method == 'POST':
        action = request.GET.get("action", None)
        if action == "pl":
            pl_sha1 = request.GET.get("pl_sha1", None)
        elif action == "pltp":
            exercise = None
            request.session["exercise"] = None
        elif action == "reset":
            if 'code' in exercise.dic:
                    value = exercise.dic["code"]
            else:
                value = ""
            Answer(value=value, user=request.user, pl=PL.objects.get(sha1=exercise.dic['pl_sha1']), seed=exercise.dic['seed'], state=Answer.STARTED).save()
        elif action == "next":
            try:
                activity = Activity.objects.get(name=activity_name)
                pl = activity.pltp.pl.all()
                current = False
                for item in pl:
                    if item.sha1 == exercise.dic["pl_sha1"]:
                        current = True
                    elif current:
                        pl_sha1 = item.sha1
                        break
                if current == True and pl_sha1 == None: #Last exercise
                    exercise = None
                    request.session["exercise"] = None
            except Exception as e:
                raise Http404("Impossible d'accéder à l'exercice suivant ("+str(e)+"). Merci de contacter votre professeur.")
            
        try: #AJAX
            status = None
            status = json.loads(request.body.decode())
        except:
            pass
        if status:
            if status['requested_action'] == 'submit': # Valider
                success, feedback = exercise.evaluate(status['inputs'])
                if 'answer' in status['inputs']:
                    value = status['inputs']['answer']
                else:
                    value = ""
                if success == None:
                    feedback_type = "info"
                    Answer(value=value, user=request.user, pl=PL.objects.get(sha1=exercise.dic['pl_sha1']), seed=exercise.dic['seed'], state=Answer.STARTED).save()
                elif success:
                    feedback_type = "success"
                    Answer(value=value, user=request.user, pl=PL.objects.get(sha1=exercise.dic['pl_sha1']), seed=exercise.dic['seed'], state=Answer.SUCCEEDED).save()
                else:
                    feedback_type = "fail"
                    Answer(value=value, user=request.user, pl=PL.objects.get(sha1=exercise.dic['pl_sha1']), seed=exercise.dic['seed'], state=Answer.FAILED).save()
                return HttpResponse(json.dumps({'feedback_type': feedback_type, 'feedback': feedback}), content_type='application/json')
            
            elif status['requested_action'] == 'save': #Sauvegarder
                if 'answer' in status['inputs']:
                    value = status['inputs']['answer']
                else:
                    value = ""
                Answer(value=value, user=request.user, pl=PL.objects.get(sha1=exercise.dic['pl_sha1']), seed=exercise.dic['seed'], state=Answer.STARTED).save()
                return HttpResponse(json.dumps({'feedback_type': "info", 'feedback': "Votre réponse à bien été enregistrée."}), content_type='application/json')
           
    if not exercise or pl_sha1:
        activity = Activity.objects.get(name=activity_name)
        pl = None
        seed=None
        if pl_sha1:
            pl = PL.objects.get(sha1=pl_sha1)
            dic=json.loads(pl.json)
            try:
                if "oneshot" not in dic and dic['oneshot']=="True":
                    seed = Answer.objects.filter(user=request.user, pl=pl)[0].seed
                
            except: #No existing answer
                pass
        exercise = PythonBuilder(request, activity, pl, seed).get_exercise()
        if pl_sha1:
            request.session['exercise'] = exercise.dic
            return redirect(activity_view) #Remove get parameters from url
            
    request.session['exercise'] = exercise.dic
    return HttpResponse(exercise.render(request, feedback, success))
    

@login_required
@csrf_exempt
def lti_receiver(request, activity_name, strategy_name, pltp_sha1):
    activity_id = request.session.pop("activity", None)
    course_id = request.session.pop("course_id", None)
    if not activity_id or not course_id:
        raise Http404("Impossible d'accéder à la page, la requête LTI doit contenir une ID d'activité ainsi que d'une ID de classe.")
    
    try:
        activity = Activity.objects.get(id=activity_id)
    except:
        try:
            pltp = PLTP.objects.get(sha1=pltp_sha1)
            strategy = Strategy.objects.get(name=strategy_name)
        except:
            raise Http404("Impossible de charger le TP associé à cette activité, celle-ci n'existe peut être plus sur la plateforme, merci de contacter votre professeur")
        activity = Activity(name=activity_name, pltp=pltp, strategy=strategy, id=activity_id)
        activity.save()
    Course.objects.get(id=course_id).activity.add(activity)
    
    request.session['current_activity'] = activity.name
    return HttpResponseRedirect(reverse(activity_view))

@login_required
def test_receiver(request, activity_name, strategy_name, pltp_sha1):
    try:
        activity = Activity.objects.get(name=activity_name)
    except:
        pltp = PLTP.objects.get(sha1=pltp_sha1)
        strategy = Strategy.objects.get(name=strategy_name)
        activity = Activity(name=activity_name, pltp=pltp, strategy=strategy, id=0)
        activity.save()
    request.session['current_activity'] = activity_name
    request.session['exercise'] = None
    return HttpResponseRedirect(reverse(activity_view))


@csrf_exempt
@login_required
def try_pl(request, pl=None, warning=None):
    with evaluate(False):
        exercise = request.session.get('exercise', None)
    success = None
    feedback = None
    
    if pl:
        messages.success(request, "Le PL <b>"+pl.name+"</b> a bien été chargé.")
        messages.warning(request, warning)
        messages.error(request, "Attention, ceci est une session de test, les réponses ne seront pas enregistrer après la fermeture de la fenêtre (Pensez à copier/coller).")
    
    if not exercise:
        pl_dic = pl.json
        exercise = PythonBuilderTest(pl_dic).get_exercise()
    else:
        exercise = ExerciseTest(exercise)
    
    if request.method == 'GET' or request.method == 'POST':
        status = None
        try:
            status = json.loads(request.body.decode())
        except:
            pass
        if status and status['requested_action'] == 'submit' :
            success, feedback = exercise.evaluate(status['inputs'])
            if (success):
                feedback_type = "success"
            else:
                feedback_type = "failed"
            return HttpResponse(json.dumps({'feedback_type': feedback_type, 'feedback': feedback}), content_type='application/json')
            
    request.session['exercise'] = exercise.dic
    return HttpResponse(exercise.render(request, feedback, success))
    
    
def not_authenticated(request):
    logout(request)
    return render(request, 'playexo/not_authenticated.html', {})
    
