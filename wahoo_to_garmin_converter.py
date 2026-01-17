"""Convert Wahoo workout text files to Garmin workout objects using AWS Bedrock."""

import boto3
from garminconnect import Garmin
from garminconnect.workout import (
    CyclingWorkout,
    HikingWorkout,
    RunningWorkout,
    SwimmingWorkout,
    WalkingWorkout,
    WorkoutSegment,
    create_cooldown_step,
    create_interval_step,
    create_recovery_step,
    create_repeat_group,
    create_warmup_step,
)
from workout_helpers import (
    create_cooldown_step_distance,
    create_cooldown_step_distance_effort,
    create_interval_step_distance,
    create_interval_step_distance_effort,
    create_recovery_step_distance,
    create_recovery_step_distance_effort,
    create_warmup_step_distance,
    create_warmup_step_distance_effort,
)


class WahooToGarminConverter:
    """Converts Wahoo workout text files to Garmin workout Python code using AWS Bedrock."""

    def __init__(
        self, 
        region_name: str = "us-east-1", 
        system_prompt_path: str = "system_prompt.txt",
    ):
        """Initialize the converter with AWS Bedrock client.
        
        Args:
            region_name: AWS region for Bedrock service
            system_prompt_path: Path to system prompt file
        """
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime", region_name=region_name
        )
        self.model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
        
        # Load workout.py module from installed package
        import garminconnect.workout
        import inspect
        workout_module = inspect.getsource(garminconnect.workout)
        
        # Load system prompt and replace placeholder with workout module
        with open(system_prompt_path, encoding="utf-8") as f:
            prompt_template = f.read()
        
        self.system_prompt = prompt_template.replace("{pydantic_workout_module}", workout_module)

    def convert_workout(
        self, wahoo_text: str, workout_type: str | None = "swimming", output_file: str = "generated_workout.py"
    ) -> str:
        """Convert Wahoo workout text to Python code and save to file.
        
        Args:
            wahoo_text: The raw text from Wahoo workout file
            workout_type: Type of workout ('swimming', 'running', or 'cycling')
            output_file: Path to save the generated Python code
            
        Returns:
            Generated Python code as string
        """
        # Use Bedrock Converse API to generate Python code
        python_code = self._generate_workout_code(wahoo_text, workout_type)
        
        # Save to file
        self._save_workout_code(python_code, output_file, workout_type)
        
        return python_code

    def retry_with_error(
        self,
        wahoo_text: str,
        workout_type: str | None,
        output_file: str,
        error_message: str,
        previous_code: str
    ) -> str:
        """Retry workout conversion with error feedback.
        
        Args:
            wahoo_text: The raw text from Wahoo workout file
            workout_type: Type of workout
            output_file: Path to save the generated Python code
            error_message: Error message from previous attempt
            previous_code: Previously generated code that failed
            
        Returns:
            Generated Python code as string
        """
        # Use Bedrock Converse API with error feedback
        python_code = self._generate_workout_code_with_error(
            wahoo_text, workout_type, error_message, previous_code
        )
        
        # Save to file
        self._save_workout_code(python_code, output_file, workout_type)
        
        return python_code

    def _generate_workout_code(self, wahoo_text: str, workout_type: str | None) -> str:
        """Use AWS Bedrock Converse API to generate Python workout code.
        
        Args:
            wahoo_text: The raw text from Wahoo workout file
            workout_type: Type of workout (or None to auto-detect)
            
        Returns:
            Generated Python code as string
        """
        if workout_type:
            user_message = f"""Convert this {workout_type} workout to Python code:

{wahoo_text}

Generate the Python code that creates a {workout_type.capitalize()}Workout object."""
        else:
            user_message = f"""Convert this workout to Python code (auto-detect the workout type from the content):

{wahoo_text}

Generate the Python code that creates the appropriate Workout object (SwimmingWorkout, RunningWorkout, or CyclingWorkout)."""

        response = self.bedrock_runtime.converse(
            modelId=self.model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": user_message}],
                },
                {
                    "role": "assistant",
                    "content": [{"text": "```python"}],
                },
            ],
            system=[{"text": self.system_prompt}],
            inferenceConfig={
                "maxTokens": 4096,
                "temperature": 0.1,
            },
        )

        # Extract the generated text (already prefilled with ```python)
        output_message = response["output"]["message"]
        content = output_message["content"][0]["text"]
        
        # Remove closing ``` if present
        if content.endswith("```"):
            content = content[:-3].rstrip()
        
        return content

    def _generate_workout_code_with_error(
        self, wahoo_text: str, workout_type: str | None, error_message: str, previous_code: str
    ) -> str:
        """Use AWS Bedrock Converse API to regenerate code with error feedback.
        
        Args:
            wahoo_text: The raw text from Wahoo workout file
            workout_type: Type of workout (or None to auto-detect)
            error_message: Error from previous attempt
            previous_code: Previously generated code that failed
            
        Returns:
            Generated Python code as string
        """
        if workout_type:
            workout_instruction = f"creates a {workout_type.capitalize()}Workout object"
        else:
            workout_instruction = "creates the appropriate Workout object (SwimmingWorkout, RunningWorkout, or CyclingWorkout)"
            
        user_message = f"""The previous workout conversion failed with this error:

ERROR: {error_message}

PREVIOUS CODE:
```python
{previous_code}
```

ORIGINAL WORKOUT:
{wahoo_text}

Please fix the error and generate corrected Python code that {workout_instruction}."""

        response = self.bedrock_runtime.converse(
            modelId=self.model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": user_message}],
                },
                {
                    "role": "assistant",
                    "content": [{"text": "```python"}],
                },
            ],
            system=[{"text": self.system_prompt}],
            inferenceConfig={
                "maxTokens": 4096,
                "temperature": 0.1,
            },
        )

        # Extract the generated text
        output_message = response["output"]["message"]
        content = output_message["content"][0]["text"]
        
        # Remove closing ``` if present
        if content.endswith("```"):
            content = content[:-3].rstrip()
        
        return content

    def _save_workout_code(self, python_code: str, output_file: str, workout_type: str) -> None:
        """Save generated Python code to file.
        
        Args:
            python_code: Generated Python code (just the workout object)
            output_file: Path to save the file
            workout_type: Type of workout
        """
        # Strip leading/trailing whitespace from generated code
        python_code = python_code.strip()
        
        # Save just the workout object code
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(python_code)

    def evaluate_workout(self, workout_file: str) -> tuple[bool, str, object]:
        """Evaluate a generated workout file.
        
        Args:
            workout_file: Path to the generated workout Python file
            
        Returns:
            Tuple of (success, error_message, workout_object)
        """
        try:
            # Read the workout code
            with open(workout_file, encoding="utf-8") as f:
                workout_code = f.read()
            
            # Create namespace with all necessary classes and functions
            namespace = {
                'SwimmingWorkout': SwimmingWorkout,
                'RunningWorkout': RunningWorkout,
                'CyclingWorkout': CyclingWorkout,
                'WalkingWorkout': WalkingWorkout,
                'HikingWorkout': HikingWorkout,
                'WorkoutSegment': WorkoutSegment,
                'create_warmup_step': create_warmup_step,
                'create_warmup_step_distance': create_warmup_step_distance,
                'create_warmup_step_distance_effort': create_warmup_step_distance_effort,
                'create_interval_step': create_interval_step,
                'create_interval_step_distance': create_interval_step_distance,
                'create_interval_step_distance_effort': create_interval_step_distance_effort,
                'create_recovery_step': create_recovery_step,
                'create_recovery_step_distance': create_recovery_step_distance,
                'create_recovery_step_distance_effort': create_recovery_step_distance_effort,
                'create_cooldown_step': create_cooldown_step,
                'create_cooldown_step_distance': create_cooldown_step_distance,
                'create_cooldown_step_distance_effort': create_cooldown_step_distance_effort,
                'create_repeat_group': create_repeat_group,
            }
            
            # Execute the code to create the workout object
            workout = eval(workout_code, namespace)
            
            # Validate it's the right type
            if not isinstance(workout, (SwimmingWorkout, RunningWorkout, CyclingWorkout, WalkingWorkout, HikingWorkout)):
                return False, f"Generated object is not a valid workout type: {type(workout)}", None
            
            # Try to convert to dictionary (validates structure)
            workout_dict = workout.to_dict()
            
            # Basic validation
            if not workout.workoutName:
                return False, "Workout is missing workoutName", None
            
            if not workout.workoutSegments:
                return False, "Workout has no segments", None
            
            return True, "", workout
            
        except SyntaxError as e:
            return False, f"Syntax error in generated code: {e}", None
        except NameError as e:
            return False, f"Name error (missing import or undefined name): {e}", None
        except TypeError as e:
            return False, f"Type error in workout construction: {e}", None
        except Exception as e:
            return False, f"Error evaluating workout: {type(e).__name__}: {e}", None

    def convert_with_retry(
        self,
        wahoo_text: str,
        workout_type: str | None = None,
        output_file: str = "generated_workout.py",
        max_retries: int = 3,
        verbose: bool = True
    ) -> tuple[bool, str, object]:
        """Convert workout with evaluation and retry on failure.
        
        Args:
            wahoo_text: Wahoo workout text
            workout_type: Type of workout (optional, will auto-detect if None)
            output_file: Output file path
            max_retries: Maximum number of retry attempts
            verbose: Whether to print progress messages
            
        Returns:
            Tuple of (success, message, workout_object)
        """
        for attempt in range(max_retries):
            if verbose:
                print(f"\n{'='*60}")
                print(f"Attempt {attempt + 1}/{max_retries}")
                print(f"{'='*60}")
            
            # Generate workout code
            if attempt == 0:
                # First attempt - normal conversion
                if verbose:
                    workout_type_msg = f"{workout_type} " if workout_type else "(auto-detecting type) "
                    print(f"Generating {workout_type_msg}workout code...")
                python_code = self.convert_workout(wahoo_text, workout_type, output_file)
            else:
                # Retry with error feedback
                if verbose:
                    print(f"Retrying with error feedback...")
                python_code = self.retry_with_error(
                    wahoo_text, 
                    workout_type, 
                    output_file,
                    error_message,
                    previous_code
                )
            
            if verbose:
                print(f"✓ Code generated ({len(python_code)} characters)")
            
            # Evaluate the generated code
            if verbose:
                print("Evaluating generated workout...")
            success, error_message, workout = self.evaluate_workout(output_file)
            
            if success:
                if verbose:
                    print("✓ Workout validated successfully!")
                    print(f"  - Name: {workout.workoutName}")
                    print(f"  - Type: {type(workout).__name__}")
                    print(f"  - Duration: {workout.estimatedDurationInSecs}s")
                    print(f"  - Segments: {len(workout.workoutSegments)}")
                return True, "Workout converted and validated successfully!", workout
            else:
                if verbose:
                    print(f"✗ Validation failed: {error_message}")
                previous_code = python_code
                
                if attempt < max_retries - 1:
                    if verbose:
                        print(f"Will retry with error feedback...")
                else:
                    if verbose:
                        print(f"Max retries ({max_retries}) reached.")
        
        return False, f"Failed after {max_retries} attempts. Last error: {error_message}", None

    def upload_workout(self, workout: object, garmin_api: Garmin) -> dict:
        """Upload a workout object to Garmin Connect.
        
        Args:
            workout: Workout object (SwimmingWorkout, RunningWorkout, CyclingWorkout, etc.)
            garmin_api: Authenticated Garmin API instance
            
        Returns:
            Response from Garmin Connect API
            
        Raises:
            ValueError: If workout type is not supported
        """
        # Upload based on workout type
        if isinstance(workout, SwimmingWorkout):
            return garmin_api.upload_swimming_workout(workout)
        elif isinstance(workout, RunningWorkout):
            return garmin_api.upload_running_workout(workout)
        elif isinstance(workout, CyclingWorkout):
            return garmin_api.upload_cycling_workout(workout)
        elif isinstance(workout, WalkingWorkout):
            return garmin_api.upload_walking_workout(workout)
        elif isinstance(workout, HikingWorkout):
            return garmin_api.upload_hiking_workout(workout)
        else:
            raise ValueError(f"Unsupported workout type: {type(workout).__name__}")
