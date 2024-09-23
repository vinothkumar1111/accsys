from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate ,logout as auth_logout # Import login and rename it to auth_login
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import re
from django.utils.timesince import timesince
from django.http import JsonResponse,HttpResponse
from django.utils.dateformat import format
from django.db.models import Max
from django.utils.timezone import localtime
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt


def createuserpage(req):
    return render(req,"createuserpage.html")


def create_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        
        # Create the user
        User.objects.create_user(username=username, email=email, password=password)
        print("user saved")

        
        
        # Redirect to the admin interface
        return redirect('admin:index')  # Redirects to the Django admin home

    return render(request, 'create_user.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        mobile = request.POST['mobile']

        password = request.POST['password']
        password2 = request.POST['cpassword']

        
         # Initialize the response dictionary
        response = {'status': 'success'}

            # Email validation regex to check format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', email):
            response = {'status': 'error', 'message': 'Invalid email format. Email must end with @gmail.com'}
            return JsonResponse(response)
        
          # Check if mobile already exists
        if UserProfile.objects.filter(mobile=mobile).exists():
            response = {'status': 'error', 'message': 'Mobile number already in use'}
            return JsonResponse(response)
        

        # Check if mobile number is valid (e.g., length and numeric)
        if not re.match(r'^\d{10}$', mobile):
            response = {'status': 'error', 'message': 'Invalid mobile number. Must be 10 digits.'}
            return JsonResponse(response)



        # Check if passwords match
        if password != password2:
            response = {'status': 'error', 'message': 'Passwords do not match'}
            return JsonResponse(response)
        
        mobile = int(mobile)


        # Password validation
        # if len(password) < 8:
        #     response = {'status': 'error', 'message': 'Password must be at least 8 characters long'}
        #     return JsonResponse(response)

        # if not re.search(r'[A-Z]', password):
        #     response = {'status': 'error', 'message': 'Password must contain at least 1 uppercase letter'}
        #     return JsonResponse(response)

        # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        #     response = {'status': 'error', 'message': 'Password must contain at least 1 special character'}
        #     return JsonResponse(response)

        # if not re.search(r'[0-9]', password):
        #     response = {'status': 'error', 'message': 'Password must contain at least 1 digit'}
        #     return JsonResponse(response)

        # if not re.search(r'[a-z]', password):
        #     response = {'status': 'error', 'message': 'Password must contain at least 1 lowercase letter'}
        #     return JsonResponse(response)

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            response = {'status': 'error', 'message': 'Email already in use'}
            return JsonResponse(response)


        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()


        # Create user profile with mobile number
        user_profile = UserProfile.objects.create(user=user, mobile=mobile)
        user_profile.save()


         # Log the user out to ensure no session persists after registration
        auth_logout(request)


        # Return JSON response with success status and the login URL
        response = {
            'status': 'success',
            'message': 'Registration successful!',
            'redirect_url': reverse('login')  # Pass the login URL
        }

        return JsonResponse(response)

    return render(request, 'register.html')


    



def user_login(request):
    # Check if the user is already authenticated
    if request.user.is_authenticated:
        return redirect('members')  # Redirect to members page if user is logged in

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            # Check if a user with the entered email exists
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Return an error response if email does not exist
            return JsonResponse({'status': 'error', 'message': 'No User Found'})

        # Authenticate using the username linked to the email
        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            # If authentication is successful
            auth_login(request, user)
            request.session['login_success'] = True
            return JsonResponse({'status': 'success', 'redirect_url': reverse('todlistpage')})
        else:
            # Return an error response if the password is incorrect
            return JsonResponse({'status': 'error', 'message': 'Invalid login credentials'})
    
    return render(request, 'login.html')




@login_required
def members(request):
    print("member fun")

 
    if request.user.is_authenticated:
        print("f true")
        username = request.user.username
        return render(request, 'all_leads.html', {'username': username})
    else:
        print("if fail")
        return redirect('login')


def user_logout(request):
   if request.method == 'POST':  # Only allow logout on POST request
        auth_logout(request)
        return redirect('login')  # Redirect to login after logout
   return redirect('members')  # If not logged out, redirect to members



# def forgotpassword(request):
#     return render(request,"forgotpassword.html")




def forms(request):
    return render(request,"forms.html")

@login_required
def tables(request):
    return render(request,"tables-data.html")

def chartaccount(req):
    return render(req,"ca_accounts.html")


def assets(req):
    return render(req,"assets.html")


def currentassets(req):
    return render(req,"currentassets.html")



def fdwithbank(req):
    return render(req,"fdwithbank.html")




def todolist(request):
    print("todo")
    return render(request,"todolist.html")



def custom_admin(request):
    return render(request,"custom_admin.html")




def components(request):
    return render(request,"components.html")


def todlistpage(request):
    print("tolistpage fun")
    # Retrieve all projects, ordered by creation time (most recent first)
    projects = Project.objects.filter(user=request.user).order_by('-created_at')
    status_choices = Project.STATUS_CHOICES

    return render(request, 'todopage.html', {'projects': projects, 'status_choices': status_choices})



@require_POST
def update_status(request, project_id):
    status_value = request.POST.get('status')
    project = get_object_or_404(Project, id=project_id)
    if status_value in dict(Project.STATUS_CHOICES).keys():  # Validate status
        project.status = status_value
        project.save()
    return redirect('todlistpage') # Redirect to the project list page after saving as needed




def todopgt(request):
     print("pgt function")
     if request.method == 'POST':
        projectname = request.POST.get('projectname')
        projectdate = request.POST.get('projectdate')
        projectpriority = request.POST.get('projectpriority')


        print(projectname)
        if projectname:     
            print("pgt if")
            # Create and save the project
            Project.objects.create(
                projectname=projectname,
                to_date=projectdate,
                priority=projectpriority,
                user=request.user,  # Assign the currently logged-in user
                assigned_by=request.user  # Assign the currently logged-in user as the creator

            )
            print("project saved")
            return redirect('todlistpage')  # Redirect to the project list page after saving
     return render(request,"todolist.html")



@login_required
def projects(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Retrieve all tasks related to the project and categorize them by status
    todo_tasks = project.details.filter(status='todo')
    in_progress_tasks = project.details.filter(status='in_progress')
    done_tasks = project.details.filter(status='done')

    # Combine project details and comments into one list (if needed for something else)
    combined_list = list(todo_tasks) + list(in_progress_tasks) + list(done_tasks)
    combined_list.sort(key=lambda x: x.created_at, reverse=True)

    # Calculate time ago for each task
    for item in combined_list:
        item.time_ago = timesince(item.created_at).split(', ')[-1]

    # Pass the categorized tasks to the template
    return render(request, 'todolist.html', {
        'project': project,
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'done_tasks': done_tasks,
    })

def delete_project(request, project_id):
    print("Arun pgt function")
    project = get_object_or_404(Project, id=project_id)
    
    deleted_at_utc = timezone.now()  # Get the current time in UTC
    deleted_at_local = timezone.localtime(deleted_at_utc)


    archived_project = ArchivedProject(
        projectname=project.projectname,
        # taskname=project.taskname,
        priority=project.priority,
        from_date=project.from_date,
        to_date=project.to_date,
        created_at=project.created_at,
        updated_at=project.updated_at,
        deleted_at=deleted_at_local,  # Set the deletion date and time
  # Set the deletion date and time

        user=project.user,
        assigned_by=project.assigned_by,
        status=project.status,
    )
    archived_project.save()
    print(f"Project {project_id} deleted at {deleted_at_local.strftime('%Y-%m-%d %H:%M:%S')}")
    print("Deleted Projet Saved")

    # Delete the original project
    project.delete()
    
    return redirect('todlistpage')

def create_issue(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        issuename = request.POST.get('issuename')
        print(issuename)
        if issuename:
            print("if",issuename)
            Issue.objects.create(project=project, title=issuename, description=issuename)
            return redirect('projects', project_id=project.id)
    
    return render(request, 'todolist.html', {'project': project})




def edit_issue(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    
    if request.method == 'POST':
        issue.description = request.POST.get('description')
        issue.save()
        
        return redirect('projects', project_id=issue.project.id)  # Redirect to the project's issues view

    return render(request, 'edit_issue.html', {'issue': issue})


@require_POST
def delete_issue(request, issue_id):
    print("print delete issue")
    issue = get_object_or_404(Issue, id=issue_id)
    project_id = issue.project.id  # Capture the project ID before deleting
    issue.delete()
    return redirect('projects', project_id=project_id)  # Redirect to the projects view after deletion


def create_todolist(request, task_id):
    print("Entered create_todolist view")
    task = get_object_or_404(Task, id=task_id)  # Get task by ID

    project = task.project  # Access the project via the task

    if request.method == 'POST':
        print("POST method detected")
        description = request.POST.get('description')
        comments = request.POST.get('comments')

        # print("this is status",status)

        
        # Get the list of attached files
        attached_files = request.FILES.getlist('attached_file[]')

        # # Check if total file size exceeds 25 MB
        # max_file_size = 25 * 1024 * 1024  # 25 MB in bytes
        # total_file_size = sum(file.size for file in attached_files)

       
       

        print(f"Description: {description}")
        print(f"Comments: {comments}")
        print(f"Attached Files: {attached_files}")
        print(f"Task Status: {task.status}")  # Using the task's status

        
        if attached_files:
            for file in attached_files:
                print(f"Processing file: {file.name}")

        if description:
            todolist = Todolist(
                project=project,
                description=description,
                comments=comments,
                status=task.status,  # Use the task's status for the todo list

                # status=status,

                user=request.user
            )
            todolist.save()

            print("data saved ")

            for attached_file in attached_files:
                TodolistFile.objects.create(
                    todolist=todolist,
                    attached_file=attached_file
                )
                print(f"Saved file: {attached_file.name}")

            print("New data and files saved successfully")
            return redirect('todo_card_detail_view', task_id=task.id)
        else:
            print("No description provided")

    return render(request, 'todolist.html', {'project': project})


def fetch_all_data(request):    
    print("Fetching all comments")

    # Fetch all comments from the Todolist model
    todotasks = Todolist.objects.all()

    # Serialize only the comment data
    data = []
    for task in todotasks:
        data.append({
            'id': task.id,
            'comment': task.comments,  # Fetching the comments
            'created_at': task.created_at.isoformat(),  # Ensure ISO 8601 format

        })

    return JsonResponse(data, safe=False)
    

@login_required
def user_list(request):
    if request.user.groups.filter(name__in=["Admin", "Superadmin"]).exists():
            users = User.objects.exclude(is_superuser=True).exclude(id=request.user.id)
            return render(request, 'user_list.html', {'users': users})
    else:
        # Redirect non-superusers or show a permission denied message
            return JsonResponse({'error': 'Permission Denied'}, status=403)
    

@login_required
def delete_user(request, user_id):
    if request.user.is_superuser:
        user = get_object_or_404(User, id=user_id)
        
        # Archive the user details before deletion
        ArchivedUser.objects.create(
            username=user.username,
            email=user.email,
            date_joined=user.date_joined
        )
        
        # Delete the user
        user.delete()
        
        return JsonResponse({'success': 'User deleted successfully.'})
    else:
        return JsonResponse({'error': 'Permission Denied'}, status=403)


def create_project(request, user_id):
    print("create pgt function")
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Get form data from POST request
        projectname = request.POST.get('projectname')
        # taskname = request.POST.get('taskname')
        priority = request.POST.get('priority')
        from_date = request.POST.get('fromdate')
        to_date = request.POST.get('todate')

        try:
            print("try block")
            # Create and save new Project instance, linking it to the user
            project = Project(
                projectname=projectname,
                # taskname=taskname,
                priority=priority,
                from_date=from_date,
                to_date=to_date,
                user=user,  # Associate the project with the selected user
                assigned_by=request.user  # Set the user creating the project

            )
            project.save()
            print(" project data saved")

            # Redirect back to the user's project page
            return redirect('user_project', user_id=user.id)

        except Exception as e:
            print("except")
            return HttpResponse(f"An error occurred: {e}", status=500)

    # If GET request, just render the page with the user's existing projects
    projects = Project.objects.filter(user=user)
    return render(request, 'userproject.html', {'projects': projects, 'user': user})


def user_project(request, user_id):
    print("user_project function")
    # Get the user by ID or return 404 if not found
    user = get_object_or_404(User, id=user_id)

    # Get all projects associated with the specific user
    user_projects = Project.objects.filter(user=user).order_by('-created_at')
    print("this is the user_projects",user_projects)
    context = {
        'user': user,  # Pass the selected user
        'projects': user_projects,  # Pass the projects for this user
    }

    return render(request, 'userproject.html', context)






def edit_project(request, project_id):
    print("edit pgt")
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        # if request.user.is_superuser:
            # project.projectname = request.POST.get('projectname')
            # # project.priority = request.POST.get('priority')
            # project.from_date = request.POST.get('fromdate')
            # # print(project.taskname)
            # project.to_date = request.POST.get('todate')
        # else:

        

            project.projectname = request.POST.get('projectname')
            # project.taskname = request.POST.get('taskname')
            project.priority = request.POST.get('priority')
            project.from_date = request.POST.get('fromdate')
            project.to_date = request.POST.get('todate')
        
            project.save()
            # if request.user.is_superuser:
            return redirect('user_project', user_id=project.user.id)  # Assuming the project has a foreign key to User
            # else:
            #     return redirect('user_project', user_id=project.user.id)




    
    return HttpResponse("Invalid request method.", status=400)


@login_required
def assigned_projects_view(request):
    if request.user.is_authenticated:
        # Fetch projects assigned to the currently logged-in user
        projects = Project.objects.filter(user=request.user)
        print(projects,"username")
    else:
        projects = Project.objects.none()  # No projects if not authenticated
        print(projects,"username else")

    context = {
        'projects': projects
    }
    return render(request, 'todopage.html', context)

def update_task_status(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        new_status = request.POST.get('status')

        # Retrieve the task or return error if not found
        task = get_object_or_404(Todolist, id=task_id)

        # Update the task status
        task.status = new_status
        task.save()

        # Respond with a success status
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def task_view(request):
    todotasks = Todolist.objects.filter(status='todo')
    in_progress_tasks = Todolist.objects.filter(status='in_progress')
    done = Todolist.objects.filter(status='done')

    context = {
        'todotask': todotasks,
        'in_progress_tasks': in_progress_tasks,
    }

    return render(request, 'todolist.html', context)


def project_detail(request, project_id):
    print("vinpoth")
    # Get the project by ID or return 404 if not found
    project = get_object_or_404(Project, id=project_id)

    # Get all tasks for the selected project
    project_tasks = Task.objects.filter(project=project).order_by('-from_date')
    
    # Get all projects for the same user (for retaining the full table if needed)
    user_projects = Project.objects.filter(user=project.user).order_by('-created_at')
    
    context = {
        'selected_project': project,  # Pass the selected project
        'projects': user_projects,    # Pass all projects for the user
        'tasks': project_tasks,       # Pass the tasks related to the selected project
    }

    return render(request, 'task_detail.html', context)



def create_task(request, project_id):
    if request.method == "POST":
        # Get the related project by ID
        project = get_object_or_404(Project, id=project_id)

        # Extract form data
        taskname = request.POST.get('taskname')
        priority = request.POST.get('priority')
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')

        # Validate the data and create the task object
        if taskname and priority and fromdate and todate:
            # Create a new task and associate it with the specific project
            task = Task.objects.create(
                project=project,
                user=request.user,  # Assign the current logged-in user to the task

                taskname=taskname,
                priority=priority,
                from_date=fromdate,
                to_date=todate,
            )
            task.save()

            # Success message

            # Redirect to the project detail page after saving the task
            return redirect('project_detail', project_id=project.id)
        else:
            # Error message if fields are not filled
            # messages.error(request, 'Please fill all the fields.')

            # Reload the form with the selected project
            return redirect('project_detail', project_id=project.id)

    # In case of GET request, redirect to project detail page
    return redirect('project_detail', project_id=project_id)



@login_required
def delete_task(request, task_id):
    # Get the task to delete
    task = get_object_or_404(Task, id=task_id)
    deleted_at = localtime(timezone.now())


    # Backup the task details before deleting
    DeletedTask.objects.create(
        taskname=task.taskname,
        priority=task.priority,
        from_date=task.from_date,
        to_date=task.to_date,
        user=task.user,
        project=task.project,
        deleted_at=deleted_at
    )

    # Now delete the task from the Task table
    task.delete()
    deletion_time_formatted = deleted_at.strftime("%d-%m-%Y %H:%M:%S")
    print(deletion_time_formatted,"Deleted time and date")


    # Success message
    # messages.success(request, "Task deleted successfully!")

    # Redirect to the project detail page or task list
    return redirect('project_detail', project_id=task.project.id)


def specific_user_tasks_view(request, project_id):
    # Get the project by its ID
    print("specific task view")
    project = get_object_or_404(Project, id=project_id)
    
    # Get the tasks related to the project
    tasks = Task.objects.filter(project=project)
    
  

    context = {
        'project': project,
        'tasks': tasks,
        # 'task_counts': task_counts,

    }
    
    return render(request, 'specific_user_task.html', context)



def specific_user_task_view_task_mgt(request, project_id, user_id):
    if request.method == 'POST':
        # Retrieve project and user objects
        project = get_object_or_404(Project, id=project_id)
        user = get_object_or_404(User, id=user_id)

        # Get form data
        taskname = request.POST.get('taskname')
        priority = request.POST.get('priority')
        from_date = request.POST.get('fromdate')
        to_date = request.POST.get('todate')

        # Create a new task object
        task = Task(
            taskname=taskname,
            priority=priority,
            from_date=from_date,
            to_date=to_date,
            user=user,
            project=project
        )
        task.save()

        # Display success message and redirect to project page (or wherever you want)
        # messages.success(request, 'Task created successfully.')
        return redirect('specific_user_tasks_view', project_id=project.id)

    else:
        # If it's a GET request, render the form page
        return render(request, 'specific_user_task_form.html')
    


@csrf_exempt  # For handling AJAX request
def delete_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        task.delete()
        return JsonResponse({'message': 'Task deleted successfully'}, status=200)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)
    


# View to update the task
def update_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        
        # Get the updated values from the POST request
        taskname = request.POST.get('taskname')
        priority = request.POST.get('priority')
        from_date = request.POST.get('fromdate')
        to_date = request.POST.get('todate')
        
        # Update the task object with the new data
        task.taskname = taskname
        task.priority = priority
        task.from_date = from_date
        task.to_date = to_date
        
        # Save the updated task to the database
        task.save()

        # Return a JSON response indicating success
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def edit_projects(request, project_id):
    project = get_object_or_404(Project, id=project_id)  # Get the project by ID
    if request.method == 'POST':
        # Get the updated values from the form
        project.projectname = request.POST.get('projectname')
        project.priority = request.POST.get('priority')
        project.from_date = request.POST.get('fromdate')
        project.to_date = request.POST.get('todate')

        # Save the updated project details
        project.save()

        # Redirect to a project list or a specific project page
        return redirect('user_project', user_id=project.user.id)  # Assuming project has a related 'user' field

    return HttpResponse("Invalid request method", status=400)



def todo_card_detail_view(request, task_id):
    # Get the task by its ID
    print("crds")
    task = get_object_or_404(Task, id=task_id)          
    tasks = Task.objects.filter(project=task.project)
    
    # Retrieve the Todolist data associated with the project
    todolist_entries = Todolist.objects.filter(project=task.project)

    
      # Count tasks by status
    task_counts = {
        'todo': tasks.filter(status='Not Started').count(),
        'in_progress': tasks.filter(status='Working').count(),
        'done': tasks.filter(status='Completed').count(),
    }
    
    
    print(task_counts,"counts")
    print(todolist_entries,"todoentry")
    
    context = {
        'task': task,   
        'task_counts': task_counts,  # Add task counts to the context
        'todolist_entries': todolist_entries  # Add Todolist entries to the context


    }
    
    return render(request, 'usercard.html', context)



def card_update_task_status(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        status = request.POST.get('status')
        
        if status in dict(Task.STATUS_CHOICES).keys():
            task.status = status
            task.save()

        return redirect('specific_user_tasks_view', project_id=task.project.id)
