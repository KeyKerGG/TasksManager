from flask import Flask, request, jsonify
from pydantic import BaseModel, ValidationError, validator
from typing import Optional, List
import json
import os

app = Flask(__name__)
DATA_FILE = 'tasks.json'


class TaskSchema(BaseModel):
    title: str
    description: str
    status: str

    @validator('status')
    def status_must_be_valid(cls, v):
        allowed = ['todo', 'in_progress', 'done']
        if v not in allowed:
            raise ValueError(f'status должен быть одним из: {allowed}')
        return v


if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)


def read_tasks():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def write_tasks(tasks):
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)


@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = read_tasks()
    return jsonify(tasks)


@app.route('/tasks', methods=['POST'])
def create_task():
    try:
        task_data = TaskSchema(**request.json)
    except ValidationError as e:
        return jsonify(e.errors()), 400

    tasks = read_tasks()
    new_id = max([t['id'] for t in tasks], default=0) + 1
    task_dict = task_data.dict()
    task_dict['id'] = new_id
    tasks.append(task_dict)
    write_tasks(tasks)
    return jsonify(task_dict), 201


@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        task_data = TaskSchema(**request.json)
    except ValidationError as e:
        return jsonify(e.errors()), 400

    tasks = read_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task.update(task_data.dict())
            write_tasks(tasks)
            return jsonify(task)

    return jsonify({'error': 'Задача не найдена'}), 404


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks = read_tasks()
    updated_tasks = [t for t in tasks if t['id'] != task_id]

    if len(updated_tasks) == len(tasks):
        return jsonify({'error': 'Задача не найдена'}), 404

    write_tasks(updated_tasks)
    return jsonify({'message': 'Задача удалена'})


if __name__ == '__main__':
    app.run(debug=True)
