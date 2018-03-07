#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Python [Version]
#
#  Author: Coumes Quentin     Mail: qcoumes@etud.u-pem.fr
#  Created: 2017-07-03
#  Last Modified: 2017-07-03

import json

from django.template import Template, RequestContext
from gitload.models import PLTP
from playexo.models import Answer
from classmanagement.models import PLUser

default_load = '{% load bootstrap3 %}{% load static %}{% load markdown_deux_tags %}{% load input_fields_ajax %}{% load json_filter %}'
pls_known = [
    ('form', 'form'), ('css', 'css'), ('pl', 'exo'),
    ('pltp', 'exo'), ('navigation', 'navigation'),
    ('load', 'load'), ('state', 'state'), ('end_script', 'end_script'),
    ('header_script', 'header_script')
]

class Exercise:
    def __init__(self, pl_dic):
        self.dic = pl_dic
    
    def evaluate(self, answer):
        try:
            exec(self.dic['evaluator'], globals())
            dic = self.__build()
            state, feedback = evaluator(answer, dic)
            if (not isinstance(state, bool) and state != None) or (not isinstance(feedback, str)):
                return None, ("/!\ ATTENTION: La fonction d'évaluation de cet exercice est incorrecte, merci de prévenir votre professeur:\n"
                              "Function evaluator() should return a tuple (bool, str).")
            return state, feedback
        except Exception as e:
            return None, ("/!\ ATTENTION: La fonction d'évaluation de cet exercice est incorrecte, merci de prévenir votre professeur:<br>Error - "+str(type(e)).replace("<", "[").replace(">", "]")+": "+str(e))
    
    def __build(self):
        if 'build' in self.dic:
            exec(self.dic['build'], globals())
            return build(self.dic)
        return self.dic
            
    def __get_context(self, request, feedback=None, success=None):
        #Bootstrap class corresponding to every state.
        color = { 
            Answer.SUCCEEDED: "1",
            Answer.FAILED: "2",
            Answer.STARTED: "3",
            Answer.NOT_STARTED: "4",
        }
        
        #Give the right state number for the css class according to user color blindness
        blindness = {
            PLUser.NONE: "",
            PLUser.DEUTERANOPIA: "-deuteranopia",
            PLUser.PROTANOPIA: "-protanopia",
            PLUser.TRITANOPIA: "-tritanopia",
        }

        
        pltp = PLTP.objects.get(sha1=self.dic['pltp_sha1'])
        pl_list = list()
        for item in pltp.pl.all():
            state = Answer.pl_state(item, request.user)

            is_pl=False
            if 'pl_sha1' in self.dic and item.sha1 == self.dic['pl_sha1']:
                if state != Answer.NOT_STARTED:
                    self.dic['student_answer'] = Answer.objects.filter(user=request.user, pl=item).order_by('-date')[0].value
                is_pl = True
            content = json.loads(item.json)
            pl_list.append((item, color[state]+blindness[request.user.pluser.color_blindness], content["title"]))
                
        context = RequestContext(request)
        dic = self.__build()
        context.update(dic)
        context['is_pl'] = is_pl
        context['pl_list'] = pl_list
        
        if success:
            context['success'] = success
        if feedback:
            context['feedback']= feedback
        
        return context
    
    def __get_template(self):
        if 'pl_sha1' in self.dic:
            raw = '{% extends "playexo/default_pl_exo.html" %}'+default_load
            for key, block_name in pls_known:
                if key in self.dic:
                    raw += "{% block "+block_name+" %}"+self.dic[key]+"{% endblock %}"
        else:
            raw = '{% extends "playexo/default_pltp_exo.html" %}'+default_load
        return raw
        
    def render(self, request, feedback=None, success=None):  
        """ Return the rendered template for this PL """
        context = self.__get_context(request, feedback, success)
        template = self.__get_template()
        return Template(template).render(context)
    
    
    
class ExerciseTest(Exercise):
    def __init__(self, pl_dic):
        super().__init__(pl_dic)
    
    def __build(self):
        if 'build' in self.dic:
            exec(self.dic['build'], globals())
            return build(self.dic)
        return self.dic
    
    def __get_template(self): 
        raw = '{% extends "playexo/default_pl_test.html" %}'+default_load
        for key, block_name in pls_known:
            if key in self.dic:
                raw += "{% block "+block_name+" %}"+self.dic[key]+"{% endblock %}"
        return raw
    
    def __get_context(self, request, feedback=None, success=None):
        context = RequestContext(request)
        dic = self.__build()
        context.update(dic)
        if success:
            context['success'] = success
        if feedback:
            context['feedback']= feedback
        return context
        
    def render(self, request, feedback=None, success=None):  
        """ Return the rendered template for this PL """
        context = self.__get_context(request, feedback, success)
        template = self.__get_template()
        return Template(template).render(context)
