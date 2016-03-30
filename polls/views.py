from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.http import Http404
from django.core.urlresolvers import reverse
from django.template import loader
from .models import Question, Choice
from django.views import generic
from django.core import serializers
from django.utils import timezone
import logging
from django.db.models import F

class IndexView(generic.ListView):
	template_name = 'polls/index.html'
	context_object_name = 'latest_question_list'

	def get_queryset(self):
		"""Return the last five published question."""
		return Question.objects.order_by('-pub_date')[:5]

class DetailView(generic.DetailView):
	model = Question
	template_name = 'polls/detail.html'

class ResultsView(generic.DetailView):
	model = Question
	template_name = 'polls/results.html'

# def index(request):
# 	latest_question_list = Question.objects.order_by('-pub_date')[:5]
# 	template = loader.get_template('polls/index.html')
# 	context = {
# 		'latest_question_list' : latest_question_list,
# 	}
# 	return HttpResponse(template.render(context, request))

# def detail(request, question_id):
# 	question = get_object_or_404(Question, pk=question_id)
# 	context = { 'question' : question }
# 	return render(request, 'polls/detail.html', context)

# def results(request, question_id):
# 	question = get_object_or_404(Question, pk=question_id)
# 	context = { 'question' : question }
# 	return render(request, 'polls/results.html', context)

def vote(request, question_id):
	question = get_object_or_404(Question, pk=question_id)
	try:
		selected_choice = question.choice_set.get(pk=request.POST['choice'])
	except (KeyError, Choice.DoesNotExist):
		context = {
			'question':question,
			'error_message': "You didn't select a choice."
		}
		return render(request, 'polls/detail.html', context)
	else:
		# selected_choice.votes += 1
		selected_choice.votes = F('votes') + 1
		selected_choice.save()
		return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

class QuestionsView(generic.View):
	def get(self, request, *args, **kwargs):
		questions = Question.objects.all()
		json_data = serializers.serialize('json', questions)
		return HttpResponse(json_data)

class QuestionView(generic.View):

	def post(self, request, *args, **kwargs):
		
		logger = logging.getLogger(__name__)
		json_data = {}

		question_text = request.POST.get('question_text', '')

		if(question_text):
			q = Question(question_text=question_text, pub_date=timezone.now())
			# q.save()
			json_data['id'] = q.id
			json_data['question_text'] = q.question_text
			json_data['pub_date'] = q.pub_date
			json_data['status'] = True
			json_data['message'] = 'Data saved successfully'
		else:
			json_data['status'] = False
			json_data['message'] = 'Incorrect form parameters'
		
		logger.debug(json_data['message'])
		return JsonResponse(json_data)
