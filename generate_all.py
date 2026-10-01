import json
from builder_topics_2_to_4 import get_topics_2_to_4
from builder_topics_5_to_8 import get_topics_5_to_8
from builder_topics_9_to_12 import get_topics_9_to_12

# Read Topic 1 from existing generator
with open("/Users/satdevkumar/.gemini/antigravity/scratch/android-interview-prep/js/topics-data.js", "r") as f:
    content = f.read()
    json_str = content.replace("// Auto-generated Comprehensive Android Mastery Database\nwindow.ANDROID_TOPICS = ", "").rstrip(";\n")
    topic_1_list = json.loads(json_str)

all_topics = []
all_topics.extend(topic_1_list)
all_topics.extend(get_topics_2_to_4())
all_topics.extend(get_topics_5_to_8())
all_topics.extend(get_topics_9_to_12())

print(f"Total topics compiled: {len(all_topics)}")

with open("/Users/satdevkumar/.gemini/antigravity/scratch/android-interview-prep/js/topics-data.js", "w") as f:
    f.write("// Android Interview Mastery Database - Complete 12 Comprehensive Modules\n")
    f.write("window.ANDROID_TOPICS = " + json.dumps(all_topics, indent=2) + ";\n")

print("Successfully written complete database to js/topics-data.js")
