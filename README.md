# Wahoo to Garmin Workout Converter

Convert Wahoo workout text files to Garmin Connect workout objects using AWS Bedrock AI.

## Features

- Parses Wahoo workout text files using AWS Bedrock (Claude)
- Converts to python-garminconnect workout objects
- Supports Swimming, Running, and Cycling workouts
- Automatically converts swimming distances from meters to yards
- Handles complex workout structures (repeats, intervals, rest periods)

## Installation

```bash
pip install -r requirements.txt
```

## AWS Setup

1. Ensure you have AWS credentials configured (via `~/.aws/credentials` or environment variables)
2. Enable Claude 3.5 Sonnet model access in AWS Bedrock console
3. Set your preferred AWS region (default: us-east-1)

## Usage

### Basic Usage

```python
from wahoo_to_garmin_converter import WahooToGarminConverter, load_wahoo_workout

# Initialize converter
converter = WahooToGarminConverter(region_name="us-east-1")

# Load Wahoo workout text
wahoo_text = load_wahoo_workout("example_wahoo_workout.txt")

# Convert to Garmin workout (swimming example)
garmin_workout = converter.convert_workout(wahoo_text, workout_type="swimming")

# Get workout as dictionary for API upload
workout_dict = garmin_workout.to_dict()
```

### Command Line Usage

```bash
python convert_cli.py example_wahoo_workout.txt --type swimming --output workout.json
```

### Workout Types

- `swimming` - Automatically converts distances to yards
- `running` - Running workouts
- `cycling` - Cycling workouts

## Example

Input (Wahoo format):
```
Warm Up
Number of Sets: 1
Number of Repeats: 6 × 100m @ RPE 3-4-- Z2
20 sec rest
```

Output (Garmin workout object):
```python
SwimmingWorkout(
    workoutName="Swimming Workout",
    estimatedDurationInSecs=1200,
    workoutSegments=[...]
)
```

## Swimming Distance Conversion

All swimming workouts are automatically converted from meters to yards:
- 25m → 25 yards (pool length)
- 50m → 50 yards
- 100m → 100 yards
- 200m → 200 yards
- Other distances: meters × 1.09361

## Project Structure

- `wahoo_to_garmin_converter.py` - Main converter class
- `workout.py` - Garmin workout models (from python-garminconnect)
- `convert_cli.py` - Command line interface
- `sample_workouts/` - Example Garmin workout structures
- `example_wahoo_workout.txt` - Sample Wahoo workout file

## Next Steps

To upload workouts to Garmin Connect, use the python-garminconnect library:

```python
from garminconnect import Garmin

# Authenticate
garmin = Garmin("your_email", "your_password")
garmin.login()

# Upload workout
garmin.add_workout(garmin_workout.to_dict())
```

## License

MIT
