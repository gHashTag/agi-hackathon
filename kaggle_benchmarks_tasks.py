#!/usr/bin/env python3
"""
Create all 5 Kaggle Benchmark Tasks (Learning, Metacognition, Attention, Executive Functions, Social Cognition)
"""

from kaggle_benchmarks import Task
import yaml

# Task configurations
TASK_CONFIGS = {
    "thlp": {
        "title": "Trinity THLP MC Benchmark",
        "description": "Hippocampal Learning Probe - Adversarial dataset testing pattern learning, belief update, and rule induction",
        "dataset_path": "kaggle/data/extra/thlp_mc_adversarial.csv",
        "dataset_size": 274,
        "adversarial_techniques": ["paraphrasing", "negative_constraints", "choice_scrambling"]
    },
    "ttm": {
        "title": "Trinity TTM MC Benchmark",
        "description": "Metacognition Probe - Physics Enhanced (φ, E8, LQG) - confidence calibration, error detection, meta-learning",
        "dataset_path": "kaggle/data/extra/ttm_physics_mc.csv",
        "dataset_size": 199,
        "adversarial_techniques": ["physics_integration", "distractor_enhancement", "reasoning_chain"]
    },
    "tagp": {
        "title": "Trinity TAGP MC Benchmark",
        "description": "Targeted Attention and General Perception Probe - Adversarial testing selective filtering, sustained attention, attention shifting",
        "dataset_path": "kaggle/data/tagp_mc_aggressive.csv",
        "dataset_size": 851,
        "adversarial_techniques": ["attention_traps", "working_memory_overflow", "inhibitory_control"]
    },
    "tefb": {
        "title": "Trinity TEFB MC Benchmark",
        "description": "Temporal and Executive Function Benchmark - Multi-step planning, working memory, inhibitory control",
        "dataset_path": "kaggle/data/extra/tefb_mc_cleaned.csv",
        "dataset_size": 1512,
        "adversarial_techniques": ["planning_distractors", "resource_constraint_traps", "deadline_pressure"]
    },
    "tscp": {
        "title": "Trinity TSCP MC Benchmark",
        "description": "Theory of Mind and Social Cognition Probe - Adversarial testing social norms, pragmatic reasoning",
        "dataset_path": "kaggle/data/extra/tscp_mc_cleaned.csv",
        "dataset_size": 25,
        "adversarial_techniques": ["social_norm_violations", "pragmatic_reasoning_traps", "theory_application_failures"]
    }
}

def create_learning_task():
    """Create THLP Learning task"""
    config = TASK_CONFIGS["thlp"]

    task = Task(
        id="trinity_thlp_mc",
        title=config["title"],
        description=config["description"]
    )

    return task

def create_metacognition_task():
    """Create TTM Metacognition task"""
    config = TASK_CONFIGS["ttm"]

    task = Task(
        id="trinity_ttm_mc",
        title=config["title"],
        description=config["description"]
    )

    return task

def create_attention_task():
    """Create TAGP Attention task"""
    config = TASK_CONFIGS["tagp"]

    task = Task(
        id="trinity_tagp_mc",
        title=config["title"],
        description=config["description"]
    )

    return task

def create_executive_task():
    """Create TEFB Executive Functions task"""
    config = TASK_CONFIGS["tefb"]

    task = Task(
        id="trinity_tefb_mc",
        title=config["title"],
        description=config["description"]
    )

    return task

def create_social_task():
    """Create TSCP Social Cognition task"""
    config = TASK_CONFIGS["tscp"]

    task = Task(
        id="trinity_tscp_mc",
        title=config["title"],
        description=config["description"]
    )

    return task

def create_all_tasks():
    """Create all 5 Kaggle Benchmark Tasks"""
    tasks = {}

    # Create all 5 tasks
    for track_name, config in TASK_CONFIGS.items():
        if track_name == "thlp":
            tasks[track_name] = create_learning_task()
        elif track_name == "ttm":
            tasks[track_name] = create_metacognition_task()
        elif track_name == "tagp":
            tasks[track_name] = create_attention_task()
        elif track_name == "tefb":
            tasks[track_name] = create_executive_task()
        elif track_name == "tscp":
            tasks[track_name] = create_social_task()

    return tasks

def main():
    """Main execution function"""
    print("Creating 5 Kaggle Benchmark Tasks...")

    # Create all tasks
    tasks = create_all_tasks()

    print(f"Created {len(tasks)} tasks:")
    for track_id, task in tasks.items():
        print(f"  - {track_id}: {task.title}")
        print(f"    Dataset: {task.dataset}")
        print(f"    Description: task.description}")

    return tasks

if __name__ == "__main__":
    tasks = main()
