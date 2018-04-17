from django.shortcuts import render,get_object_or_404,redirect
from django.utils import timezone
from blog.models import Post,Comment
from blog.forms import PostForm,CommentForm,SignUpForm,LoginForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.views.generic import (TemplateView,ListView,
                                    DetailView,CreateView,
                                    UpdateView,DeleteView,)

# View for about landing page
class AboutView(TemplateView):
    template_name = 'about.html'

# List view for post list on main landing page shows most recent 6 posts
class PostListView(ListView):
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')

# View that displays all posts not just he most recent
class AllPostListView(ListView):
    model = Post
    template_name = "all_posts.html"


    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')


class PostDetailView(DetailView):
    model = Post


class CreatePostView(LoginRequiredMixin,CreateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post

class PostUpdateView(LoginRequiredMixin,UpdateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post

class PostDeleteView(LoginRequiredMixin,DeleteView):
    model = Post
    success_url = reverse_lazy('post_list')

class DraftlistView(LoginRequiredMixin,ListView):
    login_url = '/login/'
    redirect_field_name = 'post_draft_list.html'
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('created_date')

class signup(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = "signup.html"

class login(CreateView):
    form_class = LoginForm
    success_url = reverse_lazy('post_list')
    template_name = "./registration/login.html"

####################################
####################################

@staff_member_required
def post_publish(request,pk):
    post = get_object_or_404(Post,pk=pk)
    post.publish()
    return redirect('post_detail',pk=pk)

@login_required
def add_comment_to_post(request, pk):
    current_user = request.user
    currentUser = current_user.first_name
    print(currentUser)
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)

            comment.post = post
            comment.author = currentUser
            comment.approve()
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()

        return render(request,'blog/comment_form.html',{'form':form})

@staff_member_required
def comment_approve(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    comment.approve()
    return redirect('post_detail',pk=comment.post.pk)

@staff_member_required
def comment_remove(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail',pk=post_pk)