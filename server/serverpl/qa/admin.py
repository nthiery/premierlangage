from django.contrib import admin
from qa.models import QAAnswer, AnswerComment, AnswerVote, QAQuestion, QuestionComment

admin.site.register(QAQuestion)
admin.site.register(QAAnswer)
admin.site.register(AnswerComment)
admin.site.register(QuestionComment)
admin.site.register(AnswerVote)
