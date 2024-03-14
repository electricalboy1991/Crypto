from datetime import datetime

# Example timestamps
timestamp1 = 1710374289.999401
timestamp2 = 1710374324.306725

# Convert timestamps to datetime objects
datetime1 = datetime.fromtimestamp(timestamp1)
datetime2 = datetime.fromtimestamp(timestamp2)

# Format datetime objects into strings
formatted_time1 = datetime1.strftime('%Y-%m-%d %H:%M:%S')
formatted_time2 = datetime2.strftime('%Y-%m-%d %H:%M:%S')

print("Formatted Time 1:", formatted_time1)
print("Formatted Time 2:", formatted_time2)