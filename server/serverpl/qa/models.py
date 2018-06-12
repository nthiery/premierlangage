from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from django.utils.text import slugify
from django_markdown.models import MarkdownField

from user_profile.models import Profile

from hitcount.models import HitCountMixin

from taggit.managers import TaggableManager



class QAQuestion(models.Model, HitCountMixin):
    slug = models.SlugField(max_length=200)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=10000)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    tags = TaggableManager()
    reward = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    closed = models.BooleanField(default=False)
    positive_votes = models.IntegerField(default=0)
    negative_votes = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)
            try:
                points = settings.QA_SETTINGS['reputation']['CREATE_QUESTION']
            except KeyError:
                points = 0
            self.user.profile.modify_reputation(points)
        self.total_points = self.positive_votes - self.negative_votes
        super(QAQuestion, self).save(*args, **kwargs)
    
    
    def __str__(self):
        return self.title



class QAAnswer(models.Model):
    question = models.ForeignKey(QAQuestion, on_delete=models.CASCADE, related_name="answer_set")
    answer_text = models.CharField(max_length=10000)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    updated = models.DateTimeField('date updated', auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.BooleanField(default=False)
    positive_votes = models.IntegerField(default=0)
    negative_votes = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    
    def save(self, *args, **kwargs):
        try:
            points = settings.QA_SETTINGS['reputation']['CREATE_ANSWER']
        except KeyError:
            points = 0
        
        self.user.profile.modify_reputation(points)
        self.total_points = self.positive_votes - self.negative_votes
        super(QAAnswer, self).save(*args, **kwargs)
    
    
    def __str__(self):  # pragma: no cover
        return self.answer_text
    
    
    class Meta:
        ordering = ['-answer', '-pub_date']



class AnswerVote(models.Model):
    """Model class to contain the votes for the answers."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.BooleanField(default=True)
    answer = models.ForeignKey(QAAnswer, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = (('user', 'answer'),)



class QuestionVote(models.Model):
    """Model class to contain the votes for the questions."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.BooleanField(default=True)
    question = models.ForeignKey(QAQuestion, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = (('user', 'question'),)



class AnswerComment(models.Model):
    """Model class to contain the comments for the answers."""
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.CharField(max_length=250)
    answer = models.ForeignKey(QAAnswer, on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        try:
            points = settings.QA_SETTINGS['reputation']['CREATE_ANSWER_COMMENT']
        except KeyError:
            points = 0

        self.user.profile.modify_reputation(points)
        super(AnswerComment, self).save(*args, **kwargs)



class QuestionComment(models.Model):
    """Model class to contain the comments for the questions."""
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.CharField(max_length=250)
    question = models.ForeignKey(QAQuestion, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        try:
            points = settings.QA_SETTINGS['reputation']['CREATE_QUESTION_COMMENT']
        except KeyError:
            points = 0

        self.user.profile.modify_reputation(points)
        super(QuestionComment, self).save(*args, **kwargs)
