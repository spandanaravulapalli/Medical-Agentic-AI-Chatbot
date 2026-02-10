 #!/bin/bash
 # Create Project Directory Structure
mkdir -p src
mkdir -p research

#Create Project Files
touch src/_init_.py
touch src/helper.py
touch src/prompt.py
touch .env
touch setup.py
touch app.py
touch research/trials.ipynb
touch requirements.txt

echo "Project Directory Structure Created Successfully"
