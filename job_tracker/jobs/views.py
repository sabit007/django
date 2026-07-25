from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import JobApplicationForm
from .models import JobApplication


def home(request):
    """
    Dashboard: total count + per-status counts.
    We build a list of dicts so the template can loop over it instead of
    hardcoding 5 separate variables.
    """
    applications = JobApplication.objects.all()

    status_counts = []
    for value, label in JobApplication.STATUS_CHOICES:
        status_counts.append({
            "label": label,
            "count": applications.filter(status=value).count(),
        })

    context = {
        "total": applications.count(),
        "status_counts": status_counts,
    }
    return render(request, "home.html", context)


def job_list(request):
    applications = JobApplication.objects.all()
    return render(request, "jobs/list.html", {"applications": applications})


def job_detail(request, pk):
    application = get_object_or_404(JobApplication, pk=pk)
    return render(request, "jobs/detail.html", {"application": application})


def job_create(request):
    if request.method == "POST":
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Job application added successfully.")
            return redirect("job_list")
        # if invalid, fall through and re-render the same form with errors attached
    else:
        form = JobApplicationForm()

    return render(request, "jobs/create.html", {"form": form})


def job_update(request, pk):
    application = get_object_or_404(JobApplication, pk=pk)
    if request.method == "POST":
        form = JobApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, "Job application updated successfully.")
            return redirect("job_list")
    else:
        form = JobApplicationForm(instance=application)

    return render(request, "jobs/update.html", {"form": form, "application": application})


def job_delete(request, pk):
    application = get_object_or_404(JobApplication, pk=pk)
    if request.method == "POST":
        # Only actually delete on POST (i.e. after the user confirms).
        # A GET request just shows the confirmation page below.
        application.delete()
        messages.success(request, "Job application deleted successfully.")
        return redirect("job_list")

    return render(request, "jobs/delete.html", {"application": application})
