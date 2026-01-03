import json
import os
from datetime import datetime
import streamlit as st
import pandas as pd
from github import Github, GithubException

class DataManager:
    DATA_DIR = "data"
    FILES = {
        "profile": "profile.json",
        "tasks": "tasks.json",
        "health": "health.json",
        "history": "history.json",
        "journal": "journal.json"
    }

    DEFAULT_DATA = {
        "profile": {
            "name": "New User",
            "height": 170.0,
            "current_weight": 70.0,
            "goal_weight": 65.0,
            "calorie_limit": 2000,
            "avatar_config": {"style": "default"}
        },
        "tasks": [],
        "health": [],
        "history": [],
        "journal": []
    }

    def __init__(self):
        # Check if we are in Cloud Mode (Secrets exist)
        self.cloud_mode = False
        self.repo = None
        self.branch = "main"
        
        try:
            if "github" in st.secrets:
                self.cloud_mode = True
                token = st.secrets["github"]["token"]
                repo_name = st.secrets["github"]["repo"]
                self.branch = st.secrets["github"].get("branch", "main")
                
                # Init GitHub
                g = Github(token)
                self.repo = g.get_repo(repo_name)
        except Exception as e:
            # print(f"GitHub Init Failed: {e}")
            pass # Fallback to local
        
        if not self.cloud_mode:
            self._initialize_local_storage()

    def _initialize_local_storage(self):
        """Checks if data directory and files exist. Creates them if not."""
        if not os.path.exists(self.DATA_DIR):
            os.makedirs(self.DATA_DIR)

        for key, filename in self.FILES.items():
            filepath = os.path.join(self.DATA_DIR, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    json.dump(self.DEFAULT_DATA[key], f, indent=4)

    def load_data(self, key):
        """Loads data from either Cloud or Local JSON."""
        if self.cloud_mode:
            return self._load_from_cloud(key)
        else:
            return self._load_from_local(key)

    def save_data(self, key, data):
        """Saves data to either Cloud or Local JSON."""
        if self.cloud_mode:
            self._save_to_cloud(key, data)
        else:
            self._save_to_local(key, data)

    # --- LOCAL HANDLING ---
    def _load_from_local(self, key):
        if key not in self.FILES:
            raise ValueError(f"Invalid data key: {key}")
        filepath = os.path.join(self.DATA_DIR, self.FILES[key])
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.DEFAULT_DATA[key]

    def _save_to_local(self, key, data):
        filepath = os.path.join(self.DATA_DIR, self.FILES[key])
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    # --- CLOUD HANDLING (GitHub) ---
    def _load_from_cloud(self, key):
        file_path = f"data/{self.FILES[key]}"
        try:
            contents = self.repo.get_contents(file_path, ref=self.branch)
            json_str = contents.decoded_content.decode("utf-8")
            return json.loads(json_str)
        except GithubException as e:
            if e.status == 404:
                return self.DEFAULT_DATA[key]
            return self.DEFAULT_DATA[key]
        except Exception:
            return self.DEFAULT_DATA[key]

    def _save_to_cloud(self, key, data):
        file_path = f"data/{self.FILES[key]}"
        json_str = json.dumps(data, indent=4)
        
        try:
            # Try to get existing file to update (we need the SHA)
            try:
                contents = self.repo.get_contents(file_path, ref=self.branch)
                self.repo.update_file(contents.path, f"Update {key}", json_str, contents.sha, branch=self.branch)
            except GithubException as e:
                if e.status == 404:
                    # Create if doesn't exist
                    self.repo.create_file(file_path, f"Init {key}", json_str, branch=self.branch)
        except Exception as e:
            st.error(f"Failed to save to GitHub: {e}")

    # --- EXISTING HELPER METHODS (Unchanged logic, relying on load/save) ---
    def log_action(self, action_type, details):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "details": details
        }
        history = self.load_data("history")
        history.append(entry)
        self.save_data("history", history)

    def add_task(self, task_name, category):
        tasks = self.load_data("tasks")
        new_task = {
            "name": task_name,
            "category": category,
            "status": "Pending",
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "completed_date": None
        }
        tasks.append(new_task)
        self.save_data("tasks", tasks)
        self.log_action("TASK_ADD", f"Added task: {task_name} ({category})")

    def update_task_status(self, task_index, new_status):
        tasks = self.load_data("tasks")
        if 0 <= task_index < len(tasks):
            task = tasks[task_index]
            task["status"] = new_status
            if new_status == "Done":
                task["completed_date"] = datetime.now().strftime("%Y-%m-%d")
            self.save_data("tasks", tasks)

    def archive_completed_tasks(self):
        tasks = self.load_data("tasks")
        active_tasks = []
        completed_tasks = []
        for t in tasks:
            if t.get("status") == "Done":
                completed_tasks.append(t)
            else:
                active_tasks.append(t)
        
        if completed_tasks:
            self.save_data("tasks", active_tasks)
            for t in completed_tasks:
                self.log_action("TASK_COMPLETE", f"Finished: {t['name']}")
            return len(completed_tasks)
        return 0

    def get_daily_health_entry(self, date_str):
        health_data = self.load_data("health")
        for entry in health_data:
            if entry["date"] == date_str:
                return entry
        new_entry = {
            "date": date_str,
            "food_entries": [],
            "workout_completed": False,
            "weight_log": None
        }
        health_data.append(new_entry)
        self.save_data("health", health_data)
        return new_entry

    def update_daily_health_entry(self, date_str, updated_entry):
        health_data = self.load_data("health")
        found = False
        for i, entry in enumerate(health_data):
            if entry["date"] == date_str:
                health_data[i] = updated_entry
                found = True
                break
        if not found:
            health_data.append(updated_entry)
            
        self.save_data("health", health_data)
    
    def add_food_log(self, date_str, food_name, calories):
        entry = self.get_daily_health_entry(date_str)
        entry["food_entries"].append({"name": food_name, "calories": calories})
        self.update_daily_health_entry(date_str, entry)
        self.log_action("FOOD_LOG", f"Ate {food_name} ({calories} kcal)")

    def set_workout_status(self, date_str, status):
        entry = self.get_daily_health_entry(date_str)
        entry["workout_completed"] = status
        self.update_daily_health_entry(date_str, entry)
        action = "Completed workout" if status else "Undo workout"
        self.log_action("WORKOUT_LOG", action)

    def log_weight(self, date_str, weight):
        entry = self.get_daily_health_entry(date_str)
        entry["weight_log"] = weight
        self.update_daily_health_entry(date_str, entry)
        profile = self.load_data("profile")
        profile["current_weight"] = weight
        self.save_data("profile", profile)
        self.log_action("WEIGHT_LOG", f"Logged weight: {weight}kg")

    def get_weight_history(self):
        health_data = self.load_data("health")
        # Ensure health_data is a list (sometimes pandas connection might return empty df as empty list)
        if not isinstance(health_data, list): health_data = []
        
        sorted_data = sorted(health_data, key=lambda x: x["date"])
        history = {}
        for entry in sorted_data:
            if entry.get("weight_log"):
                history[entry["date"]] = entry["weight_log"]
        return history

    def get_monthly_analytics(self, year, month):
        month_str = f"{year}-{month:02d}"
        health_data = self.load_data("health")
        profile = self.load_data("profile")
        cal_limit = profile.get("calorie_limit", 2000)
        
        days_tracked = 0
        days_under_limit = 0
        workouts_count = 0
        daily_cals = {} 
        weights = []
        
        for entry in health_data:
            if entry["date"].startswith(month_str):
                days_tracked += 1
                cals = sum(item["calories"] for item in entry.get("food_entries", []))
                daily_cals[entry["date"]] = cals
                if cals > 0 and cals <= cal_limit:
                    days_under_limit += 1
                if entry.get("workout_completed"):
                    workouts_count += 1
                w = entry.get("weight_log")
                if w:
                    weights.append((entry["date"], w))
        
        weights.sort()
        weight_change = 0.0
        if len(weights) > 1:
            weight_change = weights[-1][1] - weights[0][1]

        tasks = self.load_data("tasks")
        tasks_completed_month = 0
        
        # Check active tasks
        for t in tasks:
            if t.get("status") == "Done":
                if t.get("completed_date", "").startswith(month_str):
                    tasks_completed_month += 1
        
        # Check history
        history = self.load_data("history")
        for entry in history:
            if entry["timestamp"].startswith(month_str):
                if entry["action_type"] == "TASK_COMPLETE":
                    tasks_completed_month += 1
        
        active_pending = len([t for t in tasks if t.get("status") == "Pending"])
        total_relevant = tasks_completed_month + active_pending
        completion_rate = 0.0
        if total_relevant > 0:
            completion_rate = (tasks_completed_month / total_relevant) * 100
            
        return {
            "completion_rate": completion_rate,
            "days_under_limit": days_under_limit,
            "workouts_count": workouts_count,
            "weight_change": weight_change,
            "daily_cals": daily_cals,
            "cal_limit": cal_limit
        }

    def add_journal_entry(self, title, content):
        journal = self.load_data("journal")
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": title,
            "content": content
        }
        journal.append(entry)
        self.save_data("journal", journal)
        self.log_action("JOURNAL_ADD", f"Created entry: {title}")

    def get_journal_entries(self):
        journal = self.load_data("journal")
        if not isinstance(journal, list): journal = []
        return sorted(journal, key=lambda x: x["date"], reverse=True)
