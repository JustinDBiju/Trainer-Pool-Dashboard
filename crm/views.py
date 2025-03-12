from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Trainer, TrainerData
from .forms import TrainerDataForm, TrainerProfileForm
from .sheets_service import fetch_google_sheets_data  # ✅ Corrected function name
from collections import defaultdict

# ✅ LOGIN VIEW
def login_view(request):
    login_type = request.GET.get("type", "")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user_type = request.POST.get("user_type")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if user_type == "admin" and user.is_superuser:
                return redirect("admin_dashboard")
            elif user_type == "trainer":
                if Trainer.objects.filter(user=user).exists():
                    return redirect("trainer_dashboard")
                else:
                    logout(request)
                    return render(request, "crm/trainer_login.html", {"error": "Not a registered trainer"})

        return render(request, "crm/login.html", {"error": "Invalid credentials"})

    return render(request, f"crm/{login_type}_login.html" if login_type in ["admin", "trainer"] else "crm/login.html")


# ✅ TRAINER SIGNUP
def trainer_signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, "crm/trainer_signup.html", {"error": "Passwords do not match"})

        if User.objects.filter(username=username).exists():
            return render(request, "crm/trainer_signup.html", {"error": "Username already exists"})

        user = User.objects.create_user(username=username, password=password)
        Trainer.objects.create(user=user)

        return redirect(f"{reverse('login')}?type=trainer")

    return render(request, "crm/trainer_signup.html")


# ✅ ADMIN DASHBOARD
from collections import defaultdict

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect("login")

    section = request.GET.get("section", "trainer_list")

    # Fetch all trainers
    trainers = Trainer.objects.all()

    # Fetch self-evaluation data for each trainer
    trainer_data_list = []
    for trainer in trainers:
        latest_data = TrainerData.objects.filter(trainer=trainer).order_by("-date_submitted").first()
        self_evaluation_score = latest_data.calculate_score() if latest_data else 0

        trainer_data_list.append({
            "trainer": trainer,
            "self_evaluation_score": self_evaluation_score,
            "classes_taken": latest_data.classes_taken if latest_data else 0,
            "workshops": latest_data.workshops if latest_data else 0,
            "students_participated": latest_data.students_participated if latest_data else 0,
            "students_won": latest_data.students_won if latest_data else 0,
        })

    # Fetch student feedback data
    feedback_data = []
    if section in ["students_feedback", "trainers_average", "leaderboard"]:
        try:
            feedback_data = fetch_google_sheets_data()
            print("✅ Fetched Feedback Data:", feedback_data)  # Debugging
        except Exception as e:
            print(f"❌ Error fetching Google Sheets data: {e}")
            feedback_data = []

    # Calculate average points from student feedback
    trainer_feedback_data = defaultdict(lambda: {"total_points": 0, "count": 0})
    for feedback in feedback_data:
        trainer_name = feedback.get("Trainer_Name", "")
        trainer_points = feedback.get("Trainers_Point", "0")

        try:
            trainer_points = float(trainer_points)  # Convert to float
        except ValueError:
            trainer_points = 0  # Default to 0 if conversion fails

        trainer_feedback_data[trainer_name]["total_points"] += trainer_points
        trainer_feedback_data[trainer_name]["count"] += 1

    # Compute the average points for each trainer
    avg_points_list = [
        {
            "Trainer_Name": trainer,
            "Average_Points": round(data["total_points"] / data["count"], 2) if data["count"] > 0 else 0,
        }
        for trainer, data in trainer_feedback_data.items()
    ]

    # Combine self-evaluation and feedback scores for the leaderboard
    leaderboard_data = []
    for trainer in trainer_data_list:
        trainer_name = trainer["trainer"].user.username
        self_evaluation_score = trainer["self_evaluation_score"]
        feedback_score = next(
            (item["Average_Points"] for item in avg_points_list if item["Trainer_Name"] == trainer_name),
            0  # Default to 0 if no feedback data is found
        )

        combined_score = self_evaluation_score + feedback_score

        leaderboard_data.append({
            "trainer": trainer["trainer"],
            "self_evaluation_score": self_evaluation_score,
            "feedback_score": feedback_score,
            "combined_score": combined_score,
        })

    # Sort leaderboard data by combined score (descending)
    leaderboard_data.sort(key=lambda x: x["combined_score"], reverse=True)

    return render(request, "crm/admin_dashboard.html", {
        "trainers": trainers,
        "trainer_data_list": trainer_data_list,
        "feedback_list": feedback_data,  # Pass feedback data
        "avg_points_list": avg_points_list,  # Pass average points data
        "leaderboard_data": leaderboard_data,  # Pass leaderboard data
        "section": section,
    })
# ✅ TRAINER DETAIL VIEW
@login_required
def trainer_detail(request, trainer_id):
    trainer = get_object_or_404(Trainer, id=trainer_id)
    return render(request, "crm/trainer_detail.html", {"trainer": trainer})


# ✅ TRAINER DASHBOARD
@login_required
def trainer_dashboard(request):
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        return redirect("login")

    section = request.GET.get("section", "score_entry")
    latest_data = TrainerData.objects.filter(trainer=trainer).order_by("-date_submitted").first()
    latest_score = latest_data.calculate_score() if latest_data else 0

    form = TrainerDataForm(request.POST) if request.method == "POST" and section == "score_entry" else TrainerDataForm()

    if request.method == "POST" and form.is_valid():
        data = form.save(commit=False)
        data.trainer = trainer
        data.save()
        return redirect("trainer_dashboard")

    return render(request, "crm/trainer_dashboard.html", {
        "form": form,
        "latest_score": latest_score,
        "trainer": trainer,
        "section": section,
    })


# ✅ EDIT TRAINER PROFILE
@login_required
def edit_profile(request):
    try:
        trainer = Trainer.objects.get(user=request.user)
    except Trainer.DoesNotExist:
        return redirect("login")

    form = TrainerProfileForm(request.POST, instance=trainer) if request.method == "POST" else TrainerProfileForm(instance=trainer)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("trainer_dashboard")

    return render(request, "crm/edit_profile.html", {"form": form})


# ✅ EDIT TRAINER (ADMIN)
@login_required
def edit_trainer(request, trainer_id):
    trainer = get_object_or_404(Trainer, id=trainer_id)

    if request.method == "POST":
        trainer.user.email = request.POST.get("email")
        trainer.user.save()
        return redirect("admin_dashboard")

    return render(request, "crm/edit_trainer.html", {"trainer": trainer})


# ✅ DELETE TRAINER (ADMIN)
@login_required
def delete_trainer(request, trainer_id):
    trainer = get_object_or_404(Trainer, id=trainer_id)

    if request.method == "POST":
        trainer.user.delete()
        return redirect("admin_dashboard")

    return render(request, "crm/delete_trainer.html", {"trainer": trainer})


# ✅ LOGOUT VIEW
def logout_view(request):
    logout(request)
    return redirect("login")


# ✅ GOOGLE SHEETS FEEDBACK VIEW
@login_required
def feedback_list(request):
    try:
        feedback_data = fetch_google_sheets_data()
    except Exception as e:
        feedback_data = []
        print(f"Error fetching Google Sheets data: {e}")

    return render(request, "crm/feedback.html", {"feedback_data": feedback_data})


# ✅ STUDENTS FEEDBACK
@login_required
def students_feedback(request):
    if not request.user.is_superuser:
        return redirect("login")

    feedback_data = fetch_google_sheets_data()
    print("✅ Debugging Feedback Data:", feedback_data)  # Debugging

    return render(request, "crm/students_feedback.html", {
        "feedback_list": feedback_data,  # Ensure this key matches the template
    })


# ✅ TRAINERS AVERAGE POINTS
from django.shortcuts import render
from collections import defaultdict

@login_required
def trainers_average_points(request):
    if not request.user.is_superuser:
        return redirect("login")

    # Fetch Google Sheets data
    try:
        feedback_data = fetch_google_sheets_data()
        print("✅ Raw Feedback Data from Google Sheets:", feedback_data)  # Debugging
    except Exception as e:
        print(f"❌ Error fetching Google Sheets data: {e}")
        feedback_data = []

    if not feedback_data:
        return render(request, "crm/trainers_average.html", {
            "avg_points_list": [],
            "error": "No feedback data available."
        })

    # Verify expected keys
    for feedback in feedback_data:
        print("🔹 Feedback Entry:", feedback)

    # Calculate average points per trainer
    trainer_data = defaultdict(lambda: {"total_points": 0, "count": 0})

    for feedback in feedback_data:
        trainer_name = feedback.get("Trainer Name", "").strip()
        trainer_points = feedback.get("Trainers Point", "").strip()

        if trainer_name and trainer_points:
            try:
                trainer_points = float(trainer_points)
                trainer_data[trainer_name]["total_points"] += trainer_points
                trainer_data[trainer_name]["count"] += 1
            except ValueError:
                print(f"⚠️ Invalid trainer points: {trainer_points}")

    # Convert to list format for template
    avg_points_list = [
        {
            "Trainer_Name": trainer,
            "Average_Points": round(data["total_points"] / data["count"], 2) if data["count"] > 0 else 0,
        }
        for trainer, data in trainer_data.items()
    ]

    print("✅ Processed Trainer Scores:", avg_points_list)  # Debugging

    return render(request, "crm/trainers_average.html", {
        "avg_points_list": avg_points_list
    })
