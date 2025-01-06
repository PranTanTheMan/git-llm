import random
import time
import subprocess
from datetime import datetime, timedelta
import os
from openai import OpenAI
import json


class LeetCodeSolutionGenerator:
    def __init__(self, repo_path, api_key, base_url):
        """
        Initialize the solution generator
        repo_path: Path to your git repository
        api_key: API key for the LLM service
        base_url: Base URL for the API
        """
        self.repo_path = repo_path
        self.client = OpenAI(api_key=api_key, base_url=base_url)

        # Ensure the solutions directory exists
        self.solutions_dir = os.path.join(repo_path, "leetcode_solutions")
        os.makedirs(self.solutions_dir, exist_ok=True)

    async def generate_problem(self):
        """Generate a random LeetCode-style problem"""
        prompt = """Generate a random LeetCode-style coding problem. 
        Include:
        1. Problem description
        2. Input/output examples
        3. Constraints
        Format the response as JSON with keys: 'title', 'difficulty', 'description', 'examples', 'constraints'"""

        completion = await self.client.chat.completions.create(
            model="llama3.1:70b",
            messages=[
                {"role": "system", "content": "You are a coding problem generator."},
                {"role": "user", "content": prompt},
            ],
        )

        return json.loads(completion.choices[0].message.content)

    async def generate_solution(self, problem):
        """Generate solution for the given problem"""
        prompt = f"""Solve this coding problem:
        {json.dumps(problem)}
        
        Provide:
        1. Detailed thought process
        2. Time and space complexity analysis
        3. Python solution code
        4. Example walkthrough
        
        Format the response as JSON with keys: 'thought_process', 'complexity_analysis', 'solution_code', 'walkthrough'"""

        completion = await self.client.chat.completions.create(
            model="llama3.1:70b",
            messages=[
                {"role": "system", "content": "You are an expert programmer."},
                {"role": "user", "content": prompt},
            ],
        )

        return json.loads(completion.choices[0].message.content)

    def create_markdown_file(self, problem, solution):
        """Create a markdown file with the problem and solution"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        filename = f"{current_date}_{problem['title'].lower().replace(' ', '_')}.md"
        file_path = os.path.join(self.solutions_dir, filename)

        content = f"""# {problem['title']}
        
## Difficulty: {problem['difficulty']}

## Problem Description
{problem['description']}

### Examples
{problem['examples']}

### Constraints
{problem['constraints']}

## Solution

### Thought Process
{solution['thought_process']}

### Complexity Analysis
{solution['complexity_analysis']}

### Code
```python
{solution['solution_code']}
```

### Walkthrough
{solution['walkthrough']}

Generated on: {current_date}
"""

        with open(file_path, "w") as f:
            f.write(content)

        return file_path

    def commit_solution(self, file_path):
        """Commit the solution to git"""
        os.chdir(self.repo_path)

        # Add the changes
        subprocess.run(["git", "add", file_path])

        # Create commit message
        commit_msg = f"Add LeetCode solution for {os.path.basename(file_path)}"

        # Commit
        subprocess.run(["git", "commit", "-m", commit_msg])

        # Push changes
        subprocess.run(["git", "push"])

    async def daily_solution(self):
        """Generate and commit a daily solution"""
        # Generate problem
        problem = await self.generate_problem()

        # Generate solution
        solution = await self.generate_solution(problem)

        # Create markdown file
        file_path = self.create_markdown_file(problem, solution)

        # Commit and push
        self.commit_solution(file_path)

        print(f"Successfully generated and committed solution for: {problem['title']}")


# Usage example
if __name__ == "__main__":
    import asyncio

    # Replace these with your actual values
    REPO_PATH = "/path/to/your/repo"
    API_KEY = "your-api-key"
    BASE_URL = "https://api.galadriel.com/v1"

    generator = LeetCodeSolutionGenerator(REPO_PATH, API_KEY, BASE_URL)

    # Schedule daily solutions
    async def run_daily():
        while True:
            try:
                await generator.daily_solution()
                # Wait for 24 hours
                await asyncio.sleep(24 * 60 * 60)
            except Exception as e:
                print(f"Error occurred: {e}")
                # Wait for 1 hour before retrying
                await asyncio.sleep(60 * 60)

    # Run the daily schedule
    asyncio.run(run_daily())
