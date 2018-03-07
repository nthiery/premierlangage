# coding: utf-8

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from gitload.models import Strategy, PLTP, PL


class Activity(models.Model):
    id = models.CharField(max_length=30, null=False, default=0)
    name = models.CharField(max_length=200, primary_key=True, null=False)
    strategy = models.ForeignKey(Strategy, null=False)
    pltp = models.ForeignKey(PLTP, null=False)

    def __str__(self):
        return self.name



class Answer(models.Model):
    STARTED = 'ST'
    FAILED = 'FA'
    SUCCEEDED = 'SU'
    NOT_STARTED = 'NS'
    STATE = (
        (STARTED, 'Commencé'),
        (FAILED, 'Echoué'),
        (SUCCEEDED, 'Réussi'),
        (NOT_STARTED, 'Non Commencé'),
    )
    
    value = models.TextField(max_length = 50000, null = False)
    user = models.ForeignKey(User, null = False)
    pl = models.ForeignKey(PL, null = False)
    seed = models.CharField(max_length=50, null=True)
    date = models.DateTimeField(null = False, default=timezone.now)
    state = models.CharField(max_length=2, choices=STATE, null = False, default=STARTED)
    
    
    @staticmethod
    def pl_state(pl, user):
        """
            Return the state of the answer associated to this pl and user following these rules in this order:
                - If no answer exists: Answer.NOT_STARTED
                - If at least one good answer exists: Answer.SUCCEEDED
                - If at least one bad answer exists: Answer.FAILED
                - Otherwise: Answer.STARTED
            TL,DR: Success prevail over fail which prevail over save/reload.
        """
        
        answers = Answer.objects.filter(user=user, pl=pl)
        if not answers:
            return Answer.NOT_STARTED
        
        failed = False
        for item in answers:
            if item.state == Answer.SUCCEEDED:
                return Answer.SUCCEEDED
            if item.state == Answer.FAILED and not failed:
                failed = True
        
        if failed:
            return Answer.FAILED
        return Answer.STARTED
    
    
    @staticmethod
    def pltp_state(pltp, user):
        """ Return a list of tuples (pl_sha1, state) where state follow pl_state() rules. """
        
        lst = list()
        for pl in pltp.pl.all():
            lst.append((pl.sha1, Answer.pl_state(pl, user)))
            
        return lst
    
    
    @staticmethod
    def pltp_summary(pltp, user):
        """
            Give information about the PLTP's completion of this user as a dict of 3 tuples:
            {
                'succeeded': (% succeeded, nbr succeeded),
                'failed': (% failed, nbr failed),
                'started: (% started, nbr started),
                'not_started': (% not started, nbr not started),
            }
        """
    
        succeeded = 0
        failed = 0
        started = 0
        not_started = 0
        for pl, state in Answer.pltp_state(pltp, user):
            if state == Answer.SUCCEEDED:
                succeeded += 1
            elif state == Answer.FAILED:
                failed += 1 
            elif state == Answer.STARTED:
                started += 1
            else:
                not_started += 1
                        
        nb_pl = succeeded + failed + started + not_started
        if not nb_pl:
            nb_pl = 1
        state = {
            'succeeded':    (str(succeeded*100/nb_pl), str(succeeded)),
            'failed':       (str(failed*100/nb_pl), str(failed)),
            'started':      (str(started*100/nb_pl), str(started)),
            'not_started':  (str(not_started*100/nb_pl), str(not_started)),
        }
        
        return state
    
    
    @staticmethod
    def course_state(course):
        """ 
            Return every pltp state of every user of this course as a list of dicts:
            {
                'user_id': id,
                'pltp_sha1' sha1,
                'pl': list(pl_sha1, state)
            }
            where 'state' follow pl_state() rules.
        """
        
        lst = list()
        for user in course.user:
            dct = dict()
            dct['user_id'] = user.id
            for activity in course:
                dct['pltp_sha1'] = activity.pltp.sha1
                dct['pl'] = Answer.pltp_state(activity.pltp, user)
            lst.append(dct)
        
        return lst
    
    
    @staticmethod
    def user_course_summary(course, user):
        """
            Give information about the completion of every PL of this user in course as a dict of 3 tuples:
            {
                'succeeded': (% succeeded, nbr succeeded),
                'failed': (% failed, nbr failed),
                'started: (% started, nbr started),
                'not_started': (% not started, nbr not started),
            }
            where finished pl are either failed or succeeded pl.
        """
    
        succeeded = 0
        failed = 0
        started = 0
        not_started = 0
        for activity in course.activity.all():
            for pl, state in Answer.pltp_state(activity.pltp, user):
                if state == Answer.SUCCEEDED:
                    succeeded += 1
                elif state == Answer.FAILED:
                    failed += 1
                elif state == Answer.STARTED:
                    started += 1
                else:
                    not_started += 1
                        
        nb_pl = succeeded + failed + started + not_started
        if not nb_pl:
            nb_pl = 1
        state = {
            'succeeded':    (str(succeeded*100/nb_pl), str(succeeded)),
            'failed':       (str(failed*100/nb_pl), str(failed)),
            'started':      (str(started*100/nb_pl), str(started)),
            'not_started':  (str(not_started*100/nb_pl), str(not_started)),
        }
        
        return state
