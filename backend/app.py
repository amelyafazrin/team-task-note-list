from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

DATA_DIR = "/app/data"
DATA_FILE = os.path.join(DATA_DIR, "tasks.json")

os.makedirs(DATA_DIR, exist_ok=True)


def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=4, ensure_ascii=False)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "application": "Team Task & Note List"
    }), 200


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(load_tasks()), 200


@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be valid JSON"
        }), 400

    task_name = data.get("task")
    responsible = data.get("responsible")
    notes = data.get("notes", "")

    if not isinstance(task_name, str) or not task_name.strip():
        return jsonify({
            "error": "Task is required"
        }), 400

    if not isinstance(responsible, str) or not responsible.strip():
        return jsonify({
            "error": "Responsible person is required"
        }), 400

    if not isinstance(notes, str):
        return jsonify({
            "error": "Notes must be text"
        }), 400

    tasks = load_tasks()

    new_task = {
        "task": task_name.strip(),
        "responsible": responsible.strip(),
        "notes": notes.strip(),
        "completed": False
    }

    tasks.append(new_task)
    save_tasks(tasks)

    return jsonify({
        "message": "Task added successfully",
        "task": new_task,
        "tasks": tasks
    }), 201


@app.route("/tasks", methods=["DELETE"])
def delete_task():
    index = request.args.get("index")

    if index is None or not index.isdigit():
        return jsonify({
            "error": "Valid task index is required"
        }), 400

    tasks = load_tasks()
    index = int(index)

    if index >= len(tasks):
        return jsonify({
            "error": "Task not found"
        }), 404

    deleted_task = tasks.pop(index)
    save_tasks(tasks)

    return jsonify({
        "message": "Task deleted successfully",
        "deleted_task": deleted_task
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)