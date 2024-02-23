from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.signing import BadSignature
from django.core.paginator import Paginator
from django.db.models import Q

from .models import AdvUser, SubRubric, Es
from .forms import ProfileEditForms, RegisterForm, SearchForm, EsForm, AIFormSet
from .utilities import signer


@login_required
def profile(request):
    ess = Es.objects.filter(author=request.user.pk)
    context = {'ess': ess}
    return render(request, 'main/profile.html', context)


class ESLoginView(LoginView):
    template_name = 'main/login.html'


class ESLogoutView(LogoutView):
    pass


class RegisterView(CreateView):
    model = AdvUser
    template_name = 'main/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('main:register_done')


class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'


class ProfileEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'main/profile_edit.html'
    form_class = ProfileEditForms
    success_url = reverse_lazy('main:profile')
    success_message = 'Данные пользователя изменены'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)

class PassportEditView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'main/password_edit.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Пароль пользователя изменен'


class ProfileDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'main/profile_delete.html'
    success_url = reverse_lazy('main/index')
    success_message = 'Пользователь удален'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'main/activation_failed.html')
    user = get_object_or_404(AdvUser, username=username)
    if user.is_activated:
        template = 'main/activation_done_earlier.html'
    else:
        template = 'main/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)

def index(request):
    ess = Es.objects.filter(is_active=True).select_related('rubric')[:10]
    context = {'ess': ess}
    return render(request, 'main/index.html', context)

def other_page(request, page):
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


def rubric_ess(request, pk):
    rubric = get_object_or_404(SubRubric, pk=pk)
    ess = Es.objects.filter(is_active=True, rubric=pk)
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        ess = ess.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(ess, 2)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'rubric': rubric, 'page': page, 'ess': page.object_list,
               'form': form}
    return render(request, 'main/rubric_ess.html', context)


def es_detail(request, rubric_pk, pk):
    es = get_object_or_404(Es, pk=pk)
    ais = es.additionalimage_set.all()
    context = {'es': es, 'ais': ais}
    return render(request, 'main/es_detail.html', context)


@login_required
def profile_es_detail(request, rubric_pk, pk):
    es = get_object_or_404(Es, pk=pk)
    ais = es.additionalimage_set.all()
    context = {'es': es, 'ais': ais}
    return render(request, 'main/profile_es_detail.html', context)


@login_required
def profile_es_add(request):
    if request.method == 'POST':
        form = EsForm(request.POST, request.FILES)
        if form.is_valid():
            es = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=es)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS,
                                     'Позиция добавлена')
                return redirect('main:profile')
    else:
        form = EsForm(initial={'author': request.user.pk})
        formset = AIFormSet()
        context = {'form': form, 'formset': formset}
        return render(request, 'main/profile_es_add.html', context)


@login_required
def profile_es_edit(request, pk):
    es = get_object_or_404(Es, pk=pk)
    if request.method == 'POST':
        form = EsForm(request.POST, request.FILES, instance=es)
        if form.is_valid():
            es = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=es)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS,
                                     'Позиция исправлена')
                return redirect('main:profile')
    else:
        form = EsForm(instance=es)
        formset = AIFormSet(instance=es)
    context = {'form': form, 'formset': formset}
    return render(request, 'main/profile_es_edit.html', context)

@login_required
def profile_es_delete(request, pk):
    es = get_object_or_404(Es, pk=pk)
    if request.method == 'POST':
        es.delete()
        messages.add_message(request, messages.SUCCESS, 'Позиция удалена')
        return redirect('main:profile')
    else:
        context = {'es': es}
        return render(request, 'main/profile_es_delete.html', context)