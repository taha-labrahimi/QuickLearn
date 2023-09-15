from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Professeur, Etudiant,Course,Quiz,Question,Answer
from account.models import Account,DemandeAcces


class AccountAdmin(UserAdmin):
    list_display = ('email', 'username', 'date_joined', 'last_login', 'user_type')
    search_fields = ('email', 'username', 'user_type')
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class EtudiantAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'date_inscription')

class DemandeAccesAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_demande', 'accepte')
    list_filter = ('accepte',)
    actions = ['accept_requests', 'delete_requests']

    def accept_requests(self, request, queryset):
        queryset.update(accepte=True)  
        for demande_acces in queryset:
            demande_acces.accepte = True
            demande_acces.save()
            professeur = Professeur.objects.create(email=demande_acces.user.email, user=demande_acces.user)
            professeur.save()
        queryset.delete()

    accept_requests.short_description = "Accept selected requests"

    def delete_requests(self, request, queryset):
        queryset.delete()

    delete_requests.short_description = "Delete selected requests"

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'quiz', 'display_correct_answer')
    list_filter = ('quiz',)  # Add filters if needed

    def display_correct_answer(self, obj):
        correct_answer = obj.answer_set.filter(is_correct=True).first()
        if correct_answer:
            return f"{correct_answer.response_text}"
        return None

    display_correct_answer.short_description = 'Correct Answer'


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('response_text', 'question', 'quiz', 'is_correct')
    list_filter = ('question__quiz',)  

    def question(self, obj):
        return obj.question.question_text

    def quiz(self, obj):
        return obj.question.quiz

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    inlines = [AnswerInline]

class QuizAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]


admin.site.register(Account,AccountAdmin)
admin.site.register(Professeur)
admin.site.register(Course)
admin.site.register(Etudiant,EtudiantAdmin)
admin.site.register(DemandeAcces, DemandeAccesAdmin)
admin.site.register(Quiz,QuizAdmin)
admin.site.register(Question,QuestionAdmin)
admin.site.register(Answer,AnswerAdmin)
